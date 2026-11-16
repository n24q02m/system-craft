# SYS101 — BỘ SLIDE 11 CHƯƠNG XƯƠNG SỐNG (★)

> **Hệ thống:** SYSTEMS ATLAS `SA-2028.1` · **Môn:** `SYS101 — Nền tảng Hệ thống (4 tín)`  
> **Nguồn duy nhất:** Trích rút từ `§0 + §1 + §3 + §5 + §6` của 11 chương `★` (`0.2 · 1.1 · 1.2 · 1.4 · 1.7 · 2.1 · 2.3 · 2.4 · 3.1 · 3.10 · 4.1`)  
> **Quy tắc giảng:** *Không có số thì không có điểm* · Đọc chậm §3 và đo trực tiếp trong Lab `L00–L04`.

---

## [0.2] 1/7 — Mười Tiền đề (Axioms) & Điều kiện biên

- **Vị trí trong tuyến học:** Cụm `P0` · Chương thứ 2 (Tuần 1) · **Đọc trước:** `0.1` (Hệ quy chiếu 7 Trục).
- **Câu hỏi nghề:** *"Tôi đang đứng trên những định luật vật lý/tổ chức nào — và định luật nào đang rạn nứt khiến kiến trúc 5 năm nữa phải viết lại?"*
- **Điểm mở đầu:** Sách không đoán tương lai; sách **tuyên bố tường minh 10 giả định nền** và gắn sẵn *"điều kiện viết lại"* cho từng giả định.

---

## [0.2] 2/7 — Bốn Quyết định Cốt lõi (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Tuyên bố tường minh 10 giả định nền | Tôi có biết mình đang đứng trên định luật nào — và cái nào sắp gãy? |
| **2** | Gắn *"điều kiện viết lại"* cho từng tiên đề | Tiên đề nào sập thì chương nào / hệ nào phải sửa? |
| **3** | Ghi rõ phạm vi loại trừ (Vòng 3) | Cái gì hệ thống/tài liệu cố tình **không** phủ để chữ "đủ" đo được? |
| **4** | Cơ chế soát lại theo ấn bản | Ai, bao lâu một lần, cập nhật khi có dấu hiệu rung? |

---

## [0.2] 3/7 — Mười Tiên đề Nền: A1 đến A5 (§2)

| # | Tiên đề | Độ lệch thật ngoài đời | Sập thì ảnh hưởng |
|---|---|---|---|
| **A1** | Nhị phân & von Neumann | Bit-flip soft error, analog/neuromorphic | `14.1.3` |
| **A2** | Đồng hồ lệch giữa các máy | NTP lệch ms–s; dùng đồng hồ logic để thoát | `8.1 · 13.1` |
| **A3** | Mạng mất/trùng/đảo gói | TCP/QUIC che bớt, không xoá TTL/partial fail | `4.x · 8.5` |
| **A4** | Phần cứng hỏng âm thầm | Silent data corruption, ECC không bắt hết | `1.4 · 14.1.3` |
| **A5** | Mật mã bất đối xứng tin được | Lượng tử uy hiếp RSA/ECC → di dân sang PQC | `10.2 · 14.10.2` |

---

## [0.2] 4/7 — Mười Tiên đề Nền: A6 đến A10 (§2)

| # | Tiên đề | Độ lệch thật ngoài đời | Sập thì ảnh hưởng |
|---|---|---|---|
| **A6** | CMOS tiếp tục co nhỏ *(từng thời)* | Moore chậm lại từ ~2015; HBM/wafer là tường | `1.2 · 14.1` |
| **A7** | Điện sẵn có và rẻ | Hết điện trước khi hết rack tại cloud/AI DC | `1.10 · 14.3` |
| **A8** | Chương trình tất định | LLM non-deterministic (`12.1`), GPU (`14.5.2`) | `12.1 · 14.5.2` |
| **A9** | Con người vận hành (Conway) | Mô hình hệ thay đổi theo luân chuyển đội | `11.4–11.7` |
| **A10** | Dữ liệu có chủ pháp lý | GDPR / PDPD / CRA thực thi ngày càng chặt | `10.8 · 5.13` |

---

## [0.2] 5/7 — Bảng Số & Mốc Kiểm Chứng (§3)

| Thông số | Giá trị chuẩn | Nhãn | Ý nghĩa thực chiến |
|---|---|---|---|
| Số tiên đề nền | **10** (`A1–A10`) | `V` | Bao phủ máy, mạng, điện, mật mã, người, luật |
| Chuẩn hoá PQC | **FIPS 203 / 204 / 205 (8/2024)** | `V` | Tiên đề A5 đã chuyển trạng thái sang di dân |
| Moore chậm lại | **~2015 trở đi** | `I` | Hết "ngồi yên chờ CPU nhanh gấp đôi mỗi 2 năm" |
| Nhịp đóng băng ấn bản | **Hàng quý** (`SA-2028.x`) | `P` | Chống tin vào số liệu công nghệ đã mục nát |

---

## [0.2] 6/7 — Hỏng Thế nào & Cách Rà Ngầm Định (§5–§6)

| Triệu chứng ngoài đời | Nguyên nhân | Cách kiểm chứng / xử lý |
|---|---|---|
| Cãi nhau "luật kiến trúc" không hồi kết | Hai bên mặc định 2 tiên đề khác nhau | Quy chiếu về bảng `A1–A10` |
| Tin số benchmark 4 năm trước | Không soát theo nhịp ấn bản | Kiểm tra `facts/versions.csv` & ngày đo |
| Thiết kế mất dữ liệu vì mất điện/lệch đồng hồ | Giả định ngầm phá `A2`, `A4` | Liệt kê giả định sập theo `7 trục` |

> **Thực hành tại lớp (10 phút):** Mỗi nhóm viết **3 giả định ngầm** của app quen dùng và gắn mã `A1–A10` nào bị vi phạm khi app sập.

---

## [0.2] 7/7 — Bài Tập & Điểm Neo Chương 0.2

- **Đo đạc / đối chiếu:** Kết nối với **Lab L0** (`P15-03-L00`: bản đồ 7 trục một hệ thật) + câu `Q00` (`P15-02-Q00`).
- **Chuẩn nộp bài (Rubric §05):**
  1. Chỉ rõ tiên đề nào (`A1–A10`) bị chạm khi đưa giả định thiết kế.
  2. Không viết chung chung *"mạng ổn định"* hay *"đĩa bền vững"* mà không kèm ngưỡng URE / RTT / RPO.
  3. Chốt 1 dòng: **Nếu tiên đề này sai thì hệ thống mất gì và kiểm bằng gì?**

---

## [1.1] 1/7 — Bậc thang Độ trễ (Latency Numbers)

- **Vị trí trong tuyến học:** Cụm `P1` · Tuần 3 · **Đọc trước:** `0.1`.
- **Ví dụ mở đầu:** Khách bấm *"Đặt món"* và chờ **800 ms**. Thời gian đó là một tháp: `1 ns` L1 vs `100 ns` DRAM vs `100 µs` NVMe vs `500 µs` RTT cùng DC vs `150 ms` xuyên lục địa.
- **Sợi chỉ đỏ:** Phần lớn mọi bài toán hiệu năng thất bại ngay trên giấy vì nhầm **4–8 bậc độ lớn** giữa bộ nhớ, đĩa và mạng.

---

## [1.1] 2/7 — Bốn Quyết Định Phân Bổ Độ Trễ (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **D1** | Đặt ranh giới đồng bộ ở đâu | Nếu phép gọi nằm trên critical path tới người dùng, chịu được bao nhiêu ms? |
| **D2** | Tầng nào giữ dữ liệu | In-process cache, Redis/Valkey, replica hay đọc đĩa gốc? |
| **D3** | Có bao nhiêu hop mạng mỗi request | Đếm hop × `~0,5 ms`: có lọt ngân sách p99 không? |
| **D4** | Chọn vùng (region) | Dữ liệu gốc ở đâu, người dùng ở đâu, khoảng cách cáp quang là bao nhiêu? |

