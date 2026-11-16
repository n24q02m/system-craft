# 3.1 — Lý thuyết Đồng thời & 4 Trường phái Quản lý Bộ nhớ

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** part2-theory.md

---

## 0. Nhập môn

**Đọc trước:** 1.2 (cache) · 2.3 (task/scheduler).

**Sợi chỉ đỏ:** *Hiểu máy và OS rồi — DM viết lại bằng ngôn ngữ nào, và đồng thời cùng GC dạy bài học đầu tiên gì?* — trả lời: trước khi chọn ngôn ngữ phải nắm ba công thức sizing và bốn mô hình "ai chờ kiểu nào" — mọi chương runtime phía sau chỉ là biến thể của một vài mô hình đó, và lỗi tồn kho âm của DM chính là lỗi mô hình chứ không phải lỗi code. Câu hỏi để lại cho chương sau: *Python ra sản phẩm nhanh — nhưng chậm ở đâu, và khi nào lỗi của bạn không phải tại ngôn ngữ?*

**Thuật ngữ sẽ gặp:** *concurrency* — nhiều việc trộn nhau trên một tài nguyên; *parallelism* — nhiều việc chạy thật cùng lúc trên nhiều lõi: hai khái niệm khác nhau; *luật Little* — số việc đang trong hệ = throughput × thời gian ở lại: thước tính pool; *mutex* — khoá độc quyền một tài nguyên; *trường phái bộ nhớ* — marking GC / đếm tham chiếu / ownership / stack discipline; *cooperative/preemptive* — tự nhường hoặc bị giật quyền.

**Ví dụ mở đầu:** Hai shipper cùng thấy "còn 1 suất giao nhanh" và cùng nhận — tồn kho thành âm một. Lỗi không phải "code ẩu" mà là mô hình concurrency sai: chia sẻ trạng thái không kèm khoá, hoặc có khoá nhưng hai người giữ chéo nhau thành deadlock. Chương này là bản đồ các mô hình để lỗi kia có tên gọi và có cách chọn.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Mô hình đồng thời: event loop / thread pool / green threads / async-await | Bài toán tôi chờ I/O nhiều hay tính nhiều? Đội code nào gánh được? |
| 2 | Trường phái bộ nhớ cho hệ mới: GC tracing / RC / ownership / manual | Tôi chấp nhận pause nào: µs, ms, hay "không bao giờ"? |
| 3 | Mức song song hoá (Amdahl thật sự của bài toán) | Phần tuần tự của tôi chiếm bao nhiêu % — đo chứ đừng đoán? |
| 4 | Chiến lược backpressure thay xếp hàng vô hạn | Hàng đợi của tôi dài bao nhiêu thì từ chối? |

---

## 2. Cơ chế

### 2.1 Concurrency ≠ Parallelism — câu cửa miệng nhưng đúng

**Concurrency** là cấu trúc (nhiều việc đan xen); **parallelism** là thực thi (nhiều lõi cùng lúc). Một CPU 1 lõi vẫn concurrent (event loop); 8 lõi chạy 8 batch song song mà không đan xen vẫn parallel. Chọn mô hình concurrency quyết định *hình dạng* code; phần cứng quyết định *độ rộng* thực thi. Hầu hết server là **I/O-bound concurrent** — và đó là lý do event loop/green thread thắng ở tầng web, không phải vì "nhanh hơn" mà vì **rẻ hơn khi chờ**.

### 2.2 Ba công thức nền của mọi sizing

1. **Little's Law:** `L = λ × W` (đang xử lý = throughput × độ trễ). Biết 2 → suy ra 3. Sizing pool (→3.10), chiều dài queue, số kết nối — tất cả là Little.
2. **Amdahl:** speedup ≤ `1 / (s + (1−s)/n)` — phần tuần tự **s** ghim trần. s = 10% thì 100 lõi chỉ được ~9,1×. Kinh nghiệm: ở hệ thật, "s" thường là lock + I/O chia sẻ, không phải thuật toán.
3. **Utilization–latency (queueing):** thời gian chờ tăng phi tuyến khi utilization → 1 (M/M/1: W ∝ ρ/(1−ρ)). Vì vậy "CPU 80%" là biên vận hành, 95% là thảm hoạ p99 — không phải vì tôn giáo mà vì toán.

### 2.3 Bốn mô hình concurrency — ai chờ kiểu nào

