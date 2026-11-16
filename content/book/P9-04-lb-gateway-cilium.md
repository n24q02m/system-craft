# 9.4 — Cân bằng Tải, Gateway API & Cilium eBPF Mesh

> **Tầng:** Nền tảng · **Quyển II** · **Trục đọc:** điều phối · **Động từ liên quan:** Chọn · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 9.1 (Ingress nằm trong cụm) · 2.7 (thang cách ly — mesh cũng là sandbox).

**Sợi chỉ đỏ:** *Vào cụm qua cửa nào — LB, gateway, mesh làm gì mà app không cần biết?* — trả lời: vào cụm qua ba tầng cân bằng — mỗi tầng một câu hỏi (L4 connection, L7 route, logic mesh); Gateway API là Ingress thế hệ trưởng thành; mesh có ba mô hình triển khai; và health check là hợp đồng sống: LB bắn tin vào xác khi probe nói dối. Câu hỏi để lại cho chương sau: *Có việc chạy 100 mili-giây mỗi giờ — serverless đáng tiền chưa?*

**Thuật ngữ sẽ gặp:** *ba tầng cân bằng* — L4 theo connection, L7 theo route, mesh theo logic service: mỗi tầng một câu hỏi; *Gateway API* — Ingress trưởng thành: role chia quyền, route giàu hơn, chuẩn 2026; *ba mô hình mesh* — sidecar, sidecar-less, eBPF: cùng giải mTLS, retry, telemetry: chọn theo chi phí và đội ngũ; *health check* — hợp đồng sống của LB: probe qua không nghĩa là người dùng hài lòng; *circuit breaking ở gateway* — cản bão ngay từ tầng vào (nối 8.5); *quan sát tại gateway* — trace, access log: chỗ duy nhất thấy mọi request.

**Ví dụ mở đầu:** Endpoint trả 200 cho probe nhưng response người dùng mất nhiều giây: LB vẫn bắn traffic — hợp đồng sống chỉ là "probe qua", không phải "người dùng ổn". Gateway đặt retry sai là bão nhân đôi đúng lúc hệ yếu nhất. Chương này đặt từng tầng đúng câu hỏi của nó thay vì chồng ba lớp làm cùng một việc.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | LB lớp nào ở đâu: L4 cloud / L7 gateway / service mesh | Terminated TLS ở đâu, quyết định route theo gì? |
| 2 | Ingress→Gateway API (hay còn chờ)? | Tôi cần tính năng Gateway API (cross-namespace, L7 phong phú) chưa? |
| 3 | Mesh: sidecar / ambient / không mesh (Cilium thay kube-proxy) | Cần mTLS + policy L7 thật không — hay chỉ cần network policy? |
| 4 | Health check & draining đúng nghĩa | Deploy của tôi có làm rơi request không — ai đo? |

---

## 2. Cơ chế

### 2.1 Ba tầng cân bằng — mỗi tầng một câu hỏi

```
[Cloud L4 NLB]        — TCP/UDP, IP spoof-check, cực bền, "đầu mối" (IP tĩnh)
      ↓
[L7 Gateway/API GW]   — HTTP: route theo path/header, TLS end, rate limit, authn
      ↓
[Service (kube-proxy/Cilium)] — trong cluster: pod-to-pod, east-west
```

Quy tắc chọn: kết thúc client **L4 cloud** (an toàn, nhanh); **L7** ở gateway trong cluster/edge (linh hoạt, quan sát được); **east-west** qua service/mesh. Cùng lúc trên một chuỗi là bình thường — mỗi lần "lặp L7" (hai lớp cùng parse HTTP) cần lý do ( thường không có).

### 2.2 Gateway API — Ingress trưởng thành

Ingress (annotation thần thánh chồng chất) chạm trần: mỗi annotation là cài đặt của một controller cụ thể, không chuẩn hoá, không phân quyền. Gateway API tách vai: **GatewayClass** (loại hạ tầng — ai vận hành), **Gateway** (cửa — IP + TLS), **Route** (HTTPRoute/GRPCRoute/TCPRoute — do **team app** sở hữu, có thể cross-namespace có kiểm soát `ReferenceGrant`). Kiểu này hợp mô hình "platform team cấp cửa, app team tự khai route" — cùng triết lý cell/platform 8.7. 2026: Gateway API GA (v1), triển khai rộng Envoy Gateway/NGINX/Traefik/Cilium; Ingress vẫn chạy — kế hoạch dời theo strangler (→8.8), đừng big-bang.

