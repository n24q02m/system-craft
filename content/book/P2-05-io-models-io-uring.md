# 2.5 — Mô hình I/O: epoll, Reactor/Proactor, io_uring & Zero-copy

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** part1-hardware-os.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 2.3 · 2.4.

**Sợi chỉ đỏ:** *Một process phải hứng trăm nghìn connection — mô hình I/O nào sống nổi?* — trả lời: từ blocking I/O qua epoll tới io_uring — bốn thế hệ mô hình I/O, mỗi thế hệ hạ chi phí "chờ" xuống một bậc; chọn thế hệ theo số connection và hình dạng công việc. Câu hỏi để lại cho chương sau: *Gói tin từ socket xuống card và ngược lại — netstack có chỗ nghẽn nào theo số lượng?*

**Thuật ngữ sẽ gặp:** *blocking I/O* — một thread chờ một I/O, mỗi connection một thread; *epoll* — hỏi kernel "cái nào sẵn sàng" rồi mới xử lý; *readiness* — trạng thái descriptor đã đọc/ghi được; *io_uring* — hàng đợi chung hai chiều giữa app và kernel, giảm syscall; *zero-copy* — gửi file không chép qua không gian người dùng; *C10K* — bài toán xưa "mười nghìn connection", nay đã giải được.

**Ví dụ mở đầu:** Phiên bản đầu của DM mở một thread mỗi connection: 200 khách ổn, 5.000 thì máy gục — không phải vì CPU, mà vì 5.000 stack và 5.000 lần chuyển ngữ cảnh. Đổi sang epoll: cùng máy đó 50.000 connection nhàn nhã. Cùng phần việc, khác mô hình chờ.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Mô hình I/O: thread-per-conn / epoll+reactor / io_uring | Số kết nối đồng thời? Độ phức tạp code đội ngự được chưa? |
| 2 | Edge-triggered (ET) hay level-triggered (LT) với epoll | Tôi muốn ít wakeup (ET) hay dễ đúng (LT)? |
| 3 | Zero-copy (sendfile/splice) ở đâu trong đường phục vụ | Payload có cần TLS không — và kTLS đã có chưa? |
| 4 | Worker pool cho việc chặn (blocking) còn sót | Việc chặn còn lại chạy ở đâu để không lây event loop/pool chính? |

---

## 2. Cơ chế

### 2.1 Bốn thế hệ mô hình I/O

```
1. Blocking, thread-per-conn   — đơn giản; chết ở ~10k conn (stack+switch — 2.3)
2. Non-blocking + poll/select  — 1 thread quét tất cả fd; O(n) mỗi lần → chết ở ~10k fd
3. epoll readiness             — O(ready); event loop + thread pool → nginx/Node/Redis
4. io_uring completion         — gửi batch operation, nhận completion; async toàn đường
```

Bài học xuyên thế hệ: **chi phí chuyển từ "số kết nối × chi phí chờ" sang "số sự kiện × chi phí xử lý"** — và mỗi thế hệ giảm một lớp syscall/khởi tạo.

### 2.2 epoll: mức độ readiness và hai chế độ

`epoll_ctl` đăng ký fd; `epoll_wait` trả danh sách **đã sẵn sàng**. Chế độ **LT** (mặc định): báo tới khi còn dữ liệu — dễ đúng, hơi thừa wakeup. Chế độ **ET** (EPOLLET): báo 1 lần, buộc đọc cạn (loop tới EAGAIN) — hiệu quả hơn, sai một chỗ là mất event vĩnh viễn. **EPOLLEXCLUSIVE** chống thundering herd khi nhiều worker chờ cùng listen fd; **EPOLLONESHOT** cho pattern "một worker một lúc".

Reactor (dựa readiness — epoll/kqueue): "báo cho tôi khi **có thể** đọc/ghi". Proactor (dựa completion — IOCP Windows, io_uring): "làm giúp tôi rồi **báo kết quả**". Proactor hợp callback/future tự nhiên hơn; reactor hợp event loop. Toàn bộ async/await của ngôn ngữ (→3.x) là syntax xây trên một trong hai.

