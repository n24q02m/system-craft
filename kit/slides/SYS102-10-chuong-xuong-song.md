# SYS102 — Bộ Slide 10 Chương Xương Sống (★) · Môn 2: Hệ thống Thực

> **Ấn bản:** SA-2028.1 · **Phạm vi:** 10 chương ★ của `SYS102` (`5.2, 5.7, 5.12, 5.14, 6.5, 8.2, 8.3, 9.1, 9.7, 10.3`) · **Khổ 16:9**

| Cụm | Chương ★ | Trọng tâm quyết định |
|---|---|---|
| `P5` Dữ liệu | `5.2, 5.7, 5.12, 5.14` | RDBMS/Index/Pool, Log vs Queue, Flink Watermark, Multi-tenant RLS |
| `P6` Client/Edge | `6.5` | CDN Cache-Control, Invalidate & Edge Compute |
| `P8–P10` Phân tán, Cloud, An ninh | `8.2, 8.3, 9.1, 9.7, 10.3` | Raft & Fencing, Outbox & Saga, K8s cgroups/PDB, Progressive Delivery, AuthN/AuthZ |

---

## [5.2] 1/6 — RDBMS: PostgreSQL & MySQL (§0–§1)

- **Đọc trước:** `5.1` (ruột B-Tree/WAL) · `3.10` (pool DB là một trạm phục vụ).
- **Bốn quyết định (`D-053`–`D-055`):**
  1. **Isolation level (`D-053`):** `Read Committed` mặc định đủ chưa hay cần `Snapshot` / `Serializable`?
  2. **Chiến lược index (`D-054`):** B-Tree mặc định; GIN/GiST/BRIN hay Covering `INCLUDE` theo hình câu hỏi.
  3. **Connection pool (`D-055`):** `cores × 2–4` (PostgreSQL process tốn MB + context switch).
  4. **Nâng cấp:** Read replica hay Partitioning trước khi nghĩ Sharding.

---

## [5.2] 2/6 — Cơ chế Lõi: EXPLAIN, Pool & Autovacuum (§2)

- **`EXPLAIN (ANALYZE, BUFFERS)`:** Công cụ duy nhất tranh luận index; chênh row ước lượng vs thật = stats stale.
- **Bốn bệnh kinh điển:** Long transaction giữ `xmin` (chặn vacuum gây bloat) · `N+1` query từ ORM · Connection storm (`replicas × pool > max_connections` → dùng `PgBouncer` transaction mode) · Deadlock do thứ tự khoá lộn xộn.

| Thông số | Giá trị bậc | Nhãn / Nguồn | Ghi chú |
|---|---:|---|---|
| Pool gốc hiệu dụng | `cores × 2–4` | `I` (HikariCP baseline) | Quá ngưỡng giảm throughput |
| Autovacuum scale factor | `20%` dead tuples | `V` (PostgreSQL docs) | Hạ xuống 2–5% với bảng nóng |
| Hot standby replica lag | `ms–s (async)` | `I` | Đọc ngay sau ghi cần đọc leader |

---

## [5.2] 3/6 — Con Số Phiên Bản & Lệnh Chẩn PG (§3, §6)

```sql
SELECT pid, now() - xact_start AS age, state, left(query, 60)
FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY age DESC LIMIT 10;

SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;
```

- **Quy tắc PR:** Mọi query mới đều kèm `EXPLAIN (ANALYZE, BUFFERS)`.
- **Bật sẵn từ ngày một:** `pg_stat_statements` + `pg_stat_activity` là JFR của cơ sở dữ liệu.

---

## [5.2] 4/6 — Hỏng Thế nào & Chẩn Đoán (§5)

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh / Bước chẩn |
|---|---|---|
| Cảnh báo TX wraparound (PG) | Long tx / autovacuum không kịp | Kiểm `datfrozenxid` age & `pg_stat_activity` |
| Bảng phình dù row ít | Dead tuples + index bloat | `pg_stat_user_tables` + `pg_repack` |
| Too many connections | App mở quá ngưỡng `cores × 2–4` | Đặt `PgBouncer` + giảm pool từng pod |
| Deadlock vã lai | Thứ tự khoá không nhất quán | Log deadlock + khoá theo thứ tự ID |

---

## [5.2] 5/6 — Năm Thấu Kính & Lựa Chọn Thay Thế (§7)

- **Kinh tế:** Licence `$0` nhưng vận hành/DBA + nâng cấp major PG hàng năm (EOL tracking trong `facts/versions.csv`) mới là chi phí thật.
- **Lịch sử:** Postgres hấp thụ `JSONB` (document) và `pgvector` (vector) trong cùng transaction — đẩy ngưỡng phải tách DB mới ra rất xa.
- **An ninh:** Row-Level Security (`5.14`), user app least-privilege, `pgAudit`.

---

## [5.2] 6/6 — Bài Tập & Lab Cụm P5 (`P15-03-L05`)

- **Thực hành chuẩn:** Chạy `pg_stat_statements` top-10 `total_exec_time` trên hệ gần nhất; tìm ít nhất 1 `Seq Scan` ẩn.
- **Kiểm chéo pool:** Đối chiếu `pod_count × pool_size` với `cores × 2–4` trên Primary.
- **Gắn Lab:** **`P15-03-L05`** — đo Query Plan trước và sau khi thiết kế đúng Index B-Tree / Composite.

