# 4.4 — RPC Nhị phân: gRPC, ConnectRPC & Protobuf

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** p5-ch29-contracts.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 3.10 (chín trạm) · 4.3.

**Sợi chỉ đỏ:** *Nội bộ cần RPC hiệu năng và streaming — gRPC/protobuf đáng thêm một giao thức không?* — trả lời: nội bộ service gọi service thì protobuf nhỏ hơn JSON và có luật tiến hoá chặt, bốn kiểu call phủ đủ unary + streaming; ConnectRPC cho phép cùng hợp đồng chạy cả gRPC lẫn HTTP JSON — đáng thêm một giao thức, với điều kiện deadline phải lan truyền theo chuỗi gọi. Câu hỏi để lại cho chương sau: *Mỗi client cần một mẩu dữ liệu khác nhau — GraphQL có giải hay có thêm vấn đề?*

**Thuật ngữ sẽ gặp:** *protobuf* — schema nhị phân + luật tiến hoá: thêm trường được, đổi số trường là chết người; *4 kiểu call* — unary, server-streaming, client-streaming, bidi; *deadline lan truyền* — thời hạn của request gốc chia xuống từng hop, hết hạn thì huỷ cả chuỗi; *ConnectRPC* — gRPC "thoải mái hơn": chạy được trên HTTP/1.1 và curl được; *codegen* — sinh client/server từ schema: hết gõ tay hai đầu; *mục KHÔNG dùng* — công khai cho đối tác hay team không có tooling: chương có hẳn một mục.

**Ví dụ mở đầu:** Pipeline gợi ý món của DM gọi 4 service nối nhau, mỗi hop qua lại JSON. Đổi sang protobuf: gói nhỏ hẳn, parse rẻ hơn, stream tiến trình từng phần về client. Nhưng lần đầu deploy quên deadline — một service cuối chậm thì cả chuỗi treo tới timeout của client, không ai tự huỷ. Chương này cho cả bài học lẫn cái giá của nó.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | gRPC hay ConnectRPC cho đường nội bộ | Tôi cần streaming + đầy đủ hay "gRPC đơn giản hơn cho browser/curl"? |
| 2 | Đặt field number & reserved đúng cách | Tôi có thể gỡ field sau này mà không vỡ (reserved)? |
| 3 | Compatibility mode: backward/forward/full | Đường sự kiện: ai nâng cấp trước? |
| 4 | Deadline & retry policy ở service config (không phải code rải) | Timeout có truyền xuyên không (→3.10)? |

---

## 2. Cơ chế

### 2.1 Protobuf: schema nhị phân + luật tiến hoá

`.proto` mô tả message; biên dịch sinh typed code mọi ngôn ngữ (→3.9 giảm bẫy biên). Nhị phân nhỏ + parse nhanh hơn JSON ~2–5× (I). Luật tiến hoá: **thêm field** an toàn (cũ đọc mới bỏ qua — forward); **gỡ field phải `reserved`** số (tái dùng số = thảm hoạ âm thầm); đổi type/field number = breaking. Đây là "versioning miễn phí" — thứ JSON không có sẵn (→4.7 schema registry bù).

### 2.2 gRPC: HTTP/2 + protobuf + 4 kiểu call

Unary (request-response), **server-streaming**, client-streaming, bidi-stream. Trên HTTP/2: mỗi call là stream (→4.2); header mang metadata. Điểm mạnh vận hành: **deadline truyền tự động** (`grpc-timeout` header — cascading cancel đúng — →3.10), interceptor (auth/log/rate-limit đồng loạt), load balancing builtin (client-side LB qua xDS). Điểm yếu: browser cần grpc-web proxy; debug cần grpcurl (không curl được); đòi HTTP/2 xuyên suốt (LB phải hỗ trợ — →2.6/9.4).

### 2.3 ConnectRPC (2022+): gRPC "thoải mái hơn"

Cùng protobuf + service definition, nhưng: unary hỗ trợ **HTTP/1.1 + JSON** (curl/debug dễ, browser native, không cần proxy) và vẫn nói gRPC/HTTP2 khi có thể. Giá trị thật: **một stack, ba chế độ** — nội bộ gRPC nhanh, công khai JSON dễ, công cụ chung. Adoption: Buf ecosystem (buf CLI thay protoc + manage registry). Khi nào chọn: team muốn protobuf nhưng không muốn trả chi phí vận hành gRPC chuẩn đầy đủ.

### 2.4 Vận hành gRPC production

- **Deadline bắt buộc** — không có mặc định! (call không deadline = công việc mồ côi — →3.10);
- Retry policy (cấu hình service, có hedging cho read-đắt) — cẩn thận bão retry (→8.5);
- **Message size limit** (mặc định 4 MB) — lớn hơn thì stream theo chunk, không nâng mù;
- Load balancing: client-side (headless service K8s) hoặc L7 proxy (Envoy — →9.4); conn không tự cân lại như HTTP/1 pool;
- Observability: interceptor + OpenTelemetry (span tự nhiên theo call).

### 2.5 Khi nào KHÔNG dùng gRPC

