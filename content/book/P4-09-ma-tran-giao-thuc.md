# 4.9 — Ma trận Chọn Giao thức, 10 Bẫy & Gateway/Mesh

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** p5-ch32-matrix.md

---

## 0. Nhập môn

**Đọc trước:** Lướt 4.1–4.8 — mỗi cặp giao tiếp một hàng của ma trận.

**Sợi chỉ đỏ:** *Nhìn lại toàn cảnh: cặp nào nói chuyện bằng gì — có ma trận quyết định không?* — trả lời: có — ma trận chọn theo cặp giao tiếp (trình duyệt-gateway, service-service, sự kiện nội bộ, batch) chứ không theo "giao thức tốt nhất", kèm 10 bẫy xuyên chương, khi nào gateway và mesh đáng, và chính sách mặc định của org để 80% team khỏi phải quyết. Câu hỏi để lại cho chương sau: *API đông thì dữ liệu phình — B-tree và LSM, ruột của mọi DB, khác nhau thế nào?*

**Thuật ngữ sẽ gặp:** *ma trận cặp giao tiếp* — hỏi "ai nói với ai, nhịp nào, ai giữ client" trước khi hỏi "giao thức nào"; *gateway* — chốt chặn TLS, authn, rate limit: đúng tầng, đừng nhét nghiệp vụ; *service mesh* — mTLS + retry + observability cho mọi service: đáng tiền infra hay không; *chính sách mặc định* — org chọn sẵn REST/OpenAPI ngoài, gRPC trong: 80% khỏi họp; *mTLS nội bộ* — hai chiều mọi service: không tin mạng nội bộ là vô trùng; *10 bẫy* — tổng kết 4.1–4.8: từ 0-RTT replay tới offset pagination.

**Ví dụ mở đầu:** Cuộc họp chọn giao thức cho service mới của DM lại chuẩn bị kéo hai giờ — mỗi người đề xuất cái mình quen. Đặt ma trận ra: cặp nào nói chuyện? nhịp nào? ai giữ client? — quyết định rơi trong 15 phút. Chương này là ma trận đó, điền sẵn kèm chính sách mặc định cho 80% trường hợp còn lại.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Họ giao thức cho từng cặp (client-public, service-service, event, realtime) | Ma trận 4×N của tôi đã điền đủ và có chủ không? |
| 2 | Gateway (ngõ vào chung) đến đâu thì dừng | Gateway làm auth/rate-limit/routing — và **không** làm nghiệp vụ? |
| 3 | Service mesh có đáng cho cụm tôi | Tôi cần mTLS + traffic policy đồng loạt không — hay 3 sidecar rất đắt? |
| 4 | Chính sách "một giao thức mặc định" của org | Mặc định gì để 80% case không phải quyết định? |

---

## 2. Cơ chế

### 2.1 Ma trận chọn — theo cặp giao tiếp, không theo "giao thức tốt nhất"

| Cặp | Mặc định nên | Khi nâng cấp | Tránh |
|---|---|---|---|
| Public web/mobile → API | REST + OpenAPI (→4.3) + H2/H3 (→4.2) | GraphQL khi client đa dạng lệch nhu cầu (→4.5) | gRPC public; SOAP mới |
| Service ↔ service (đồng bộ) | REST nội bộ hoặc gRPC/Connect (→4.4) | gRPC khi streaming + throughput | XML; tự chế binary |
| Hệ ↔ hệ (bất đồng bộ) | Event + CloudEvents + schema registry (→4.7) | Kafka khi replay/log (→5.7) | "Webhook cho internal" |
| Server → client realtime | SSE (→4.6) | WS hai chiều; WebTransport datagram | Polling 100ms |
| Webhook → đối tác | POST + HMAC + retry (→4.8) | — | Fire-and-forget |

Đọc bảng theo **cặp**, không theo công nghệ: cùng một org, bốn hàng bốn lựa chọn khác nhau là bình thường và đúng.

