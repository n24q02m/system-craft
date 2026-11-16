# MÔN 1 — NỀN TẢNG HỆ THỐNG (4 tín)

### SYS101 · 45 tiết lý thuyết + 45 tiết thực hành · học kỳ 1 · sách: SYSTEMS ATLAS SA-2028.1, cụm **P0–P4 + 5.1/5.2/5.4**

> **Một câu mô tả môn:** học cách *nhìn thấy* trần vật lý của mọi hệ thống — từ bộ nhớ đệm CPU tới giới hạn của một kết nối TCP — rồi biến những trần đó thành quyết định thiết kế có số.
> **Không cần biết trước gì** ngoài lập trình cơ bản (một ngôn ngữ bất kỳ, biết vòng lặp và hàm). Môn này **không** dạy framework.

---

## 1. Chuẩn đầu ra (CLO) — kiểm được, không phải khẩu hiệu

| # | Sau môn này, sinh viên **làm được** | Kiểm bằng |
|---|---|---|
| CLO1 | Đọc một hệ thống lạ và **vẽ được bản đồ 7 trục** (độ trễ/thông lượng/chi phí/đúng đắn/vận hành/an ninh/tổ chức), chỉ ra trục nào đang là nút thắt | Bài kiểm 1 (tuần 3) |
| CLO2 | Tính **bậc độ lớn** cho một thiết kế: độ trễ, băng thông, dung lượng, tiền — sai số ≤ 1 bậc | Bài kiểm 2 (tuần 7) |
| CLO3 | Chẩn đoán một hệ chậm bằng **số đo** (không bằng phỏng đoán): chọn đúng 3 metric/tool cho 5 triệu chứng khác nhau | Lab 4 + thi cuối |
| CLO4 | Viết một **ADR 1 trang** có số, có phương án bị loại, có hạn xét lại | Bài tập nhóm (tuần 12) |
| CLO5 | Đọc một bài benchmark/blog kỹ thuật và **chỉ ra 3 điểm khiến nó không dùng được** cho quyết định của mình | Thi cuối (câu 5) |

## 2. Lịch 15 tuần (3 tiết LT + 3 tiết TH mỗi tuần)

| Tuần | Lý thuyết (chương sách) | Thực hành | Sinh viên nộp |
|---|---|---|---|
| 1 | 0.1 Hệ quy chiếu 7 trục · 0.2 Mười tiên đề · 0.3 Ma trận 5 lăng kính × 9 động từ | Lab L0: tự đo 1 hệ quen thuộc (máy tính của mình) | Bản đồ 7 trục của một app mình dùng |
| 2 | 0.4 Nhận thức luận: provenance, 5 mức tin cậy | Lab L0 (tt): kiểm chứng 3 con số trên Internet | 3 con số + nguồn + ngày |
| 3 | 1.1 Bậc thang độ trễ · 1.2 CPU, cache, SIMD | Lab L1: đo cache vs RAM (bài 1.2 Bài 2) | **Bài kiểm 1** (CLO1) |
| 4 | 1.3 Bộ nhớ DRAM/NUMA/ECC · 1.4 SSD, RAID, độ bền | Lab L1 (tt): tính RAID5 12×12 TB | Bài tính xác suất rebuild |
| 5 | 1.5 GPU & accelerator · 1.6 Bus: PCIe, NVLink, RDMA | Lab: đo băng thông thật vs spec | Bảng "trần thật" của máy mình |
| 6 | 1.7 Mạng vật lý: RTT, BDP · 1.8 Ảo hoá, cloud, TEE · 1.9 Đồng hồ NTP/PTP | Lab: `chronyc tracking` trên 3 máy | Báo cáo offset |
| 7 | 1.10 Điện, nhiệt, làm mát (PUE) · 2.1 Bộ nhớ ảo, OOM killer | Lab L2: `memory.high`, PSI | **Bài kiểm 2** (CLO2) |
| 8 | 2.2 Stack/heap/allocator · 2.3 Process/thread, EEVDF, cgroups | Lab L2 (tt): `vmstat` 1× vs 4× tải | Đường cong context switch |
| 9 | 2.4 VFS, pagecache, fsync · 2.5 Mô hình I/O, io_uring | Lab: audit 4 bước ghi config | Danh sách chỗ thiếu fsync |
| 10 | 2.6 Network stack, socket tuning · 2.7 Cô lập, microVM · 2.8 eBPF | Lab L2: bpftrace `openat()` của DB | Histogram + kết luận |
| 11 | 3.1 Đồng thời & GC · 3.2 Python · 3.3 Node | Lab L3: `orjson` (đo 15,2×) | Số đo trước/sau |
| 12 | 3.4 Go · 3.5 Rust · 3.6 Java (virtual threads) · 3.7 C++ | Lab L3: `go test -race` trên repo thật | **ADR 1 trang** (CLO4) |
| 13 | 3.8 Wasm/WASI · 3.9 Ma trận runtime (contract test) · 3.10 Giải phẫu tầng phục vụ · 3.11 HTTP stack 6 ngôn ngữ | Lab: contract test Python↔Node (int64 > 2⁵³) | Bảng contract 5 ca |
| 14 | 4.1 TCP/TLS/QUIC · 4.2 HTTP/1·2·3 · 4.3 REST/OpenAPI · 4.4 gRPC · 4.5 GraphQL & tRPC · 4.6 SSE/WebSocket | Lab L4: benchmark 2 stack với payload thật | Bảng p99 + CPU/request |
| 15 | 4.7 AsyncAPI/CloudEvents · 4.8 Vòng đời API · 4.9 Ma trận chọn giao thức · 5.1–5.2·5.4 (Storage/RDBMS/KV cốt lõi) | Ôn + thi thực hành | **Thi cuối** (CLO3, CLO5) |

