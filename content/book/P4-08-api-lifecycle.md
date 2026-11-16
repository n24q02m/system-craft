# 4.8 — Vòng đời API: Versioning, Idempotency-Key, Rate Limit, Webhooks, RFC 9457

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Thiết kế · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.3 · 4.7 (compatibility).

**Sợi chỉ đỏ:** *API đã công khai — sống mãi à: version, deprecate, idempotency cho đối tác là gì?* — trả lời: API công khai là lời hứa sống mãi — nên cần version theo ba trường phái và một nguyên tắc "không phá mà không báo", Idempotency-Key cho POST an toàn retry, pagination cursor cho tập dữ liệu lớn, lỗi chuẩn RFC 9457 cho máy xử lý được. Câu hỏi để lại cho chương sau: *Nhìn lại toàn cảnh: cặp nào nói chuyện bằng gì — có ma trận quyết định không?*

**Thuật ngữ sẽ gặp:** *deprecation window* — hai version sống song song một thời gian, kèm header cảnh báo; *Idempotency-Key* — client gửi khoá, server nhớ kết quả: retry không tạo hai đơn; *cursor pagination* — con trỏ "đọc tới đâu": tốc độ đều, sống với dữ liệu đang đổi; *offset pagination* — nhảy theo trang: đơn giản nhưng trang cuối chậm dần; *rate limiting* — token bucket + header báo hạn mức còn lại; *RFC 9457* — problem details: lỗi có type, title, detail chuẩn để code xử lý thay vì parse chuỗi.

**Ví dụ mở đầu:** Đối tác của DM retry tạo đơn vì timeout mạng — không Idempotency-Key: hai đơn, một khách, một cú điện thoại giận. Cùng tuần, crawl của đối tác duyệt tới trang sâu bằng offset: query chậm dần, DB nóng lên. Cả hai đều sửa được bằng một dòng ở chương này — nhưng phải gọi đúng tên vấn đề trước.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Chiến lược versioning (URI /v2, header, date-based) + chính sách deprecate | Tôi có thể bỏ version cũ sau bao lâu — và biết ai còn dùng không? |
| 2 | Idempotency-Key cho POST có hiệu ứng (đặt hàng/thanh toán) | Retry mạng có làm khách trả 2 lần không (→8.5)? |
| 3 | Pagination chuẩn (cursor/keyset) + rate limit (theo tenant/IP/token) | Danh sách tôi sắp to — offset chết ở đâu? Ai được gọi bao nhiêu? |
| 4 | Chuẩn lỗi RFC 9457 + webhook có ký + retry | Client xử lý lỗi được không? Webhook của tôi bị mạo danh/spam được không? |

---

## 2. Cơ chế

### 2.1 Versioning: ba trường phái và một nguyên tắc

- **URI (/v2/...):** trong mặt, cache thân thiện, dễ route — xấu URL; phổ biến nhất;
- **Header (Accept version):** sạch URL, khó debug/route — ít dùng;
- **Date-based (Stripe-style):** thanh lịch cho API lớn nhiều version song song.

Nguyên tắc quan trọng hơn trường phái: **mọi đổi breaking đều qua version mới + version cũ có đồng hồ đếm ngược**. Metric usage per version là điều kiện sống còn — không có nó, "deprecate" là lời hứa không thể kiểm chứng. Quy trình chuẩn: header `Deprecation` + `Sunset` (RFC 8594) → email/metric → gỡ sau N quý (N công bố trong policy, không đổi đơn phương).

### 2.2 Idempotency-Key: lớp cứu mạng cho POST

Client gửi `Idempotency-Key: <uuid>` với request có hiệu ứng; server: (1) thấy key đã xử lý → trả **kết quả cũ** (không thực hiện lại); (2) thấy key đang xử lý → trả 409/chờ; (3) key mới → xử lý + lưu kết quả (TTL 24h+). Lưu trạng thái, không chỉ flag — response replay được. **Bắt buộc cho:** thanh toán, đặt hàng, tạo tài nguyên tốn kém. Kết hợp retry có jitter (→8.5) tạo lớp an toàn: khách bấm 2 lần, mạng retry 3 lần — vẫn 1 đơn hàng. Stripe chuẩn hoá pattern này (V).

### 2.3 Pagination: offset vs cursor — quyết định 1 dòng, hệ quả triệu

`offset` (skip 10000 limit 20): đơn giản, nhưng (a) DB phải scan + bỏ (O(n)), (b) **item chèn giữa → trang lặp/mất**. `cursor/keyset` (`WHERE id > last ORDER BY id LIMIT 20`): O(log n) index seek, ổn định qua insert. Quy tắc: **public API → cursor mặc định**; offset chỉ cho internal admin nhỏ. Stable sort bắt buộc (→3.9 bẫy 8): thêm tie-break key duy nhất.

### 2.4 Rate limiting: thuật toán + chiều giới hạn

- **Token bucket:** burst được, refill đều — mặc định tốt;
- **Sliding window:** chính xác, tốn bộ nhớ hơn;
- **Fixed window:** rẻ, méo ở biên cửa sổ.

Chiếu giới hạn theo **tenant/token > IP > global** (IP NAT nhiều user — →9.3 NAT bill). Response chuẩn: `429` + `Retry-After` + headers `X-RateLimit-*`. Về placement: gateway/ingress (đồng loạt — →9.4) hoặc service (chi tiết) — thường cả hai tầng: tầng gateway thô (an ninh), tầng service tinh (nghiệp vụ).

### 2.5 Lỗi chuẩn RFC 9457 + Webhooks an toàn

**RFC 9457 Problem Details** (thay RFC 7807, 2024): body JSON `type/title/detail/status/instance` + extensions — client xử lý lỗi theo máy được, không parse message tiếng người. Quy tắc: 5xx không lộ stack; 4xx mang `errors[]` field-level khi validate.

