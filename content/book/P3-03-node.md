# 3.3 — Node.js / TypeScript Runtime (18 → 26 LTS)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** lang-3.md

---

## 0. Nhập môn

**Đọc trước:** 3.1 · 2.5 (mô hình I/O).

**Sợi chỉ đỏ:** *Đẩy trạng thái đơn realtime cho hàng vạn client — event loop của Node dạy gì?* — trả lời: Node thâu tóm concurrency bằng một event loop và một quy tắc vàng "đừng chặn vòng" — ai phá quy tắc thì cả server đứng; worker_threads là lối thoát cho việc nặng. Câu hỏi để lại cho chương sau: *Muốn một file binary, concurrency rẻ, deploy đơn giản — Go đổi lấy gì?*

**Thuật ngữ sẽ gặp:** *event loop* — vòng một thread quay qua sáu phase xử lý callback; *non-blocking* — API không chặn vòng: mọi chờ trở thành promise; *loop delay* — độ trễ giữa hai vòng lặp: nhịp tim của Node; *worker_threads* — thread thật cho tính nặng, trao đổi bằng message; *cluster* — nhiều process chia nhau một cổng; *TypeScript* — kiểu tĩnh trên nền JS, chi phí nằm ở bước build.

**Ví dụ mở đầu:** Bản deploy hôm đó có một endpoint mới đọc PDF 10 MB rồi parse đồng bộ. Trong 300 ms đó, toàn bộ DM — mọi khách, mọi request — đứng im vì event loop đang bận. Máy vẫn nhàn: CPU 5%, RAM vơi. Nhưng không ai được phục vụ: cái giá của một dòng code phá quy tắc vàng.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Scale theo process (cluster/PM2) hay container nhiều pod | V8 + event loop là biên — tôi đã đặt biên đó ở đâu trong topology? |
| 2 | Cái gì được phép chặn event loop — và chạy ở đâu khi cần | Danh sách việc chặn của tôi có nơi khai báo không? |
| 3 | Worker threads cho CPU-bound hay gọi service khác | CPU-bound 100 ms trong Node là 100 ms của mọi user — chuyển đi đâu? |
| 4 | TypeScript build path (tsc/tsc-go/bundler) & typecheck trong CI | Feedback loop dev chậm bao nhiêu — có dấu hiệu tsc thành tắc nghẽn văn hoá? |

---

## 2. Cơ chế

### 2.1 Trạng thái phiên bản (verify 2026-10-30)

| LTS | Trạng thái | Ghi chú |
|---|---|---|
| **26** | Active LTS (28/10/2026) | V8 mới; require() ESM dần hoàn thiện |
| 24 | Maintenance | qua LTS đầy đủ 10/2025 |
| 22 | Maintenance (EOL 04/2027) | type stripping ổn định hoá |
| 20 | **EOL 30/04/2026** | chết — nâng cấp |

Chu kỳ: LTS chẵn/năm, Active 10→4, EOL ~30 tháng. Điểm đáng chú ý 22–26: type stripping native (`--experimental-strip-types` → ổn định), `require(esm)`, `node:sqlite`, watch mode — giảm phụ thuộc tooling để chạy TS.

### 2.2 Event loop: sáu phase và một quy tắc vàng

Một vòng: **timers → pending → poll (I/O) → check (setImmediate) → close**; microtask (Promise) chen **giữa từng callback**. Quy tắc vàng: **mọi callback phải ngắn** — vì chỉ có một luồng JavaScript. Chờ I/O thì loop rảnh (đẹp); **tính/CPU/sync-IO thì mọi user chờ** (tệ). Metric bảo vệ: **event loop delay** (đo bằng `perf_hooks.monitorEventLoopDelay` — biến nó thành chuông báo trung tâm của mọi service Node).

### 2.3 V8 và bộ nhớ: thế giới hai heap

V8 JIT: interpreter (Ignition) → optimizing compiler (TurboFan), deopt khi giả định sai (kiểu không ổn định → chậm hơn tưởng). Heap có **giới hạn mặc định** (~4 GB trên 64-bit cũ; hiện đại điều chỉnh theo RAM container — nhưng vẫn phải đặt `--max-old-space-size` tường minh trên Kubernetes). GC là **generational + incremental + concurrent** — pause thường < vài chục ms nhưng "thêm heap" là liệu pháp phổ biến nhất che giấu leak (→3.9 closure trap).

### 2.4 Cluster, worker threads, và ranh giới thật

- **cluster:** N process, mỗi process một event loop đầy đủ, share cổng qua OS — scale đa lõi cách "thô nhưng đúng"; trong K8s thường thay bằng N pod 1 process (đổi phẳng scale theo deployment — →9.2).
- **worker_threads:** thread có V8 instance riêng, truyền structured clone/SharedArrayBuffer — cho CPU-bound (crypto, hình ảnh, parse lớn). Chi phí khởi tạo ~ms + bộ nhớ per-worker — pool hoá.
- **gọi service khác:** với CPU-bound nặng, kiến trúc "Node làm gateway + service native làm tính" là pattern bền vững nhất (Node mạnh nhất ở I/O fan-out — đúng thiết kế).

### 2.5 TypeScript: chi phí nằm ở đâu

TS không chạy trong production (trừ type stripping native) — chi phí là **thời gian dev + CI**: `tsc` whole-program chậm theo đồ thị; giải pháp cấu trúc: project references, `--build` incremental, tsgo (bản Go của compiler — đang được Microsoft đưa vào mainline 2025–2026 (V: lộ trình công bố)), hoặc chỉ typecheck ở CI + esbuild/swc cho transform. TypeErr rẻ hơn bug; chậm typecheck đắt hơn cả hai — cân bằng là quyết định kỹ thuật thật.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Event loop delay khoẻ | < 10 ms p99 | I | ngưỡng cảnh báo |
| V8 heap default | ~4 GB (cũ) — đặt tường minh | I | container càng cần |
| Worker thread init | ~ms + MB | I | pool hoá |
| cluster scale | tuyến tính theo lõi | I | trừ phần chung |
| Node 26 LTS bắt đầu | 2026-10-28 | V | versions.csv |