**Chương bắt buộc đọc kỹ (đánh dấu ★ trong sách):** 0.2 · 1.1 · 1.2 · 1.4 · 1.7 · 2.1 · 2.3 · 2.4 · 3.1 · 3.10 · 4.1. Mười một chương này là "xương sống"; các chương còn lại đọc để biết mình sẽ tra ở đâu.

## 3. Đánh giá

| Thành phần | Trọng số | Hình thức |
|---|---|---|
| Bài kiểm 1 (tuần 3) | 10% | 45 phút, giấy, không tài liệu — vẽ bản đồ 7 trục + chỉ nút thắt |
| Bài kiểm 2 (tuần 7) | 15% | 60 phút — 5 bài tính bậc độ lớn (độ trễ/băng thông/tiền) |
| Lab (10 bài, chấm 5 bài) | 25% | nộp **số đo + lệnh + kết luận**; không có số = 0 điểm |
| ADR nhóm (tuần 12) | 15% | 1 trang, có phương án bị loại, có hạn xét lại |
| Thi cuối | 35% | 120 phút: 3 bài tính + 2 câu chẩn đoán + 1 câu phê bình benchmark |

**Quy tắc chấm xuyên suốt:** *không có số thì không có điểm*. Một câu trả lời đúng ý nhưng không có con số hoặc ngưỡng hành động được tính **nửa điểm** — vì ngoài đời nó không dùng được.

## 4. Vì sao môn này thay được môn "hệ điều hành + kiến trúc máy tính + mạng" của chương trình cũ

Ba môn cũ thường dạy **cơ chế tách rời** và kiểm bằng bài tập tính toán trên giấy. Môn này dạy cùng cơ chế nhưng **buộc phải đo trên máy thật** và **buộc phải ra quyết định**:

| Môn cũ | Môn này (SYS101) |
|---|---|
| Kiến trúc máy tính: pipeline, cache, số nhị phân | 1.1–1.4 + lab đo cache vs RAM, tính RAID — vẫn đủ lý thuyết, thêm **hệ quả thiết kế** |
| Hệ điều hành: process, bộ nhớ ảo, file system | 2.1–2.6 + lab `memory.high`, PSI, fsync 4 bước |
| Mạng: mô hình OSI, TCP | 1.7 + 4.1–4.9 + lab `curl` breakdown trên 4G thật |
| (không có) | 0.x **cách biết mình sai** + 3.9 contract test + 3.10 giải phẫu tầng phục vụ |

Chỗ môn cũ mạnh hơn: toán rời rạc, xác suất, và lý thuyết tính toán — **môn này không thay ba môn đó**, và không nên thay.

## 5. Học liệu và chuẩn bị

- **Sách:** `SYSTEMS-ATLAS-LEARNER-SA-2028.1.pdf` (hoặc Tập 1–2 phân phần trong `volumes/`), quiz cụm P0–P4 (+ câu nâng cao trong `P15-02-QA`), lab `L00–L04`, lời giải `S00–S04`, bộ slide 11 chương `★` (`kit/slides/`).
- **Máy:** một VM Linux 2 vCPU là đủ cho **tất cả** lab (mọi lab trong sách đã được chạy trên 2 vCPU — xem ghi chú "kết quả rỗng" ở 1.2).
- **Phần mềm:** `perf`, `bpftrace`, `fio`, `iperf3`, `jq`, `python3`, `go`/`node` (chỉ để chạy lab runtime).
- **Không cần:** tài khoản cloud trả tiền. Mọi bài tính tiền dùng giá công bố và ghi ngày tra.
