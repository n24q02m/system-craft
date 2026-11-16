# 1.4 — Lưu trữ: SSD, RAID, độ bền

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.3 (bộ nhớ thật).

**Sợi chỉ đỏ:** *Dữ liệu phải sống qua nhiều lần reboot — ổ SSD và RAID hứa gì, phản bội gì?* — trả lời: dữ liệu sống qua reboot nhờ ổ SSD — nhưng SSD ghi theo trang, xoá theo khối, có ổ "nói dối" fsync; và RAID với đĩa terabyte không còn là lựa chọn an toàn mặc định như hai mươi năm trước — đó là bài toán xác suất. Câu hỏi để lại cho chương sau: *Có việc tính toán mà CPU không gánh nổi — khi nào GPU vào cuộc, và cái gì làm nó đắt?*

**Thuật ngữ sẽ gặp:** *NAND* — vật liệu lưu của SSD: ghi theo trang, xoá theo khối; *PLP* — tụ điện giữ đủ điện ghi xong khi mất nguồn: ranh giới ổ datacenter và ổ rẻ; *fsync* — lệnh cam kết dữ liệu thật xuống đĩa; *write amplification* — ghi 1 byte phải xoá/di chuyển cả khối; *RAID5/RAID10* — parity rẻ nhưng rebuild rủi ro vs mirror đắt nhưng an toàn; *URE* — lỗi không đọc được trong lúc rebuild.

**Ví dụ mở đầu:** Đêm thứ ba hằng tháng, job đối soát của DM chậm gấp bốn. Nguyên nhân: ổ SSD consumer làm WAL — đầy 80% thì việc dọn rác nội bộ của ổ tranh tài với ghi của job. "Đĩa nhanh" ghi trên hộp không nói nó giữ lời hứa fsync; khác biệt ấy có giá bằng những sự cố nửa đêm.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Loại SSD cho từng vai trò (write-heavy / read-mostly / cold) | Workload tôi ghi bao nhiêu TB/ngày? DWPD cần bao nhiêu? |
| 2 | Bảo vệ mất dữ liệu thế nào (RAID/EC/replication) | Tôi chịu mất bao nhiều byte, bao nhiêu phút, khi nào? |
| 3 | fsync/commit policy của DB nằm đâu trên trục bền–nhanh | Mỗi commit trả giá bao nhiêu IOPS? Có PLP chưa? |
| 4 | Dùng SMR được chưa (giá rẻ hơn) | Rebuild/copy lớn có xảy ra thường xuyên không? |

---

## 2. Cơ chế

### 2.1 NAND: trang ghi một lần, xoá theo khối

NAND không cho ghi đè. Cứ 4–16 KB phải ghi vào trang **trống**; xoá chỉ chạy theo **khối** (MB-scale). Hệ quả là **FTL (Flash Translation Layer)** — lớp firmware ánh xạ LBA logic → vị trí vật lý, dọn rác bằng **garbage collection (GC)**: ghép các trang còn sống vào khối mới, xoá khối cũ.

Từ đó sinh ra mọi hiện tượng kỳ lạ của SSD:

- **WAF (Write Amplification Factor):** ghi logic 1 GB có khi đụng vật lý 3–4 GB. DB ghi tuần tự đẹp → WAF ~1–1,5; ghi ngẫu nhiên nhỏ, ghi đè nhiều → WAF 3+.
- **Write cliff:** khi các khối trống cạn (vùng SLC-cache giả lập đầy), GC phải chạy **đồng thời với workload** → throughput sụp vài lần, latency phân tán rộng. Đây là lý do benchmark 60 giây nói dối bạn; benchmark 30 phút mới nói thật.
- **Tầng NAND: SLC → MLC → TLC → QLC:** mỗi bậc gấp số bit/cell (1→2→3→4), đổi lấy giá rẻ hơn nhưng P/E cycles giảm (~100k → ~3k → ~1k → ~hundreds (I)), tốc độ chậm hơn. QLC rẻ cho read-mostly; đừng dùng QLC cho WAL/journal.
- **PLP (Power Loss Protection):** tụ điện cho firmware kịp ghi bảng ánh xạ khi mất điện. **Có PLP:** fsync gần như miễn phí (vài µs); **không PLP (consumer SSD):** fsync buộc flush toàn bộ, trả giá ms — và một số đĩa consumer còn **nói dối** đã flush (đã bị bắt quả tang nhiều lần; dùng `fio` verify để kiểm tra). Đây là khác biệt giá thật giữa enterprise và consumer, không phải con số IOPS trên hộp.

### 2.2 NVMe vs SATA: hàng đợi mới

