# 6.4 — Giao tiếp Client, Push Notification & Năng lượng/Mạng

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** nền client · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.6 (kênh realtime) · 6.1 (ràng buộc pin).

**Sợi chỉ đỏ:** *Có tin mới phải báo — push tốn pin thế nào và thông báo nào xứng đáng đánh thức người?* — trả lời: push là con dao hai lưỡi — đưa tin tới người trong vài giây nhưng đánh thức cả pin lẫn kiên nhẫn; độ tin là best-effort (không đảm bảo, TTL ngắn); collapse key gộp bớt, silent push cập nhật ngầm; kênh realtime chọn theo "người dùng có đang nhìn màn hình không". Câu hỏi để lại cho chương sau: *Ảnh menu nặng, khách ở xa — edge/CDN caching là hợp đồng gì với origin?*

**Thuật ngữ sẽ gặp:** *đường ống push* — APNs/FCM: hệ điều hành giữ một connection dài thay mọi app, app không được tự giữ; *độ tin best-effort* — push có thể mất hoặc trễ: thiết kế phải chịu được mất, không được dựa; *collapse key* — gộp thông báo cùng chủ đề: ba tin "đơn mới" thành một; *silent push* — đánh thức app cập nhật ngầm: ngân sách pin có hạn, iOS cắt nếu lạm dụng; *đang nhìn / không nhìn* — đang mở app thì SSE/WebSocket (4.6), tắt màn hình thì push: đúng kênh mỗi trạng thái; *quyền web push* — quyền là lời hứa: xin rồi mà lạm dụng là bị tắt vĩnh viễn.

**Ví dụ mở đầu:** "Đơn mới gần bạn" xứng đáng đánh thức shipper lúc nửa đêm; "Món mới tuần này" thì không. DM từng push cả hai như nhau — tỉ lệ gỡ app nhích sau mỗi chiến dịch. Pin và sự chú ý của khách là tín dụng: chương này lập ngân sách cho từng loại thông báo.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Kênh đẩy: APNs/FCM/WebPush — và độ tin cậy cần gì | Thông báo của tôi có phải "phải tới" (y tế/giao hàng) không? |
| 2 | Tần suất & hợp nhất (collapse/silent push) | Tôi có đang dạy người dùng tắt notification vĩnh viễn không? |
| 3 | Chiến lược nền: poll, long-poll, WebSocket, hay push | Độ tươi cần bao nhiêu — đổi bằng bao nhiêu pin? |
| 4 | Phân loại tin nhắn theo ưu tiên & độ ồn | Tin nào được phép đánh thức người dùng 3h sáng? |

---

## 2. Cơ chế

### 2.1 Kiến trúc push: hai hệ điều hành, một đường ống

```
[Server] → APNs (Apple) / FCM (Google) / WebPush (VAPID) → thiết bị
              └— hệ điều hành giữ connection dài duy nhất với dịch vụ push
```

Điểm mấu chốt: **hệ điều hành đã giữ sẵn một kết nối dài cho mọi app** — app bạn không cần (và không được) tự giữ socket riêng ở background. Push payload: notification (hiển thị) hoặc **silent/data push** (đánh thức app vài giây để sync — bị OS throttle theo budget). TTL quan trọng: push "đơn đã giao" sau 2 giờ vô nghĩa — đặt expiry, không để hàng tồn.

### 2.2 Ngữ nghĩa "độ tin" của push

Push là **best-effort**: có thể trễ (phút), gộp, hoặc rơi (thiết bị offline lâu). Với thông báo **phải tới** (giao hàng, y tế, bảo mật): push chỉ là "gợi ý mở app" — **khi app mở phải pull sự thật từ server** (in-app inbox là nguồn hiển thị). Thiết kế chuẩn: push = chuông; nội dung luôn fetch; fallback = badge + email/SMS cho lớp critical.

### 2.3 Collapse key, silent push, và ngân sách pin

- **collapse_key / topic:** thông báo mới thay cũ (3 tin "có tin nhắn mới" → 1) — bắt buộc cho chat;
- **silent push:** đánh thức app để fetch (iOS `content-available`) — bị OS giới hạn tần suất (budget giảm dần nếu user ít mở app); đừng xây "sync realtime" trên silent push;
- **Doze/App Standby (Android):** mạng bị treo khi màn hình tắt — batch công việc vào cửa sổ maintenance; job scheduler (WorkManager) thay tự lo;
- **Rà soát radio:** cellular wake tốn pin (→6.1) — batch upload (gps, log) theo cụm 15 phút tốt hơn mỗi 10 giây một gói.

### 2.4 Thời gian thực ở client: chọn theo "người dùng có đang nhìn không"

| Tình huống | Nên | Vì sao |
|---|---|---|
| App đang mở, cần live (chat) | WebSocket/SSE (→4.6) | người dùng đang chờ |
| App background cần dữ liệu mới khi mở | Push silent hoặc fetch-on-open | pin |
| Đối tác/CRM cập nhật hiếm | Poll 15 phút hoặc push+pull | đơn giản, đủ |
| Vị trí liên tục (giao hàng) | nền tảng native background location + batching | OS cho phép có điều kiện |

Quy tắc "mắt": **chỉ giữ kênh realtime khi người dùng đang nhìn**; không nhìn thì push (chuông) + pull (khi mở). Đây là khác biệt sống còn với server-side realtime (→4.6 giữ connection lúc nào cũng được).

### 2.5 Web push & quyền

