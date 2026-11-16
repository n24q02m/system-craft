# 5.8 — OLAP & Columnar: ClickHouse & DuckDB

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** ds-23-olap-vector-object.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 5.2 (OLTP làm đối chứng).

**Sợi chỉ đỏ:** *Chủ chuỗi muốn báo cáo tháng — OLAP khác gì DB giao dịch, nhanh hơn ở đâu?* — trả lời: OLAP lưu theo cột nên aggregation chỉ đụng đúng cột cần — nhanh hơn hàng chục lần; OLTP giữ hàng cho transaction. ClickHouse với MergeTree là trục; insert phải gộp mẻ; DuckDB 2.0 cho analytics nhúng đúng một file. Câu hỏi để lại cho chương sau: *Dữ liệu nhiều năm nhiều nguồn — object storage và lakehouse tổ chức ra sao?*

**Thuật ngữ sẽ gặp:** *columnar* — lưu theo cột: "doanh thu theo thành phố" chỉ đọc cột tiền và cột thành phố; *OLTP vs OLAP* — giao dịch từng dòng vs phân tích cả bảng: hai workload, hai loại máy; *MergeTree* — họ engine của ClickHouse: LSM tinh thần cho analytics; *batch insert* — nhỏ giọt là tự sát: gộp mẻ là luật; *DuckDB 2.0* — OLAP nhúng một file như SQLite của analytics (LTS 21/10/2026, verify trong chương); *late data* — dữ liệu đến trễ phải có đường hợp nhất lại.

**Ví dụ mở đầu:** Chủ chuỗi muốn "doanh thu theo thành phố, theo tuần, trừ hoàn": chạy trên DB giao dịch là quét cả bảng đơn — chậm và phá cache của khách đang đặt hàng. Bản sao ClickHouse trả cùng câu hỏi trong tích tắc. Hai workload hai kho: chương này vẽ đường ranh và luật vận hành từng bên.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | OLAP workload tách khỏi OLTP chưa — và chọn columnar nào | Query aggregation của tôi chạy trên đúng engine chưa? |
| 2 | MergeTree/partition/order key thiết kế | Query của tôi lọc theo gì — key có đi đúng trục đó không? |
| 3 | Nhánh ClickHouse (LTS vs monthly) & DuckDB vai trò (embed/notebook) | Ai cần server, ai cần in-process? |
| 4 | Insert pattern (batch ≥ 1k rows) | Tôi có đang giết server bằng insert nhỏ liên tục không? |

---

## 2. Cơ chế

### 2.1 Columnar: vì sao aggregation nhanh 10–100×

Hàng lưu theo **cột** không theo dòng: (a) chỉ đọc cột query chạm (20 cột dùng 3 = đọc ~15%); (b) cùng kiểu dữ liệu liền nhau → **nén tuyệt hảo** (10× phổ biến (I)); (c) vector hoá + SIMD (→1.2). Đổi lấy: **đọc cả row đắt** (phải ghép cột) — columnar tệ cho `SELECT *`, OLTP point-query. Vì thế: **OLTP hành cột trong DB giao dịch, OLAP phân tích trong columnar** — tách hai thế giới (hoặc HTAP hybrid — →5.15).

### 2.2 ClickHouse: MergeTree là bàn thờ

```
CREATE TABLE events (
  ts DateTime, tenant_id UInt32, ...
) ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, ts)
TTL ts + INTERVAL 90 DAY
```

- **ORDER BY** = clustered index vật lý: query `WHERE tenant_id=? AND ts BETWEEN` chỉ đọc "vùng" liên quan — **đây là quyết định hiệu năng số một** (lưu ý: khác index DB thường, đây là bố cục vật lý);
- **PARTITION** cho lifecycle (drop partition nguyên khối) — đừng partition quá mảnh (mỗi part có overhead — "too many parts" là bệnh kinh điển: mục 5);
- **TTL** tự xoá theo thời gian;
- **Materialized view** tính sẵn aggregate — "index cho queryAnalytics".

### 2.3 Insert pattern: batch là luật

ClickHouse tối ưu cho **insert theo block lớn**: < 1k rows/insert hoặc insert liên tục từng dòng → too many parts → background merge không kịp → reject/chậm. Chuẩn: buffer app ≥ 1.000–10.000 rows hoặc ~1 s gì đó flush; async_insert (server gom giúp) cho client nhỏ. Dữ liệu đến từ Kafka → ClickHouse qua engine Kafka/materialized view hoặc công cụ ETL (→5.12).

### 2.4 DuckDB 2.0 (verify: LTS "Cinnamon Teal" 21/10/2026)

In-process columnar (giống SQLite của analytics — →5.3): nhúng trong app/notebook; 2.0: **server mode ("Quack")**, async I/O, VARIANT, mutating CTE, agent-mode query (−59% output trên benchmark agent TPC-H của họ (V)); đóng gói trong dbt v2 (V). Vai trò 2026: **analytics cục bộ + file parquet trực tiếp** (query S3/parquet không cần cluster) — "một query, không ops". Hạn chế: một process chính (write), không thay cluster phân tán.

### 2.5 Trạng thái ClickHouse (verify 10/2026)

