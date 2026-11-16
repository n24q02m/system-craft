# 9.1 — Kubernetes Internals (v1.35–1.37)

> **Tầng:** Nền tảng · **Quyển II** · **Trục đọc:** điều phối · **Động từ liên quan:** Vận hành · Chọn
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số) · **Bản mới nhất đã verify: 1.37**
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.2 (Raft — etcd chính là control plane) · 2.3 (cgroups).

**Sợi chỉ đỏ:** *Tự vận hành chục máy thủ công đã chật — Kubernetes và control plane gánh việc gì?* — trả lời: K8s gánh việc "giữ chục máy chạy đúng trạng thái đã khai báo" — control plane là bốn cơ quan cộng một kho (etcd chạy Raft); pod có vòng đời và bốn probe; requests/limits quyết định xếp chỗ và mức throttle; PDB là hợp đồng hạ tầng cho mọi đợt nâng cấp. Câu hỏi để lại cho chương sau: *Tải trưa cao gấp mười lần tối — autoscale tính theo gì, GPU xếp thế nào?*

**Thuật ngữ sẽ gặp:** *control plane* — API server, scheduler, controller manager, etcd: khai báo rồi vòng reconcile kéo về; *reconcile loop* — quan sát, so sánh, sửa: đúng trạng thái là đủ, không ra lệnh từng bước; *probe* — readiness, liveness, startup: LB và kubelet dựa vào để biết pod sống tới mức nào; *requests/limits* — CPU và RAM cam kết và trần: scheduler xếp theo requests, vượt limits là bị throttle (bẫy có mã sự cố I-057, I-062); *PDB* — PodDisruptionBudget: đợt nâng cấp phải tôn trọng số pod tối thiểu; *topology spread* — trải pod theo zone và rack: chống trùng máy.

**Ví dụ mở đầu:** Đêm nâng cấp cụm DM, node bị drain lần lượt: service không có PDB bị cạo sạch pod khi vẫn đang nhận traffic; service có PDB thì hạ tầng phải chờ. K8s không phải "máy ảo to" — là vòng reconcile giữ trạng thái khai báo bất chấp máy chết, và chương có hẳn mục chọn "dùng K8s đúng chỗ".

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | requests vs limits: chính sách cho CPU/mem theo lớp workload | Tôi muốn **chịu lỗi vì OOM** hay **chậm vì throttle** — từng lớp việc? |
| 2 | PDB & graceful drain | Node nâng cấp — tôi chấp nhận sập bao nhiêu pod cùng lúc? |
| 3 | Topology spread/anti-affinity: trải theo AZ/node như nào | Một AZ chết còn chạy được bao nhiêu %? |
| 4 | Ai được scheduling "đắt" (GPU, node riêng, taint) | Workload nào xứng node xịn — có bảng giá nội bộ chưa? |

---

## 2. Cơ chế

### 2.1 Control plane — bốn cơ quan + một kho

```
[kube-apiserver] ←— mọi đọc/ghi qua đây (REST + watch)
   ├── [etcd]            — state nguồn chân lý (Raft — →8.2)
   ├── [scheduler]       — gán pod → node (filters + scoring)
   ├── [controller mgr]  — các vòng reconcile (deployment, node, endpoint…)
[kubelet + container runtime] — mỗi node: đảm bảo pod chạy đúng "spec"
```

Ba phẩm chất để nhớ: (1) **mọi thứ là vòng reconcile** — declarative: so trạng thái mong muốn vs thật, sửa lệch (mô hình chat cũng dùng ở nền tảng khác — từ Redis đến Terraform); (2) **watch là xương sống** — client (kubectl, controller) đăng ký nhận biến đổi, không poll (etcd watch — →8.2); (3) **apiserver là cổng duy nhất** — mọi tự động hoá, policy, audit đi qua một chỗ (tốt để kiểm soát, tệ nếu nó chết: control plane HA = 3 etcd + ≥2 apiserver).

### 2.2 Pod lifecycle & probe — bốn con ngựa

- **startupProbe** (đợi khởi động chậm) → **readinessProbe** (pod "sẵn" nhận traffic — Gateway/Service chỉ route pod ready) → **livenessProbe** (chết thì restart) — thứ tự sai: liveness hung quá giết app đang khởi động = vòng restart vĩnh viễn (lỗi thường gặp nhất của người mới);
- **preStop + terminationGracePeriodSeconds**: nhận SIGTERM → làm nốt việc (drain connection — →8.5), rồi tắt; Service có **readiness gate** để không còn nhận request mới; quá grace period thì SIGKILL. Drain node nâng cấp: cordon (không pod mới) → evict (tôn trọng **PDB**).