---

## [5.7] 1/6 — Event Log, Stream & Queue: Kafka vs RabbitMQ vs NATS (§0–§1)

- **Đọc trước:** `4.7` (AsyncAPI / Schema Registry) · `4.8` (Idempotency).
- **Quyết định trung tâm (`D-062`):** Chọn **Queue** (xong là xoá: RabbitMQ/SQS) hay **Log** (lưu giữ & replay được theo offset: Kafka/KRaft, NATS JetStream)?
- **Sợi chỉ đỏ:** Log vs Queue là quyết định *ngữ nghĩa dữ liệu*, đổi giữa hai mô hình về sau là một cuộc di cư dữ liệu thật.

---

## [5.7] 2/6 — Cơ chế Lõi: Partition, KRaft & Rebalance (§2)

- **Kafka 4.x (`4.4.0`):** KRaft thay hoàn toàn ZooKeeper; thêm Share Groups + tiered storage S3.
- **Thứ tự chỉ có trong 1 partition:** Chọn partition key quyết định đồng thời độ song song và skew (`I-034`).
- **Ba cạm bẫy consumer:** Offset `at-least-once` (consumer bắt buộc idempotent) · Rebalance stop-the-world nếu xử lý vượt `max.poll.interval.ms` (`I-043`) · Thiếu **DLQ** khi gặp **poison message** (`I-042`).

---

## [5.7] 3/6 — Bảng Số & Lệnh Chẩn (§3, §6)

| Thông số | Giá trị bậc | Nguồn / Nhãn | Ý nghĩa vận hành |
|---|---:|---|---|
| Kafka / RabbitMQ | `4.4.0 / 4.4.0` | `V` (`versions.csv`) | KRaft chuẩn, Quorum queue thay mirror |
| Thứ tự đảm bảo | `Within-partition` | `V` (Kafka Design) | Không có global total order across partitions |
| DLQ bắt buộc | Design-time | `P` | Chặn crash-loop `I-042` |

```bash
kafka-consumer-groups --bootstrap-server :9092 --describe --group orders
```

---

## [5.7] 4/6 — Hỏng Thế nào & Chẩn Đoán (§5)

| Triệu chứng | Nguyên nhân | Cách chẩn |
|---|---|---|
| Lag tăng đều | Consumer throughput < producer | Đo lag trend theo từng partition |
| Group khựng định kỳ (`I-043`) | `session.timeout` / `poll` vượt ngưỡng | Kiểm `max.poll.records`, bật cooperative rebalance |
| Crash loop lặp (`I-042`) | Poison message chưa qua DLQ | Kiểm offset đứng im → đưa payload lỗi sang DLQ |
| 1 consumer quá tải (`I-034`) | Hot partition key (`null` / 1 tenant lớn) | Kiểm phân bố lag từng partition |

---

## [5.7] 5/6 — Thấu Kính Kiến Trúc & Thay Thế (§7)

- **Thay Kafka khi nhẹ ops:** NATS JetStream (nhẹ hạ tầng), SQS/Cloud Tasks (job queue managed), Postgres `SKIP LOCKED` (dưới ~500 msg/s ở tầng Startup — `P15-05`).
- **Dữ liệu AI/Lakehouse:** Event log đóng vai trò nguồn chân lý tái chạy pipeline RAG và bảng Iceberg (`5.9`).
- **GDPR / PII:** Hạn chế đưa PII thô vào topic immutable retention dài.

---

## [5.7] 6/6 — Bài Tập Chẩn Đoán Kafka & Event-Driven (§8)

1. Đo lag theo từng **partition**, không đọc mỗi tổng cluster (partition lệch `> 10×` báo hiệu hot key).
2. Thử bơm 1 JSON sai schema ở staging: consumer có sống sót và đẩy sang `-dlq` không?
3. Lập bảng *Partition Plan*: số partition, key, retention, tiered on/off, tên DLQ cho topic chính.

---

## [5.12] 1/6 — Stream Processing (Flink) & Batch Orchestration (§0–§1)

- **Đọc trước:** `5.7` (Log/Offset) · `5.9` (Iceberg Lakehouse).
- **Ba quyết định chính:**
  1. Chọn độ trễ thật: Micro-batch giây/phút hay True-stream millisecond (`Flink`)?
  2. Quy định **Watermark bound**: chấp nhận sự kiện đến trễ tối đa bao nhiêu phút trước khi đóng cửa sổ?
  3. Chiến lược **Backfill** & idempotency cho cả stream và batch DAG (Airflow/Dagster).

---

## [5.12] 2/6 — Event Time, Watermark & State Checkpointing (§2)

- **Event time vs Processing time:** Không bao giờ dùng đồng hồ server xử lý để tính cửa sổ kinh doanh khi client mất mạng (`I-048`, `6.1`).
- **Watermark (`t - bound`):** Sự kiện muộn hơn watermark vào `side output` thay vì làm hỏng số liệu đã đóng.
- **Checkpoint Flink (`30s–5min`):** Lưu RocksDB/aligned snapshot xuống object storage; state không đặt **TTL** sẽ phình tới khi sập OOM/checkpoint timeout.

