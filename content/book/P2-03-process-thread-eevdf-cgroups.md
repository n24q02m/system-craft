# 2.3 — Process, Thread, Context Switch, EEVDF, cgroups v2 & PSI

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** part1-hardware-os.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 2.2 · 1.2.

**Sợi chỉ đỏ:** *Nhiều process chia một CPU — scheduler cắt lát thế nào, và vì sao quota 500m lại giết p99?* — trả lời: kernel nhìn mọi process và thread đều là task, cắt lát theo EEVDF — và khi cgroup đặt quota CPU 500m thì chu kỳ 100 ms bị cắt ngang, p99 nhảy bậc thang; PSI là đồng hồ "đang thiếu". Câu hỏi để lại cho chương sau: *Ghi file mà máy chết giữa chừng thì sao — page cache và fsync đang chơi trò gì?*

**Thuật ngữ sẽ gặp:** *task* — cách kernel nhìn process và thread như nhau; *chuyển ngữ cảnh* — đổi task đang chạy, có giá và giá năm bậc; *EEVDF* — bộ lập lịch mới của Linux 6.6+; *cgroup v2* — nhóm tài nguyên, giới hạn CPU/RAM theo quota; *throttling* — bị đứng khi hết quota trong chu kỳ; *PSI* — pressure stall information: thời gian chờ tài nguyên của process.

**Ví dụ mở đầu:** Kỳ lạ: nâng CPU của pod DM từ 500m lên 1000m thì p99 giảm một nửa dù usage chỉ 30%. Vì quota 500m nghĩa là 50 ms được chạy rồi 50 ms đứng mỗi chu kỳ — request tới đúng lúc đứng thì xếp hàng. "CPU chưa hết" và "CPU bị cắt" là hai chuyện khác nhau, và dashboard trung bình không nhìn thấy vết cắt.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Đặt requests/limits CPU & QoS class (Guaranteed/Burstable) | limits.cpu có đang throttle tôi ở p99 mà trung bình không thấy? |
| 2 | Thread-per-connection hay worker pool cố định | Bao nhiêu thread là đủ — theo công thức nào chứ không phải "cảm giác"? |
| 3 | Nhận CPU burst (burstable) hay cam kết riêng | Tôi trả tiền cho p99 hay cho trung bình? |
| 4 | NICE/cpu.weight cho service lẫn nhau | Background job có được phép gây latency cho service chính không? |

---

## 2. Cơ chế

### 2.1 Process vs thread: trong kernel chỉ là task

Linux thấy mọi thứ là `task_struct` — "thread" là task **chia sẻ** không gian địa chỉ với task khác (CLONE_VM). Khác biệt nằm ở chi phí tạo/chuyển:
- **Tạo:** fork ~ hàng trăm µs–ms (copy page table, mmap); thread ~10 µs (I);
- **Chuyển ngữ cảnh:** cùng process ~1–5 µs, khác process thêm đổi TLB/cache (nhiều hơn nữa khi khác NUMA — →1.3).

Số thread không miễn phí: mỗi cái tốn stack (→2.2), scheduler overhead, và **đầu mối "CPU 100% nhưng throughput tụt"** — cái máy đang dành thời gian cho việc đổi vai hơn là việc thật.

### 2.2 Năm loại "chuyển ngữ cảnh" xếp theo giá

1. **Syscall** (~100–300 ns + mitigation Spectre tốn hơn nữa (I)): vào kernel làm việc rồi ra;
2. **Interrupt/softirq**: bị chen ngang (network packets xử lý ở đây — →2.6);
3. **Voluntary switch** (yield, chờ I/O): rẻ về mặt CPU, đắt về cache;
4. **Preemption** (hết time slice): kèm re-schedule;
5. **Idle→busy:** đánh thức lõi ngủ (C-state — →1.10) tốn µs đầu.

Đo bằng `perf sched` / `pidstat -wt` — cs/s là chỉ số sức khoẻ của kiến trúc thread.

