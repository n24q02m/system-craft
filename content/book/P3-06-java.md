# 3.6 — Java / JVM Runtime (8 → 25 LTS / 27)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** lang-6.md

---

## 0. Nhập môn

**Đọc trước:** 3.1 · 3.4 (để soánh Goroutine).

**Sợi chỉ đỏ:** *Đội to dần cùng di sản JVM — virtual threads có đổi trò chơi không?* — trả lời: JVM đắt lúc khởi động vì JIT chưa nóng nhưng chạy càng lâu càng nhanh; G1 là mặc định, ZGC cho p99; virtual threads đưa mô hình thread-per-request trở lại với giá rẻ như goroutine. Câu hỏi để lại cho chương sau: *C++ vẫn đứng ở đâu trong stack của DM, và giá của nó là gì?*

**Thuật ngữ sẽ gặp:** *JIT* — biên dịch tăng dần theo độ nóng của code: chậm lúc mới lên, nhanh dần sau; *G1/ZGC* — hai GC: một cân bằng mặc định, một pause dưới miligiây cho p99; *virtual thread* — thread nhẹ do JVM quản (Project Loom), chờ I/O không tốn OS thread; *pin* — virtual thread dính vào carrier thread vì khối synchronized; *container awareness* — JVM đọc đúng limit CPU/RAM của pod thay vì của máy thật.

**Ví dụ mở đầu:** Hệ đối soát chạy trên JVM mười năm: khởi động 90 giây, báo cáo đêm đầu chậm hơn đêm sau 40%. Người mới tưởng "máy lạnh" — thực ra máy đang ấm dần theo JIT. Và dịch vụ checkout từng đặt pool 200 thread cho 200 request chờ I/O: sau khi bật virtual threads, cùng tải đó chỉ cần vài chục OS thread thật.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Thread model: virtual threads (21+) hay platform pool | Code tôi chờ I/O nhiều? Thư viện đã pin-safe chưa? |
| 2 | GC: G1 (mặc định) / ZGC generational / Shenandoah | Pause chấp nhận: ms hay sub-ms — đổi bằng CPU bao nhiêu? |
| 3 | Heap sizing trong container (MaxRAMPercentage, không -Xmx cứng) | Limit K8s là gì — heap + metaspace + direct nhớ đủ chưa? |
| 4 | Upgrade path LTS 17/21/25 — thời điểm và trở lực | App tôi còn ở 8/11 bao lâu nữa, và ai sở hữu quyết định? |

---

## 2. Cơ chế

### 2.1 Trạng thái phiên bản (verify 2026-10-30)

| Phiên bản | Trạng thái | Điểm đáng chú ý |
|---|---|---|
| 27 (10/2026) | non-LTS mới nhất | tiếp tục đà 6-tháng |
| **25 LTS** (9/2025) | LTS hiện hành (EOL 2031) | Scoped values ổn định; những cải tiến nhỏ khác |
| 21 LTS (2023) | LTS (EOL 2029) | virtual threads GA; generational ZGC; pattern matching |
| 17 LTS (2021) | LTS (EOL 2027) | ít nhất nên ở đây |
| 8/11 | 11 EOL 10/2026 gần; 8 prolonged support riêng | **di cư**: đa số org đã xong, số còn lại đang trả lãi |

Chu kỳ hiện đại: LTS mỗi 2 năm (17→21→25), non-LTS mỗi 6 tháng.

### 2.2 JIT: warmed-up machine

JVM interpreter → C1 (nhanh compile) → C2 (tối ưu theo profile). Hệ quả:
- **Warm-up thật**: benchmark phải qua vài trăm nghìn invocation; FaaS lạnh với JVM là ngược sở trường (vì thế có CRaC/AOT — §2.5);
- **Deoptimization** khi giả định vỡ (đa hình quá mức, reflection) — "code chậm hơn sau refactor" thường ở đây;
- **JFR (Java Flight Recorder)** — flight recorder always-on chi phí <1% (V) — quan sát chất lượng sản xuất tốt nhất ngành, bật mặc định.