---

## [5.12] 3/6 — Bảng Số & Hợp Đồng Vận Hành (§3, §6)

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---:|---|---|
| Checkpoint interval chuẩn | `30 s – 5 min` | `I` (Apache Flink Docs) | Cân bằng replay recovery vs I/O |
| Flink E2E latency | `ms – s` | `I` | Phụ thuộc checkpoint ở Exactly-Once sink |
| Backfill idempotency | Bắt buộc | `P` | Upsert/partition overwrite, không append mù |

---

## [5.12] 4/6 — Năm Ca Hỏng Điển Hình Của Pipeline Dữ liệu (§5)

| Triệu chứng | Nguyên nhân | Điểm đo |
|---|---|---|
| Job khựng định kỳ | Checkpoint size quá lớn | Theo dõi `checkpoint_duration` & alignment time |
| Số liệu báo "thiếu event" | Watermark đóng sớm | Đo `late_events_ratio` & `side_output` |
| State phình vô hạn | Quên đặt **State TTL** cho keyed state | Biểu đồ `state_size` theo thời gian |
| Backfill chạy lại bị nhân đôi | Sink không idempotent | Audit `MERGE` / partition atomic swap |

---

## [5.12] 5/6 — Thấu Kính & Pattern Streaming-to-Lakehouse (§7)

- **Hội tụ 2026:** Kafka → Flink / Kafka Connect → **Apache Iceberg (`5.9`)** hợp nhất stream + batch về một định dạng bảng mở, tránh kiến trúc Lambda phải viết logic hai lần.
- **Batch Orchestration:** Airflow/Dagster không phải data-mover — chỉ điều phối Spark/DuckDB/dbt; phải có SLA alert + idempotent partition backfill.

---

## [5.12] 6/6 — Bài Tập Thiết Kế Watermark & State TTL (§8)

1. Vẽ đường đi một sự kiện đi trễ `15 phút` từ app mobile mất sóng qua pipeline của bạn.
2. Kiểm tra tất cả toán tử stateful (`JOIN`, `dedup`, `session window`): mỗi cái đã có `State TTL` chưa?
3. Thiết kế 1 lệnh backfill lại dữ liệu `3 ngày trước` đảm bảo chạy `2 lần liên tiếp` ra cùng kết quả.

---

## [5.14] 1/6 — Kiến Trúc Đa Thuê Bao ở Tầng Dữ liệu (§0–§1)

- **Đọc trước:** `5.2` (Postgres) · `4.7` (event metadata theo `tenant_id`).
- **Quyết định `D-068` & `D-136`:** Chọn mô hình cho từng phân khúc khách hàng:
  - **Pool (Shared Schema + RLS):** 10k+ tenant nhỏ, chi phí/tenant thấp nhất.
  - **Bridge (Schema per tenant):** vài trăm–nghìn tenant vừa (cẩn thận catalog bloat).
  - **Silo (DB/Cluster riêng):** Enterprise cần compliance / chống noisy neighbor tuyệt đối.

---

## [5.14] 2/6 — Ba Tầng Cô Lập & Khung RLS Cứng (§2)

- **Pool + Postgres RLS:** Cài `CREATE POLICY` trên `app.tenant_id`, ép biến session trong cùng transaction pooler (`SET LOCAL app.tenant_id = ...`), và **tuyệt đối không để role app có quyền `BYPASSRLS` / table owner**.
- **Noisy neighbor:** Tenant lớn chạy query quét bảng làm nghẽn I/O & buffer pool cho hàng nghìn tenant nhỏ.
- **Escape hatch (`Silo`):** Thiết kế tenant abstraction từ ngày 1 để dời 1 tenant VIP sang cluster riêng trong giờ–ngày không viết lại app.

---

## [5.14] 3/6 — Bảng Số & Chẩn Rò Rỉ Chéo Tenant (§3, §6)

| Thông số | Giá trị bậc | Nguồn / Nhãn | Ghi chú |
|---|---:|---|---|
| Pool tenant hợp lệ | `10.000+` | `P` | Giới hạn theo query throughput / connection |
| Schema-per-tenant (Bridge) | Tối đa vài nghìn | `I` (PG System Catalogs) | Sau đó `pg_class`/`pg_attribute` phình, vacuum chậm |
| RLS overhead | `~vài %` | `I` | Rẻ nếu index bắt đầu bằng `(tenant_id, ...)` |

---

## [5.14] 4/6 — Hỏng Thế nào & Kiểm Thử Bắt Buộc Trong CI (§5)

| Triệu chứng | Nguyên nhân | Kiểm tra & Vá |
|---|---|---|
| Rò dữ liệu giữa Tenant A và B | Query chạy với role owner / quên `SET LOCAL` | Test tích hợp cross-tenant trên **mỗi PR migration** |
| Tenant nhỏ chậm khi tenant lớn chạy report | Chung Primary & buffer pool | Query timeout + đọc replica / move VIP sang Silo |
| Không tính được giá vốn từng tenant (`11.5`) | Thiếu metering query/storage theo `tenant_id` | Gắn metric `tenant_id` (lưu ý cardinality `11.2`) |

