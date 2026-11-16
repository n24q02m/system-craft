# 4.7 — Hợp đồng Bất đồng bộ: AsyncAPI 3.0, CloudEvents & Schema Registry

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.3 · 4.4.

**Sợi chỉ đỏ:** *Sự kiện bên trong tổ chức (đơn mới, ship, hoàn) mô tả và khớp nối thế nào — AsyncAPI, CloudEvents?* — trả lời: hợp đồng bất đồng bộ không có response để soi — nên AsyncAPI 3.0 mô tả kênh và payload, CloudEvents chuẩn hoá phong bì metadata, và Schema Registry với quy tắc compatibility là trái tim giữ producer không giết consumer. Câu hỏi để lại cho chương sau: *API đã công khai — sống mãi à: version, deprecate, idempotency cho đối tác là gì?*

**Thuật ngữ sẽ gặp:** *phong bì CloudEvents* — metadata chuẩn (type, source, time, id) bọc payload: consumer biết mình đang giữ gì; *AsyncAPI 3.0* — "OpenAPI của thế giới sự kiện": mô tả kênh, payload, binding; *Schema Registry* — kho schema + cổng kiểm tra trước khi publish; *compatibility* — BACKWARD/FORWARD/FULL: quy tắc tiến hoá sự kiện; *at-least-once* — consumer phải chịu trùng lặp: thiết kế idempotent; *dead letter queue* — nơi sự kiện hỏng nằm chờ người soi.

**Ví dụ mở đầu:** Sự kiện "đơn mới" của DM do teamOrders phát, ba team tiêu thụ: kho, ship, đối soát. Một buổi sáng producer thêm trường mà không ai hay: consumer đối soát chết ngầm tới cuối ngày — trùng đơn hoàn tiền. Schema Registry chặn đúng buổi sáng đó: schema vỡ không publish được. Chương này là hợp đồng cho thế giới không có response để dựa vào.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Schema cho sự kiện: JSON Schema trong AsyncAPI hay Avro/Protobuf trong registry | Đường sự kiện của tôi ai tiêu thụ — và họ nâng cấp trước/sau thế nào? |
| 2 | Compatibility mode (backward/forward/full) cho từng topic | Cho phép đổi gì trước khi consumer kịp theo? |
| 3 | Envelope chuẩn hoá (CloudEvents) hay schema riêng | Metadata (id, time, source, type) có thống nhất toàn org chưa? |
| 4 | Registry + CI gate cho schema (giống OpenAPI diff — →4.3) | Schema đổi có ai chặn breaking change không? |

---

## 2. Cơ chế

### 2.1 Hợp đồng bất đồng bộ khác hợp đồng đồng bộ ở chỗ nào

REST/gRPC: caller chờ — sai schema thấy **ngay** (lỗi 4xx/5xx). Sự kiện: producer gửi xong là đi; consumer có thể **chưa tồn tại hoặc chưa viết** — sai schema chỉ hiện sau tuần/month, khi dữ liệu hỏng đã lan (→5.7). Vì vậy hợp đồng async cần **hợp máy** (registry kiểm tra được) chứ không chỉ hợp người (doc).

### 2.2 AsyncAPI 3.0 (2024): OpenAPI cho thế giới sự kiện

Mô tả: application/channel/operation — pub/sub riêng bạch; binding cho Kafka/MQTT/AMQP/WebSocket (→5.7); reusable payload schema (JSON Schema/Avro). Ứng dụng: sinh doc, sinh client, **test that** consumer khớp producer (contract test async), discover topic. 3.0 đáng chú ý: tách operation khỏi message, hỗ trợ nhiều protocol hơn chuẩn hoá cách mô tả.

### 2.3 CloudEvents: phong bì chuẩn cho metadata

`id`, `source`, `type`, `time`, `specversion`, `datacontenttype`, `data` — chuẩn CNCF, binding JSON/Protobuf/HTTP/Kafka. Giá trị thật: **thống nhất metadata toàn org** — mọi consumer xử lý id/time/type giống nhau (trace, idempotency — →4.8, dedup). Chi phí gần 0. **Quy tắc: phong bì chuẩn, nội dung theo schema riêng** — đừng nhét nghiệp vụ vào header chuẩn.

### 2.4 Schema Registry & compatibility — trái tim của hệ sự kiện

Registry (Confluent/buf/Apicurio hoặc git-based) lưu version schema + kiểm tra tại đăng:

| Mode | Cho phép | Nghĩa vận hành |
|---|---|---|
| BACKWARD | consumer mới đọc schema cũ | upgrade **consumer trước** |
| FORWARD | consumer cũ đọc schema mới | upgrade **producer trước** |
| FULL | cả hai | tự do tuần tự — hiếm khi giữ được lâu |

Luật tiến hoá giống protobuf (→4.4): thêm field OK; xoá/đổi type phải qua 2 bước (deprecate → gỡ sau khi hết reader). **Sai sót đắt nhất ngành:** đổi schema producer khi consumer legacy vẫn chạy — dữ liệu âm thầm sai (không lỗi!) — vì vậy: **registry check trong CI + thời gian cooldown giữa version**.

