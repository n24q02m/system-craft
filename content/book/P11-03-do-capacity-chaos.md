# 11.3 — Đo lường, Capacity Planning & Chaos Engineering

> **Tầng:** Vận hành · **Quyển II** · **Trục đọc:** độ tin cậy · **Động từ liên quan:** Đo · Dự báo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** sizing-ops.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 3.1 (luật Little) · 5.16 (sizing).

**Sợi chỉ đỏ:** *Biết sức chứa đâu mà cân tải — đo đạc, capacity planning và chaos dạy gì?* — trả lời: biết sức chứa đâu mà cân tải — luật Little là con dao đa dụng của capacity; USL giải thích vì sao thêm máy không nhân đôi throughput (ph phần nối tiếp); load test đo giới hạn thật trước giờ chết; chaos engineering kiểm định giả định bằng thí nghiệm có chủ đích, không đợi sự cố tới. Câu hỏi để lại cho chương sau: *Sự cố lúc 2h sáng — ai chỉ huy, ai nói với khách, học được gì?*

**Thuật ngữ sẽ gặp:** *luật Little* — số việc trong hệ = throughput nhân thời gian ở lại: biết hai được một (nối 3.1, 5.16); *USL* — universal scalability law: throughput dẹt rồi đi xuống vì tranh chấp và đồng bộ: thêm máy có điểm hết lời; *điểm gối (knee)* — nơi thêm tài nguyên hết sinh lời: đo trước khi mua; *load test* — k6, Locust giả lập giờ cao điểm thật: giới hạn đo, không phỏng; *chaos engineering* — giết node có chủ đích trong giờ hành chính: giả định "chịu được một AZ chết" phải được kiểm định; *đủ cho bao nhiêu user* — đổi tài nguyên ra đơn vị người dùng: câu hỏi cuối cùng của capacity.

**Ví dụ mở đầu:** DM chuẩn bị chiến dịch 11/11: "chịu nổi không" không trả lời bằng cảm giác — Little cộng load test cho con số; chaos cho biết dự phòng có thật hay chỉ trên slide. Quy trình năm bước, làm trên chính hệ của bạn, không phải máy ảo demo.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Mô hình capacity: Little + USL dự báo theo tải nào | Tôi mua máy cho mùa cao điểm bằng phép tính hay bằng cảm giác? |
| 2 | Headroom mục tiêu (bao nhiêu % dư) | Đỉnh bất ngờ ×20% — tôi còn đứng không? |
| 3 | Chaos: thử cái gì, tần suất nào, ở đâu | Tôi có bằng chứng hệ chịu được "một AZ chết" không (→8.7)? |
| 4 | Đo giới hạn thật (load test định kỳ) | Sức chứa "trên giấy" vs đo lại gần đây nhất — chênh bao lâu? |

---

## 2. Cơ chế

### 2.1 Little's Law — con dao đa dụng của capacity

`L = λ × W` (số việc trong hệ = tốc độ đến × thời gian ở lại). Ba cách dùng:
- **Nhẩm node cần:** pod ≈ RPS × thời gian xử lý / sức một pod (+ headroom) — đã dùng ở 9.2;
- **Nhẩm hàng đợi:** thêm 100 ms xử lý với 2.000 RPS ⇒ thêm ~200 việc treo (RAM/conn phải có chỗ);
- **Chẩn bệnh:** queue dài + latency tăng mà throughput **không** tăng ⇒ đã chạm giới hạn (thêm queue không thêm năng lực — chỉ thêm chờ).

### 2.2 USL — tại sao "thêm máy" không nhân đôi

Universal Scalability Law: `C(N) = N / (1 + α(N−1) + βN(N−1))` — **α** là tranh chấp (lock, shared DB), **β** là nhất quán (giao tiếp đồng bộ chéo node). Hiểu đơn giản: có α/β > 0 thì scale ** logarithm rồi đi ngang, thậm chí tụt** (nhiều hệ thật có đỉnh: 8–16 node xong thêm máy chậm hơn — vì giao tiếp). Bài thực hành: đo throughput 1/2/4/8 node (load test), fit USL — biết đỉnh của mình **trước** khi khách biết. Đây là lý do "chia state" (→8.4 sharding, cell 8.7) là kỹ thuật capacity thật, còn "thêm máy" chỉ là kỹ thuật budget.

### 2.3 Quy trình capacity chuẩn (di chuyển từ sizing-ops)

1. **Liệt kê tài nguyên giới hạn** của từng tầng (CPU/mem/IO — →1.x; connection pool; license; quota cloud; **độ trễ nghiệp vụ**);
2. **Đo mức dùng theo p95/p99** theo ngày/tuần (không trung bình — đỉnh giết người);
3. **Nhân hệ số mùa** (giờ cao điểm × ngày lễ × tăng trưởng — lấy từ dữ liệu năm trước);
4. **Headroom 20–50%** cho sự cố + deploy (khi 1 node chết, phần còn lại gánh — →8.4 RF);
5. **Kế hoạch mua/scale theo lịch** (đặt trước mùa — cloud có quota cần xin trước — →9.2; mua máy on-prem có lead time tuần–tháng).

