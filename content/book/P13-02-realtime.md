# 13.2 — Playbook: Realtime, Chat & Cộng tác

> **Tầng:** Nghiệp vụ · **Quyển III** · **Trục đọc:** playbook theo miền · **Động từ liên quan:** Áp dụng · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.6 (SSE/WebSocket) · 6.3 (CRDT đã gặp).

**Sợi chỉ đỏ:** *Tiền đã vào sổ sạch — trạng thái đơn nhảy realtime cho hàng trăm nghìn người thế nào?* — trả lời: trạng thái đơn nhảy realtime cho hàng trăm nghìn người — fan-out có hai mô hình đối nghịch (ghi một lần đọc nhiều, hay ghi từng bản cho từng người: D-135); ngữ nghĩa giao hàng phải công khai; reconnect storm là bài toán thiết kế chứ không phải sự cố; presence và typing là tín hiệu rẻ, route riêng. Câu hỏi để lại cho chương sau: *Mọi sự kiện chảy về một chỗ — ingest và stream vận hành ra sao?*

**Thuật ngữ sẽ gặp:** *fan-out* — một tin tới N người: câu hỏi nền của mọi hệ realtime; *write-once vs write-per-user* — đổi dung lượng lấy độ trễ: tài khoản "sao lớn" là ca thử thật; *ngữ nghĩa giao hàng* — at-most-once, at-least-once, có thứ tự: client phải được biết mình đang giữ ngữ nghĩa nào; *reconnect storm* — deploy xong vạn client cùng quay lại trong một giây: backoff cộng jitter (nối 3.10, 6.4); *presence/typing* — tín hiệu tần số cao, giá rẻ: tách đường riêng khỏi dữ liệu thật; *OT/CRDT* — cộng tác chung tài liệu: chỉ khi cần (nối 6.3).

**Ví dụ mở đầu:** Trang theo dõi đơn của DM deploy lại giữa trưa: chục nghìn tab reconnect cùng lúc — LB gục trước khi app kịp khởi động. Câu trả lời nằm ở thiết kế (jitter, stagger), không ở may mắn. Chương này là playbook chat và cộng tác: mọi quyết định có đánh số, mọi ngữ nghĩa giao hàng công khai.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Fan-out realtime quy mô lớn: broadcast vs per-connection (D-135) | 1 tin nhắn tới 10.000 người online — tôi ghi 1 lần hay 10.000 lần? |
| 2 | Transport: WebSocket / SSE / polling (theo nền tảng — →4.6) | Người dùng tôi đang "nhìn" app hay ở background? |
| 3 | Reconnect & đồng bộ lại sau gián đoạn | Mất mạng 30 giây — mở lại thấy gì (đúng 6.3 đã hỏi)? |
| 4 | Presence/typing: tần suất, TTL, lưu ở đâu | "Đang gõ..." của tôi tốn bao nhiêu gói/giây? |

---

## 2. Cơ chế

### 2.1 Kiến trúc tham chiếu chat/cộng tác

```
[Client WS/SSE] ⇄ [Gateway connection (sticky — →9.4)]
                    ⇅ [Presence service] (TTL redis-style — 5.4)
[Message API] → [Kafka (→5.7)] → [Fan-out worker]
                    ├→ ghi store (5.2/5.3) — nguồn chân lý
                    ├→ push vào connection đúng người (nhiều node gateway)
                    └→ badge/unread counter (đếm — idempotent)
[Sync API] ← client mở lại: "từ last_event_id cho tôi những gì thiếu"
```

### 2.2 Fan-out: write-once vs write-per-user (D-135)

Hai trường phái: **fan-out-on-write** (lúc gửi: ghi sẵn hộp từng người — đọc nhanh, ghi nổ khi nhóm to) vs **fan-out-on-read** (ghi một nơi, đọc tính theo người — ghi nhẹ, đọc nặng). Chat/cộng tác thực chiến: **lai theo cỡ** — nhóm nhỏ on-write, kênh lớn/kênh có đông người theo dõi on-read + cache (→5.5 tư duy Cassandra áp đúng chỗ). Kèm nguyên tắc: **payload tách khỏi danh sách người nhận** (gửi reference, mỗi connection tự hydrate) — tiết kiệm băng thông khi 10.000 connection nhận cùng một bản ghi.

