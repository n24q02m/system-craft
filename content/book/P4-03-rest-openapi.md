# 4.3 — REST, JSON Schema & OpenAPI 3.2

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** p5-ch29-contracts.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 4.2 (ngữ nghĩa HTTP).

**Sợi chỉ đỏ:** *Hợp đồng tài nguyên cho đối tác — REST cùng OpenAPI mô tả thế nào cho máy đọc được?* — trả lời: hợp đồng cho đối tác cần đủ ba tầng — REST là bộ ràng buộc giữ hệ mở rộng được (stateless, cacheable, uniform interface), OpenAPI 3.2 là bản vẽ máy đọc được, và JSON Schema chạy trong CI là người gác cửa chặn breaking change trước khi merge. Câu hỏi để lại cho chương sau: *Nội bộ cần RPC hiệu năng và streaming — gRPC/protobuf đáng thêm một giao thức không?*

**Thuật ngữ sẽ gặp:** *ràng buộc REST* — sáu điều, ba cái hay bị bỏ: stateless, cacheable, uniform interface; *OpenAPI 3.2* — spec 2025 mô tả đường, tham số, response: hợp đồng thực thi được; *JSON Schema* — kiểu và ràng buộc từng trường: bỏ cả một lớp bug validate tay; *contract test* — CI sinh request từ spec, chặn schema vỡ ở pull request; *versioning schema* — phiên bản dữ liệu, phân biệt versioning đường API; *idempotent* — GET/PUT/DELETE lặp lại an toàn: nền cho retry của 4.8.

**Ví dụ mở đầu:** DM mở API cho 200 đối tác logistik. Trước OpenAPI: mỗi câu hỏi "trường này nullable không?" là một tin nhắn chờ team trả lời. Sau khi spec vào CI: SDK sinh tự động, pull request đổi tên trường mà quên nâng version bị máy chặn đỏ mặt ngay. Hợp đồng không phải tài liệu viết cho người đọc — là thứ máy thực thi được.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Contract-first hay code-first (và ai review) | Spec là nguồn chân lý hay tài liệu ch Retrofit? |
| 2 | OpenAPI 3.2 dùng tính mới (SSE, QUERY method) khi nào | User của tôi cần streaming + query phức tạp? |
| 3 | JSON Schema nghiêm đến đâu (additionalProperties, required) | Tôi muốn catch bug compile-time-ish ở đâu? |
| 4 | Sinh code/docs/mock từ spec (generator pipeline) | CI có fail khi spec-code lệch không? |

---

## 2. Cơ chế

### 2.1 REST: 6 ràng buộc, 3 cái thường bị bỏ

Resource URI + method ngữ nghĩa + status code + stateless + **cache** + **hypermedia (HATEOAS)**. Thực tế ngành: 3 đầu tuân thủ, hypermedia gần như không ai làm đủ — và không sao: giá trị chính của REST là **cấu trúc dễ đoán** (GET an toàn, PUT idempotent — →4.8), không phải giáo điều. Đừng tôn giáo hoá; cũng đừng "REST" mà POST /getUserList.

### 2.2 OpenAPI 3.2 (2025): hợp đồng thực thi được

Bản 3.2 đáng chú ý: mô tả **SSE** (không phải hack text/event-stream nữa), **QUERY method** (query phức tạp không còn b stuff vào URL), webhook và JSON Schema 2020-12 nền. Ứng dụng thực dụng: spec là **nguồn để**: (a) sinh client typed (tái sử dụng — giảm 12 bẫy →3.9), (b) mock server trước khi có backend (song song hoá team), (c) diff contract trong CI (phát hiện breaking change trước khi ship), (d) gateway validate request (400 sớm thay vì 500 sâu).

### 2.3 JSON Schema: loại bug cả một lớp

`required`, `additionalProperties: false`, `format: date-time` (UTC! — →1.9/3.9 bẫy 6), `pattern`, giới hạn length. Bật nghiêm ở **biên công khai** (client bên ngoài không kiểm soát được) và **biên tổ chức** (service khác team); lỏng hơn ở nội bộ tin cậy nếu cần tốc độ iterate. Chi phí: ~0,1–1 ms mỗi validate (I) — rẻ so với một bug dữ liệu tràn xuống DB.

### 2.4 Pipeline contract trong CI

```
spec.yaml ──> lint (spectral) ──> diff breaking (oasdiff) ──> sinh client (openapi-generator)
          └─> mock (prism) cho FE    └─> docs (redoc)          └─> test runtime khớp spec
```

Quy tắc vàng: **PR fail nếu**: spec vi phạm style guide, có breaking change không đánh version (→4.8), hoặc runtime response lệch spec (contract test). Đây là một trong vài đầu tư CI có lãi kép thật: giảm both bug và thời gian giao tiếp team.

### 2.5 Versioning schema (data) phân biệt versioning API (đường)

