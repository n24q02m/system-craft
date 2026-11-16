# 10.3 — AuthN & AuthZ: OAuth 2.1, Passkeys, RBAC/ABAC/ReBAC

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Chọn · Bảo vệ
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 6.7 (token nằm đâu — đã gặp) · 5.14 (tenant là câu hỏi quyền).

**Sợi chỉ đỏ:** *Ai là ai, được làm gì — authn/authz và token xử lý thế nào cho 4 triệu user?* — trả lời: ai là ai (AuthN) và được làm gì (AuthZ) cho 4 triệu user — quyết định định hình mọi thứ là session hay JWT, vì nó quyết định "thu hồi được không"; AuthZ có ba mô hình chọn theo câu hỏi của tổ chức; danh tính nội bộ là vòng đời SSO, SCIM, JIT. Câu hỏi để lại cho chương sau: *Lỗ hổng phổ biến nhất của web là gì — OWASP 2025 dạy gì cho DM?*

**Thuật ngữ sẽ gặp:** *AuthN vs AuthZ* — chứng minh danh tính rồi mới quyết định quyền: hai vấn đề khác nhau, hai hệ khác nhau; *session vs JWT* — server giữ phiên (thu hồi tức thì) hay token tự chứa (chết khi hết hạn): định hình mọi thứ phía sau; *RBAC/ABAC/ReBAC* — vai trò, thuộc tính, quan hệ: ba mô hình AuthZ; *UI đi kèm dữ liệu* — ẩn nút không đủ: API phải chặn đúng như UI (nối 6.7, 5.14); *SSO + SCIM + JIT* — một cửa đăng nhập, cấp gỡ quyền tự động, quyền đúng lúc: vòng đời danh tính nội bộ;

**Ví dụ mở đầu:** Khách DM mất điện thoại: "đăng xuất mọi thiết bị" phải có hiệu lực trong vài giây — session làm được, JWT phải chờ hoặc có blacklist. Nhân viên nghỉ việc 10h sáng: SCIM gỡ quyền trước 10h05. Chương này chọn mô hình theo hai câu: thu hồi nhanh cỡ nào, ai giữ quyền.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | AuthN flow: OAuth 2.1 + PKCE, passkeys, device flow, mTLS | Ai đăng nhập, từ thiết bị gì, mức bảo đảm cần bao nhiêu? |
| 2 | Session vs JWT (server-side session? thu hồi được?) | Token của tôi lộ — tôi tắt được trong bao lâu? (I-064) |
| 3 | Mô hình phân quyền: RBAC / ABAC / ReBAC | "Ai được làm gì với cái gì" — biểu diễn bằng gì cho đúng tổ chức tôi? |
| 4 | Đơn giản hoá danh tính (SSO, scim, jit) | Nhân viên mới có đủ quyền trong ngày đầu, và nghỉ việc mất quyền trong giờ? |

---

## 2. Cơ chế

### 2.1 AuthN 2026 — bộ chuẩn tiêu dùng

- **OAuth 2.1 + PKCE** cho ủy quyền/app (implicit flow & ROPC chết — 2.1 gộp các RFC sửa lỗi; mọi client — kể cả "bí mật" — đều PKCE);
- **OIDC** trên OAuth để đăng nhập chuẩn hoá (id_token, discovery);
- **Passkey/FIDO2/WebAuthn** chống phishing bằng bản chất (khoá gắn origin — →6.7): mặc định 2026 cho consumer; mật khẩu còn lại phải kèm rate limit + Argon2id (→10.2);
- **Device flow** cho TV/thiết bị không bàn phím; **mTLS/certificate** cho machine-to-machine cao cấp; **workload identity** cho service (→10.6).

### 2.2 Session vs JWT — quyết định "thu hồi" định hình mọi thứ

| | Server-side session (cookie + store) | JWT tự chứa |
|---|---|---|
| Kiểm tra | tra store mỗi request (nhanh nếu local/redis) | verify chữ ký (không cần gọi ai) |
| Thu hồi | **xoá khỏi store = tức thì** | khó (token còn hạn còn dùng được) |
| Trạng thái | centralized | distributed dễ |
| Phù hợp | web app, quyền hay đổi | service-to-service ngắn hạn, claim ổn định |

Thực chiến chuẩn: **access token ngắn (phút) + refresh token có thể thu hồi** (reference token lưu store) —Jwt như "vé xe 5 phút": tự chứa nhưng ngắn đến mức lộ cũng kịp chết; refresh là "tấm vé dài" có thể bị hủy. Phải có **logout thật** (xoá refresh + đưa access vào denylist ngắn) — không có là I-064 ("token leak không thu hồi nổi").

