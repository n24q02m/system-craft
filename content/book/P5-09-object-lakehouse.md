# 5.9 — Object Storage & Open Lakehouse: S3 & Iceberg v3

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** ds-23-olap-vector-object.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 5.8 (nơi dữ liệu phân tích chảy về) · 5.7 (nguồn đổ).

**Sợi chỉ đỏ:** *Dữ liệu nhiều năm nhiều nguồn — object storage và lakehouse tổ chức ra sao?* — trả lời: object storage là nền "rẻ, to, bền"; Parquet cho định dạng cột nhưng thiếu giao dịch — table format (Iceberg/Delta/Hudi) bọc ngàn file thành bảng có schema, snapshot và time-travel; layout (partition, sort, compaction) quyết định hóa đơn cuối tháng. Câu hỏi để lại cho chương sau: *Gợi ý món và tìm theo ngữ nghĩa — vector search đổi trò tìm kiếm thế nào?*

**Thuật ngữ sẽ gặp:** *object storage* — blob qua HTTP API, bền 11 chữ 9, rẻ nhất theo GB: nền của mọi thứ to; *Parquet* — định dạng cột columnar đặt trên object; *table format* — lớp giao dịch + schema + version trên ngàn file: Iceberg/Delta/Hudi; *medallion* — bronze/silver/gold: lọc dần theo chất lượng, mỗi tầng một hợp đồng; *compaction* — gom file nhỏ thành lớn: nhỏ giọt làm query chậm dần; *catalog* — metastore biết bảng gồm những file nào: metadata là xương sống.

**Ví dụ mở đầu:** DM giữ đơn năm năm, hàng chục nguồn: nhét thẳng OLAP thì lưu trữ đắt và phân tích chéo gượng. Lakehouse: Kafka đổ bronze, job lọc silver, bảng tổng hợp gold — mỗi câu hỏi dùng đúng tầng. Nhưng dashboard realtime 5 giây không thuộc về đây: chương có hẳn mục "khi nào đừng dựng lakehouse".

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Dữ liệu nào xuống object storage (cold/audit/ML corpus) | Bao nhiêu % dữ liệu tôi thực sự query "nóng"? |
| 2 | Table format cho lakehouse (Iceberg/Delta/Hudi) | Ai đọc: Spark/Trino/CH/DuckDB — format nào cả họ đọc được? |
| 3 | Partition + sort order + compaction service | Layout quyết định chi phí query — đã thiết kế theo trục lọc thật? |
| 4 | Lifecycle (tiering, expiry) + chi phí egress | Hóa đơn S3 đi theo ba trục: lưu, đọc, yêu cầu — tôi tối ưu trục nào? |

---

## 2. Cơ chế

### 2.1 Object storage: nền của mọi thứ "rẻ, to, bền"

Key-value phẳng (S3/GCS/Azure Blob/MinIO/R2): object bất biến + key; durability 11 nine (thiết kế — →1.4 EC bên dưới); **không có** file system thật (không rename nguyên tử, không append), metadata limit (5 TB/object, key length). Mô hình giá 3 trục: lưu trữ (GB-tháng), request (PUT/GET), **egress** (ra ngoài — thứ hay quên; R2/others = $0 egress để phá cuộc chơi — (V bảng giá công khai 10/2026)).

Ba sự thật vận dụng: (a) object **bất biến** → "sửa" = ghi object mới + cập nhật con trỏ (đó là lý do table format tồn tại); (b) listing key to là chậm (prefix quét) — metadata/catalog tách riêng; (c) consistency read-after-write đã mạnh (S3 từ 2020) — nhưng vẫn không phải database.

### 2.2 Vì sao cần table format (Iceberg/Delta/Hudi)

Parquet thô trên S3 = "các file tốt" nhưng: không transaction, không schema tiến hoá an toàn, không có stats toàn bảng, nhỏ file proliferate. **Table format** thêm lớp metadata (manifest/catalog) phía trên: commit atomic, time travel, schema/Partition evolution, hidden partitioning. Ba cái đáng phân biệt:

| | Iceberg | Delta | Hudi |
|---|---|---|---|
 | Chủ | Apache (Netflix gốc) | Linux Fdn (Databricks gốc) | Apache (Uber gốc) |
| Điểm mạnh | spec mở, engine-agnostic rộng nhất (Spark/Trino/Flink/CH/DuckDB/Snowflake) | hệ sinh thái Databricks liền mạch | upsert/timeline tốt |
| 2026 | **v3 spec** — phổ quát nhất | Delta UniForm thu hẹp khoảng cách | ngách hơn |

Verify: Iceberg v3 (1.11.0+ — 10/2026). v3 thêm: hàng xoá theo vị trí cải tiến, statistics mở rộng, view chuẩn hoá. **Quy tắc sách: chọn Iceberg khi cần đa engine** — nó là "linhua franca" lakehouse 2026.

### 2.3 Layout quyết định hóa đơn: partition + sort + compaction

```
CREATE TABLE events (
  event_date DATE, tenant_id, ...
) PARTITIONED BY (days(event_date))   -- xoá/lifecycle theo ngày
  SORT ORDER (tenant_id, event_time)  -- trong partition, dữ liệu xếp theo query chính
```

- **Partition** theo trục lifecycle + lọc thô (ngày/tenant lớn);
- **Sort order** trong file giúp min/max pruning (như ORDER BY ClickHouse — →5.8): query 1 tenant không đọc tenant khác;
- **Compaction service** (maintain): gộp small files (sinh từ stream ghi nhỏ) + rewrite manifests — bỏ bền là "bệnh small files": mỗi file = 1 request + đọc metadata — query chậm dần đều (triệu chứng "lakehouse già hóa").

### 2.4 Kiến trúc tiêu chuẩn 2026: Kafka → Lakehouse (medallion)

```
[App] → Kafka (→5.7) → Flink/consumer → Iceberg (bronze)
                                → cleaning (silver) → aggregate (gold)
                                        ↓
         Trino/DuckDB/CH/Spark — query — S3
```

Bronze (thô, replay được) → silver (sạch) → gold (aggregate cho BI). Điểm mạnh cấu trúc: **replay từ bronze** khi logic sai — không mất dữ liệu gốc; **schema tiến hoá** qua Iceberg không khóa query. Đây cũng là pipeline chuẩn cho corpus AI (→12.x): một bản dữ liệu, nhiều người tiêu thụ (BI + training + RAG).

### 2.5 Khi nào KHÔNG dùng lakehouse

Query latency < giây trên dữ liệu nóng (dùng CH — →5.8); cần transaction OLTP (dùng RDBMS — →5.2); dữ liệu nhỏ (< vài trăm GB — DuckDB file + parquet đủ, khỏi S3); team chưa có ops pipeline (ETL chết là sự cố chết — →5.12).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Iceberg | v3 (1.11.0+, 10/2026) | V | versions.csv |
| Durability S3-class | 11×9 | V | thiết kế |
| Object max | 5 TB | V | |
| Nén parquet | ~10× | I | như columnar — →5.8 |
| Small file bệnh | < 128 MB mỗi file | I | ngưỡng compaction |

---

## 4. Suy luận kiến trúc

- **S1:** Object storage là **lớp $.01/GB-tháng của kiến trúc** — mọi dữ liệu "không nóng" nên kết thúc ở đây; giữ nóng ở đắt là lãng phí cấu trúc.
- **S2:** Tham số trụ: cost theo trục (lưu/request/egress), small-file count, compaction lag, query bytes-scanned.
- **S3:** Iceberg đổi tính mở đa engine lấy chút phức tạp metadata; Delta đổi "một nhà" cho đơn giản; compaction đổi compute lấy chi phí query về sau.
- **S4:** Tách compute/storage (query engine stateless + S3) là trục kiến trúc thập kỷ — CH/Trino/Snowflake/DuckDB đều hội tụ về "đọc parquet/iceberg"; kế hoạch dữ liệu mới nên sinh ra **parquet-compatible mặc định**.
- **S5:** AI amplifies: corpus training + RAG index đều từ cùng hồ iceberg — "một bản dữ liệu, ba người dùng (BI/ML/RAG)" giảm sao chép (single source — chống phân rã).
- **S6:** Khi lakehouse "chậm": small files → layout sai (partition/sort) → không pruning — theo thứ tự đó; engine hiếm khi là thủ phạm đầu.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Query chậm dần theo tuần | Small files proliferate | files count / partition | §2.3 |
| Hóa đơn S3 vọt | Request/egress (không phải lưu) | bill theo trục | §2.1 |
| Iceberg commit xung đột | Nhiều writer cùng bảng | writer hợp nhất / wap | §2.2 |
| "Sửa" dữ liệu khó | Object bất biến — thiếu mô hình | Iceberg delete/overwrite | §2.1 |
| Replay không được | Bronze không giữ thô | pipeline audit | §2.4 |
| Catalog "mất" bảng | Không dùng catalog chuẩn | Nessie/REST catalog | §2.2 |

