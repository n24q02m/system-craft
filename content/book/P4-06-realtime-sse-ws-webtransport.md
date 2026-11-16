# 4.6 — Thời gian thực: SSE, WebSocket & WebTransport

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.1 · 4.2.

**Sợi chỉ đỏ:** *Đơn đổi trạng thái liên tục — đẩy realtime qua SSE/WebSocket/WebTransport thế nào cho tin?* — trả lời: 90% "thời gian thực" của web thật ra chỉ cần đẩy một chiều — SSE chạy trên HTTP thường, xuyên được LB và proxy; WebSocket hai chiều nhưng đòi hạ tầng riêng; WebTransport là lựa chọn mới trên H3 cho media và game. Câu hỏi để lại cho chương sau: *Sự kiện bên trong tổ chức (đơn mới, ship, hoàn) mô tả và khớp nối thế nào — AsyncAPI, CloudEvents?*

**Thuật ngữ sẽ gặp:** *SSE* — stream một chiều qua HTTP: reconnect và Last-Event-ID có sẵn trong chuẩn; *WebSocket* — kênh hai chiều sau khi bắt tay Upgrade: cần sticky và tường lửa mở; *heartbeat* — ping/pong phát hiện kết nối chết trước khi khách phát hiện; *reconnect + backoff* — client tự nối lại với khoảng chờ tăng dần để không tạo bão; *sticky session* — ghim connection vào một server: cái giá hạ tầng thật của WS; *WebTransport* — kênh không tin cậy, đa stream trên HTTP/3.

**Ví dụ mở đầu:** Bản đồ shipper của DM cập nhật vị trí mỗi vài giây: dữ liệu chảy một chiều từ server ra. Bản đầu dùng WebSocket vì "thời gian thực": nuôi sticky session, tự viết reconnect, đêm deploy gánh bão kết nối. Đổi sang SSE: qua LB thường, reconnect có sẵn, code đi một nửa. Bài học: chọn kênh theo bài toán, không theo từ nghe sang.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | SSE hay WebSocket cho luồng một chiều | Tôi cần client→server thường xuyên không, hay chỉ server→client? |
| 2 | WebTransport/WebRTC khi nào | Cần latency thấp + datagram + unordered (game/media)? |
| 3 | Kết nối dài qua hạ tầng: LB idle timeout, proxy buffering | Mọi hop đã cho stream chảy chưa (định kỳ ping)? |
| 4 | Trạng thái kết nối & reconnect protocol | Client rớt 30 giây — bắt đầu lại từ đâu (Last-Event-ID)? |

---

## 2. Cơ chế

### 2.1 SSE: stream một chiều, 90% use case "thời gian thực" của web

`Content-Type: text/event-stream` trên HTTP thường: **server đẩy** sự kiện liên tục; client tự reconnect (built-in) với `Last-Event-ID` resume. Ưu: đi qua HTTP/1.1/2/3 nguyên vẹn, proxy/LB hiểu, authorize bằng header chuẩn, debug bằng curl (`curl -N`). Nhược: một chiều; số kết nối đồng giới hạn browser cũ (6/host trên H1 — hết hạn với H2); text overhead nhỏ.

**Bẫy số một: proxy buffering** — nginx/Envoy gom sự kiện thành cụm (client nhận mỗi vài giây). Thuốc: `X-Accel-Buffering: no` (nginx), cấu hình flush, hoặc tăng cấp hop. 2026 chú ý: OpenAPI 3.2 đã mô tả SSE chuẩn (→4.3) — hợp đồng cho stream không còn là hack.

### 2.2 WebSocket: hai chiều đầy đủ, chi phí hạ tầng thật

Upgrade HTTP→WS (`Connection: Upgrade`), sau đó là frame song song hai chiều. Hợp: chat, edit cộng tác, game — nơi client gửi thường xuyên. Chi phí: **không phải HTTP nữa** — LB idle timeout cắt (ping/pong ~30 s), LB phải sticky hoặc dùng message Broker phía sau; authorize chỉ ở handshake (token trong query/subprotocol — cẩn thận log — →10.6); scale-out cần pub/sub chung (Redis/Kafka — →5.3/5.7).

### 2.3 WebTransport (+ WebRTC cho media)

WebTransport: trên **HTTP/3/QUIC** (→4.1) — nhiều stream độc lập + **datagram** (không đảm bảo, siêu nhẹ), unordered option. Hợp: game/telemetry/điều khiển robotics — nơi datagram + migration (đổi mạng) ăn điểm. Hạn chế: cần H3 thật sự xuyên suốt, browser/edge hỗ trợ 2024+ đang mở rộng; API còn trẻ. **WebRTC** giữ vị trí media thời gian thực (audio/video, P2P) — chương 14.6 đi sâu cho game/media.

### 2.4 Bảng chọn nhanh

| Nhu cầu | Chọn | Ghi chú |
|---|---|---|
| Server đẩy (feed, log, progress, **token AI**) | **SSE** | đơn giản, HTTP nguyên vẹn |
| Chat/collab hai chiều | WebSocket | kèm pub/sub + ping |
| Vị trí/telemetry nhanh, dung sai mất | WebTransport datagram | H3 bắt buộc |
| Audio/video call | WebRTC | →14.6 |

### 2.5 Vận hành chung mọi channel dài

