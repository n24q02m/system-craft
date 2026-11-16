# 5.12 — Stream Processing (Flink) & Batch Orchestration

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.7 (queue/stream) · 5.9 (lakehouse).

**Sợi chỉ đỏ:** *Tính toán chảy liên tục hay gom theo mẻ — stream và batch ăn khớp nhau thế nào?* — trả lời: stream và batch không đánh nhau — phân lớp theo độ trễ cần thiết rồi chọn đúng đài; Flink cho stateful đúng đắn (event time, watermark, state checkpoint); orchestrator điều mẻ theo DAG; pattern chuẩn 2026 là stream chảy về lakehouse. Câu hỏi để lại cho chương sau: *Dữ liệu cá nhân của khách — ai được giữ gì, bao lâu, xoá kiểu gì (governance)?*

**Thuật ngữ sẽ gặp:** *event time vs processing time* — thời gian trong dữ liệu và thời gian xử lý: lệch nhau là chuẩn, không phải lỗi; *watermark* — mốc "dữ liệu cũ đã tới đủ": đóng cửa sổ aggregation; *state* — kết quả dở dang của stream: to, phải checkpoint và khôi phục được; *cửa sổ* — tumbling/sliding/session: ba ngữ nghĩa gom dữ liệu; *orchestrator* — Airflow/Dagster/Prefect điều batch theo DAG, xử lệ thuộc và retry; *lambda/kappa* — hai kiến trúc cũ-mới: một ý tưởng, hai đường đi.

**Ví dụ mở đầu:** Đối soát cuối ngày của DM cần đủ dữ liệu — batch. Cảnh báo gian lận cần trong năm giây — stream. Và cùng một logic đếm viết hai lần ở hai hệ là nguồn bug kinh điển. Chương này dạy phân lớp theo độ trễ, viết logic một lần, và nối hai đài vào một kiến trúc.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Stream thật hay micro-batch đủ cho bài toán | Độ trễ chấp nhận: ms, giây, hay phút? |
| 2 | Xử lý trễ/đến muộn (watermark + allowed lateness) | Event đến muộn 5 phút — bỏ, vá, hay đợi? |
| 3 | Exactly-once: checkpoint + transactional sink | Tôi chấp nhận lặp nào (→5.7) cho từng pipeline? |
| 4 | Orchestration (Airflow/dagster) + SLA pipeline | Batch chết lúc 3h sáng — ai biết, ai chạy lại? |

---

## 2. Cơ chế

### 2.1 Phân lớp theo độ trễ — chọn đúng đài

| Lớp | Công cụ | Độ trễ | Use case |
|---|---|---|---|
| Pure stream | **Flink** | ms–s | cảnh báo, join thời gian thực |
| Micro-batch | Spark Structured Streaming | s–phút | ETL lớn, đội đã biết Spark |
| Consumer đơn giản | Kafka consumer + công cụ của bạn | s | dự báo, đơn giản |
| Batch | Airflow/Dagster + SQL/CH | giờ | báo cáo, rebuild |

**Quy tắc kinh tế:** mỗi bậc "sớm hơn" tốn ops hơn bậc dưới; **đừng dựng Flink cho báo cáo sáng hôm sau** — batch + scheduler là câu trả lời rẻ hơn 10×.

### 2.2 Flink: event time, watermark, state

- **Event time vs processing time:** sự kiện mang timestamp riêng (điện thoại offline 5 phút) — tính toán theo event time mới đúng;
- **Watermark:** cam kết "đến giờ T, dữ liệu event-time ≤ X coi như đủ" — cửa sổ đóng khi watermark qua; dữ liệu đến sau → **allowed lateness** (chờ thêm) hoặc **side output** (bỏ ra nhánh xử lý riêng);
- **State + checkpoint:** state trong RocksDB (→5.1), checkpoint định kỳ xuống storage; crash → khôi phục state + replay từ offset Kafka = **exactly-once trong phạm vi pipeline** (sink phải transactional/idempotent — →4.8/5.7);
- **Backpressure:** consumer chậm → tín hiệu lan về source — metric sức khỏe số một của job.

### 2.3 Join stream: ba cửa sổ, ba ngữ nghĩa

- **Window join:** hai stream trong cùng cửa sổ thời gian — chuẩn cho "sự kiện + enriched";
- **Interval join:** A xảy ra trong khoảng ±X quanh B (order → payment trong 1 giờ) — không cần window cứng;
- **Temporal lookup:** stream ⨝ bảng chiều hiện tại (dimension) — nhớ: bảng đổi theo thời gian, lookup dùng **version đúng lúc** (temporal join) không thì enrichment sai lịch sử.

### 2.4 Batch orchestration — Airflow/Dagster/Prefect

Ý nghĩa: DAG task + dependency + retry + alert + lịch. Điểm thiết kế đáng tiền: **idempotent task** (chạy lại không lặp kết quả — cùng Idempotency-Key tư duy →4.8), **SLA + alert sớm** (pipeline ETL 4h sáng trễ = page người), **backfill plan** (logic mới chạy lại lịch sử — cần dữ liệu replay được: →5.9 bronze). Dagster/Prefect thế hệ mới: asset-centric (định nghĩa "tài sản dữ liệu" + lineage) — hợp tư duy lakehouse.

### 2.5 Streaming-to-Lakehouse — pattern chuẩn 2026

```
Kafka → Flink (validate/enrich) → Iceberg (bronze/silver)
                      ↓ alert nếu anomaly
Airflow (gold aggregate + compaction schedule) ← catalog/lineage
```