### 2.3 Service mesh — ba mô hình

| Mô hình | Cách | Đổi bằng gì |
|---|---|---|
| **Sidecar** (Envoy per pod) | proxy theo từng pod, mTLS tự lo | ~50–100 MB RAM/pod + sidecar lifecycle |
| **Ambient/sidecar-less** | L4 overlay node + L7 chỉ nơi cần (waypoint) | ít tài nguyên, phức tạp mới để hiểu |
| **eBPF-native (Cilium)** | trong kernel (→2.7 eBPF), thay kube-proxy; policy L7 qua proxy chọn lọc | quan trọng hoá kernel; less magic, more tracing (Hubble) |

Câu "có cần mesh không": mesh mua **mTLS everywhere + policy L7 + telemetry tự động**; nếu tổ chức chưa có yêu cầu zero-trust nội bộ (→10.1) và chưa đau vì "không biết ai gọi ai" — network policy + gateway là đủ (mesh là 20% giá cho 80% tính năng không dùng). Lộ trình Cilium "không mesh nhưng eBPF" đang phổ biến ở org muốn network policy mạnh + hiệu năng, không muốn sidecar.

### 2.4 Health check — hợp đồng sống của LB

LB chỉ tốt bằng thông tin nó có: health endpoint phải **kiểm đúng "sẵn sàng phục vụ"** (dependencies sống, DB ping, pool còn chỗ — không chỉ "process còn thở"); interval × unhealthy-threshold = thời gian LB loại node xấu (quá chậm = user thấy lỗi; quá nhanh = dao động); **drain**: preStop + readiness về false + chờ connection cạn rồi mới hạ (→9.1 lifecycle; 8.5 graceful). Đo "deploy có rơi request không": synthetic request mỗi 100 ms xuyên suốt deploy — con số lỗi trong cửa sổ là chỉ số chất lượng release (→9.7).

### 2.5 Định tuyến & khả năng quan sát ở gateway

Gateway là chỗ tốt để: canary theo header/weight (→8.8/9.7), rate limit (→11.3 — ở lớp sớm nhất có thể), authn trước (JWT verify — như edge 6.5), **timeout toàn trình** (mặc định an toàn + override per route — 8.5 ngân sách), và ghi access log chuẩn (một format cho mọi service — →11.5). Mọi thứ trên là "tính năng platform" — quyết định một lần, mọi service hưởng (lý do tồn tại của tầng này).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Gateway API | GA v1, triển khai rộng | V | 2026 |
| Istio ambient | GA (từ 1.24, 2024) | V | sidecar-less |
| Sidecar overhead | ~50–100 MB RAM/pod | I | |
| Cilium | kube-proxy replacement ổn định | V | eBPF (→2.7) |
| Health check interval | 5–10 s điển hình | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Mỗi tầng LB tồn tại để **mua một loại quyết định** (IP bền / route HTTP / policy pod-to-pod) — thêm tầng mà không quyết định mới là trả thuế trùng lặp (giống caching 6.5: mỗi tầng phải trả lời "khoá gì, hết hạn khi nào").
- **S2:** Tham số trụ: tỉ lệ request rơi trong deploy, thời gian phát hiện endpoint xấu, chi phí RAM sidecar nếu có, số route sở hữu app-team (đo "platform hoá" thật).
- **S3:** Gateway API đổi mô hình **sở hữu** (app team tự route) lấy một contract phải dạy — đáng khi số team > ~5 và platform không muốn là cổ chai duyệt tay.
- **S4:** mTLS nội bộ là **điều kiện** của zero-trust (→10.1) — mesh cung cấp rẻ hơn tự lo; nhưng policy phải đi kèm (mTLS mà "ai cũng gọi được ai" chỉ là mã hoá của sự lỏng lẻo).
- **S5:** eBPF (→2.7) đang làm "mesh" và "networking" hội tụ: cùng một lớp kernel lo cả policy + observability + hiệu năng — lựa chọn "mesh truyền thống vs eBPF-native" là quyết định kiến trúc 2 năm tới của platform team.
- **S6:** Khi "lúc gọi được lúc không" ở gateway: đọc thứ tự health-check → readiness → drain (§2.4) — đa số lỗi gateway là lỗi **thông tin** (LB không biết pod chưa sẵn/thôi sẵn), không phải lỗi tải.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| 502 vã lai | Health check sai/draining thiếu | synthetic xuyên deploy | §2.4 |
| Deploy rơi request | Không preStop/readiness gate | audit lifecycle (→9.1) | §2.4 |
| Policy "không ăn" | CNI không hỗ trợ / sai selector | kiểm tra CNI + policy audit | §2.3 |
| RAM cluster bốc hơi | Sidecar × nghìn pod | cân nhắc ambient/eBPF | §2.3 |
| Route mới không có tác dụng | Ingress annotation của controller khác | chuyển Gateway API | §2.2 |
| TLS hết hạn giữa đêm | Cert không renew tự động | cert-manager + alert | §2.1 |

