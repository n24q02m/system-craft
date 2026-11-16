# 10.4 — An ninh Ứng dụng & API: OWASP Top 10:2025

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Bảo vệ · Kiểm thử
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 10.3 (vừa đọc) · 4.8 (API mặt tiền).

**Sợi chỉ đỏ:** *Lỗ hổng phổ biến nhất của web là gì — OWASP 2025 dạy gì cho DM?* — trả lời: OWASP 2025 — A01 Broken Access Control giữ ngôi số một (gộp cả SSRF), A03 Supply Chain mới lên, A10 Mishandling Exceptional Conditions mới vào; chương này khuyến nghị đổ 80% nỗ lực vào A01, coi A02 misconfiguration là "nghèo mà nguy hiểm", và đọc kèm bản đồ anh em API Security Top 10. Câu hỏi để lại cho chương sau: *Code của DM thật ra là của hàng nghìn package người khác — supply chain giữ sao?*

**Thuật ngữ sẽ gặp:** *A01:2025* — broken access control: đổi order_id trong URL đọc được đơn người khác, không cần exploit: giữ ngôi số một nhiều kỳ; *A03 supply chain* — hạng mới: code của bạn là của hàng nghìn người khác (nối 10.5); *A02 misconfiguration* — cấu hình sai, quyền mở, debug bật: nghèo mà nguy hiểm, quét tự động ra được; *A10 exceptional conditions* — mới 2025: hệ sập nửa chừng lộ dữ liệu trong thông báo lỗi; *API Top 10* — BOLA, BFLA: endpoint có bảng riêng vì tội danh riêng; *injection 2026* — framework giảm mạnh nhưng chưa chết: đăng ký lệnh trong dữ liệu vẫn là đường cũ.

**Ví dụ mở đầu:** Khách đổi một số trong URL của DM và thấy đơn của người khác — không cần công cụ hack nào, chỉ cần trình duyệt: đó là A01. Chặn ở API bằng authz, không phải ẩn nút ở UI. Chương này là bản đồ 2025 kèm thứ tự ưu tiên thực chiến.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | OWASP 10 hạng mục — tôi dọn theo thứ tự rủi ro nào | Ba hạng đầu của **tôi** là gì (theo dữ liệu pentest/audit, không theo số thứ tự)? |
| 2 | Validate input ở đâu (schema/edge/service/DB) | Tôi có một chỗ schema tin cậy không — hay mỗi layer tự đoán? |
| 3 | Webhook/callback ra vào kiểm soát thế nào (SSRF) | Server tôi fetch URL người dùng cung cấp — ai chặn 169.254.169.254? (I-065) |
| 4 | Báo lỗi & logging: fail-closed, không lộ stack | Lỗi của tôi nói gì với kẻ tấn công (và với tôi)? |

---

## 2. Cơ chế

### 2.1 Danh mục OWASP Top 10:2025 — bản đồ mới

Công bố 11/2025 (Global AppSec), phân tích ~589 CWE từ >2,8 triệu ứng dụng (I):

| # | Hạng mục | Chuyển động so 2021 |
|---|---|---|
| A01 | Broken Access Control (gồm cả **SSRF** nhập về đây) | giữ #1 |
| A02 | Security Misconfiguration | lên từ #5 |
| A03 | **Software Supply Chain Failures** | mới (mở rộng từ "Vulnerable Components") |
| A04 | Cryptographic Failures | xuống 2 bậc |
| A05 | Injection | xuống 2 bậc |
| A06 | Insecure Design | xuống 2 bậc |
| A07 | Authentication Failures | đổi tên |
| A08 | Software/Data Integrity Failures | giữ |
| A09 | Logging & **Alerting** Failures | đổi tên, nhấn mạnh cảnh báo |
| A10 | **Mishandling of Exceptional Conditions** | mới |

Đọc đúng: **A01 vẫn là vua** (3,7% app có CWE nhóm này (I)); injection tụt không phải vì hết — vì access control/misconfig phổ biến hơn; **supply chain lên #3** là trả lời thời đại (xáo trộn npm/pypi thật — →10.5); SSRF nằm trong A01: mọi "server fetch URL theo ý người dùng" là access control của chính server.

### 2.2 A01 thực chiến — 80% nỗ lực đáng bỏ vào đây

