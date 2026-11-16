# 3.11 — HTTP/RPC Stack của 6 Ngôn ngữ (ngang bằng)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** python-ops-chapter.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 3.10 · 2.6 (netstack).

**Sợi chỉ đỏ:** *Mỗi runtime dựng HTTP stack riêng — serializer và keep-alive cháy ở đâu?* — trả lời: cùng chuẩn HTTP nhưng mỗi runtime dựng stack khác nhau — serialization, keep-alive, pool là ba chỗ cháy nhiều nhất; chương này cho bảng chọn theo ngôn ngữ và phép benchmark không tự lừa mình. Câu hỏi để lại cho chương sau: *Service chạy ngon trong máy — giờ mở cửa cho thế giới: transport an toàn và nhanh là gì?*

**Thuật ngữ sẽ gặp:** *serializer* — biến đối tượng thành byte và ngược lại: JSON, protobuf, msgpack; *keep-alive* — tái dùng connection thay vì bắt tay TLS lại mỗi request; *pool phía client* — số connection giữ sẵn: ranh giới giữa 502 và mượt; *streaming* — trả từng phần thay vì chờ đủ cả; *header parsing* — chi phí ẩn của request nhiều header; *benchmark methodology* — warm-up, p99, payload thật: thiếu một thứ thì kết quả là truyện kể.

**Ví dụ mở đầu:** Đội Python và đội Go cãi "API của tao nhanh hơn": benchmark hello-world mỗi bên thắng theo cách riêng. Lấy payload thật của DM — 40 trường, 3 KB — khoảng cách thu hẹp, và chỗ quyết định không phải ngôn ngữ mà là serializer và keep-alive. Chương này dạy đo tới khi hai bên cãi nhau bằng cùng một loại số.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | HTTP stack cho service mới từng ngôn ngữ | Framework nào theo bảng — và tôi có thêm gì ngoài "quen tay"? |
| 2 | JSON path (serializer) + schema-first hay code-first | Serialization chiếm bao nhiêu % CPU request của tôi? |
| 3 | HTTP/1.1 keep-alive pool hay HTTP/2 multiplexing nội bộ | Traffic nội cụm qua gì — và mọi client đã cấu hình pool đúng chưa? |
| 4 | gRPC/protobuf cho đường nội bộ quan trọng | Đổi gì lấy gì: schema chặt, streaming, ~2–5× serialization? |

---

## 2. Cơ chế

### 2.1 Bảng chọn — stack khuyến nghị theo ngôn ngữ (2026)

| Ngôn ngữ | HTTP server mặc định nên chọn | Client HTTP | Ghi chú vận hành |
|---|---|---|---|
| Python | Uvicorn/ASGI + FastAPI (orjson) | httpx (async) | 1 worker/process; GIL — →3.2 |
| Node/TS | Fastify (hoặc Express) | undici (fetch chuẩn Node) | loop lag là metric sống — →3.3 |
| Go | net/http chuẩn (đủ nhanh) | net/http + transport pool | fasthttp chỉ khi profile chỉ rõ |
| Rust | axum (tokio + hyper) | reqwest | tower middleware hệ sinh thái |
| Java | Spring Boot 3 + virtual threads hoặc Helidon Nima | java.net.http / Netty | JSON: Jackson vs JSON-B — đo |
| C++ | Drogon / proxygen | — | chỉ cho engine cần |

Quy tắc xuyên suốt: **chuẩn > nhanh nhất** — net/http, Fastify, axum đều "đủ nhanh"; khác biệt thực tế đến từ **cấu hình pool + serializer + framework overhead của chính bạn** (middleware, logging sync).

### 2.2 Chi phí serialization — con số ít ai đo

JSON parse+serialize chiếm 10–40% CPU request ở traffic cao (I, tùy payload). Bậc hiệu năng (payload vừa):
`protobuf/flatbuffers ≈ 2–5× > orjson/msgspec ~5–10× > json stdlib Python ~1×` (I). Ba quyết định:
1. Đổi serializer cùng họ (json→orjson): 10 dòng, lợi tức ngay;
2. Đổi format (JSON→protobuf/msgpack): cần 2 đầu — hợp đường nội bộ;
3. Bớt payload (bỏ field không dùng, phân trang): luôn thắng, không cần đổi gì.

### 2.3 Pool & keep-alive — chỗ 10.000 service bỏ sót

Client HTTP không tái sử dụng connection = handshake TLS mỗi request (→1.7 RTT + CPU — →4.1). Kiểm tra: cấu hình pool (max conn per host), keep-alive idle timeout **client < server idle timeout** (tránh 502 sau deploy — →4.2), và HTTP/2 cho nội bộ (multiplex 1 TCP — bớt conntrack — →2.6).

### 2.4 gRPC nội bộ: khi nào đáng

Đổi lấy: schema chặt (compile-time), streaming 4 kiểu, deadline truyền tự động (→3.10), interceptor quan sát chuẩn. Trả bằng: khó debug bằng curl (cần grpcurl), vài vấn đề tương thích (envoy/LB HTTP/2 bắt buộc), team phải học. **Ngưỡng thực dụng:** nội cụm > 1k RPS giữa 2 service quan trọng, hoặc cần streaming — đáng; CRUD thấp tần — REST + schema (OpenAPI) đủ và dễ hơn cho người ngoài.

### 2.5 Benchmark đúng cách (đừng tin TechEmpower blindly)