---

## [1.1] 3/7 — Tháp Độ Trễ Từ L1 Tới Hà Nội ↔ Frankfurt (§3)

| Thao tác | Độ trễ | Tỉ lệ so L1 | Quy đổi (`1 ns = 1 s`) |
|---|---|---|---|
| L1 cache | `~1 ns` | `1×` | **1 giây** |
| DRAM | `~100 ns` | `100×` | **1 phút 40 giây** |
| Đọc 4 KB ngẫu nhiên NVMe | `~100 µs` | `100.000×` | **27,7 giờ** |
| RTT cùng datacenter | `~500 µs` | `500.000×` | **5,8 ngày** |
| Seek HDD | `~10 ms` | `10 triệu×` | **3,8 tháng** |
| RTT Hà Nội ↔ Frankfurt | `~150 ms` | `150 triệu×` | **4,8 năm** |

---

## [1.1] 4/7 — Con Số Cáp Quang & So Sánh Ngược (§3)

| Chặng / Thao tác | Độ trễ thực tế | Ghi chú quyết định |
|---|---|---|
| L2 / L3 cache | `~4 ns` / `~10–15 ns` | Dùng chung giữa các lõi; NUMA làm xa hơn |
| Branch mispredict | `~3–5 ns` | Xoá pipeline CPU |
| Nén 1 KB (`zstd`) | `~1–2 µs` | Rẻ hơn nhiều so với gửi qua mạng chậm |
| RTT khác AZ cùng region | `~1–2 ms` | Quorum ghi đồng bộ đa AZ trả giá mỗi lần |
| Hà Nội ↔ Singapore | `~35–45 ms` | Cáp ~2.300 km (tối thiểu lý thuyết ~23 ms) |

> **Nhìn theo chiều ngược:** Một vòng lặp `N+1` có `await db.query()` bên trong đặt **`~5,8 ngày`** lên từng phần tử!

---

## [1.1] 5/7 — Hỏng Thế Nào Theo Bậc Thang (§5)

| Triệu chứng | Nguyên nhân theo bậc thang | Xác nhận & Sửa |
|---|---|---|
| p50 ổn, p99 tăng theo tải | Hàng đợi phình theo định luật Little `L = λ × W` | Kiểm queue length vs concurrency worker |
| Cả hệ thống chậm cùng giờ | Nghẽn 1 tầng dùng chung (DB, DNS, Auth, NTP) | Đối chiếu span giữa các service |
| Request fail nhanh bất thường | Timeout ngắn hơn bậc độ trễ thật (`RTT × hop`) | Đặt timeout theo bậc thang từ ngoài vào trong |
| Tối ưu bằng cache vẫn chậm | Mất nhất quán / hit rate thấp / TTL trượt | Đo hit rate + số retry do stale data |

---

## [1.1] 6/7 — Đo Đúng, Đừng Đo Lệch (§6)

| Cần biết | Công cụ / Phương pháp đúng | Sai lầm phổ biến (cấm dùng) |
|---|---|---|
| Độ trễ khách cảm nhận | **RUM** ở browser / app thật | Chỉ đo access log server |
| Độ trễ từng hop | OpenTelemetry span + trace | Log string *"took X ms"* rời rạc |
| Đuôi phân phối | **Histogram** / HDR bucket tới `10 s` | Biểu đồ `avg()` trên dashboard |
| Tầng chậm nhất | Thay tầng bằng hằng số (`0 ms`) đo delta | Suy đoán theo trực giác |

---

## [1.1] 7/7 — Bài Kiểm Tại Lớp & Gắn Lab L1

- **Bài tính nhanh (CLO2):** Một API thanh toán gọi 4 hop nội bộ trong DC + 1 sync replicate sang AZ khác + 2 lần đọc NVMe. Hỏi sàn p50 vật lý không dưới bao nhiêu ms? *(~`4×0,5 + 1,5 + 0,2 ≈ 3,7 ms` — chưa tính serialize/DB logic)*.
- **Lab gắn kèm:** **Lab L1 (`P15-03-L01`)** — đo độ trễ RAM/cache trên máy `2 vCPU` bằng code thật.
- **Tự chấm:** Có phân biệt rõ p50 vs p99, có đủ hop + đơn vị?

---

## [1.2] 1/7 — CPU: Lõi, Cache, SIMD

- **Vị trí trong tuyến học:** Cụm `P1` · Tuần 3 · **Đọc trước:** `1.1`.
- **Ví dụ mở đầu:** Cùng ma trận `4096×4096` (~67 MB), duyệt theo hàng mất **~23 ms**, duyệt theo cột mất **~200 ms** — cùng thuật toán, khác biệt ~9× nằm hoàn toàn ở **dòng cache 64 byte** và bộ nạp trước phần cứng.

---

## [1.2] 2/7 — Bốn Quyết Định Kiến Trúc Tầng CPU (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Ước lượng chi phí theo bậc cache | Vòng lặp nóng đang đọc từ **L1** (`4–5 chu kỳ`) hay **DRAM** (`200–300 chu kỳ`)? |
| **2** | Bố cục dữ liệu (AoS vs SoA) | Mỗi truy cập đang kéo theo bao nhiêu byte rác cùng cache line **64 B**? |
| **3** | Có đáng vector hoá (SIMD) không | Dữ liệu có liền khối và ít nhánh để dùng `AVX2`/`NEON`/`SVE`? |
| **4** | Chọn ISA (`x86-64` / `ARM` / `RISC-V`) | Mua xung đơn lõi, hiệu năng/watt cloud (`Graviton`/`Axion`), hay hệ sinh thái mở? |

---

## [1.2] 3/7 — Dữ Liệu Tầng Vi Kiến Trúc (§3)

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Kích thước dòng cache | **64 B** *(vài ARM: 128 B)* | `V` | Đơn vị vận chuyển tối thiểu CPU ↔ RAM |
| Chu kỳ L1 / L2 / L3 / DRAM | **4–5 / ~12 / ~40–50 / 200–300** | `I` | Chênh ~50–70× chu kỳ máy |
| Retire width lõi server | **4–8 µops / chu kỳ** | `I` | Golden Cove, Zen 4/5 |
| Branch mispredict | **~15–20 chu kỳ** | `I` | Cẩn thận `if/else` ngẫu nhiên trong hot loop |
| Độ rộng SIMD | `AVX2: 256 bit` · `AVX-512: 512 bit` | `V` | `SVE2`: vector length tuỳ cấu hình |
| Truy cập NUMA remote | **~1,5–2×** DRAM local | `I` | Quan trọng trên máy multi-socket |

---

## [1.2] 4/7 — So Sánh 3 Kiến Trúc ISA (§2)

| Tiêu chí | x86-64 | ARM (Neoverse v9) | RISC-V (RV64GC) |
|---|---|---|---|
| **Thế mạnh** | Đơn lõi mạnh, hệ phần mềm chín muồi | Hiệu năng/watt tốt (`Graviton`, `Axion`) | Mở hoàn toàn, tuỳ biến chip/nhúng |
| **SIMD** | `AVX2` / `AVX-512` | `NEON` / `SVE2` | `V extension` (`128–1024 bit`) |
| **Khi nào chọn** | Workload legacy hoặc ưu tiên single-thread | Service cloud mới tính chi phí/watt | Embedded, accelerator đặc thù |

---

## [1.2] 5/7 — Năm Triệu Chứng Hỏng Phổ Biến (§5)

