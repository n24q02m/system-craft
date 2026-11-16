# 6.1 — 8 Ràng buộc Ngược của Tầng Client

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** nền client · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.8 (API client sẽ gọi) · 3.9 (đã chọn runtime).

**Sợi chỉ đỏ:** *Backend đã có hình hài — nhưng khách cầm điện thoại, xuống hầm mất sóng, máy yếu pin: ràng buộc client đổi gì?* — trả lời: client không phải "server yếu hơn" — là một thế giới khác: pin hữu hạn, mạng đứt quãng, phần cứng muôn hình, máy không tin được, và người dùng một chạm là bỏ đi; chương này gom tám ràng buộc, dịch thành chiến lược, đo bằng thước khác hẳn server. Câu hỏi để lại cho chương sau: *Điện thoại, máy tính, kiosk quán, TV — bốn môi trường, logic chia theo đường nào?*

**Thuật ngữ sẽ gặp:** *tám ràng buộc* — pin, mạng, phần cứng, màn hình, độ tin của máy, kiên nhẫn người dùng, cửa hàng app, hệ điều hành chủ; *RUM* — đo trên máy thật của khách, không phải trong lab; *cold start* — từ lúc chạm tới lúc dùng được: thước khách thật sự cảm nhận; *crash-free rate* — tỉ lệ phiên không treo: chỉ số sức khoẻ duy nhất không nói dối được; *ngân sách hiệu năng* — cold start bao nhiêu giây, pin bao nhiêu phần trăm: chốt trước khi viết code; *đo client khác đo server* — không kiểm soát, mẫu lệch, số tự báo: hiểu cách đo trước khi đọc số.

**Ví dụ mở đầu:** App của shipper DM chạy cả ngày ngoài nắng, mạng nhảy liên tục, máy rẻ pin mỏng: một lần treo là mất đơn. Server đo p99 — client đo tỉ lệ phiên kết thúc thành công và pin mỗi giờ. Chương này là bản dịch giữa hai thế giới.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chấp nhận ràng buộc nào là chủ đạo cho sản phẩm của tôi | Ứng dụng tôi "chết" vì hết pin, mạng yếu, hay update lệch? |
| 2 | Độ giảm cấp (degradation) thiết kế cho từng điều kiện xấu | Mất mạng/địt pin/older device — app tôi làm gì? |
| 3 | Chính sách update & version floor | Tôi hỗ trợ thiết bị/nền tảng cũ tới đâu — và bỏ theo lịch nào? |
| 4 | Ngân sách tài nguyên client (pin, dữ liệu, bộ nhớ) | App tôi tiêu bao nhiêu % pin/ngày — ai đo? |

---

## 2. Cơ chế

### 2.1 Vì sao cần một chương "ràng buộc" mở đầu Quyển II

Mọi chương từ 1–5 giả định **bạn kiểm soát máy chủ**. Tầng client đảo ngược từng giả định đó. Tám ràng buộc dưới đây là "định luật vật lý" của nửa bên kia — thiết kế chống lại chúng thì thua, thiết kế theo chúng thì mọi chương tiếp theo (6.2–6.7, 7.x) có chỗ đứng.

### 2.2 Tám ràng buộc

1. **Năng lượng hữu hạn:** pin là ngân sách cứng — CPU/radio/GPS rút theo tỷ lệ khác nhau; radio (cellular) tốn gấp nhiều lần wifi cho cùng dữ liệu (I). Mỗi lần wake radio đều trả giá.
2. **Mạng lúc có lúc không:** RTT cao + mất intermittent (đường hầm, thang máy) — request-response giả định ổn định là giả định sai (→6.3 offline-first).
3. **Môi trường KHÔNG tin cậy:** client nằm trong tay người dùng — mọi thứ trong RAM/storage có thể bị đọc/sửa (→6.7); secret trong client = secret công khai.
4. **Phiên bản không kiểm soát:** user ở lại bản cũ hàng tháng (web may hơn — reload; app store: tuần); **phiên bản cũ vẫn gọi API của bạn** — compatibility là nghĩa vụ một chiều (→4.8).
5. **Phần cứng phân tán cực rộng:** từ flagship tới máy 4 năm tuổi RAM 2 GB — p99 người dùng chạy trên thiết bị bạn không benchmark.
6. **Độ trễ cảm nhận trực tiếp:** 16 ms một khung hình, 100 ms "cảm giác phản hồi" — không có tầng nào che được cho bạn; jitter còn tệ hơn trễ (→11.1).
7. **Người dùng ngắt quãng:** notification, cuộc gọi, chuyển app — session chết giữa chừng; state phải sống sót qua kill (→6.3/7.2).
8. **Không có "ops on-call" cho client:** bạn không thể SSH vào điện thoại người dùng — mọi chẩn đoán phải được **thiết kế từ trước** (telemetry, breadcrumb, crash report — →7.6/11.1).

### 2.3 Từ ràng buộc đến chiến lược

| Ràng buộc | Chiến lược tiêu biểu | Chương |
|---|---|---|
| Pin/mạng | batching dữ liệu, exponential backoff, cache-offline | 6.3, 6.4 |
| Không tin cậy | secret zero ở client, attest, thin client cho nghiệp vụ nhạy | 6.7 |
| Phiên bản rải | API versioning + feature flag + kill-switch client | 4.8, 8.7 |
| Phần cứng rộng | performance budget theo máy p75, đo RUM | 7.3, 7.6 |
| Ngắt quãng | local-first, idempotent sync | 6.3 |

### 2.4 Đo client khác đo server

