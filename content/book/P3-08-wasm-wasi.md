# 3.8 — WebAssembly & WASI 0.3

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 2.7 (thang cách ly).

**Sợi chỉ đỏ:** *Biên dịch một lần chạy mọi nền — Wasm là sandbox gì cho plugin và trình duyệt?* — trả lời: Wasm là sandbox bằng chính kiến trúc của nó — bộ nhớ tuyến tính có biên cứng, không có lệnh nào chạm ra ngoài; biên dịch một lần, chạy mọi nền từ server tới trình duyệt và edge. Câu hỏi để lại cho chương sau: *Đủ runtime đặt cạnh nhau — quyết định 'viết cái này bằng gì' có ma trận không?*

**Thuật ngữ sẽ gặp:** *Wasm* — định dạng bytecode di động với sandbox nằm trong kết cấu; *bộ nhớ tuyến tính* — vùng duy nhất chương trình được chạm, có biên cứng; *WASI* — "hệ điều hành" của Wasm: file, mạng, đồng hồ cấp theo quyền; *boundary overhead* — chi phí mỗi lần qua biên native và wasm; *wasm-opt* — tối ưu kích thước và tốc độ module; *WasmGC* — để ngôn ngữ có GC biên dịch xuống gọn hơn.

**Ví dụ mở đầu:** Duyệt ảnh món ăn của DM phải chạy ở ba nơi: server, trình duyệt, edge. Trước đây là ba bản code ba nhánh bảo trì. Một module Wasm chạy cả ba nơi, và ảnh độc hại — cố tràn, cố đọc file — chỉ đập được vào hộp cát bộ nhớ của nó. Phần đo thực tế cho thấy biên giới này chỉ tốn vài trăm nanogiây mỗi lần gọi.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Wasm dùng ở đâu: edge / plugin / sandbox đa ngôn ngữ | Tôi mua gì — startup ms, cô lập, hay "viết 1 lần chạy nhiều nơi"? |
| 2 | Component Model + WASI 0.2/0.3 cho giao tiếp | Interface-first thay FFI — đã mô hình hoá ranh giới chưa? |
| 3 | Ngôn ngữ biên dịch sang Wasm nào | Rust/Go/JS/Python — mỗi cái trade gì về kích thước + GC? |
| 4 | Runtime mục tiêu (Wasmtime/WasmEdge/edge provider) | Cold start, throughput, API đủ cho use case? |

---

## 2. Cơ chế

### 2.1 Sandbox bằng kiến trúc, không bằng giám sát

Wasm là **bytecode stack-machine** chạy trong runtime (Wasmtime, V8, WasmEdge). Ba ràng buộc tạo sandbox:
1. **Linear memory** — một khối bộ nhớ duy nhất, mọi truy cập kiểm tra bounds (không đọc ngoài vùng — không raw pointer);
2. **Không syscall** — chỉ gọi hàm runtime cho phép (capability-based: truyền handle, không truyền đường dẫn);
3. **Kián đoạn có ngân sách** — runtime giới hạn fuel/epoch (chống vòng lặp vô hạn).

Chi phí: bounds check + gián tiếp call — JIT tốt đạt **~80–100% native** cho tính toán (I), kém hơn ở cấu trúc phức tạp + boundary call dày.

### 2.2 WASI: hệ điều hành của Wasm

WASI 0.1 (preview) → **0.2** (Component Model, ổn định 2024) → **0.3** (2026): **native async** — component async không block thread. Verified: WASI 0.3.2 (10/2026), Wasmtime 49.x (V). Ý nghĩa: Wasm thành **mục tiêu biên dịch chung** — Rust/Go/JS/Python compile sang component, giao tiếp qua **WIT interface** (interface-first) thay FFI dễ vỡ.

```
[Rust component] --WIT--> [Go component] --WIT--> [JS host]
   (KV interface)            (auth)               (browser/edge)
```

### 2.3 WasmGC & ngôn ngữ

**WasmGC** (engines chính hỗ trợ 2024–2025): struct/array gốc trong engine — GC-lang (Java/Kotlin/Dart/JS) biên dịch không phải ship GC riêng → module nhỏ, perf tốt hơn. Trạng thái từng họ (bậc, 2026): Rust/Go đầu tàu (AOT-friendly); JS/TS tự nhiên; Java/Kotlin ổn định hoá qua WasmGC; Python (Pyodide) bundle ~MB — hợp notebook/plugin, không hợp edge nhỏ.

### 2.4 Ba use case đang thắng

1. **Edge/serverless:** Cloudflare Workers/Fastly — V8 isolate/Wasm, cold start ~ms, mật độ tenant cao (một process chạym nghìn isolate) — bỏ chi phí boot so container/VM;
2. **Plugin hệ thống lớn:** Envoy filter, Shopify Functions, database UDF (kể cả vector UDF — →5.10) — chạy code khách an toàn trong process mình;
3. **Portable compute:** CLI đa OS, game logic cross-platform, FaaS portable giữa provider.

Chưa thắng (2026): service backend "thường" — container + runtime ngôn ngữ đủ dùng, và hệ sinh thái quan sát/retry/văn hoá ops chưa theo kịp.

### 2.5 Vận hành