---

## [5.14] 5/6 — Thấu Kính Chi Phí & Pháp Lý (§7)

- **Kinh tế SaaS B2B (`13.7`):** Dùng Pool cho bậc Free/Pro (`80%` số lượng tenant), Bridge/Silo cho gói Enterprise trả tiền cao (tính vào giá hợp đồng).
- **Residency:** Tenant EU vs US có thể đòi Silo cứng đặt ở region chỉ định (`8.7`) — chỉ giải được nếu tầng routing biết ánh xạ `tenant_id → shard/cluster`.

---

## [5.14] 6/6 — Bài Tập Kiểm Tra RLS & Escape Hatch (§8)

1. Liệt kê mọi bảng mới thêm trong 6 tháng qua: có bảng nào thiếu cột `tenant_id` và CI test `tenant A đọc được record tenant B` không?
2. Đo độ phình index khi đưa `tenant_id` làm cột đầu của composite B-Tree index.
3. Viết runbook 5 bước chuyển 1 tenant nặng ra khỏi DB Pool sang Silo với downtime < 1 phút.

---

## [6.5] 1/6 — Edge Compute & Kiến Trúc CDN (§0–§1)

- **Đọc trước:** `5.4` (cache phía server) · `4.2` (HTTP header & semantics).
- **Quyết định `D-074`:** Đặt đường biên ở đâu — cache asset tĩnh, cache HTML có điều kiện (`stale-while-revalidate`), hay đưa logic định tuyến/auth nhẹ ra V8 Isolate / Edge Worker?
- **Sợi chỉ đỏ:** Tải từ PoP gần người dùng (`1–30 ms`) đánh bại việc tối ưu hàm DB thêm `5 ms` ở origin cách nửa vòng trái đất (`150 ms`).

---

## [6.5] 2/6 — `Cache-Control` & Ma Trận Vô Hiệu Hoá (§2)

- **Asset có hash tên file (`app.a1b2c3.js`):** `Cache-Control: public, max-age=31536000, immutable` (`RFC 8246`).
- **HTML / API động cá nhân hoá:** Tuyệt đối gắn `private, no-store` hoặc phân tách khoá cache chính xác (không để `Cookie` lọt qua CDN cache chung!).
- **Hai trường phái Invalidate:** Đợi TTL ngắn + `stale-while-revalidate` vs Purge chủ động theo Surrogate-Key / Cache-Tag (`s–phút` tuỳ nhà cung cấp).

---

## [6.5] 3/6 — Bảng Số & Lệnh Soi Header Chẩn Đoán (§3, §6)

| Thông số | Giá trị bậc | Nguồn / Nhãn | Ý nghĩa |
|---|---:|---|---|
| RTT tới PoP CDN gần | `~1–30 ms` | `I` | So với `100–300 ms` xuyên lục địa |
| Max-age asset hash | `31.536.000 s (1 năm)` | `P` (`RFC 9111` / `RFC 8246`) | Hit ratio mục tiêu `> 90%` |
| V8 Isolate cold start | `~ms` | `I` (Edge Isolate Specs) | Nhẹ hơn container 100× |

```bash
curl -sI example.com/assets/app.js | grep -iE 'cache-control|age|cf-cache-status|vary'
```

---

## [6.5] 4/6 — Hỏng Thế nào ở Tầng Biên (§5)

| Triệu chứng | Nguyên nhân | Lệnh kiểm / Sửa |
|---|---|---|
| Sửa xong vẫn hiện bản cũ | Thiếu content-hash trên filename / chưa purge | Bắt buộc content hash cho CSS/JS; purge HTML by tag |
| User A thấy trang cá nhân User B | Cache public trên response chứa `Set-Cookie`/PII | Đóng `Cache-Control: private` mặc định cho route auth |
| Origin nổ đúng lúc key hot hết hạn | Cache stampede từ hàng nghìn PoP | Bật request collapsing / `stale-while-revalidate` |
| Hit ratio `< 50%` | Query string rác (`utm_*`) / `Vary: User-Agent` | Chuẩn hoá cache key (drop tracking params) |

---

## [6.5] 5/6 — Cái Gì Nên & Không Nên Chạy Ở Edge (§7)

- **Đáng ra Edge:** Terminate TLS/QUIC, kiểm tra chữ ký JWT access (`10.3`), A/B routing, bot/WAF/rate-limit chặn storm trước khi tới origin (`8.5`), geo-redirect.
- **Tránh đẩy ra Edge:** Logic cần đọc/ghi lặp **5+ lần** về 1 DB tập trung (mỗi hop Edge ↔ Origin lại trả `RTT × 5`, chậm hơn giữ app nằm sát DB!).

---

## [6.5] 6/6 — Bài Tập Soi Header & Chống Stampede (§8)

1. Chạy `curl -sI` vào 3 URL quan trọng (static JS, landing page, API `/me`): xác minh chính xác `Cache-Control` và `Vary`.
2. Kiểm tra tỷ lệ cache hit hiện tại — nếu `< 90%` với asset tĩnh, tìm đúng query parameter hoặc header đang làm nổ cache key.

---

## [8.2] 1/6 — Đồng Thuận (Raft), Leases & Fencing Tokens (§0–§1)

