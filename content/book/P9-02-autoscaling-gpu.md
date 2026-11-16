# 9.2 — Autoscaling (HPA/VPA/KEDA/Karpenter) & Lập lịch GPU

> **Tầng:** Nền tảng · **Quyển II** · **Trục đọc:** điều phối · **Động từ liên quan:** Chọn · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 9.1 (pod, scheduler) · 5.16 (sizing, headroom).

**Sợi chỉ đỏ:** *Tải trưa cao gấp mười lần tối — autoscale tính theo gì, GPU xếp thế nào?* — trả lời: tải trưa gấp mười lần tối — HPA nhân pod theo metric nhưng có dao động "cưa" phải tránh (I-059); KEDA đánh thức worker theo chiều dài hàng đợi, scale-to-zero cho việc theo nhịp; Karpenter mua node đúng hình workload; GPU là tầng lập lịch mới; kèm mô hình đơn giản để nhẩm. Câu hỏi để lại cho chương sau: *Mạng trong cloud — VPC, private link, endpoint: an toàn và tiền đổi chỗ nào?*

**Thuật ngữ sẽ gặp:** *HPA* — nhân pod theo CPU hoặc queue: hành xử theo chu kỳ, đặt sai nhịp là dao động cưa phình-xẹp; *scale-to-zero* — không việc thì tắt hẳn: rét là cái giá của lần đánh thức sau; *KEDA* — autoscale theo độ sâu hàng đợi Kafka/Redis: worker hiện đại; *Karpenter* — mua node đúng kích cỡ workload, xong việc trả lại: node như mua rau; *DRA* — lập lịch GPU theo tài nguyên động: GPU không còn là "trời cho ai lấy"; *mô hình nhẩm* — QPS nhân số pod nhân giá node: suy luận quy mô không cần bảng tính.

**Ví dụ mở đầu:** Trưa DM gấp mười lần sáng sớm: HPA nhân worker theo độ sâu hàng đợi — nhịp đặt sai, cụm "cưa" liên tục phình rồi xẹp. Karpenter mua node đúng cỡ thay vì ba loại cố định đùn đẩy. Chương này là bốn công cụ và một mô hình nhẩm để ước lượng trước khi tin dashboard.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chiều scale chính: pod (HPA) hay node (Karpenter/CA) | Thường hết pod trước hay hết node trước? |
| 2 | Metric scale: CPU/mem, RPS, latency, queue depth | Tín hiệu nào *dẫn* tải của tôi (không phải *theo sau*)? |
| 3 | Scale-to-zero & queue-driven (KEDA) cho workload nào | Batch/job chờ có đáng để không máy nào chạy? |
| 4 | GPU: pool riêng? MIG/time-slicing? queue (Kueue/Volcano)? | GPU đắt ×30 — ai được dùng, chờ thế nào? |

---

## 2. Cơ chế

### 2.1 Bốn công cụ, bốn bài toán

| Công cụ | Scale cái gì | Tín hiệu | Điểm mạnh |
|---|---|---|---|
| **HPA** | số **pod** | CPU/mem, custom metrics, RPS | ngắn mạch, mặc định |
| **VPA** | **requests** của pod (kích thước) | usage lịch sử | sửa "đặt sai requests"; không tăng số pod |
| **KEDA** | pod từ **hàng đợi ngoài** | queue depth (Kafka/Redis/…) | scale-to-zero tự nhiên cho worker |
| **Karpenter/CA** | **node** (mua máy) | pod pending | đúng loại máy, đúng giá, giây–phút |

Bộ hoàn chỉnh phổ biến 2026: HPA (đường nóng) + KEDA (worker theo queue) + Karpenter (máy theo nhu cầu) + VPA (chỉnh requests định kỳ, chế độ **InPlaceOrRecreate** cập nhật không restart pod — đáng dùng để "sửa dần" requests sai).

### 2.2 HPA hành xử — tránh cưa (I-059)

HPA tính `desired = ceil(current × metric/target)`. Ba điều chỉnh bắt buộc biết: **scale-down stabilization** (mặc định 5 phút nhìn về quá khứ — tránh giật), **behavior** (tốc độ lên nhanh/xuống chậm — lên có thể 100%/phút, xuống 10%/phút), **metric nhiễu** (CPU trên pod đang khởi động = ảo; scale theo **external metric** như RPS/queue thường sạch hơn — →11.2 metric đáng tin). Cưa qua lại (phình/xẹp lặp) gần như luôn do tín hiệu nhiễu hoặc stabilization quá ngắn — tăng cửa sổ, đổi metric, hoặc thêm **tolerance** (±10% không hành động).

