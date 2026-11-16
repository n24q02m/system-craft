# 2.4 — VFS, Page Cache, Ngữ nghĩa Bền vững (fsync/O_DIRECT)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** part1-hardware-os.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 1.4 (SSD/fsync) · 2.1.

**Sợi chỉ đỏ:** *Ghi file mà máy chết giữa chừng thì sao — page cache và fsync đang chơi trò gì?* — trả lời: page cache biến RAM thành cache của đĩa — ghi "xong" thường mới tới RAM; fsync là lời thề đưa xuống đĩa, và ghi an toàn crash là một checklist bốn bước có thứ tự. Câu hỏi để lại cho chương sau: *Một process phải hứng trăm nghìn connection — mô hình I/O nào sống nổi?*

**Thuật ngữ sẽ gặp:** *page cache* — RAM giữ bản sao các trang đĩa để đọc nhanh và ghi gom; *fsync/fdatasync* — ép dữ liệu (kèm hay không kèm metadata) xuống đĩa thật; *writeback* — kernel dồn trang bẩn xuống đĩa theo nhịp, chỉnh được; *O_DIRECT* — đường thẳng bỏ cache cho DB tự quản; *pattern ghi an toàn* — ghi file tạm, fsync, rename, fsync thư mục.

**Ví dụ mở đầu:** DM ghi file config mới, hiện "Đã lưu", 10 giây sau mất điện — khởi động lại: file cũ. "Đã lưu" nói với page cache, chưa nói với đĩa. Cả một họ sự cố "dữ liệu biến mất dù app báo thành công" chỉ là một câu chuyện này — và có một checklist bốn bước chữa dứt.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Ngữ nghĩa bền vững: fsync/fdatasync mỗi commit, nhóm, hay không | Mỗi lần gọi trả bao nhiêu µs/ms? Ai gánh? |
| 2 | Buffered I/O hay O_DIRECT (hoà page cache) | Ai thông minh hơn về cache — kernel hay ứng dụng? |
| 3 | Cấu hình dirty writeback (vm.dirty_*) cho workload | Tôi muốn dirty pages dâng tới đâu trước khi kernel tự flush? |
| 4 | Pattern ghi an toàn crash (write-temp + rename + fsync dir) | Code tôi có tuân thủ "atomic rename" đúng không — kể cả thư mục? |

---

## 2. Cơ chế

### 2.1 Page cache: RAM biến thành cache của đĩa

Mọi `read()`/`write()` buffered đi qua **page cache**: đọc lần hai là RAM; ghi chỉ ghi vào bộ nhớ dirty rồi kernel **writeback** xuống đĩa sau (theo tuổi trang + tỉ lệ dirty). Lợi to: đĩa "biến nhanh"; rủi ro hai lớp:
- **Độ bền:** mất điện/panic = mất mọi thứ chưa writeback (và nếu đĩa consumer nói dối — →1.4 §2.1 — còn mất cả cái đã fsync);
- **Độ trễ không đều:** writeback dồn → I/O burst → "write() khựng" (mục 5).

### 2.2 fsync, fdatasync, sync_file_range — bậc thang bền vững

- `fsync(fd)`: đợi dữ liệu **và metadata** xuống đĩa thật (FLUSH/FUA tới SSD);
- `fdatasync(fd)`: chỉ dữ liệu (+metadata tối thiểu để tìm tới dữ liệu) — rẻ hơn khi file size không đổi;
- `sync()`: toàn hệ — không dùng cho service;
- không gọi gì: "best effort" — chấp nhận mất tới vài GB khi sập.

Chuỗi commit DB (WAL — →5.2) = ghi record + `fdatasync` + ghi positional checkpoint: chi phí fsync là **thông số #1** quyết định TPS của OLTP. SSD có PLP → fsync ~10 µs (P); không PLP → ms — chênh 100× (→1.4).

### 2.3 O_DIRECT và cuộc chiến "ai giữ cache"