- **Đọc trước:** `8.1` (Định lý CAP, FLP, Clock Skew) · `5.7` (KRaft).
- **Hai quyết định `D-084`–`D-085`:**
  1. Có **thực sự cần đồng thuận** (leader election, metadata cấu hình, Distributed Lock chuẩn) hay không?
  2. Dùng Distributed Lock để *tối ưu hiệu năng* (chống tính lặp vô hại) hay để *bảo vệ đúng đắn* (bắt buộc kèm **Fencing Token**)?

---

## [8.2] 2/6 — Raft Quorum, Lease & Bẫy GC Pause (§2)

- **Quorum (`Ongaro & Ousterhout, 2014`):** `floor(N/2) + 1` → cụm `N=3` chịu mất `1` node; `N=5` chịu mất `2` node (`N=2` hay `N=4` không tăng khả năng chịu lỗi so với lẻ kế dưới!).
- **Lease hết hạn khi GC Pause (`I-055`):** Client A giữ lock, bị Stop-the-World GC `35s`, lock hết hạn → Client B lấy lock ghi vào storage → Client A tỉnh dậy tưởng mình vẫn giữ lock rồi ghi đè dữ liệu của B!
- **Thuốc duy nhất (`Fencing Token`):** Lock service cấp số đơn điệu tăng dần (`token = 33, 34...`); tầng **storage từ chối mọi ghi có `token < max_seen_token`**.

---

## [8.2] 3/6 — Bảng Số Đồng Thuận & Raft Timing (§3)

| Thông số | Giá trị bậc | Nguồn chính | Ghi chú |
|---|---:|---|---|
| Raft Quorum | `floor(N/2) + 1` | Ongaro & Ousterhout (ATC 2014) | 3 chịu 1; 5 chịu 2 |
| Election Timeout | `~10× RTT` chéo node | Raft §5.6 Timing Requirement | Quá nhỏ → flapping `I-054` |
| etcd write ceiling | `~vài nghìn ops/s` | etcd benchmarks | Chỉ giữ metadata, **không** dùng làm DB nghiệp vụ |

---

## [8.2] 4/6 — Hỏng Thế nào ở Raft & Distributed Lock (§5)

| Triệu chứng | Nguyên nhân | Cách kiểm & Vá |
|---|---|---|
| Leader bầu liên tục (`I-054`) | Mạng/disk `fsync` WAL chậm > election timeout | Đo ping chéo node + tách đĩa NVMe riêng cho etcd/Raft |
| Split-brain / Dữ liệu bị ghi đè "bởi ma" (`I-053`, `I-055`) | Thiếu fencing token ở storage | Storage check version/token đơn điệu (hoặc DB conditional `WHERE version = ...`) |
| Cụm đóng băng toàn bộ không ghi | Mất đa số quorum (mất ≥ 2/3 node) | Chạy ít nhất 3 node trải 3 AZ; kiểm tra backup snapshot |

---

## [8.2] 5/6 — Thấu Kính Vận Hành & Gắn Lab L8 (§7–§8)

- **Khi nào KHÔNG cần đồng thuận:** Counter xấp xỉ, cache vô hại, crdt local-first (`6.3`) — trả giá latency quorum xuyên vùng cho thứ chấp nhận eventual consistency là lãng phí (`P15-05`).
- **Gắn Lab (`P15-03-L08`):** Dựng cụm 3-node quorum thật, giết Leader → đo thời gian failover; giết 2/3 node → quan sát cụm từ chối ghi bảo toàn tính đúng đắn.

---

## [8.2] 6/6 — Bài Tập Tự Kiểm Quorum & Fencing (§8)

1. Xem lại mọi chỗ đang dùng `SET NX EX` (Redis lock) trong codebase: nếu lock dùng để bảo vệ **tính đúng đắn tài chính/tồn kho**, kiểm tra xem tầng DB có kiểm phiên bản đơn điệu (`fencing token` / optimistic lock `version = version + 1`) hay không.
2. Kiểm tra triển khai `etcd` / `Kafka KRaft` hiện tại có đặt disk WAL trên ổ chia sẻ với container ồn ào không.

---

## [8.3] 1/6 — Giao Dịch Phân Tán, Saga, Outbox & "Exactly-Once" (§0–§1)

- **Đọc trước:** `5.15` (Dual-write bug) · `5.7` (At-least-once consumer).
- **Quyết định `D-086`:** Cần sự cố đồng bộ trên nhiều dịch vụ — chọn **2PC/XA** (hiếm dùng ở microservice vì chặn lock khi coordinator chết), **Transactional Outbox**, hay **Saga (Choreography/Orchestration)**?
- **Sự thật về "Exactly-Once":** Trên mạng A3 (gói mất/trùng), "Exactly-once delivery" là bất khả thi — cái chúng ta xây là **At-least-once delivery + Idempotent processing (Effectively-once)**.

---

## [8.3] 2/6 — Transactional Outbox & Khung Saga (§2)