### 2.5 Test bất đồng bộ — pipeline tối thiểu

```
producer schema ──CI: đăng thử + compatibility check──> registry
        │
consumer ──CI: contract test với schema mới nhất (consume fixture)──> pass?
```

Cộng: **consumer-driven test** (producer phát fixture "golden events" — consumer chạy qua pipeline xác nhận không vỡ) — tương đương contract test REST nhưng lệch pha thời gian.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| AsyncAPI | 3.0 (2024) | V | operation/message tách |
| CloudEvents | 1.0 (specversion) | V | CNCF |
| Compatibility 3 mode | backward/forward/full | V | Kafka semantics |
| Cooldown giữa 2 version schema | theo vận tốc deploy consumer | P | thường 1–4 tuần |

---

## 4. Suy luận kiến trúc

- **S1:** Hệ async **trả lỗi chậm** — hợp đồng phải là tường máy (registry + CI) thay vì hồi ức các team đồng ý gì.
- **S2:** Tham số trụ: schema version trong payload (đếm theo version), lỗi deserialize/s, topic không có schema (%).
- **S3:** CloudEvents đổi tự do metadata lấy sự thống nhất; registry đổi tốc độ đổi schema lấy an toàn — cả hai rẻ so với một sự cố dữ liệu lan.
- **S4:** Outbox pattern (→5.15) + CloudEvents + registry hợp thành "API sáng sủa" cho thế giới event-driven — ba mảnh này ổn định và ghép được.
- **S5:** AI pipeline cũng là consumer/producer (event-driven data — →12.x) — schema chặt là điều kiện RAG/agent không "ảo tưởng" về dữ liệu.
- **S6:** Khi consumer "thỉnh thoảng parse lỗi": hỏi schema version nào đang trên wire vs consumer đọc — và vì sao registry không chặn được chỗ đó.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Dữ liệu consumer sai âm thầm | Schema đổi không qua registry | audit: % topic có schema | §2.4 |
| Consumer mới vỡ sau deploy producer | Backward-compat vi phạm | registry check log | §2.4 |
| Metadata mỗi team mỗi kiểu | Không có envelope chuẩn | adopt CloudEvents | §2.3 |
| Doc topic cũ rạc | Doc viết tay | AsyncAPI sinh doc | §2.2 |
| Idempotency xử lý không nhất quán | id semantics lệch | chuẩn hoá qua envelope | §4.8 |

---

## 6. Cách đo

```bash
# Registry: liệt kê topic có/không schema
#   (Confluent: kafka-schema-registry REST; buf: buf registry ls)

# Trên wire: schema version thực tế đang bay (confluent wire format header 0-5 bytes)
kcat -C -t orders -o -5 -e | head    # 5 message cuối — xem structure thật

# Contract test async: phát golden fixture vào topic test, chạy consumer staging
```

Nguyên tắc: **đếm topic không có schema như đếm endpoint không có OpenAPI** — con số đó là nợ kỹ thuật có thể trả lời bằng một query registry.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay registry tự host:** git + CI check (schema là file YAML trong repo — nhỏ mà đủ) — hợp org nhỏ; registry service đáng khi nhiều team + nhiều runtime. **Thay CloudEvents:** envelope tự thiết kế — chỉ khi đã có chuẩn nội bộ thật sự tốt (đừng phát minh lại kém hơn).

Năm thấu kính:
- **Kinh tế:** Một breaking schema lọt = giờ debug dữ liệu lan (ngày–tuần) so với chi phí registry (một tuần setup) — bất cân xứng rõ ràng.
- **Vận hành:** Schema cooldown nên bằng **vận tốc deploy chậm nhất của consumer** — đo, đừng đoán (SLA deploy từng team).
- **An ninh:** Event chứa PII cần tagging trong schema (field phân loại) — chính sách che/định tuyến về sau dựa vào đó (→10.6).
- **Lịch sử:** REST học bài này sớm (OpenAPI/contract test); thế giới event chậm hơn 5 năm — đang lặp lại đúng thứ tự, với công cụ tốt hơn.
- **Người dùng:** Người dùng không thấy schema — họ thấy "thông báo đến khi nó còn đúng" (đơn huỷ nhưng vẫn ship vì event sai format). Chương này là lớp phòng against loại sự cố khó truy ấy.

---

## 8. Đọc tiếp & bài tập

- Queue/Kafka vận hành: **5.7** · Outbox: **5.15** · Idempotency: **4.8** · Event-driven AI: **12.5**
- **Bài tập 1:** Đếm topic/queue đang chạy: bao nhiêu % có schema trong registry? Con số dưới 50% là bản đồ việc cần làm quý này.
- **Bài tập 2:** Chọn 1 topic quan trọng: thử đổi schema (thêm field OK, xoá field) qua CI — registry chặn cái gì, cho cái gì? Ghi lại làm training team.
- **Bài tập 3:** Đề xuất envelope CloudEvents cho 1 topic có nhiều consumer — đếm dòng code mỗi consumer tiết kiệm được (parse id/time/type riêng lẻ).