### 2.2 10 bẫy chọn/vận hành giao thức (tổng kết xuyên chương 4)

1. **Chọn theo trend** thay vì theo cặp use case (ma trận trên);
2. **Nhiều phiên bản HTTP không đồng nhất** — client H1 cũ đánh server H2 (keep-alive lệch — →3.11);
3. **Timeout không truyền xuyên** (deadline — →3.10/4.4) — công việc mồ côi;
4. **Retry không idempotency** (→4.8/8.5) — trừ tiền 2 lần;
5. **Validate thiếu ở biên công khai** — 500 sâu thay vì 400 sớm (→4.3);
6. **Breaking change không metric usage** — không dám gỡ version cũ (→4.8);
7. **Event không schema/registry** — dữ liệu sai lan âm thầm (→4.7);
8. **Stream không xử lý hop** (buffering/idle — →4.6) — "realtime" thành cụm;
9. **Rate limit sai chiều** (IP thay tenant) — một NAT dập cả cụm (→4.8/9.3);
10. **Gateway làm nghiệp vụ** — logic phình vào tầng trung gian không ai test được.

### 2.3 Gateway: chốt chặn đúng, không phải tầng nghiệp vụ

Gateway/ingress (nginx/Envoy/Kong/APISIX — →9.4) nên: terminate TLS, authn (verify token), rate limit thô, routing/versioning, request size limit, observability. **Không nên:** nghiệp vụ (chuẩn hoá dữ liệu, aggregation, retry thông minh) — vì gateway khó test, khó version, là SPOF của mọi thứ. Ngưỡng thực dụng: gateway giữ dưới ~5ms p99 và dưới ~1k dòng config có ý nghĩa; hơn thế là dịch vụ thật — viết như service.

### 2.4 Mesh: khi nào đáng

Mesh (Istio/Linkerd/Cilium service mesh) cấp: mTLS tự động, L7 telemetry, traffic split/canary, retry/outlier detection đồng loạt. Chi phí: sidecar (hoặc ambient — Cilium eBPF/sidecar-less đang giảm giá này), độ phức tạp vận hành, giải troubleshooting mới. **Ngưỡng:** ≥ ~15–20 service + cần mTLS/policy thật + team platform sở hữu được — dùng. Dưới đó: library (SDK chung) + gateway + network policy đạt 80% lợi ích với 20% chi phí (I).

### 2.5 Chính sách mặc định của org (để 80% khỏi quyết định)

Một trang: "API mới = REST+OpenAPI; nội bộ cùng khu = gRPC nếu streaming, không thì REST; sự kiện = CloudEvents+registry; realtime = SSE; auth = OAuth2/OIDC; lỗi = 9457; pagination = cursor". Việc còn lại: viết ngoại lệ có giải thích. Chính sách này là artifact chống "mỗi service một phong cách".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Gateway p99 mục tiêu | < 5 ms | I | hơn = dịch vụ thật |
| Mesh sidecar overhead | ~5–15% latency/HTTP (giảm với ambient) | I | |
| Ngưỡng mesh đáng | ~15–20+ service | P | |
| Số giao thức đồng thời quản lý được | 3–4/org | P | hơn = cần consolidation |

---

## 4. Suy luận kiến trúc

