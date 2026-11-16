# 8.3 — Giao dịch Phân tán, Saga, Outbox & "Exactly-Once"

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** lý thuyết vận hành hoá · **Động từ liên quan:** Chọn · Thiết kế
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.15 (outbox đã gặp) · 5.7 (offset, at-least-once).

**Sợi chỉ đỏ:** *Một giao dịch chạm nhiều service — saga và outbox thay 2PC thế nào?* — trả lời: giao dịch chạm nhiều service thì ACID một máy không còn — 2PC gần như không dùng trong thực tế; outbox biến "ghi DB và phát sự kiện" thành một transaction; saga thay rollback bằng chuỗi bước có "phản đề" (compensation); còn exactly-once thật ra là at-least-once cộng idempotency. Câu hỏi để lại cho chương sau: *Một DB không còn đủ — sharding và replication chia dữ liệu sao cho đều và sống?*

**Thuật ngữ sẽ gặp:** *outbox* — ghi sự kiện vào bảng, trong cùng transaction với dữ liệu: một viên gạch (5.15 đã gặp); *saga* — chuỗi bước địa phương, mỗi bước có bước hoàn tác: rollback nghiệp vụ thay vì rollback kỹ thuật; *compensation* — "phản đề": huỷ đơn, hoàn tiền — là nghiệp vụ, không phải UNDO; *2PC/XA* — khoá chéo chờ nhau: vì sao gần như chỉ còn trong sách; *orchestration vs choreography* — có đạo diễn trung tâm hay múa theo sự kiện: hai kiểu dàn saga; *exactly-once* — hiệu ứng-một-lần = at-least-once + idempotency (4.8): chương giải mê cung thuật ngữ này.

**Ví dụ mở đầu:** Đặt món DM chạm đơn hàng, kho, thanh toán, ship: hai cái thành công, một cái hỏng — "hoặc cả bốn hoặc không cái nào" không còn tồn tại. Saga cho mỗi bước một phản đề: kho trừ hụt thì phản đề cộng lại, thanh toán fail thì huỷ đơn. Chương này kết thúc bằng sơ đồ quyết định nhanh cho từng tổ hợp thực tế.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Giao dịch xuyên service: 2PC / Saga / Outbox / tránh hẳn | Hai hệ phải đổi cùng lúc — ai "đảm bảo", bằng cơ chế nào? |
| 2 | Nếu Saga: choreography hay orchestration | Tôi có cần nhìn thấy toàn bộ luồng ở một chỗ không? |
| 3 | Isolation của Saga (bức màn giữa các bước) | Nghiệp vụ dở dang — người khác đọc thấy gì? |
| 4 | "Exactly-once" tôi hứa với ai, thật ra là gì | Đích đến là at-least-once + idempotency — tôi đã ghi rõ chưa? |

---

## 2. Cơ chế

### 2.1 Vấn đề gốc: hai hệ, một "hoặc là cả hai"

Đơn hàng ghi vào DB **và** sự kiện lên Kafka **cùng lúc** — không có giao dịch chéo hai hệ (DB commit xong, process chết trước khi publish → đơn "ma" không có sự kiện; ngược lại → sự kiện ma). Mọi mẫu trong chương này là biến thể của việc đối phó câu đó.

### 2.2 2PC/XA — vì sao gần như không dùng

Coordinator hỏi mọi người "chuẩn bị?" rồi "commit!" — chặn khoá chờ; **coordinator chết giữa hai pha = mọi participant khoá treo không biết kết cục** (blocking, vi phạm tính sẵn sàng — bài toán 8.1/FLP hiện hình). XA driver chậm (đã đo chậm hơn nhiều lần so với giao dịch thường (I)) và ops khó. Vùng dùng được: bên trong một DB phân tán (họ Cockroach/Spanner làm "2PC cải tiến + đồng thuận" — nhưng đó là DB, không phải kiến trúc ứng dụng); ở tầng ứng dụng: gần như luôn chọn Saga/Outbox.

### 2.3 Outbox — viên gạch đầu tiên

```
BEGIN
  INSERT orders ...;          -- nghiệp vụ
  INSERT outbox (event) ...;  -- cùng giao dịch!
COMMIT
-- riêng: relay/publisher (Debezium CDC hoặc poller) đọc outbox → publish Kafka
--   → delete/đánh dấu đã gửi
```