BOLA/IDOR (→10.3 §2.4): ownership trong query, test hai-user tự động. SSRF (I-065): webhook URL người dùng cung cấp — **allowlist scheme+host** (https + domain xác minh), **chặn IP nội bộ/metadata** (169.254.169.254, 10/8, 127/8...) ở tầng fetch (không tin DNS — rebind: resolve rồi kiểm IP, hoặc egress proxy chỉ tới public), response không trả thẳng về user (fetch → trích trường cần, không proxy nguyên trang). Privilege: kiểm ở **mọi** đường vào (HTTP + queue job + cron + admin script — quên đường phụ là lỗ hổng thật).

### 2.3 Injection 2026 — đã ít hơn nhưng chưa chết

SQLi: prepared statement/ORM là chuẩn — lỗi còn lại ở **query động** (ORDER BY nối chuỗi, search theo cột người chọn — allowlist cột). NoSQL/JSON injection (Mongo operator `$where`), **template injection** (render chuỗi người dùng như template), **format string/log injection** (newline vào log — fake log line), command injection ở script gọi `sh -c`. Bộ phòng: **một schema tin cậy ở biên** (OpenAPI + validator — →4.3; typed DTO — →3.x) — mọi thứ phía sau nhận dữ liệu đã định hình, không "string tù mù".

### 2.4 A02 Misconfiguration — nghèo mà nguy hiểm

CORS `*` kèm credentials (đã gặp 7.7), debug endpoint lộ (actuator/pprof không authn — pprof là kho vàng của kẻ tấn công), bucket storage public, header an ninh thiếu, quyền DB quá rộng (`SELECT *` mọi schema), default credential. Đối phó tư duy **IaC + audit**: cấu hình an toàn là code → review → CI kiểm (curl header check — 7.7 §6; CSPM scanner cloud). Misconfig là hạng "không ai cố tình làm sai" — nên giải pháp là **mặc định đúng** (platform/golden path — →9.6), không phải training.

### 2.5 A09+A10 — sự im lặng và sự sập nửa chừng

- **Logging & Alerting:** log đủ để điều tra (ai-gì-khi nào — →11.5) **và có alert thật** từ log an ninh (đăng nhập thất bại dồn, 403 đột biến, payload lạ) — log không ai đọc là camera không băng;
- **Mishandling exceptional conditions:** fail-open (lỗi validate → cho qua), leak stack trace tới user, transaction dở dang không rollback (→8.3), retry làm việc hai lần (→4.8 idempotency). Thiết kế lỗi là **con đường code** (error path được test như happy path — coverage nhánh lỗi trong CI).

### 2.6 API Security Top 10 — bản đồ anh em

Đối với API thuần: **API1 BOLA** · API2 Broken Auth · API3 Property-level authz (field/trường trả quá) · **API4 Unrestricted resource consumption** (không limit — →11.3) · API5 Function-level authz · API6 Sensitive business flows (scrape/abuse nghiệp vụ) · API7 SSRF · API8 Misconfig · **API9 Inventory** (API phiên bản cũ vẫn mở — →4.8 kill-switch) · API10 unsafe consumption của API bên thứ ba. Hai điểm thực chiến: GraphQL trả **đúng field theo quyền** (n+1 resolver có authz mỗi field — →4.5) và inventory: danh sách endpoint Version-X đang chạy là tài liệu an ninh.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| OWASP Top 10 | ấn bản 2025 (11/2025) | V | 589 CWE, 2,8M app |
| A01 tỷ lệ app | ~3,7% có CWE nhóm A01 | I | báo cáo OWASP |
| Metadata IP cloud | 169.254.169.254 | V | mục tiêu SSRF kinh điển |
| ASVS | checklist bảo mật theo cấp | V | OWASP |

---

## 4. Suy luận kiến trúc

- **S1:** An ninh app là **hợp đồng dữ liệu + ownership query + fail-closed** — ba thứ dựng ở kiến trúc; còn lại (pentest, scanner) là kiểm chứng, không phải thay thế.
- **S2:** Tham số trụ: số endpoint không qua schema validator, số fetch-theo-URL-người-dùng không chặn IP nội bộ, tỉ lệ error path có test, số alert an ninh hoạt động (không im).
- **S3:** Mặc định đúng (platform/golden path) thắng training cho misconfig — con người không thể là lớp phòng thủ chính của các hạng lặp lại.
- **S4:** SSRF là access control "server tự truy cập" — cùng engine policy (allowlist) như authz thường; webhook = tính năng nguy hiểm nhất phổ biến nhất (I-065 gần như mọi SaaS có webhook đều từng có).
- **S5:** AI mở hai mặt mới (→12.7): **prompt injection** (ngữ liệu người dùng điều khiển agent — coi như injection thế hệ mới: untrusted input vào lệnh), và **API consumption** (agent gọi ồ ạt — rate limit per actor). A05 không chết — đổi chất liệu.
- **S6:** Khi pentest báo lỗi: xếp hạng theo **đường khai thác tới tài sản** (A01/BOLA > phần lớn còn lại) — sửa theo lộ trình kẻ tấn công, không theo thứ tự report.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Webhook quét nội mạng (I-065) | Fetch URL không chặn IP private | egress allowlist + resolve-then-check | §2.2 |
| Cloud credential bị lấy qua SSRF | Metadata endpoint truy cập được | chặn 169.254.169.254 + IMDSv2 | §2.2 |
| Sửa `?id=` thấy data người khác | BOLA | ownership query + test | §2.2 |
| Log có dòng "giả" | Log injection (newline) | sanitize khi ghi + parse nghiêm | §2.3 |
| Lỗi validate → cho qua (fail-open) | Exception handling sai | fail-closed + test error path | §2.5 |
| API v1 cũ vẫn mở | Inventory không quản | kill-switch + danh sách endpoint | §2.6 |