| Triệu chứng | Nguyên nhân thực chất | Lệnh chẩn đoán |
|---|---|---|
| Multi-thread chạy **chậm hơn** 1 thread | **False sharing** trên cùng cache line `64 B` | `perf c2c record` (xem `HITM`) |
| Thuật toán hay hơn vẫn chậm | Đang **memory-bound**, stall ở DRAM | `perf stat`: `IPC < 0,5` + `LLC-miss` cao |
| Bật SIMD nhưng không tăng tốc | Branch / pointer aliasing cản vector hoá | Flag biên dịch `-Rpass=loop-vectorize` |
| Service bị tụt xung khi láng giềng chạy | `AVX-512` downclock / chia chung turbo budget | `turbostat` khi chạy cô lập vs chạy chung |

---

## [1.2] 6/7 — Đo Trên Máy 2 vCPU & Bẫy "Kết Quả Rỗng" (§6)

1. Luôn bắt đầu bằng `perf stat` để đọc **`IPC` (Instructions Per Cycle)** và **`LLC-load-misses`**.
2. Đo off-CPU wait (chờ lock/I/O) bằng **off-CPU flamegraph** (`eBPF` / `offcputime`), đừng chỉ đọc on-CPU sample!
3. **Bẫy Cloud VM (2 vCPU):** Một số VM đám mây tắt PMU counter phần cứng (`cycles`/`LLC-misses` hiện `<not supported>`) — ghi rõ *"không đo được trên vPMU, kiểm tra lại bằng wall-clock timing theo mảng N nhỏ → N lớn"* trong **Lab L1** (`P15-03-L01`)!

---

## [1.2] 7/7 — Bài Tập Kiểm Chứng Tại Lớp

- **Thực nghiệm 5 phút:** Cho 2 vòng lặp cộng mảng `int64` step=1 vs step=16 (64–128 B). Giải thích vì sao step=16 giảm tốc dù số phép cộng giảm **16 lần**?
- **Chốt kiến thức:** Cache không thuộc về C/Rust hay Java — mọi ngôn ngữ cuối cùng vẫn qua **cùng một dòng cache 64 byte** và **cùng một tháp chu kỳ L1/L2/L3/DRAM**.

---

## [1.4] 1/7 — Lưu trữ: SSD, RAID & Độ bền Dữ liệu

- **Vị trí trong tuyến học:** Cụm `P1` · Tuần 4 · **Đọc trước:** `1.3` (RAM thật).
- **Ví dụ mở đầu:** Đêm thứ ba hằng tháng job đối soát chậm **×4**: ổ SSD consumer dùng làm WAL bị ghi đầy 80%, garbage collection NAND + không có tụ PLP khiến mọi `fsync` từ `µs` vọt lên `ms`.

---

## [1.4] 2/7 — Bốn Quyết Định Tầng Lưu Trữ (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Chọn loại SSD cho từng vai trò | Workload ghi bao nhiêu **TB/ngày**? Cần `DWPD` `1–3` hay `10+`? |
| **2** | Cơ chế chống mất dữ liệu (RAID/EC/Replication) | Chịu mất tối đa bao nhiêu byte (**RPO**) và downtime bao lâu (**RTO**)? |
| **3** | Chính sách `fsync` của DB (bền vs nhanh) | Đĩa có **PLP** thật không hay đang nói dối? |
| **4** | Dùng đĩa từ SMR cho dữ liệu nguội? | Tác vụ rebuild / compaction kéo dài có làm nghẽn cả cụm? |

---

## [1.4] 3/7 — Bảng Số SSD, PLP & Độ Bền (§3)

| Thông số | Giá trị chuẩn | Nhãn | Hệ quả kiến trúc |
|---|---|---|---|
| Chu kỳ xoá P/E: `SLC/MLC/TLC/QLC` | **~100k / ~3k / ~1k / ~300** | `I` | QLC rẻ dung lượng nhưng chết nhanh nếu làm WAL |
| `Enterprise DWPD` | **1–3** *(read)* · **10+** *(write)* | `V` | `DWPD` = Drive Writes Per Day suốt bảo hành |
| Băng thông `NVMe Gen4 / Gen5 x4` | **~7 GB/s** / **~14 GB/s** *(tuần tự)* | `V` | Ngẫu nhiên 4 KB thấp hơn nhiều (`~100 µs`) |
| `fsync` có tụ **PLP** vs không PLP | **~10 µs** vs **~1–10 ms** | `P` | Chênh **100–1000×** IOPS ghi bền vững! |
| Tỉ lệ lỗi đọc **URE** | **1 / 10¹⁴–10¹⁵ bit** | `V` | Trên mảng đĩa `12 TB × 10 ổ`, xác suất gặp URE rất cao |
| Thời gian rebuild **RAID5 `12 TB`** | **~1–2 ngày** | `I` | Đọc kiệt toàn bộ ổ khác → rủi ro chết ổ thứ 2 khi rebuild |

---

## [1.4] 4/7 — Cơ Chế NAND, Write Amplification & RAID (§2)

- **NAND ghi theo trang (~4–16 KB) nhưng chỉ xoá được theo khối (~MB):** Đĩa đầy >75–80% khiến controller vừa đọc-chép-xoá dọn block (**write amplification**), kéo p99 latency tăng vọt.
- **PLP (Power Loss Protection):** Tụ điện trên SSD enterprise cho phép trả về `fsync OK` ngay khi ghi vào DRAM cache trên ổ, vì đảm bảo xả hết xuống NAND nếu sập nguồn. Đĩa consumer không có PLP: hoặc chậm (~ms) hoặc **tự ý giữ ở cache dễ bay hơi**.

---

## [1.4] 5/7 — Hỏng Thế Nào Khi Lưu Trữ "Phản Bội" (§5)

| Triệu chứng | Nguyên nhân | Chẩn đoán |
|---|---|---|
| DB ghi chậm đột ngột khi dung lượng ~80% | SSD hết block sạch, GC chạy liên tục | Xem độ trễ ghi `p99` dưới tải kéo dài (`fio`) |
| Rebuild RAID5 bị đứt giữa chừng | URE xảy ra ở ổ còn lại khi đọc 100 TB | Bỏ RAID5 mảng HDD lớn → RAID10 / Erasure Coding / Replica |
| `pgbench` đạt 10.000 TPS nhưng mất điện corrupt | Cache ghi đĩa bật mà không có PLP / flush barrier | Dùng `pg_test_fsync` kiểm chứng từng chế độ flush |

---

## [1.4] 6/7 — Đo Lưu Trữ Đúng Cách (§6)

1. Chạy benchmark `fio` tối thiểu **15–30 phút** ở đúng mức đầy ổ (không benchmark đĩa trống tinh!).
2. Tách biệt chỉ số: **sequential GB/s** vs **random 4 KB QD1** vs **random 4 KB QD32** + p99 latency.
3. Dùng `smartctl` đọc **`Percentage Used` / `Data Units Written` / `Media Errors`** định kỳ — đừng đợi kernel báo I/O error mới thay.

---

## [1.4] 7/7 — Bài Tập Tính Xác Suất Rebuild Tuần 4

- **Đề toán nộp Tuần 4:** Một mảng RAID5 dùng ổ **12 TB × 12 ổ** (`URE = 10⁻¹⁴` bit). Tính tổng số bit cần đọc khi 1 ổ hỏng phải rebuild (`11 × 12 TB`), xác suất gặp ít nhất 1 lỗi URE trong lúc rebuild, và quyết định kiến trúc thay thế *(RAID6 / RAID10 / object erasure coding + replication)*.

---

## [1.7] 1/7 — Mạng Vật Lý: Ánh Sáng, RTT, BDP & Đệm Switch