---

## 6. Cách đo

```bash
# Synthetic xuyên suốt deploy (dòng lệnh, mỗi 100 ms):
while true; do curl -s -o /dev/null -w '%{http_code} %{time_total}\n' \
  https://app.example.com/api/health; sleep 0.1; done | tee during-deploy.log
#   — đếm mã != 200 trong cửa sổ: đây là "chỉ số rơi request khi release" của bạn

# Kiến trúc gọi nội bộ (ai gọi ai): Hubble observe / mesh dashboard —
#   bản đồ này là đầu vào của quyết định policy (zero-trust)
```

Nguyên tắc: **gateway đo được bằng synthetic request** — mọi cuộc tranh luận "deploy có sập không" kết thúc bằng một dòng lệnh chạy 5 phút, không bằng ý kiến.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay mesh:** network policy + gateway (đủ cho đa số đến một quy mô lớn — đừng mặc định mua mesh); **thay Gateway API:** giữ Ingress + controller một nhà (ổn nếu một team giữ toàn bộ route); **thay LB cloud:** keepalived/HAProxy tự lo (chỉ khi on-prem hoặc ràng buộc đặc biệt — đang tự nuôi một sản phẩm).

Năm thấu kính:
- **Kinh tế:** Sidecar × nghìn pod = một cụm máy "vô hình" chỉ làm proxy — tính ra tiền/năm trước khi chọn mô hình mesh; ambient/eBPF thường thắng cỡ số lớn ở org đông pod.
- **Vận hành:** Tầng gateway là nơi **mọi sự cố dồn về** (TLS, DNS, health) — runbook từng loại + drill chứng chỉ hết hạn (đã từng hạ lớn các dịch vụ công — lỗi "cert 1 năm hết hạn giữa đêm" kinh điển).
- **An ninh:** Gateway = điểm thu quả (auth, rate limit, WAF — →11.3); mesh = đường nối mã hoá; thiếu một trong hai thì tầng còn lại làm quá sức của nó.
- **Lịch sử:** Hardware LB (F5, 1990s) → HAProxy/nginx (2000s) → ELB (2009+) → Ingress (2015) → Service mesh (2017+) → Gateway API + ambient/eBPF (2023+): mỗi thế hệ kéo **chính sách** (ai được nói chuyện với ai) xuống gần workload hơn một tầng.
- **Người dùng:** Người dùng gặp gateway mỗi lần bấm app: "mở nhanh, không lỗi, không bị đăng xuất bất thường". Cả chương này là giữ cho trạm gác đầu tiên của hệ thống tỉnh táo.

---

## 8. Đọc tiếp & bài tập

- eBPF nền: **2.7** · K8s service/probe: **9.1** · Canary/progressive: **9.7** · Zero-trust: **10.1** · Rate limit/WAF: **11.3** · TLS/QUIC: **4.1**
- **Bài tập 1:** Chạy synthetic §6 trong lần deploy tới. Ghi số request rơi — nếu > 0: đường lifecycle (§2.4) có lỗ; sửa rồi đo lại (con số này nên về 0 mới gọi là "deploy không gián đoạn").
- **Bài tập 2:** Vẽ bản đồ "ai gọi ai" (Hubble/mesh hoặc survey config) — đánh dấu các cạnh **không ai giải thích được**; mỗi cạnh vô danh là ứng viên policy chặn trước khi bị lợi dụng.
- **Bài tập 3:** Liệt kê mọi chỗ terminate TLS trong hệ thống (cloud LB? gateway? service?). Mỗi chỗ: cert ai cấp, hết hạn khi nào, ai nhận alert? Ô trống = bom nổ chậm có ngày cụ thể.
