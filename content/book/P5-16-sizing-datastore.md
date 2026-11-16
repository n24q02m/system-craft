# 5.16 — Công thức Sizing Datastore

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Sizing · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** sizing-ops.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 3.1 (luật Little) · 5.1 (ruột engine).

**Sợi chỉ đỏ:** *Chốt hạ tầng dữ liệu: bao nhiêu node, bao nhiêu GB, bao nhiêu tiền — tính kiểu gì?* — trả lời: sizing có công thức — từ workload (QPS, tỉ lệ đọc ghi, kích thước bản ghi) ra tài nguyên; con số quyết định là working set: dữ liệu nóng vừa RAM hay không định đoạt mọi thứ; headroom 2 lần không phải mê tín; và có ngưỡng dừng scale-up, bắt đầu scale-out. Câu hỏi để lại cho chương sau: *Backend đã có hình hài — nhưng khách cầm điện thoại, xuống hầm mất sóng, máy yếu pin: ràng buộc client đổi gì?*

**Thuật ngữ sẽ gặp:** *working set* — phần dữ liệu thật được đụng tới: vừa RAM hay không là ranh giới nhanh/chậm; *QPS × kích thước bản ghi* — thông lượng nhân cỡ dữ liệu = băng thông bắt buộc; *luật Little* — concurrency = throughput × latency: nối 3.1, tính pool và node; *headroom 2×* — gấp đôi cho giờ đỉnh và ngày một node chết: số liệu, không mê tín; *scale-up vs scale-out* — thêm RAM hay thêm máy: ngưỡng đổi chi phí có tính được; *bài toán ngược* — từ ngân sách ra SLA: chọn chỗ cắt.

**Ví dụ mở đầu:** Chốt hạ tầng dữ liệu DM: bao nhiêu node, bao nhiêu GB, bao nhiêu tiền — ba con số có công thức, không phải phỏng. Working set 60 GB nóng thì node 64 GB là tự sát: cache trượt liên tục. Bài toán ngược cũng giải được: ngân sách có hạn, SLA nào bán được cho chuỗi lớn. Chương này tính cả hai chiều trên chính DM.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Dung lượng + IOPS + throughput mục tiêu 18 tháng | Công thức nào — số nào — ai review? |
| 2 | Headroom (đệm) từng lớp: bao nhiêu % là khoa học | 2×? 3×? — hay "bao nhiêu đủ ngủ ngon"? |
| 3 | Điểm "dừng mua, bắt đầu shard" | Ngưỡng scale-up hết hiệu lực tính khi nào? |
| 4 | Chi phí cho 3 hình: đúng giờ, dư, thiếu | Thiếu lúc Black Friday đáng giá bao nhiêu? |

---

## 2. Cơ chế

### 2.1 Công thức nền — từ workload ra tài nguyên

```
Storage = data_raw × nén_đúng (1–10×) × replication × growth^t × (1 + overhead 20–50%)
RAM     = working_set (dữ liệu nóng) + overhead engine (heap/index)
IOPS    = reads/s + writes/s × write_amp (→5.1)
Network = (reads×payload + replication traffic + backup) × peak factor
CPU     = IOPS driver (serialization) + query compute — đo, khó công thức
```

Ba con số đầu vào phải có chủ: **data_raw** (biết từ nghiệp vụ), **working_set** (đo từ hệ hiện tại/mvp), **growth** (từ sản phẩm — không phải "multiplying 10× cho chắc"). Peak factor: p99/ngày × mùa vụ (Black Friday 3–10× bình thường (I, ngành BNPL/VN e-com)).

### 2.2 Working set — con số quyết định RAM, quyết định mọi thứ

Định nghĩa: dữ liệu **được chạm** trong cửa sổ hiệu dụng (buffer pool/ cache giữ được). Đo: `cache hit ratio` của hệ hiện tại (→5.1 §6) — hit < 95% và working_set > RAM → thêm RAM hoặc thu hẹp working set (partition/partition pruning — TTL nóng). Working set thường **10–30% data tổng** (I) — sizing RAM theo tổng dữ liệu là lỗi kinh điển làm đốt tiền.

### 2.3 Headroom — vì sao "2×" không phải mê tín

Ba lý do cần đệm: (1) **đo đạc sai** (sai số 30–50% là bình thường trước production); (2) **spike + failover** (node chết → phần dồn: cluster N node sống N-1 phải gánh — cần headroom ≥ 1/(N-1)); (3) **thời gian phản ứng** (mua + deploy = tuần). Chuẩn sách: **CPU 50–60% là mục tiêu, 70% là ceiling (→3.1 queueing); disk 70% ceiling (compaction cần khoảng trống — →5.5); RAM theo working set × 1,5**. Trên ceiling không hành động = chọn thời điểm sự cố.

### 2.4 Ngưỡng "dừng scale-up, bắt đầu scale-out"

- RDBMS: đơn node tới ~vài TB + CPU đỉnh; đọc tách replica trước (→8.1); shard khi **write** vượt (không phải read);
- Wide-column/CH: shard ngay từ đầu theo thiết kế (→5.5/5.8);
- KV: khởi đầu 3 node nhỏ, scale bằng thêm shard — không "máy to";
- Lake: tự nhiên out (S3); sizing = **engine nodes** (compute tách storage).

Quy tắc: **shard muộn hơn tưởng, sớm hơn cần** — muộn = migration dưới áp lực (tệ nhất); sớm = pays ops phức tạp. Điểm đổi được tính từ công thức: khi write IOPS×write_amp đụng trần node to nhất có thể mua.

### 2.5 Bài toán ngược: từ ngân sách ra SLA

