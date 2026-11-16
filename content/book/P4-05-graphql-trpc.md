# 4.5 — Truy vấn Linh hoạt & BFF: GraphQL (Federation) & tRPC

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** p5-ch30-graphql.md

---

## 0. Nhập môn

**Đọc trước:** 4.3 · 4.4 (đối trọng RPC).

**Sợi chỉ đỏ:** *Mỗi client cần một mẩu dữ liệu khác nhau — GraphQL có giải hay có thêm vấn đề?* — trả lời: GraphQL cho mỗi client tự chọn mẩu dữ liệu — hết over-fetch — nhưng đổi lại N+1 và query lồng sâu; production cần đủ bộ vệ sinh (depth limit, cost limit, persisted query) và DataLoader, nếu không thì vấn đề chỉ di chuyển chứ không biến mất. Câu hỏi để lại cho chương sau: *Đơn đổi trạng thái liên tục — đẩy realtime qua SSE/WebSocket/WebTransport thế nào cho tin?*

**Thuật ngữ sẽ gặp:** *over-fetch/under-fetch* — lôi cả thứ không cần, hoặc gọi nhiều lần mới đủ mẩu cần; *resolver* — hàm trả từng trường: chỗ N+1 nấp; *N+1* — một query lồng tạo nhiều vòng ra DB; *DataLoader* — gom các resolver cùng nhịp thành một truy vấn batch; *depth/cost limit* — chặn query lồng sâu hoặc đắt bất thường: hai van bắt buộc; *federation* — nhiều service góp vào một supergraph: GraphQL của microservice.

**Ví dụ mở đầu:** App mobile của DM cần tên món với giá; web cần thêm mô tả, ảnh, đánh giá. Thời REST: ba endpoint chật vật, mobile vẫn tải dư. GraphQL: mỗi màn hình một query đúng mẩu cần. Đêm đầu production: một query lồng 7 tầng làm DB spike — vì không ai đặt cost limit. Chương này trao đủ bộ công cụ vệ sinh, không chỉ phần đẹp.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | GraphQL cho ai: public API hay chỉ BFF nội bộ | Tôi cần linh hoạt client hay tôi đang "theo trend"? |
| 2 | Giới hạn độ sâu/chi phí truy vấn (depth & cost limit) | Một query {$__typename × đệ quy} có đốt được máy tôi không? |
| 3 | Persisted queries cho production public | Client có bị phép gửi query text tuỳ ý không? |
| 4 | DataLoader/N+1 ở mọi resolver | Batch + cache per-request đã mặc định chưa (→5.2 N+1)? |

---

## 2. Cơ chế

### 2.1 GraphQL giải bài toán gì (và không giải gì)

Client khai báo **đúng dữ liệu cần** trong 1 round-trip; server trả đúng shape. Hết: over-fetch (REST trả 40 field, FE dùng 3), under-fetch (FE gọi 4 endpoint ghép), versioning field-level (thay đổi từng field thay vì cả endpoint). Không giải: quyền truy cập theo field (phải tự làm), cache HTTP (POST — mất cache chuẩn →5.4), chi phí server (query phức tạp = join phức tạp).

### 2.2 Ba công cụ vệ sinh bắt buộc production

1. **Depth/cost limit:** query lồng không giới hạn = đồ họa đệ quy đánh server; giới hạn theo "điểm" gán cho field;
2. **Persisted queries:** client gửi **hash** của query đã đăng ký trước — không query text tuỳ ý: hết attack surface, hết query "quên xóa" nặng nề, được cache CDN (GET + hash);
3. **Introspection off ở production công khai** (map schema cho kẻ tấn công).

Không có 3 cái này mà mở GraphQL public = tự mở cửa DoS.

### 2.3 N+1: bẫy số một của GraphQL (và DataLoader là thuốc)

Resolver lồng: mỗi item gọi DB riêng → 1 request GraphQL thành **hàng trăm query** (→5.2 N+1). DataLoader: gom batch trong một tick + memo per-request. Kinh nghiệm vận hành: bật logging đếm query/request ở dev — N+1 phát hiện trong 5 phút, không phải 5 tuần.

### 2.4 Federation: microservice GraphQL

Mỗi service góp subgraph; **gateway** dựng schema thống nhất (Apollo Federation/Router, GraphQL Hive). Giá trị: team tự chủ schema, client 1 endpoint. Chi phí: một lớp gateway nữa phải vận hành + xử lý **entity ownership** qua service. Khi nào: ≥ 3–4 service + client đa dạng (web/mobile/TV) — ít hơn thì 1 monolith GraphQL (hoặc REST+BFF) thường rẻ hơn.

### 2.5 tRPC: "GraphQL của TypeScript trọn gói"

