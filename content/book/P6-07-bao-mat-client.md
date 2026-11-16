# 6.7 — Bảo mật Phía Client & Attestation

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** nền client · **Động từ liên quan:** Chọn · Bảo vệ
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 2.7 (thang cách ly) · 4.8 (API mặt tiền).

**Sợi chỉ đỏ:** *Mọi thứ chạy trên máy không tin được — bảo mật client là phòng tuyến nào?* — trả lời: nguyên lý số một — client là lãnh thổ của đối phương: mọi thứ nằm trong app đều đọc được, sửa được, giả được; nên bí mật không nằm trên client, token ngắn hạn, server tự quyết mọi quyền; attestation hỏi "client này là bản thật không"; và có hẳn kịch bản client đã bị xâm nhập. Câu hỏi để lại cho chương sau: *Mặt tiền web chính là sản phẩm — trang tải và vẽ thế nào cho người ở lại?*

**Thuật ngữ sẽ gặp:** *lãnh thổ đối phương* — obfuscate không phải bảo mật: giả định mọi code đều bị soi; *keychain/keystore* — kho bí mật của hệ điều hành: dùng đúng, không tự chế; *token ngắn hạn* — access token tính bằng phút, refresh thu hồi được: thu hẹp thiệt hại; *attestation* — Play Integrity, App Attest: bằng chứng client chưa bị bẻ: tăng rào, không tường thành; *zero trust client-server* — server kiểm mọi request: không tin header "app của tao gửi"; *kịch bản bị xâm nhập* — khoá thiết bị, xoá phiên, giới hạn tần suất: tập trước, không ứng khẩu lúc nổ.

**Ví dụ mở đầu:** Voucher giảm giá nằm trong app DM: kẻ bẻ khoá đọc được giá trị, sửa điều kiện, dùng lại nhiều lần. Giá thật phải do server tính và ký; client chỉ trưng bày. Chương này vẽ ranh giới "tin client tới đâu" — câu trả lời chuyên nghiệp: không tin, chỉ kiểm.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Client giữ gì (không bao giờ giữ gì) | Secret nào tôi dám đặt vào client — câu trả lời đúng: "không"? |
| 2 | Lưu trữ an toàn: keychain/Keystore/IndexedDB | Token nằm ở đâu, ai đọc được khi mất máy? |
| 3 | Mức attest cần: không / Play Integrity / App Attest / web trust signals | Tôi cần biết client "thật" tới mức nào — để làm gì tiếp? |
| 4 | Chống lạm dụng nghiệp vụ ở server (không ở client) | Cầu thủ gian lận của tôi dùng client chuẩn hay tool tự viết? |

---

## 2. Cơ chế

### 2.1 Nguyên lý số một: client là lãnh thổ của đối phương

Mọi thứ gửi xuống client — code, token, cấu hình, "logic kiểm tra" — **có thể bị đọc, sửa, chạy lại, bỏ qua**. Vô hiệu hoá nút bấm phía client chỉ là gợi ý; chọn giá client chỉ là mẹo. Hệ quả kiến trúc:

- **Nghiệp vụ nhạy cảm kiểm tra ở server, luôn** (giá, quyền, giới hạn tốc độ — →11.3);
- **Secret dài hạn không đặt ở client** — dùng token ngắn hạn + refresh qua luồng chuẩn (OAuth2.1/PKCE — →7.7);
- **Obfuscation/licence check client** chỉ nâng chi phí crack, không ngăn — hợp đồng pháp lý + server-side check mới là rào thật.

### 2.2 Lưu trữ an toàn theo nền tảng

| Nền tảng | Nơi giữ | Bảo mật |
|---|---|---|
| iOS | Keychain (Secure Enclave cho khoá) | chống đọc khi khoá máy; wipe khi reset |
| Android | Keystore (StrongBox nếu có) | khoá không rời chip; hardware-backed |
| Web | IndexedDB/Storage — **không có keychain** | mọi JS chạy cùng origin đọc được → XSS = mất token (→7.7) |
| Desktop | OS keychain (Secret Service/Keychain) | tốt nếu dùng; file plaintext là mặc định tệ |

