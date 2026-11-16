# 8.5 — Mẫu Chịu lỗi & Kiểm soát Tải Toàn trình

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** lý thuyết vận hành hoá · **Động từ liên quan:** Thiết kế · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 3.10 (retry storm) · 5.16 (headroom).

**Sợi chỉ đỏ:** *Phụ thuộc cứ chết lúc cao điểm — retry, breaker, shedding giữ hệ đứng bằng gì?* — trả lời: phụ thuộc chết lúc cao điểm là định mệnh chứ không phải bất ngờ — thứ giữ hệ đứng là nguyên bộ bốn tầng: retry có kỷ luật (backoff, jitter, chỉ retry cái đáng), circuit breaker ngừng gọi khi chắc sập, bulkhead chia khoang, load shedding chủ động chọn ai sống. Câu hỏi để lại cho chương sau: *Service đã đông — ranh giới nào mới đúng (bounded context, sở hữu dữ liệu)?*

**Thuật ngữ sẽ gặp:** *retry có kỷ luật* — backoff luỹ tiến cộng jitter (nối 3.10): retry bừa là tự tạo bão; *circuit breaker* — đếm lỗi tới ngưỡng thì ngừng gọi một khoảng: cho phụ thuộc hồi sức; *bulkhead* — chia pool và thread theo service: chìm một khoang, không chìm cả tàu; *load shedding* — quá tải thì chủ động từ chối việc rẻ trước: trả 503 thà treo 30 giây; *hedging* — bản thứ hai gửi đi nếu bản đầu trễ: đổi tải lấy đuôi p99; *graceful degradation* — tắt tính năng phụ, giữ lõi: menu vẫn xem được khi gợi ý đã chết.

**Ví dụ mở đầu:** Đêm cao điểm DM: service gợi ý chết — 40 service retry không kỷ luật biến một cái chết thành bão, toàn hệ gục theo. Có breaker: 40 service nhận "chết rồi" trong vài mili-giây và chạy graceful. Chương này xếp bốn tầng phòng thủ đúng thứ tự, vì thiếu một tầng là đủ sập.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chính sách retry: ai được retry, mấy lần, backoff thế nào | Retry của tôi có làm dependency thêm yếu không (bài toán nhân)? |
| 2 | Circuit breaker & bulkhead cho dependency nào | Dependency chết — tôi chết theo hay thu mình lại sống? |
| 3 | Load shedding: bỏ gì trước khi sập | Quá tải — đơn nào được phục vụ, đơn nào bị từ chối sớm? |
| 4 | Timeout từng tầng, tổng ngân sách | 3 giây user chờ — chia thế nào cho từng bước downstream? |

---

## 2. Cơ chế

### 2.1 Cái chết theo tầng cấp: vì sao cần nguyên bộ

Dependency chậm (không chết — **chậm**) → connection đầy → thread đầy → client khác timeout → client retry → gấp đôi tải → dependency chậm hơn → sập cả chuỗi (cascading failure, I-051). Bài toán không phải "một hệ yếu" mà là **sự yếu lan truyền bằng tài nguyên**. Bốn lớp phòng thủ (retry/breaker/bulkhead/shedding) chặn bốn con đường lan truyền khác nhau — thiếu một lớp là cửa mở.

### 2.2 Retry — chỉ retry cái đáng, và im lặng đúng cách

- **Đáng:** lỗi tạm thời (timeout, 503, connection reset); **không đáng:** 4xx nghiệp vụ, 500 lập lại (lỗi logic);
- **Backoff + jitter (full jitter):** `sleep(random(0, min(cap, base×2^n)))` — không jitter = mọi client cùng nhịp dồn đỉnh (thundering herd, I-052);
- **Retry budget:** giới hạn tỉ lệ retry so với traffic thường ≤ ~10% (I) — vượt thì buông (shed) thay vì cố; nếu hệ cần 30% retry để sống thì retry không phải vấn đề — sức chứa mới là;
- **Timeout mỗi lần thử** riêng — và **tổng ngân sách** phải nhỏ hơn timeout của người gọi phía trên (nếu không, cấp trên timeout trước rồi tự retry — nhân lên lần nữa).

### 2.3 Circuit breaker — ngừng gọi khi chắc chắn sập