Field thêm (compatible) vs bỏ/đổi tên/đổi ngữ nghĩa (breaking). Nguyên tắc: **thêm tự do, xoá theo lịch** (deprecate header → metric usage → gỡ sau N quý — →4.8). Schema Registry (→4.7) làm đúng việc này cho sự kiện; OpenAPI diff làm cho REST.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| OpenAPI | 3.2 (09/2025) | V | SSE + QUERY + JSON Schema 2020-12 |
| JSON Schema | 2020-12 | V | |
| Validate cost | ~0,1–1 ms | I | tuỳ library |
| Sinh client | giảm bug biên | P | 12 bẫy →3.9 |

---

## 4. Suy luận kiến trúc

- **S1:** Hợp đồng là **biên sở hữu** — service có thể đổi nội thất tự do miễn biên không đổi; ngược lại mọi đổi bên trong thành coordinated deploy.
- **S2:** Tham số trụ: số breaking change lọt production, % endpoint có spec đúng, contract-test pass rate.
- **S3:** Strictness đổi an toàn lấy tốc độ iterate; generator đổi công thủ công lấy nhất quán — mức độ nên theo "ai dùng biên này".
- **S4:** Spec-as-code + AI (client sinh từ spec, spec sinh từ code, agent đọc spec làm tool — →12.5) làm hợp đồng có giá trị mới: máy đọc được là điều kiện của tự động hoá.
- **S5:** REST + OpenAPI vẫn là mặc định công khai; gRPC nội bộ (→4.4) — ranh giới ổn định; GraphQL chỗ cần linh hoạt client (→4.5).
- **S6:** Khi bug "hai bên hiểu khác nhau": thuốc nằm ở đây (schema nghiêm + contract test), không ở "gọi họ họp rõ hơn".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| FE/BE cãi nhau về response | Spec lệch runtime / không có | contract test trong CI | §2.4 |
| Breaking change sập client khác team | Không có diff gate | oasdiff trong PR | §2.5 |
| Dữ liệu bẩn vào DB | Không validate biên | JSON Schema strict | §2.3 |
| Docs cũ không ai tin | Docs viết tay, tách spec | sinh docs từ spec | §2.2 |
| 400 não lòng từ gateway | Validate + error chuẩn thiếu | RFC 9457 (→4.8) | §2.3 |

---

## 6. Cách đo

```bash
# Lint spec (style guide tổ chức)
npx @stoplight/spectral-cli lint openapi.yaml

# Diff breaking giữa 2 bản spec
npx @redocly/cli diff old.yaml new.yaml --format markdown

# Mock từ spec (test FE không cần BE)
npx @stoplight/prism-cli mock openapi.yaml

# Runtime khớp spec? (contract testing)
#   schemathesis / dredd — fuzz theo schema, tìm 500 thật
```

Nguyên tắc: **mọi artifact của hợp đồng sinh từ spec** (docs, mock, client, test) — viết tay một trong số đó là tạo thêm một nguồn chân lý thứ hai.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay contract-first:** code-first + sinh spec (Spring/FastAPI làm tốt) — nhanh hơn lúc đầu, rủi ro spec "đẹp hoá" code; hợp team nhỏ. **Thay JSON Schema:** protobuf/avro chặt hơn (→4.4/4.7) nhưng đổi cả stack; hoặc validation trong code — mất tính khai báo + test được.

Năm thấu kính:
- **Kinh tế:** Một contract test pipeline tiết kiệm hàng trăm giờ "debug giữa team"/năm — ROI khó thấy trên dashboard, dễ thấy trên retrospective.
- **Vận hành:** Spec nên sống **cùng repo** service (thay đổi nguyên tử) hoặc registry riêng (cần ownership rõ) — hai mô hình, chọn một, đừng lẫn.
- **An ninh:** Validate biên là lớp chống payload ác ý rẻ nhất (size limit, type strict, pattern) — trước cả authz logic (→10.4).
- **Lịch sử:** WSDL/SOAP từng là "contract-first" và chết vì nặng; REST thắng bằng nhẹ; OpenAPI là "lấy lại kỷ luật của WSDL không lấy lại đồ nghề nặng" — lịch sử không lặp, nhưng làm lại điệp khúc.
- **Người dùng:** Người dùng không thấy OpenAPI; họ thấy "API này dùng dễ, docs đúng, không đổi bất ngờ" — đó chính là sản phẩm của chương này.

---

## 8. Đọc tiếp & bài tập

- gRPC/protobuf: **4.4** · AsyncAPI/schema registry: **4.7** · Versioning + error: **4.8** · AI đọc spec làm tool: **12.5**
- **Bài tập 1:** Chạy `oasdiff` giữa spec hiện tại và 6 tháng trước của API chính. Danh sách breaking change lọt — mỗi cái một sự cố tiềm ẩn đã tránh được tương lai.
- **Bài tập 2:** Bật `additionalProperties: false` + `required` cho 1 endpoint quan trọng; chạy fuzz (schemathesis). Đếm bug tìm được trong giờ đầu.
- **Bài tập 3:** Kiểm tra docs public của bạn: sinh từ spec hay viết tay? Nếu viết tay — đo độ lệch bằng cách sinh docs từ spec và diff.