- **Vị trí trong tuyến học:** Cụm `P1` · Tuần 6 · **Đọc trước:** `1.1`.
- **Ví dụ mở đầu:** Đường truyền **10 Gbps** giữa hai datacenter có RTT **40 ms**. Khi copy một file lớn chỉ qua một TCP flow mặc định với buffer nhỏ, tốc độ kẹt ở **~100 MB/s** dù mạng rảnh 90%!

---

## [1.7] 2/7 — Bốn Quyết Định Về Vận Tốc & Đường Truyền (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Kích thước window / concurrency | **BDP** của đường truyền là bao nhiêu? TCP window có nhỏ hơn BDP không? |
| **2** | MTU chuẩn (`1500 B`) hay Jumbo (`9000 B`) | Đường đi qua overlay (`VXLAN` mất ~`50 B`) hay Internet công cộng? |
| **3** | Oversubscription tầng leaf–spine | Tải burst/incast có làm nghẽn uplink switch? |
| **4** | Đệm (buffer) switch & chiến lược xếp hàng | Chọn deep-buffer hay shallow-buffer + ECN? |

---

## [1.7] 3/7 — Bảng Số Vật Lý Không Đàm Phán Được (§3)

| Thông số | Giá trị chuẩn | Nhãn | Ý nghĩa |
|---|---|---|---|
| Vận tốc ánh sáng trong sợi quang | **~⅔c → ~5 µs/km** *(~10 µs/km RTT)* | `V` | Trần vật lý tuyệt đối, không phần mềm nào bẻ được |
| RTT nội cụm (cùng DC) | **0,1–1 ms** | `I` | |
| RTT cùng khu vực (same-region) | **1–10 ms** | `I` | |
| RTT liên lục địa (cáp biển) | **50–300 ms** *(vệ tinh LEO: 20–50 ms)* | `I` | Bổ sung yếu tố mất gói & đường vòng |
| **BDP (`10 Gbps × 30 ms`)** | **~37,5 MB** | `V` | `throughput ≤ window / RTT` |
| **MTU Ethernet** | **1500 B** *(jumbo **9000 B**)* | `V` | VXLAN/overlay cắt bớt ~50 B |
| Buffer datacenter switch | **~MB-scale** *(chia chung cổng)* | `I` | Khác router WAN (`GB-scale` gây bufferbloat) |

---

## [1.7] 4/7 — Giải Bài Toán Mở Đầu Bằng Công Thức BDP (§2)

> **`BDP = Bandwidth × RTT`**

- Đường truyền `10 Gbps` (= `1,25 GB/s`), `RTT = 40 ms` (`0,04 s`):  
  `BDP = 1,25 GB/s × 0,04 s = 50 MB` cần luôn "nằm trên dây".
- Nếu `tcp_rmem` / `SO_RCVBUF` kẹp ở `4 MB` (`1 flow`), tốc độ tối đa bị chặn cứng bởi vật lý:  
  `4 MB / 0,04 s = 100 MB/s = 0,8 Gbps` (< 1/10 dung lượng thuê!).
- **Hai hướng mở khoá:** Tăng TCP window tuning (`rmem`/`wmem` & autotuning) **hoặc** chạy nhiều kết nối song song / **BBR** trên đường mất gói.

---

## [1.7] 5/7 — Hỏng Thế Nào Ở Đường Truyền Vật Lý (§5)

| Triệu chứng | Nguyên nhân thực chất | Chẩn đoán |
|---|---|---|
| Tốc độ xa chậm hẳn dù link rảnh | Cửa sổ TCP nhỏ hơn BDP hoặc packet loss nhỏ phạt `CUBIC` | Chạy `iperf3` `1` vs `8` stream; xem retransmit (`ss -ti`) |
| Packet drop hàng loạt dù average traffic 20% | **Incast microburst** làm tràn buffer switch ~MB | Đọc drop counter switch theo sub-second |
| Gói lớn timeout âm thầm trong VPN/K8s | MTU `1500` lọt qua `VXLAN` bị fragment/blackhole PMTUD | `tracepath` / `ping -M do -s 1472` |

---

## [1.7] 6/7 — Đo Trên Hệ Thật (§6)

- Đừng dùng ICMP `ping` làm chân lý duy nhất (nhiều router hạ ưu tiên hoặc chặn ICMP): đo RTT tầng ứng dụng (`curl -w`, TLS/HTTP handshake hoặc gRPC ping).
- Kiểm tra `ss -ti` (xem `cwnd`, `rtt`, `retrans`, `pacing_rate`, `bytes_acked`) để biết ngay đang bị nghẽn do **ứng dụng**, **cửa sổ nhận** hay **congestion window**.

---

## [1.7] 7/7 — Bài Tập Kiểm Chứng & Gắn Tầng Giao Tiếp

- **Gắn tiếp chương `4.1`:** Mọi tối ưu ở `HTTP/2`, `HTTP/3`, `QUIC`, `BBRv3` sau này đều chỉ xoay quanh 2 nút vặn vật lý từ `1.7`: **giảm số RTT bắt tay** và **không để mất gói làm sập `cwnd` dưới BDP**.

---

## [2.1] 1/7 — Bộ nhớ Ảo, Page Table, TLB, HugePages & OOM Killer

- **Vị trí trong tuyến học:** Cụm `P2` · Tuần 7 · **Đọc trước:** `1.2`, `1.3`.
- **Ví dụ mở đầu:** Dashboard báo service thanh toán ăn **2 GB RAM**, service log ăn **2 GB RAM** — nhưng máy **8 GB RAM** lại kích hoạt **OOM Killer**! Tại sao? Đọc `RSS` đếm cả trang dùng chung vs **Copy-on-Write / Anonymous + Page Cache**.

---

## [2.1] 2/7 — Bốn Quyết Định Về Bộ Nhớ Tiến Trình (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Chính sách overcommit (`vm.overcommit_memory` `0/1/2`) | Từ chối `malloc` sớm khi hết cam kết, hay cho chạy tới khi OOM Killer hạ gục? |
| **2** | Cgroup v2 `memory.max` + `memory.high` | Ngưỡng bóp mềm (*throttling/reclaim*) ở đâu so với giới hạn chết cứng (*OOM*)? |
| **3** | Static `HugePages` vs Transparent (`THP`) | Dùng trang `2 MB` giảm TLB miss cho DB/JVM, hay tránh `compaction stall` của THP? |
| **4** | Cô lập workload hay `fork()` (`Redis BGSAVE`) | Dự phòng `1,3–2×` RAM cho burst **Copy-on-Write (COW)** chưa? |

---

## [2.1] 3/7 — Thông Số Chuẩn Bộ Nhớ Ảo (§3)

| Thông số | Giá trị bậc | Nhãn | Hệ quả |
|---|---|---|---|
| Kích thước trang (page) | **4 KB** · Huge: **2 MB / 1 GB** | `V` | `8 GB RAM` = `~2 triệu` trang `4 KB` |
| Số mục **TLB** mỗi lõi | **~1–2k entries/lõi** | `I` | Quá nhiều working set ngẫu nhiên → TLB miss! |
| Page table walk (4 tầng) | **~4 lần đọc bộ nhớ** khi TLB miss | `I` | Mỗi miss tốn hàng trăm chu kỳ |
| Overhead Python/Go vs C | **2–10×** bộ nhớ trên cùng logic | `I` | Object header, pointer, GC headroom |
| COW khi **Redis BGSAVE** | Footprint tăng **~1,3–2×** trong vài giây | `I` | Phải chừa trống RAM trước khi snapshot |

---

## [2.1] 4/7 — Phân Biệt `VSZ`, `RSS`, `PSS` & `USS` (§2)