### 2.3 Requests/limits & CFS throttle (I-057, I-062 phải tránh)

- **requests** = chỗ dựa scheduler (bin-packing theo tài nguyên cam kết); **limits** = trần cứng;
- CPU limit = CFS quota: hết quota trong chu kỳ 100 ms thì **dừng tới kỳ sau** — app "chậm vã lai" không phải vì thiếu CPU tổng, mà vì **lố quota theo từng mảnh nhỏ** (throttle latency — p99 giết chết);
- Mem limit vượt = **OOMKilled** (chết ngay — đổi lấy "không lây lan");
- Chính sách chuẩn: CPU requests=limits (tránh throttle) hoặc requests cao + không limit cho latency-critical; mem requests=limits (đo trước — →5.16 sizing); **burstable cho batch, guaranteed cho đường nóng**.

### 2.4 PDB — hợp đồng hạ tầng cho mọi đợt nâng cấp

PodDisruptionBudget (`minAvailable`/`maxUnavailable`): evict (tự nguyện — drain) không vi phạm; node chết (không tự nguyện) PDB không cứu. Thiếu PDB: một đợt nâng cấp cluster có thể "ăn" cả service (I-058); PDB quá chặt (`maxUnavailable: 0` + single-replica): drain node **kẹt vĩnh viễn** — đợt nâng cấp treo. Công thức: replicas ≥ 3 + PDB `maxUnavailable: 1` là điểm khởi đầu chuẩn cho service quan trọng.

### 2.5 Trải topology & chống trùng máy

`topologySpreadConstraints` (mỗi AZ một số pod cân) + `anti-affinity` (hai pod "quý" không cùng node) — hiện thân cloud của nguyên lý 8.4 §2.6 (replica không cùng failure domain). Thiếu hai thứ này: cluster "đẹp trung bình" nhưng một AZ/node giữ trọn bản sao của service — sự cố vật lý thành sự cố tổng (I-062).

### 2.6 Chọn "dùng K8s" đúng chỗ

K8s là **hệ điều hành của trung tâm dữ liệu** — trả chi phí học + vận hành (control plane, upgrade, bảo mật — đủ nội dung P9) để mua: API chuẩn hoá cho mọi workload + hệ sinh thái vận hành phong phú nhất. Không cần khi: < ~10 service ổn định + 1 team nhỏ (mấy VM + systemd + Ansible giản dị hơn — định luật Yagni của hạ tầng); static website (CDN — →6.5); batch hiếm khi chạy (FaaS — →9.5).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| K8s bản mới | 1.37 (1.37.2 patch 30/10) | V | versions.csv |
| CFS chu kỳ | 100 ms | V | |
| terminationGrace | 30 s mặc định; batch có thể 10 m+ | P | |
| PDB chuẩn | ≥3 replica, maxUnavailable 1 | P | |
| Pod đi từ Pending→Running | s (scheduler ~ms) | I | |

---

## 4. Suy luận kiến trúc

- **S1:** K8s là **máy trạng thái reconcile hướng declarative** — hiểu mô hình này dự đoán được mọi hành vi lạ (đó là lý do nó "tự chữa": lỗi pod bị thay, không ai SSH sửa từng cái — tinh thần immutable của 2.7).
- **S2:** Tham số trụ: số lần restart/evict theo ngày, throttle time p99 (container_cpu_cfs_throttled), tỉ lệ pod không spread đúng topology, thời gian drain node trung bình.
- **S3:** requests/limits là **bảng giá nội bộ tài nguyên** — đặt theo đo lường (p95 usage + headroom), review theo quý như sizing 5.16; "đặt đại 1 CPU/1 GB" là ẩn số chi phí + rủi ro.
- **S4:** Control plane dựa etcd (→8.2): mất đa số = cluster "đóng băng" (pod vẫn chạy nhưng không đổi gì) — backup etcd + drill restore là nghĩa vụ, không phải tùy chọn.
- **S5:** GPU/DRA (→9.2) và workload AI đang đổi scheduler K8s nhanh nhất từ trước tới nay (tham số mới: topology GPU, kết nối NVLink, MIG slice) — kiến trúc platform cần định vị "node thường/GPU" như hai lớp tài nguyên riêng.
- **S6:** Khi pod "pending/evicted": đọc **event stream trước** (`kubectl describe`) — 90% câu trả lời nằm trong 5 dòng cuối (hết tài nguyên, PDB chặn, affinity vô lời giải — I-057/I-058/I-062 đủ ba kết luận).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Pod Pending mãi (I-057) | Không đủ tài nguyên/affinity/quota | `describe` đọc events | §2.3 |
| Latency vã lai khắp app | CFS throttle (CPU limit thấp) | metric throttled seconds | §2.3 |
| Restart loop | Liveness đánh app đang khởi động | thêm startupProbe | §2.2 |
| Drain node kẹt (I-058) | PDB quá chặt | sửa maxUnavailable | §2.4 |
| Một AZ mất = mất service (I-062) | Không topology spread | thêm constraint | §2.5 |
| Lỗi 502 lúc deploy | Không preStop/readiness đủ | review lifecycle | §2.2 |