- **Dual-write bug (`I-045`):** `db.commit()` xong rồi `kafka.publish()` bị rớt mạng → đơn hàng có trong DB nhưng dịch vụ giao hàng/email không bao giờ hay!
- **Transactional Outbox:** Ghi **nghiệp vụ + bảng `outbox_events` trong CÙNG 1 local DB ACID transaction**, sau đó Relay (CDC Debezium hoặc Poller) đẩy ra broker có idempotency key.
- **Saga:** Chia transaction dài thành chuỗi `T1 → T2 → T3`; nếu `T3` thất bại, chạy ngược **bù trừ `C2 → C1`** (lưu ý: thao tác bù trừ cũng phải idempotent & retryable!).

---

## [8.3] 3/6 — Bảng Số & So Sánh 3 Mô Hình (§3)

| Tiêu chí | 2PC / XA | Outbox + Idempotent | Saga (2–6 bước) |
|---|---|---|---|
| Phạm vi | Cùng cluster / legacy XA | DB → Broker + Service downstream | Nhiều service & API ngoài |
| Latency / Lock | Giữ lock lâu xuyên mạng | Sub-s (CDC) / s (poller) | Async, trạng thái `PENDING` |
| Failure mode chính | Coordinator treo lock | Outbox phình nếu không dọn | Quên hành động bù trừ `C_i` |

---

## [8.3] 4/6 — Hỏng Thế nào ở Outbox & Saga (§5)

| Triệu chứng | Nguyên nhân | Giải pháp |
|---|---|---|
| Đơn có ở DB, event mất tích (`I-045`) | Dual-write ngoài transaction | Đóng hết vào Transactional Outbox |
| Kafka replay làm cộng tiền 2 lần | Consumer thiếu bảng `processed_events` / deduplication | Lưu `event_id` UNIQUE trong cùng transaction nghiệp vụ |
| Saga kẹt vĩnh viễn ở giữa | Thiếu timeout / DLQ cho compensation `C_i` | Gắn saga state machine + cảnh báo timeout `PENDING` |

---

## [8.3] 5/6 — Năm Thấu Kính Thiết Kế (§7)

- **Semantic lock:** Hiển thị trạng thái `PENDING` cho người dùng trong lúc Saga đang chạy, đừng giả vờ đã hoàn tất rồi rút lại bất ngờ (`13.1`).
- **Quy mô:** Nếu thấy Saga vượt **> 6 bước**, thường là boundary microservice bị cắt vụn sai chỗ (`8.6`, `P15-05`) — gộp lại thay vì cố điều phối 12 dịch vụ.

---

## [8.3] 6/6 — Bài Tập Đọc Outbox & Bù Trừ (§8)

1. Tìm 1 chỗ codebase đang gọi broker/webhook ngay sau `commit()`: thiết kế bảng `outbox_events` + cột `idempotency_key` thay thế.
2. Viết ra cặp `(Hành động T_i, Bù trừ C_i)` cho luồng Đặt hàng → Khoá tồn kho → Trừ tiền → Tạo vận đơn.

---

## [9.1] 1/6 — Kubernetes Internals (`v1.35–1.37`) (§0–§1)

- **Đọc trước:** `8.2` (`etcd` = não của Control Plane) · `2.3` (`cgroups v2` & CFS throttling).
- **Hai quyết định `D-096`–`D-097`:**
  1. Đặt **`requests` vs `limits`**: CPU limit thấp sinh CFS throttling (`I-002`) — có nên bỏ CPU limit cho service latency-sensitive?
  2. Cấu hình **Probes (`startup`/`readiness`/`liveness`), PDB & Topology Spread** để drain node không rớt request (`I-058`, `I-062`).

---

## [9.1] 2/6 — Control Plane, Pod Lifecycle & Bẫy CFS (§2)

- **Bốn cơ quan Control Plane:** `kube-apiserver` (cửa duy nhất vào `etcd`), `etcd` (Raft state), `kube-scheduler` (chọn node theo `requests`), `controller-manager` (vòng lặp điều chỉnh actual → desired).
- **Bốn con ngựa Pod:** `InitContainer` → `startupProbe` (che chắn app khởi động chậm) → `readinessProbe` (rút IP khỏi EndpointSlice/Service khi bận) → `livenessProbe` (kill pod khi deadlock thật — không trỏ liveness vào DB ngoài!).
- **Graceful Shutdown chuẩn:** `preStop: sleep 5` để kube-proxy/ALB kịp rút IP trước khi process dừng lắng nghe, đặt `terminationGracePeriodSeconds` đủ lớn.

---

## [9.1] 3/6 — Bảng Số & Kiểm Tra Trong Cụm (§3, §6)

| Thông số | Giá trị bậc | Nguồn | Ghi chú |
|---|---:|---|---|
| K8s phiên bản mới | `1.37` (`1.37.2`) | `versions.csv` | Theo dõi API deprecation mỗi minor |
| CFS quota period mặc định | `100 ms` | Linux `cgroup-v2` | Quá quota 100ms bị ngưng chạy dù node rảnh (`I-002`) |
| `terminationGracePeriodSeconds` | `30 s` mặc định | Kubernetes PodSpec | Batch / LLM decode dài cần 300s+ |
| PDB an toàn | `>= 3` replicas, `maxUnavailable: 1` | Kubernetes Docs | `minAvailable: 100%` làm kẹt drain node (`I-058`) |

---