### 2.3 io_uring: vì sao nó là bước nhảy thật

Hai hàng đợi chia sẻ giữa user/kernel: **SQ** (submit) và **CQ** (completion). Gộp được nhiều op — kể cả `openat`, `fsync` (→2.4), `connect`, `send` — thành một submit; giảm syscall từ "mỗi op một cái" xuống "một batch một cái". Kèm: registered buffers/files (bỏ lookup), SQPOLL (kernel thread riêng hút SQ — zero syscall), hỗ trợ Await chain. Kết quả đo được: workload I/O dày giảm 20–50% CPU hệ thống (I, theo workload).

Chi phí của nó: **độ phức tạp và tuổi đời**. API khó, lỗi dùng dễ teo CQ (cần drain), một số bản kernel 2020–2022 từng là chủ đề security (mặc định tắt qua sysctl ở vài distro — kiểm tra `kernel.io_uring_disabled`). Node 22+/Go 1.25+ (runtime dùng dần cho file I/O), các DB mới (→5.x) adopt theo tuần tự. Quyết định: dịch vụ thường — runtime của bạn lo; service I/O chuyên dụng — đọc kỹ benchmark cho **đúng workload** rồi hãy viết theo.

### 2.4 Zero-copy: giảm bản sao trong đường gửi tĩnh

`sendfile()`: kernel đẩy file→socket không chạm userspace (2 bản sao → 0 copy CPU, DMA trực tiếp). `splice()`: ống giữa hai fd bất kỳ. Vấn đề: **TLS làm vòng gửi thường vô hiệu** — dữ liệu phải qua userspace để mã hoá. Lối ra: **kTLS** (kernel TLS — key nạp xuống kernel, sendfile hoạt động lại; dùng được ở nginx/Envoy) hoặc decrypt ở LB (terminating). Đo lại trước khi khẳng định lợi ích: payload nhỏ + TLS thường không thấy khác biệt.

### 2.5 Chọn theo bài toán — bảng quyết định

| Workload | Mô hình nên chọn | Vì sao |
|---|---|---|
| < 1k conn, code đơn giản quan trọng | thread-per-conn (hoặc runtime lo) | chi phí switch chấp nhận được (2.3) |
| 10k–1M conn, request ngắn | epoll + reactor (như nginx/Node) | không tạo thread theo conn |
| I/O dày + file + fsync (storage engine) | io_uring | gộp op, giảm syscall |
| Windows | IOCP (proactor gốc) | cổ nhất và vẫn tốt |

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| select/poll chi phí | O(n) mỗi call | V | chết ở ~10k fd |
| epoll_wait | O(ready) | V | |
| Syscall io_uring | ~1/batch (0 với SQPOLL) | I | |
| sendfile tiết kiệm CPU | 30–50% (payload tĩnh lớn, không TLS) | I | đo lại từng trường hợp |
| io_uring ổn định | 5.15+; 6.x khuyến nghị | I | kiểm tra sysctl distro |

---

## 4. Suy luận kiến trúc

- **S1:** Mô hình I/O quyết định **đường cong chi phí theo kết nối** — exponential (thread) vs phẳng (event) — trước khi bất kỳ tối ưu nào khác có ý nghĩa.
- **S2:** Tham số trụ: conn/worker, event loop lag (→3.3), syscalls/request, CPU softirq (→2.6).
- **S3:** ET đổi hiệu năng lấy rủi ro mất event; io_uring đổi syscall lấy phức tạp; kTLS đổi khả năng gửi nhanh lấy lớp tin cậy kernel — không có lựa chọn một chiều tốt cho mọi thứ.
- **S4:** Hiệu ứngྒช hợp: io_uring + registered buffer + SQPOLL ≈ "CPU spends no time on I/O" — nhưng chỉ đáng ở QPS/IOPS đủ cao để chi phí cố định của phức tạp được chia đều.
- **S5:** Runtime hấp thụ dần (Go/Node dùng io_uring nội bộ cho file I/O) — lập trình ứng dụng sẽ ít thấy API này trực tiếp, trừ storage engine/việc đặc biệt.
- **S6:** Khi I/O chậm, phân tầng: model sai (chương này), netstack tắc (2.6), hay đĩa chậm (1.4/2.4)?

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Càng nhiều conn càng chậm tuyến tính | Thread-per-conn + switch (→2.3) | `vmstat` cs; ss -s count | §2.1 |
| Đôi khi "mất" request không lỗi | ET đọc không cạn | strace read pattern; chuyển LT thử | §2.2 |
| CPU cao ở softirq, không phải app | Netstack (→2.6) | perf softirq | §2.1 |
| Node/event-loop lag cao (→3.3) | Việc chặn chạy nhầm vòng chính | event-loop monitor | §2.5 |
| io_uring chết ở staging | sysctl disabled/blocked seccomp | `kernel.io_uring_disabled`; profile runtime | §2.3 |

