# 2.1 — Bộ nhớ Ảo, Page Table, TLB, HugePages & OOM Killer

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** part1-hardware-os.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 1.2 (cache) · 1.3 (RAM thật).

**Sợi chỉ đỏ:** *Một máy một process là trần đầu tiên — process ấy đang được Linux đối xử thế nào với bộ nhớ của nó?* — trả lời: mỗi process nhận một không gian địa chỉ riêng và "tưởng" mình có cả thanh RAM; Linux chỉ cấp thật khi chạm — hợp đồng ấy có giá của nó: overcommit, copy-on-write, và khi cạn thì OOM killer chọn người chết. Câu hỏi để lại cho chương sau: *Process thấy cả một không gian địa chỉ 'của mình' — bên trong, stack và heap vận hành ra sao?*

**Thuật ngữ sẽ gặp:** *bộ nhớ ảo* — không gian địa chỉ riêng mỗi process, ánh xạ vào RAM khi cần; *VSZ/RSS/PSS* — ba cách đo bộ nhớ đếm khác nhau, PSS mới chia phần dùng chung theo đúng tỉ lệ; *overcommit* — kernel hứa nhiều hơn RAM thật có; *copy-on-write* — hai process chia trang chỉ-đọc tới khi một bên ghi; *OOM killer* — kernel chấm điểm và giết process khi cạn bộ nhớ; *oom_score_adj* — núm chỉnh điểm ấy để bảo vệ process quan trọng.

**Ví dụ mở đầu:** Dashboard của DM báo service thanh toán "2 GB", service log "2 GB" — nhưng máy 8 GB đã cạn. RSS đếm trang chia sẻ nguyên vẹn cho từng process nên tổng đội lên; PSS chia phần chung theo số người dùng. Đọc nhầm con số thì cả việc mua thêm RAM lẫn việc chỉnh monitor đều ra quyết định sai.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Chính sách overcommit (`vm.overcommit_memory` 0/1/2) | Tôi muốn từ chối cấp phát sớm, hay chấp nhận OOM killer tới? |
| 2 | Cgroup memory limit + `memory.high` xử phạt | Giới hạn cứng ở đâu, phần "đệm xử phạt" đặt ở đâu? |
| 3 | HugePages tĩnh hay THP (→1.3) cho dịch vụ | Đổi TLB miss lấy rủi ro compaction stall — đáng không? |
| 4 | Fork-heavy workload (Redis BGSAVE, proxy) đặt ở đâu | Copy-on-Write có thể làm footprint nổ — tôi đã tính chưa? |

---

## 2. Cơ chế

### 2.1 Bộ nhớ ảo: mọi process đều "tưởng" mình có cả thanh RAM

Mỗi process thấy một không gian địa chỉ riêng (64-bit: ~128 TB usable trên x86-64 (V)); ánh xạ sang khung vật lý qua **bảng trang nhiều tầng** (4–5 tầng). CPU đi qua nhờ **TLB** — cache ánh xạ nhỏ (~1–2k mục) nằm trong lõi (→1.2). TLB miss → page table walk tốn hàng trăm chu kỳ. Đó là toàn bộ lý do tồn tại của **hugepage**: trang 2 MB làm số mục TLB ít đi 512× so với 4 KB.

Ba kiểu trang đáng biết:
- **Anonymous** (heap, stack) — hỗ trợ swap;
- **File-backed** (mmap file, page cache) — bỏ được, đọc lại từ đĩa;
- **HugePages tĩnh** (hugetlbfs) — reserve trước, không swap, không bị compaction (khác THP — xem 1.3 §2.4).

### 2.2 Ba con số hay đọc nhầm: VSZ / RSS / PSS

`VSZ` = không gian địa chỉ (ảo, gồm cả mmap chưa chạm); `RSS` = đang nằm trong RAM (gặp bài toán đếm kép: thư viện dùng chung tính cho mọi process); `PSS` = RSS chia đều theo người dùng chung (con số đúng để trả tiền/đặt limit). Khi nhìn monitor, luôn hỏi: nó đo cái nào? Container runtime báo đa số là RSS + page cache (tùy driver) — đây là gốc của sự cố "OOMKill dù RSS < limit" (mục 5).

