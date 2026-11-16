# 3.10 — Giải phẫu Tầng Phục vụ (9 Trạm)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền runtime · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** p5-ch27-anatomy.md

---

## 0. Nhập môn

**Đọc trước:** 3.1 · 3.4.

**Sợi chỉ đỏ:** *Runtime chỉ là một trạm — request của khách đi qua bao nhiêu trạm trước khi quay lại?* — trả lời: chín trạm — client, LB, gateway, app, pool, queue, cache, DB, trả về — mỗi trạm là một hàng đợi đo được bằng luật Little; timeout budget chia chín phần với quy tắc con nhỏ hơn cha; và nút thắt biết di chuyển khi bạn chữa chỗ cũ. Câu hỏi để lại cho chương sau: *Mỗi runtime dựng HTTP stack riêng — serializer và keep-alive cháy ở đâu?*

**Thuật ngữ sẽ gặp:** *trạm* — một tầng xử lý trên đường request, dù không ai vẽ ra; *Little mỗi trạm* — hàng đợi = throughput × thời gian trạm: công thức tính pool; *timeout budget* — tổng thời gian cho phép chia xuống từng trạm, con nhỏ hơn cha; *pool* — số connection/worker giữ sẵn: tính được, không phỏng; *retry storm* — retry chồng lên retry đúng lúc hạ tầng chậm; *nút thắt di chuyển* — chữa xong chỗ này, tắc chuyển sang chỗ kia.

**Ví dụ mở đầu:** p99 của DM xấu đi sau một đợt "tối ưu". Đo theo chín trạm: app nhanh hơn 30 ms — nhưng pool DB vẫn 10 connection cho 40 request đang bay, hàng đợi dài thêm 200 ms. Không ai nhìn tổng thì đợt "tối ưu" thành đợt dịch tắc: nhanh một trạm, chậm cả tuyến.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Số worker/pool mỗi trạm (theo Little) | `workers = throughput × latency` — tôi đã tính, hay "đặt 50 cho chắc"? |
| 2 | Timeout budget toàn trình + phân bổ xuống 9 trạm | Tổng timeout con có vượt budget cha? Ai owns con số này? |
| 3 | Mỗi trạm có hàng đợi riêng — sâu bao nhiêu, từ chối khi nào | Queue vô hạn ở trạm nào đang âm thầm tồn tại? |
| 4 | Retry/phần dư đặt ở trạm nào | Retry đúng trạm, đúng tầng — không phải "mọi nơi cho chắc"? |

---

## 2. Cơ chế

### 2.1 Chín trạm của một request (mỗi request đều đi qua, dù không ai vẽ)

```
[1 LB/DNS] → [2 Ingress/TLS] → [3 App worker] → [4 Serializer/Parse]
   → [5 Client nội (HTTP/gRPC pool)] → [6 DB driver pool] → [7 DB engine]
   → [8 Response path] → [9 Log/metric/trace]
```

Mỗi trạm là một **hàng đợi + một worker pool + một timeout**. Nghẽn trạm nào, latency cộng dồn từ đó trở đi. Việc của kiến trúc sư: vẽ đúng 9 trạm **của hệ mình**, gắn số cho từng trạm, và làm cho số đo được.

### 2.2 Little's law là thước đo của từng trạm

`L = λ × W`: đang-xử-lý = throughput × độ trễ. Ví dụ: 2.000 req/s × 0,3 s (app) = 600 request đang nằm trong app → app pool cần ~600 unit (hoặc 600 đang chờ — hai tình huống khác nhau — đo mới biết). Tính cho từng trạm: DB pool, HTTP client pool, thread/event-loop. **Sai số thường gặp:** tính theo throughput đỉnh lý thuyết, không phải đỉnh thất bại (spike + retry nhân — →8.5).

### 2.3 Timeout budget: chia 9 phần, tổng phải ≤ phần cha

Budget tổng (ví dụ 500 ms p99) phân bổ: DNS 20 · TLS/handshake 50 · LB 10 · app queue 50 · xử lý 200 (trong đó DB 120, downstream 60) · serialize 20 · log async 0 (không block đường trả lời). Ba quy tắc:
1. **Timeout con < timeout cha** ở mọi nhánh — vi phạm = công việc mồ côi cháy tài nguyên (leak giữ pool);
2. Deadline **truyền xuống** (gRPC deadline, ctx — →3.4): DB nhận biết "còn 30 ms thôi" để bỏ cuộc đúng lúc;
3. Mỗi trạm đo **thời gian ở trạm mình** (span) — tổng hóa ra được p99 giải phẫu (→11.1 tracing).

### 2.4 Hàng đợi mỗi trạm và nút thắt cổ chai di chuyển

Vì mỗi trạm là queue: khi tải tăng, **trạm bão hoà đầu tiên** nuốt phần dư latency của cả hệ (queueing — →3.1 §2.2). Bão hoà di chuyển theo từng mùa: hôm qua là DB pool, hôm nay là serializer (payload mới to), mai là log sync. Do đó: mỗi trạm cần (a) giới hạn queue riêng, (b) metric riêng, (c) cách từ chối riêng (503 nhanh > timeout chậm — →8.5 load shedding).

### 2.5 Pool sizing — công thức thực chiến

```
pool ≈ target_throughput × worst_latency    (Little)
       × (1 + retry_factor)                 (spike)
       × safety (1,2–1,5)
```