- Chuẩn hoá môi trường (cùng máy, cùng payload, keep-alive BẬT);
- Đo p99 + phân phối, không chỉ RPS trung bình;
- Payload giống **thật** của bạn (không "hello world 1 field");
- Kể cả serializer + logging như production (đó là chỗ framework "nhanh" chết).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| JSON vs protobuf CPU | ~2–5× | I | payload vừa |
| json → orjson | ~5–10× | I | Python |
| Chiếm CPU serialization | 10–40% traffic cao | I | đo để biết |
| HTTP/2 gain nội bộ | ít conn, multiplex | V | →2.6/4.2 |

---

## 4. Suy luận kiến trúc

- **S1:** HTTP stack là **bề mặt tiếp xúc lớn nhất** của service — chọn chuẩn sâu (middleware, quan sát, pool) ăn nhiều hơn chọn nhanh nhất.
- **S2:** Tham số trụ: CPU% serializer, pool wait, p99 per endpoint (không per service chung chung).
- **S3:** protobuf đổi debug-ability lấy hiệu năng + schema; HTTP/2 đổi đơn giản TCP quản lý lấy multiplex; fasthttp đổi hệ sinh thái (middleware chuẩn) lấy throughput thô.
- **S4:**REST+OpenAPI là lingua franca của API công khai; gRPC của nội bộ — ranh giới này ổn định gần 10 năm và chưa có dấu hiệu đổi.
- **S5:** AI serving kéo interface mới (SSE streaming — →4.6, gRPC-gateway cho token stream — →12.2) — HTTP stack phải chọn được streaming, không chỉ request/response.
- **S6:** Khi endpoint chậm: profile trước (serializer? pool? downstream?) — đổi framework là phương án cuối, và 90% không cần.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| CPU cao bất thường ở traffic lớn | Serialization (JSON stdlib) | profile; orjson/proto | §2.2 |
| 502 lẻ tẻ sau deploy | Keep-alive timeout lệch (client > server) | audit timeout 2 đầu | §2.3 |
| Conntrack đầy (→2.6) | Mỗi request 1 connection mới | pool config; HTTP/2 | §2.3 |
| gRPC "không chạy qua LB" | LB không hỗ trợ HTTP/2 upstream | cấu hình/đổi ingress | §2.4 |
| Benchmark không khớp production | Payload/keep-alive/logging lệch | chuẩn hoá theo §2.5 | §2.5 |

---

## 6. Cách đo

```bash
# Chi phí serialization riêng — micro nhưng nói thật
python -m timeit -s "import json,orjson,d" "orjson.dumps(d)"
# (tương tự từng ngôn ngữ; đo cả parse lẫn dump)

# Pool & keep-alive của client (ví dụ Node undici / Go transport):
#   expose metric: active/pending/queued connection

# Endpoint-level p99 — trung thành theo route, không tổng:
#   histogram theo route từ tracing/metrics (→11.1)

# Kiểm tra HTTP/2 thật sự:
curl -sI --http2 https://internal-svc/ -o /dev/null -w '%{http_version}\n'
```

Nguyên tắc: **đo endpoint, không đo service** — trung bình cả service che mất 1 endpoint tệ đang đốt p99.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay đổi serializer:** bớt field + nén (gzip/zstd ở gateway — đổi CPU cho bytes) trước khi đổi format. **Thay gRPC:** REST + OpenAPI + generator (client typed) đạt 80% lợi ích schema với chi phí quen thuộc hơn. **Thay framework:** gần như chỉ khi framework gây overhead đo được (middleware ấu trĩ, logging sync) — sửa cấu hình trước.

Năm thấu kính:
- **Kinh tế:** Chuẩn hoá 1 stack/ngôn ngữ toàn org giảm chi phí onboarding/reuse — lợi tức lớn hơn 15% throughput của stack lạ.
- **Vận hành:** Mỗi stack có cách cấu hình pool/keep-alive riêng — checklist deploy phải liệt kê theo từng loại.
- **An ninh:** Deserialization là vecto kinh điển (parser khác biệt, entity mở rộng) — schema chặt + giới hạn kích thước payload là lớp rẻ nhất (→10.4).
- **Lịch sử:** Từ servlet nặng (2000s) → Express nhẹ (2010s) → "framework đủ tốt, hạ tầng quyết định" (2020s) — cạnh tranh dịch sang vận hành; chọn ít quyết định hơn xưa.
- **Người dùng:** Người dùng thấy "load 200 ms không phải 2 s" — chương này là chi tiết làm nên con số đó, chọn đúng thì vô hình, chọn sai thì rất hữu hình.

---

## 8. Đọc tiếp & bài tập

- Giao thức sâu: **4.1–4.3** · Trạm & pool: **3.10** · Streaming/SSE: **4.6, 12.2** · Quan sát endpoint: **11.1**
- **Bài tập 1:** Profile 1 endpoint nóng: % thời gian serializer? Nếu > 20% — orjson/protobuf là ticket tuần này.
- **Bài tập 2:** Audit keep-alive timeout client vs server của 3 service chính. Vi phạm quy tắc "client < server"? Đó là nguồn 502 kế tiếp.
- **Bài tập 3:** Benchmark 2 stack ứng viên với payload thật của bạn (không hello-world). Ghi p99 + CPU — bằng chứng cho quyết định, thay vì "team quen".