### 2.3 GC 2026: G1 mặc định, ZGC/Shenandoah cho p99

- **G1** (mặc định từ 9): vùng hoá, pause mục tiêu ~ms — đủ cho đa số;
- **ZGC generational** (21+): pause < 1 ms kể cả heap TB; chi phí CPU ~5–10% (I) — cho p99 khắt khe;
- **Shenandoah**: tương tự thế hệ, một số workload thắng ZGC nhẹ — đo trên app bạn.
- Hai bẫy kinh điển: **humongous allocation** (G1: object > nửa vùng → phân phối đặc biệt → pause/fragmentation) — thường do list/byte[] khổng lồ; và **heap gần max** (GC chạy như kho cuối mùa — theo dõi "post-GC live" để phân biệt leak với quá tải).

### 2.4 Virtual threads (Project Loom, 21 GA)

`Thread.ofVirtual()` — hàng triệu thread "nhẹ" do JVM schedule lên platform thread. Chỉ hợp **chờ I/O**; CPU-bound vẫn cần platform pool. Cạm bẫy lịch sử: `synchronized` pin platform thread — **JDK 24 bỏ pin này** (JEP 491, verified lộ trình) — thư viện cũ an toàn dần; tạm thời dùng `ReentrantLock` thay cho hotspot. Quyết định kiến trúc: virtual thread + chuẩn hoá structured concurrency (`StructuredTaskScope` — preview) = "code tuần tự, scale như async" — thay thế gần như toàn bộ reactive-stack (WebFlux) cho use case chờ I/O.

### 2.5 JVM trong container & FaaS

- **Đặt `-XX:MaxRAMPercentage=75`** (75% limit) thay `-Xmx` cứng — nhớ để 25% cho metaspace + code cache + direct buffer + thread stack;
- **CRaC** (Coordinated Restore at Checkpoint): checkpoint JVM warmed → restore ms — giải quyết cold start cho JVM serverless (AWS Lambda SnapStart sản phẩm hoá (V));
- **AOT/Leyden** (Project Leyden, đang theo lộ trình 2024–2027): rút ngắn khởi động thêm nữa — theo dõi, chưa mặc định.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| LTS hiện hành | 25 (EOL 2031) | V | versions.csv |
| G1 pause mục tiêu | ~ms | V | |
| ZGC pause | < 1 ms (heap TB) | V | CPU ~5–10% (I) |
| Virtual threads GA | 21; unpin synchronized JDK 24 | V | |
| JFR overhead | < 1% | V | tài liệu Oracle |
| Warm-up cần | 10⁴–10⁵ invocation | I | benchmark lưu ý |

---

## 4. Suy luận kiến trúc

- **S1:** JVM đổi "cứng nhắc khởi động/warm-up" lấy "throughput đỉnh sau nóng" — hợp service dài hạn, ngược FaaS (trừ khi CRaC).
- **S2:** Tham số trụ: pause p99 (GC log/JFR), heap sau GC (live), thread count, CPU% JIT+GC tách biệt.
- **S3:** ZGC đổi CPU lấy p99 phẳng; virtual threads đổi reactive-complexity lấy mô hình tuần tự; CRaC đổi tính portable lấy khởi động ms.
- **S4:** Java 8→25 là 10 năm hiện đại hoá nén lại: records, sealed, pattern matching, VT, ZGC — codebase "Java hiện đại" khác Java 8 nhiều như TypeScript khác ES5; quyết định upgrade là quyết định năng suất.
- **S5:** Hệ sinh thái enterprise (Spring 6/7, Kafka clients, CDC, JVM data stack) đủ sâu để "Java là mặc định doanh nghiệp" tự củng cố — rủi ro nằm ở staying-back chứ không phải chọn nó.
- **S6:** Khi JVM chậm: đọc GC log/JFR trước. 80% là heap/GC/humongous hoặc lock; không phải "Java chậm".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Pool cạn thread, service treo | Thread-per-conn + I/O chậm | JFR; jstack; pool metrics | §2.4 |
| Pause vài trăm ms định kỳ | G1 humongous / heap gần max | GC log; JFR alloc profile | §2.3 |
| Sau deploy chậm 10 phút | JIT warm-up + C2 chưa tối ưu | JFR compiler events | §2.2 |
| OOM nhưng heap chưa full | Metaspace/direct/thread stack tràn | NMT; native memory tracking | §2.5 |
| Virtual thread không scale | Pin synchronized (thư viện cũ) | JFR pin events; JDK 24 | §2.4 |
| Cold start FaaS tệ | JVM khởi động + class loading | CRaC/SnapStart | §2.5 |