`O_DIRECT` bỏ page cache (alignment 512B/4KB bắt buộc): DB lớn (PostgreSQL/Oracle) tự quản buffer pool — tránh double cache + kiểm soát eviction. Đổi lại: mọi lợi ích read-ahead của kernel mất; app sai alignment → lỗi hoặc âm thầm chậm. **Quy tắc:** dùng O_DIRECT chỉ khi ứng dụng có buffer pool riêng (DB, storage engine); ứng dụng thường để buffered là đúng.

Còn `mmap` + `msync`: tốt cho random-read file lớn tĩnh; tệ cho ghi bền (page fault + writeback khó kiểm soát — nhìn lại 2.1 §2.4).

### 2.4 Writeback tuning: ba con số quản cơn bão

`vm.dirty_ratio` (đến mức này thì process ghi bị **chặn** để flush — gốc "write khựng"), `vm.dirty_background_ratio` (kernel bắt đầu flush nền), `vm.dirty_expire_centisecs` (tuổi dirty tối đa). Workload ghi dồn (ETL, Kafka) nên hạ hai ratio (ví dụ 5/10) để writeback đều tay; máy latency-critical nên thấp nữa. Cũng nhớ cgroup v2 `io.max` — throttle I/O theo nhóm (thuốc cho "tenant này dập đĩa của tenant kia").

### 2.5 Pattern ghi an toàn crash — checklist atomicity

```
write file.tmp          # 1
fsync(file.tmp)         # 2 — dữ liệu xuống
close(file.tmp)
rename(file.tmp, file)  # 3 — atomic trong cùng filesystem
fsync(dir)              # 4 — METADATA rename xuống (hay bị quên!)
```

Bỏ bước 4: sau mất điện, file mới "biến mất" dù bước 3 đã chạy (rename chỉ nằm trong journal dir). Bỏ bước 2: rename thành công nhưng nội dung rỗng/loạn. Đây là lỗi kinh điển của mọi config-writer, từ nginx reload tới Kubernetes manifest — và là lý do "config mất sau restart" xảy ra.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| fsync (SSD PLP / không PLP) | ~10 µs / ~1–10 ms | P | →1.4 |
| fdatasync vs fsync | rẻ hơn khi size cố định | I | |
| Dirty ratio mặc định | 20% / 10% background | V | distro có thể override |
| Page cache hit | ~ns (RAM) | V | đọc lần 2 |
| O_DIRECT alignment | 512B–4KB | V | sai = lỗi/EIO |

---

## 4. Suy luận kiến trúc

- **S1:** Ngữ nghĩa bền vững là **hợp đồng với vật lý** (mất điện) — mọi lớp phía trên (DB transaction, queue ack) chỉ là cách đóng gói lại các fsync này (→5.2, →5.7).
- **S2:** Tham số trụ: fsync/s, dirty bytes (nr_dirty), iowait PSI io, TPS mỗi fsync-mode.
- **S3:** O_DIRECT đổi kiểm soát lấy gánh nặng đúng đắn; dirty tuning đổi đỉnh ghi lấy độ đều; group-commit đổi latency từng ghi lấy throughput — ba đòn trong cùng một toolbox.
- **S4:** SSD nhanh làm fsync rẻ đi 100× → thiết kế "commit mỗi record" (WAL strict) trở lại khả thi; từng bất khả thi trên HDD — kiến trúc cũ tồn tại vì đĩa cũ.
- **S5:** io_uring (→2.5) gộp được cả fsync vào chain async — lớp bền vững đang hoà vào lớp I/O chung.
- **S6:** Khi "ghi chậm", hỏi: chờ đĩa (→1.4), chờ writeback (mục 2.4), chờ fsync thật (mục 2.2), hay chờ lock của chính DB (→5.2)?

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| write() khựng đột ngột khi ghi nhiều | Dirty pages chạm dirty_ratio → chặn | `/proc/vmstat` nr_dirty; `iostat` util | §2.4 |
| DB TPS thấp hơn benchmark 10× | fsync trên đĩa không PLP | `pg_test_fsync`; fio --fsync=1 | §2.2 |
| File mới mất sau crash dù "đã lưu" | Thiếu fsync thư mục sau rename | audit code theo checklist §2.5 | §2.5 |
| RAM "cạn" dù process nhỏ | Page cache chiếm (tốt!) | `free -h` available; smaps | §2.1 |
| I/O latency lệch giữa tenant | Không io.max; shared volume | cgroup io.stat | §2.4 |