- **`VSZ` (Virtual Size):** Tổng vùng địa chỉ đã cấp trên giấy (có thể hàng chục GB dù chưa chạm RAM thật).
- **`RSS` (Resident Set Size):** Tổng trang đang nằm trong RAM *kể cả trang thư viện chia sẻ* (cộng `RSS` mọi process sẽ vượt tổng RAM vật lý!).
- **`PSS` (Proportional Set Size):** Trang chia sẻ được chia đều cho số process cùng dùng → tổng `PSS` phản ánh **sát RAM thật bị chiếm**.
- **`memory.high` vs `memory.max`:** Chạm `memory.high`, kernel ép cgroup đi reclaim chậm lại (**PSI memory tăng**) trước khi chạm trần `memory.max` gây OOM kill!

---

## [2.1] 5/7 — Hỏng Thế Nào & Bẫy OOM Killer (§5)

| Triệu chứng | Nguyên nhân | Chẩn đoán |
|---|---|---|
| Service chết không log exception | **OOM Killer** bắn `SIGKILL` | `dmesg -T | grep -i oom` · `memory.events` |
| Latency giật cục dù CPU & RAM dư | **THP compaction stall** / `kswapd` quét trang | `grep Compact /proc/vmstat` · **PSI** `memory` |
| Redis sập đúng lúc backup ban đêm | `BGSAVE` `fork()` + ghi nhiều → nổ **COW** | Kiểm tỷ lệ đổi trang khi snapshot + reserve 50% RAM |

---

## [2.1] 6/7 — Đo Áp Lực Bộ Nhớ Bằng `PSI` Thay `%RAM` (§6)

- `%RAM` cao chưa chắc xấu — Linux tận dụng RAM rảnh làm **page cache**!
- Hãy đọc **PSI (`/proc/pressure/memory`)** (`some avg10`, `full avg10`): cho biết tiến trình đang thật sự **bị kẹt chờ bộ nhớ** bao nhiêu `% thời gian`!
- Kiểm chi tiết anon vs file vs shared per-cgroup qua `/sys/fs/cgroup/.../memory.stat`.

---

## [2.1] 7/7 — Bài Tập & Gắn **Lab L2 (`P15-03-L02`)**

- **Lab L2:** Đặt `memory.high` thấp hơn nhu cầu làm việc trong cgroup v2 và quan sát trực tiếp **PSI (`memory.pressure`)** tăng trước khi tiến trình chạm `memory.max`.
- **Câu hỏi tự vấn:** Dịch vụ Redis / PostgreSQL production đang chạy có bật overcommit/THP đúng như khuyến nghị chưa — và lần gần nhất bạn đọc `dmesg` tìm `oom-killer` là bao giờ?

---

## [2.3] 1/7 — Process, Thread, EEVDF, `cgroups v2` & PSI

- **Vị trí trong tuyến học:** Cụm `P2` · Tuần 8 · **Đọc trước:** `2.2`, `1.2`.
- **Ví dụ mở đầu:** Hạ **K8s CPU limit** hoặc nâng từ `500m` lên `1000m`: tại sao **p99 latency giảm một nửa** dù `CPU utilization` trung bình chỉ **30%**? Bởi vì **`500m` không phải "nửa tốc độ xung nhịp"** — đó là **`50 ms` chạy trong mỗi chu kỳ `100 ms`, hết quota thì bị đóng băng hoàn toàn `50 ms` tiếp theo!**

---

## [2.3] 2/7 — Bốn Quyết Định Lập Lịch CPU (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Đặt `requests/limits CPU` & QoS class | `limits.cpu` có đang **CFS/EEVDF throttle** âm thầm cắt cụt p99? |
| **2** | Thread-per-connection hay worker pool cố định | Bao nhiêu worker là tối ưu theo số lõi (`CPU-bound`) hay Little's law (`I/O`)? |
| **3** | Burstable hay Guaranteed CPU | Tôi đang trả tiền cho p50 rảnh hay trả cho **p99** không bị giành CPU? |
| **4** | `nice` / `cpu.weight` giữa foreground & background | Job nén log/backup có đang đẩy service API vào hàng đợi runnable? |

---

## [2.3] 3/7 — Thông Số Chuẩn Scheduler & Context Switch (§3)

| Thông số | Giá trị chuẩn | Nhãn | Ý nghĩa thực tế |
|---|---|---|---|
| Tạo thread / `fork()` | **~10 µs** / **~100 µs–ms** | `I` | Đừng spawn thread/process mới cho từng HTTP request! |
| Context switch *(cùng process)* | **~1–5 µs** | `I` | Plus **chi phí gián tiếp**: cache L1/L2/TLB bị nguội! |
| Syscall *(hậu mitigation CPU)* | **~100–300 ns+** | `I` | Spectre/Meltdown làm syscall đắt hơn rõ rệt |
| CFS/EEVDF quota period mặc định | **100 ms** | `V` | `500m` = `50 ms` chạy + `50 ms` chờ nếu dùng hết burst |
| Wakeup từ C-state sâu | **~10–100 µs** | `I` | Máy tiết kiệm điện làm wakeup chậm (`1.10`) |
| **EEVDF thay CFS** | **Linux kernel 6.6 (2023)** | `V` | Virtual deadline ưu tiên task ngắn/latency-sensitive tốt hơn |

---

## [2.3] 4/7 — Bẫy Kinh Điển: `nr_throttled` & Đa Luồng Quá Số Lõi (§2)

- Có `4 vCPU` nhưng ứng dụng Go/Java có `64` thread cùng chạy khi vừa nhận spike `10 ms`: cả `64` thread chia nhau ngốn sạch `50 ms` CPU quota của `500m` chỉ trong **`~1 ms` wall-clock**, rồi **toàn bộ pod bị throttle đứng yên `~99 ms` còn lại của period**!!
- Cố định thread/worker CPU-bound quanh số lõi cấp (`GOMAXPROCS` đọc từ cgroup quota!) tránh cả throttle lẫn context-switch storm.

---

## [2.3] 5/7 — Hỏng Thế Nào & Chỉ Dấu Cgroup Throttle (§5)

| Triệu chứng | Nguyên nhân | Lệnh chẩn đoán |
|---|---|---|
| p99 nhảy bậc theo bội số `100 ms` dù CPU avg 30% | **CPU throttling** do `limits.cpu` + đa luồng | `/sys/fs/cgroup/.../cpu.stat` (`nr_throttled`, `throttled_usec`) |
| System CPU time tăng vọt | Tạo/hủy thread liên tục hoặc contention futex | `vmstat 1` (cột `cs`), `pidstat -w` |
| Latency nền giật khi có noisy neighbor | Không cô lập `cpu.weight` / core pinning | Đọc **PSI CPU** (`/proc/pressure/cpu`) |

---

## [2.3] 6/7 — Đo Scheduler Trên Máy Thật (§6)

```bash
cat /sys/fs/cgroup/cpu.stat        # nr_throttled & throttled_usec
cat /proc/pressure/cpu             # PSI CPU some avg10/60/300
vmstat 1                           # cột r (run queue), cs (context switch/s)
```

> Nếu **`nr_throttled` tăng hàng giây** trong lúc service đang lag dù biểu đồ "% CPU" màu xanh chỉ ở 35%, thủ phạm chính là **`limits.cpu` quá chật so với số thread burst**.

---

## [2.3] 7/7 — Gắn **Lab L2 (`P15-03-L02`)** & Bài Nộp Tuần 8

- **Bài tập nộp Tuần 8:** Vẽ đường cong `context switch/s` và phân phối `latency` từ `vmstat` ở mức **`1×` vs `4×` tải thread**; chỉ rõ điểm gãy bắt đầu thừa luồng trên máy `2 vCPU`.

