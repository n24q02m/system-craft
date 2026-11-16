# 7.7 — Bảo mật Frontend & Mô hình An ninh Trình duyệt

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** web frontend · **Động từ liên quan:** Bảo vệ · Chọn
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 6.7 (client là lãnh thổ đối phương) · 7.3 (npm supply chain).

**Sợi chỉ đỏ:** *Trình duyệt là chiến trường — XSS, CSP, token xử lý thế nào?* — trả lời: trình duyệt là chiến trường — same-origin là luật gốc để hiểu mọi thứ còn lại; XSS vẫn là vua lỗi frontend, CSP là hãm; token nằm đâu là quyết định một lần, chịu hậu quả mãi; và npm là bề mặt tấn công lớn nhất của frontend. Câu hỏi để lại cho chương sau: *Mặt tiền đẹp mà lưng chỉ có một máy chủ — DM nhân bản, và nhiều bản sao nghĩa là nhiều sự thật: ai đúng?*

**Thuật ngữ sẽ gặp:** *same-origin policy* — luật gốc của trình duyệt: scheme, host, port phải khớp; *XSS* — chèn script chạy trong trang của bạn: vẫn là vua lỗi FE; *CSP* — Content-Security-Policy: hạn chế nguồn script được tải: hãm thiệt hại khi XSS vẫn lọt; *token nằm đâu* — localStorage đọc được bởi XSS, cookie HttpOnly thì không: quyết định đúng một lần; *SSR/RSC* — render phía server mở bề mặt mới: nối lại 6.7; *supply chain* — một package npm độc hại chạy ngay trong lúc build: bề mặt lớn nhất của FE.

**Ví dụ mở đầu:** Đánh giá món của DM hiển thị comment khách gõ: thoát sai một chuỗi, script chạy dưới domain DM cùng phiên độ của người dùng. Chương này đi từ luật same-origin, qua chỗ đứng của token, tới chuỗi npm — vẽ bản đồ chiến trường cho người viết mặt tiền.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chính sách CSP: strict nonce/hash, report-only trước | Trang tôi có thể chèn script từ đâu — và tôi kiểm soát được không? |
| 2 | Trusted Types + framework escaping | DOM sink nguy hiểm có bị chặn ở tầng trình duyệt chưa? |
| 3 | Danh tính & phiên ở FE: cookie HttpOnly vs token storage | Token của tôi nằm ở đâu khi có XSS? |
| 4 | Phòng thủ dependency (SBOM, lockfile, audit) | Tôi có biết đang chạy code của bao nhiêu người lạ không? |

---

## 2. Cơ chế

### 2.1 Mô hình an ninh của trình duyệt — gốc hiểu mọi thứ

- **Same-Origin Policy:** script ở origin A không đọc DOM/dữ liệu origin B — gốc mọi thứ; mọi lỗ hổng về sau là "vô tình mở cửa SOP";
- **Cookie (SameSite):** Lax/Strict chặn hầu hết CSRF truyền thống — **SameSite=Lax + POST có CSRF token** cho luồng nhạy;
- **CORS:** cấu hình **server** quyết định ai đọc response — `Access-Control-Allow-Origin: *` kèm credentials là mâu thuẫn chết người (trình duyệt chặn — vì cả hai không đi cùng nhau);
- **postMessage/iframe:** `targetOrigin` cụ thể + kiểm `event.origin` — hai dòng này thiếu là cổng chéo origin mở.

### 2.2 XSS — vẫn là vua lỗi FE

Ba dạng: **reflected** (tham số quay lại HTML), **stored** (chuỗi từ DB ra trang — nguy hiểm nhất), **DOM-based** (client tự chèn — `innerHTML`, `eval`, `document.write`). Phòng thủ theo tầng:

1. **Framework escaping mặc định** (React/Vue escape chuỗi — không bao giờ `dangerouslySetInnerHTML`/`v-html` với input người dùng; cần rich text: sanitizer chỉ cho whitelist tag/thuộc tính);
2. **CSP strict:** `script-src 'nonce-…'` — script inline không nonce bị chặn → dù có XSS injection, payload không chạy; đặt qua `Content-Security-Policy` header (meta tag không đủ cho nhiều directive);
3. **Trusted Types:** chặn toàn bộ DOM sink nguy hiểm (`innerHTML`...) trừ policy đã cho phép — lớp cuối, đang được các browser lớn hỗ trợ (Chrome nhóm đầu);
4. **Báo cáo trước khi ép:** `Content-Security-Policy-Report-Only` chạy 1–2 tuần, đọc report, rồi mới enforce — nhảy thẳng strict là tự DoS (→11.7 dạy launch an toàn).