- **Heartbeat/idle:** dưới idle timeout của mọi hop (LB 60s → ping 25–30s);
- **Backpressure:** SSE/WS không có flow control ứng dụng — tự giới hạn queue gửi + bỏ sự kiện cũ (không dồn vô hạn — →5.7);
- **Fan-out scale:** N instance × M client = cần pub/sub backbone + (nếu to) dedicated fan-out layer (→5.4);
- **Resume protocol:** client giữ ID/generation — reconnect không mất dữ liệu, không lặp (idempotent replay — →4.8).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| SSE qua HTTP | mọi version; H2 hết giới hạn 6 conn | V | |
| Ping interval chuẩn | 25–30 s | I | < LB idle |
| WebTransport | cần HTTP/3 | V | 2024+ browsers |
| SSE overhead | ~byte/event + newline | I | nhỏ |
| Token AI stream | SSE là chuẩn de-facto (→12.2) | V | |

---

## 4. Suy luận kiến trúc

- **S1:** Channel thời gian thực là **trạng thái dài sống trên hạ tầng tưởng "stateless"** — LB/proxy/node drain đều cần kế hoạch riêng cho connection đang mở.
- **S2:** Tham số trụ: connection đồng thời mỗi node, sự kiện/s, disconnect rate, time-to-first-event sau reconnect.
- **S3:** SSE đổi đơn giản lấy một chiều; WS đổi hai chiều lấy hạ tầng; WebTransport đổi độ trẻ của stack lấy datagram/migration.
- **S4:** AI token stream (→12.2) biến SSE từ "tính năng" thành **đường máu của sản phẩm AI** — kỹ năng §2.1–2.5 giờ là core backend.
- **S5:** Deployment (rolling) với hàng trăm nghìn connection dài là bài toán riêng: connection draining + graceful handoff + client backoff có jitter (→8.5).
- **S6:** Khi stream "không chảy": đi theo hướng ngược dòng — app flush → proxy buffering → LB idle → CDN — 90% dừng ở proxy buffering.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| SSE client nhận cụm mỗi vài giây | Proxy buffering | curl -N trực tiếp vs qua proxy | §2.1 |
| WS đứt đúng chu kỳ (60s/120s) | LB idle timeout | capture ping; audit config | §2.2 |
| Reconnect = mất sự kiện | Không Last-Event-ID/resume | log sequence gap | §2.5 |
| Deploy kéo sập toàn client | Không draining + backoff | deployment runbook | §2.5 |
| Fan-out đốt CPU khi viral | Không dedicated layer | events/s mỗi node | §2.5 |

---

## 6. Cách đo

```bash
# SSE chảy thật không? (đọc thẳng, không qua proxy)
curl -N https://svc/stream   # sự kiện phải xuất hiện liên tục

# Qua proxy so sánh — nếu cụm: buffering ở hop nào (thêm header dò từng hop)

# Connection & event rate từ metric server:
#   ws_connections_gauge, sse_open_gauge, events_sent_total

# Idle timeout thật của đường:
#   mở connection, ngừng gửi, đồng hồ đến khi bị cắt — lặp cho từng hop
```

Nguyên tắc: **mỗi hop của stream phải được chứng minh bằng cách nó flush** — đừng tin config, chứng minh bằng curl từng chặng.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay stream:** polling dài kỳ (đủ cho update chậm — rẻ, cache được, không connection dài); long-poll (cổ nhưng ổn qua mọi proxy). **Thay WS hai chiều:** hai SSE ngược + POST (không đẹp nhưng qua mọi tường lửa doanh nghiệp). **Thay self-host WS:** managed service (Pusher/Ably/MQTT over WS) khi fan-out viral là nghiệp vụ chính.

Năm thấu kính:
- **Kinh tế:** Connection dài = bộ nhớ + draining phức tạp; tính "giá mỗi 10k connection" trước khi chọn "realtime mọi thứ".
- **Vận hành:** Runbook deploy phải có mục "connection dài": drain bao lâu, client backoff thế nào — không có mục này là deploy = sự cố.
- **An ninh:** Token trong WS handshake URL bị log (→10.6); SSE authorize chuẩn header — một lý do nhỏ nữa nghiêng về SSE khi có thể.
- **Lịch sử:** Comet/long-poll (2000s) → WS (2011) → SSE được yêu lại (2020s do AI stream + đơn giản): mỗi thế hệ "đơn giản hoá việc đẩy" — hướng đi vẫn là về phía HTTP nguyên vẹn.
- **Người dùng:** "Chữ AI chảy từng dòng" là SSE/WebTransport đang làm việc; "chat không rớt khi đổi wifi" là QUIC migration — người dùng cảm nhận chương này mỗi ngày mà không gọi tên.

---

## 8. Đọc tiếp & bài tập

- Token stream: **12.2** · Fan-out/cache: **5.4** · Pub/sub: **5.3, 5.7** · Media realtime: **14.6**
- **Bài tập 1:** curl -N vào endpoint SSE của bạn qua từng hop (thẳng, qua nginx, qua LB/CDN). Ghi lại nơi bắt đầu "gom cụm" — đó là cấu hình cần sửa.
- **Bài tập 2:** Mở 1 WS, ngừng traffic, bấm giờ tới khi bị cắt. Lặp qua từng lớp. Số đó trừ 20% là interval ping bạn cần.
- **Bài tập 3:** Mô phỏng deploy: tắt 1/4 instance đang giữ connection. Đo: bao lâu client hồi phục, mất bao nhiêu sự kiện? Kết quả là SLA deploy thật của bạn hôm nay.
