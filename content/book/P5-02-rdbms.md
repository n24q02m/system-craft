# 5.2 — RDBMS: PostgreSQL & MySQL

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.1 (ruột engine) · 3.10 (pool là một trạm).

**Sợi chỉ đỏ:** *Engine là ruột — vận hành PostgreSQL cho đơn hàng có bài riêng gì?* — trả lời: PostgreSQL cho đơn hàng là mặc định khôn ngoan — chương này đi qua bảng giá thật của isolation level (mỗi mức đổi một bệnh), index bám theo hình câu hỏi chứ không phải "càng nhiều càng tốt", và pool tính bằng công thức chứ không phải "nâng cho hết lỗi". Câu hỏi để lại cho chương sau: *Không phải gì cũng quan hệ — menu và giỏ hàng đổi hình dạng hoài: document store khi nào đúng?*

**Thuật ngữ sẽ gặp:** *isolation level* — thoả hiệp giữa độ đúng đắn và độ đồng thời: READ COMMITTED tới SERIALIZABLE; *execution plan* — EXPLAIN cho thấy DB định chạy thế nào: đọc trước khi tối ưu; *index* — cấu trúc phụ theo hình câu hỏi: sai hình là quét bảng; *max_connections* — mỗi connection tốn RAM thật: nâng bừa là chuột rút; *bốn bệnh kinh điển* — query N+1, index bỏ sót, pool cạn, lock chờ nhau; *pg_stat_statements* — nơi mọi câu hỏi chậm có tên.

**Ví dụ mở đầu:** Báo cáo cuối tháng làm app đơn hàng của DM chậm: một query quét triệu dòng vì index không đúng hình câu hỏi. Cao điểm thì pool cạn — cách sửa nhanh là nâng max_connections, và RAM gục theo. Hai vụ đều có thuốc trong chương này, nhưng phải đo trước: EXPLAIN và pg_stat_statements là kính hiển vi.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Isolation level cho từng đường giao dịch | Read committed đủ không — hay tôi đang âm thầm chấp nhận phantom/skip? |
| 2 | Chiến lược index + EXPLAIN trong review | Index nào đáng tiền — và ai chịu trách nhiệm xoá index chết? |
| 3 | Connection pool (PgBouncer/Odin) + sizing | Công thức Little (→3.10) đã áp cho DB chưa — hay "nâng max_connections"? |
| 4 | PG hay MySQL cho hệ mới | Đội hình + extension + workload — chứ không phải "vốn quen" |

---

## 2. Cơ chế

### 2.1 Trạng thái phiên bản (verify 2026-10-30)

| Hệ | Phiên bản | Ghi chú |
|---|---|---|
| PostgreSQL | **19** — RC1 15/10/2026, **GA 19/11/2026** (V); 18.6 hiện hành | PG14 EOL 12/11/2026 — nâng cấp bắt buộc cho ai còn 14 |
| MySQL | 9.7.4 (innovation); 8.4.13 LTS; nhánh 26.10.0 mới | chọn LTS cho production |

PostgreSQL 19 nổi bật (từ Beta/RC): online checksums, MERGE/SPLIT PARTITIONS, 3 hàm pg_get_*_ddl, JIT tắt mặc định; MySQL 8.4/9.x: hash join trưởng thành, hơn nữa xem changelog chính thức. **Nguyên tắc sách:** phiên bản .0 không lên production — chờ .1+.

### 2.2 Isolation level — bảng giá thật

| Level | Ngăn được | Còn lọt | Dùng khi |
|---|---|---|---|
| READ COMMITTED (mặc định) | dirty read | non-repeatable, phantom | đa số web — đủ |
| REPEATABLE READ | non-repeatable | (PG: snapshot isolation; MySQL InnoDB: gần serializable qua gap lock) | báo cáo trong transaction |
| SERIALIZABLE | mọi anomaly (theo lý thuyết 2PL/SSI) | — | tiền/ton kho — đánh giá chi phí retry |