---

## [2.4] 1/7 — VFS, Page Cache & Ngữ Nghĩa Bền Vững (`fsync`/`O_DIRECT`)

- **Vị trí trong tuyến học:** Cụm `P2` · Tuần 9 · **Đọc trước:** `1.4`, `2.1`.
- **Ví dụ mở đầu:** App ghi xong file cấu hình mới, log báo *"Đã lưu thành công"*. **10 giây sau máy mất điện** → khởi động lại thấy file cũ *(hoặc file trắng 0 byte)*! Chữ *"Đã lưu"* mới nói chuyện với **Page Cache trong RAM**, hoàn toàn chưa chạm đĩa!

---

## [2.4] 2/7 — Bốn Quyết Định Khi Ghi Dữ Liệu (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Gọi `fsync` / `fdatasync` mỗi commit hay theo nhóm (group commit) | Mỗi lần gọi trả **`~10 µs`** *(PLP)* hay **`~1–10 ms`** *(non-PLP)*? Ai gánh? |
| **2** | Buffered I/O (qua Page Cache) hay `O_DIRECT` | DB tự quản lý buffer pool (Postgres/MySQL InnoDB) có nên bị double-cache? |
| **3** | Cấu hình `vm.dirty_ratio` / `dirty_background_ratio` | Cho phép dirty pages phình tới bao nhiêu % RAM trước khi kernel chặn toàn bộ app để flush? |
| **4** | Pattern ghi file an toàn trước crash | Đã dùng **`write temp → fsync(temp) → rename → fsync(dir)`** chưa? |

---

## [2.4] 3/7 — Thông Số Chuẩn Page Cache & `fsync` (§3)

| Thông số | Giá trị chuẩn | Nhãn | Ghi chú |
|---|---|---|---|
| `fsync` trên SSD có **PLP** / không PLP | **~10 µs** / **~1–10 ms** | `P` | Chênh 100–1000× bền vững (`1.4`) |
| `fdatasync` vs `fsync` | Rẻ hơn khi kích thước không đổi | `I` | Không ép flush metadata mtime nếu không cần |
| `dirty_ratio` / `dirty_background` | **20% / 10%** RAM | `V` | Trên máy `128 GB RAM`, `20%` = **`25 GB` chưa ghi xuống đĩa!** |
| Page cache hit | **~ns (tốc độ RAM)** | `V` | Đọc file lần 2 gần như tức thời |
| Căn lề `O_DIRECT` | **512 B – 4 KB** *(block size)* | `V` | Cấp buffer sai alignment sẽ báo lỗi `EINVAL` / `EIO` |

---

## [2.4] 4/7 — Giải Phẫu Crash-Safe File Write 4 Bước (§2)

1. Mở & ghi toàn bộ dữ liệu vào `config.tmp` *(cùng filesystem/thư mục đích để `rename` nguyên tử)*.
2. Gọi **`fsync(fd_tmp)`** — ép dữ liệu file mới xuống đĩa *(kể cả metadata size)*.
3. Gọi **`rename("config.tmp", "config.json")`** — cập nhật con trỏ thư mục nguyên tử.
4. Gọi **`fsync(fd_parent_dir)`** — **hay bị quên nhất!** Nếu không `fsync` thư mục cha, mất điện xong con trỏ file mới có thể biến mất khỏi directory entry!

---

## [2.4] 5/7 — Hỏng Thế Nào Ở Tầng VFS & Page Cache (§5)

| Triệu chứng | Nguyên nhân | Hậu quả & Kiểm tra |
|---|---|---|
| Máy có `64 GB RAM`, ghi file nhanh rồi đột ngột treo cứng | Chạm `vm.dirty_ratio` (12 GB dirty) → write stall đồng loạt | Hạ `vm.dirty_background_bytes` / `vm.dirty_bytes` |
| File JSON thành rỗng `0 B` sau cúp điện | Ghi trực tiếp không temp+rename, hoặc quên `fsync` temp | Audit mọi đoạn code ghi state/config/WAL |
| Database tốn gấp đôi RAM khi chạy trên VM | Buffer pool DB (`shared_buffers` / `InnoDB`) trùng với Page Cache | Hiểu rõ chế độ `buffered` vs `direct I/O` của engine |

---

## [2.4] 6/7 — Công Cụ Kiểm Chứng Độ Trung Thực Của Đĩa (§6)

- **`pg_test_fsync`**: Đo tốc độ thật các kiểu flush (`fdatasync`, `fsync`, `open_datasync`). Nếu con số vượt **hàng trăm nghìn sync/giây** trên đĩa không PLP → ổ hoặc hypervisor đang **nói dối `fsync`**!
- Theo dõi `/proc/meminfo` (`Dirty:`, `Writeback:`) và `iotop` / `biolatency` (`eBPF`).

---

## [2.4] 7/7 — Bài Nộp Thực Hành Tuần 9

- **Audit 4 bước ghi:** Lấy một đoạn code thực tế trong dự án đọc/ghi tệp cấu hình hoặc queue cục bộ; chỉ ra chính xác chỗ thiếu bước nào trong chuỗi **`temp → fsync(file) → rename → fsync(dir)`**.

---

## [3.1] 1/7 — Lý thuyết Đồng thời & 4 Trường phái Bộ nhớ

- **Vị trí trong tuyến học:** Cụm `P3` · Tuần 11 · **Đọc trước:** `1.2`, `2.3`.
- **Ví dụ mở đầu:** Hai shipper cùng nhìn thấy *"còn 1 suất giao nhanh"* và cùng nhận → tồn kho âm một (**-1**). Không phải do code "xấu" — mà do đọc-kiểm-ghi không nguyên tử dưới **concurrency**!
- Phân biệt rạch ròi: **Concurrency** = nhiều việc đan xen tiến trình (tổ chức code); **Parallelism** = nhiều việc chạy cùng một khoảnh khắc vật lý trên nhiều lõi (thực thi).

---

## [3.1] 2/7 — Bốn Quyết Định Khi Chọn Runtime & Mô Hình Chạy (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Event loop / Thread pool / Green thread / `async-await` | Bài toán chờ I/O nhiều hay nghiền CPU? Cả đội có né nổi *"function coloring"* / callback hell? |
| **2** | Trường phái bộ nhớ *(Tracing GC / Ref-Count / Ownership / Manual)* | Sản phẩm chấp nhận tail-pause ở mức **`µs`**, **`ms`**, hay **tuyệt đối 0**? |
| **3** | Mức song song theo **Định luật Amdahl** | Phần tuần tự bắt buộc (`lock`, DB single writer, GIL) chiếm bao nhiêu %? |
| **4** | **Backpressure** thay hàng đợi vô hạn | Hàng đợi dài tới ngưỡng nào thì phải trả `429` / từ chối ngay? |

---

## [3.1] 3/7 — Thông Số Chuẩn Đồng Thời & GC (§3)

| Thông số | Giá trị chuẩn | Nhãn | Ý nghĩa chọn công nghệ |
|---|---|---|---|
| Stack goroutine / Virtual Thread | **~KB lúc khởi đầu** | `V` | So với **`~8 MB` mặc định của OS thread** (`ulimit -s`) |
| Pause **Go GC** | **`< 1 ms` thường** | `V` | Tăng nhẹ CPU overhead bù lại p99 ổn |
| Pause **JVM ZGC** *(JDK 21+ gen)* | **`< 1 ms`** *(thiết kế < 10 ms max)* | `V` | Giải phóng khỏi ám ảnh *"Java GC stop-the-world hàng giây"* |
| **Utilization an toàn** | **70–80%** | `I` | Vượt 80%, độ trễ hàng đợi phình theo hàm `1 / (1 − ρ)`! |
| **Amdahl (`s = 10%`, `64 lõi`)** | **Tối đa `~7×`** *(không bao giờ `64×`!)* | `V` | `S(N) = 1 / (0,1 + 0,9 / 64) ≈ 8,7×` *(kèm sync cost ~7×)* |