Server đo p99 request; client đo **phân phối theo người dùng** (p75/p95 user, không phải request — vì một người dùng khó chịu bị đếm 1.000 lần trong request-metric). Ba bộ số bắt buộc: Core Web Vitals/INP (web — →7.3), crash-free session, battery/data usage (mobile). Mọi tối ưu client không có số này là trang trí.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Frame budget | 16 ms (60 fps) | V | |
| Cảm giác phản hồi | < 100 ms | I | nghiên cứu UX cổ điển |
| Radio wake (cellular) | tốn năng lượng gấp ~×wifi | I | batching đáng tiền |
| App store update lan | tuần; web: reload | I | |
| Thiết bị p75 thế giới | giữa-dưới flagship ~3–4 năm tuổi | I | Android Stats |

---

## 4. Suy luận kiến trúc

- **S1:** Client là **môi trường đối tác, không phải phần mở rộng của server** — hợp đồng API phải thiết kế cho "đối tác chậm update, mạng xấu, phần cứng yếu" (→4.8 additive-first).
- **S2:** Tham số trụ: theo người dùng (crash-free, vitals p75, sync success), không theo request.
- **S3:** Mỗi chiến lược client là đổi công: offline-first đổi độ phức tạp sync lấy UX; thin-client đổi tính năng offline cho an ninh — chọn theo nghiệp vụ từng màn hình, không cho cả app.
- **S4:** Điện thoại là máy tính chính của đa số người dùng thế giới (VN ~70–80% traffic mobile (I)) — "mobile-first" từ khẩu hiệu thành ràng buộc số liệu.
- **S5:** AI on-device (model nhỏ, NPU — →12.3) đang kéo tính toán về client vì ràng buộc #1 (pin) và #3 (privacy) — vòng lặp "thin↔thick client" lại quay.
- **S6:** Khi app "chậm/khó chịu": tra bảng ràng buộc — 80% nguyên nhân là vi phạm một trong tám điều, không phải "code chưa tối ưu".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| User phàn nàn "ngốn pin" | Polling/wake radio liên tục | battery historian / energy log | §2.2-1 |
| App "khóc" khi mạng yếu | Thiếu thiết kế offline/retry | airplane-mode test | §2.2-2 |
| Lỗi chỉ trên máy cũ | Memory/CPU budget vượt | device-lab test p75 | §2.2-5 |
| API vỡ sau upgrade server | Client cũ vẫn gọi | version usage metric (→4.8) | §2.2-4 |
| "Không tái lập được" bug client | Thiếu telemetry | crash + breadcrumb (→7.6) | §2.2-8 |

---

## 6. Cách đo

```bash
# Web — Core Web Vitals thật (RUM + CrUX)
#   Lighthouse chỉ là lab; CrUX/api là người dùng thật
# Mobile — Android:
adb shell dumpsys batterystats --charged com.app > bs.txt
#   (phân tích wake lock, radio, alarm)

# Crash-free & phiên bản lan tỏa: dashboard theo app-version × device-tier
#   — quyết định "floor" nâng cấp (mục 1) cần số này
```

Nguyên tắc: **mở airplane mode + máy cũ nhất có thể + bản app 3 tháng tuổi** — nếu app vẫn dùng được, bạn đã tôn trọng tám ràng buộc; nếu chết, bảng §2 cho biết chết vì điều nào.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay đắt đỏ offline-first:** chấp nhận online-only cho tính năng phụ (không phải đường máu) — đánh đổi UX vùng mạng xấu; giữ offline-first cho phần lõi (soạn thảo, giỏ hàng). **Thay đo RUM:** lab benchmark + thiết bị đại diện (rẻ hơn, mù theo người dùng thật) — kết hợp, đừng thay thế.

Năm thấu kính:
- **Kinh tế:** Mỗi % pin app của bạn "ăn" là cơ hội bị gỡ; dữ liệu di động của người dùng là tiền của họ — hai ngân sách đạo đức + kỹ thuật.
- **Vận hành:** Kill-switch + force-update flow (server-driven config) là "bảng điều khiển hỏa hoạn" duy nhất bạn có ở client — kiểm thử định kỳ.
- **An ninh:** Ràng buộc #3 (không tin cậy) là gốc của mọi chương bảo mật client (→6.7, 7.7) — lặp lại: client không phải vault.
- **Lịch sử:** Từ terminal (mọi tính toán tập trung) → fat client (PC era) → web mỏng → mobile native → local-first (2020s): vòng lặp pendulum mỗi ~15 năm; đang ở nhánh "client thông minh trở lại" — nhưng lần này có sync engine trưởng thành.
- **Người dùng:** Người dùng không biết "offline-first" là gì — họ biết "tầng hầm vẫn soạn được tin nhắn". Tám ràng buộc này là bản dịch kỹ thuật của những khoảnh khắc đời thường đó.

---

## 8. Đọc tiếp & bài tập

- Bốn môi trường: **6.2** · Offline/CRDT: **6.3** · Push/energy: **6.4** · Client security: **6.7** · Web sâu hơn: **7.x**
- **Bài tập 1:** Với app của bạn: đo % session có ≥ 1 lần chuyển mạng (wifi↔cellular). Con số đó là tỉ trọng "ràng buộc #2 sống thật".
- **Bài tập 2:** Mở app ở airplane mode 60 giây, ghi lại mọi màn hình chết. Danh sách đó là backlog offline-first theo thứ tự người dùng cảm nhận.
- **Bài tập 3:** Tra bảng phiên bản device × app-version: bao nhiêu % user ở bản > 6 tháng tuổi? Đó là cửa sổ compatibility bạn thật sự phải hỗ trợ.