### 2.3 Đảm bảo giao hàng — chọn ngữ nghĩa công khai

Ba mức (viết vào hợp đồng sản phẩm — không để ngầm): **at-most-once** (được phép mất — typing indicator), **at-least-once + client idempotent** (tin nhắn — gửi kèm client msg id), **exactly-once effect** (đếm/ghi sổ — →13.1 chuẩn). Kèm thứ tự: **thứ tự per-conversation** (không toàn cục — 8.1 đã dạy thứ tự là costly); gap detection bằng **sequence per conversation** — client thấy đứt thì gọi sync API (không "chấp nhận thiếu").

### 2.4 Reconnect storm — khi 10.000 client cùng quay lại

Sự cố node/restart mạng → sóng reconnect ập vào (thundering herd — 8.5): phòng bằng **backoff + jitter client-side** (→6.4/8.5), **rate limit handshake** ở gateway, **sticky session** giữ trải nghiệm (hoặc session token để reconnect đâu vào đó — 9.4), và **đồng bộ delta thay vì full reload** (client giữ last_event_id). Drill: tắt một gateway node giờ làm việc — reconnect tự nhiên là bài kiểm tra thật (11.3 chaos áp vào realtime).

### 2.5 Presence & typing — tín hiệu rẻ, không phải dữ liệu

"Online/đang gõ": TTL key ở KV store (Redis/Valkey — 5.4), **không** ghi DB; tần suất typing throttle 2–3 s; presence chỉ báo cho người cùng cuộc trò chuyện (không broadcast toàn hệ). Lỗi kinh điển: coi presence là dữ liệu quan trọng (lưu vĩnh viễn + query nặng) — nó là **hiệu ứng thị giác**, mất là bình thường, cheap by design.

### 2.6 Trải nghiệm cộng tác sâu: OT/CRDT (khi cần)

Cùng soạn tài liệu (con trỏ người khác, gõ đồng thời): CRDT/OT engine (Yjs/Automerge — →6.3) + **awareness** (vị trí con trỏ — presence-style tín hiệu) + persist periodic snapshot (không lưu từng keystroke — compact). Đáng tiền cho sản phẩm "cộng tác là tính năng bán hàng"; chat thường + badge thì không cần — chọn theo product, không theo mốt.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Connection/node | ~chục–trăm nghìn (tùy stack) | I | →3.x event loop |
| Typing throttle | 2–3 s | P | |
| Presence TTL | 30–60 s | P | |
| Reconnect backoff | jitter, cap 30–60 s | P | →8.5 |
| Delta sync | theo last_event_id | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Realtime là bài **đủ hai đường**: push (đang nhìn — 4.6) + pull/sync (mở lại — 6.3); hệ chỉ có push sẽ "mù" đúng lúc user quay lại — và đó là khoảnh khắc user đánh giá app;
- **S2:** Tham số trụ: connection đồng thời theo node, tỉ lệ reconnect thành công < 5 s, tỉ lệ gap bị client phát hiện, chi phí fan-out/tin (byte + lệnh ghi).
- **S3:** Fan-out lai theo cỡ + payload-by-reference đổi bộ nhớ/đọc lấy ghi/băng thông — mỗi tổ hợp hợp lệ với một dạng sản phẩm (chat riêng tư vs kênh lớn vs feed);
- **S4:** Gateway connection là **stateful tier đặc biệt** (sticky, drain chậm — 9.1/9.4): deploy phải tính drain connection (→8.5 graceful; 9.7 synthetic xuyên deploy là test bắt buộc);
- **S5:** Agent/AI vào chat (bot trả lời, tóm tắt) là "người tham gia" mới: **presence riêng + rate limit + đánh dấu rõ là bot** (10.3 danh tính + 12.4 agent) — user phải biết mình đang nói chuyện với ai;
- **S6:** Khi "tin nhắn đôi khi không tới": tách ba lớp — broker giao (Kafka lag?), fan-out đúng connection (route user→node đúng?), client nhận rồi render (gap detection?) — trace theo msg id xuyên ba lớp (11.2).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Nhóm to lag nặng | Fan-out-on-write cho kênh lớn | lai on-read + cache | §2.2 |
| Mất mạng 30 s mất tin | Không delta sync | last_event_id + sync API | §2.3 |
| Restart node → sóng sập | Reconnect storm | jitter + rate limit + drill | §2.4 |
| Tin nhắn đôi khi đôi bản | Idempotency client thiếu | client msg id | §2.3 |
| "Đang gõ" đốt băng thông | Không throttle | throttle 2–3 s | §2.5 |
| Deploy là disconnect sạch | Không graceful drain | preStop + sticky/session token | §2.4 |