### 2.3 Token nằm đâu — quyết định một lần, chịu hậu quả mãi

| Nơi | Ai đọc được | Hệ quả |
|---|---|---|
| **HttpOnly cookie** (kèm CSRF token) | JS không đọc được | XSS không lấy được token — nhưng vẫn hành động như user (gửi request); cần CSP |
| localStorage/sessionStorage | mọi JS cùng origin | XSS = ăn cắp token = tài khoản (→6.7) |

Chuẩn 2026 cho SPA công khai: **access token ngắn trong bộ nhớ (không localStorage) + refresh trong HttpOnly SameSite cookie**; server trả theo BFF pattern (backend-for-frontend giữ secret OAuth) — client không bao giờ thấy refresh token dài hạn.

### 2.4 SSR/RSC mở mặt mới (lặp lại bài 6.7 ở tầng FE)

Server render giữ secret + dữ liệu người khác; sai lầm kinh điển: **serialize props chứa dữ liệu nhạy xuống client** (query cho user A chạy xuống bundle cho mọi người — hoặc log URL chứa token). Bộ quy tắc: secret chỉ qua biến môi trường server; props xuống client là dữ liệu đã phân quyền; log không ghi token (→11.5 log hygiene). Thêm: **một URL = một nội dung** trừ khi có Vary đúng (→6.5) — leak chéo user qua cache CDN là sự cố có thật, đã xảy ra ở các nền tảng lớn (I).

### 2.5 Supply chain FE — npm là bề mặt lớn nhất

- **Lockfile bất biến + CI cài từ lock** (npm ci);
- **Audit thường xuyên** (`npm audit`, GitHub Dependabot/OSSI) — nhưng **triage theo exposure**: dependency chạy ở build-time khác runtime khác trình duyệt;
- **SBOM + ít dependency** (→7.3 cùng lý do hiệu năng — hai mục tiêu trùng nhau ở đây);
- **integrity hash** cho script tải từ CDN (SRI) — hoặc tự host (không phụ thuộc bên thứ ba = không mất khi CDN chết/đổi);
- Bài học từ các sự kiện typosquat/clipboard-hijack trong npm: dependency mới = code review như code của mình (mỗi install là một lần thuê code lạ chạy trên máy người dùng).

### 2.6 Subresource, iframe, và third-party

Mỗi third-party script (analytics, chat, ads) = **code của người khác chạy cùng origin quyền năng** (đọc DOM, cookie tùy cấu hình). Chèn qua CSP framework (script-src domain), cân nhắc iframe sandbox + postMessage có kiểm tra origin (§2.1); đếm số third-party mỗi release — nó phình âm thầm và là cả chi phí hiệu năng (→7.3) lẫn an ninh.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| CSP report-only giai đoạn | 1–2 tuần trước enforce | P | |
| Trusted Types hỗ trợ | Chrome/Edge nhóm đầu; FF/Safari đang tới | V | |
| Access token TTL | phút–giờ | P | →6.7 |
| các sự cố supply chain npm | nhiều sự cố lớn công khai 2018–2026 | I | chuỗi sự cố 2018–2026 |

---

## 4. Suy luận kiến trúc