26.10.2.103 (nhánh monthly mới 24/10); **26.8 LTS** (EOL 08/2027) — production nên đứng nhánh LTS. Điểm nổi bật thế hệ gần: shared-mergeTree/S3 disk trưởng thành (tách compute/storage), lightweight delete cải thiện, vector index (→5.10).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| ClickHouse | 26.10 monthly / 26.8 LTS | V | versions.csv |
| DuckDB | 2.0.0 LTS (21/10/2026) | V | |
| Nén columnar | ~10× phổ biến | I | |
| Insert batch chuẩn | ≥ 1k rows / block | V | |
| Aggregation vs OLTP engine | 10–100× | I | đúng query |

---

## 4. Suy luận kiến trúc

- **S1:** Columnar đổi **đọc nhanh có chọn lọc** lấy viết/đọc-row chậm — workload quyết định, không phải marketing.
- **S2:** Tham số trụ: query p99 theo bảng, parts count, merge backlog, nén ratio, insert block size.
- **S3:** ORDER BY đổi bố cục lấy tốc độ truy vấn (chọn theo query thật); partition đổi lifecycle lấy chi phí; MV đổi lưu trữ lấy latency dashboard.
- **S4:** DuckDB + parquet + S3 tạo lớp "OLAP không cluster" — lượng lớn analytics nội bộ rơi về mô hình này (tốt hơn nuôi cluster CH cho 5 người dùng BI).
- **S5:** Log + trace + metric (→11.1) là workload columnar thuần — ClickHouse là backend quan sát phổ biến nhất 2026 (ngay cả các nền tảng obser bán hàng đều dùng nó bên dưới).
- **S6:** Khi query CH chậm: đọc bao nhiêu cột/rows (EXPLAIN) — ORDER BY sai trục hoặc SELECT * là 90% nguyên nhân.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| "Too many parts" | Insert nhỏ liên tục | system.parts; batch | §2.3 |
| Query chậm dù có "index" | ORDER BY lệch trục query | EXPLAIN reads | §2.2 |
| Đĩa đầy | TTL/partition chưa gọt | system.parts size | §2.2 |
| Dashboard lag sau spike ghi | Merge backlog | merges metric | §2.3 |
| SELECT * chậm | Columnar bản chất | đổi query/đưa về row engine | §2.1 |
| Notebook analyst chậm server chung | Tranh tài nguyên | tách hoặc DuckDB cục bộ | §2.4 |

---

## 6. Cách đo

```sql
-- ClickHouse: đọc thật của query (cột, phần, bytes)
EXPLAIN indexes = 1 SELECT ... ;

-- Bệnh parts theo bảng
SELECT table, count() FROM system.parts WHERE active GROUP BY table ORDER BY 2 DESC LIMIT 10;

-- Query tốn nhất
SELECT query, elapsed, read_rows, formatReadableSize(read_bytes)
FROM system.query_log WHERE type='QueryFinish' ORDER BY read_bytes DESC LIMIT 10;

-- DuckDB (in-process): tự đo
--   PRAGMA database_size; EXPLAIN ANALYZE SELECT ...;
```

Nguyên tắc: **đo bằng bytes/rows đọc, không bằng thời gian** — thời gian là hệ quả; bytes đọc là quyết định thiết kế (ORDER BY, cột chọn).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay ClickHouse:** DuckDB + parquet (nhỏ/vừa + không cần realtime), BigQuery/Snowflake (managed, đổi tiền), Druid (sub-second dashboard có thật sự cần). **Thay ETL phức tạp:** DBT + view + materialized — ít tầng hơn, dễ debug hơn.

Năm thấu kính:
- **Kinh tế:** Một cluster CH 3 node thay được cụm ES-to cho log (rẻ hơn nhiều lần); DuckDB gần như $0 ops — phổ hiệu năng/ops tốt nhất nhóm datastore.
- **Vận hành:** Nhánh LTS (26.8) cho production; monthly cho thử feature — theo dõi chu kỳ nâng cấp như distro Linux.
- **An ninh:** Analytics thường chứa dữ liệu tổng hợp đủ nhạy — row policy theo tenant (→5.14) + audit query log.
- **Lịch sử:** CERN tạo ClickHouse cho telemetry (2016); DuckDB từ CWI (Hà Lan — cùng triết lý "SQLite của analytics"); hai dự án "giải bài toán của chính người tạo" lại thành chuẩn ngành — motif lặp lại (Cassandra, Kafka — chương 5).
- **Người dùng:** Analyst thấy "query 10 tỷ dòng trong 2 giây" — đó là columnar + nén + vector hoá cùng làm việc; còn "chờ 5 phút" thường là row-engine bị ép làm việc sai chuyền.

---

## 8. Đọc tiếp & bài tập

- Lakehouse/parquet: **5.9** · Stream vào CH: **5.12** · Vector index: **5.10** · Observability backend: **11.1** · Ma trận: **5.15**
- **Bài tập 1:** Lấy query analytics chậm nhất của bạn; EXPLAIN indexes=1 — bytes đọc > 100× kết quả? ORDER BY không đi đúng trục lọc.
- **Bài tập 2:** Kiểm tra insert pattern (system.query_log): block size trung bình của INSERT. < 1.000 rows — đây là "too many parts" tương lai.
- **Bài tập 3:** Cài DuckDB; query một file parquet lớn trực tiếp (bãi đậu dữ liệu của bạn). Ghi thời gian — con số này thường đổi quan điểm về "cần cluster không".