Có $X/tháng → config nào tối đa SLA? Ví dụ: $500/tháng → CH 3 node 8GB + 500GB NVMe hoặc managed PG 4 vCPU + 200GB — hai world khác nhau cho cùng tiền. **Kỹ năng trình bày: bảng "SLA theo giá"** (3 phương án: tối thiểu — khuyến nghị — thoải mái) cho người quyết định ký — đưa quyết định kỹ thuật về ngôn ngữ tiền.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Working set/data | ~10–30% | I | đo từng hệ |
| Peak mùa VN e-com | 3–10× ngày thường | I | qui năm |
| CPU mục tiêu / ceiling | 50–60% / 70% | P | →3.1 |
| Disk ceiling | ~70% | P | compaction room |
| Failover headroom | ≥ 1/(N−1) | V | số học |
| RAM đệm | × 1,5 working set | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Sizing là **đưa quyết định từ cảm giác về công thức có nguồn gốc số** — chính nó là kỹ năng kiến trúc, không phải việc "trước khi gọi cloud team".
- **S2:** Tham số trụ: cache hit, IOPS dùng vs trần, disk %, CPU p99, cost/1k request.
- **S3:** Headroom đổi tiền lấy thời gian phản ứng + sống sót failover — không phải "cho chắc ăn"; mức đệm phải gắn cơ chế (mùa vụ, N node, chu kỳ mua).
- **S4:** Compute-storage tách (lake/CH shared) làm sizing tách hai trục — câu chuyện "thêm đĩa" không kéo theo "thêm CPU" nữa; đổi tư duy bài toán.
- **S5:** AI workload (GPU + KV-cache + corpus — →12.4) mang hình sizing mới (VRAM! HBM — →1.5) nhưng công thức tư duy giống hệt: working set (KV cache) × headroom (burst) × peak factor.
- **S6:** Khi sự cố "hết tài nguyên": soát bài toán ngược — công thức sai ở đâu (working set? peak? growth?) thay vì chỉ "thêm máy" — cùng công thức sai sẽ tái diễn ở quy mô to hơn.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Cache hit tụt dần | Working set mọc (data lớn) | hit trend + data growth | §2.2 |
| Sự cố đúng mùa cao điểm | Không nhân peak factor | history peak | §2.1 |
| Failover chết dây chuyền | Không headroom 1/(N−1) | capacity khi mất 1 node | §2.3 |
| Migration dưới áp lực | Bỏ qua ngưỡng shard | write IOPS trend | §2.4 |
| Hóa đơn bất ngờ | Sizing không từ công thức | cost review | §2.5 |

---

## 6. Cách đo

```bash
# Hiện trạng — input thật cho công thức
#   storage: df -h / data + nén ratio (engine metric)
#   IOPS: iostat -xz 1 (r/s w/s — đỉnh & trung bình)
#   cache hit: engine metric (→5.1 §6)
#   network: node-level (replication + query traffic)

# Bài toán ngược: tính chi phí 3 phương án (min/recommended/dư)
#   — bảng cho người ký: SLA (p99, uptime) theo giá
```

Nguyên tắc: **sizing chỉ đáng tin khi cả ba con số đầu vào (data/working set/growth) có nguồn gốc** — một con "đoán cho chắc" làm cả công thức thành cảm giác đắt tiền.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự sizing:** managed autoscaling (đổi tiền + tin vendor — phù hợp tầng không phải lõi); đặt "khung" (min-max) tự động co giãn. **Thay mua đĩa:** TTL + archive xuống lớp rẻ (→5.13/5.9) — thường "thiếu chỗ" thật ra là "chưa ai dọn dẹp". **Thay RAM:** nén (columnar/TDE compression) đổi CPU lấy RAM.

Năm thấu kính:
- **Kinh tế:** Bảng "SLA theo giá" biến cuộc tranh "mua hay không" thành quyết định kinh doanh có thông tin — kỹ năng này đáng giá hơn mọi tối ưu kỹ thuật riêng lẻ trong chương.
- **Vận hành:** Sizing là tài liệu sống: review mỗi quý với số thật (đo) — bảng tính tĩnh 18 tháng là mớ giấy vô nghĩa.
- **An ninh:** Headroom cũng là an ninh (disk đầy = log dừng = audit mù); 70% ceiling có chức năng chống mất quan sát.
- **Lịch sử:** Từ "máy chủ vật lý mua 5 năm" → cloud giờ → autoscale — mỗi thế hệ rút ngắn chu kỳ phản ứng; headroom thu hẹp theo — nhưng không bao giờ về 0 (vật lý + mùa vụ không thương lượng).
- **Người dùng:** Người dùng không biết capacity planning tồn tại — họ chỉ biết "app sống qua đêm sale". Mỗi chữ số trong chương này tồn tại vì đêm đó.

---

## 8. Đọc tiếp & bài tập

- Queueing (vì sao 70%): **3.1** · Write amp: **5.1** · Compaction room: **5.5** · Sizing cụm AI: **12.4** · TCO/đám mây: **11.3**
- **Bài tập 1:** Tính working set thật của DB chính (từ cache hit + data size). So với RAM hiện tại — bạn đang trả cho đúng phần nóng hay toàn bộ?
- **Bài tập 2:** Lập bảng "SLA theo giá" 3 phương án cho dịch vụ chính (min/khuyến nghị/dư). Trình bày cho người quyết định — quan sát quyết định nhanh hơn thế nào.
- **Bài tập 3:** Mô phỏng mất 1 node lúc tải đỉnh: cluster còn gánh nổi không (CPU/IOPS/disk)? Nếu câu trả lời là "không biết" — headroom của bạn là con số may mắn, không phải thiết kế.