---

## [3.1] 4/7 — Bốn Trường Phái Bộ Nhớ: Đổi Cái Gì Lấy Cái Gì (§2)

| Trường phái | Ngôn ngữ tiêu biểu | Được | Mất / Giá phải trả |
|---|---|---|---|
| **Tracing GC** | Go, Java, C#, JS/Node | Viết nhanh, an toàn con trỏ, ít bug bộ nhớ | Ăn thêm 2–3× RAM headroom + chi phí pause/CPU quét heap |
| **Reference Counting** | Python *(+GC chu kỳ)*, Swift | Giải phóng tức thì theo phạm vi | Tốn atomic increment trên đa luồng; dễ rò tham chiếu vòng |
| **Ownership & Borrow** | Rust | Không GC pause, an toàn compile-time | Đường cong học cao; mô hình đồ thị/vòng phức tạp khó viết |
| **Manual (`malloc/free`)** | C, C++, Zig | Kiểm soát layout từng byte (`1.2`) | Rủi ro bảo mật nghiêm trọng (*use-after-free*, *buffer overflow*) |

---

## [3.1] 5/7 — Hỏng Thế Nào Khi Đồng Thời Sai (§5)

| Triệu chứng | Nguyên nhân thực chất | Chẩn đoán |
|---|---|---|
| Nâng lên `64 vCPU` nhưng throughput tăng `1,5×` | Nút cổ chai tuần tự (**Amdahl**: global lock, GIL, 1 row hot) | Off-CPU flamegraph tìm lock hotspot |
| Event loop bị đơ hàng trăm ms | Có **blocking I/O** / JSON khổng lồ chạy thẳng trên event loop | `PYTHONASYNCIODEBUG=1` · event-loop lag metric |
| Memory tăng tuyến tính tới khi OOM dưới spike | Không chặn **queue vô hạn** (channel/task backlog) | Kiểm bounded queue depth + load shedding |

---

## [3.1] 6/7 — Ba Thao Tác Đo Bắt Buộc Ở Tầng Runtime (§6)

1. **Kiểm chứng định luật Little (`L = λ × W`):** So `request đang xử lý` (`throughput × latency`) với `tổng kết nối/worker đang giữ`. Chênh lớn = có queue ngầm đang phình!
2. **Vẽ `Utilization` và `Latency p99` trên cùng biểu đồ thời gian:** Nhận diện ngay điểm uốn phi tuyến quanh **70–80%**.
3. **Bật race detector trong CI:** `go test -race` (**Lab L3**), `TSan` cho C/C++, blocking detector cho asyncio/Node.

---

## [3.1] 7/7 — Đọc Tiếp & Cầu Sang Ngôn Ngữ Cụ Thể (`3.2–3.9`)

- Từ nền `3.1`, các chương `3.2–3.8` (`Python/GIL-3.14t`, `Node`, `Go`, `Rust`, `Java Virtual Threads`, `C++`, `Wasm`) chỉ là **các lựa chọn kỹ thuật** đứng ở những toạ độ khác nhau trên 2 trục: **mô hình đồng thời × trường phái bộ nhớ**.
- **Lab L3 (`P15-03-L03`)**: đo tăng tốc JSON `orjson` (`~15×` từ tối ưu cấp thấp) + chạy `go test -race` bắt data race thật.

---

## [3.10] 1/7 — Giải Phẫu Tầng Phục Vụ (9 Trạm Của Một Request)

- **Vị trí trong tuyến học:** Cụm `P3` · Tuần 13–14 · **Đọc trước:** `3.1`, `3.4`.
- **Ý tưởng cốt lõi:** Mọi backend từ nhỏ tới lớn thực chất là **một dây chuyền gồm 9 trạm nối tiếp** (từ TLS/LB/Ingress → Parse → Auth/Validation → Business Logic → External/DB Call → Pool Queue → DB Engine → Response Serialize → Client Egress). Tắc ở *bất kỳ* 1 trạm nào cũng làm cả request chết.

---

## [3.10] 2/7 — Bốn Quyết Định Sizing & Timeout Tầng Phục Vụ (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Số worker / DB connection pool mỗi trạm | Đã tính bằng **`L = λ × W`** hay chỉ *"đặt đại `50` cho yên tâm"*? |
| **2** | **Timeout budget** toàn trình (truyền xuống từng trạm) | Tổng timeout các trạm con có lớn hơn timeout của caller? *(gây orphan work!)* |
| **3** | Kích thước hàng đợi tối đa ở mỗi trạm | Hàng đợi vô hạn nào đang âm thầm ăn RAM và đẩy latency thành 30 giây? |
| **4** | Điểm đặt **Retry** | Đặt ở đúng 1 tầng ngoài cùng (kèm jitter + budget) hay **mọi tầng cùng retry** tạo bão nhân cấp số mũ? |

---

## [3.10] 3/7 — Thông Số Chuẩn Tầng Phục Vụ (§3)

| Thông số | Giá trị chuẩn | Nhãn | Hệ quả thiết kế |
|---|---|---|---|
| Số trạm chuẩn của mô hình | **9 trạm** | `V` | Giúp debug từng đoạn thay vì nói chung *"API chậm"* |
| Hàng đợi bùng phát phi tuyến | **~70–80% utilization** | `I` | Quá ngưỡng này chỉ cần spike nhỏ là kẹt dây chuyền (`3.1`) |
| **Retry amplification** thực tế lúc sự cố | **1,2–2×** *(có thể thành **10×** nếu retry tầng chồng tầng!)* | `I` | Phải nhân vào phép tính pool & dùng retry budget (`8.5`) |
| Chi phí 1 kết nối DB (PostgreSQL backend) | **~vài MB RAM / conn** | `I` | `100` pod × pool `50` = **`5.000` conn → sập PostgreSQL** (`5.2`) |
| Hậu quả vi phạm timeout budget | **Công việc mồ côi (orphan work)** | `P` | Client đã bỏ đi nhưng server & DB vẫn đốt CPU cày tiếp! |

---

## [3.10] 4/7 — Công Thức Thực Chiến: Pool Sizing & Timeout Cascade (§2)

- **Pool DB:** Thực tế số connection cần cho một DB core CPU thấp hơn bạn nghĩ nhiều: công thức kinh nghiệm khởi điểm `≈ số lõi × 2 + hệ số I/O` *(~`20–100` tổng toàn cụm qua PgBouncer, không phải `5.000` direct!)*.
- **Deadline Propagation:** Caller gán `Deadline = now + 800 ms` vào header/gRPC metadata; mỗi trạm đọc deadline còn lại — còn `< 20 ms` thì **từ chối ngay (`DEADLINE_EXCEEDED`)** thay vì chạy tốn công vô ích!

---

## [3.10] 5/7 — Năm Triệu Chứng Sập Dây Chuyền Phục Vụ (§5)

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh / Metric kiểm tra |
|---|---|---|
| Client timeout `504` nhưng DB vẫn chạy cháy CPU | Không truyền timeout/cancellation xuống SQL query | Đối chiếu trace span cha vs thời lượng statement SQL |
| Cạn pool định kỳ lúc cao điểm nhẹ | Thiếu retry factor hoặc rò kết nối quên đóng | Metric `pool_wait_ms` & `active / idle` connections |
| p99 tăng cao nhưng CPU mọi máy đều thấp | Hàng đợi ở **1 trạm giữa** phình dài | Kiểm `queue_depth` riêng từng trong 9 trạm |
| Traffic tăng nhẹ → toàn cụm sập đứng | Thiếu load shedding + queue không giới hạn | Audit `max_queue` / `concurrency_limit` |

