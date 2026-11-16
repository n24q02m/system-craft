# 3.9 — Ma trận 6+1 Runtime, 12 Bẫy xuyên ngôn ngữ & Chi phí vòng đời

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** matrix-langs.md + traps-crosslang.md

---

## 0. Nhập môn

**Đọc trước:** Lướt 3.2–3.8 — mỗi runtime một hàng của ma trận.

**Sợi chỉ đỏ:** *Đủ runtime đặt cạnh nhau — quyết định 'viết cái này bằng gì' có ma trận không?* — trả lời: có — một ma trận 6+1 runtime theo hàng, tiêu chí quyết định theo cột (pause, cold start, bộ nhớ, interop), kèm 12 bẫy xuyên ngôn ngữ và chi phí vòng đời TCO: thứ bị bỏ quên trong mọi cuộc họp chọn ngôn ngữ. Câu hỏi để lại cho chương sau: *Runtime chỉ là một trạm — request của khách đi qua bao nhiêu trạm trước khi quay lại?*

**Thuật ngữ sẽ gặp:** *TCO* — tổng chi phí sở hữu: học, mượn người, vận hành — không chỉ chi phí chạy; *pause GC* — thời gian "dừng thế giới" của từng runtime; *cold start* — từ lệnh chạy tới sẵn sàng phục vụ; *interop* — chi phí gọi qua biên ngôn ngữ: FFI, CGO, C extension; *contract test* — chặn bug xuyên ngôn ngữ ngay ở chỗ giao nhau; *12 bẫy* — số thập phân, múi giờ DST, emoji, null-chuỗi-rỗng: sai giống nhau ở mọi ngôn ngữ.

**Ví dụ mở đầu:** Họp chọn ngôn ngữ cho service thông báo mới của DM: mỗi người đề xuất ngôn ngữ mình quen, hai giờ không tới đâu. Đặt ma trận ra: cần cold start thấp (FaaS?), pause nhỏ (push realtime?), người có sẵn (ai trực đêm?) — quyết định rơi ra trong 15 phút. Chương này là ma trận đó, đã điền sẵn và ghi nguồn từng ô.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Chọn runtime cho workload mới | I/O-bound / CPU-bound / mixed / độ phức tạp đội hình — dùng ma trận nào để quyết định có thể bảo vệ trước ban lãnh đạo? |
| 2 | Chuẩn hoá "ít ngôn ngữ" hay đa ngôn ngữ theo đặc thù | Chi phí context-switch của team bao nhiêu so với lợi ích từng tool? |
| 3 | Checklist bẫy xuyên ngôn ngữ cho mọi codebase | 12 bẫy đã được review/template hoá chưa? |
| 4 | TCO runtime (không chỉ p99) | Ai trả hoá đơn: build, hiring, upgrade, security — tính đủ chưa? |

---

## 2. Cơ chế

### 2.1 Ma trận 6+1 runtime — đọc theo hàng ngang, quyết theo cột

| Tiêu chí | Python | Node/TS | Go | Rust | Java | C++ | Wasm |
|---|---|---|---|---|---|---|---|
| Mô hình concurrency | async + GIL | event loop + worker | goroutine | async/task + rayon | thread → virtual thread | thread/std::exec | isolate |
| Bộ nhớ | RC + cycle GC | GC (V8) | GC (GC nhỏ, pause <1ms) | ownership | GC (chọn pause) | manual | linear + host |
| Startup | ~100ms+import | ~50–100 ms | ~ms | ~ms | ~s (CRaC: ms) | ~ms | ~ms |
| Vòng đời p99 | phụ thuộc (đo) | tốt nếu không block | rất tốt | tốt nhất | tốt với GC đúng | tốt nhất | tốt |
| Năng suất MVP | ★★★★★ | ★★★★★ | ★★★★ | ★★ | ★★★ | ★★ | ★★★ |
| Hiệu năng trần | ★★ (trừ native lib) | ★★★ | ★★★★ | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ |
| Đội hình/dạy | dễ | dễ | dễ-trung bình | khó | trung bình | khó | trung bình |
| Điểm chết | CPU-bound thuần | việc chặn loop | hệ sinh thái ML | tốc độ phát triển | startup/footprint (đã giảm) | memory-safety | tooling quan sát |