### 2.3 Copy-on-Write: lợi và bẫy của fork

`fork()` không copy trang mà đánh dấu read-only; trang chỉ copy thật khi một bên ghi. Server khai thác: Redis `BGSAVE` fork con để ghi RDB — trong lúc đó cha tiếp tục phục vụ. Bẫy: nếu cha ghi **rợ** lên toàn heap trong lúc con còn sống, COW copy từng trang → footprint gần gấp đôi → chạm limit → OOM kill (nổi tiếng với Redis + `INFO` theo dõi `latest_fork_usec`). Quy tắc: fork-heavy + ghi nhiều = đặt limit gấp 1,5–2× working set (I).

### 2.4 Overcommit và OOM killer: hợp đồng thật của Linux

- **Mode 0** (mặc định): cấp thoải mái, ước lượng hào phóng;
- **Mode 1**: không kiểm tra gì — malloc luôn thành công (dùng cho workload khoa học tự biết mình cần bao nhiêu) (dùng cho workload khoa học biết mình làm gì);
- **Mode 2** (`overcommit_ratio`): từ chối sớm nếu vượt công thức commit limit.

Khi hết khung vật lý thật, kernel đi **direct reclaim**, rồi **OOM killer** chọn nạn nhân theo `oom_score` (chấm điểm theo RSS + privileged điều chỉnh qua `oom_score_adj`). Với cgroup v2: kill theo **cgroup** chạm `memory.max` — triệu chứng "Pod OOMKilled" (→9.1). `memory.high` là mức **xử phạt** (thu hồi + throttle) thay vì kill — dùng làm đệm.

Hai cối xay ngầm cần nhớ: **kswapd** (nền) và **direct reclaim** (đường đẻ của process — đây là gốc "ghi chậm đột ngột" khi áp lực bộ nhớ lớn). PSI memory (`/proc/pressure/memory`) cho thấy thời gian stall do thiếu — metric cảnh báo tốt hơn "RAM còn bao nhiêu GB".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Kích thước trang | 4 KB · huge 2 MB / 1 GB | V | |
| TLB mục | ~1–2k/lõi | I | L2 TLB lớn hơn |
| Walk 4-tầng khi miss | ~4 lần đọc bộ nhớ | I | | 
| Python/Go runtime overhead so với C | 2–10× bộ nhớ/tuyến | I | →3.x |
| COW với Redis BGSAVE | footprint ~1,3–2× trong vài giây | I | phụ thuộc ghi trong lúc fork |
| watermarks reclaim | min/low/high theo zone | V | kernel internals |

---

## 4. Suy luận kiến trúc

- **S1:** Bộ nhớ ảo cho ảo giác "RAM riêng từng process" — ràng buộc thật vẫn là khung vật lý + cgroup limit; thiết kế theo ảo giác đó sẽ gặp OOM ở nơi không ngờ.
- **S2:** Tham số trụ: PSS mỗi service, PSI memory full avg10, tỉ lệ major fault, `oom_score_adj` của service quan trọng.
- **S3:** Overcommit 0/1/2 đổi tính "từ chối sớm" lấy throughput; memory.high đổi kill lấy throttle; hugepage tĩnh đổi linh hoạt lấy TLB — mỗi cái đều đúng ở một workload.
- **S4:** Máy to RAM nhiều → cgroup memory là biên giới thật, không phải máy — do đó "đủ RAM" của cụm không cứu được pod thiếu limit hợp lý.
- **S5:** PSI (năm 2019+) và cgroup v2 đã trở thành mặc định của distro hiện đại — monitoring cũ dựa trên "free -m" là mù với stall thật.
- **S6:** Khi OOM/thiếu bộ nhớ, lùi một bậc: đó là limit sai (cgroup), nổ footprint (COW/leak →3.9), page cache tranh chấp, hay thật sự hết máy? Bốn câu bốn thuốc khác nhau.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Pod OOMKilled dù RSS < limit | Page cache + kernel memory tính vào cgroup; hoặc VMSizes của metric khác định nghĩa | `dmesg`; so `memory.max` vs `memory.current` (không phải RSS) | §2.4 |
| Hệ thống chậm dần rồi sập (spiral) | Swap + PSI tăng → queue nổ | `vmstat 1` (si/so); `/proc/pressure/memory` | §2.4 |
| Redis/DB spike p99 định kỳ | THP compaction (→1.3) hoặc fork COW | `SLOWLOG`; `info memory` trong lúc fork | §2.3 |
| mmap file lớn treo I/O | Page fault đường đẻ + reclaim | `perf sched`; PSI io | §2.4 |
| Service chết "vô cớ" lúc 3h sáng | Cron backup + OOM killer chọn nhầm nạn nhân | `dmesg -T`; `oom_score_adj` audit | §2.4 |