---

## 6. Cách đo

```bash
# SSRF check (tự test webhook của bạn — có cho phép):
#   đặt webhook URL = http://169.254.169.254/latest/meta-data/  (đúng cú pháp cloud bạn)
#   → server bạn fetch và trả về gì? Trả "blocked" = qua; trả JSON metadata = I-065 sống

# Scanner nền tảng (CI): zap baseline / nuclei với template OWASP —
#   chạy mỗi đêm cho môi trường staging; mỗi finding có owner + hạn
```

Nguyên tắc: **kiểm tra an ninh tự động hoá như test chức năng** — an ninh không phải sự kiện pentest năm một lần; pentest xác nhận, pipeline phòng thủ.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự viết validator/policy:** gateway/API layer có sẵn (→9.4: schema validate + rate limit + WAF ở một chỗ); **thay pentest nội bộ:** thuê ngoài định kỳ (mắt mới bắt bias — hợp lệ như một lớp, đừng dùng như lớp duy nhất).

Năm thấu kính:
- **Kinh tế:** Chi phí sửa theo hạng: misconfig (giờ) < injection (ngày) < access control sai kiến trúc (tuần); bảng OWASP là bảng chi phí ưu tiên ngầm — đọc như budget không phải như danh vinh dự.
- **Vận hành:** Mỗi hạng có checklist CI tương ứng (header check, IDOR test, dependency scan) — "an ninh chuyển trái" (shift-left) y như testing đã đi (→7.6).
- **An ninh:** A03 (supply chain) là hạng duy nhất **bên ngoài code bạn** — muốn quản được phải có chương riêng (→10.5); các hạng khác là kỷ luật code, hạng này là kỷ thái hệ sinh thái.
- **Lịch sử:** 2003 (SQLi #1) → 2010 (injection vẫn #1) → 2017 (injection #1, broken auth #2) → 2021 (access control nhảy #1) → 2025 (giữ #1, supply chain #3): 20 năm công cụ tốt hơn (ORM, framework) đẩy injection xuống — mỗi hạng mục tụt là một thắng lợi kỹ thuật được ghi nhận bằng thống kê.
- **Người dùng:** Người dùng trao app của bạn dữ liệu đời thật — căn cước, tiền, sức khoẻ; Top 10 là danh sách **20 cách phổ biến nhất xé lời hứa đó**; đọc nó mỗi năm là văn hoá tối thiểu của nghề.

---

## 8. Đọc tiếp & bài tập

- Supply chain: **10.5** · AuthN/Z chi tiết: **10.3** · FE/TLS defense: **7.7, 4.1** · Rate limit: **11.3** · API đời sống/inventory: **4.8** · Prompt injection: **12.7**
- **Bài tập 1:** Chạy SSRF check §6 với webhook của bạn. Ghi kết quả; nếu fetch được nội bộ — đó là ticket "ngay hôm nay" kèm bằng chứng tái lập.
- **Bài tập 2:** Xếp lại Top 10 **của riêng bạn**: cột hạng OWASP, cột "bằng chứng hệ tôi" (pentest/scanner/log). Hàng nào không có bằng chứng cả hai chiều ("có lỗi" hoặc "đã kiểm, sạch") là mù — chọn 3 hàng đầu làm quý này.
- **Bài tập 3:** Thêm IDOR test hai-user vào CI cho 5 endpoint giàu dữ liệu nhất (→10.3 §6). Chạy một tuần — mỗi fail là một A01 đang chờ người tình cờ (hoặc không tình cờ) quét `/api/.../1234`.