DB pool: 500 req/s × 0,05 s × 1,3 × 1,2 ≈ 39 connection. **Cẩn thận phía DB:** connection có giá thật mỗi cái (memory, mỗi process/postgres worker) — pool to "cho chắc" = tự sát DB (→5.2 connection storm). Giới hạn trên pool theo sức chứa DB, không theo sức chứa app.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Số trạm chuẩn | 9 | V | mô hình của sách này |
| Queueing phi tuyến từ | ~70–80% util | I | →3.1 |
| Retry factor thực tế | 1,2–2× lúc sự cố | I | →8.5 |
| DB conn cost | ~MB mỗi conn (Postgres) | I | →5.2 |
| Timeout budget vi phạm hậu quả | công việc mồ côi | P | giữ pool/leak |

---

## 4. Suy luận kiến trúc

- **S1:** Kiến trúc phục vụ = **tổng 9 hàng đợi** — không một tối ưu trạm đơn lẻ vượt nổi trạm chậm nhất (Amdahl của hệ phân tán).
- **S2:** Tham số trụ: p99 **per trạm** (span), pool utilization từng cái, queue depth, timeout vi phạm/s.
- **S3:** Little đổi "cảm giác đủ" thành số; budget đổi "timeout mặc định" thành hợp đồng; load shedding đổi "chậm tất cả" thành "từ chối ít cái".
- **S4:** Service mesh/serverless không bỏ trạm — chỉ đổi chủ sở hữu (LB ingress → platform; pool → shared) — mô hình 9 trạm vẫn đúng, đổi tên người giữ.
- **S5:** Tracing chuẩn hoá (OpenTelemetry — →11.1) làm "giải phẫu 9 trạm" thành dữ liệu thay vì sơ đồ — đầu tư span ở mọi trạm là đầu tư chẩn đoán sau này.
- **S6:** Khi p99 xấu: xem span theo trạm trước khi đoán nguyên nhân — 90% trường hợp một trạm nuốt phần dư, và trạm đó đổi tên qua các lần sự cố.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Timeout client nhưng server "xong việc" | Timeout không truyền xuống; mồ côi | trace span; deadline header | §2.3 |
| Pool cạn định kỳ | Little sai (thiếu retry factor) | pool wait metric | §2.5 |
| p99 tăng nhưng mọi CPU rảnh | Hàng đợi trạm nào đó dài | queue depth per trạm | §2.4 |
| Spike tải → sập hẳn (không chỉ chậm) | Không load shedding; queue vô hạn | audit giới hạn queue | §2.4 |
| DB chết lúc app scale out | Pool mỗi instance × instance nhiều | tổng conn vs max_connections | §2.5 |

---

## 6. Cách đo

```bash
# 1. Span mỗi trạm (OpenTelemetry) — xem phân bổ p99
#    service graph + span durations theo trạm

# 2. Pool metric mọi loại (HTTP client, DB driver):
#    active / idle / waiting — waiting > 0 kéo dài là trần pool sai

# 3. Timeout audit — liệt kê timeout từng tầng (config diff)
#    grep -r "timeout" configs/ | sắp theo tầng để kiểm tra §2.3

# 4. Little kiểm chứng: throughput × latency ≈ đang xử lý?
#    so với pool thực tế — chênh = hàng đợi vô danh
```

Nguyên tắc: **span là đèn soi từng trạm** — hệ không có span per trạm là hệ mù giữa các comma của monitoring.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tinh chỉnh pool:** tách trạm bão hoà thành service riêng (đổi topology lấy focused tuning); hoặc cache phía trước trạm đắt (→5.4). **Thay budget thủ công:** adaptive timeout theo p99 quan sát (một số client hỗ trợ) — vẫn phải có trần cứng. **Thay hàng đợi in-process:** queue phân tán (→5.7) khi cần sống qua restart — đổi latency lấy durability.

Năm thấu kính:
- **Kinh tế:** Pool to quá trả tiền máy + rủi ro DB; pool nhỏ trả tiền latency — Little là công cụ đặt đúng điểm giữa, mỗi quý một lần.
- **Vận hành:** Runbook sự cố nên có bảng 9 trạm × metric × ngưỡng — on-call nhìn bảng, không nhìn 40 dashboard.
- **An ninh:** Mỗi trạm là điểm ghép (queue vô hạn = DoS dễ; parse không giới hạn = bomb payload) — giới hạn là biên an ninh lẫn vận hành.
- **Lịch sử:** Mô hình "tuần tự qua các trạm" cổ như công ty điện thoại; cái mới là **đo per-span realtime** — 20 năm trước diagram, hôm nay data.
- **Người dùng:** Người dùng chỉ thấy tổng — 500 ms. Chương này là kỹ năng chia 500 đó thành 9 con số có thể sửa.

---

## 8. Đọc tiếp & bài tập

- Tracing/observability: **11.1** · Retry/bão: **8.5** · DB pool: **5.2** · Queue phân tán: **5.7** · Sizing cụm: **11.3**
- **Bài tập 1:** Vẽ 9 trạm của hệ bạn (đúng tên service thật). Đo p99 từng trạm một tuần. Chuẩn bị ngạc nhiên: trạm tệ nhất thường không phải trạm nghi ngờ đầu tiên.
- **Bài tập 2:** Tính Little cho DB pool chính: throughput × latency × retry × safety. So với cấu hình hiện tại. Sai số > 2× = một quyết định chưa ai đưa ra.
- **Bài tập 3:** Lập bảng timeout mọi tầng (grep config). Kiểm tra quy tắc con < cha. Mỗi vi phạm là một "công việc mồ côi" đang chờ giờ cao điểm.