- **S1:** Giao thức là **chi phí cố định của giao tiếp** (công cụ, debug, docs, team) — ít giao thức được chọn đúng > nhiều giao thức được chọn đẹp.
- **S2:** Tham số trụ: phân bổ gọi theo giao thức, gateway latency p99, mesh resource overhead, số ngoại lệ chính sách.
- **S3:** Gateway đổi an toàn biên lấy tốc độ; mesh đổi ops phức tạp lấy policy đồng loạt; chính sách mặc định đổi tự do cá nhân lấy tốc độ tổ chức.
- **S4:** Ambient mesh/sidecar-less (eBPF — →2.8) đang hạ chi phí mesh xuống ngưỡng mới — quyết định "mesh chưa đáng" 2023 có thể đáng 2027; review định kỳ.
- **S5:** AI agent như client (→12.5) tái sử dụng đúng stack này (OpenAPI, 9457, rate limit) — đầu tư chương 4 không chỉ cho người.
- **S6:** Khi "giao tiếp rối": vẽ lại ma trận cặp × giao thức thật đang chạy (không phải trên diagram) — mỗi ô lệch mặc định là một cuộc trò chuyện chưa diễn ra.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| 10 cách gọi API trong 1 org | Không có chính sách mặc định | bảng §2.5 | §2.5 |
| Gateway là SPOF nghẽn | Logic phình vào gateway | profile gateway; dời nghiệp vụ | §2.3 |
| Mesh "có nhưng không biết làm gì" | Adopt theo trend | audit feature dùng thật | §2.4 |
| Debug sản xuất chậm vì binary protocol | Thiếu công cụ (grpcurl/qlog) | tooling checklist | §2.1 |
| Chính sách ai cũng vi phạm | Ngoại lệ không tổng kết | review ngoại lệ/quý | §2.5 |

---

## 6. Cách đo

```bash
# Phân bổ gọi theo giao thức (access log + mesh telemetry):
#   % REST / gRPC / event / SSE — và trend 6 tháng

# Gateway tự đo (nó là service!):
#   p99 của chính gateway, riêng biệt với upstream

# Mesh overhead: cùng endpoint có/không sidecar (staging A/B)
#   chênh > 15%? → ambient mode hoặc bỏ mesh cho service đó

# Chính sách: đếm service vi phạm default — con số lên đều = chính sách chết
```

Nguyên tắc: **gateway và mesh là service — đo chúng như service** (latency, lỗi, tài nguyên), đừng coi là "hạ tầng vô hình".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay mesh:** library chuẩn + gateway + mTLS thủ công (cert-manager) — hợp cụm nhỏ/vừa. **Thay gateway tự host:** managed (AWS API Gateway/Cloudflare) — đổi chi phí biên lấy ops nhẹ, vendor lock cần tính (→11.3). **Thay chính sách:** "architecture decision records" cho từng ngoại lệ — chống biến ngoại lệ thành mặc định ngầm.

Năm thấu kính:
- **Kinh tế:** Mỗi giao thức thêm một chi phí cố định (tooling + training) — bảng 2.5 là cách biến chi phí đó từ "ẩn" thành "lựa chọn".
- **Vận hành:** Chính sách giao thức nên có **chủ sở hữu + review quý** — không có chủ thì 12 tháng sau nó là cổ vật.
- **An ninh:** Gateway là nơi tập trung auth/rate-limit/size — cũng là mục tiêu số một; version gateway phải được theo dõi CVE như OS (→10.4).
- **Lịch sử:** ESB/SOA (2000s) từng là "gateway làm mọi thứ" và chết vì đúng bẫy §2.3; microservice-era gateway là bài học đã học — giữ cho nó mỏng là giữ cho nó sống.
- **Người dùng:** Người dùng không biết REST hay gRPC — họ biết "mọi app của công ty gọi nhanh, ổn định, lỗi rõ". Ma trận này là nền của cảm giác đó.

---

## 8. Đọc tiếp & bài tập

- Toàn bộ chương 4 là nguồn của ma trận này · Ingress/K8s: **9.4** · Event: **5.7** · Retry/chaos: **8.5** · Agent client: **12.5**
- **Bài tập 1:** Vẽ ma trận cặp × giao thức **thật** của org bạn (từ access log, không từ diagram). So với bảng 2.1 — mỗi khác biệt chưa giải thích là một câu hỏi kiến trúc.
- **Bài tập 2:** Đo p99 của gateway riêng (không gồm upstream). > 5 ms? Profile nó — thường tìm thấy nghiệp vụ lậu vào.
- **Bài tập 3:** Viết trang chính sách mặc định (§2.5) — nửa giờ — rồi đếm trong tháng tới có bao nhiêu quyết định "giao thức nào đây" nó thay mặt bạn trả lời.