Vai trò phân công rõ: Flink lo "đúng lúc", Airflow lo "đúng lịch", Iceberg lo "đúng lịch sử" — không chồng chéo trách nhiệm. Observability của pipeline (nếu data trễ, business phải biết — freshness metric — →11.1).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Flink độ trễ end-to-end | ms–s (true stream) | I | checkpoint interval ảnh hưởng |
| Checkpoint interval chuẩn | 30s–5min | I | theo dung lượng state |
| Watermark bound | theo nghiệp vụ (phút) | P | đếm tỷ lệ muộn |
| Airflow/Dagster | batch chuẩn ngành | V | |
| Backfill | bắt buộc thiết kế từ đầu | P | idempotency |

---

## 4. Suy luận kiến trúc

- **S1:** Chọn lớp xử lý theo **độ trễ nghiệp vụ thật** (không phải "realtime nghe hay") — mỗi bậc sớm hơn là 5–10× ops.
- **S2:** Tham số trụ: freshness (event-time → có mặt trong store), backpressure, checkpoint duration/success, late-events ratio.
- **S3:** Watermark đổi completeness lấy latency; side-output đổi đơn giản lấy xử lý muộn tay; micro-batch đổi ms lấy ops quen thuộc.
- **S4:** Streaming + lakehouse (kafka→flink→iceberg) là pipeline mặc định dữ liệu 2026: một đường, ba trách nhiệm rõ ràng (§2.5).
- **S5:** AI pipeline (embedding, RAG index — →12.5) là workload pipeline như mọi workload: cần freshness metric + backfill — đừng dựng "pipeline AI đặc biệt", dùng lớp này.
- **S6:** Khi pipeline "chậm": backpressure ở operator nào (web UI Flink cho thấy từng bước) — chưa từng có "chậm đều", chỉ có "tắc một chỗ".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Job Flink khựng định kỳ | Checkpoint lớn/chậm | checkpoint duration metric | §2.2 |
| Kết quả "thiếu" sự kiện | Watermark đóng sớm + muộn | late events ratio; side output | §2.2 |
| State phình vô hạn | Keyed state không TTL | state size graph | §2.2 |
| ETL chết không ai biết | Không SLA/alert | airflow sla; on-call | §2.4 |
| Chạy lại backfill lặp dữ liệu | Task không idempotent | audit write path | §2.4 |
| Enrich sai lịch sử | Lookup bảng chiều không temporal | temporal join | §2.3 |

---

## 6. Cách đo

```bash
# Flink: backpressure + checkpoint (Web UI / REST)
curl -s jobmanager:8081/jobs/<id>/checkpoints | jq '.summary'
#  — duration trend + size trend: hai con số health của stateful stream

# Late events (đo bằng side output rate):
#   late_events_total / events_total — > 1%? watermark cần nới

# Freshness (metric pipeline, export Prometheus):
#   max(event_time) đã ghi xuống store — so với now()
```

Nguyên tắc: **freshness là SLA của pipeline như p99 là SLA của API** — đo được, alert được, không tranh luận.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Flink:** consumer thường + DB/CH (đa số "streaming" thật ra là "xử lý theo lô nhỏ mỗi 30 giây"); Kafka Streams nếu đã sâu Kafka (JVM trong app); materialized view của CH cho aggregate. **Thay Airflow:** cron + script cho ≤ 5 task (đừng dựng platform cho 3 cron); Dagster nếu tư duy asset hợp tổ chức.

Năm thấu kính:
- **Kinh tế:** Flink cluster + người hiểu watermark là chi phí thật; giải pháp "đủ chậm" (micro-batch/CH) thường thắng tổng — tính cả giờ debug cửa sổ thời gian.
- **Vận hành:** Job stream chết giữa đêm là sự cố **dữ liệu im lặng** — alert theo freshness, không theo process sống (process sống ≠ dữ liệu chảy).
- **An ninh:** Pipeline là đường đi của dữ liệu PII tới nhiều nơi (log/store/backup — →5.13) — inventory luồng như inventory bảng.
- **Lịch sử:** Lambda (batch + speed layer, 2014) → Kappa (một đường stream, 2017) → 2026 thực dụng: stream-to-lakehouse (một đường + replay) — ngành hội tụ về "một đường, nhiều lớp độ trễ".
- **Người dùng:** "Vé vừa quét đã thấy trong app" (stream) và "báo cáo sáng ra có đủ" (batch đúng giờ) — hai loại đúng giờ khác nhau, chương này là hợp đồng cho cả hai.

---

## 8. Đọc tiếp & bài tập

- Kafka nền: **5.7** · Lakehouse: **5.9** · Idempotency: **4.8** · Freshness/observability: **11.1** · AI pipeline: **12.5**
- **Bài tập 1:** Với pipeline chính: đo late-events ratio (side output). > 1% nghĩa là watermark đang "đóng cửa sớm" — mỗi event muộn là một con số sai trong báo cáo.
- **Bài tập 2:** Liệt kê task batch không idempotent. Mỗi cái là một "backfill tương lai sẽ lặp dữ liệu" — đánh dấu và sửa theo Idempotency-Key tư duy.
- **Bài tập 3:** Tính freshness thật: `now() - max(event_time)` trong store. Con số này so với SLA nghiệp vụ (không phải SLA kỹ thuật) là cuộc trò chuyện đáng giá nhất tuần này.
