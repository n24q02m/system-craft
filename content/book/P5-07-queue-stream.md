# 5.7 — Event Log, Stream & Queue: Kafka vs RabbitMQ vs NATS

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** ds-21-search-queue.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 4.8 (idempotency) · 4.7 (hợp đồng sự kiện).

**Sợi chỉ đỏ:** *Các bước xử lý đơn cần bốc xếp đáng tin — stream kiểu Kafka khác queue thường chỗ nào?* — trả lời: queue thường hoàn thành là xoá; stream/log giữ lại theo thời gian — replay được và nhiều consumer độc lập đọc cùng lịch sử; thiết kế số một là partition: thứ tự chỉ giữ trong partition; Kafka hiện đại thêm KRaft, share groups, tiered storage. Câu hỏi để lại cho chương sau: *Chủ chuỗi muốn báo cáo tháng — OLAP khác gì DB giao dịch, nhanh hơn ở đâu?*

**Thuật ngữ sẽ gặp:** *queue vs log* — xoá sau ack, hay giữ để tua lại: hai ngữ nghĩa gốc; *partition* — đơn vị song song: có thứ tự trong partition, không có thứ tự giữa chúng; *consumer group* — nhóm chia nhau partition, mỗi nhóm một offset riêng; *rebalance* — chia lại khi consumer chết: làm sai là bão; *poison message* — tin làm consumer sập lặp vô hạn: phải có DLQ; *RabbitMQ 4.x* — hàng đợi cạnh tranh trưởng thành: chỗ dùng khác Kafka.

**Ví dụ mở đầu:** Bốc xếp đơn của DM: xác nhận, đóng gói, giao — mỗi bước cần tin đáng tin: mất tin hoặc xử lý hai lần đều mất tiền. Queue thường xoá sau ack: sửa logic xong muốn xử lý lại thì hết dữ liệu. Stream giữ lịch sử: tua lại từ offset cũ. Chương này tách ba họ (queue, log, subject) và chỉ chỗ nào dùng họ nào.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Queue (RabbitMQ) hay log (Kafka) cho bài toán này | Cần "xử lý xong xoá" hay cần "replay/history"? |
| 2 | Partition & consumer group thiết kế | Bao nhiêu partition — theo throughput hay theo thứ tự? |
| 3 | Delivery semantic: at-most/at-least/exactly-once | Tôi chịu lặp thế nào — và đã idempotent (→4.8) chưa? |
| 4 | DLQ + retry policy + poison message xử lý | Message hỏng đi đâu — ai nhìn? |

---

## 2. Cơ chế

### 2.1 Ba họ: queue, log, subject — ba ngữ nghĩa khác nhau

| Họ | Đại diện | Mô hình | Đặc trưng |
|---|---|---|---|
| **Queue truyền thống** | RabbitMQ (4.4.0 — verify) | đẩy tới consumer, xử lý xong xoá | routing phong phú, độ trễ ~µs–ms |
| **Distributed log** | Kafka (4.4.0 — verify) | append-only theo partition, consumer giữ offset | replay, retention ngày–năm, throughput MB/s–GB/s |
| **Subject-based** | NATS/JetStream | pub/sub theo subject tree, at-most-one mặc định | siêu nhẹ, microservices request/reply |

**Quy tắc chọn:** cần replay + nhiều consumer độc lập + retention → Kafka; cần routing phức tạp + độ trễ thấp + "xử lý xong là hết" → RabbitMQ; cần mesh nhẹ + đơn giản ops → NATS. Đừng dùng Kafka làm "queue công việc có thứ tự đơn giản" (trả bằng ops phức tạp) — cũng đừng đòi RabbitMQ replay 7 ngày (không phải thiết kế của nó).

### 2.2 Kafka hiện đại: KRaft, share groups, tiered storage