---

## [3.10] 6/7 — Ba Kiểm Chứng Phải Làm Trước Khi Go-Live (§6)

1. Đặt **OpenTelemetry span riêng** quanh mỗi trạm (ingress, auth, handler, DB query, external API) để thấy đúng trạm nào chiếm % p99.
2. Export 3 metric bắt buộc của mọi pool (HTTP client & DB driver): **`active`**, **`idle`**, **`waiting`** (`waiting > 0` kéo dài = pool hoặc DB đang là cổ chai).
3. Diff toàn bộ cấu hình timeout từ CDN → LB → Gateway → App → DB driver trên một bảng duy nhất: đảm bảo **ngoài > trong**.

---

## [3.10] 7/7 — Gắn **Lab L4 (`P15-03-L04`)** & Chuyển Mạch Sang HTTP/Mạng

- **Lab L4:** Benchmark 2 HTTP stack với payload thật, tách biệt thời gian CPU xử lý vs serialize vs mạng, ghi p50/p95/p99 và CPU/request.
- Sau khi làm chủ 9 trạm trong `3.10`, ta sẵn sàng sang **Cụm P4 (`4.1`–`4.9`)**: các kết nối đi ra khỏi hộp theo TCP/TLS/QUIC/HTTP/gRPC hoạt động thế nào?

---

## [4.1] 1/7 — Transport Hiện Đại: TCP (`BBRv3`), TLS 1.3 & QUIC

- **Vị trí trong tuyến học:** Cụm `P4` · Tuần 14 · **Đọc trước:** `2.6` (Linux netstack), `1.7` (RTT/BDP).
- **Câu hỏi mở đầu:** Mỗi request HTTPS mới từ điện thoại 4G Việt Nam trước khi gửi 1 byte HTTP đã mất bao nhiêu **RTT bắt tay**? Với TCP cũ + TLS 1.2 là **3–4 RTT** (~`150–200 ms` chết đứng!). Với **QUIC + TLS 1.3** chỉ còn **1 RTT** (hoặc `0-RTT` resume)!

---

## [4.1] 2/7 — Bốn Quyết Định Ở Tầng Transport (§1)

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **1** | Bật **TLS 1.3** và **`0-RTT`** ở đâu? | Endpoint nào **idempotent (`GET`)** để nhận `0-RTT` mà không dính lỗ hổng *replay attack*? |
| **2** | **mTLS nội bộ** service-to-service | Cần xác thực danh tính lẫn nhau (SPIFFE/mesh) hay chỉ mã hoá đường truyền? Ai xoay cert tự động? |
| **3** | Thuật toán kiểm soát tắc nghẽn (`CUBIC` vs `BBRv3`) | Đường truyền ra user cuối có bị lossy (`wifi/4G/xuyên lục địa`) như `1.7` đo chưa? |
| **4** | Bật **QUIC / HTTP/3** tại CDN / Edge chưa? | Tỷ lệ người dùng di động chuyển mạng IP (wifi ↔ 4G) chiếm bao nhiêu %? |

---

## [4.1] 3/7 — Thông Số Chuẩn TCP / TLS 1.3 / QUIC (§3)

| Thông số | Giá trị chuẩn | Nhãn | Ghi chú |
|---|---|---|---|
| **TLS 1.2 vs TLS 1.3 handshake** | **2-RTT vs 1-RTT** *(0-RTT resume)* | `V` | **RFC 8446** — bỏ cipher yếu, ẩn cert khi handshake |
| **QUIC + TLS gộp** | **1-RTT kết hợp cả transport + TLS** | `V` | **RFC 9001** — tránh *Head-of-Line Blocking* đa stream |
| **BBR vs CUBIC** trên đường lossy | **Nhiều lần throughput** | `I` | CUBIC thấy mất 1 gói liền chia đôi cửa sổ; BBR đo *bottleneck bandwidth + minRTT* |
| Vòng đời cert nội bộ tự động | **24 giờ – 90 ngày** | `I` | Không quản lý bằng file tay |
| CPU TLS handshake mới | **~ms mỗi kết nối không resume** | `I` | Tốn CPU nếu đóng-mở connection liên tục không pool/ticket |

---

## [4.1] 4/7 — Khi Nào Chọn Transport Nào (§2)

| Kịch bản hệ thống | Lựa chọn chuẩn | Lý do chính |
|---|---|---|
| **API công khai / App mobile** | HTTPS + **HTTP/3 (QUIC)** *(fallback H2)* | Chống đứng hình khi mất gói 4G + connection migration |
| **Nội bộ cùng datacenter** | **HTTP/2 hoặc gRPC trên TCP** | Ổn định, hỗ trợ hardware offload (`TSO/GRO`), ít bị firewall chặn |
| **Mạng enterprise bị chặn UDP** | **TCP + TLS 1.3 + `BBR`** | ~3–5% mạng doanh nghiệp chặn UDP port `443` |

---

## [4.1] 5/7 — Hỏng Thế Nào Ở Tầng Transport (§5)

| Triệu chứng | Nguyên nhân | Cách xác nhận & Sửa |
|---|---|---|
| CPU server tăng cao khi client kết nối mới nhiều | Tái lập TLS đầy đủ, thiếu **Session Ticket / Resume** | Kiểm tỷ lệ SSL session reuse · bật keep-alive |
| Yêu cầu `POST` thanh toán bị lặp 2 lần hiếm gặp | Bật **`0-RTT` trên non-idempotent route** bị attacker/mạng replay | **Tuyệt đối chỉ bật `0-RTT` cho safe/idempotent read** |
| Dịch vụ nội bộ chết đột ngột hàng loạt | Cert **mTLS hết hạn** do chưa có auto-rotation + alert | Đặt expiry alert `< 7 ngày` · tự động hoá ACME/SPIFFE |
| HTTP/3 không chạy ở văn phòng khách hàng | Middlebox / Firewall chặn UDP 443 | Luôn công bố `Alt-Svc` + giữ H2 fallback liền mạch |

---

## [4.1] 6/7 — Đo Tầng Transport Thực Chiến (§6)

```bash
curl -o /dev/null -s -w "dns=%{time_namelookup} tcp=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer}\n" target.internal:443
```

- So sánh **`tcp`** (`1 RTT`), **`tls - tcp`** (`1 RTT` ở TLS 1.3 vs `2 RTT` ở TLS 1.2) và kiểm **`%{http_version}`** xem có đang chạy `3`, `2`, hay kẹt về `1.1`!

---

## [4.1] 7/7 — Tổng Kết 11 Chương Xương Sống (`★`) Của `SYS101`

1. **Vật lý trước (`1.x`):** Bậc thang độ trễ (`1 ns` → `150 ms`), cache line `64 B`, PLP `fsync` (`10 µs` vs `10 ms`), `BDP = BW × RTT`.
2. **Hệ điều hành (`2.x`):** `PSS` & `PSI` (`memory.high`), `EEVDF` + cgroup `nr_throttled`, chuỗi ghi an toàn 4 bước (`temp → fsync → rename → fsync dir`).
3. **Runtime & Giao tiếp (`3.x–4.1`):** Định luật **Amdahl**, định luật **Little (`L = λ × W`)**, sử dụng **70–80% util**, **9 trạm phục vụ** với timeout phân tầng, và **TLS 1.3 / QUIC** cắt RTT bắt tay.
4. **Hẹn ở Tuần 15 (`SYS101` Thi cuối):** Không có số và không có phương án đo = tối đa nửa điểm!