Web Push (VAPID): iOS 16.4+ (PWA add-to-homescreen) — đã phủ kín nền tảng lớn; vẫn thua native ở deep background action. Quyền notification là **tài sản một lần**: xin ngay lần mở đầu tiên = từ chối vĩnh viễn ~đa số; pattern chuẩn: hỏi sau khi người dùng thấy giá trị ("bật thông báo để theo dõi đơn này?").

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Push latency (đến thiết bị) | s–phút (best-effort) | I | không SLA |
| Silent push budget | OS quyết định, giảm nếu ít dùng | V | iOS docs |
| Collapse key | thay thế thông báo cùng key | V | FCM/APNs |
| Cellular wake cost | tốn hơn wifi rõ rệt | I | →6.1 |
| TTL push | đặt theo nghiệp vụ (phút–giờ) | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Push là **một chiều best-effort trên hạ tầng người khác** — mọi quyết định "đảm bảo tới" phải xây trên pull/inbox, không trên push.
- **S2:** Tham số trụ: delivery rate (đã gửi → thiết bị), open rate theo loại thông báo, battery impact (trước/sau bản phát hành), opt-out rate.
- **S3:** Mỗi bậc realtime đổi pin lấy độ tươi — bảng §2.4 là bản giá; đặt "được phép giành" theo từng màn hình.
- **S4:** OS ngày càng siết background (iOS budget, Android doze) — kiến trúc "app tự giữ socket nền" là nợ technical mỗi bản OS mới; thiết kế theo push+pull để sống sót.
- **S5:** AI notification (tóm tắt, ưu tiên hoá thông báo) đang vào OS (On-device AI) — thông báo "đẹp" sẽ được lọc bởi AI của hệ điều hành: nội dung phải thật sự đáng, nếu không bị chôn.
- **S6:** Khi "notification không tới": đo theo chặng (server→APNs/FCM có lỗi? thiết bị nhận? hiển thị?) — mỗi chặng có metric riêng; đừng đổ hết cho "đường truyền".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Push trễ phút–giờ | Best-effort + hàng đợi provider | delivery log theo chặng | §2.1 |
| Silent push ngừng hoạt động | Budget OS cạn (user ít mở) | iOS metric; cần fallback | §2.3 |
| Người dùng "bom" thông báo | Không collapse + không phân loại | audit tần suất/người dùng | §2.5 |
| Pin tụt khi thêm realtime nền | Giữ socket + poll đồng thời | energy log; bảng §2.4 | §2.4 |
| Web push không nhận iOS | PWA chưa add-to-homescreen (16.4+) | hướng dẫn cài | §2.5 |
| Thông báo "đến" nhưng sai nội dung | Payload stale (đẩy nội dung, không fetch) | push chỉ chuông | §2.2 |

---

## 6. Cách đo

```bash
# Đo theo chặng (bắt buộc với push quan trọng):
#   1) server→provider: response code APNs/FCM (log từng bản)
#   2) provider→device: delivery receipt (FCM diagnostic / APNs feedback)
#   3) device→mở: analytics open event (khớp id thông báo)

# Pin: A/B hai bản build (có/không tính năng nền) — battery & network usage
#   Android: dumpsys batterystats; iOS: MetricKit
```

Nguyên tắc: **mỗi thông báo có id — theo nó qua ba chặng**; không có chuỗi id thì mọi tranh luận "không nhận được" là lời đối đầu không chứng cứ.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay push:** email/SMS (độ tin khác, chi phí khác); in-app inbox khi mở (khi "tươi" không quan trọng); badge số trên icon (im lặng, hiệu quả). **Thay realtime nền:** fetch-on-open + refresh khi pull-to-refresh — 90% app không cần hơn thế.

Năm thấu kính:
- **Kinh tế:** Opt-out notification là mất kênh tiếp cận **vĩnh viễn** cho người dùng đó — mỗi thông báo vô giá trị là tiêu một phần tư tài sản hữu hạn đó.
- **Vận hành:** Runbook push phải có nhánh "provider đổi chính sách/budget" (APNs/FCM từng thay không báo trước) — theo dõi changelog như dependency.
- **An ninh:** Payload push đi qua hạ tầng nhà mạng + provider — không đặt dữ liệu nhạy cảm; deep-link từ notification vào màn hình cần auth lại nếu nhạy (→6.7).
- **Lịch sử:** Từ SMS push (thập niên 2000) → APNs (2009) → GCM/FCM → WebPush (2016→iOS 2023): mỗi nền tảng co về **một đường ống của OS** — và điều khiển năng lượng là lý do, không phải tiện ích.
- **Người dùng:** "Tôi nhận thông báo đúng lúc tôi cần, không bị làm phiền" — chương này là kỹ thuật đứng sau một câu nghe dễ mà khó bậc nhất của mobile.

---

## 8. Đọc tiếp & bài tập

- Realtime khi mở app: **4.6** · Ràng buộc pin/mạng: **6.1** · Local-first sync: **6.3** · IoT push (MQTT): **6.6**
- **Bài tập 1:** Đo opt-out rate notification theo 30 ngày. > 20%? Đó là người dùng đang tự cài đặt chế độ im lặng với sản phẩm — nội dung cần đổi trước khi kỹ thuật đổi.
- **Bài tập 2:** Gửi 10 push test qua 3 chặng (§6) và đo từng chặng. Chuỗi id có xuyên không? Nếu đứt ở chặng nào — đó là khoảng mù chẩn đoán của bạn.
- **Bài tập 3:** Với mỗi loại thông báo hiện có: viết tên nó + "người dùng vì sao cần nó NGAY BÂY GIỜ". Không viết được = ứng viên gộp vào digest hằng ngày.
