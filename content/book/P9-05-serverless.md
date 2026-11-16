# 9.5 — Serverless, FaaS & Mô hình Compute

> **Tầng:** Nền tảng · **Quyển II** · **Trục đọc:** điều phối · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 9.1 (pod là đơn vị lớn hơn) · 3.9 (cold start theo runtime).

**Sợi chỉ đỏ:** *Có việc chạy 100 mili-giây mỗi giờ — serverless đáng tiền chưa?* — trả lời: việc 100 mili-giây mỗi giờ không cần máy chạy cả ngày — FaaS tính theo GB-giây và số lần gọi; nhưng cold start là con số phải đo chứ đừng đồn; giới hạn (thời gian, bộ nhớ, băng thông) tạo "dạng sự cố" riêng; và có điểm hoà vốn với container. Câu hỏi để lại cho chương sau: *Hạ tầng bằng code — IaC và GitOps: ai là sự thật khi hai bên khác nhau?*

**Thuật ngữ sẽ gặp:** *FaaS* — hàm được đánh thức theo request, tính GB-giây: gần đúng "không việc không tiền"; *cold start* — lần đánh thức đầu tiên: đo theo runtime (nối 3.9), đừng đồn; *giới hạn & hình dải* — thời gian chạy, bộ nhớ, số kết nối song song: vượt là sự cố dạng riêng của FaaS; *điểm hoà vốn* — tần suất gọi nào thì container rẻ hơn: chương có mô hình tính; *kiến trúc trưởng thành* — không phải "viết hàm rồi bỏ": connection, idempotency, quan sát vẫn phải có; *serverless rộng hơn FaaS* — DB, queue, storage quản lý: phổ "quên đi hạ tầng".

**Ví dụ mở đầu:** Resize ảnh món ăn DM: hàng trăm triệu ảnh mỗi tháng x vài trăm mili-giây — container 24/7 tốn gấp nhiều lần FaaS tính theo lần gọi. Nhưng hàm giữ connection DB giữa các lần gọi là bẫy số một; cold start Node và JVM chênh nhau một bậc. Chương này trao thước đo thay vì tín điều.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Compute nào cho workload này: VM / container / FaaS / edge | Mức "được phép quên hạ tầng" phù hợp là đâu? |
| 2 | Cold start chấp nhận được bao nhiêu | Người dùng chờ thêm 100 ms–1 s được không, ở đường nào? |
| 3 | Scale & giới hạn nền tảng (concurrent, thời gian chạy) | Đỉnh tải của tôi có đâm thủng giới hạn FaaS không? |
| 4 | Hoà vốn: giá per-invocation vs luôn-chạy | Ngưỡng QPS nào thì container rẻ hơn? (tính bằng số) |

---

## 2. Cơ chế

### 2.1 Bốn mô hình compute — phổ "quên được bao nhiêu"

| Mô hình | Bạn quản | Quên được | Đổi bằng |
|---|---|---|---|
| **VM** | OS, patch, scale | phần cứng, mạng | ops nặng nhất, linh hoạt nhất |
| **Container/K8s** | image, requests | OS, máy | nền tảng phải nuôi (→9.1) |
| **FaaS (Lambda/Functions)** | code hàm | mọi thứ | cold start, giới hạn, giá per-call |
| **Edge/Workers (→6.5)** | code | mọi thứ + gần user | runtime hạn chế, thời gian CPU nhỏ |

Không có mô hình "tiến hoá" đúng đắn — đó là bốn điểm trên một phổ trao đổi; hệ thật dùng nhiều mô hình (đường nóng container, webhooks FaaS, edge cho auth/rewrite).

### 2.2 Cold start — con số phải đo, không phải đồn

Bước khởi động: phân bổ sandbox + runtime + code + (init DB connect...) → trễ **trước** khi hàm chạy dòng đầu. Bậc: interpreter warm (V8 isolate — ms), container snapshot (100–300 ms điển hình (I)), JVM-classloading không snapshot (giây — SnapStart kiểu snapshot hoá để về vài trăm ms). Ba đòn giảm: (1) **provisioned concurrency** (giữ ấm — tiền tháng); (2) **init đúng nghĩa** (lazy init, connect ngoài handler, cache — cấu trúc code — →3.x); (3) **chọn runtime nhẹ** (JS/Python/Go-native). Đo bằng synthetic định kỳ — "cold start" thay đổi theo version/dependency; đo trước khi hứa SLA.