Đảm bảo: nghiệp vụ và sự kiện **nguyên tử** (cùng DB transaction — →5.15 đã gặp ở tầng dữ liệu); publisher dừng bao lâu thì outbox phình, chạy lại là tiếp — **at-least-once**. Đây là mẫu nền: mọi kiến trúc "kết quả nhất quán qua service" dựng trên nó.

### 2.4 Saga — chuỗi bước, mỗi bước có "phản đề"

Một nghiệp vụ dài = chuỗi giao dịch cục bộ; mỗi bước xuất **sự kiện/kịch bản ngược (compensation)**: đặt hàng → trừ tồn kho → trừ tiền. Thất bại ở trừ tiền → **hoàn tồn kho** (compensate). Hai dạng:
- **Choreography:** mỗi service nghe sự kiện, làm việc, phát sự kiện tiếp — không ai nhìn toàn cục; 4–5 bước trở lên là "mèn đén bể" khó hiểu;
- **Orchestration:** một orchestrator (state machine — Temporal/Camunda-style hoặc tự viết) gọi từng bước, giữ trạng thái, quyết định rollback — nhìn được, đo được, và là một điểm phải highly available.

Bất biến phải nhớ: **Saga không có isolation** (bước giữa nhìn thấy trạng thái dở dang của nhau — "anomaly" A1–A3 theo tài liệu kinh điển): đối phó bằng **semantic lock** (cột trạng thái "PENDING" — người khác đọc thấy và né), **commutative update** (thao tác hoán đổi được), hoặc **snapshot/đọc phiên bản**.

### 2.5 "Exactly-once" — giải mê cung thuật ngữ

Không máy nào đảm bảo delivered exactly once trên mạng có lỗi (tin nhắn hoặc tới hoặc mất hoặc trùng — phải chọn). Chuỗi chuẩn: **at-least-once + idempotent consumer = hiệu ứng exactly-once**:
- Mỗi lệnh/sự kiện có **id duy nhất** (UUID/event id);
- Consumer lưu id đã xử lý (hoặc khóa unique constraint) — xử lý lần 2 là no-op;
- Kafka "exactly-once" (transactional producer + read-process-write trong txn) chính là gói này ở tầng broker (→5.7) — vẫn yêu cầu **đầu ra** idempotent nếu đích là hệ ngoài.

Đặt tên đúng trong hợp đồng nội bộ: hứa "idempotent theo event id" — không hứa "exactly once" (hứa thứ không tồn tại là nợ pháp lý kỹ thuật).

### 2.6 Sơ đồ quyết định nhanh

```
Cùng một DB?                     → transaction thường (đừng phân tán hóa vấn đề)
2 hệ, 1 chiều, chấp nhận trễ?    → outbox + at-least-once + idempotent consumer
Nhiều bước, có hoàn tác nghiệp vụ? → saga (orchestrator nếu >4 bước hoặc cần audit)
Cần "mọi hay không có gì" chặt?  → tái thiết để cùng DB; nếu thật không được: 2PC cải tiến (DB phân tán)
```

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Outbox lag | ms–s (poller) / sub-s (CDC) | I | →5.15 |
| XA penalty | chậm rõ rệt so với tx thường | I | đo trong benchmark |
| Saga step hợp lý | 2–6 bước | P | hơn = mùi thiết kế |
| Kafka EOS | transactional producer (→5.7) | V | broker-scope |

---

## 4. Suy luận kiến trúc

- **S1:** Đừng phân tán giao dịch **trước khi cần**: hợp nhất DB/schema (→5.14) là giải "distributed transaction" rẻ nhất; mỗi ranh giới service tạo ra là một saga tương lai.
- **S2:** Tham số trụ: outbox lag p95, số compensation chạy/giờ (tỉ lệ thất bại nghiệp vụ), số event trùng lặp bị idempotency chặn (bằng chứng cơ chế sống).
- **S3:** Orchestrator đổi "trung tâm dễ debug" lấy một thành phần HA phải nuôi (state, version, upgrade); choreography đổi autonomy lấy vô hình — chọn theo số bước và mức cần audit.
- **S4:** Idempotency là **hợp đồng API** (→4.8) không phải chi tiết cài đặt — viết vào OpenAPI/AsyncAPI: id ở đâu, trong bao lâu nhớ, chạy lại trả gì.
- **S5:** Workflow engine (Temporal-style) đang trở thành "DB của nghiệp vụ dài" — code nghiệp vụ viết như hàm, engine lo retry/state/timeout; biên giới "orchestrator tự viết vs engine" quyết định theo số luồng dài và độ phức tạp compensation.
- **S6:** Khi "có đơn không có sự kiện" (hoặc ngược lại): tra đúng nhánh sơ đồ §2.6 — nếu kiến trúc không outbox thì đó là lỗi thiết kế, không phải bug code: thêm retry không vá được "hai ghi không nguyên tử".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Đơn có, downstream không biết | Commit + publish không nguyên tử | cài outbox | §2.3 |
| Sự kiện trùng gây đôi kê | Consumer không idempotent | audit id dedupe | §2.5 |
| Saga "kẹt giữa" vĩnh viễn | Compensation thiếu/timeout không có | state machine audit | §2.4 |
| Nghiệp vụ dở bị người đọc | Không semantic lock | cột trạng thái PENDING | §2.4 |
| 2PC treo participant | Coordinator chết giữa pha | tránh 2PC app-level | §2.2 |
| Outbox phình to | Relay chết/lag | alert kích thước outbox | §2.3 |