---

## 6. Cách đo

```bash
# Chẩn nhanh một JVM đang chạy
jcmd <pid> VM.uptime GC.heap_info Thread.print | head -50
jcmd <pid> JFR.start duration=120s filename=rec.jfr   # flight recorder 2 phút

# GC log — luôn bật từ ngày đầu
java -Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=5,filesize=20m ...

# Heap histogram nhanh
jcmd <pid> GC.class_histogram | head -20

# Phân tích offline: VisualVM / async-profiler (flame + alloc)
./asprof -d 30 -f flame.html <pid>
```

Nguyên tắc: **JFR + GC log là hai mắt** — bật luôn (chi phí <1%), vì bằng chứng phải có trước khi sự cố xảy ra.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay đổi GC:** trước hết giảm cấp phát (object pooling ngược thời đại — thay bằng: bớt allocation nóng, primitive/specialized collection, immutable reuse). **Thay WebFlux reactive:** virtual threads đạt cùng mục tiêu với code tuần tự — refactor dần theo module. **Thay JVM cho FaaS:** Go/Rust native (→3.4/3.5) hoặc CRaC nếu buộc giữ thư viện Java.

Năm thấu kính:
- **Kinh tế:** Team Java lớn và dễ tuyển; chi phí nằm ở upkeep phiên bản — mỗi năm trên LTS chết là nợ CVE + năng suất mất dần.
- **Vận hành:** JVM metrics đã sâu nhất ngành — tận dụng: mỗi service nên expose JFR→Prometheus qua JMX exporter.
- **An ninh:** Log4Shell (2021) dạy một bài học hệ sinh thái: dependency lớn = bề mặt lớn — SBOM + scanner (→10.4) cho JVM đặc biệt quan trọng.
- **Lịch sử:** Từ "ngôn ngữ applet" (1995) qua J2EE nặng nề tới virtual threads (2023): mỗi 10 năm JVM tái sinh một lần; tuyên bố "Java chết" là một thể thao không bao giờ thắng.
- **Người dùng:** Người dùng JVM tốt = "ổn định qua năm"; JVM xấu = "mỗi ngày 14h00 đứng 2 giây". Chương này là công cụ xoá các chữ số trên đồng hồ đó.

---

## 8. Đọc tiếp & bài tập

- Ma trận runtime: **3.9** · HTTP stack JVM: **3.11** · GC lý thuyết: **3.1** · Queue & backpressure: **5.7**
- **Bài tập 1:** Bật `-Xlog:gc*` trên một service production; đọc 1 ngày log: pause p99, live heap sau GC. Hai con số này định hướng mọi quyết định GC tiếp theo.
- **Bài tập 2:** Với một endpoint chờ I/O: thử virtual threads (Spring Boot 3 + `spring.threads.virtual.enabled=true`). So p99 và thread count — viết xuống kết luận.
- **Bài tập 3:** Chạy `jcmd GC.class_histogram` lúc tải cao; tìm object > 10% heap — đó là ứng viên "humongous" hoặc leak thật; truy về code.