### 2.3 AuthZ — ba mô hình, chọn theo "câu hỏi của tổ chức"

- **RBAC** (role: admin/editor/viewer): đơn giản, đủ khi quyền theo **chức năng**; chết khi "editor của phòng A" ≠ "editor của phòng B";
- **ABAC** (thuộc tính: `user.dept == doc.dept && user.level >= 3`): quyền theo **ngữ cảnh** (địa điểm, loại thiết bị, nhạy cảm dữ liệu) — linh hoạt, khó debug ("tại sao tôi không thấy?" cần engine giải thích);
- **ReBAC** (quan hệ — Zanzibar-style: "owner của document cha có quyền con"): khi hệ là **đồ thị** (org/team/folder/file — Google Drive-style); zanzibar-likes (SpiceDB/OpenFGA) phổ quát hoá mô hình này.

Thực chiến: **RBAC cho khung + ABAC cho ngoại lệ theo ngữ cảnh + ReBAC nếu sản phẩm có cấu trúc cha-con chia sẻ**. Bất biến mọi mô hình: **decision point một chỗ** (library/middleware — không rải if-else 47 nơi) + **audit mọi quyết định từ chối** (vừa an ninh vừa debug).

### 2.4 Phân quyền dữ liệu đi cùng phân quyền giao diện

Vấn đề số một thực tế (OWASP A01:2025 — →10.4) là **BOLA/IDOR**: object-level — `/api/orders/12345` của người khác. Phòng: **kiểm tra ownership trong query** (`WHERE id=? AND tenant_id=?` — →5.14 RLS là cơ chế của chuẩn này), không phải "endpoint kiểm tra rồi query theo id trần"; test tự động hóa IDOR (hai user thử đọc của nhau — thêm vào E2E). UUID làm id **không phải** kiểm soát truy cập (chỉ làm khó đoán — obscurity).

### 2.5 SSO + SCIM + JIT — vòng đời danh tính

IdP tập trung (SSO) + **SCIM** (tự động tạo/xoá tài khoản theo HR system) + **JIT** (cấp quyền khi dùng lần đầu, gắn sự kiện) + **access review định kỳ** (chủ sở hữu xác nhận còn cần quyền — thứ tự thực tiễn: tắt quyền nghỉ việc < 1 giờ là mục tiêu tối thiểu, review quý cho quyền nhạy). Mọi ứng dụng nội bộ nên **không có mật khẩu riêng** — một IdP để chăm (đổi một chỗ), thay vì 50 app mỗi cái một tuổi thọ mật khẩu.

### 2.6 Đo danh tính an toàn

Metric: **MTTR-thu hồi** (phát hiện → token chết), tỉ lệ quyền không qua review > 90 ngày, số app có mật khẩu riêng (→0), tỉ lệ login bằng passkey (mục tiêu tăng), số quyết định từ chối không giải thích được (chất lượng policy). Đăng nhập an toàn vẫn **đo được bằng UX**: thời gian đăng nhập trung bình — an ninh tốt không phải chậm.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| OAuth 2.1 | draft ổn định, best-practice gộp | V | PKCE bắt buộc |
| Passkey | hỗ trợ nền tảng lớn đầy đủ | V | 2024+ |
| Access token TTL | phút–giờ | P | |
| MTTR thu hồi token | mục tiêu < 5 phút | P | I-064 |
| SCIM | RFC 7644 | V | |

---

## 4. Suy luận kiến trúc