## [9.1] 4/6 — Năm Ca Lỗi Kinh Điển trên Kubernetes (§5)

| Triệu chứng | Nguyên nhân | Lệnh kiểm tra |
|---|---|---|
| Pod Pending mãi (`I-057`) | Thiếu node `requests`, taint/affinity, PVC | `kubectl describe pod <p>` (đọc Events) |
| p99 nhảy gấp 3, CPU node chỉ 55% (`I-002`) | CFS throttling do `limits.cpu` quá chật | Metric `cpu_cfs_throttled_periods` & `/sys/fs/cgroup/cpu.stat` |
| Drain node bị kẹt (`I-058`) | PDB chặn không cho evict | `kubectl get pdb -A` |
| Restart loop lúc vừa deploy | `livenessProbe` đánh sớm hơn app warmup | Thêm `startupProbe`, tách DB khỏi liveness |
| Sập 1 AZ là chết service (`I-062`) | Tất cả pod dồn cùng 1 zone | `topologySpreadConstraints` theo zone |

---

## [9.1] 5/6 — Thấu Kính Khi nào KHÔNG Dùng Kubernetes (§7)

- **Khi nào SAI (`P15-05`):** Đội `< 10` kỹ sư chạy `3` backend gọn gàng — YAML RBAC/Ingress/Cilium/CNI ngốn thời gian đáng lẽ dùng cho sản phẩm; hãy xem PaaS/systemd VM trước khi lên K8s.
- **Tích hợp AI/GPU (`9.2`, `12.2`):** Scheduler K8s kết hợp Karpenter / Kueue tối ưu bin-packing và GPU MIG/time-slicing ở quy mô `Scale-up`/`Enterprise`.

---

## [9.1] 6/6 — Thực hành Lab Cụm P9 (`P15-03-L09`) (§8)

1. Soát lại YAML của 1 service production: so `requests.cpu` vs usage P95, kiểm tra `limits.cpu` đang gây throttle hay không, và thử test rollback/drain `1 node` xem có dính `502` hoặc kẹt PDB không.
2. **Gắn Lab:** **`P15-03-L09`** — deploy trên cụm `kind` cục bộ, scale, giết Pod quan sát vòng tự chữa & Readiness rút endpoint.

---

## [9.7] 1/6 — Build Systems & Progressive Delivery (§0–§1)

- **Đọc trước:** `8.8` (Feature flag, Expand-Contract) · `7.6` (Tháp test & RUM).
- **Hai quyết định `D-104`–`D-105`:**
  1. **Chiến lược build (`D-104`):** Monorepo hermetic build + remote cache hay multi-repo? **Nguyên tắc:** Build 1 artifact bất biến một lần, promote `dev → staging → prod` bằng immutable digest (không build lại mỗi môi trường!).
  2. **Progressive delivery (`D-105`):** Canary theo bậc + **auto-rollback** nối trực tiếp vào metric SLO (`11.1`).

---

## [9.7] 2/6 — Trunk-Based, Canary & Bốn Chỉ Số DORA (§2)

- **Trunk-based + Feature Flag:** Tách bạch **Deployment** (đưa binary mới lên cụm) khỏi **Release** (bật flag cho 1% → 5% → 25% → 100% người dùng thật).
- **Schema an toàn:** Dùng mẫu `Expand-Contract` (`8.8`) mọi migration DB tương thích ngược ít nhất 1 release cũ để auto-rollback không bao giờ gãy code cũ.
- **DORA Metrics (`Accelerate`):** Tốc độ (**Deploy Frequency**, **Lead Time for Changes**) phải đi cùng ổn định (**Change Failure Rate**, **MTTR**) — ship nhanh mà CFR 40% là phá hoại!

---

## [9.7] 3/6 — Bảng Số & Hợp Đồng CI/CD (§3, §6)

| Thông số | Mục tiêu khuyến nghị | Nguồn / Nhãn | Ý nghĩa |
|---|---:|---|---|
| CI pipeline p95 | `< 10–15 phút` | `P` | Quá 30p khuyến khích PR khổng lồ |
| Remote build cache hit | `> 80–90%` | `P` | Bazel / Turborepo / BuildKit cache |
| Canary progression | `1% → 5% → 25% → 100%` | `P` | Cửa sổ eval `1–5 phút` auto-rollback |
| 4 chỉ số DORA | `DF · LT · CFR · MTTR` | DORA Research | Đo đồng bộ tốc độ + độ bền |

---

## [9.7] 4/6 — Hỏng Thế nào Trong Chuỗi Giao Hàng (§5)

| Triệu chứng | Nguyên nhân | Hành động vá |
|---|---|---|
| CI 45 phút, PR chồng đống | Chạy tuần tự mọi test / không cache | Tách unit nhanh & E2E chậm + remote cache |
| Staging xanh, Prod nổ | Rebuild lại artifact từng môi trường | Promote cùng SHA256 image digest + SBOM (`10.5`) |
| Sợ rollback vì schema DB đã đổi | Migration xoá/đổi tên cột in-place | Bắt buộc **Expand → Backfill → Switch → Contract** |
| Lỗi ảnh hưởng 100% khách | Big-bang rollout | Canary 1%–5% + Argo Rollouts / Flagger auto-abort |

---