Web là môi trường khó nhất: token trong JS-accessible storage + một lỗ XSS là sạch tài khoản. Chuẩn hiện đại: **token ngắn (phút) + refresh token trong HttpOnly cookie** (nếu same-site phù hợp) + **https + HSTS** toàn tuyến.

### 2.3 Attestation — "client này là bản thật không?"

| Cơ chế | Nền tảng | Bảo đảm | Không bảo đảm |
|---|---|---|---|
| **Play Integrity** | Android | device + app nguyên vẹn (kết quả: verdict server kiểm) | không thấy nội dung thiết bị; verdict có thể stale |
| **App Attest / DeviceCheck** | iOS | khoá app + device, anti-tamper | tương tự |
| **WebAuthn/passkey** | web+ | khoá trong authenticator — chống phising mạnh | không attest "trình duyệt sạch" |
| **Remote attestation** (TPM/TEE) | nhúng/server | đo chuỗi boot, khoá bị buộc phần cứng | phức tạp vận hành |

Điểm then chốt: **verdict attest phải được server kiểm và quyết** (không chỉ thu thập) — flow chuẩn: client xin challenge → attest → server gọi verify API của Google/Apple → cấp token có "độ tin" gắn vào. Và attest là **rào giơ thiệu cho abuser, không phải tường tuyệt đối**: root/jailbreak cao cấp vẫn vượt một phần; kết hợp rate limit + anomaly (→11.2) mới thành hệ thống.

### 2.4 Zero trust client → server

Mọi request từ client mang: token ngắn hạn (scope tối thiểu), device id, attest verdict (khi cần), dấu vết request hợp lệ. Server tin **chính xác mức verdict cho phép**, không tin "vì request đến từ app của tôi". Đây là bản dịch client-side của zero trust (→10.1) — cùng nguyên lý: không tin danh tính mạng, tin bằng chứng theo yêu cầu.

### 2.5 Khi client đã bị xâm nhập

Kịch bản phải thiết kế trước: mất máy (remote wipe token qua MDM/revoke), token lộ (short TTL giới hạn thiệt hại + revoke refresh), device gian lận (flag fleet — kết hợp pattern →11.2). Mỗi kịch bản có runbook — "client là lãnh thổ đối phương" nghĩa là phản xạ đầu tiên của bạn phải là "thu hồi", không phải "điều tra".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| TTL access token | phút–giờ | P | ngắn = thiệt hại lộ nhỏ |
| Attest verdict cache | giờ | P | stale verdict = cửa sổ lạm dụng |
| Passkey (FIDO2/WebAuthn) | chuẩn phủ iOS/Android/browser | V | 2026 phổ biến |
| OAuth2.1 + PKCE | khuyến nghị mặc định cho public client | V | RFC draft ổn định |

---

## 4. Suy luận kiến trúc