**Webhook outbound (tôi là người gửi):** ký HMAC mỗi payload (`X-Signature`), timestamp + nonce chống replay (→10.5), retry có backoff + jitter, dead-letter sau N lần (→5.7), endpoint của khách verify URL (SSRF — →10.4). Inbound (tôi nhận): verify chữ ký **trước** mọi xử lý, idempotent theo event id.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| Deprecation headers | RFC 8594 (Sunset) | V | |
| Problem details | RFC 9457 (2024) | V | thay 7807 |
| Idempotency TTL | 24h+ (Stripe-style) | V | theo nghiệp vụ |
| Cursor vs offset tại 1M rows | ms vs s | I | phụ thuộc index |
| Rate limit response | 429 + Retry-After | V | HTTP sem |

---

## 4. Suy luận kiến trúc

- **S1:** Vòng đời API là **hợp đồng dài hạn với người không kiểm soát được** (client ngoài) — mọi tiện hôm nay phải trả bằng deprecation ngày mai.
- **S2:** Tham số trụ: usage per version, idempotency replay hit, 429 theo tenant, webhook failure rate.
- **S3:** URI version đổi cache cho đổi tooling; cursor đổi đơn giản client cho scale; mỗi lựa chọn "điều gì được đổi lấy gì" phải ghi ra policy công khai.
- **S4:** AI agent đang thành client API mới (→12.5) — chúng cần: schema khai báo (→4.3), lỗi máy đọc được (9457), rate limit rõ — chính ba thứ chương này.
- **S5:** Idempotency + rate limit + error chuẩn là "bộ ba vệ sinh" tách API nghiệp dư khỏi API sản phẩm — ít nơi đầu tư đúng mức, mọi nơi trả giá.
- **S6:** Khi "client dùng sai API": hỏi đã cho họ cách dùng đúng chưa (schema, error chuẩn, doc sinh tự động) — trước khi đổ lỗi.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Trừ tiền/lập đơn 2 lần | POST không idempotent + retry | audit Idempotency-Key | §2.2 |
| Danh sách lặp/mất item khi phân trang | Offset + insert song song | đổi cursor | §2.3 |
| Một tenant dập API của mọi người | Rate limit sai chiều (IP toàn cụm) | limit theo tenant | §2.4 |
| Client không hiểu lỗi 500 | Lỗi tự chế/string | RFC 9457 | §2.5 |
| Webhook bị spam/mạo danh | Không verify HMAC + timestamp | audit chữ ký | §2.5 |
| Không dám gỡ /v1 | Không có metric usage per version | access log theo version | §2.1 |

---

## 6. Cách đo

```bash
# Usage per version (điều kiện sống còn để deprecate)
#   access log: group by version prefix — vẽ 90 ngày

# Idempotency hoạt động thật không (test replay):
curl -X POST https://api/orders -H 'Idempotency-Key: test-123' -d '{...}'   # 2 lần
#   mong đợi: cùng order id, 1 bản ghi DB

# Rate limit headers + hành vi:
curl -s -D- -o /dev/null https://api/x   # X-RateLimit-* hiện?

# Webhook tự gửi: verify chữ ký bằng chính secret (round-trip test)
```

Nguyên tắc: **mọi chính sách vòng đời phải có metric chứng minh nó được tuân theo** — deprecate không đo được là giấc mơ, không phải quy trình.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay versioning:** thiết kế additive-only (chỉ thêm field — →4.3/4.4) + deprecate field — đẩy versioning xuống thấp nhất có thể; chỉ breaking khi thật sự không còn lối. **Thay idempotency server-side:** client-side "check-then-create" — **không thay được** (race); idempotency là thuộc tính server. **Thay rate limit tự làm:** gateway có sẵn (→9.4) + quota plan.

Năm thấu kính:
- **Kinh tế:** Mỗi version API song song = chi phí duy trì nhân bản; metric usage là công cụ "hạ giá" version cũ đúng lúc — tiết kiệm đo được theo quý.
- **Vận hành:** Sunset header + changelog tự sinh từ spec diff — deprecate thành quy trình máy thay vì chiến dịch email.
- **An ninh:** Rate limit là lớp chống DoS ứng dụng rẻ nhất; webhook HMAC là lớp duy nhất chống mạo danh cuộc gọi "từ bạn".
- **Lịch sử:** Idempotency-Key (Stripe ~2016) và Problem Details (7807→9457) cho thấy: tiêu chuẩn nhỏ đúng chỗ giải quyết cả lớp đau — "best practice" thật sự lan bằng hữu dụng, không bằng tiếng ồn.
- **Người dùng:** Khách không biết 9457 là gì — nhưng họ biết "bấm 2 lần vẫn 1 đơn" và "app báo lỗi rõ ràng thay vì đỏ lửa". Đó là hai lời hứa chương này giữ.

---

## 8. Đọc tiếp & bài tập

- Retry/bão: **8.5** · Schema/versioning: **4.3, 4.7** · Webhook SSRF: **10.4** · Gateway rate limit: **9.4** · API cho agent: **12.5**
- **Bài tập 1:** Chọn POST quan trọng nhất của hệ thống; gửi 2 lần cùng Idempotency-Key (nếu hỗ trợ). 2 bản ghi DB = bug P1 chưa ai lập ticket.
- **Bài tập 2:** Vẽ usage theo version API chính, 90 ngày. Version nào = 0 request 30 ngày liền? Đó là ứng viên Sunset đầu tiên.
- **Bài tập 3:** Gửi 200 request trong 5 giây từ 1 token. Không thấy 429? Rate limit của bạn là trang trí — đó là phát hiện đáng giá hơn cả bài tập.