API công khai cho bên ngoài (JSON/OpenAPI dễ tiêu thụ — →4.3); CRUD thấp tần (lợi gRPC nhỏ hơn chi phí học); team debugging-by-curl culture; cần cache HTTP (gRPC bỏ cache header ngữ nghĩa — proxy khó). **Không dùng gRPC vì "nó hiện đại"** — dùng vì deadline-streaming-schema là vấn đề thật của bạn.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Protobuf vs JSON | ~2–5× parse/nhỏ hơn | I | payload vừa |
| gRPC message limit mặc định | 4 MB | V | nâng có chủ đích |
| Connect unary | HTTP/1.1 + JSON hoặc gRPC/H2 | V | cùng proto |
| Deadline | không mặc định — phải đặt | V | →3.10 |

---

## 4. Suy luận kiến trúc

- **S1:** RPC nhị phân đổi **công cụ quen (curl, log văn bản)** lấy schema chặt + deadline lan truyền + throughput — hợp nội bộ sâu, kém hợp biên công khai.
- **S2:** Tham số trụ: deadline vi phạm/s, retry nhân lúc sự cố (→8.5), message size p99, stream duration.
- **S3:** Connect đổi "đầy đủ gRPC" lấy tiện browser/ops; buf registry đổi git-ops proto riêng; mỗi mức hợp một quy mô team.
- **S4:** Hạ tầng (Envoy/xDS, service mesh) nói gRPC gốc — gRPC nội bộ cộng hưởng với platform; JSON công khai cộng hưởng với hệ sinh thái client ngoài.
- **S5:** Streaming AI (token stream) kéo gRPC/SSE vào vị trí trung tâm (→12.2) — kỹ năng streaming RPC từ "nâng cao" thành "cơ bản" của backend 2026.
- **S6:** Khi gRPC "chậm": thường là LB/connection tái dùng sai hoặc payload lớn — không phải protocol; đo trước khi đổi stack.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Tải không đều qua pod | Client-side LB không bật | grpc metrics per backend | §2.4 |
| Bão request lúc dependency chậm | Không deadline/retry policy | audit config | §2.4 |
| Sập sau khi "dọn field" | Tái dùng field number | protobuf lint (buf) | §2.1 |
| Gọi qua LB bị "unsupported" | LB không HTTP/2 upstream | đổi ingress/cấu hình | §2.2 |
| Stream nghẽn không chảy | Message lớn + window (→1.7 BDP) | chunk; window setting | §2.4 |

---

## 6. Cách đo

```bash
# Gọi thủ (không cần app client)
grpcurl -plaintext -d '{"id":"1"}' svc:9090 my.Package/GetUser

# Lint + phá vỡ schema (buf)
buf lint; buf breaking --against '.git#branch=main'

# Xem thật stream trên wire
nghttp -v https://grpc-svc:443   # thấy HTTP/2 frames

# Metrics chuẩn gRPC: grpc_server_handled_total theo code
#   deadline exceeded cao = tầng dưới chậm (→3.10 span)
```

Nguyên tắc: **`buf breaking` trong CI là cửa ải** — field number tái dùng và xoá field chỉ nên chết ở PR, không chết ở production.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay gRPC nội bộ:** REST+OpenAPI (→4.3) đủ cho đa số + tool quen; JSON + messagepack bù 1 nửa khoảng cách serialize. **Thay protobuf:** Avro (hệ sự kiện — →4.7), Thrift (di sản). **Giữ JSON nhưng muốn deadline lan truyền:** header `deadline` tự quy ước + middleware — 80% lợi ích, 20% công.

Năm thấu kính:
- **Kinh tế:** gRPC đáng ở **cặp service gọi dày + cần streaming** — ở đó 2–5× serialize + deadline lan = tiền máy và sự cố thật; còn lại là chi phí học.
- **Vận hành:** Proto nên version control chung (registry) — "proto trong repo riêng không ai review" là nơi breaking change sinh con.
- **An ninh:** Protobuf parse an toàn hơn JSON (không eval, size rõ) nhưng **không tự validate logic** (required type ≠ hợp lệ nghiệp vụ) — validate nghiệp vụ vẫn phải có.
- **Lịch sử:** CORBA/DCE từng hứa "RPC đa ngôn ngữ" và chết vì phức tạp; gRPC thắng bằng đứng trên HTTP/2 + protobuf đơn giản hơn — bài học: RPC sống khi nó là *mỏng*, không phải khi nó là *nền tảng*.
- **Người dùng:** Người dùng không biết unary hay streaming — nhưng họ biết "chat trả lời từng chữ" (stream) và "đặt hàng không treo 30 giây" (deadline). Chương này là hai trải nghiệm đó.

---

## 8. Đọc tiếp & bài tập

- REST/OpenAPI: **4.3** · AsyncAPI/Avro: **4.7** · Deadline budget: **3.10** · Token streaming: **12.2** · Mesh: **9.4**
- **Bài tập 1:** Audit mọi gRPC call của một service: có deadline không? Retry policy gì? Mỗi call thiếu deadline là mồ côi tương lai — liệt kê.
- **Bài tập 2:** Chạy `buf breaking` trên repo proto của bạn. Kết quả bất ngờ thường xuất hiện trong 5 phút đầu.
- **Bài tập 3:** Viết 1 server-streaming endpoint đơn giản (log tail); đo qua grpcurl + nghttp — cảm nhận frame HTTP/2 thật, vì lần tới bạn sẽ cần nó cho token stream (→12.2).