- **KRaft** (RAFT metadata — hết ZooKeeper từ 4.0): đơn giản hoá deploy thật;
- **Kafka 4.4 (10/2026, verify):** KIP-1191 — **DLQ cho share groups** (share.version 2), KIP-892 transactional state stores cho Streams, deprecate broker.id — thế hệ "queue-semantics trên log" đang khép khoảng cách với RabbitMQ;
- **Tiered storage:** dữ liệu lạnh đẩy S3 — cluster local nhỏ, retention dài giá rẻ (đường chuẩn 2026 cho log-heavy).

### 2.3 Partition & ordering — thiết kế số một

- Thứ tự chỉ đảm bảo **trong 1 partition**; partition = đơn vị song song consumer;
- `partition = hash(key) % N` — cùng key một partition (đúng cho "cùng đơn hàng theo thứ tự");
- Nhiều partition = nhiều file seg + nhiều consumer + rebalance phức tạp hơn; **đừng đặt 200 partition cho 1k msg/s** (mỗi partition tốn memory/FH);
- Repartition (đổi key/N) = mất thứ tự cục bộ trong cửa sổ chuyển — nâng cấp có kế hoạch.

**Hot partition:** key thiên lệch ("tenant lớn" — như →5.5) → một consumer đói, số kia rảnh. Thuốc: salt key (kèm bảng tạm) hoặc tách topic theo tenant lớn.

### 2.4 Consumer: offset, rebalance, poison

- Offset commit: **at-least-once** mặc định (commit sau xử lý — lặp khi crash); at-most-once (commit trước — mất khi crash); "exactly-once" Kafka = transaction producer + commit nguyên tử (chỉ trong hệ Kafka: Streams/transactional API);
- **Rebalance** (consumer rời/vào): stop-the-world nhóm (KIP-848 static membership + cooperative rebalance giảm đau); triệu chứng "cả group khựng vài giây định kỳ" thường là rebalance do session timeout < thời gian xử lý;
- **Poison message:** một message làm consumer crash → lặp crash loop. Bắt buộc: try/catch + **DLQ** (topic -dlq) + alert + dashboard DLQ — không DLQ = bom nổ chậm (triệu chứng "consumer chết lặp liên tục").

### 2.5 RabbitMQ 4.x vận hành

Quorum queue (RAFT — thay mirror cổ), classic queue v2 (đỡ memory), **streams** (thêm replay kiểu Kafka) + plugin federation/shovel cho geo. Bẫy: prefetch quá cao làm message dồn 1 consumer (đói hàng xóm); unacked full → flow control block toàn connection.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Kafka / RabbitMQ | 4.4.0 / 4.4.0 (10/2026) | V | versions.csv |
| Latency: RabbitMQ vs Kafka | ms vs ~ms–chục ms | I | theo cấu hình |
| Throughput Kafka | MB/s–GB/s cluster | I | |
| Partition & thứ tự | trong partition | V | |
| DLQ | bắt buộc thiết kế | P | §2.4 |

---

## 4. Suy luận kiến trúc

- **S1:** Log vs queue là **quyết định ngữ nghĩa dữ liệu** (history có giá trị không?) — không phải "cái nào hot hơn"; đổi giữa hai cái là migration dữ liệu thật.
- **S2:** Tham số trụ: consumer lag (theo partition — quan trọng nhất), rebalance/s, DLQ depth, ISR/under-replicated, publish latency.
- **S3:** Partition nhiều đổi song song lấy chi phí metadata/rebalance; retention dài đổi tiền lưu trữ; tiered đổi độ trễ đọc lạnh lấy giá rẻ.
- **S4:** Kafka đang nuốt semantics queue (share groups + DLQ — 4.4) và storage (tiered/S3) — hợp nhất hai thế giới; theo dõi thay vì đặt cược ngược.
- **S5:** Event-driven AI (agent trace, pipeline dữ liệu RAG — →12.x) tiêu thụ replay log: "log là nguồn chân lý của dữ liệu AI" đang thành pattern chuẩn (→5.9 lakehouse từ log).
- **S6:** Khi consumer "chậm": lag vì throughput thiếu (scale partition/consumer), rebalance gián đoạn, hay poison loop — ba dạng ba số ba thuốc.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Consumer lag tăng đều | Throughput < producer | lag trend; partition throughput | §2.3 |
| Cả group khựng định kỳ | Rebalance (session < xử lý) | group metric; log member | §2.4 |
| Consumer chết lặp liên tục | Poison message | consumer log; DLQ chưa có? | §2.4 |
| Một consumer đói, số rảnh | Hot partition | per-partition lag | §2.3 |
| Disk đầy | Retention + tiered chưa bật | log retention | §2.2 |
| Message lặp xử lý | At-least-once + chưa idempotent | audit idempotency (→4.8) | §2.4 |