### 2.4 Load test — đo giới hạn thật

Chuẩn hoá: k6/Locust-style sinh tải thật (kịch bản hành vi, không "GET / một triệu lần"), môi trường giống prod (số liệu cloud test lệch nhau nhiều — cùng loại máy!), **theo dõi trong lúc dập**: RPS đạt, p95, error rate, dùng tài nguyên, **điểm gãy** (nơi p95 bắt đầu leo dốc không tuyến tính). Ba hình thức: **định kỳ** (mỗi quý — cảnh giới thấm dần), **trước sự kiện** (black Friday/mở thị trường), **soak** (6–24 h tải vừa — rò rỉ mem/conn chỉ lộ sau giờ). Kết quả lưu làm baseline cho 11.1 và cho autoscaler (→9.2 — biết max capacity một pod thật).

### 2.5 Chaos engineering — kiểm định giả định bằng thí nghiệm

Nguyên lý: giả định "hệ chịu được X" chỉ là giả định tới khi **thử X** (có kiểm soát). Bậc thang an toàn:
1. **Bắt đầu bằng quan sát** ("hệ thống Monday sáng" — tìm nhiễu sẵn có: tự nhiên đang chaos, đo trước);
2. **Tiêm nhỏ, giờ làm việc, có nút dừng**: kill một pod (→9.1: phải tự chữa, không ai biết); thêm 200 ms vào dependency (→8.5: breaker có mở không?); hết token CPU (→9.1: throttle?);
3. **Lên tiểu vùng**: tắt một AZ (→8.7 game day); hết một region (chỉ staging đầu tiên);
4. **Tự động hoá định kỳ** (chaos-scheduler): mọi thay đổi kiến trúc phải qua lại thí nghiệm tồn tại.
Điều kiện an toàn: **blast radius giới hạn** (một cell — →8.7), **abort tự động** khi SLO cháy quá nhanh (→11.1 burn rate), và **bảng giả định trước** (viết "tao tin hệ vẫn chạy" rồi thử — không có giả định ghi ra thì kết quả không có giá trị).

### 2.6 Đo cái khó: "đủ cho bao nhiêu người dùng"

Capacity cuối cùng là **con người**: "hệ chịu 50k concurrent user" cần định nghĩa user (kịch bản gì? tần suất bấm gì?) — quy đổi qua Little (mỗi user ≈ λ request/s trung bình → tổng λ → tài nguyên). Sai lầm kinh điển: demo 1.000 user nội bộ rồi mở cửa 1M (kịch bản thật khác: bot, sao chép, đồng bộ thiết bị — →6.3 nền tảng "khó chịu" hơn người). Mỗi sản phẩm lớn có **bảng quy đổi user → tài nguyên** sống và update theo quý — đó là tài sản của 11.5 (định giá unit economics).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Headroom | 20–50% | P | theo tầng |
| Load test định kỳ | quý | P | |
| Soak test | 6–24 h | P | rò rỉ |
| USL α, β | fit từ đo | I | |
| Chaos bước đầu | kill pod / thêm trễ | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Capacity là **bài toán mô hình hoá** (Little cho hàng đợi, USL cho tranh chấp), không phải danh sách máy — không có mô hình thì mọi tranh luận "thêm máy" là khẩu vị;
- **S2:** Tham số trụ: điểm gãy (từ load test gần nhất), headroom hiện tại theo tầng, sai số dự báo (dự báo vs thật mùa trước), số giả định chaos đã kiểm chứng.
- **S3:** Chaos đổi "niềm tin" lấy "bằng chứng" — cùng logic test (→7.6): nếu tự động hoá thì mỗi thay đổi kiến trúc được tái kiểm chứng không tốn người;
- **S4:** Mô hình hoá nối thẳng sang tiền (→11.5): mỗi unit capacity có giá — headroom là **bảo hiểm trả bằng tiền thật**; chọn bậc theo giá trị sự cố (như SLO chọn 9 — 11.1);
- **S5:** AI workload làm capacity hai lớp (→12.3): GPU khan hiếm (lịch/xếp hàng — →9.2 Kueue) + inference bùng nổ theo prompt — dự báo khó hơn web truyền thống một bậc; kỹ thuật của chương này giữ nguyên (đo, fit, thí nghiệm), chất liệu đổi;
- **S6:** Khi "hệ chậm không rõ vì sao": load test nhỏ theo tầng (DB? app? mạng?) tìm điểm gãy cục bộ — đừng tranh luận trước khi đo; gần như luôn có một tầng đã ở vùng phi tuyến (USL) mà dashboard trung bình không lộ.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Thêm máy mà không nhanh hơn | USL α/β cao (tranh chấp) | fit USL; tách state | §2.2 |
| Đỉnh giờ cao điểm chết nối tiếp | Headroom 0 + không dự báo mùa | headroom + kế hoạch | §2.3 |
| Chậm sau 12 h chạy | Rò rỉ (mem/conn) | soak test | §2.4 |
| Chaos chưa chạy lần nào | Giả định chưa kiểm chứng | bậc thang §2.5 | §2.5 |
| "50k user" không ai biết nghĩa | Thiếu bảng quy đổi user→tài nguyên | định nghĩa kịch bản user | §2.6 |
| Quota cloud chặn đúng mùa | Xin quota muộn | lịch xin trước mùa | §2.3 |