| Mô hình | Đại diện | Chờ I/O tốn | Bẫy đặc trưng |
|---|---|---|---|
| Thread-per-conn | Java cổ, C servlet | 1 thread (stack) mỗi chờ | switch + stack (→2.3) |
| Event loop | Node, Redis, nginx | ~0 khi chờ (1 loop) | một việc chặn → tất cả chờ (→3.3) |
| Green/fiber | Go goroutine, Java virtual threads | ~KB mỗi chờ | scheduling không hợp tác (block C-lib) |
| Async/await | Rust, Python, JS, C# | ~0–KB, cần `await` đúng chỗ | "async màu" lây toàn call stack; blocking giấu |

Quy tắc chọn thực dụng: request ngắn + chờ nhiều → event loop/async; CPU đặc + thư viện chặn → thread pool; "muốn code tuần tự mà scale" → green threads. **Chưa từng có mô hình thắng tuyệt đối — chỉ có mô hình hợp bài toán.**

### 2.4 Bốn trường phái quản lý bộ nhớ

| Trường phái | Đại diện | Cách hoạt động | Giá phải trả |
|---|---|---|---|
| **Tracing GC** | JVM, Go, V8 | dò đồ tham chiếu, dọn thế hệ | pause (nay µs–ms), RSS > live heap |
| **Reference counting** | Python, Swift,ObjC | đếm tham chiếu, free khi về 0 | chu kỳ → leak (cần cycle detector); atomic RC tốn CPU |
| **Ownership** | Rust, C++ (RAII) | compiler chứng minh ai giải phóng | đường cong học; design quanh borrow |
| **Manual** | C, C++ thô | malloc/free tay | use-after-free/double-free — cả ngành CVE |

Ba nhận định để không mê hoặc:
1. **Pause không còn là boogeyman:** ZGC/Shenandoah ~sub-ms, Go GC ~sub-ms thường (→3.4/3.6). Giết p99 ngày nay thường là **thuât toán cấp phát** (humongous, large object) chứ không phải bản thân GC.
2. **RC không "không tốn":** mọi gán biến là một atomic đếm — ở workload đếm nhiệt, RC thua tracing cả về CPU lẫn cache (→1.2).
3. **Ownership không miễn phí vận hành:** leak vẫn có (Arc cycle), chỉ đổi chỗ đứng — sang review con người.

### 2.5 Hợp tác vs chiếm đoạt (cooperative vs preemptive)

Event loop/goroutine-y-cần-yield: hợp tác — đơn giản hoá suy luận (không có race tự sinh giữa 2 dòng) tới khi một task quên nhường. Thread OS: chiếm đoạt — mọi dòng code đều có thể bị chen giữa — do đó cần lock/volatile. Go từ 1.14 preempt được goroutine (async preemption) — thu hẹp khoảng cách; Java virtual thread pin (`synchronized`) tới JDK 24 mới tháo hết — xem 3.6.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Stack goroutine/virtual thread | ~KB lúc khởi đầu | V | vs 8 MB thread OS |
| Go GC pause | < 1 ms thường | V | p99 theo heap |
| ZGC pause | < 1 ms (thuật toán thiết kế 10ms max) | V | JDK 21+ generational |
| Utilization an toàn | 70–80% | I | queueing phi tuyến |
| Amdahl s=10%, 64 lõi | ~7× | V | không phải 64× |

---

## 4. Suy luận kiến trúc