PostgreSQL dùng MVCC + SSI cho serializable (retry khi xung đột — cần code ứng xử); MySQL dùng gap lock (khóa khoảng — dễ deadlock hơn dưới tải cao). **Non-repeatable read/phantom trong OLTP thường vô hại; skip anomaly trong REPEATABLE READ (PG) có hại với "kiểm-tra-rồi-gán" — điểm cần SERIALIZABLE hoặc SELECT FOR UPDATE chủ động.**

### 2.3 Index: B-tree mặc định, còn lại theo hình câu hỏi

- **B-tree:** =, range, ORDER BY — mặc định đúng;
- **GIN:** chứa (JSONB, array, full-text) — index nhiều-key-per-row;
- **BRIN:** dữ liệu vật lý theo trục thời gian — cực nhỏ (→5.1 §2.5);
- **Partial + expression:** index "chỉ row lỗi chưa xử lý" (`WHERE status='error'`) — nhỏ, dùng đúng chỗ;
- **Covering (INCLUDE):** index thỏa cả SELECT — khỏi chạm table.

**EXPLAIN (ANALYZE, BUFFERS)** là cách duy nhất tranh luận index — rows ước lượng vs thật lệch lớn = statistics stale (autovacuum/analyze chưa chạy). Quy tắc review: PR có query mới phải kèm EXPLAIN.

### 2.4 Pool & max_connections — bẫy "nâng cho hết lỗi"

Connection PG là **process** (~MB mỗi cái — →3.9) + context switch (→2.3): 1.000 connection ≠ 1.000 throughput; quá core×2–4 là bắt đầu tụt. Công thức: `pool ≈ cores × 2–4 + spares` (nghiên cứu HikariCP baseline), còn **thực tế** dùng Little: throughput × latency (→3.10). PgBouncer (transaction mode) trung gian: hàng nghìn client → vài chục connection thật. MySQL thread nhẹ hơn nhưng max_connections cao vẫn giết bằng context switch + memory.

### 2.5 Bốn bệnh kinh điển và thuốc

1. **Long transaction:** giữ xmin → vacuum không dọn → bloat + index phình. Tìm: `pg_stat_activity WHERE xact_start < now()-5min`. Thuốc: statement_timeout, chia nhỏ;
2. **N+1 (từ ORM):** 1 request = 100 query (→4.5/3.10). Tìm: query log theo request_id;
3. **Connection storm:** app scale-out × pool/instance > max (→3.10). Thuốc: pgbouncer + giới hạn pool theo sức chứa DB;
4. **Deadlock:** thứ tự khóa không nhất quán. Thuốc: lock theo thứ tự key cố định; retry với jitter (→8.5).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Pool gốc | cores × 2–4 | I | HikariCP baseline |
| Connection chi phí (PG) | ~MB/process | I | |
| Autovacuum mặc định | 20% burst | V | tuning theo bảng nóng |
| PG 19 GA | 19/11/2026 | V | versions.csv |
| Hot standby lag | ms–s (async) | I | →8.1 |

---

## 4. Suy luận kiến trúc

- **S1:** RDBMS bán **nhất quán giao dịch** — nếu workload không cần ACID, trả giá bền vững cho thứ không dùng (→5.15 ma trận).
- **S2:** Tham số trụ: cache hit, long-running txn/s, pool wait, replication lag, bloat ratio.
- **S3:** SERIALIZABLE đổi throughput lấy đúng-đắn; replica đọc đổi nhất quán đọc (→8.1) lấy scale; pool transaction-mode đổi session semantics (SET/prepared) lấy concurrency — mỗi cái đều "đổi gì lấy gì" ghi rõ.
- **S4:** PG extension hệ sinh thái (PostGIS, pgvector, TimescaleDB) đang biến "một DB" thành "nền nhiều model" — ranh giới "cần DB khác" lùi xa hơn truyền thống.
- **S5:** AI/RAG kéo pgvector vào mặc định (→5.10/12.5) — "SQL + vector trong một transaction" là lợi thế cấu trúc của PG năm 2026.
- **S6:** Khi DB chậm: EXPLAIN trước, hardware sau; 90% là query/index/lock, không phải "DB yếu".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Replica lag tăng theo ghi | Single-thread áp dụng / network | lag metric; hot standby | §2.5 |
| Cảnh báo wraparound (PG) | Autovacuum không theo kịp | datfrozenxid age | §2.5 |
| Bảng phình dù ít row | Dead tuples + index bloat | pg_stat_user_tables | §2.5 |
| Chập chờn deadlock | Thứ tự khóa lộn xộn | log deadlock; audit code | §2.5 |
| "Too many connections" giờ cao điểm | App mở conn theo request | pgbouncer + pool app | §2.4 |
| Kết quả báo cáo "nhảy" | Isolation thấp cho báo cáo dài | snapshot/repeatable read | §2.2 |