**Cách dùng đúng:** không hỏi "runtime nào tốt nhất" — hỏi "workload của tôi chết ở runtime nào". I/O fan-out → Node/Go/Python-async đều ổn; CPU đều đặn → Go/Java; p99 khắt khe + mật độ máy → Rust; plugin/edge → Wasm; prototyping đổi yêu cầu mỗi tuần → Python/TS.

### 2.2 12 bẫy xuyên ngôn ngữ (dịch từ legacy + chuẩn hoá)

Không phụ thuộc runtime — bẫy này giết hệ đa ngôn ngữ nhiều hơn bug từng ngôn ngữ:

1. **Blocking giấu trong async** — mọi runtime đều có (Node JSON to, Python lib sync, Rust std call trong task — 3.3–3.8);
2. **Unbounded queue/buffer** — hàng đợi không trần biến backpressure thành OOM (→5.7);
3. **Retry không jitter/budget** — bão retry lúc chính xác lúc cần giảm tải (→8.5);
4. **Timeout không phân tầng** — timeout con > timeout cha = leak công việc mồ côi (→3.10);
5. **Bẫy số thực** — so sánh `==` float, tích luỹ sai số, parse khác nhau giữa ngôn ngữ (JSON number!);
6. **Ngày-giờ & timezone** — lưu local-time thay UTC/instant; DST tính 2 lần (→1.9);
7. **Unicode/grapheme** — `length()` đếm code unit, không đếm "chữ người dùng nhìn thấy" (emoji, tiếng Việt ghép);
8. **Sort không ổn định/khác key** — phân trang lặp lại khác kết quả giữa 2 service;
9. **Số ngẫu nhiên không seed/khác PRNG** — test không tái lập được giữa các runtime;
10. **Format số/decimal** — làm tròn tiền tệ bằng float; i18n khác locale;
11. **Encoding mặc định** — một bên UTF-8, một bên Latin-1/UTF-16: lỗi chỉ hiện ở dữ liệu "lạ";
12. **Versioning protobuf/JSON implicit** — thêm field không default → runtime cũ vỡ âm thầm.

**Bài học cấu trúc:** bẫy 5–11 đều là **ranh giới giữa hai runtime** — nơi không ngôn ngữ nào "sở hữu" ngữ nghĩa. Thuốc là contract test + schema (→4.3) + bộ fixture dữ liệu chia sẻ.

### 2.3 Chi phí vòng đời (TCO) — phần bị bỏ quên

| Khoản | Python/Node | Go/Rust/Java |
|---|---|---|
| Hiring | phổ biến nhất | Go dễ; Rust khó |
| Build/CI | nhanh | Rust/C++ chậm (phút) |
| Upgrade runtime | EOL 5 năm (Py) / 30 tháng (Node) | Go 2 minors; JVM LTS 2 năm |
| Security patch | phụ thuộc nhiều (npm/PyPI to) | ít package hơn (thường) |
| Observability | phải tự gắn (loop lag, py-spy) | có sẵn sâu (pprof/JFR) |

Quy tắc: **rẻ để bắt đầu ≠ rẻ để giữ** — nhập weighting theo tuổi thọ dự án: dự án < 1 năm ưu tiên năng suất; > 3 năm ưu tiên vận hành/đội hình.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Startup: Go/Rust vs JVM (không CRaC) | ~ms vs ~s | I | |
| Footprint RSS hello-world | Go/Rust ~10–20 MB; JVM ~100+ MB | I | |
| p99 tốt nhất (tương đối) | Rust ≥ C++ > Go ≈ Java(GC đúng) > Node ≈ Python | I | workload phụ thuộc |
| Đội hình trung bình thị trường 2026 | Python/TS > Java > Go > C++ > Rust | I | |

---

## 4. Suy luận kiến trúc