- **S1:** AuthN/AuthZ là **nền của zero trust** (→10.1): mọi chương khác (mesh mTLS, RLS, gateway) tiêu thụ sản phẩm của chương này — đầu tư IdP/policy engine là đầu tư hạ tầng dùng lại toàn hệ.
- **S2:** Tham số trụ: MTTR thu hồi, tỉ lệ endpoint kiểm ownership trong query (audit), số điểm quyết định authz (nên = 1), passkey adoption.
- **S3:** JWT đổi phân tán/thu hồi chậm lấy không-điện-thoại; session đối nghịch — chọn theo **thời gian sống ngắn + thu hồi được ở một điểm nào đó trong chuỗi**; hệ lớn dùng cả hai (access JWT + refresh reference).
- **S4:** ReBAC engine (Zanzibar-style) là "DB quan hệ quyền" — khi sản phẩm có chia sẻ lồng nhau thì tự viết check quan hệ rải rác là nợ; engine tách và cache được (→5.x tư duy tương tự).
- **S5:** Agent AI (→12.7) cần **danh tính riêng với scope hẹp** — kế thừa token user cho agent nền là lỗi thiết kế 2026 phổ biến nhất của hệ có AI; audit theo actor (human vs agent) ngay từ schema log.
- **S6:** Khi "người dùng thấy thứ không nên thấy": tra BOLA trước (§2.4 — query thiếu ownership), rồi policy engine (sai mô hình), rồi UI (hiển thị sai dữ liệu đúng quyền) — theo thứ tự tần suất thực tế.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Token lộ không tắt được (I-064) | JWT dài hạn không denylist | refresh reference + logout thật | §2.2 |
| Đọc được order của người khác | BOLA/IDOR | audit query ownership | §2.4 |
| "Tại sao tôi không có quyền?" | Policy rải rác khó giải thích | decision point một chỗ + engine giải thích | §2.3 |
| Nhân viên nghỉ vẫn vào được | Không SCIM/offboard | SSO + SCIM + review | §2.5 |
| Phishing chiếm tài khoản | Mật khẩu thuần | passkey + MFA | §2.1 |
| Đăng nhập chậm/mệt mỏi | Mỗi app mật khẩu riêng | SSO IdP | §2.5 |

---

## 6. Cách đo

```bash
# IDOR smoke test (hai user thử đọc của nhau — tự động):
#   U1 tạo object; U2 thử GET /api/objects/<U1-id> → kỳ vọng 403/404, không 200

# Audit điểm quyết định: grep codebase "isAdmin\|hasRole\|can(" —
#   đếm file xuất hiện quyết định; > một vài file = policy rải rác
```

Nguyên tắc: **mọi endpoint nhạy cảm qua cùng một câu hỏi kiểm tra** ("ai, với vai trò gì, sở hữu object này?") — nếu phải nghĩ mới biết hỏi ở đâu, thiết kế đã thất bại.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự dựng AuthZ:** engine open-source (OpenFGA/SpiceDB) hoặc Keycloak/Ory/Auth0 managed — mua ngay tính năng review/audit mình mất quý viết; **thay passkey:** MFA OTP (vẫn tốt, kém chống phishing); mật khẩu thuần + rate limit chỉ cho hệ rủi ro thấp.

Năm thấu kính:
- **Kinh tế:** Một IdP + SCIM tiết kiệm giờ IT theo **tỷ lệ với số app × số nhân viên**; chi phí "quên offboard" là một sự cố báo chí — ROI của chương này dễ thuyết phục nhất trong toàn bộ an ninh.
- **Vận hành:** Access review là nợ ngược (nợ quyền): mỗi quý không review là lãi cộng dồn; đặt lịch như drain node — nhàm chá, định kỳ, đo được.
- **An ninh:** Chuỗi danh tính là chuỗi dài nhất hệ thống (HR → IdP → token → query) — mỗi mắt xích tự động hoá được là một mắt xích không quên được; "quên" là con đường lộ quyền số một.
- **Lịch sử:** Mật khẩu (1960s, multiuser mainframe) → LDAP/AD (1990s) → SAML (2002, doanh nghiệp) → OAuth/OIDC (2012–14, mobile/SaaS) → passkey (2022+, chống phishing bằng mật mã) → delegated agent identity (2026+): mỗi thế hệ đẩy gốc tin từ "cái gì người biết" xuống "cái gì người giữ" xuống "cái gì thiết bị chứng minh".
- **Người dùng:** Người dùng muốn "vào nhanh, không bị hỏi lắm, không bị hack" — ba mong muốn mâu thuẫn; passkey + SSO là điểm cân bằng tốt nhất lịch sử tới giờ, và chương này là cách dựng nó.

---

## 8. Đọc tiếp & bài tập

- Client & attestation: **6.7** · FE token: **7.7** · RLS/tenant: **5.14** · Threat model: **10.1** · Workload ID: **10.6** · Agent identity: **12.7**
- **Bài tập 1:** Đo MTTR thu hồi: ở staging, lộ một token, bấm giờ tới khi nó chết thật (đăng xuất + denylist). > 5 phút? I-064 đang chờ ngày của nó.
- **Bài tập 2:** Viết IDOR smoke test (§6) cho 10 endpoint chính, chạy trong CI. Đếm endpoint fail — mỗi cái là lỗ hổng A01:2025 nguyên mẫu.
- **Bài tập 3:** Đếm điểm quyết định authz trong code (grep §6). Vẽ kế hoạch gom về một middleware/library trong sprint tới — đó là refactoring an ninh đáng giá nhất của năm.

