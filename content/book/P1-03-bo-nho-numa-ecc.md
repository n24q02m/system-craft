# 1.3 — Bộ nhớ: DRAM, NUMA, ECC

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.2 (dòng cache).

**Sợi chỉ đỏ:** *Cache là tầng trên cùng — nhưng RAM lắp thật vào máy có gì mà spec không nói thẳng (NUMA, ECC)?* — trả lời: RAM lắp vào máy thật không phải một cái hồ phẳng — nó là các node nối bằng cầu (NUMA), các kênh định băng thông, và cần bảo hiểm chống bit lật (ECC); những thứ này quyết định số liệu sizing thật. Câu hỏi để lại cho chương sau: *Dữ liệu phải sống qua nhiều lần reboot — ổ SSD và RAID hứa gì, phản bội gì?*

**Thuật ngữ sẽ gặp:** *NUMA* — bộ nhớ chia theo node, mỗi node gần một nhóm CPU, qua cầu là chậm; *kênh* — số đường song song CPU nói chuyện RAM, quyết định băng thông; *băng thông vs độ trễ* — số byte/giây và thời gian chờ từng lần: hai thứ tăng khác nhau; *THP* — trang to 2 MB, hai mặt; *ECC* — bit dự phòng tự sửa lỗi bộ nhớ; *CXL/HBM* — hai lối mở rộng bộ nhớ ngoài phẳng cũ.

**Ví dụ mở đầu:** Server mới của DM chạy benchmark stream đạt đúng spec, nhưng dịch vụ được xếp vào node xa card mạng thì throughput rụt 30% — cùng máy, cùng code. Tờ spec ghi "2 TB RAM" mà không kể RAM đó là hai hòn đảo nối bằng cầu; không biết cầu ở đâu thì không chọn được chỗ đặt process.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Dùng loại DDR nào, bao nhiêu kênh cho máy mới | Tôi cần băng thông bao nhiêu GB/s cho workload đỉnh? Đã phủ kênh chưa? |
| 2 | Bố trí tiến trình theo NUMA | Node nào "gần" NIC nào, đĩa nào? Tôi có pin process vào node đúng chưa? |
| 3 | Bật hay tắt THP cho dịch vụ nhạy latency | Tôi đổi gì lấy gì khi bật THP? |
| 4 | ECC cho máy sản xuất: có hay không bao giờ thắc mắc | Tôi chấp nhận silent data corruption với xác suất nào? |

---

## 2. Cơ chế

### 2.1 Ô DRAM: một tụ điện đang rò

Mỗi bit DRAM là một transistor + một tụ điện nano. Tụ rò điện trong ~64 ms nên phải **refresh** liên tục — đó là lý do DRAM chậm hơn SRAM (cache) hàng chục lần và là lý do tồn tại trade-off mật độ/tốc độ giữa các thế hệ chip (DDR4 → DDR5 → GDDR → HBM, →1.5).

Tổ chức: bit → ô → **hàng (row)** → bank → rank → **kênh (channel)**. Mở một hàng tốn thời gian (tRCD, CAS, tRP) nên DRAM thích **truy cập cục bộ theo hàng** (row hit) — cùng một logic "cục bộ" với dòng cache ở 1.2, chỉ to hơn ~1000×.

### 2.2 Kênh và băng thông: con số quyết định sizing

DDR5-5600 chuyển ~44,8 GB/s/kênh (bậc: ~40–50 GB/s/kênh) (V). Máy 2 socket server có 8–12 kênh/socket: tổng ~350–550 GB/s (bậc) (I). Con số này là **băng thông lý thuyết**; thực tế đo được 70–85% là tốt.

Điều ít người nói: băng thông đó **chia sẻ cho mọi lõi** (đã tính ở 1.2 §S2). Nên "thêm RAM" chỉ giúp khi bottneck là **dung lượng**, không phải **băng thông** — hai thứ khác nhau và có);- dung lượng thiếu → OOM, swap, cache hit thấp → thêm RAM đúng;
- băng thông thiếu → thêm RAM cùng kênh không giải quyết gì.

### 2.3 NUMA: hai hòn đảo nối bằng cầu

Máy 2 socket: mỗi socket gắn nửa bộ nhớ, truy cập chéo qua liên kết (UPI/Infinity Fabric) với giá **~1,5–2× độ trễ local** và băng thông thấp hơn nhiều (I). Hệ điều hành gán trang theo chính sách — mặc định "local first", nhưng tiến trình dài hạn và page cache trôi tự do sẽ **lệch dần**.

```
        Socket 0                      Socket 1
   [Lõi ×N][MC: 0–255GB] ←—UPI—→ [Lõi ×M][MC: 256–511GB]
        │                               │
     NIC eth0                         NVMe 1
```