Ba trạng thái: CLOSED (gọi bình thường, đếm lỗi) → vượt ngưỡng → OPEN (không gọi, trả fallback ngay) → sau khoảng nghỉ → HALF-OPEN (thử lại ít request) → đủ tốt thì CLOSED. Tham số sống còn: **ngưỡng đếm theo cửa sổ** (không phải tổng) + thời gian OPEN đủ dài cho dependency hồi phục (nhanh quá = dao động, chậm quá = phục vụ fallback lâu vô ích). Fallback phải **thật** (cache cũ, giá trị mặc định, hàng đợi làm sau) — fallback là "throw exception" thì breaker chỉ đổi tên lỗi.

### 2.4 Bulkhead — chia khoang, chìm một khoang

Pool riêng cho từng dependency (connection pool, thread pool, semaphore): dependency A chết chỉ đầy khoang A, B/C còn phục vụ. Ứng dụng phổ biến: pool nhỏ cho dịch vụ "không quan trọng" (đề xuất, analytics) để nó không thể trừ hao pool của "quan trọng" (thanh toán). Kubernetes tương tự ở tầng pod/node (→9.1 requests/limits) — cùng nguyên lý, khác tầng.

### 2.5 Load shedding — chọn ai sống khi quá tải

Quá tải thật thì **từ chối sớm là nhân đạo**: trả 503 + Retry-After ở cổng rẻ hơn giữ 10.000 request treo trong queue đầy bộ nhớ rồi sập toàn bộ. Ba lựa chọn khi thiết kế: (1) **ưu tiên theo lớp** (user trả tiền > bot > scrape; health check luôn qua); (2) **hàng đợi có giới hạn + độ sâu ngắn** (Little's law — →5.16: hàng đợi dài làm latency tệ mà không cứu throughput); (3) **degradation có kế hoạch** (tắt tính năng phụ — →6.1 client đã học cùng bài). Đo được: tỉ lệ shed theo lớp theo phút — đây là "van xả" được giám sát, không phải sự cố.

### 2.6 Bộ bàn ủi khác: hedging & graceful

- **Hedged request:** hết 90% timeout thì gửi bản sao sang node khác, lấy kết quả đầu — tăng p99 đáng kể **nhưng** nhân tải khi mọi node cùng chậm (dùng có budget);
- **Graceful shutdown:** nhận SIGTERM → ngừng nhận mới, làm nốt việc trong-flight (drain), trả kết quả — rồi thoát; không có nó, mọi deploy là một đợt lỗi nhỏ (→9.1/9.7 cùng chủ đề ở tầng platform);
- **Adaptive concurrency:** đo tải bằng tín hiệu (mức đầy pool) thay vì đếm lỗi — tự co giãn số request song song (chuẩn Google "aimd" style) — hay dùng ở client gọi service khó dự báo.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Retry budget | ≤ ~10% traffic | I | |
| Backoff | full jitter, cap 1–10 s | P | |
| Breaker OPEN | ≥ vài chục giây | P | theo thời gian hồi phục |
| Shed chuẩn | 503 + Retry-After, ở edge rẻ nhất | P | |
| Little's law | L = λ×W | V | queue discipline |

---

## 4. Suy luận kiến trúc

- **S1:** Chịu lỗi là **thuộc tính của chuỗi, không của node** — một dependency không được phép kéo sập chuỗi; thiết kế mỗi cột call-graph với bốn lớp §2.1 đã trả lời "nó chết thì tôi thế nào".
- **S2:** Tham số trụ: tỉ lệ retry (theo dependency), thời gian breaker OPEN mỗi ngày, số request bị shed theo lớp, p99 độ trễ dưới tải đỉnh.
- **S3:** Shedding đổi "phục vụ ít người tốt" lấy "sập toàn bộ" — quyết định ưu tiên lớp là quyết định **sản phẩm**, phải ký duyệt trước, không bịa lúc 2h sáng.
- **S4:** Bốn lớp này là điều kiện để autoscaling (→9.2) có thời gian hoạt động: scale mất 1–5 phút, chịu lỗi giữ chuỗi sống trong cửa sổ đó — autoscale không thay được chịu lỗi (hai cơ chế, hai khoảng thời gian).
- **S5:** AI traffic (agent/batch inference) tạo mẫu tải mới: không jitter, kỷ luật retry thấp, bùng nổ đồng bộ — kiểm soát tải giờ phải hoạt động cho "client không phải người" (→12.7) như một lớp user riêng.
- **S6:** Khi "chậm lan toàn hệ": tra theo thứ tự tài nguyên lan truyền (connection→thread→memory) và tìm dependency gốc trong trace (→11.1) — gần như luôn có một nút chậm khởi nguồn; sửa gốc thay vì tăng máy mọi nơi.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Retry storm nhân lên (I-050) | Không jitter/budget | audit chính sách retry từng client | §2.2 |
| Sập dây chuyền (I-051) | Thiếu breaker/bulkhead | trace tìm lan truyền tài nguyên | §2.1 |
| Đỉnh tải đồng bộ (I-052) | Mọi client cùng nhịp (cron/retry) | jitter hoá + lệch lịch | §2.2 |
| Tụt bộ nhớ ở queue | Queue không giới hạn | bound + shed | §2.5 |
| Deploy là lỗi nhỏ | Không graceful drain | preStop/drain (→9.1) | §2.6 |
| Breaker dao động ON/OFF | Cửa sổ OPEN quá ngắn | tham số + hồi phục thật | §2.3 |

---

## 6. Cách đo

```bash
# Kịch bản kiểm định (staging, có kiểm soát):
#   1. Tiêm 500ms + 10% lỗi vào dependency chính (proxy/toxiproxy-style)
#   2. Quan sát: p99 có vượt? retry rate có > 10%? breaker có mở?
#   3. Tiêm sập hẳn (drop 100%): dịch vụ chính còn trả fallback không?
# — không qua được 3 câu = bốn lớp còn thủng, sự cố chỉ chưa tới

# Metric phải có theo dependency: gọi/s, lỗi/s, retry/s, thời gian pool đầy
```

Nguyên tắc: **chịu lỗi được kiểm định bằng tiêm lỗi định kỳ** (chaos-lite) — như diễn tập cứu hoả: không drill thì sẽ có đám cháy thật để drill.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự cài bốn lớp:** service mesh sidecar/ambient có sẵn breaker/retry/timeout (→9.4) — cấu hình thay code; vẫn phải **quyết định tham số** (mesh mặc định thường an toàn kiểu "không retry" — tức vẫn phải tư duy); **thay shedding:** scale đủ to để không bao giờ quá tải — trả tiền cho đỉnh 1% thời gian (→5.16) — hợp lệ về kinh tế đôi khi.

Năm thấu kính:
- **Kinh tế:** Retry/shed là **bảo vệ doanh thu trong giây nguy hiểm** — chi phí cài đặt nhỏ hơn một lần sập 10 phút vào giờ cao điểm (định lượng: doanh thu/phút × thời gian MTTR trung bình).
- **Vận hành:** Mỗi layer có dashboard và drill riêng; runbook "dependency X chết" viết sẵn 5 bước đầu (ai tắt breaker? có bật fallback tĩnh không?).
- **An ninh:** Quá tải là vector tấn công (slowloris-style, retry buộc từ bot — I-051 từ phía xấu): rate limit (→11.3) + shedding là phòng thủ cùng họ với chịu lỗi; hai chương dùng chung hạ tầng.
- **Lịch sử:** Try-again-naive (lập trình mạng thập niên 90) → retry budget (AWS DynamoDB paper phổ biến hoá, 2012) → Hystrix (2012, deprecate 2018 vì thread-pool model) → Resilience4j/mesh (config hóa): chu kỳ quen thuộc — từ code tay sang cấu hình khai báo, từ tri thức cá nhân sang tài sản nền tảng.
- **Người dùng:** "Trang lỗi nhẹ nhàng sau 2 giây" tốt hơn "quay quay 40 giây rồi trắng" — mọi kỹ thuật chương này phục vụ cảm giác đó; từ chối đẹp là một dạng tôn trọng người dùng.

---

## 8. Đọc tiếp & bài tập

- Autoscaling (song hành): **9.2** · Mesh breaker: **9.4** · Rate limit: **11.3** · Trace tìm lan truyền: **11.1** · Client degradation: **6.1**
- **Bài tập 1:** Audit chính sách retry toàn hệ: bảng service × dependency × số lần × jitter × budget. Ô trống nhiều bất ngờ — nhiều hệ "retry 3 lần không jitter cho mọi thứ".
- **Bài tập 2:** Chạy kịch bản tiêm lỗi §6 với dependency quan trọng nhất. Ghi lại 3 câu trả lời; mỗi câu "không" là một ticket có tên (thêm jitter / breaker / fallback).
- **Bài tập 3:** Viết bảng ưu tiên shedding (lớp nào sống, lớp nào chết trước) và gửi phụ trách sản phẩm ký. Nếu không ai muốn ký — chính là lý do sự cố tới sẽ tự chọn thay bạn.