---

## 6. Cách đo

```bash
# Dirty pages & writeback bây giờ
grep -E 'nr_dirty|nr_writeback' /proc/vmstat
watch -n1 cat /proc/meminfo | grep -i dirty

# Chi phí fsync thật của máy bạn (PostgreSQL tool)
pg_test_fsync -s 3          # so từng chế độ

# Block I/O theo process + cgroup
iostat -xz 1
cat /sys/fs/cgroup/<path>/io.stat

# Trace fsync của một process
# (BCC)  fileslower / ext4slower 10
strace -e trace=fsync,fdatasync -p <pid> -f   # thô nhưng nói thật
```

Nguyên tắc: **đo fsync bằng pg_test_fsync trên chính đĩa production** — con số datasheet không nói dối nhiều bằng con số benchmark trên đĩa khác.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay fsync mỗi commit:** group commit (DB làm sẵn — chỉ cần bật/cấu hình), WAL trên thiết bị riêng, hoặc async replication + chấp nhận RPO (→5.2). **Thay O_DIRECT:** nâng RAM cho page cache (đôi khi rẻ hơn viết buffer pool), hoặc dữ liệu nóng đưa sang KV in-memory (→5.3). **Thay tuning writeback:** tách máy ghi-dồn khỏi máy latency — đôi khi câu trả lời là topology, không phải sysctl.

Năm thấu kính:
- **Kinh tế:** Một cặp sysctl dirty sai có thể "ăn" 30% throughput ETL; ROI của một giờ tuning đây thuộc loại cao nhất trong ngành.
- **Vận hành:** Mọi thay đổi storage (đĩa mới, filesystem mới) nên kèm chạy lại pg_test_fsync — fsync là hợp đồng của **cặp** OS+đĩa, không của đĩa một mình.
- **An ninh:** Page cache là nơi dữ liệu "sống" không mã hoá (at-rest encryption thường ở thiết bị — →10.5); dump RAM = dump dữ liệu — tính cho threat model của bạn.
- **Lịch sử:** "Torn write" từ thời HDD vẫn là bài học nền của mọi format file hiện đại (append-only log, LSM tree — →5.5): thiết kế để vết xé không phá hoại.
- **Người dùng:** Với người dùng, chương này tồn tại để trả lời một câu: "tôi bấm Lưu rồi, tắt điện — dữ liệu tôi còn không?" Mọi bảng mục 2 là bản dịch kỹ thuật của câu đó.

---

## 8. Đọc tiếp & bài tập

- SSD/PLP: **1.4** · WAL & transaction: **5.2** · io_uring gộp fsync: **2.5** · Filesystem lựa chọn: **14.5** (LKG lưu trữ)
- **Bài tập 1:** Chạy `pg_test_fsync` trên máy production (giờ thấp điểm). Ghi lại số — nếu > 1 ms, mọi tính toán TPS của bạn đang dùng giả định sai.
- **Bài tập 2:** Audit một đoạn code ghi config quan trọng: đủ 4 bước §2.5 chưa? Đặt tên file người phụ trách để sửa.
- **Bài tập 3:** Trong một ETL chạy tối: plot nr_dirty theo phút. Nếu sawtooth chạm trần dirty_ratio — hạ background ratio đi 5%, đo lại tổng thời gian chạy.