- **S1:** Mô hình concurrency + trường phái bộ nhớ là **hợp đồng nền** của ngôn ngữ — quyết định chúng sau khi viết code là quyết định đắt nhất trần trung.
- **S2:** Tham số trụ: số unit đồng thời (thread/goroutine/task), await-blocking time (việc chặn lén), GC pause p99, queue depth.
- **S3:** Mỗi mô hình đổi một thứ: thread đổi RAM lấy sự đơn giản; event loop đổi đơn giản lấy "một con ngựa"; green đổi scheduler tự viết lấy UX tuần tự; async đổi "màu hàm" lấy độ rẻ.
- **S4:** Lõi đông + RAM rẻ làm chi phí "1 thread/chờ" giảm tương đối — virtual thread/goroutine hợp xu hướng phần cứng; nhưng lock + false sharing vẫn là phần tuần tự thật (Amdahl).
- **S5:** Hệ sinh thái đang quy tụ về "runtime lo concurrency, người viết logic" (Go, Java VT, Kotlin coroutines, Swift async) — kỹ năng khó còn lại là **nhận ra việc chặn**.
- **S6:** Khi hệ thống "chậm vô cớ", trở về ba công thức: Little (đủ unit?), queueing (utilization bao nhiêu?), Amdahl (phần tuần tự là gì?) — 80% trường hợp có câu trả lời từ đây.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Thêm worker không tăng throughput | Amdahl: lock/I/O chia sẻ | profile phần tuần tự; đo lock | §2.2 |
| p99 nổ khi CPU > 80% | Queueing phi tuyến | utilization graph + latency | §2.2 |
| "Leak" ở Python/Swift | Reference cycle | gc module/heap snapshot | §2.4 |
| Event loop lag chu kỳ | Việc chặn định kỳ (→3.3) | loop lag metric | §2.3 |
| GC pause nhưng p99 vẫn tệ | Cấp phát humongous/large | alloc profile | §2.4 |

---

## 6. Cách đo

```bash
# Little's law kiểm chứng: L = λ × W
# throughput (req/s) × độ trễ trung bình (s) ≈ số request đang xử lý?
# — so với số worker/conn: nếu lệch lớn, queue đang nuốt đâu đó

# Utilization & queue theo thời gian thật
# (mọi monitoring có; câu hỏi là có ai vẽ chúng trên cùng trục không)

# Async blocking audit (ví dụ Python)
python -X importtime app.py        # import chặn khởi động
# asyncio debug mode: PYTHONASYNCIODEBUG=1 — phát hiện blocking trong loop
```

Nguyên tắc: **vẽ throughput, utilization, latency, queue trên cùng một trục thời gian** — bốn đường này cộng lại chính là "điện tâm đồ" của hệ concurrent.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay đổi mô hình concurrency (đắt):** trước hết thử — tăng/ giảm unit theo Little, bóc phần tuần tự (shard, cache — →5.4/5.5), hoặc tách service theo hồ sơ chờ (I/O vs CPU). **Thay đổi trường phái bộ nhớ (rất đắt):** gần như chỉ đáng khi pause thực sự là cổ chai đã chứng minh (đo p99 theo nguyên nhân, không theo cảm giác).

Năm thấu kính:
- **Kinh tế:** Nhầm mô hình concurrency được phát hiện muộn = viết lại đường nóng; chi phí ấy là lý do chương này đứng trước các chương ngôn ngữ.
- **Vận hành:** Mỗi runtime có "đồng hồ báo chặn" riêng (loop lag, scheduler latency) — đưa chúng vào dashboard chung để so sánh các service xuyên ngôn ngữ.
- **An ninh:** Concurrency bug = race = hành vi không tái lập được — mẫu đất nuôi exploit (TOCTOU); sanitizer/TSan là công cụ an ninh cũng như chất lượng.
- **Lịch sử:** Từ coroutine thập niên 60 (Simula) → thread 90s → event loop 2000s (C10K) → async/await 2010s → virtual thread 2020s: ngành quay về "code tuần tự, runtime lo" — mỗi vòng lớn hơn, ít hạn chế hơn.
- **Người dùng:** Mọi "giờ cao điểm chậm" đều là một trong ba công thức §2.2 nói to lên — chương này dạy nghe được tiếng của chúng.

---

## 8. Đọc tiếp & bài tập

- Từng runtime: **3.2–3.7** · Pool sizing thực hành: **3.10** · Backpressure & queue: **4.2, 5.7** · Độ trễ & queueing sâu hơn: **8.5**
- **Bài tập 1:** Đo service của bạn: throughput × latency trung bình = bao nhiêu unit đang xử lý? So với cấu hình worker. Sai số > 2× nghĩa là có hàng đợi vô danh.
- **Bài tập 2:** Ước tính Amdahl: chạy benchmark 1 lõi và N lõi; suy ra phần tuần tự s. Ghi con số — nó sẽ không đổi nhiều khi bạn tối ưu, trừ khi tấn công đúng chỗ.
- **Bài tập 3:** Với một bug "không tái lập được" quen thuộc của team: viết lại giả thuyết race (2 dòng code chạy xen kẽ thế nào). Nếu viết được — bạn vừa có test case TSan.