- **S1:** An ninh FE là **sân khấu nhiều lớp** (escaping → CSP → Trusted Types → token placement → server checks) — mỗi lớp giả định lớp trên đã vỡ; không có lớp nào "đủ".
- **S2:** Tham số trụ: số violation CSP report theo ngày, số `dangerouslySetInnerHTML`/sink nguy hiểm trong repo (grep được), số third-party script, thời gian vá CVE cao theo exposure.
- **S3:** HttpOnly cookie đổi (phải chống CSRF) lấy "XSS không ăn cắp token"; BFF đổi một dịch vụ trung gian lấy client không giữ secret — mỗi lần đổi chuyển rủi ro sang nơi dễ kiểm soát hơn.
- **S4:** SOP là hợp đồng an ninh **duy nhất** trình duyệt cam kết — mọi kiến trúc FE (micro-frontend, embed, widget) là bài toán "làm gì trong SOP mà không đục nó" (→7.1 cùng triết lý hợp đồng).
- **S5:** AI sinh code có xu hướng `dangerouslySetInnerHTML`/eval khi gặp khó — CSP strict là hàng rào bắt lỗi AI tốt nhất hiện có; quy tắc review: sink nguy hiểm cần comment giải thích (→12.7).
- **S6:** Khi "bị chèn script lạ": xác định lớp vỡ (escaping? CSP thiếu? third-party? dependency?) theo thứ tự §2.2/§2.6 — mỗi lớp có công cụ kiểm riêng; "cài lại" không phải phương án.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Script chèn chạy được | CSP thiếu/thất thoát | audit header; report-only | §2.2 |
| Token bị đánh cắp | localStorage + XSS | chuyển HttpOnly/BFF | §2.3 |
| Form bị gửi từ site khác | Thiếu SameSite/CSRF token | kiểm cookie attrs | §2.1 |
| Người dùng thấy dữ liệu người khác | Vary sai/serialize nhầm | cache audit (→6.5); props audit | §2.4 |
| npm package lạ tự thêm | CI không lockfile | npm ci + review SBOM | §2.5 |
| postMessage lộ dữ liệu | Không kiểm event.origin | audit message handler | §2.1 |

---

## 6. Cách đo

```bash
# Kiểm header an ninh hiện tại (từ ngoài):
curl -sI https://app.example.com | grep -iE 'content-security|x-frame|strict|set-cookie'

# Grep sink nguy hiểm trong repo (FE):
grep -rn 'dangerouslySetInnerHTML\|innerHTML\s*=\|eval(' src --include='*.tsx' --include='*.ts'
#   — mỗi kết quả cần chủ sở hữu + lý do; không có = nợ

# Đếm third-party: lọc request ngoài origin từ trang chủ (DevTools Network)
```

Nguyên tắc: **bảo mật FE đo được bằng grep + curl** — nếu không liệt kê được sink nguy hiểm và header hiện tại của bạn trong 5 phút, an ninh FE đang là "tôi tin là có".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay CSP strict:** CSP allow-list lỏng (dễ ra mắt, gần như vô nghĩa khi có XSS — chỉ chặn kiểu cũ); **thay BFF:** silent refresh trong storage (đơn giản hơn, rủi ro lộ cao hơn — hợp cho app rủi ro thấp).

Năm thấu kính:
- **Kinh tế:** Một sự cố XSS ở app thanh toán = chi phí pháp lý + uy tín lớn hơn toàn bộ chi phí CSP/Trusted Types của 5 năm; an ninh FE là bảo hiểm rẻ nhất hệ thống.
- **Vận hành:** Header an ninh cần được giám sát như config khác — có regression (deploy mới quên CSP); thêm test kiểm header trong CI (một dòng curl — §6).
- **An ninh:** Chuỗi tin FE: browser engine (SOP) → header (CSP) → framework (escaping) → code của bạn (sink) → third-party — chuỗi yếu ở mắt xích ít được soi nhất: thường là third-party và dependency.
- **Lịch sử:** Từ "HTML tĩnh vô hại" → XSS đặt tên (1999) → SOP→CSP (2012) → Trusted Types (2019) → passkey/BFF (2020s): 25 năm thu quyền của script về từng lớp whitelist — xu hướng không đổi và không kết thúc.
- **Người dùng:** Người dùng giao cho bạn nguyên một tab trình duyệt — quyền đọc mọi thứ họ gõ; chương này là danh sách những lời hứa bạn nên giữ một cách kiểm chứng được.

---

## 8. Đọc tiếp & bài tập

- Client security chung: **6.7** · Cache leak: **6.5** · Token/identity sâu hơn: **10.1** · Log hygiene: **11.5** · Supply chain ops: **11.7**
- **Bài tập 1:** Chạy curl ở §6 với trang chính bạn: ghi 5 header an ninh. Thiếu cái nào (CSP, HSTS, X-Content-Type, frame-ancestors, cookie flags)? Mỗi cái thiếu là một PR nhỏ.
- **Bài tập 2:** Grep sink nguy hiểm trên repo (lệnh §6). Mỗi kết quả: có justification không? Tổng số đó là "điểm mở" của bạn — theo dõi nó giảm dần theo quý như một metric.
- **Bài tập 3:** Thử chèn `<script>alert(1)</script>` vào mọi ô input của một form chính (kiểm thử xâm nhập cơ bản của chính bạn — có sự cho phép). Nơi nào alert chạy: đánh dấu theo lớp vỡ §2.2 — đó là danh sách sửa có thứ tự.
