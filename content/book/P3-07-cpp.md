# 3.7 — C / C++ Runtime (C++14 → C++26)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** lang-7.md

---

## 0. Nhập môn

**Đọc trước:** 1.2 · 3.5 (đối trọng Rust).

**Sợi chỉ đỏ:** *C++ vẫn đứng ở đâu trong stack của DM, và giá của nó là gì?* — trả lời: C++ vẫn là chỗ của engine cần p99 và bộ nhớ đo bằng tay; chương này cho phần ngôn ngữ hiện đại, giá thật của nó (thời gian build, undefined behavior, thị trường người) và bộ siêu năng lực chẩn đoán: sanitizers. Câu hỏi để lại cho chương sau: *Biên dịch một lần chạy mọi nền — Wasm là sandbox gì cho plugin và trình duyệt?*

**Thuật ngữ sẽ gặp:** *RAII* — tài nguyên gắn với vòng đời đối tượng: hết phạm vi tự trả lại; *UB (undefined behavior)* — vùng hành vi không định nghĩa: compiler được làm gì cũng "đúng"; *sanitizer* — ASan/UBSan/TSan: chạy chậm hơn để bắt lỗi bộ nhớ, hành vi và đua; *move* — chuyển nhượng tài nguyên thay vì chép; *std::execution* — khung async chuẩn đang chuẩn hoá; *AoS/SoA* — bố cục dữ liệu quyết định hiệu năng cache (nối 1.2).

**Ví dụ mở đầu:** Engine tìm kiếm món của DM viết C++: p99 4 ms, không lớp nào khác gánh nổi khối chấm điểm. Nhưng bug "đọc rác" xuất hiện mỗi vài tuần — chỉ trên máy khách, không tái lập được. Bật ASan cho staging một đêm: sáng ra ba chỗ truy cập vùng đã free, in đậm đúng dòng code. Đó là ngày team bắt đầu tin sanitizers.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Có bắt đầu dự án mới bằng C++ không | Tôi cần: hiệu năng tuyệt đối? thư viện đặc thù? hay chỉ là quen tay? |
| 2 | Chuẩn hiện đại (20/23/26) + sanitizers trong CI | C++ "an toàn" (smart pointer, RAII) đã là mặc định codebase tôi chưa? |
| 3 | Mô hình concurrency: std::execution (C++26), Seastar, hay thread pool truyền thống | Scale theo lõi hay shared-nothing? |
| 4 | Phụ thuộc & phân phối (vcpkg/Conan, static link) | Ai xây binary của tôi — và tái lập được không? |

---

## 2. Cơ chế

### 2.1 C++ hiện đại: ngôn ngữ mới trong vỏ cũ

Kể từ C++11, mỗi chuẩn 3 năm: **RAII + smart pointer** (`unique_ptr`/`shared_ptr`) thay raw new/delete; **move semantics** tránh copy; `constexpr` tính lúc compile; ranges/concepts (20) làm generic code đọc được; coroutines (20) — nhưng thư viện chuẩn coroutine mỏng (khoảng trống C++26 lấp — §2.3). C++ "hiện đại" khác C++98 nhiều như Rust khác C — vấn đề là codebase thế giới chưa đồng đều.

### 2.2 Chi phí ẩn của lựa chọn C++

- **Năng suất:** cùng tính năng, C++ tốn người-giờ hơn các runtime khác;
- **Build system:** CMake là de-facto (không đẹp nhưng thắng); vcpkg/Conan cho dependency — phức tạp hơn npm/cargo một bậc;
- **ABI/platform:** compile theo OS/compiler/flag — phân phối binary là bài toán riêng (container che, không xoá);
- **Đội hình:** tuyển C++ giỏi khó hơn Go/Java giỏi — và bug C++ đắt hơn bug khác (memory corruption im lặng).

### 2.3 Concurrency C++ 2026: từ thread đến std::execution

- Cơ sở: `std::thread`/`std::async` + mutex/atomic — đủ, dễ sai;
- **Coroutines (C++20):** primitive cấp thấp (`co_await`); framework phải tự xây hoặc chọn asio — khác C#/Rust có runtime kèm sẵn;
- **std::execution (P2300, C++26):** mô hình sender/receiver chuẩn hoá async composition; NVIDIA/Intel đầu tư vì hợp GPU pipeline;
- **Seastar (shared-nothing, chạy ScyllaDB):** mỗi lõi một thread + message passing — pattern "scale theo lõi" triệt để nhất, đã chứng minh ở DB tỷ request/s.

### 2.4 Sanitizers: siêu năng lực chẩn đoán

ASan (bộ nhớ), TSan (race), UBSan (undefined), MSan (đọc chưa khởi tạo) — chạy trong CI mọi project C++ nghiêm túc. Giá: 2–10× chậm — đổi lấy phát hiện bug mà 20 năm "review cẩn thận" vẫn lọt. Đây là lý do Chromium/LLVM sống sót với C++ khổng lồ — và là câu trả lời thực dụng cho "C++ không an toàn": đúng, trừ khi công cụ bắt kịp.

### 2.5 Memory safety: cuộc tranh luận có hậu quả chính trị