---

## 6. Cách đo

```sql
-- Query đang chạy + tuổi transaction
SELECT pid, now()-xact_start AS xact_age, state, left(query,60)
FROM pg_stat_activity WHERE xact_start IS NOT NULL
ORDER BY xact_age DESC LIMIT 10;

-- Bảng bệnh nhất (bloat nghi ngờ)
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;

-- Index nào không ai dùng (ứng viên xoá)
SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes
WHERE idx_scan = 0 ORDER BY pg_relation_size(indexrelid) DESC LIMIT 10;

-- Câu query tốn thời gian nhất (pg_stat_statements)
SELECT calls, mean_exec_time, total_exec_time, left(query,60)
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
```

Nguyên tắc: **pg_stat_statements + pg_stat_activity là "JFR của PG"** — bật từ ngày một (chi phí thấp), vì bằng chứng phải tồn tại trước sự cố.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay scale-up:** read replica (→8.1), partitioning (declarative — đã dễ), hoặc Citus/sharding khi thật cần (thường muộn hơn tưởng). **Thay RDBMS:** chỉ khi model dữ liệu lệch hẳn (document — →5.3; wide-column write-hot — →5.5; OLAP — →5.8). **Thay tối ưu tay:** pgvector/pg_partman/materialized view — extension trước, migration sau.

Năm thấu kính:
- **Kinh tế:** Licence $0 nhưng ops đắt: DBA/vận hành là chi phí thật — tính TCO 3 năm kể cả người.
- **Vận hành:** Upgrade major PG mỗi năm (14 EOL 12/11/2026!) cần đường "logical replication/backup-restore" tập dượt — không phải việc phát sinh.
- **An ninh:** Row-Level Security cho multi-tenant (→5.14); least-privilege app user; audit log (pgAudit) cho compliance.
- **Lịch sử:** "NoSQL sẽ giết SQL" (2010) đảo ngược hoàn toàn 2015–2020 (Postgres thêm JSONB → document; pgvector → AI) — bài học: lớp truy vấn thắng bằng cách nuốt mô hình mới, không chống lại.
- **Người dùng:** Người dùng tin "tiền chuyển thì không mất, báo cáo thì khớp" — chương này là hợp đồng niềm tin được cài đặt bằng isolation level và WAL.

---

## 8. Đọc tiếp & bài tập

- Storage engine nền: **5.1** · Consistency/replica: **8.1** · Multi-tenant RLS: **5.14** · Ma trận chọn: **5.15** · Migration/backup: **11.2**
- **Bài tập 1:** Chạy query pg_stat_activity tuổi transaction (§6) ngay bây giờ. Transaction > 5 phút đang sống? Mỗi cái là một ràng buộc vô hình lên vacuum.
- **Bài tập 2:** Lấy top-10 query tốn thời gian (pg_stat_statements); EXPLAIN (ANALYZE, BUFFERS) từng cái. Ít nhất một Seq Scan bất ngờ — đó là tiền đang cháy.
- **Bài tập 3:** Đối chiếu max_connections × pool mỗi instance với công thức cores×2–4. Chênh lớn = một trong hai bên đang sai có hệ thống.