Ba bẫy kinh điển:
1. **Ứng dụng chạy node 0, NIC cắm node 1:** gói tin đi vào node 1, buffer ở node 1, xử lý ở node 0 — trả tiền cầu hai lần cho mỗi gói.
2. **GC quét toàn heap** chạm remote pages nhiều hơn mức GC log cho thấy.
3. **Cố first-touch từng thread khác node:** thread sinh dữ liệu ở node A, thread khác đọc ở node B.

### 2.4 THP: hai mặt của trang 2MB

Trang 2MB giảm số TLB miss — tốt cho throughput (một số workload DB tăng 5–15% (I)). Nhưng THP khuyết điểm: (a) **compaction stall** — kernel dồn dở trang vật lý để ghép trang lớn, tốn ms–hundreds ms, xảy ra **đúng lúc cấp phát lớn** → spike latency định kỳ. Nổi tiếng nhất: Redis/Valkey khuyến nghị tắt THP. (b) Bội đất phình 2MB/lần cấp. Chọn: bật cho batch/analytics; tắt (`madvise` hoặc `never`) cho dịch vụ nhạy p99 — và đo lại, đừng tin lore.

### 2.5 ECC: bảo hiểm chống bit flip

Tia vũ trụ, rò điện, hàn lỗi — bit lật âm thầm. ECC thêm chip parity để sửa 1 bit, phát 2 bit. Chi phí: ~12,5% chip bộ nhớ + chút độ trễ. Nghiên cứu kinh điển "DRAM Errors in the Wild" (Google, SOSP 2009) đo trên cả trăm nghìn máy: **~8% DIMM mỗi năm gặp lỗi có thể sửa được**, và lỗi có tính không gian–thời gian tập trung (I). Vài năm sau, "Scale-Up-Down" (Bairavasundaram et al., 2007) cho thấy lỗi corrupt trước khi ECC phát hiện ở tỉ lệ không zero → các hệ dữ liệu lớn cần checksum tầng ứng dụng.

Quyết định: **máy sản xuất không có ECC là lỗi thiết kế**, trừ khi đó là máy dev. Riêng hệ dữ liệu lớn (DB, queue) — thêm checksum tầng ứng dụng (PostgreSQL WAL checksum, Ceph scrub).

### 2.6 CXL và HBM: hai lối mở rộng

- **CXL (PCIe-based, →1.6):** gắn bộ nhớ ngoài kiểu cache-coherent — mở rộng dung lượng ~1,3–2× độ trễ DRAM local (I). Use case: tier ấm cho dữ liệu ít nóng; **không** thay DRAM cho đường nóng.
- **HBM3e/HBM4:** DRAM xếp tầng 3D sát die tính toán — băng thông 8 TB/s (HBM3e, GPU hiện hành) lên ~22 TB/s (HBM4, thế hệ Vera Rubin) (V). Chỉ có trên GPU/accelerator (→1.5) — đó chính là ranh giới kiến trúc quan trọng nhất thập kỷ này: **dữ liệu nóng dần chuyển sang sống cạnh chip tính**.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| DDR5-5600 mỗi kênh | ~44,8 GB/s | V | bậc 40–50 GB/s/kênh |
| Server 2S tổng băng thông | ~350–550 GB/s | I | 8–12 kênh/socket |
| NUMA remote/local | 1,5–2× độ trễ | I | băng thông tụt hơn nữa |
| THP size | 2 MB | V | compaction stall khi bật |
| Tỉ lệ DIMM lỗi/năm | ~8% (sửa được) | I | Google SOSP'09 — có kiểm chứng |
| HBM3e / HBM4 băng thông | ~8 / ~22 TB/s | V | theo stack, trên GPU |
| CXL thêm độ trễ | ~1,3–2× DRAM | I | tùy topology |

---

## 4. Suy luận kiến trúc