---

## 6. Cách đo

```bash
# Syscall mỗi request — con số nên tiến về 0
strace -c -p <pid> -f -e trace=network,epoll_wait,io_uring_setup 2>&1 | tail -20

# Event loop lag (Node ví dụ; runtime khác có metric tương đương)
#  perf_hooks.monitorEventLoopDelay

# epoll sử dụng thật
cat /proc/<pid>/fd | wc -l       # số fd mở ≈ conn + file

# Benchmark mô hình: wrk/vegeta với giữ kết nối (keep-alive) BẬT
wrk -t8 -c20000 -d60s --latency https://svc/
```

Nguyên tắc: **đếm syscall/request và context switch/requests** — hai con số này là "tuổi thọ kiến trúc" của bạn; tăng 10× là đã chọn sai tầng giải pháp.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay viết reactor tay:** dùng runtime/framework có sẵn (Netty, tokio, Go netpoller, libuv) — trừ khi bạn *là* runtime. **Thay io_uring:** thread pool + epoll đủ cho 95% (nhiều hệ 10k QPS chạy hoàn toàn ổn); sự phức tạp chỉ trả tiền ở IOps hàng trăm nghìn. **Thay zero-copy:** cache + nén ở tầng ứng dụng (→5.4) thường giảm bytes nhiều hơn tinh chỉnh bản sao.

Năm thấu kính:
- **Kinh tế:** Nhầm mô hình I/O không hiện trong code — nó hiện trong hóa đơn máy chủ (cần gấp đôi máy cho cùng tải)— không nhận ra cho tới khi so sánh.
- **Vận hành:** io_uring mới về mặc định an ninh — gắn nó vào checklist review kernel/distro trước khi bật ở production.
- **An ninh:** Mô hình event-loop đơn luồng cũng là mô hình "một request chặn mọi request" (→3.3) — DoS tự nhiên; giới hạn thời gian xử lý từng phase.
- **Lịch sử:** select(1983)→poll→epoll(2002)→io_uring(2019): mỗi lần "kết nối nhiều hơn" lại kéo kiến trúc mới; chu kỳ ~15 năm, lần kế có thể là CXL/NIC-offload (→1.6).
- **Người dùng:** Người dùng thấy "server từ chối kết nối giờ cao điểm" — chương này là bản đồ giải phẫu của lời phàn nàn đó.

---

## 8. Đọc tiếp & bài tập

- Runtime dùng epoll/io_uring thế nào: **3.2–3.7** · Netstack sau socket: **2.6** · fsync trong chain: **2.4** · Backpressure: **4.2**
- **Bài tập 1:** Đo syscall/request của service bạn (strace -c ở tải thật). Nếu > 20, có cả một thế hệ I/O đang chờ bạn.
- **Bài tập 2:** Viết HTTP server nhỏ theo thread-per-conn rồi epoll (hoặc dùng runtime): đo p99 tại 100/1k/10k conn. Vẽ đường cong — sẽ không quên hình dạng của nó.
- **Bài tập 3:** Kiểm tra `kernel.io_uring_disabled` trên cụm production hôm nay. Không biết câu trả lời = không biết đường thừa thoát khi cần throughput I/O.