tRPC: FE/BE **cùng TypeScript** — procedure gọi như hàm, type infer trọn (không schema riêng, không codegen). Dùng đúng: product nội bộ TS trọn gói (Next.js full-stack) — năng suất rất cao. Hạn chế: biên chỉ cho TS (client khác ngôn ngữ không có); công khai vẫn cần OpenAPI (tRPC có plugin sinh — nhưng không phải trọng tâm). **Quy tắc: tRPC cho "một team hai tay", GraphQL/OpenAPI cho "nhiều bên nhiều ngôn ngữ".**

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| N+1 nếu không DataLoader | 10²–10³ query/request | P | danh sách lồng |
| Round-trip giảm vs REST ghép | 4 → 1 | I | tuỳ màn hình |
| Persisted queries | + cache CDN được | V | |
| tRPC biên | TypeScript-only | V | |

---

## 4. Suy luận kiến trúc

- **S1:** GraphQL là **tối ưu cho người tiêu thụ dữ liệu** — chuyển chi phí sang server (query planning, cache); hợp khi số client × nhu cầu lệch nhau lớn.
- **S2:** Tham số trụ: query complexity p99, resolver time, DB query/request (≤ ~5 lành mạnh), cache hit (persisted).
- **S3:** Federation đổi tự chủ team lấy một lớp gateway; tRPC đổi tính mở lấy type-safety miễn codegen — cả hai đều "đúng theo hình dạng tổ chức".
- **S4:** BFF (một GraphQL/tRPC gateway cho từng lớp client) đang thay "API chung cho mọi màn hình" — pattern ổn định 10 năm, tên đổi (backend-for-frontend, experience API).
- **S5:** AI agent tiêu thụ API: agent đọc OpenAPI/tool schema (→12.5) nhiều hơn GraphQL — nếu mục tiêu là machine client, đầu tư schema khai báo (4.3/4.4) trước query language.
- **S6:** Khi GraphQL chậm: 90% là N+1 hoặc query phức tạp lọt qua cost limit — trace resolver trước khi đổi hạ tầng.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Server CPU vọt vì 1 client | Query sâu/lồng không giới hạn | cost limit; log complexity | §2.2 |
| p99 tệ dù DB nhanh | N+1 resolver | trace: query/request | §2.3 |
| CDN không cache được | POST + query text | persisted queries | §2.2 |
| Schema public bị dò | Introspection bật | tắt prod | §2.2 |
| Team sợ đổi field | Không có deprecation flow | field deprecate + metric | §2.4 |

---

## 6. Cách đo

```bash
# Complexity & depth từng query (từ server log/metric)
#  Apollo/GraphQL Helix expose: complexity, depth, resolver ms

# Đếm query DB mỗi GraphQL request (middleware dev)
#   > 5 → DataLoader cho resolver đó

# Smoke attack chính mình (staging):
#   query lồng sâu 20 tầng — server từ chối với lỗi rõ ràng chứ không phải 502?
```

Nguyên tắc: **complexity là "giá" của query —Metric hoá như request size**, không để "client muốn gì nhận nấy" vô chính sách.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay GraphQL BFF:** REST endpoint "theo màn hình" (vẫn BFF về tư duy, đơn giản về tooling); gRPC + FE gateway. **Thay Federation:** schema stitching thủ công hoặc một service GraphQL "di sản" — ít service thì ít lớp. **Thay tRPC:** OpenAPI + generator (mở cho client khác ngôn ngữ sau này).

Năm thấu kính:
- **Kinh tế:** GraphQL có chi phí vận hành thật (cost limit, persisted, N+1 discipline) — đáng khi **số client × độ lệch nhu cầu** lớn; internal-only với 1 web client thường không đáng.
- **Vận hành:** Gateway federation cần SRE như một service thật (không phải "thư viện"); đặt tên chủ sở hữu từ ngày một.
- **An ninh:** Authorization **per-field/per-type** là trách nhiệm server — introspection off + cost limit + persisted là bộ ba hygiene public.
- **Lịch sử:** Facebook nội bộ 2012, public 2015, hypes 2017–2019, tỉnh lại 2020s — chỗ đứng thật: BFF + client đa dạng; không phải "REST kế nhiệm".
- **Người dùng:** Người dùng thấy màn hình load 1 lần đủ dữ liệu, không spinner chồng spinner — đó là điều GraphQL mua, nếu server được bảo vệ đúng.

---

## 8. Đọc tiếp & bài tập

- N+1 & DataLoader sâu hơn: **5.2** · REST/OpenAPI: **4.3** · Cache/CDN: **5.4** · Agent dùng API: **12.5**
- **Bài tập 1:** Bật đếm query DB/request ở dev; mở màn hình danh sách phức tạp nhất. > 10? DataLoader hôm nay.
- **Bài tập 2:** Gửi query lồng sâu 15 tầng vào staging (script 5 dòng). Kết quả mong muốn: 400 lỗi cost limit trong < 10 ms; kết quả thật thường đáng lo.
- **Bài tập 3:** Liệt kê client của API chính (web/app/TV/đối tác/agent). Độ lệch nhu cầu dữ liệu của họ là case cho GraphQL — hay nhu cầu khá đồngiform và REST đủ?
