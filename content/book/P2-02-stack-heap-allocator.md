# 2.2 — Stack vs Heap, Allocator & Nguyên lý Đồng bộ cấp thấp

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** part1-hardware-os.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 1.3 · 2.1.

**Sợi chỉ đỏ:** *Process thấy cả một không gian địa chỉ 'của mình' — bên trong, stack và heap vận hành ra sao?* — trả lời: bên trong không gian địa chỉ đó, stack cấp phát rẻ theo con trỏ còn heap do một họ allocator quản — và chương này chỉ đúng chỗ tiền rơi ra: fragmentation, khoá, false sharing. Câu hỏi để lại cho chương sau: *Nhiều process chia một CPU — scheduler cắt lát thế nào, và vì sao quota 500m lại giết p99?*

**Thuật ngữ sẽ gặp:** *stack* — vùng cấp phát theo chồng, rẻ nhất hệ sinh thái; *heap* — vùng cấp phát tuỳ ý theo vòng đời đối tượng; *allocator* — malloc/jemalloc/mimalloc: cùng một tên việc, hiệu năng khác nhau; *fragmentation* — bộ nhớ còn rảnh nhưng xếp không lọt; *mutex/lock-free* — hai cách nhiều thread cùng vào một dữ liệu; *false sharing* — hai thread đánh nhau trên cùng một dòng cache dù dữ liệu khác nhau (nối 1.2).

**Ví dụ mở đầu:** Service DM rò 20 byte mỗi request — không ai thấy trong 6 giờ đầu; ngày thứ ba RAM cạn và OOM killer bắn. Leak hiếm khi nằm ở chỗ "quên free" hiển nhiên: nó nằm ở closure giữ tham chiếu, ở cache không TTL, ở fragmentation khiến bộ nhớ "rảnh mà không dùng được".

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Allocator cho workload (glibc / jemalloc / mimalloc / per-runtime) | Tôi phân mảnh, đa lõi, hay lifetime ngắn là chủ đạo? |
| 2 | Ngưỡng "đáng đưa lên heap" của cấu trúc dữ liệu | Cấu trúc này sống lâu hay chết trong microseconds? |
| 3 | Khóa mức thấp: mutex, CAS spinlock, hay lock-free queue | Độ tranh chấp tôi đo được là bao nhiêu? |
| 4 | Stack size cho service (thread stack × số thread) | 8 MB mặc định × 5.000 thread = bao nhiêu GB ảo? |

---

## 2. Cơ chế

### 2.1 Stack: cấp phát rẻ nhất hệ sinh thái

Stack là con trỏ di chuyển: push/pop ~1 lệnh; giải phóng "miễn phí" (di chuyển con trỏ về). Mỗi thread một stack (mặc định Linux 8 MB **ảo** — chỉ chiếm vật lý phần chạm tới, vài trang). Vì thế "5.000 thread × 8 MB" chưa chắc tốn RAM — nhưng tốn không gian địa chỉ + VMA, và runtime có giới hạn riêng (JVM stack 512KB–1MB/thường).

Hạn chế: kích thước biên dịch/đặt trước, không sống qua lời gọi hàm. Cấu trúc sống lâu hơn frame → heap.

### 2.2 Heap và allocator: malloc không phải một thứ, là một họ

`malloc` của glibc: **per-thread arena** (tối đa 8× số lõi trên 64-bit) để tránh tranh mutex; mỗi arena chia **bin** theo kích thước; free không trả OS ngay mà giữ lại (giải phóng thật qua `trim_threshold`). Hệ quả hai mặt:
- Tốt: cache warm, cấp phát nhanh (~dozens ns sau warm-up);
- Xấu: **phân mảnh** — RSS không giảm sau khi free (triệu chứng "memory leak" mà không phải leak); nhiều arena × workload chạm ngẫu nhiên = footprint phình.

Các lựa chọn: **jemalloc** (size class chặt, chống phân mảnh tốt — mặc định FreeBSD/Facebook/Redis khuyến nghị), **tcmalloc** (Google, thread-cache hào phóng — nhanh nhưng giữ bộ nhớ), **mimalloc** (Microsoft, nhanh và gọn cho workload ngắn hạn). Per-runtime: JVM/Go/.NET có allocator riêng (bump-pointer trong nursery — nhanh hơn malloc nhiều lần), Python đối tượng nhỏ qua pool (pymalloc) — xem 3.x.