- **S1:** An ninh client là **giảm thiệt hại** (giới hạn token, thu hồi nhanh), không phải ngăn chặn tuyệt đối — kiến trúc phải tồn tại sau khi client bị xâm nhập.
- **S2:** Tham số trụ: số token thu hồi/giờ, tỉ lệ request không qua verify attest (theo tuyến nhạy cảm), thời gian phát hiện–thu hồi (MTTR-X của client).
- **S3:** Mỗi tầng attest đổi UX (thêm bước, rớt thiết bị cũ không attest được) lấy chi phí gian lận — chỉ áp cho luồng có giá trị xứng (thanh toán, mua trong app).
- **S4:** Passkey đang thay password (2026: Apple/Google/Microsoft đều phổ biến) — thiết kế đăng nhập mới mà không có passkey là nợ từ ngày đầu.
- **S5:** AI agent chạy thay người dùng (→12.x) là "client" mới — danh tính phải phân biệt user/device/**agent** + scope hẹp: câu hỏi attest sẽ lặp lại cho agent trong vài năm tới.
- **S6:** Khi "tài khoản bị gian lận": hỏi client đã bị gì (XSS? mất máy? tool tự viết gọi API?) — bốn câu §2.5; chặn IP vô ích vì đối phương dùng chính điện thoại nạn nhân.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Token bị đọc trộm (web) | XSS đọc storage | CSP + HttpOnly refresh (→7.7) | §2.2 |
| API bị gọi bởi tool tự viết | Chỉ dựa client check | server-side verify + attest | §2.1 |
| Lộ secret trong bundle/app | Hard-code key build | quét secret trước release | §2.1 |
| Replay request cũ | Thiếu nonce/TTL | token ngắn + idempotency (→4.8) | §2.2 |
| Nạn nhân "không làm gì" | Thiết bị bị cài bad client | device flag + revoke fleet | §2.5 |

---

## 6. Cách đo

```bash
# Quét secret trong artifact client (trước mỗi release):
#   gitleaks / trufflehog trên repo + bundle output

# Audit "ai đọc được gì": với mỗi loại token, viết ra bảng
#   storage → ai truy cập (origin/app/process) → TTL → cách revoke

# Đo tuyến nhạy cảm: % request có attest verdict hợp lệ
#   (đặt metric trước khi cần — sau sự cố thì đã muộn)
```

Nguyên tắc: **mỗi token có "sổ hộ khẩu"** (nơi ở, tuổi, ai đuổi được); không có sổ là bạn đang giữ tiền trong ngăn kéo mở.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay attest:** chấp nhận gian lận thấp + bồi hoàn (mô hình kinh doanh một số fintech nhỏ) — rẻ hơn kỹ thuật, chỉ hợp khi thiệt hại đơn lẻ nhỏ; **thay keychain:** tự mã hoá file (lại cần chốt khoá ở đâu — vòng lặp về secure element): luôn thua hệ điều hành có chip; đừng tự chế.

Năm thấu kính:
- **Kinh tế:** Chi phí chống lạm dụng phải < thiệt hại mong đợi — attest mọi endpoint là trả phí cho kịch bản hiếm; chọn lọc theo giá trị luồng.
- **Vận hành:** Revocation phải là nút bấm được khi 2h sáng (quy trình + drill) — thiết kế "thu hồi trong 5 phút" và đo nó như RTO (→13.2).
- **An ninh:** Chuỗi niềm tin client: silicon (secure element) → OS (keychain) → app (signing) → attest (verdict) — mỗi tầng chỉ mạnh bằng tầng dưới;nhảy tầng là ảo tưởng.
- **Lịch sử:** Từ "obfuscate JS" thập niên 2000 → certificate pinning (2010s, giờ chống dùng) → passkey/attest (2020s): hướng đi nhất quán là đẩy gốc tin xuống **phần cứng**, không xuống code.
- **Người dùng:** Người dùng không biết token là gì — họ biết "mất điện thoại thiệt hại nhỏ, đổi máy thì mọi thứ về lại". Mỗi quyết định ở chương này nên quy về trải nghiệm đó.

---

## 8. Đọc tiếp & bài tập

- XSS/CSP/Trusted Types: **7.7** · Zero trust & identity: **10.1** · Rate limit/anti-abuse: **11.3** · IoT provisioning: **6.6** · AI agent như client: **12.7**
- **Bài tập 1:** Mở devtools app bạn (web): `localStorage`/`sessionStorage`/cookie có gì? Mỗi chuỗi tìm được — TTL bao lâu, revoke thế nào? Ghi thành bảng; ô trống là nợ.
- **Bài tập 2:** Gọi một API nhạy cảm bằng curl với token copy từ app. Nếu server trả 200 không hỏi gì thêm — attest/verify chưa là tuyến phòng thủ, chỉ là trang trí.
- **Bài tập 3:** Viết runbook "mất 1.000 thiết bị" (khóa fleet, thu hồi token, thông báo): thời gian từng bước cộng lại dưới 30 phút chưa? Nếu chưa — sự cố thực tế sẽ dài hơn nhiều.