## [9.7] 5/6 — An Ninh Chuỗi Cung Ứng Build (§7, nối `10.5`)

- **SLSA & Provenance:** Build trong runner cô lập, ký artifact bằng **Sigstore/Cosign**, xuất **SBOM** (`CycloneDX`/`SPDX`) và kiểm chứng digest trước khi Admission Controller của K8s cho phép Pod chạy (`10.5`).

---

## [9.7] 6/6 — Bài Tập Tối Ưu Đường Phát Hành (§8)

1. Đo `Lead Time` từ lúc PR mở tới lúc chạy Prod 1 tuần gần nhất và điểm nghẽn lớn nhất.
2. Viết kịch bản auto-rollback dựa trên ngưỡng `5xx burn rate` trong cửa sổ canary `3 phút`.

---

## [10.3] 1/6 — AuthN & AuthZ: OAuth 2.1, Passkeys, RBAC/ABAC/ReBAC (§0–§1)

- **Đọc trước:** `6.7` (Nơi giữ token phía client) · `5.14` (Tenant & phân quyền dữ liệu).
- **Ba quyết định `D-108`–`D-110`:**
  1. **AuthN (`D-108`):** OAuth 2.1 (bắt buộc **PKCE**) + Passkeys/WebAuthn (chống phishing tận gốc).
  2. **Session vs JWT (`D-109`):** Khi người dùng bị khoá/nghỉ việc, cần thu hồi phiên tối đa trong bao lâu? (**MTTR thu hồi `< 5 phút`**).
  3. **AuthZ (`D-110`):** RBAC (theo vai), ABAC (theo thuộc tính), hay ReBAC/Zanzibar (quan hệ trên từng tài liệu/folder)?

---

## [10.3] 2/6 — Session vs JWT & Ba Thế Giới Phân Quyền (§2)

- **Bẫy JWT thuần (`I-064`):** JWT stateless không thể huỷ trước lúc hết hạn trừ phi ngắn (5–15 phút) + **refresh token giữ stateful** hoặc kiểm tra `jti` denylist trong Valkey (`5.4`).
- **Chọn AuthZ:** RBAC sạch cho tổ chức vừa; **ReBAC (SpiceDB/OpenFGA)** khi câu hỏi là *"Alice có phải chủ sở hữu hay được share quyền `editor` trên Folder X không?"*
- **An ninh tận gốc (`BOLA/IDOR`):** Mọi endpoint truy cập tài nguyên phải áp **AuthZ ở tầng query dữ liệu** (`WHERE id = $1 AND tenant_id = $2`), không tin ID từ client.

---

## [10.3] 3/6 — Bảng Số & Hợp Đồng Danh Tính (§3)

| Chuẩn / Thông số | Giá trị / Chuẩn | Nguồn chính | Ghi chú |
|---|---|---|---|
| OAuth 2.1 | PKCE (`S256`) bắt buộc | IETF OAuth 2.1 + RFC 7636 | Bỏ Implicit & ROPC grant cũ |
| Passkeys | WebAuthn Level 2/3 | FIDO2 / W3C | Khoá công khai gắn domain → miễn nhiễm phishing |
| SCIM 2.0 | `RFC 7644` | IETF RFC 7643/7644 | Tự động thu hồi tài khoản khi offboard HR |
| Access Token TTL | `Phút – giờ` (`MTTR < 5m`) | `P` | Kết hợp short access + reference refresh |

---

## [10.3] 4/6 — Hỏng Thế nào ở AuthN & AuthZ (§5)

| Triệu chứng | Nguyên nhân | Cách vá & Kiểm chứng |
|---|---|---|
| Token lộ không khoá được (`I-064`) | JWT sống 7–30 ngày không server state | Rút access TTL còn `5–15 phút` + refresh revocation |
| Đọc lén đơn hàng người khác | Lỗi **BOLA/IDOR** (thiếu object-level auth) | Audit & viết test sở hữu trên mọi API `/:id` |
| Nhân viên nghỉ vẫn login được | Không đồng bộ **SCIM** offboarding | Nối SSO + SCIM webhook tắt session ngay |
| Người dùng bị lừa mất OTP/mật khẩu | Dùng SMS OTP/mật khẩu thuần | Lên **Passkeys** / hardware FIDO2 |

---

## [10.3] 5/6 — Vành Đai AI & Multi-Tenant (§7)

- **ACL cho Agent & RAG (`12.4`, `12.5`):** Token OAuth 2.1 đại diện người dùng phải chảy xuyên qua **MCP / AI Gateway** tới tận filter retriever của Vector DB (`I-068`); Agent tuyệt đối không dùng "service account siêu quyền" trả lời cho mọi nhân viên!

---

## [10.3] 6/6 — Bài Tập & Kiểm Chứng Quyền (`P15-03-L10`) (§8)

1. Kiểm tra access token TTL và cơ chế thu hồi tức thì nếu 1 laptop bị đánh cắp ngay bây giờ.
2. Viết `1` test tự động gửi token của `User A` gọi `GET/PATCH /orders/<order_B>` và khẳng định trả `403/404`.
3. **Gắn Lab:** **`P15-03-L10`** — đo và vá lỗi lộ timing / auth boundary.