- **S1:** Băng thông DRAM là ràng buộc **mềm** ở mức cluster (mua thêm máy được), nhưng là ràng buộc **cứng** trong một máy — không phần mềm nào vượt qua được.
- **S2:** Tham số cần theo dõi không phải "RAM bao nhiêu GB" mà là: GB/s mỗi lõi, tỉ lệ remote NUMA, và major fault/s.
- **S3:** THP là hình mẫu của trade-off throughput/latency; CXL là hình mẫu của trade-off dung lượng/tốc độ. Cả hai không có đáp án chung — có đáp án đo được.
- **S4:** Băng thông mỗi lõi giảm dần theo thế hệ (lõi tăng nhanh hơn kênh DRAM) → mọi tối ưu băng thông (SoA, nén, columnar) tăng giá trị theo thời gian.
- **S5:** HBM phình nhanh vì AI — và kéo theo đó là sự "di dân" của đường nóng khỏi CPU DRAM sang die GPU HBM; hiểu HBM là hiểu vì sao kiến trúc serving thay đổi (→12.2).
- **S6:** Khi memory là cổ chai, cân nhắc lại cả chuỗi: bố cục dữ liệu (1.2) → lượng dữ liệu đọc (nén, chỉ mục) → vị trí dữ liệu (NUMA, CXL, HBM) → có đáng tính ở đây không (GPU).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Redis/DB spike p99 định kỳ | THP compaction | `/sys/kernel/mm/transparent_hugepage/enabled`; SLOWLOG | §2.4 |
| Thêm RAM xong vẫn chậm | Bottleneck băng thông, không phải dung lượng | `mlc` throughput vs latency curve | §2.2 |
| Latency "vô cớ" trên máy 2S | Remote NUMA | `numastat` (Numa_Hit vs Numa_Miss) | §2.3 |
| Node xử lý chậm hơn node kia | Thread/app phân bố lệch | `numactl -H` topology; pidstat theo node | §2.3 |
| Số liệu tính sai rải rác | Bit flip / ECC disabled | `edac-util`; `rasdaemon`; mc log | §2.5 |

---

## 6. Cách đo

```bash
numactl -H                    # topology: node, khoảng cách
numastat                      # hit/miss theo node — miss cao = bố trí sai
mlc --loaded_latency          # đường cong tải-băng thông (Intel)
                               # điểm gãy = băng thông thật của máy bạn
stream                        # băng thông triad đo thực tế
edac-util -v                  # lỗi ECC đã sửa (đừng chờ nó thành lỗi chưa sửa)
grep -i huge /proc/meminfo    # THP đang dùng bao nhiêu
```

Dấu hiệu cần nhớ: `Numa_Miss` cao kéo dài, băng thông đo bằng `mlc` thấp hơn spec > 30%, hoặc lỗi ECC tăng theo thời gian — ba thứ đó là còi báo động thật; phần còn lại là nhiễu.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay cho "thêm RAM":** nén trong bộ nhớ (zstd, các DB có memory-columnar nén), bớt dữ liệu đọc (index, chỉ lấy cột cần), dời tier (CXL / NVMe làm tier lạnh — cẩn thận độ trễ →1.4), hoặc phân mảnh ngang sang máy khác (→5.5). **Thay cho THP bật toàn cục:** `madvise` theo vùng — dịch vụ latency dùng trang 4KB, batch dùng 2MB.

Năm thấu kính:
- **Kinh tế:** RAM là chi phí vốn; băng thông là chi phí thiết kế. Tiền mua được thứ nhất, không mua được thứ hai.
- **Vận hành:** Dashboard nên có: Numa_Miss/s, PSI memory (→2.1), ECC corrected/s. Ba số đó dự báo 90% sự cố memory trước khi user phàn nàn.
- **An ninh:** Rowhammer — lật bit bằng cách "đấm" hàng liền kề — là cầu nối giữa vật lý và an ninh; ECC giảm nhưng không triệt tiêu (nhiều bit flip). Ghi nhớ khi chọn không ECC "để rẻ".
- **Lịch sử:** Cùng một cuộc tranh luận lặp lại 3 lần — ECC có đáng không (thập niên 90: PC nói không, server nói có), THP có đáng không (2010s), CXL có đáng không (2020s). Mỗi lần câu trả lời đều: "tùy workload — đo đi".
- **Người dùng:** Người dùng không bao giờ thấy RAM; họ thấy swipe/spinner. Nhiệm vụ của bạn là dịch spinner về một trong: thiếu băng thông, thiếu dung lượng, hoặc bậc nhớ sai (đĩa — →1.4).

---

## 8. Đọc tiếp & bài tập

- Cache & bố cục dữ liệu: **1.2** · Đĩa & SSD: **1.4** · Bus PCIe/CXL: **1.6** · HBM trên GPU: **1.5** · Vấn đề OOM thực tế: **2.1**
- **Bài tập 1:** Trên máy 2S, chạy `mlc` và vẽ đường cong loaded-latency. Đánh dấu điểm băng thông gãy — đó là "trần thật" của máy bạn.
- **Bài tập 2:** Pin một tiến trình stream lớn vào node xa NIC, rồi vào node gần NIC; đo throughput chênh nhau bao nhiêu %? Nếu < 10%, bạn đang đo gì đó khác không phải NUMA.
- **Bài tập 3:** Kiểm tra mọi máy sản xuất của bạn hôm nay: `/sys/devices/system/edac/mc` có tồn tại không? Nếu không — lập ticket ngay, đừng đợi sự cố dạy cho bài học ECC.