- **Quan sát còn non:** chưa có "pprof/JFR chuẩn" xuyên runtime — cần DWARF/sourcemap; log/metric phải expose qua host API;
- **Cold start thật:** compile + instantiate — giữ module nhỏ (strip, opt-size) + pool instantiation;
- **An ninh ranh giới là của host:** Wasm không thoát sandbox bộ nhớ, nhưng logic trong đó tin được chừng nào là quyết định host (fuel limit, mem limit — vẫn trách nhiệm của bạn).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| WASI | 0.3.2 (10/2026) | V | versions.csv |
| Wasmtime | 49.x | V | versions.csv |
| Hiệu năng tính toán | ~80–100% native | I | JIT tốt |
| Cold start edge | ~ms | I | so container ~s |
| WasmGC engines | Chrome/Firefox/Safari/Node | V | 2024+ |

---

## 4. Suy luận kiến trúc

- **S1:** Wasm là **mục tiêu biên dịch + sandbox**, không phải ngôn ngữ — giá trị từ quyết định "chạy code ai/ở đâu", không phải "viết bằng gì".
- **S2:** Tham số trụ: module size, instantiate time, call overhead qua boundary (WIT), fuel/CPU theo tenant.
- **S3:** Wasm đổi portable lấy thêm một lớp biên dịch + tooling non; isolate đổi chi phí boot lấy ràng buộc API host.
- **S4:** Edge + plugin là hai chân đà thật; backend chung sẽ theo khi observability/lifecycle chuẩn hoá (theo dõi WASI 0.3 adoption).
- **S5:** Component Model + async làm Wasm tiệm cận "unix của compute phân tán" — nếu API chuẩn hoá, hiệu ứng mạng giống container 2013–2018.
- **S6:** Khi cân nhắc Wasm, hỏi: "cái gì phải chạy ở nơi tôi không kiểm soát?" — không có gì thì container truyền thống đơn giản hơn.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Module to bất thường | Ship GC riêng / debug info | wasm-opt -Oz; strip | §2.3 |
| Plugin tốn CPU vô hạn | Không fuel limit | cấu hình fuel/epoch | §2.1 |
| Boundary call chậm | Qua lại WIT trong vòng lặp | gộp batch; interface thô hơn | §2.2 |
| Không có stack trace | Symbol bị strip | giữ DWARF/sourcemap | §2.5 |
| Cold start chưa như quảng cáo | Compile mỗi lần + module lớn | cache AOT; instantiate pool | §2.5 |

---

## 6. Cách đo

```bash
# Wasmtime CLI — đo trần nhanh
wasmtime compile app.wasm && wasmtime run --dir=. app.wasm

# Kích thước & phân tích module
wasm-opt -Oz app.wasm -o app.small.wasm
wasm-objdump -h app.wasm          # sections

# Trong host: tự export instantiate time + call latency
# (Wasmtime engine metrics / epoch deadline callback)
```

Nguyên tắc: **đo boundary** — chi phí Wasm không nằm trong hàm, nằm ở việc qua lại ranh giới; thiết kế interface theo "dữ liệu to, ít lần qua".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Wasm plugin:** FFI/C ABI (nhanh, không an toàn); script nhúng (Lua/JS — nhỏ, cũ nhưng ổn); process riêng + IPC (an toàn, nặng hơn). **Thay edge Wasm:** microVM startup-optimized (Firecracker — →2.7) khi cần thư viện hệ thống đầy đủ.

Năm thấu kính:
- **Kinh tế:** Chi phí biên rẻ nhất ở **quy mô tenant lớn** (nghìn isolate/máy) — plugin marketplace, FaaS; đắt nhất khi một service tự chạy (lớp thừa).
- **Vận hành:** Tooling quan sát còn non — dự tính 1–2 quý công; giữ plugin ngắn, stateless để bù.
- **An ninh:** Sandbox theo kiến trúc là mô hình mạnh nhất cho code không tin cậy trong process (so seccomp — 2.7); nhưng fuel/mem limit vẫn là trách nhiệm host.
- **Lịch sử:** "Write once run anywhere" lần 1 (JVM) thắng enterprise; lần 2 (container) thắng cloud; Wasm là lần 3 — nhẹ hơn, hẹp hơn, và sandbox là tính năng đầu tiên chứ không phải phụ thêm.
- **Người dùng:** Người dùng thấy plugin "cài không cần restart", edge "phản hồi gần như local" — cả hai đều là Wasm làm việc thầm lặng.

---

## 8. Đọc tiếp & bài tập

- Sandbox so sánh: **2.7** · Edge/FaaS: **9.5** · Vector UDF: **5.10** · Agent tool sandbox: **12.5**
- **Bài tập 1:** Viết hàm Rust nhỏ compile sang wasm32-wasip2; đo kích thước trước/sau `wasm-opt -Oz`. Ghi con số — cảm giác "Wasm nhỏ" cần số liệu.
- **Bài tập 2:** Chạy cùng hàm native và Wasm (Wasmtime) 1 triệu lần; tính overhead boundary. Kết luận: interface plugin nên thô đến đâu?
- **Bài tập 3:** Liệt kê nơi hệ thống bạn chạy code người khác (rule, filter, UDF, hook). Mỗi nơi trả lời: sandbox là gì? Nếu là "tin tưởng" — đó là chỗ Wasm/microVM đáng bảng.