### 2.3 Giới hạn & hình dải — dạng sự cố riêng của FaaS

- **Concurrency cap** (số hàm chạy song song): đỉnh tải đâm cap → 429/Throttled **ở chỗ không đo được nếu không bật metric** — dẫn tới "mất request im lặng" (loại sự cố 11.2);
- **Thời gian chạy tối đa** (phút–15 m): batch dài phải tách/worker riêng;
- **Burst/quotas theo tài khoản**: một hàm "háo" (spam) có thể chiếm share tài khoản — cách ly hàm quan trọng vào account/region riêng (bulkhead — →8.5 nguyên lý lặp);
- **Ephemeral storage, payload size, network** — đọc bảng giới hạn **trước** kiến trúc, không sau sự cố.

### 2.4 Mô hình giá — điểm hoà vốn

FaaS tính theo GB-s + request; container tính theo giờ máy. Thực nghiệm phổ biến (hàm nhỏ): dưới ~vài chục nghìn request/giờ và traffic gồ ghề (đêm vắng) — FaaS rẻ hơn vì chỉ trả lúc chạy; traffic phẳng dày đặc — container/rẻ hơn rõ (luôn ấm rồi). Tính bằng công thức của chính bạn (giá cloud hiện hành + QPS p95 + thời gian chạy hàm) — mỗi vùng giá đổi, đừng dùng con số người khác (cũng là bài 5.16: sizing bằng số của mình).

### 2.5 Kiến trúc FaaS trưởng thành — không phải "viết hàm và bỏ"

- **Stateless tuyệt đối** (state ở DB/queue — →6.3 client-first lật ngược cùng nguyên lý);
- **Orchestration**: Step Functions/workflow cho chuỗi (đổi saga tự viết — →8.3);
- **Observability**: mỗi hàm cần log có trace-id (→11.1) — không có correlating id, chục hàm xích nhau là mê cung;
- **Dependency bundling**: hạn chế layer to (mỗi layer cộng cold start);
- **Thử tải đỉnh** trước mùa cao điểm (concurrent cap — §2.3) — drill như autoscale (→9.2).

### 2.6 Serverless rộng hơn FaaS

Xu hướng "serverless" = **đẩy trách nhiệm hạ tầng cho nhà cung cấp** ở mọi tầng: DB serverless (tính theo query — Aurora Serverless/ Neon-style — →5.2), queue/flow serverless, **container serverless** (Fargate/Cloud Run: container không nuôi node — vùng giữa đang phát triển nhanh nhất: quên node nhưng không bị giới hạn FaaS). Kiểm soát được thứ bạn giao: cấu hình network/egress vẫn là trách nhiệm của bạn (VPC endpoint — →9.3), IAM vẫn của bạn (→10.1).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Cold start container FaaS | ~100–300 ms | I | snapshot hoá |
| V8 isolate (edge) | ~ms | I | →6.5 |
| Lambda-style runtime cap | 15 phút | V | docs |
| Concurrent cap mặc định | ~1.000/account (nâng được) | V | docs AWS |
| Điểm hoà vốn điển hình | traffic gồ ghề → FaaS; phẳng dày → container | P | tự tính |

---

## 4. Suy luận kiến trúc

- **S1:** Chọn compute = chọn **điểm trên phổ "trách nhiệm ↔ kiểm soát"** — mỗi bước giao trách nhiệm cho nhà cung cấp là một giới hạn + một hoá đơn hình dạng khác; không có bước nào "miễn phí".
- **S2:** Tham số trụ: cold start p95/p99 (synthetic), tỉ lệ 429/throttle, giá/1M request theo tháng, tỉ lệ hàm không có trace-id (chất lượng kiến trúc).
- **S3:** FaaS đổi giá vận hành lấy giá giới hạn — tính điểm hoà vốn bằng số của chính hệ thống; edge FaaS (V8) đổi giới hạn runtime cho gần người dùng (cùng công với 6.5).
- **S4:** Serverless container (Fargate/Cloud Run) là **vùng cân bằng mới** cho đa số team: không nuôi node (bỏ 9.1 phần khó nhất) mà vẫn container đầy đủ — điểm mặc định hợp lý 2026 khi chưa cần hệ sinh thái K8s.
- **S5:** AI inference serverless (scaled-to-zero model endpoint — →12.3) đang là use case lớn nhất của FaaS thế hệ mới: model cold (tải trọng GW) là "cold start" mới cần đo.
- **S6:** Khi "FaaS chập chờn lúc đỉnh": đừng tối ưu code trước — kiểm tra concurrent/burst cap và IAM quota (§2.3); 90% sự cố FaaS là **giới hạn nền tảng**, không phải code chậm.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Đỉnh tải mất request im lặng | Concurrent cap 429 | metric throttle; quota tăng | §2.3 |
| p99 vã lai (lúc nhanh lúc chậm) | Cold start không provision | synthetic đo; giữ ấm | §2.2 |
| Đỉnh tải sập cả account | Burst chiếm share | tách account/region hàm quan trọng | §2.3 |
| Hóa đơn tăng bất ngờ | Traffic dày + per-call giá | tính hoà vốn §2.4 | §2.4 |
| Chuỗi hàm khó debug | Không trace-id xuyên | chuẩn hoá correlating id | §2.5 |
| Chạy lâu bị giết giữa chừng | Runtime cap | tách worker/Step Functions | §2.3 |