### 2.3 EEVDF: "CFS đã chết, EEVDF muôn năm" (6.6+)

Từ kernel 6.6 (10/2023), scheduler lớp fair là **EEVDF** (Earliest Eligible Virtual Deadline First) — thay vì chỉ chia "lát virtual runtime" đều (CFS), mỗi task còn có **deadline ảo** theo latency requirement: task ngủ nhiều (interactive) được deadline sớm hơn → latency tốt hơn mà không cần heuristic "nice". Kiến thức cần operational hoá: nice/weight vẫn hoạt động (`cpu.weight` cgroup v2), hành vi interactive tốt hơn — nhưng **throttling do bandwidth vẫn là cơ chế riêng** (mục dưới), EEVDF không cứu.

### 2.4 cgroups v2 & CPU bandwidth throttling — sát thủ p99

`cpu.max = quota period` (ví dụ `250000 100000` = 2,5 CPU). Khi nhóm dùng hết quota trong period → **throttle toàn bộ nhóm tới kỳ sau**. Tại sao độc hại với p99: quota tiêu theo **burst** (nhiều thread song song), trả nợ theo **period** (thường 100 ms) — nên trung bình CPU 60% nhưng mỗi 100 ms có cửa sổ bị đứng (triệu chứng "p99 gấp đôi, CPU host ~60%").

Ba cách đặt đúng:
1. **Đặt limits.cpu = số nguyên**, dùng CFS quota đúng nghĩa "trần" (Guaranteed khi requests=limits);
2. **cpu.weight** thay cho nice giữa service (mặc định 100; service chính 500);
3. **Tắt quota, giữ weight** (cluster với workload tin cậy lẫn nhau — cờ `--cpu-manager`/runtime cụ thể) — đổi cô lập lấy latency.

`nr_throttled`/`throttled_usec` trong `cpu.stat` là sự thật; PSI cpu (`/proc/pressure/cpu`) cho thấy thời gian chờ CPU.

### 2.5 PSI: metric "thiếu tài nguyên" thống nhất

Pressure Stall Information (4.20+, 2019): với mỗi tài nguyên (cpu/memory/io) đo `some` (ít nhất một task chờ) và `full` (mọi task chờ) theo avg10/60/300. Đây là **metric cảnh báo đầu tiên nên gắn** cho service — trực tiếp đo "đói" thay vì đo proxy (CPU%). K8s 1.31+ có PSI-aware eviction (mức alpha→beta theo version — kiểm tra cụm bạn).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Tạo thread / fork | ~10 µs / ~100 µs–ms | I | |
| Context switch cùng process | 1–5 µs | I | |
| Syscall (post-mitigation) | ~100–300 ns+ | I | tùy CPU/gen |
| CFS period mặc định | 100 ms | V | kernel |
| Wakeup từ C-state sâu | ~10–100 µs | I | →1.10 |
| EEVDF thay CFS | kernel 6.6 (2023) | V | |

---

## 4. Suy luận kiến trúc

