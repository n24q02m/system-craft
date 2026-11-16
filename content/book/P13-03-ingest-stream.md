# 13.3 — Playbook: Ingest, Telemetry & Stream

> **Tầng:** Nghiệp vụ · **Quyển III** · **Trục đọc:** playbook theo miền · **Động từ liên quan:** Áp dụng · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.7 (queue/stream) · 5.12 (stream và batch).

**Sợi chỉ đỏ:** *Mọi sự kiện chảy về một chỗ — ingest và stream vận hành ra sao?* — trả lời: mọi sự kiện chảy về một chỗ — ingest và stream là hai dòng nước khác nhau, đừng trộn; backpressure là bộ ba lựa chọn phải công khai (chặn nguồn, rơi tin, hoặc đệm); đỉnh và buffer sizing tính cho ngày tồi tệ; đúng-một-lần ở stream khi cần và trả giá; và telemetry về chính hệ telemetry. Câu hỏi để lại cho chương sau: *Nước lũ dữ liệu — lakehouse phân tích tổ chức thế nào cho tin được?*

**Thuật ngữ sẽ gặp:** *ingest vs stream* — gom nhiều nguồn về một kho, và xử lý chảy liên tục: hai dòng, hai công cụ; *backpressure* — quá tải thì chặn nguồn, rơi, hay đệm: ba lựa chọn, công khai, không mặc định ngầm; *buffer sizing* — đỉnh ngày tồi tệ nhân thời gian hồi: nhỏ giọt đầy đĩa là chết; *đúng-một-lần* — end-to-end cần idempotency ở sink (nối 5.7, 8.3): đổi bằng độ trễ; *dead letter queue* — tin hỏng có nơi nằm, có người soi: vận hành thật; *đo hệ đo* — telemetry về telemetry: khi hệ đang chết, queue của telemetry cũng đang đầy.

**Ví dụ mở đầu:** Khuyến mãi miễn phí ship của DM tạo một cột sóng sự kiện trong vài phút: buffer đầy — Kafka rơi hay chặn nguồn? Quyết định phải tồn tại từ trước và ai cũng biết. Còn observability: nếu telemetry đi chung đường dữ liệu, nó chết đúng lúc cần nhất. Chương này là playbook ingest với con số cho ngày tồi tệ.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Hàng rào giữa ingest nghiệp vụ vs telemetry (mỗi loại một chuẩn sống) | Log của tôi có được "bỏ rơi" khi quá tải không — và ai quyết? |
| 2 | Backpressure: chậm hay bỏ, ở đâu | Consumer chậm 5 phút — tôi chờ, shed, hay scale (ai trả tiền)? |
| 3 | Schema & evolution: registry, compatible-check ở CI | Thêm field vào event — consumer cũ chết không? |
| 4 | Buffer & đỉnh: Kafka partition/retention bao nhiêu cho "ngày tồi tệ" | Đỉnh 10× trung bình — buffer chứa được mấy phút? |

---

## 2. Cơ chế

### 2.1 Kiến trúc tham chiếu ingest/stream

```
[Nguồn: app/agent/IoT (→6.6)] → [Edge/collector: validate + gắn metadata]
   → [Kafka (→5.7): partition theo key, retention theo nghiệp vụ]
      → [Stream process (→5.12 Flink-style): enrich/aggregate/join]
         → [Sink: OLTP (5.2) / OLAP (5.8) / TSDB (5.11) / search (5.6)]
[DLQ] ← mọi consumer (dead-letter + replay — →5.7)
[Schema registry] — CI kiểm compatibility mọi thay đổi (→4.8 additive)
```

### 2.2 Hai dòng nước khác nhau — đừng trộn

- **Nghiệp vụ (fact):** đơn hàng, sự kiện thanh toán — **không được mất** (at-least-once + idempotent sink — 8.3), schema chặt, DLQ có chủ xử lý hàng ngày;
- **Telemetry (đo lường):** metric/log/trace — **được mất có kiểm soát** (sampling — 11.2; drop khi quá tải — 8.5 shedding), schema lỏng hơn, cardinality là kẻ thù (11.2).
Trộn hai dòng (một topic chung "events") là lỗi thiết kế kinh điển: một ngày telemetry phình làm tắc cả fact nghiệp vụ (hoặc ngược lại bị giới hạn vì sợ mất).