SATA giới hạn ~550 MB/s và hàng đợi sâu 32 (NCQ). NVMe chạy trên PCIe (→1.6): 64k hàng đợi × 64k depth mỗi đĩa, băng thông theo lane (Gen4 x4 ~7 GB/s, Gen5 x4 ~14 GB/s (V)). Với OLTP — workload hàng chờ sâu, lệnh nhỏ — NVMe không thắng vì throughput mà vì **độ trễ thấp ở QD cao**.

### 2.3 RAID và EC: độ dự phòng tính bằng số học

- **RAID 10 (mirror + stripe):** nhanh, chi phí 2×, chịu mất nhiều đĩa (mỗi bên còn một).
- **RAID 5/6 (parity):** chi phí 1,2–1,5×, nhưng rebuild đọc **toàn bộ** các đĩa còn lại. Với đĩa 8–16 TB, xác suất gặp URE (unreadable error, ~1 per 10^14–10^15 bit đọc (V)) trong một lần rebuild không còn thấp. RAID5 với đĩa TB-scale **không còn là kiến trúc an toàn** cho production — đây là thay đổi thực tiễn thật, không phải lo xa.
- **EC (erasure coding, k+m):** cùng phép tính parity kéo dài ra nhiều máy — chi phí ~1,3–1,5×, chịu mất m node nhưng **chỉ phù hợp dữ liệu lớn, lạnh** (object store, backup), vì đọc phải ghép k mảnh.
- **Replication 3× (→5.2):** anh em họ ở tầng dịch vụ, chọn khi cần độ trễ thấp và đơn giản logic.

### 2.4 SMR: ổ "giá rẻ" đổi lấy cạm bẫy

Shingled Magnetic Recording ghi đè lên track liền kề như mái ngói — ghi tuần tự đẹp, nhưng ghi đè/ngẫu nhiên buộc rewrite cả **zone** (hàng trăm MB). Năm 2020 WD bán SMR vào dòng WD Red (NAS!) mà không ghi rõ — cộng đồng bắt ra qua hiện tượng rebuild RAID chậm khủng khiếp. Bài học cấu trúc: **datasheet không phải hợp đồng; kiểm chứng bằng workload của bạn** (`fio` ghi ngẫu nhiên 30 phút, xem có cliff theo zone không).

### 2.5 Đo phân phối, không đo trung bình

Latency đĩa là phân phối đuôi dài: p99/p50 = 10–100× là bình thường ngay cả khi Healthy. Vậy nên mọi quyết định dựa trên "IOPS trung bình" là quyết định mù. Cách đo đúng ở mục 6; cách báo cáo đúng: p50/p99/p99.9 và max, kèm throughput.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| P/E: SLC/MLC/TLC/QLC | ~100k / ~3k / ~1k / ~300 | I | datasheet thường né con số |
| Enterprise DWPD | 1–3 (read-intensive), 10+ (write-intensive) | V | DWPD = drive writes per day |
| NVMe Gen4 x4 / Gen5 x4 | ~7 / ~14 GB/s | V | sequential, tươi |
| fsync có PLP | ~10 µs | P | so với ms trên đĩa consumer |
| URE | 1 / 10^14–10^15 bit | V | với đĩa 12 TB: đọc ~10 đĩa là gặp |
| RAID5 rebuild 12 TB | ~1–2 ngày | I | còn phụ thuộc tải nền |

---

## 4. Suy luận kiến trúc

- **S1:** Độ bền (durability) là ràng buộc **do vật lý đặt ra** — nó không thỏa hiệp được với ngân sách, chỉ **chuyển vị trí** (fsync mỗi commit → PLP SSD → WAL batch → replication async).
- **S2:** Tham số trụ: TB ghi/ngày, WAF ước lượng, DWPD required, thời gian rebuild chấp nhận được.
- **S3:** Mọi thứ ở tầng này là đổi công: giá/độ bền/tốc độ/độ trễ. RAID-EC đổi thời gian rebuild lấy chi phí; QLC đổi tuổi thọ lấy giá; async replication đổi RPO lấy throughput.
- **S4:** Mật độ tăng nhanh hơn tốc độ → **rebuild ngày càng tốn thời gian** → hệ phân tán chuyển sang EC + replication chéo máy, còn RAID truyền thống thu hẹp vào tầng máy đơn.
- **S5:** NVMe phình đến mức "đĩa-local gần nhanh bằng mạng-nội bộ" — làm suy yếu một loạt kiến trúc cache phân tán của thập kỷ trước; cân nhắc lại trước khi giữ chúng vì "vẫn chạy tốt".
- **S6:** Khi đĩa là cổ chai, lùi lại hỏi: ta có cần ghi nhiều vậy không (WAL tuning, batching — →5.2), cần đọc nhiều vậy không (index, cache — →5.4), rồi mới tới mua đĩa.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| p99 I/O vọt 100× giữa benchmark/production | GC cliff / SLC-cache cạn | `fio` sustained 30 phút; SMART `% wear` | §2.1 |
| Throughput sụp sau vài phút ghi lớn | QLC hết vùng cache | sustained write; so datasheet "up to" | §2.1 |
| RAID5 rebuild fail giữa chừng | URE / đĩa thứ 2 chết theo | `smartctl -a` tất cả đĩa; tính xác suất | §2.3 |
| DB commit chậm bất thường trên SSD mới | Consumer SSD, không PLP, fsync thật | `fio --fsync=1` so spec | §2.1 |
| Copy/rebuild đĩa mới chậm vô lý | SMR | model tra spec sheet; `fio` random write zone test | §2.4 |
| Đĩa "khỏe" nhưng latency phân tán rộng | Normal — đó là đĩa | histogram, đừng chữa | §2.5 |