---

## 6. Cách đo

```sql
-- Sức khoẻ outbox (cùng DB nghiệp vụ):
-- SELECT count(*), max(now()-created_at) FROM outbox WHERE sent_at IS NULL;
--   (alert: count tăng tuyến tính hoặc age > 1 phút)

-- Idempotency thật: bơm sự kiện trùng (sao chép 1 event) vào consumer ở staging
--   — downstream có sinh đôi bản ghi không? Sinh đôi = hợp đồng idempotency chưa chạy
```

Nguyên tắc: **sự cố saga/outbox là sự cố dữ liệu chậm/chồng** — đo bằng hai con số (lag, trùng lặp bị chặn) trước khi cần; sau đó chỉ tra nhánh.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay outbox:** bảng "pending" + cron (mộc mạc, chậm hơn CDC — đủ cho nhiều hệ); **thay saga:** đồng bộ hoá lại thành một service/DB (→8.6 — thường là câu trả lời đúng sau khi đếm chi phí); **thay orchestrator:** state trong DB + worker — tự viết state machine nhỏ khi chỉ 1–2 luồng.

Năm thấu kính:
- **Kinh tế:** Chi phí 2PC = độ trễ + rủi ro treo; chi phí saga = code compensation + ops orchestrator; chi phí "cùng DB" = bỏ ranh giới team — thường cái cuối rẻ nhất nhưng đắt về chính trị tổ chức.
- **Vận hành:** Saga chạy tuần lễ (duyệt, chờ thanh toán) — cần dashboard "đang ở bước nào bao nhiêu đơn" — không có dashboard là không vận hành được nghiệp vụ dài.
- **An ninh:** Sự kiện đi qua hệ trung gian (broker) — dữ liệu nhạy cần field-level mã hoá/giả danh hoá (→5.13) + ACL topic; id idempotency là dữ liệu PII-lite cần retention policy.
- **Lịch sử:** CICS/2PC thập niên 70–80 (mainframe, khóa chặt) → SOA/WS-* chuẩn hoá compensation (2000s) → microservices + event (2010s) + outbox/CDC phổ quát (2020s): vòng lặp "chặt↔lỏng" y như 7.1; mỗi vòng mở rộng được nhờ hạ tầng giám sát tốt hơn.
- **Người dùng:** Người dùng chỉ hỏi một câu: "tôi bị trừ tiền mà không có đơn thì sao?" — chương này là 30 năm kỹ thuật trả lời câu hỏi đó; nếu hệ của bạn trả lời được bằng cơ chế (không phải bằng "hiếm khi") thì đã xong.

---

## 8. Đọc tiếp & bài tập

- Outbox/CDC ở tầng dữ liệu: **5.15** · Kafka transactional: **5.7** · Idempotency hợp đồng: **4.8** · Ranh giới service: **8.6** · Data platform saga: **5.12**
- **Bài tập 1:** Vẽ mọi cặp "hai ghi phải đi cùng" trong hệ thống bạn. Mỗi cặp: outbox? 2PC? trộm chờ may? — đánh dấu cặp chưa có gì = nơi sự cố chưa bung.
- **Bài tập 2:** Ở staging, bơng trùng một sự kiện vào consumer chính (§6). Nếu downstream sinh đôi bản ghi — idempotency của bạn là tài liệu, không phải cơ chế.
- **Bài tập 3:** Với saga dài nhất của bạn: viết ra bảng các bước + compensation tương ứng. Ô nào trống (không hoàn tác được) — đó là rủi ro nghiệp vụ chưa ai ký duyệt.