---

## 6. Cách đo

```bash
# Kafka — lag theo partition (con số số một)
kafka-consumer-groups --bootstrap-server :9092 --describe --group orders

# Under-replicated (sức khỏe cluster)
kafka-topics --describe --topic orders | grep -E 'Partition|Isr'

# RabbitMQ — hàng đợi + unacked
rabbitmqctl list_queues name messages consumers

# Consumer thật: đo "độ tuổi message khi xử lý" (event time vs process time)
#   — cao hơn lag thô vì có cả thời gian nằm chờ
```

Nguyên tắc: **consumer lag là "nhiệt độ" của mọi hệ event-driven** — dashboard đầu tiên, alert đầu tiên; mọi thứ khác là chẩn phân tích.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Kafka cho log:** NATS JetStream (nhẹ hơn nhiều ops), Redpanda (protocol tương thích, C++ single binary — đổi xác thực hệ sinh thái), cloud managed (MSK/Confluent — đổi tiền lấy ops). **Thay cho queue công việc:** SQS/Cloud Tasks (managed, đổi vendor), Redis Streams (đã có Redis — →5.4). **Thay streaming processing:** Flink (→5.12) trên log đã có.

Năm thấu kính:
- **Kinh tế:** Cluster Kafka tự vận hành = 3–5 máy + người biết nó sâu; managed đổi bill trong suốt cho ngân sách đo được — decision theo TCO (→11.3) không theo đam mê.
- **Vận hành:** Bảng "partition plan" cho từng topic (số, key, retention, DLQ) là tài liệu kiến trúc đáng giá ngang diagram.
- **An ninh:** Message chứa PII qua topic chung = dữ liệu nhân bản khó xoá (GDPR — →5.13); cân nhắc pseudonym hoá trước khi publish.
- **Lịch sử:** Kafka sinh ra từ LinkedIn pipeline (2011); 15 năm sau nó là "xương sống dữ liệu" của ngành — và đang tự tái cấu trúc (KRaft, share groups) để nuốt việc của hàng xóm: bài học về ranh giới sản phẩm di chuyển.
- **Người dùng:** Người dùng thấy "đơn đặt rồi trạng thái nhảy dần theo bước" (event flowing) — hoặc "tất cả đứng im lúc Black Friday" (lag băng). Chương này là hai hình ảnh đó.

---

## 8. Đọc tiếp & bài tập

- Stream processing: **5.12** · Schema/registry: **4.7** · Outbox/CDC: **5.15** · Idempotency: **4.8** · Sizing: **5.16**
- **Bài tập 1:** Đo consumer lag của 3 group quan trọng nhất — theo partition, không tổng. Partition lệch > 10× = hot key đang hình thành.
- **Bài tập 2:** Mô phỏng poison message (gửi JSON hỏng vào topic staging). Consumer bạn sống sót không? DLQ có message không? Alert kêu không? Ba câu trả lời là điểm trưởng thành của hệ.
- **Bài tập 3:** Lập bảng partition plan (§ vận hành) cho topic tốn tiền nhất — số partition, key, retention, tiered on/off, DLQ. Nửa giờ, giá trị mỗi quý.