### 2.3 Đồng bộ: từ mutex đến lock-free

Ba mức, giá tăng dần:
1. **Fast path không tranh chấp:** `pthread_mutex_lock` = một CAS — ~20 ns (I);
2. **Tranh chấp:** futex — ngủ trong kernel, đánh thức tốn µs; **đây là chỗ "lock rẻ" đột nhiên đắt**;
3. **Spinlock/CAS loop:** chờ bận — tốt khi miền tới rất ngắn và một socket; tệ khi chờ lâu (đốt CPU) hoặc xuyên NUMA (→1.3).

Lock-free (queue, stack) dùng CAS vòng lặp: miễn dịch deadlock, không có priority inversion — nhưng khó viết đúng (ABA, memory ordering: acquire/release đủ đa số trường hợp, seq_cst cho thuật toán phi tuyến tính). **Quy tắc thực dụng: đo trước khi lock-free hoá** — thường cách rẻ nhất là giảm tần suất chạm (shard, per-thread counter, batching).

Đồng bộ ngôn ngữ xây trên đúng các nguyên tử này: `sync.Mutex` (Go), `synchronized` (JVM — biasable locker đã bị xoá, 15–18µs thời JEP… giờ thuần CAS+futex), `std::sync::Mutex` (Rust — poisoning là cải tiến thiết kế thật: nới lỏng dữ liệu không lây lan).

### 2.4 Memory ordering và false sharing (nối 1.2)

Compiler + CPU sắp xếp lại lệnh; mô hình bộ nhớ ngôn ngữ (C++ acquire/release, Java volatile, Go happens-before, Rust Send/Sync) là **hợp đồng** về thứ tự nhìn thấy. Chương này chỉ cần một quy tắc: **publish cờ sau cùng, đọc dữ liệu trước cờ** — và đánh dấu cờ bằng nguyên tử có release (ghi) / acquire (đọc). False sharing đã ở 1.2 §2.2 (dòng cache 64B) — allocator tốt sẽ pad size class để tránh.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Stack push/pop | ~1 lệnh | V | |
| Thread stack mặc định | 8 MB (ảo) Linux | V | JVM/Go nhỏ hơn nhiều |
| malloc không tranh | ~50–100 ns | I | warm |
| CAS không tranh | ~10–20 ns | I | |
| futex đánh thức | ~1–5 µs | I | bối cảnh +2 syscall |
| Tăng RSS sau free | bình thường với glibc | I | fragmentation, không phải leak |

---

## 4. Suy luận kiến trúc

- **S1:** Chi phí allocator/sync là hằng số nhỏ nhân với tần suất — ở workload QPS cao, "nanoseconds × triệu/giây" thành giây CPU thật.
- **S2:** Tham số trụ: malloc/s, mutex contentions (off-CPU), fragmentation ratio (RSS vs live bytes theo heap profile).
- **S3:** jemalloc đổi RSS lấy đô độ trễ ổn định; lock-free đổi độ phức tạp đúng-đắn lấy tail; per-thread everything đổi cuối cùng nhất quán lấy throughput.
- **S4:** Lõi tăng nhanh hơn tốc độ một lock — kiến trúc "một lock toàn cục" già đi theo phần cứng (giờ đây rõ ràng thua trên 32+ lõi).
- **S5:** Runtime có GC (Go/Java/JS) thuần hoá allocator khỏi bàn tay lập trình viên — kỹ năng đọc heap profile thay thế kỹ năng viết pool tự chế (và pool tự chế thường phản tác dụng với GC thế hệ mới).
- **S6:** Khi profile cho thấy "allocator/lock nóng", lùi lại: bớt cấp phát (object reuse sai ở GC-lang, đúng ở C++), bớt chạm (shard), rồi mới đổi allocator/khóa.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| RSS không giảm sau khi "free hết" | Fragmentation (arena giữ lại) | `malloc_stats()`/jemalloc stats; heap profile | §2.2 |
| Latency spike theo số lõi tăng | Arena/mutex tranh chấp xuyên NUMA | `perf lock`; off-CPU flame | §2.2, §2.3 |
| CPU 100% nhưng throughput sụt | Spinlock chờ lâu / backoff thiếu | perf; flame graph đỉnh `__pauser`/`osq_lock` | §2.3 |
| Đôi khi số liệu sai lơ lửng | Thiếu ordering (cờ không release/acquire) | TSan/Go race detector | §2.4 |
| Thread tạo mới thất bại | Hết không gian địa chỉ stack | `ulimit -s`×số thread vs VSZ | §2.1 |