### 2.3 Backpressure — bộ ba lựa chọn công khai

| Tình huống | Nên | Ghi chú |
|---|---|---|
| Đỉnh tạm (phút) | **buffer** (Kafka chịu) | retention đủ — §2.4 |
| Consumer thiếu năng lực thường trực | **scale consumer** (→9.2 KEDA theo lag) | rẻ hơn sheds mãi |
| Nguồn spam/lỗi (retry storm — 8.5) | **shed ở edge + rate limit nguồn** | kẻ ác phải bị chặn, không chày cối |
Đo bằng **consumer lag** (theo partition) — dashboard + alert (11.1 burn-rate tư duy: lag leo thang = ticket; lag + sắp hết retention = page).

### 2.4 Đỉnh & buffer sizing (ngày tồi tệ)

Partition Kafka: theo **throughput consumer + song song** (không phải "càng nhiều càng tốt" — rebalance tốn, 6.6 bài học); retention: ≥ vài lần "thời gian phục hồi sự cố dự kiến" (nếu MTTR thường 2 h — retention ≥ 6–12 h cho dòng nghiệp vụ: consumer chết 2 h vẫn không mất); theo dõi **disk vs retention** (hết đĩa trước hết hạn = tự gây sự cố). Drill: tắt consumer 30 phút (11.3) — mở lại: kịp không? dữ liệu vẹn nguyên? — đây là DR của stream.

### 2.5 Đúng-một-lần ở stream (khi cần)

Kafka transactional + consumer idempotent (→5.7 EOS; 8.3 chuỗi chuẩn): đếm, tổng — dùng transaction; biến đổi "làm lại được" (recompute từ nguồn — 5.15) thì at-least-once + re-run rẻ hơn — **không mua đúng-một-lần khi tái tạo được** (Yagni cho stream).

### 2.6 Đo chính hệ đo — telemetry về telemetry

Meta-monitoring (11.2 đã yêu cầu): ingest rate, drop rate, lag, DLQ depth, schema-incompatible count, tuổi dữ liệu tại sink. Luật bất đối xứng đáng nhớ: **hệ đo chết không được phép kéo hệ đo chết** (collector crash không được làm chết app — SDK phải fail-open, fire-and-forget buffer nội bộ nhỏ).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Kafka throughput/partition | MB/s bậc | I | theo cấu hình |
| Retention nghiệp vụ | ≥ vài × MTTR | P | |
| Consumer lag alert | leo thang + sắp hết retention | P | |
| Sampling telemetry | theo lớp (→11.2) | P | |
| DLQ SLA xử lý | ngày | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Stream platform là **hệ thống vận tải** — giá trị ở SLA giao hàng (lag, mất, thứ tự) cho **từng dòng nước**; thiết kế la bàn là bảng "được-mất gì" per stream, không phải "Kafka chuẩn chung";
- **S2:** Tham số trụ: lag p95 theo dòng, tỉ lệ drop (telemetry) — phải = 0 với fact, tuổi dữ liệu tại sink, DLQ depth + time-to-clear, schema break bắt ở CI (mục tiêu 100%).
- **S3:** Buffer đổi đĩa lấy thời gian phản ứng — sizing bằng **kịch bản tồi tệ × MTTR**, kiểm chứng bằng drill tắt consumer (11.3);
- **S4:** Schema registry là **OpenAPI của stream** (4.3/4.8 cùng hợp đồng): CI kiểm compatibility, additive-first, deprecate có lịch — mất rồi consumer cũ chết hàng loạt;
- **S5:** Nguồn mới 2026: **agent AI sinh event với tốc độ người-không-bấm** (mỗi bước tool một event — 12.4) và IoT tiếp tục — thiết kế edge validate + rate limit per source từ đầu (10.3/11.3), không chờ "nguồn tử tế";
- **S6:** Khi "dữ liệu stream tới sink trễ/chậm": tra theo thứ tự — lag consumer (scale/bug?), retention chạm (đĩa?), rebalance (partition di chuyển — 5.7), rồi mới tới "Kafka chậm" (gần như cuối danh sách).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Telemetry phình, tắc fact | Trộn hai dòng nước | tách topic/cluster | §2.2 |
| Consumer chết 2 h mất dữ liệu | Retention < MTTR | tăng retention + drill | §2.4 |
| Đếm bị đôi | Không idempotent/EOS | 8.3 chuỗi chuẩn | §2.5 |
| Thêm field, consumer cũ chết | Không registry/CI | schema registry + compatible check | §2.3 |
| DLQ đầy không ai biết | Không alert/chủ | alert + SLA xử lý | §2.6 |
| Retry nguồn dập ingest | Không rate limit nguồn | edge limit + jitter (8.5) | §2.3 |