- **S1:** Quota/period là hằng số vật lý của container — nó giới hạn burst trước khi giới hạn trung bình; thiết kế concurrency (→3.10) phải căn theo quota, không theo "số lõi máy".
- **S2:** Tham số trụ: cs/s, `nr_throttled`, PSI cpu some/full, runqueue length (`vmstat` r).
- **S3:** Guaranteed đổi chi phí (trả 100% requests) lấy p99; Burstable đổi p99 lấy giá; weight đổi "ai nhường ai" giữa hàng xóm.
- **S4:** Lõi thật đông (128+) khiến lock/switch overhead lộ rõ — hiệu ứng "thêm lõi thêm chậm" đã từ nghịch lý thành bình thường; kiến trúc shard-per-core (→3.10) là thuốc cấu trúc.
- **S5:** PSI + EEVDF + cgroup v2 hợp thành lớp quan sát/điều khiển mới của kernel hiện đại — monitoring còn dựa load average là bỏ qua một thế hệ.
- **S6:** Khi "CPU bận mà chậm", phân tách: tính (IPC thấp → 1.2), chờ lock (→2.2), bị throttle (mục 2.4), hay chờ CPU thật (PSI) — bốn chữ số, bốn chương.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| p99 gấp đôi, CPU host ~60% | CFS/EEVDF bandwidth throttling | `cpu.stat` nr_throttled, throttled_usec | §2.4 |
| CPU 100%, throughput giảm khi scale thread | Context switch bão | `pidstat -wt`; `vmstat` cs | §2.1 |
| Service tương tác chậm hơn batch | Nice/weight ngược ưu tiên | `cpu.weight` audit | §2.4 |
| Latency sau khi thêm feature "CPU nhẹ" | Softirq/network tăng (→2.6) | `perf -e softirq:` | §2.2 |
| Pod bị evict "không rõ" | PSI memory/eviction mới | sự kiện eviction; PSI memory | §2.5 |

---

## 6. Cách đo

```bash
# Throttle — chữ ký số một của p99 do CPU
cat /sys/fs/cgroup/<path>/cpu.stat        # nr_throttled, throttled_usec

# PSI cả ba tài nguyên
grep -H . /sys/fs/cgroup/<path>/{cpu,memory,io}.pressure

# Scheduler thật
perf sched record -- sleep 10 && perf sched latency
vmstat 1 5                                  # cs, r (runqueue)

# Thread toggle
pidstat -wt -p <pid> 1
```

Nguyên tắc: **throttle và PSI là hai con số nói thẳng "bị cản"** — mọi thứ khác chỉ giải thích tại sao.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay "thêm CPU":** giảm concurrency về công thức (→3.10 Little), tách batch sang node riêng (đổi topology lấy isolation — thường rẻ hơn trả 2× cho nguyên cụm), hoặc chuyển CPU-heavy sang native/vector hoá (→1.2, →3.5). **Thay thread-per-conn:** event loop/io_uring (→2.5) — giảm cs, tăng phức tạp code.

Năm thấu kính:
- **Kinh tế:** Burstable instance rẻ 60–80% giá on-demand — hợp lý cho workload dập dềnh, tự sát cho latency-critical; đây là phép tính quyết định, không phải mặc định.
- **Vận hành:** cpu.stat + PSI nên lên dashboard trước cả latency — vì chúng **giải thích** latency thay vì trùng lặp nó.
- **An ninh:** cgroup là ranh giới DoS nội bộ (tenant này không dập được tenant kia) — xem thêm 2.7/9.1.
- **Lịch sử:** Từ O(1) scheduler (2003) → CFS (2007) → EEVDF (2023): mỗi lần đổi là đổi định nghĩa "công bằng"; ai đọc metric cũ theo nghĩa cũ sẽ chẩn sai.
- **Người dùng:** "App chập chờn lúc giờ cao điểm" thường là throttle trá hình — chương này dạy biến phàn nàn thành con số trong `cpu.stat`.

---

## 8. Đọc tiếp & bài tập

- I/O models: **2.5** · Network softirq: **2.6** · Pool sizing theo Little: **3.10** · K8s QoS: **9.1**
- **Bài tập 1:** Tìm mọi deployment của bạn có `limits.cpu` thập phân (ví dụ 500m). Chạy tải thật, đọc `nr_throttled`. Nếu > 0 và p99 tệ — bạn vừa tìm được tiền đang cháy.
- **Bài tập 2:** Đo `vmstat` cs/s của service tại 1× và 4× tải. Nếu cs tăng nhanh hơn throughput — kiến trúc concurrency đang tới trần.
- **Bài tập 3:** Gắn PSI avg10 vào dashboard hôm nay. Trong tháng tới, đếm bao nhiêu sự cố nó giải thích trước khi monitoring cũ kịp báo.