---

## 6. Cách đo

```bash
# 1. Latency phân phối dưới tải thật (luôn chạy ≥ 15–30 phút)
fio --name=t --filename=/dev/nvme0n1 --direct=1 --rw=randrw --rwmixread=70 \
    --bs=4k --ioengine=io_uring --iodepth=32 --runtime=1800 \
    --group_reporting --percentile_list=50:99:99.9:99.99

# 2. Sức khỏe & tuổi thọ
smartctl -a /dev/nvme0n1        # Percentage Used, Data Units Written
                                 # → so với TBW spec → tuổi thòn còn lại

# 3. Kiểm tra fsync thật (đĩa có nói dối không)
fio --name=fsynctest --rw=randwrite --bs=4k --fsync=1 --direct=1 --runtime=60

# 4. Hàng đợi & bão hoà ở host
iostat -xz 1                     # %util, aqu-sz, await theo thiết bị
```

Nguyên tắc: **SMART là lời khai, fio là bằng chứng** — quyết định mua/sửa chỉ nên dựa trên đo dưới workload của chính bạn, trong thời gian đủ dài để cliff hiện ra.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay RAID5/cục bộ:** RAID10 cho máy DB; replication chéo máy cho dịch vụ (→5.2); EC cho object/lưu trữ lớn (→5.6). **Thay SSD đắt:** tách nóng/lạnh — NVMe cho nóng, SATA SSD cho ấm, object-store cho lạnh — nhưng đừng để tầng ẩm của bạn âm thầm trở thành tầng chậm của ai khác (→S6).

Năm thấu kính:
- **Kinh tế:** Chi phí thật = giá mua + chi phí rebuild + rủi ro mất dữ liệu × giá trị dữ liệu. Đĩa rẻ nhất thường đắt nhất trên phép tính đó.
- **Vận hành:** Cảnh báo nên có: SMART wear > 80%, throughput suy giảm so baseline, thời gian rebuild mô phỏng hàng năm.
- **An ninh:** Mất điện + SSD consumer nói dối fsync = mất transaction âm thầm; encryption-at-rest (→10.5) cộng thêm lớp phụ thuộc key — tính cả hai vào phương án.
- **Lịch sử:** Vòng lặp lặp lại: mỗi lần mật độ tăng (HDD GB → TB, SSD SATA → QLC), các kỷ luật cũ (RAID5 OK, benchmark 60s) chết và phải học lại. Đừng benchmark theo trí nhớ.
- **Người dùng:** Với người dùng, "lưu trữ" đồng nghĩa "không mất". Mọi thứ khác trong chương này là chi phí để giữ lời hứa đó.

---

## 8. Đọc tiếp & bài tập

- fsync/WAL từ phía DB: **5.2** · Object storage & EC: **5.6** · Bus PCIe của NVMe: **1.6** · Backup/recovery: **11.2**
- **Bài tập 1:** Chạy fio 4k randwrite 70/30 trong 5 phút rồi 30 phút trên SSD bạn định mua; so p99. Nếu khác > 2×, viết lại kết luận.
- **Bài tập 2:** Tính: cụm 12 đĩa 12 TB RAID5, URE 10^14 — xác suất rebuild sạch là bao nhiêu? Quyết định của bạn thay đổi thế nào với RAID10 cùng ngân sách?
- **Bài tập 3:** Tìm trong hệ thống của bạn một đĩa đang fsync-nói-dối (consumer SSD làm WAL/journal). Nếu tìm thấy trong 15 phút — chương này đã trả tiền cho thời gian của bạn.