---

## 6. Cách đo

```bash
# Load test k6 — kịch bản "người dùng thật" (không GET /):
#   kịch bản: 60% xem, 30% tìm kiếm, 10% thanh toán (theo funnel thật)
k6 run --vus 500 --duration 15m scenario.js
#   theo dõi song song: p95, error%, CPU/mem, connection pool, queue depth
#   GHI LẠI điểm gãy — con số đó là "sức chứa thật hôm nay"

# Fit USL nhanh: đo throughput tại 1,2,4,8 worker —
#   nếu không gần tuyến tính → tìm lock chung (DB? cache? queue?)
```

Nguyên tắc: **sức chứa là con số có ngày đo** — "khoảng 1.000 RPS" không có ngày là đồ cổ (thêm dependency một lần là đổi).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay load test tự dựng:** dịch vụ load test managed (sinh tải từ nhiều vùng — hợp khi cần mô phỏng địa lý); **thay chaos tự viết:** nền tảng chaos có sẵn (Gremlin-style / ChAoS Mesh K8s) — ít quyền kiểm soát hơn, nhanh lên quy trình; **thay USL:** phỏng đoán tuyến tính "gấp đôi tải = gấp đôi máy" (đúng tới khi sai — và sai lúc đau nhất).

Năm thấu kính:
- **Kinh tế:** Headroom là tiền ngủ (→8.7 đã tranh luận) — chaos + load test cho biết **mức sập tối thiểu** đáng giữ: đo được mới tối ưu được, không đo thì trả cho cảm giác an toàn;
- **Vận hành:** Mùa cao điểm là lịch thiệt (không phải deadline thuyết trình) — chạy ngược lịch từ tháng cao điểm: load test tháng −2, nâng cấp tháng −1, freeze tuần cao điểm;
- **An ninh:** Load test và DDoS tự vệ dùng cùng hạ tầng sinh tải — biên đạo đức rõ ràng: **chỉ dập hệ mình, có kiểm soát**; dùng "thử tải" làm cớ dập hệ người khác là tội phạm, không phải kỹ thuật;
- **Lịch sử:** Kiểm thử tải từ mainframe (thập niên 60 — batch window) → chuẩn web (2000s) → Netflix Chaos Monkey (2011, "thả khỉ trong datacenter") → GameDay đa vùng (2015+) → chaos nền tảng tự động (hiện tại): mỗi bước đưa "thí nghiệm" từ nghệ khoa học sang pipeline;
- **Người dùng:** Người dùng là đám đông xuất hiện **đồng lúc không báo trước** (viral, khuyến mãi, tin xấu) — chương này là cách hệ "đón" đám đông thay vì bị giẫm; và người dùng thứ nhất của capacity planning luôn là... chính bạn (dev thử ở staging cũng là "đám đông nhỏ").

---

## 8. Đọc tiếp & bài tập

- SLO với dữ liệu capacity: **11.1** · Telemetry: **11.2** · Autoscale dùng baseline: **9.2** · Sizing DB: **5.16** · Cell/blast radius: **8.7** · GPU capacity: **12.3**
- **Bài tập 1:** Chạy load test theo kịch bản thật (§6) và ghi điểm gãy kèm ngày. So với "con số sức chứa" đang được dùng trong kế hoạch — chênh bao nhiêu %? Đó là rủi ro định lượng.
- **Bài tập 2:** Fit USL thô: đo throughput 1/2/4/8 bản sao service chính. Vẽ đường — nếu cong xuống sớm, tìm lock chung (thường là một DB hoặc một cache chia sẻ) và viết ticket "tách state".
- **Bài tập 3:** Một thí nghiệm chaos nhỏ tuần này (giờ làm việc, có nút dừng): kill pod của service quan trọng nhất. 5 phút sau hệ thế nào? Nếu ai đó ngoài on-call nhận ra — bài học về dependency; nếu không ai nhận ra — bằng chứng đầu tiên rằng tầng tự chữa sống thật.