---

## 6. Cách đo

```bash
# Drill "consumer chết 30 phút" (staging, định kỳ):
#   dừng consumer chính → đợi 30' → khởi động lại
#   đo: dữ liệu có đủ (retention đủ)? sink khớp số? DLQ sinh bao nhiêu?
#   — ba con số là DR-plan thật của stream (không phải tài liệu)

# Lag dashboard: per (stream × partition) — alert 2 tầng:
#   lag leo thang 15' → ticket; lag × retention-còn-1h → page
```

Nguyên tắc: **mọi dòng dữ liệu có "cam kết giao hàng" ghi ra** (mất được không, trễ bao lâu, thứ tự cỡ nào) — không có cam kết thì không có vận hành, chỉ có may mắn.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Kafka tự vận hành:** managed stream (Kafka-managed/PubSub/Kinesis-style — 11.7 mua vs tự); **thay Flink tự chạy:** consumer nhóm + công cụ orchestration đơn giản (đủ cho pipeline thẳng không window phức tạp); **thay schema registry:** protobuf version field + quy ước (được lúc 2 team — vỡ ở 20).

Năm thấu kính:
- **Kinh tế:** Stream là **hạ tầng dùng chung** — chi phí phân bổ theo dòng (11.5 showback theo topic!) khiến mỗi team thấy tiền của data-thirsty feature của mình;
- **Vận hành:** Rebalance/brokerUpgrade là "deploy của stream" — window thấp điểm + drill (5.7 đã dạy cluster KRaft; đây là phần vận hành của cùng bài);
- **An ninh:** Topic là **ranh giới dữ liệu** (ACL per topic như RLS per tenant — 5.14/10.3): telemetry chứa PII phải như fact nhạy (redact ở edge — 11.2);
- **Lịch sử:** ETL batch đêm (1990s) → micro-batch (2010s) → stream (2015+): mỗi bước rút "độ trễ dữ liệu" một bậc; Kafka mang mô hình "commit log của DB" (5.1 WAL) lên thành hạ tầng độc lập — lại là cũ mới hoá;
- **Người dùng:** "Dữ liệu của tôi cập nhật khi nào?" — câu hỏi của mọi dashboard, mọi thông báo, mọi quyết định; playbook này là lời cam kết thời gian cho câu đó (và cam kết phải đo được).

---

## 8. Đọc tiếp & bài tập

- Kafka sâu: **5.7** · Stream process: **5.12** · Schema/API: **4.3, 4.8** · Backpressure: **8.5** · Telemetry: **11.2** · IoT ingest: **6.6**
- **Bài tập 1:** Liệt kê mọi stream trong tổ chức; mỗi dòng gắn nhãn fact/telemetry + cam kết (mất được? trễ tối đa?). Hàng nào không gán được nhãn — đó là rủi ro đang mở;
- **Bài tập 2:** Chạy drill consumer-chết-30-phút (§6). Retention đủ không? Sink khớp sau khi chạy lại? Kết quả đi thẳng vào ADR "retention chuẩn" của bạn;
- **Bài tập 3:** Đối chiếu DLQ: hiện có bao nhiêu message, tuổi già nhất, ai xử lý lần cuối? Không có câu trả lời trong 5 phút — DLQ đang là hố đen (và hố đen có xu hướng đầy vào đúng tuần quan trọng).