NSA/CISA/ONCD (2024) khuyến nghị memory-safe cho code mới; Linux kernel nhận driver Rust; Android/Google đo được giảm CVE khi chuyển phần code sang Rust (V/I). Hệ quả thực dụng: **C++ mới = module hiệu năng của hệ lớn, có sanitizers + biên rõ; không phải mặc định cho service mới.** Giữ C++ ở chỗ không thay được: engine (DB, browser, game), HPC, codec, firmware.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Chuẩn mới nhất | C++26 (hoàn tất 2026) | V | C++23 phổ biến trên compiler |
| Sanitizer overhead | ASan ~2×; TSan ~5–10× | I | CI-only |
| Seastar | 1 thread/lõi, shared-nothing | V | ScyllaDB |
| Startup | ~ms | I | không runtime |
| Memory-safety CVE | ~60–70% lịch sử C/C++ | I | nghiên cứu MS/Google |

---

## 4. Suy luận kiến trúc

- **S1:** C++ đổi năng suất phát triển lấy **nút trên trần hiệu năng** — chỉ hợp khi trần đó là ràng buộc kinh doanh đo được (instance/cloud bill).
- **S2:** Tham số trụ: IPC (→1.2), alloc profile, sanitizer pass rate, build time.
- **S3:** std::execution chuẩn hoá async nhưng không kèm runtime/I/O — chọn asio/Seastar vẫn là quyết định kiến trúc, không phải chi tiết.
- **S4:** "Memory-safe mặc định" đang thành yêu cầu ngang "TLS mặc định" một thập kỷ trước — kế hoạch 5 năm codebase C++ nên có biên Rust rõ ràng.
- **S5:** GPU/AI kéo C++ về trung tâm (CUDA, tensor runtime đều C++) — vị thế "ngôn ngữ bên dưới mọi runtime" không suy giảm, chỉ đổi cửa.
- **S6:** Khi C++ chậm: IPC + cache-miss trước (→1.2); thuật toán sau; "đổi ngôn ngữ" là câu trả lời sai cho câu hỏi chưa đo.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Crash khó tái hiện | UAF/race | ASan/TSan trong CI | §2.4 |
| Prod đúng, staging sai | UB (flag khác nhau) | UBSan; chuẩn hoá flags | §2.4 |
| Build vỡ theo platform | ABI/dependency | container hoá; vcpkg | §2.2 |
| Async deadlock | Coroutine tự quản sai | TSan + audit | §2.3 |
| Perf không lặp lại | Governor/NUMA (→1.2/1.10) | perf stat kiểm soát | §2.2 |

---

## 6. Cách đo

```bash
# Sanitizer trong CI
cmake -B build -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer"

# Benchmark có kiểm soát
perf stat -e cycles,instructions,cache-misses ./bench   # IPC + miss (→1.2)

# Static analysis vào pre-merge
clang-tidy; cppcheck

# Flame
perf record --call-graph dwarf ./app && perf report
```

Nguyên tắc: **sanitizer là test, không phải tùy chọn** — codebase C++ không chạy ASan/TSan đều đặn là codebase đang mò trong tối.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay C++ cho service thường:** Rust (an toàn, cùng lớp hiệu năng — →3.5); Go (đủ nhanh, rẻ hơn hẳn về năng suất). **Giữ C++:** thư viện đặc thù (CUDA, codec, engine sẵn có), đội hình chuyên sâu, hoặc đường nóng đã tối ưu. **Thay "tối ưu C++ tay":** thêm số học (SIMD qua thư viện), đổi thuật toán, tách phần nóng thành module nhỏ.

Năm thấu kính:
- **Kinh tế:** C++ đắt nhất theo "chi phí mỗi dòng an toàn" — rẻ nhất theo "chi phí mỗi op ở tỷ QPS"; biên quyết định là quy mô.
- **Vận hành:** Không runtime = ít phụ thuộc khi chạy, nhưng build pipeline phức tạp — CI + sanitizer + container từ ngày đầu là bảo hiểm bắt buộc.
- **An ninh:** Memory-safety là rủi ro cơ cấu (không vá được bằng coding convention) — nơi chạm Internet, cân nhắc biên Rust/managed.
- **Lịch sử:** 40 năm, mỗi 3 năm một chuẩn, hai lần "sắp chết" (Java 1995, Rust 2015) — vẫn nằm dưới mọi thứ bạn dùng; tôn trọng bằng cách chọn đúng chỗ cho nó.
- **Người dùng:** Người dùng không biết hệ thống lõi viết bằng gì — nhưng họ cảm nhận crash định kỳ và hóa đơn cloud; chương này là về hai con số đó.

---

## 8. Đọc tiếp & bài tập

- Rust biên thay thế: **3.5** · SIMD/CPU: **1.2** · Seastar & DB: **5.2** · std::execution & GPU: **12.4**
- **Bài tập 1:** Bật ASan+UBSan cho test suite một dự án C++ bạn sở hữu. Số bug trong tuần đầu thuyết phục hơn mọi tài liệu.
- **Bài tập 2:** Đo IPC module nóng (perf stat). Nếu < 1 và cache-miss cao — quay lại 1.2 trước khi kết luận "C++ không đủ nhanh".
- **Bài tập 3:** Liệt kê codebase C++ chạm Internet trực tiếp. Với mỗi cái viết 3 dòng: biên an ninh hiện tại, kế hoạch sanitizer, ngày xem xét Rust.
