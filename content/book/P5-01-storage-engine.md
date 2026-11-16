# 5.1 — Nền tảng Storage Engine: B-Tree, LSM, WAL, MVCC & Cấu trúc Xác suất

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** ds-16-foundation.md

---

## 0. Nhập môn

**Đọc trước:** 2.4 (page cache) · 1.4 (SSD/RAID).

**Sợi chỉ đỏ:** *API đông thì dữ liệu phình — B-tree và LSM, ruột của mọi DB, khác nhau thế nào?* — trả lời: hai ruột — B-tree tối ưu đọc (ghi tại chỗ, có thứ tự) và LSM-tree tối ưu ghi (ghi tuần tự, đọc phải lục qua nhiều tầng); mọi DB ở chương này về sau đều chọn một trong hai, kèm WAL để không mất dữ liệu và MVCC để đọc không chặn ghi. Câu hỏi để lại cho chương sau: *Engine là ruột — vận hành PostgreSQL cho đơn hàng có bài riêng gì?*

**Thuật ngữ sẽ gặp:** *B-tree* — cây có thứ tự: đọc O(log n), ghi đè tại chỗ trong trang; *LSM-tree* — ghi tuần tự memtable rồi flush thành tầng file, compaction gom dần; *WAL* — nhật ký viết trước: sự cố giữa chừng thì tua lại được; *MVCC* — mỗi transaction thấy ảnh dữ liệu tại thời điểm nó bắt đầu; *bloom filter* — "chắc chắn không có" với giá rẻ; *compaction* — gom dọn tầng file: I/O nền, thủ phạm p99 vọt.

**Ví dụ mở đầu:** Hệ thống đơn của DM ghi liên tục; hệ menu đọc lặp không ngừng. Engine ghi tuần tự (LSM) hợp máy trước, engine đọc nhanh (B-tree) hợp máy sau — và đêm compaction của một DB LSM làm p99 vọt là cái giá thật của "ghi tuần tự rẻ". Chương này là ruột: hiểu 5.1 thì mười lăm chương store phía sau chỉ là biến hình.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Workload đọc hay ghi chủ đạo → B-Tree hay LSM | Tỉ lệ read:write của tôi là bao nhiêu — và có "đọc những gì vừa ghi" nhiều không? |
| 2 | WAL + fsync policy (→2.4) | Tôi chấp nhận mất bao nhiêu transaction khi mất điện? |
| 3 | MVCC tuning (vacuum/compaction) cho engine tôi dùng | Dọn xác dead version có theo kịp tốc tạo không? |
| 4 | Cấu trúc phụ (bloom/skiplist/bitmap) ở đâu đáng tiền | Index phụ nào thật sự giảm I/O, cái nào chỉ tốn ghi? |

---

## 2. Cơ chế

### 2.1 B-Tree: cây đọc nhanh, ghi tại chỗ

Cây cân bằng cao ~3–4 cấp cho hàng tỷ key: 1 đọc = 3–4 page I/O (đỉnh nằm trong buffer pool). Ghi **tại chỗ** (in-place update + ghi page đầy đủ) → tốt cho read-after-write, điểm-toán túi: WAL + page. Nhược: ghi ngẫu nhiên (page đầy → split), write amplification theo page (ghi 1 byte cập nhật 8–16 KB page), mặc định của PostgreSQL/MySQL (InnoDB).

### 2.2 LSM-Tree: ghi tuần tự, đọc phải lục

Log-Structured Merge: ghi chỉ **append vào memtable + WAL**, rồi flush thành SST bất biến, nền nén từng cấp. Write throughput cao (sequential — →1.4/2.4), file bất biến thân thiện nén. Cái giá:
- **Read phải gộp nhiều level** (bloom filter cứu — xác suất cấu trúc);
- **Compaction** chạy nền: I/O burst, write stall khi tụt hậu (triệu chứng "ghi khựng định kỳ" — giống GC của storage);
- **Space amplification** (nhiều bản sao chờ gộp) — RSS/volume phình hơn data thật.

LSM trong: RocksDB (nền Kafka Streams, Cockroach, TiKV), LevelDB, Cassandra/Scylla, ClickHouse (biến thể columnar).

### 2.3 WAL: vì sao không có engine nào "ghi thẳng vào file dữ liệu"

Ghi dữ liệu thật rải rác nhiều page → crash giữa chừng hỏng cấu trúc. Nên: **ghi log tuần tự trước** (append-only, fsync — →2.4), rồi lười cập nhật page sau (checkpoint). Crash → replay WAL. Toàn bộ "bền vững" của DB = chuỗi: `commit → WAL append → fdatasync → OK trả client`. Chi phí fsync là trần TPS của OLTP (→1.4 PLP, →2.4).

### 2.4 MVCC: đọc không chặn ghi

Mỗi row mang version (xmin/xmax trong PG); reader thấy "snapshot" của thời điểm query — không lock người đọc. Cái giá: **bản chết phải được dọn** — PostgreSQL dùng vacuum (một quá trình dọn rác kinh điển — mục 5), MySQL/InnoDB rollback segment, LSM gộp trong compaction. Hiểu MVCC là điều kiện hiểu: "vì sao DB của tôi phình", "vì sao transaction dài độc hại" (giữ snapshot → đọng version → bloat).

### 2.5 Bộ cấu trúc xác suất và phụ