- **S1:** Runtime là **hợp đồng nền tảng** — mọi quyết định phía trên (framework, queue, DB client) kế thừa giới hạn của nó; chọn sai tốn một lần viết lại.
- **S2:** Tham số trụ cho mọi runtime (chuẩn hoá để so sánh): loop/scheduler delay, GC pause p99, RSS/unit công việc, CPU% tính vs chờ.
- **S3:** Đa ngôn ngữ đổi "đúng tool cho việc" lấy chi phí context-switch + biên 12 bẫy — ngưỡng thực dụng: 2–3 runtime/đội, hơn thế cần cấu trúc sở hữu (team platform).
- **S4:** Ba xu hướng gộp về "runtime lo concurrency" (Go lịch sử, Java VT 2023+, Python free-thread 2024+) — kỹ năng phân biệt "việc chờ" vẫn là kỹ năng phân định.
- **S5:** Hợp đồng xuyên runtime (OpenAPI/gRPC/JSON Schema) đang thành "ngôn ngữ chung" thật sự — chất lượng interface quan trọng hơn chất lượng ngôn ngữ.
- **S6:** Khi hệ "chậm", trước khi đổ lỗi runtime: đo phần chờ vs tính (mọi chương 3.2–3.8 đều có công cụ) — 80% là I/O phía sau (4.x/5.x).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Một service chậm, không rõ vì runtime | Chưa tách chờ/tính | py-spy/pprof/JFR/loop-lag | §2.1 |
| Lỗi dữ liệu "lạ" giữa 2 service | Bẫy 5–11 (số/unicode/encoding) | contract test + fixture chung | §2.2 |
| Team chậm, không phải máy | Context-switch đa ngôn ngữ | audit số runtime/đội | §2.3 |
| Pagination đôi khi lặp/miss | Sort không ổn định (bẫy 8) | key ổn định + tie-break | §2.2 |
| Retry gây sập thay vì cứu | Bẫy 3 | jitter + budget (→8.5) | §2.2 |

---

## 6. Cách đo

```bash
# Chuẩn hoá metric xuyên runtime — mỗi service phải expose:
#   - unit đồng thời đang chạy (thread/goroutine/task)
#   - thời gian chờ I/O vs tính (per request)
#   - GC/scheduler pause p99
#   - RSS per worker

# Ví dụ đối chiếu nhanh hai service (bất kỳ ngôn ngữ):
#   tải 100 RPS trong 5 phút — đo p50/p99 + CPU + RSS
#   cùng endpoint "echo + 1 query DB" — khác biệt còn lại là runtime/stack
```

Nguyên tắc: **đo cùng một hình, vẽ trên cùng trục** — so sánh runtime bằng benchmark lệch kiểu (payload khác, DB khác) là so sánh không gì cả.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay đổi quyết định runtime (đắt):** thường chỉ đáng khi (a) chi phí máy đo được > chi phí rewrite, (b) ràng buộc mới (p99 SLA, edge), (c) đội hình đổi. **Thay chuẩn hoá 1 ngôn ngữ:** chuẩn hoá 1 *stack HTTP + 1 hệ quan sát + 1 bộ schema* — phần thưởng giống nhau, mất tự do ít hơn.

Năm thấu kính:
- **Kinh tế:** Chi phí thật của runtime = máy + người + rủi ro; bảng 2.3 là bản kiểm kê — thiếu một dòng là quyết định lạch bạch.
- **Vận hành:** Mỗi runtime thêm một nhánh upgrade/EOL theo dõi — đặt chung calendar, review mỗi quý.
- **An ninh:** 12 bẫy phần nào là bề mặt tấn công (số thực tiền tệ, encoding, timezone lệch audit log) — schema test là lớp phòng thủ.
- **Lịch sử:** Thập kỷ 2010 tranh "ngôn ngữ nào thắng"; thập kỷ 2020 câu trả lời: container + HTTP/gRPC làm mọi ngôn ngữ "đủ tốt" — cạnh tranh dịch xuống hệ sinh thái và vận hành.
- **Người dùng:** Người dùng không chọn runtime; họ chọn "app này ổn không". Ma trận này tồn tại để người làm kỹ thuật chọn thay mặt họ một cách có thể giải thích.

---

## 8. Đọc tiếp & bài tập

- Chi tiết từng runtime: **3.2–3.8** · Serving tier: **3.10** · Schema/contract: **4.3** · Retry: **8.5**
- **Bài tập 1:** Với 3 service khác runtime của bạn: thu bộ metric chuẩn (§6). Vẽ một bảng — đó là bằng chứng cho quyết định runtime tiếp theo.
- **Bài tập 2:** Viết contract test cho một cặp service (2 runtime) với fixture chứa: số thập phân, emoji, ngày DST, chuỗi trống. Đếm test fail — thường > 0 ngay lần đầu.
- **Bài tập 3:** Đếm số runtime đang chạy production trong org bạn. Với mỗi cái trên ngưỡng 3: viết 1 đoạn "tại sao nó đáng một chỗ".