---

## 6. Cách đo

```bash
# 1. Sự thật về bộ nhớ của một process
cat /proc/<pid>/smaps_rollup | grep -E 'Rss|Pss|Swap|Private'

# 2. Áp lực thật (không phải %RAM)
cat /proc/pressure/memory      # some vs full — full>0 là dấu hiệu sắp chết
grep -E 'full|some' /sys/fs/cgroup/<path>/memory.pressure

# 3. OOM audit
dmesg -T | grep -i -E 'oom|killed process'   # kèm oom_score từng ứng viên

# 4. Phân tích anonymous/file/huge
grep -E 'AnonHugePages|HugePages' /proc/meminfo
```

Nguyên tắc: **đo theo định nghĩa của người giết bạn** (cgroup `memory.current`, PSI) — không đo theo `top`, vì top không ngồi trong kernel.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay "tăng memory limit":** giảm working set (nén cache trong app, →5.4), giảm bản sao (share memory qua mmap/Redis thay vì copy từng service), hoặc phân mảnh ngang (→5.5). **Thay swap:** tắt swap cho dịch vụ latency (systemd `MemorySwapMax=0`), giữ swap như "van cứu hộ" chỉ cho batch. **Thay hugepage tĩnh:** THP madvise vùng chọn — trung gian giữa hai cực.

Năm thấu kính:
- **Kinh tế:** RAM over-provision 2× "cho an tâm" là chi phí ẩn đều đặn; đo PSS thật và cắt về đúng size là tiết kiệm lập tức.
- **Vận hành:** Mọi service nên khai `oom_score_adj` (tên trong hợp đồng: "ai được chết trước") — để OOM killer không chọn ngẫu nhiên lúc 3h sáng.
- **An ninh:** OOM killer từng là vector DoS (fork bomb ép kill dịch vụ lân cận); cgroup + user namespace (→2.7) chặn lớp này.
- **Lịch sử:** Overcommit từng là tranh luận nóng thập niên 90 (Linux "liều" vs các Unix bảo thủ); kết cục: mode 0 thắng vì batch workload cần ảo — và cgroup ra đời (2007) để trả phần kỷ luật mà overcommit bỏ qua.
- **Người dùng:** Người dùng thấy "service restart lúc nửa đêm". Với họ, mọi cơ chế chương này chỉ có một ý nghĩa: dự đoán được cái chết và chọn đúng nạn nhân thay vì ngẫu nhiên.

---

## 8. Đọc tiếp & bài tập

- THP/HBM/NUMA: **1.3** · Allocator & đồng bộ: **2.2** · Scheduler & PSI: **2.3** · OOM trong K8s: **9.1**
- **Bài tập 1:** Với một service đang chạy: đọc `smaps_rollup`, so PSS với con số monitor đang báo. Chênh > 30%? Metric của bạn đang nói dối kiểu có hệ thống.
- **Bài tập 2:** Đặt `memory.high` = 80% limit trên một deployment không quan trọng; quan sát PSI memory tăng — đó là "điện báo" trước khi OOM.
- **Bài tập 3:** Tìm trong hệ thống của bạn service nào chưa ai đặt `oom_score_adj`. Đó là lá bài mà kernel sẽ rút ngẫu nhiên khi cần.