- **Bloom filter:** "chắc chắn không có / có thể có" — LSM dùng để bỏ qua SST không chứa key; sai số ~1% đổi lấy bớt 1 lần disk read;
- **Skiplist:** memtable của RocksDB (danh sách liên kết nhiều tầng — insert/update rẻ hơn cây cân bằng);
- **Bitmap index:** cột cardinality thấp (giới tính, trạng thái) — đọc nhanh, ghi đắt;
- **BRIN (PG):** block-range index cho dữ liệu vật lý xếp theo tự nhiên (thời gian) — cực nhỏ, cực rẻ, đúng khi correlation cao.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| B-Tree cao (tỷ key) | 3–4 page | I | |
| Page chuẩn | 4–16 KB | V | PG 8KB, InnoDB 16KB |
| LSM write amp | 5–30× (tuỳ level/compaction) | I | |
| Bloom sai số | ~1% cấu hình được | V | |
| WAL fsync chi phối TPS | đúng với OLTP | P | →2.4 |

---

## 4. Suy luận kiến trúc

- **S1:** Chọn họ engine = chọn **biên I/O profile** (đọc ngẫu nhiên vs ghi tuần tự + compaction nền) — workload lệch thì không tối ưu nào cứu được engine sai họ.
- **S2:** Tham số trụ: read/write amp, compaction lag (hoặc vacuum lag), cache hit ratio buffer pool.
- **S3:** Bloom đổi vài bit bộ nhớ lấy bớt disk read; BRIN đổi "chỉ đúng khi dữ liệu vật lý tuần tự" lấy index gần miễn phí — cấu trúc phụ là máy đục lỗ theo hình của workload.
- **S4:** SSD làm giá của đọc ngẫu nhiên giảm → lợi thế LSM (ghi tuần tự) mỏng đi trên NVMe; nhưng write-amp vẫn quyết định tuổi thọ SSD (→1.4) — bài toán chưa hết.
- **S5:** Mọi datastore của chương 5 đều là **sự phối trí của chính các mảnh này** (B+tree/LSM/WAL/MVCC + replication — →8.x) — học 5.1 một lần, đọc 5.2–5.11 nhanh gấp ba.
- **S6:** Khi datastore "chậm": hỏi read-amp hay write-amp, compaction/vacuum có theo kịp, buffer pool có đủ — trước khi đổ lỗi phần cứng.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Ghi khựng định kỳ (RocksDB/Kafka Streams) | Compaction stall | compaction stats; level score | §2.2 |
| DB phình dù row không tăng (PG) | Vacuum tụt hậu/bloat | pg_stat_user_tables n_dead_tup | §2.4 |
| Đọc latency cao sau ghi lớn | Cache bị ghi dọn đọc | cache hit ratio; cfstats | §2.2 |
| TPS thấp hơn benchmark 10× | fsync đĩa không PLP | pg_test_fsync (→2.4) | §2.3 |
| Index phụ làm ghi chậm hẳn | Quá nhiều index | audit index usage | §2.5 |

---

## 6. Cách đo

```bash
# PostgreSQL: bloat & vacuum
SELECT relname, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;

# RocksDB: compaction lag + stall
#   metrics: rocksdb-compaction-pending, actual-delayed-write-rate

# Buffer pool / cache hit (cận quyết định mua RAM)
#   PG: SELECT blks_hit::float/(blks_hit+blks_read) FROM pg_stat_database WHERE datname='prod';

# Đo write amp: bytes ghi xuống đĩa / bytes ghi logic (theo metric thiết bị + app)
```

Nguyên tắc: **mọi engine đều tự phơi ra "độ khỏe" của dọn rác và cache hit** — hai con số này dự báo 80% sự cố trước khi user than phiền.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay đổi engine (đắt):** thường chỉ đáng khi profile workload đổi căn bản (thêm analytics → columnar — →5.8; thêm graph query → →5.11). **Thay tối ưu:** thêm RAM cho buffer pool (thường rẻ nhất), nén (→5.9), tách read replica (→5.2). Bộ cấu trúc phụ (§2.5) là "tối ưu nội bộ" rẻ nhất trước khi đổi.

Năm thấu kính:
- **Kinh tế:** Write-amp 20× nghĩa là SSD chết nhanh gấp 20× — chi phí phần cứng ẩn của engine sai; tính DWPD (→1.4) theo write-amp thật.
- **Vận hành:** Compaction/vacuum là "GC của storage" — lên dashboard cùng GC pause của app (→3.1).
- **An ninh:** WAL chứa mọi dữ liệu gần nhất — mã hoá at-rest phải tính cả WAL không chỉ data file (→10.5).
- **Lịch sử:** B-tree (1970s) vs LSM (1996 paper, phổ biến 2010s nhờ RocksDB/LevelDB): vòng lặp "ghi nhanh" vs "đọc nhanh" 50 năm chưa có người thắng tuyệt đối — vì vật lý chưa đổi phe.
- **Người dùng:** Người dùng thấy "đơn vừa tạo đã thấy" (read-your-write) và "giờ cao điểm vẫn lưu được đơn" — hai trải nghiệm đó được bảo vệ bởi MVCC và LSM-qua-compaction của chương này.

---

## 8. Đọc tiếp & bài tập

- RDBMS thực chiến: **5.2** · Wide-column/LSM vận hành: **5.5** · Columnar: **5.8** · WAL & fsync: **2.4** · Replication/consistency: **8.1–8.2**
- **Bài tập 1:** Đo cache hit ratio của DB chính (§6). < 95%? Tính RAM cần thêm để đạt — thường là bản trình bày dễ nhất trong năm.
- **Bài tập 2:** Với bảng ghi nhiều nhất: đếm index trên bảng × kích thước. Mỗi index không dùng = tiền ghi + SSD bạn đốt vô ích.
- **Bài tập 3:** Nếu dùng engine LSM: tìm metric compaction pending; vẽ 7 ngày. Đỉnh trùng "ghi khựng"? Đó là causal, không phải trùng hợp.