---

## 6. Cách đo

```bash
# Synthetic cold start: gọi endpoint FaaS mỗi phút, ghi time_total:
while true; do curl -s -o /dev/null -w '%{time_total}\n' $URL; sleep 60; done \
  | awk '{ if ($1>prev*3) print "COLD? " $1; prev=$1 }'
#   — vẽ phân phối: p50 vs p99 chênh > 5× = cold start đang chi phối trải nghiệm

# Metric phải bật: Throttles, ConcurrentExecutions, Errors (mặc định có — đừng tắt)
```

Nguyên tắc: **cold start và throttle là hai con số luôn đo** — không đo thì mọi tranh luận về "serverless chậm" là chuyện ma.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay FaaS:** container scale-to-zero (KEDA — →9.2) — cùng hiệu quả tiết kiệm, ít giới hạn, giữ trong cluster; **thay provisioned concurrency:** giữ 1 container nhỏ luôn chạy (đôi khi rẻ hơn "giữ ấm 10 hàm" — tính); **thay edge worker:** API gateway làm gần (→9.4/6.5).

Năm thấu kính:
- **Kinh tế:** FaaS là "trả theo ngụm": đỉnh ngắn giá rẻ, nền phẳng giá cao — vẽ biểu đồ tải 24h trước khi chọn (một buổi, quyết định cả năm).
- **Vận hành:** Ít infra phải trực nhưng **giới hạn phải đọc như runbook**: bảng cap/quota/giá là tài liệu vận hành của FaaS; mỗi khi nâng phiên nền tảng — đọc lại (chúng đổi không báo trước rộng rãi).
- **An ninh:** Nhiều hàm = nhiều xíu IAM role — quyền tối thiểu mỗi hàm (→10.1); hàm "quyền rộng vì tiện" là thứ lỗi khó thấy nhất ở serverless (audit định kỳ).
- **Lịch sử:** Không máy chủ hoàn toàn không mới: CGI (thập niên 90) cũng "spawn per request"; khác biệt hôm nay là **giây-scale scale + tính theo ngụm** — nền tảng làm được điều thập niên 90 không làm được vì cold start giờ tính bằng tiền được.
- **Người dùng:** Người dùng không biết hàm nào chạy — họ biết "webhook của tôi đôi khi mất 2 giây". Cold start là trải nghiệm thật; đo nó là tôn trọng người dùng cuối cùng của chuỗi vô hình đó.

---

## 8. Đọc tiếp & bài tập

- KEDA/scale-to-zero: **9.2** · Edge compute: **6.5** · Saga/orchestration: **8.3** · Trace xuyên hàm: **11.1** · AI inference serverless: **12.3** · Định giá kỹ thuật: **11.8**
- **Bài tập 1:** Vẽ biểu đồ QPS 24h của một dịch vụ (log hiện có). Chấm bằng mắt: gồ ghề hay phẳng? Gồ ghề → FaaS đáng tiền; phẳng → tính hoà vốn container.
- **Bài tập 2:** Đo cold start p99 (lệnh §6) một tuần. Nếu p99/p50 > 5× ở đường người dùng thật: bật provisioned một lớp nhỏ hoặc chuyển đường đó sang container.
- **Bài tập 3:** Đọc bảng giới hạn của nền tảng FaaS bạn đang dùng (cap, runtime, payload). Đối chiếu từng con số với hệ thống — mỗi con số gần chạm là một kế hoạch phải có (tăng quota hay tách kiến trúc).