### 2.3 Scale-to-zero & KEDA — worker hiện đại

Worker nghe queue: 0 tin → 0 pod (tiết kiệm lớn cho traffic lẻ tẻ/giờ thấp điểm); tin tới → scaler đánh thức (giây–chục giây — chấp nhận được cho async, không cho HTTP đồng bộ). Kết hợp §8.5: **autoscale là kế hoạch dài hạn, chịu lỗi là kế hoạch tức thời** — queue + retry + breaker sống sót trong cửa sổ scale-up; nếu bỏ chương đó thì scale-to-zero chỉ đổi "chậm vì không máy" thành "lỗi vì không ai nghe".

### 2.4 Karpenter — mua node như mua rau

Thay "node group cố định" bằng pool linh hoạt: Karpenter nhìn pod pending → chọn loại máy **vừa vặn** (CPU/mem/GPU/spot) → tạo → gộp/rã khi vắng (consolidation). Lợi kép: giá (spot + đúng size) và tốc độ (không chờ cấu hình). Rủi ro: pod lẻ tạo máy riêng (đặt **limits cho daemonset + ttl + consolidation**); spot bị giật (đã có grace — vẫn cần PDB/spread — →9.1: hai chương cùng một chuỗi an toàn).

### 2.5 Lập lịch GPU — tầng tài nguyên mới (DRA)

GPU: đắt, cồng kềnh, gắn qua PCIe/NVLink — lịch không chỉ "đủ số" mà "đúng **topology**". Ba mô hình chia: (a) **nguyên con** (đơn giản, lãng khi job nhỏ); (b) **MIG** (chia vật lý một GPU thành nhiều slice cô lập — cho inference nhỏ); (c) **time-slicing** (chia thời gian — rẻ, không cô lập, độ trễ chao đảo). **DRA (Dynamic Resource Allocation)** — API thế hệ mới của K8s — mô tả yêu cầu tài nguyên "đặc biệt" (GPU, FPGA, kết nối) và để driver quyết định; kèm hàng đợi công bằng: **Kueue/Volcano-style** (batch đợi pool GPU theo quota/priority — tránh job lớn bỏ đói job nhỏ). Đặt giá nội bộ GPU (đội nào bao nhiêu giờ) — không có giá thì GPU bị dùng như MIỄN PHÍ (luôn khan hiếm).

### 2.6 Suy luận quy mô — mô hình đơn giản để nhẩm