---

## 4. Suy luận kiến trúc

- **S1:** Node = "một luồng logic, vô hạn chờ I/O" — mọi quyết định kiến trúc phải tôn trọng 2.2 quy tắc vàng; vi phạm không sửa bằng thêm máy.
- **S2:** Tham số trụ: event loop delay p99, heap used vs limit, GC pause/s, active handles (conn).
- **S3:** Cluster đổi đơn giản ops lấy process-state nhân bản; worker_threads đổi giao tiếp (clone) lấy CPU thật; tách service đổi độ phức tạp hệ thống lấy tự do ngôn ngữ.
- **S4:** ESM hoá (10 năm!) gần xong ở 22+ — codebase mới nên ESM thuần, đừng mang thêm nợ CommonJS.
- **S5:** Node trên edge/serverless (Vercel/Cloudflare Workers dùng V8 isolate — chapter 3.8) hợp nhất "một runtime, nhiều quy mô" — kỹ năng Node chuyển dịch xuống edge tự nhiên.
- **S6:** Khi Node chậm: đo loop delay trước. Cao → tìm việc chặn (CPU/sync); thấp → vấn đề ở I/O phía sau (DB/network — 4.x/5.x), không phải Node.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| API Node chậm tốn thời mọi request | Event loop bị chặn (JSON lớn, sync crypto, regex ác) | loop delay; --prof | §2.2 |
| OOM sau vài ngày | Leak closure/global (→3.9) | heap snapshot diff | §2.3 |
| Đôi khi treo không lỗi | Sync I/O / DNS chậm (getaddrinfo) | strace; async hooks | §2.2 |
| p99 tăng khi thêm tính năng | V8 deopt (kiểu không ổn định) | --trace-deopt | §2.3 |
| Cluster không scale | Shared resource (session store) | theo dõi phần tuần tự | §2.4 |
| Build CI chậm dần | tsc whole-program | project refs; tsgo | §2.5 |

---

## 6. Cách đo

```bash
# Event loop delay — metric trung tâm
node -e "const {monitorEventLoopDelay}=require('perf_hooks');const h=monitorEventLoopDelay({resolution:20});h.enable();setInterval(()=>{h.disable();console.log('p99 ms:', (h.percentile(99)/1e6).toFixed(1));h.enable();},5000)"

# CPU profile 30 giây, không dừng service
node --prof app.js && node --prof-process isolate*.log | head -50
# hoặc 0x / clinic.js để flame chart tự động

# Heap snapshot diff (tìm leak)
#   trong process: v8.writeHeapSnapshot() theo lịch; so 2 bản bằng Chrome DevTools

# Đếm handle đang giữ
process._getActiveHandles().length    # (debug endpoint nội bộ)
```

Nguyên tắc: **loop delay là "nhiệt độ" của service Node** — mọi hiện tượng khác chỉ là triệu chứng của nó hoặc của hàng xóm.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay "thêm máy Node":** đưa việc chặn ra đúng chỗ (worker/service native — §2.4), cache (→5.4), hoặc bớt công việc mỗi request (payload nhỏ hơn, schema gọn hơn — →4.3). **Thay Node cho gateway:** giữ Node cho BFF/I/O fan-out, chuyển phần tính dày sang Go/Rust (→3.4/3.5) — pattern "polyglott theo đường nóng" phổ biến hơn viết lại toàn bộ.

Năm thấu kính:
- **Kinh tế:** Lương JS dev phổ biến/dễ tuyển; chi phí nằm ở "không nhìn thấy việc chặn" — một metric loop delay rẻ hơn nhiều một team on-call mù.
- **Vận hành:** Node upgrade chu kỳ LTS 30 tháng — tự động hoá nâng cấp trong image base; đừng để service chạy LTS chết (20 đã EOL 04/2026).
- **An ninh:** npm là hệ sinh thái phụ thuộc lớn nhất thế giới (không hiếm: hàng trăm package transitive cho một app "hello") — lockfile + audit + minimized image; supply chain là bề mặt chính (→10.4).
- **Lịch sử:** Từ "JS không thể server" (2009) tới nửa Internet chạy trên V8-derived stack (2026) — bài học: đơn giản hoá async (callback → promise → await) là đòn bẩy lớn nhất lịch sử runtime.
- **Người dùng:** Người dùng Node tốt = "mọi request được xử lý công bằng"; Node hỏng = "một user phá nát mọi user". Cảm nhận đó chính là event loop delay — chương này là bản đồ vá lại niềm tin.

---

## 8. Đọc tiếp & bài tập

- Wasm plugin trong Node: **3.8** · HTTP stack Node: **3.11** · Leak closure: **3.9** · FaaS cold start: **9.5**
- **Bài tập 1:** Thêm loop-delay metric vào một service Node production hôm nay. Thiết lập alarm 50 ms. Trong tháng, nó sẽ chỉ cho bạn đúng chỗ "luôn biết nhưng chưa đo".
- **Bài tập 2:** Viết endpoint parse JSON 10 MB sync rồi chuyển sang worker; đo loop delay hai trường hợp. Số này sẽ thuyết phục team hơn mọi slide.
- **Bài tập 3:** Đếm số service Node trong tổ chức chạy trên LTS đã EOL (20 hoặc cũ hơn). Mỗi cái là một CVE đang chờ ngày — liệt kê và lập kế hoạch tuần này.