---

## 6. Cách đo

```bash
# S3: kích thước + số file theo prefix (small file scan)
aws s3 ls s3://lake/events/ --recursive | awk '{s+=$3; n++} END {print n, "files", s/n, "avg"}'

# Iceberg: history + files (qua engine — Spark/Trino)
-- SELECT * FROM my_table.files;      -- size per file
-- SELECT * FROM my_table.history;    -- snapshot gần đây

# Chi phí theo trục (Cost Explorer: Storage vs Requests vs DataTransfer)
#   — vẽ 3 đường: thường thấy egress/request bất ngờ
```

Nguyên tắc: **đo hóa đơn theo trục như đo latency theo tầng (→3.10)** — "S3 đắt" không phải thông tin; "request đắt" hay "egress đắt" mới là quyết định.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay lakehouse:** ClickHouse cho log/telemetry nóng (rồi TTL xuống S3), DuckDB+parquet cho nhóm nhỏ, warehouse managed (BigQuery/Snowflake — đổi tiền lấy ops-zero). **Thay S3:** MinIO/R2 (egress $0) cho traffic ra nhiều; on-prem khi chủ quyền dữ liệu bắt buộc (→10.5).

Năm thấu kính:
- **Kinh tế:** Lakehouse là lời giải "giá theo độ nóng": hot (CH/DRAM) → warm (iceberg+S3) → cold (glacier) — mỗi bậc ~10× rẻ hơn; thiết kế tiering = tiết kiệm cấu trúc.
- **Vận hành:** Compaction + manifest maintenance là "nha sĩ" của hồ (như repair Cassandra — →5.5): lịch định kỳ, đo trước sau.
- **An ninh:** Bucket công khai là sự cố số một lịch sử cloud — policy deny-by-default + mã hoá + audit log (→10.5); GDPR erasure xuyên lake (iceberg delete + rewrite — →5.13).
- **Lịch sử:** Hadoop "xếp file vào HDFS theo thư mục" (2006) → Databricks Delta (2016) → Iceberg chuẩn mở (2020s): ngành học cùng một bài 15 năm — metadata đúng mới là database; file chỉ là vật chứa.
- **Người dùng:** Người dùng thấy "dashboard 3 năm dữ liệu vẫn query được, không ai đòi mua thêm SSD" — đó là lakehouse trả tiền thuê rẻ cho lịch sử, giữ SSD cho hôm nay.

---

## 8. Đọc tiếp & bài tập

- Pipeline: **5.12** · OLAP engine: **5.8** · Catalog/git-like: — · Corpus AI: **12.4** · Retention/GDPR: **5.13** · Sizing: **5.16**
- **Bài tập 1:** Quét prefix lớn nhất hồ của bạn: số file + kích thước TB. Trung bình < 128 MB = kế hoạch compaction tuần này.
- **Bài tập 2:** Mở Cost Explorer 3 trục (lưu/request/egress) 90 ngày. Trục nào bất ngờ? Mỗi bất ngờ là một kiến trúc chưa ai đưa ra.
- **Bài tập 3:** Viết Iceberg table đơn giản (Spark/Trino local): insert → sửa schema (thêm cột) → time travel về snapshot cũ. 30 phút này dạy "table format" nhanh hơn một tuần đọc spec.