---

## 6. Cách đo

```bash
# Synthetic reconnect drill (mỗi quý): tắt 1 gateway node → đo:
#   - thời gian trung vị client vào lại ổn định (< 5 s là khoẻ)
#   - sóng CPU/gateway còn lại (quá cao = thiếu rate limit handshake)
# Gap test: 2 client — chặn mạng 1 client 30 s rồi mở —
#   client đó có tự lấp khoảng trống không? (đúng = delta sync sống)
```

Nguyên tắc: **realtime đo bằng "khoảnh khắc khó"** (mở lại sau mất mạng, deploy giữa cuộc trò chuyện) — không bằng trung bình thời gian đẹp.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự dựng:** dịch vụ chat managed (Sendbird/Ably-style) hoặc nền tảng open (Matrix) — mua nhanh, khóa; hợp khi chat không phải lợi thế cạnh tranh (11.7); **thay WebSocket:** SSE một chiều + POST gửi (đơn giản hơn nhiều — đủ cho thông báo/dashboards — 4.6 bảng chọn); **thay CRDT:** locking thô (không cùng lúc — trải nghiệm 2005) — đôi khi đủ và rẻ.

Năm thấu kính:
- **Kinh tế:** Realtime tier là chỗ **đốt connection/tiền bộ nhớ** lặng lẽ (mỗi connection = fd + bộ nhớ đệm — 1.x/3.x); đo per-connection cost để định giá "online user" cho chính mình;
- **Vận hành:** Stateful connection + deploy thường = căng nhất của SRE: runbook drain + drill (11.8) — tài sản không thấy cho tới khi thấy;
- **An ninh:** Mọi connection phải **authn + authz khi đăng ký kênh** (đăng ký kênh ai-cũng-được = lỗi chéo dữ liệu — 10.3/12.3 cùng bệnh); rate limit per connection (chống spam + tài nguyên);
- **Lịch sử:** IRC (1988) → XMPP (1999) → WebSocket (2011) → CRDT cộng tác (2020s): mỗi thế hệ giảm chi phí "biết ngay điều gì đang xảy ra"; nhu cầu là của con người từ khi có điện báo — công nghệ chỉ giảm giá mỗi 10 năm một bậc;
- **Người dùng:** "Tôi gửi, bạn thấy ngay" — realtime là sản phẩm của **sự hiện diện** (presence) theo đúng nghĩa con người; mọi kỹ thuật này tồn tại để khoảng cách hai con người trên mạng = 0 giận giục.

---

## 8. Đọc tiếp & bài tập

- Transport: **4.6** · Offline/sync: **6.3** · Kafka: **5.7** · KV/presence: **5.4** · Graceful/drain: **8.5, 9.1** · Chaos drill: **11.3**
- **Bài tập 1:** Đo fan-out của tin nhắn nhóm lớn nhất bạn (số bản ghi ghi/lần gửi — log một hôm). > 1.000 ghi/tin? Ứng viên chuyển on-read + cache;
- **Bài tập 2:** Chạy gap test (§6) với app thật: chặn mạng client 30 giây giữa cuộc trò chuyện. Lấp được = đạt; không lấp = backlog sync API tuần này;
- **Bài tập 3:** Tính chi phí presence: số người online × gói/s × byte — nhân theo p95. Con số nhỏ nhưng **liên tục** — throttle/TTL đúng làm nó biến mất khỏi hóa đơn.

