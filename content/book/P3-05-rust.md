# 3.5 — Rust Runtime (1.85 → 1.99)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** lang-5.md

---

## 0. Nhập môn

**Đọc trước:** 2.5 · 2.7 (sandbox).

**Sợi chỉ đỏ:** *Phần thanh toán đòi memory-safety tuyệt đối — Rust có đáng cái giá học nó?* — trả lời: Rust xoá cả một lớp lỗi bộ nhớ bằng ownership — không GC, không null bất ngờ, không dùng-sau-khi-free — cái giá là trình biên dịch khắt khe và async có "màu" riêng. Câu hỏi để lại cho chương sau: *Đội to dần cùng di sản JVM — virtual threads có đổi trò chơi không?*

**Thuật ngữ sẽ gặp:** *ownership* — mỗi giá trị đúng một chủ, hết phạm vi tự dọn; *borrow checker* — kiểm tra mọi lần mượn tham chiếu ngay lúc biên dịch; *Result/Option* — lỗi và "không có" là kiểu rõ ràng, không null ẩn; *tokio* — runtime async của Rust: scheduler + I/O; *async có màu* — hàm async lây lan kiểu, đổi cách tổ chức code; *unsafe* — lối chủ động gỡ hàng rào: hiếm và phải chứng minh được.

**Ví dụ mở đầu:** Module thanh toán DM là nơi "null bất ngờ" và "dùng sau khi free" đắt nhất — mỗi lỗi là một đợt hoàn tiền. Rust đẩy cả hai lớp lỗi này về trước khi chạy: biên dịch xong là chúng không còn, trừ unsafe có chủ ý. Đồng nghiệp phàn nàn "ba tuần mới hết cãi với compiler" — ba tuần đó rẻ hơn một sự cố tiền.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Tokio multi-thread hay current-thread (+ rayon cho CPU) | Workload của tôi là chờ nhiều hay tính nhiều — và có cần cả hai? |
| 2 | Async ở đâu, sync ở đâu trong cùng codebase | "Màu async" lây lan — biên tôi vẽ ở đâu để lây có kiểm soát? |
| 3 | spawn_blocking cho việc chặn (I/O file, crypto, sleep) | Việc chặn của tôi đang chạy đúng "phòng cách ly" chưa? |
| 4 | Build/deloy: cargo features, compile time, image | Team tôi trả chi phí compile thế nào — và có đo không? |

---

## 2. Cơ chế

### 2.1 Kiểm soát sở hữu = chương trình không cần GC

Borrow checker chứng minh tại compile-time: mỗi giá trị có đúng một chủ, mượn có thời hạn, không alias + mutate cùng lúc. Kết quả vận hành: **không pause GC, không GC CPU%, heap biến động nhỏ** — và cả nhóm bug (use-after-free, data race) biến mất *theo phân loại* (memory-safety CVE của C/C++ chiếm ~60–70% (I, nghiên cứu Microsoft/Google)). Cái giá không nằm ở runtime mà ở **đường cong phát triển** — đổi thời gian con người lấy thời gian máy.

### 2.2 Tokio: scheduler + I/O cho async Rust

Tokio là de-facto runtime: worker thread (mỗi lõi một) chạy task; **work-stealing** như Go; network poller epoll/kqueue/io_uring tuỳ feature flag (→2.5). Task ~đôi trăm bytes (nhẹ hơn goroutine). Hai quy tắc vàng:
1. **Không block worker**: việc chặn (file I/O, sleep, CPU dài, đợi mutex của thư viện sync) phải `spawn_blocking` (pool riêng). Vi phạm = đói scheduler — triệu chứng "Tokio lat/qua chậm, CPU thấp" (mục 5);
2. **Không giữ std Mutex/RefCell qua `.await`**: lock không phải Send-safe — hoặc deadlock tiềm ẩn, hoặc compiler chặn (tin compiler).

### 2.3 Async Rust: mạnh và chu đáo, nhưng "màu"

`async fn` trả Future phải `.await`; lây kiểu (hàm gọi async phải async). Giải pháp cấu trúc: (a) giữ lõi sync, async chỉ ở lớp ngoài; (b) `async fn` in trait ổn định từ 1.75 — bớt được nền tảng generic phức tạp cũ; (c) channel/actor cho biên tách bạch. Hiểu nhầm phổ biến: async không làm code "nhanh hơn" — nó làm **chờ rẻ hơn**; CPU-bound vẫn cần thread (rayon — data-parallel chuẩn).

### 2.4 Sinh thái vận hành

- **Compile time** là chi phí thật: dự án lớn clean build tính bằng phút; incremental + `sccache` + chia crate nhỏ là liệu pháp; đo bằng `cargo build --timings` (nó thành metric team được);
- **Binary** tĩnh, ~MB-scale, strip + musl cho image nhỏ; startup ms → hợp FaaS/edge;
- **Observability**: `tracing` + OpenTelemetry là chuẩn de-facto; profile bằng `perf` (không cần trinity runtime — chương trình là native);
- **unsafe**: ẩn mình ở thư viện hệ thống; audit với `cargo geiger` cho code tổ chức mình.

### 2.5 Rust trong hạ tầng ai cũng dùng