Công thức cảm giác (Little's law — →5.16): cần pod ≈ RPS × thời gian-xử-lý / (mức chịu của 1 pod) × headroom. Ví dụ: 2.000 RPS × 50 ms / (1 pod chịu 200 RPS) = 5 pod × 1,5 headroom ≈ 8. Nhẩm trước, dùng HPA theo metric để giữ — **con số "tự động" không có nghĩa là "không cần hiểu"** (autoscaler giấu mô hình, không xoá mô hình).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| HPA phản ứng | ~15–60 s (metric + định kỳ) | I | |
| Karpenter tạo node | ~30–60 s | I | |
| Scale-to-zero wake | giây–chục giây | I | theo scaler |
| GPU so CPU giá | ~×10–30 mỗi đơn vị tính toán | I | |
| DRA | beta→GA hoá dần 1.34–1.37 | V | kiểm tra bản đang dùng |

---

## 4. Suy luận kiến trúc

- **S1:** Scale theo **trục** pod/node/tài nguyên-đặc biệt là ba quyết định khác nhau; tổ chức trưởng thành có câu trả lời cho cả ba trục (HPA/KEDA, Karpenter, DRA+queue) thay vì một "autoscaling" chung chung.
- **S2:** Tham số trụ: thời gian từ tải tăng → sức chứa tăng (đo bằng thử tải định kỳ), số lần scale-up/down mỗi giờ (dao động = bệnh I-059), tỉ lệ node rỗng (tiền ngủ), tỉ lệ dùng GPU (giờ GPU thuê × dùng thật).
- **S3:** Chọn metric = chọn **mô hình hệ thống**: RPS dẫn trước tải; CPU theo sau (đang bận≠sắp bận); queue depth là tín hiệu tương lai tốt nhất cho worker — đặt metric theo nghiệp vụ, không theo default.
- **S4:** Autoscale không thay chịu lỗi (8.5) và không thay sizing ban đầu (5.16) — ba lớp ba khung thời gian: thiết kế (tháng), thích ứng (phút), sống sót (giây).
- **S5:** Workload AI (training/inference) đổi mọi giả định scale: tính toán dài (giờ–ngày), checkpoint/restart đắt, và **topology-aware scheduling** (NVLink/affinity — DRA) — platform cho AI là chương lớn riêng của P12 (→12.3).
- **S6:** Khi "scale rồi vẫn chậm": kiểm tra chiều bị kẹt — pod scale nhưng node không (Karpenter thiếu quyền/hết quota); hoặc pod lên nhưng cold (JIT warm-up — →1.1); autoscaler đúng, cổ chai ở tầng khác.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Scale cưa qua lại (I-059) | Metric nhiễu + ổn định ngắn | đổi metric + behavior | §2.2 |
| Tăng tải nhưng không scale | Metric sai (CPU ảo/targets sai) | audit pipeline metric | §2.2 |
| Pod scale, node không | Node pool cạn/quota | Karpenter log/quota | §2.4 |
| Queue phình, worker 0 | KEDA trigger cấu hình sai | audit scaler + auth | §2.3 |
| GPU nằm không dùng | Không ai chịu giá + job bỏ đói | quota + Kueue policy | §2.5 |
| Spot giật làm vỡ batch | Không checkpoint/PDB | checkpoint + tolerance (→12.3) | §2.4 |

---

## 6. Cách đo

```bash
# Thử tải định kỳ (mỗi tháng): bơ tải thật (k6/locust) tăng 10 phút
#   đo: T0 tải tới → T1 pod mới ready → T2 p95 ổn định
#   "Thời gian đáp ứng scale" = T2−T0 — con số này là SLA platform thật của bạn

kubectl get hpa -w      # xem hành xử theo thời gian thực (cưa thấy ngay)
kubectl get nodes -L karpenter.sh/provisioner-name -o wide   # máy đang theo pool nào
```

Nguyên tắc: **autoscaling phải được kiểm tra như tính năng** (load test định kỳ), không phải "cấu hình xong là xong" — hành vi metric nhiễu chỉ lộ ra dưới tải thật.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay KEDA:** cron scale (biết giờ cao điểm — mộc mạc, đủ cho mẫu tải lặp); **thay Karpenter:** node group có sẵn + cluster-autoscaler (ổn định, ít "thông minh" hơn); **thay tất cả:** mặc định + theo dõi (scale tay theo lịch — hệ nhỏ vẫn xứng đáng đơn giản).

Năm thấu kính:
- **Kinh tế:** Autoscale là công cụ **chuyển CAPEX thành OPEX theo phút**: giá chênh giữa "mua cho đỉnh" và "mua theo mức dùng" là toàn bộ ROI chương này (đo bằng: giá tháng node rỗng).
- **Vận hành:** Mỗi tầng scale có alarm riêng (pending quá lâu, queue quá sâu, scale-down liên tục) — im lặng của autoscaler là tin xấu, không phải tin tốt.
- **An ninh:** Node xuất hiện/tự biến mất mở mặt diện mới (image trust cho node mới, spot eviction abuse-detection) — IaC (→9.6) là cách giữ pool node "sạch" khi nó thay đổi liên tục.
- **Lịch sử:** Tự scale từ batch scheduler (thập niên 60!) → web auto-scaling nhóm (2010s) → K8s HPA (2015) → event-driven KEDA (2019) → DRA/topology (2020s): mỗi bước thêm một **loại tín hiệu** và một **loại tài nguyên** — xu hướng: tín hiệu ngày càng gần nghiệp vụ, tài nguyên ngày càng gần phần cứng.
- **Người dùng:** Người dùng cuối không biết có 3 hay 30 pod — họ biết "giờ cao điểm không chậm". Autoscale là cách trả tiền đúng cho câu đó thay vì trả cho đỉnh 24/7.

---

## 8. Đọc tiếp & bài tập

- K8s cơ bản: **9.1** · Chịu lỗi trong cửa sổ scale: **8.5** · Sizing/Little: **5.16** · AI scheduling sâu: **12.3** · Đo SLO cho platform: **11.2**
- **Bài tập 1:** Liệt kê workload bạn theo trục: đường nóng (HTTP) / worker (queue) / batch (lịch) — mỗi hàng ghi công cụ scale hiện tại. Trống ở đâu, rủi ro ở đó (hoặc tiền bị đốt ở đó).
- **Bài tập 2:** Chạy thử tải §6 một lần tháng này, ghi "thời gian đáp ứng scale". Con số > 5 phút với đường nóng = must-fix trước mùa cao điểm.
- **Bài tập 3:** Nếu có GPU: đo tỉ lệ giờ-GPU-thuê × thực-dùng tuần này (metric nvidia hoặc cloud billing). < 40%? Bắt đầu MIG/queue/đặt giá — mỗi điểm % là hóa đơn thật.