---

## 6. Cách đo

```bash
# Off-CPU: đợi lock/allocator là gì?
# (BCC)      offcputime-bpfcc -p <pid> 30
# (perf)     perf record -e sched:sched_switch ./app

# Allocator của tiến trình C/C++
MALLOC_CONF=stats_print:true jemalloc-enabled-app    # fragmentation thật
valgrind --tool=massif ./app                          # profile heap theo thời gian

# Runtime khác: heap profile là chuẩn (xem 3.x từng ngôn ngữ)
# Go:       go tool pprof http://localhost:6060/debug/pprof/heap
# Java:     jcmd <pid> GC.class_histogram

# Thread & stack audit
cat /proc/<pid>/status | grep Threads
pmap -x <pid> | tail -3        # tổng VSZ/RSS
```

Nguyên tắc: **on-CPU flame cho biết tính gì; off-CPU cho biết chờ ai** — lock và allocator sống ở vế thứ hai.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay lock:**
message passing (channel/queue — tuần tự hoá qua một điểm), RCU/epoch cho read-heavy, hoặc thiết kế lại không cần chia sẻ (share-nothing — →3.10 mỗi worker một phân vùng). **Thay heap optimize:** đưa object về stack (escape analysis — Go/Rust làm tự động), arena/region lifetime (Rust `bumpalo`, C++ `pmr`), hoặc bỏ hẳn: columnar/buffer pool ở tầng DB (→5.2).

Năm thấu kính:
- **Kinh tế:** Đổi allocator là patch 1 dòng + đo 1 tuần — ROI thường cao hơn viết lại code; nhưng chỉ khi đo ra fragmentation thật.
- **Vận hành:** Link allocator vào binary (LD_PRELOAD dễ; static link sạch hơn) và **ghi vào runbook** — allocator lạ đổi hành vi OOM/heap.
- **An ninh:** Allocator là bề mặt khai thác kinh điển (heap feng shui, tcache poisoning…); hardened allocator (scudo, hardened_malloc) đáng cân nhắc cho service nhận input lạ.
- **Lịch sử:** Bài toán concurrent malloc định hình cả ngành (paper jemalloc/tcmalloc thập niên 2000); kết cục dồn về 3 họ còn sống — và bài học "arena per-thread" lặp lại trong JS heap, Go mcache: cùng một thuốc cho cùng một bệnh.
- **Người dùng:** Người dùng chỉ cảm nhận hai thứ từ chương này: "tốn RAM" (fragmentation) và "đôi khi chậm" (lock). Cả hai đều có thể đo — và khi đo được thì không còn là "đôi khi".

---

## 8. Đọc tiếp & bài tập

- Cache/false sharing: **1.2** · GC các trường phái: **3.1** · Leak trong từng runtime: **3.9** · Pool & Little's law: **3.10**
- **Bài tập 1:** Viết counter 4 thread chia một biến `long` vs mảng pad 64B mỗi thread; đo thời gian. Giải thích bằng 1.2 §2.2.
- **Bài tập 2:** Với service C/C++ đang chạy: thu `malloc_stats` (hoặc jemalloc stats); tính fragmentation = 1 − live/allocated. > 30% là đáng đổi allocator.
- **Bài tập 3:** Đếm số thread × stack size của service bạn. Nếu VSZ > 10× RSS, bạn đang nằm ở vùng "ảo nhiều hơn thật" — chỉ cần biết để khỏi hoảng khi đọc monitor.