Hạ tầng hiện đại có bóng Rust ở khắp nơi: firecracker (microVM — →2.7), data-plane proxy (Linkerd2-proxy), cơ sở dữ liệu (TiKV, Turso), trình duyệt (Firefox), driver kernel Linux (từ 6.1), thành phần Windows. "Có nên viết service bằng Rust" là câu hỏi team; "ai đang chạy Rust giùm mình" là câu hỏi ai cũng đang trả lời "có" mà không biết.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Rust stable | 1.99.1 (10/2026); Edition 2024 từ 1.85 | V | versions.csv |
| Task async | ~hundreds bytes | I | nhẹ hơn goroutine |
| Memory-safety CVE giảm | ~60–70% nhóm bị xoá | I | Microsoft/Google studies |
| Startup binary | ~ms | I | hợp edge/FaaS |
| Clean build dự án lớn | phút | P | quản bằng chia crate |

---

## 4. Suy luận kiến trúc

- **S1:** Rust đổi chi phí từ **vận hành** (GC/pause/leak) sang **phát triển** (compile/thiết kế kiểu) — quyết định đúng phụ thuộc thời gian sống của code: càng dài, càng hợp.
- **S2:** Tham số trụ: block-in-async thời gian (console tokio), compile time p50/p95, alloc/s (thấp đáng kể so với GC-lang).
- **S3:** Tokio đổi mức trừu tượng lấy hiệu năng; rayon đổi đơn giản lấy data-parallel; "sync lõi + async vỏ" đổi ít async lấy tốc độ phát triển.
- **S4:** Hạ tầng consolidated về Rust cho phần "gần kim loại" (microVM, data plane) — hiệu ứng mạng: càng nhiều hạ tầng viết Rust thì tooling/hiring càng dễ — vòng tự củng cố như Go thập kỷ trước.
- **S5:** async Rust + WASM (→3.8) tạo cặp "viết một lần, chạy edge/browser/plugin" — phần thị trường mà Go không nhắm.
- **S6:** Khi Rust "chậm": 99% là chờ I/O hoặc block sai chỗ (tokio-console), không phải ngôn ngữ; phần còn lại là thuật toán — perf sẽ chỉ thẳng.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Tokio task đói (latency cao, CPU thấp) | Block không spawn_blocking | tokio-console; tracing | §2.2 |
| Deadlock khó hiểu | Giữ lock qua await | audit pattern; clippy lint | §2.2 |
| Compile chậm kéo dài tuần | Crate khổng lồ + features nhiều | cargo build --timings | §2.4 |
| Futures "bị bỏ quên" (không chạy) | Quên .await / spawn | clippy; must_use | §2.3 |
| CPU-bound async không nhanh hơn | Async nhầm chỗ — cần rayon | benchmark hai mô hình | §2.3 |
|panic trong production | unwrap ở đường biên | audit unwrap/expect | §2.1 |

---

## 6. Cách đo

```bash
# Scheduler & task — realtime console
tokio-console                       # cần ConsoleLayer bật trong app

# Profile native (không runtime đặc biệt)
perf record --call-graph dwarf ./app && perf report
flamegraph crate; hoặc cargo flamegraph

# Compile time theo crate
cargo build --timings               # mở report html

# Static audit
cargo clippy -- -W clippy::all      # lint "đúng idioma"
cargo geiger                        # đếm unsafe
```

Nguyên tắc: **tokio-console là loop-delay của Rust** — gắn nó trước khi tối ưu bất cứ gì.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Rust khi deadline ngắn:** Go (đơn giản, đủ nhanh cho 95% service); Rust chỉ rõ ràng thắng ở: p99 cực, mật độ máy (số instance ít — tiết kiệm cloud thật), hoặc môi trường không GC (kernel/plugin/edge). **Thay Tokio phức tạp:** actix/axum là đủ cho web service; async chỉ cần ở I/O fan-out thật.

Năm thấu kính:
- **Kinh tế:** Rust rẻ nhất ở **quy mô lớn và thời gian dài** (AWS/Firecracker/Cloudflare đo được: ít máy hơn cho cùng tải); đắt nhất ở MVP short-lived.
- **Vận hành:** Binary tĩnh + không runtime = ít thứ vỡ; nhưng on-call cần biết đọc core dump panic (RUST_BACKTRACE=1 vào runbook).
- **An ninh:** Loại bỏ cả lớp memory-safety CVE — với service đối diện Internet, đó là giảm rủi ro cấu trúc, không phải tweak.
- **Lịch sử:** Từ "trò chơi nghiên cứu" (2010) tới kernel Linux (2022) và hạ tầng chủ lưu (2026): mỗi bước là một tổ chức lớn đánh cược bằng code thật — không phải bằng whitepaper.
- **Người dùng:** Người dùng thấy "dịch vụ không bao giờ pause, không phình RAM" — họ không biết gọi tên đó là Rust; đó chính là điểm.

---

## 8. Đọc tiếp & bài tập

- Wasm: **3.8** · Ma trận so sánh: **3.9** · Việc chặn & pool: **3.10** · MicroVM (Firecracker): **2.7**
- **Bài tập 1:** Viết service nhỏ có endpoint CPU 50 ms: một bản block worker (không spawn_blocking), một bản đúng. So tokio-console + p99. Bài học trọn đời về §2.2.
- **Bài tập 2:** `cargo build --timings` trên repo lớn nhất của team: crate nào chiếm > 20% thời gian? Đó là đề tài refactor tuần này.
- **Bài tập 3:** `grep -rc unwrap()` từng repo Rust của bạn. Mỗi unwrap ở đường biên là một panic tương lai lúc 3h sáng — quy về `?` + error handling có loại.