---

## 6. Cách đo

```bash
kubectl top nodes; kubectl top pods -A | sort -k3 -h | tail   # usage thật
kubectl get events -A --sort-by=.lastTimestamp | tail -30      # "console lỗi"
kubectl get pods -A -o wide | column -t | less -S              # spread bằng mắt

# Throttle CPU (PromQL): rate(container_cpu_cfs_throttled_periods_total[5m])
#   / rate(container_cpu_cfs_periods_total[5m])  — > 5% với latency-critical là đỏ
```

Nguyên tắc: **đọc events trước, hỏi Slack sau** — K8s kể chuyện mình tốt hơn đồn thổi; hình thức "chẩn 5 phút" chuẩn của platform.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự vận hành:** managed K8s (GKE/EKS/AKS) — bỏ việc khó nhất (control plane HA, upgrade) — mặc định khôn ngoan 2026; **thay K8s:** Nomad (đơn giản hơn, hệ sinh thái nhỏ), VM + systemd (rẻ, không API chuẩn), serverless container (→9.5 — bỏ luôn khái niệm node). Chọn theo **đội hình thật**, không theo xu hướng.

Năm thấu kính:
- **Kinh tế:** Cluster K8s "không có tải" vẫn tốn (control plane + node tối thiểu + công vận hành) — tính giá/tri service; dưới một mốc thì mỗi service đắt hơn VM thuần.
- **Vận hành:** Upgrade cluster mỗi ~4 tháng theo nhịp release — đặt lịch là nghĩa vụ của platform team; PDB/health chuẩn là "điều kiện nâng cấp được" (chapter này chính là cẩm nang nâng cấp không sập).
- **An ninh:** Mọi thứ qua apiserver = **một chỗ áp policy/audit** (RBAC, admission, network policy — →9.4) — nhưng cũng một chỗ bị chiếm là mất cả vương quốc: ít đặc quyền, PSA, audit log bật (→11.6).
- **Lịch sử:** Borg (Google nội bộ 2003+) → Omega → Kubernetes mở (2014, Raft/etcd nền tảng — →8.2) → chuẩn de-facto (2018+) → API mở rộng (Gateway API, DRA — 2020s): mỗi giai đoạn nhường một phần "ma thuật nội bộ" cho cộng đồng — lý do hệ sinh thái thắng.
- **Người dùng:** Với dev, "kubectl apply rồi đi uống cà phê, hệ tự lo phần còn lại" là trải nghiệm sản phẩm thật của platform; chương này tồn tại để câu đó không phải khẩu hiệu (pod pending 2 giờ vì thiếu PDB cũng là trải nghiệm — chiều ngược lại).

---

## 8. Đọc tiếp & bài tập

- Autoscaling & GPU: **9.2** · Mạng/mesh: **9.4** · Cơ chế đồng thuận etcd: **8.2** · Bảo mật platform: **11.6** · Giới hạn Linux nền (cgroup/CFS): **2.3**
- **Bài tập 1:** `kubectl top pods` — so usage thật với requests của 10 deployment chính. Chênh > 3× (đặt thừa) hoặc < 0,5× (đặt thiếu, đợi sự cố): điều chỉnh từng cái — 30 phút, tiền thật.
- **Bài tập 2:** Mô phỏng mất một node (drain + cordon giờ làm việc): service còn phục vụ? Bao nhiêu pod "kẹt"? — nếu trả lời không/kẹt: PDB + spread đang là lý thuyết (I-058/I-062).
- **Bài tập 3:** Đo throttle ratio (truy vấn §6) cho service latency-critical quan trọng nhất. > 5%? Tăng limit hoặc bỏ limit (CPU) và theo dõi p99 một tuần.

