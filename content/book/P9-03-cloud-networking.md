# 9.3 — Mạng Đám mây: VPC, NAT, PrivateLink, DNS

> **Tầng:** Nền tảng · **Quyển II** · **Trục đọc:** điều phối · **Động từ liên quan:** Thiết kế · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.1 (TCP/TLS nền tảng) · 6.7 (không tin gì mặc định).

**Sợi chỉ đỏ:** *Mạng trong cloud — VPC, private link, endpoint: an toàn và tiền đổi chỗ nào?* — trả lời: VPC là tòa nhà logic trên hạ tầng người khác — "an toàn" đúng bằng các rule bạn viết; NAT Gateway có cái bẫy SNAT cạn cổng (I-060); PrivateLink là đường riêng không ra phố công cộng; và DNS là lớp bị coi thường nhất (I-061) nhưng giết thì rất nhanh. Câu hỏi để lại cho chương sau: *Vào cụm qua cửa nào — LB, gateway, mesh làm gì mà app không cần biết?*

**Thuật ngữ sẽ gặp:** *VPC/subnet* — không gian IP riêng của bạn trên hạ tầng chia sẻ: ranh giới logic, không phải tường gạch; *Security Group* — firewall stateful gắn instance: mặc định từ chối, mở từng cổng, viết đè nhau là bẫy; *NAT Gateway* — ra internet không cần IP công cộng: bẫy SNAT khi nghìn kết nối song song; *PrivateLink/VPC endpoint* — đường riêng tới dịch vụ cloud: không ra internet, tính theo giờ và theo GB; *private DNS* — zone và resolver nội bộ: sự cố "sáng vẫn chạy chiều chết" thường nằm ở đây; *peering/TGW* — nối VPC: topology quyết định chi phí và độ trễ.

**Ví dụ mở đầu:** Service trong private subnet của DM sáng vẫn chạy, chiều dừng: không ai đổi code — resolver của VPC vừa lỗi phân giải tên. Mạng cloud mỗi lớp đều có bảng giá và bẫy đã có mã sự cố: chương này đi từng lớp, từ tòa nhà logic tới những con đường riêng.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Thiết kế CIDR VPC (và dư chỗ cho peering/region mới) | Hai VPC nối nhau mà trùng dải — tôi có làm lại từ đầu không? |
| 2 | Ra internet thế nào: NAT GW / public subnet / không ra | Đường nào cần internet thật — còn lại PrivateLink? |
| 3 | DNS: resolution nội bộ, split-horizon, ndots | Pod hỏi "db.internal" mất bao lâu — và hỏi mấy lần? |
| 4 | Vào/ra giữa VPC: peering / transit gateway / endpoint | Topology mạng theo sao, trục, hay mesh? |

---

## 2. Cơ chế

### 2.1 VPC — tòa nhà logic trên hạ tầng người khác

VPC = dải IP riêng + bảng route + security group (stateful) + NACL (stateless, ít dùng). Ba quyết định sống còn ngay ngày đầu:

1. **CIDR lớn và không trùng ai:** chọn /16 cho VPC chính, chia subnet /20–/24 theo AZ × vai trò; **dự phòng dải cho VPC thứ hai/ngoài vùng** (peering trùng dải = không nối được, phải làm lại — tốn cả quý); tránh dải công ty VPN đang dùng (10.x phổ biến — nên cân nhắc dải riêng biệt);
2. **Private subnet mặc định:** mọi thứ không bắt buộc public thì private; public subnet chỉ cho LB/NAT;
3. **Egress có ý thức:** mỗi đường ra internet là hoá đơn + rủi ro — hỏi từng service "ra làm gì" (update? API ngoài? telemetry?) rồi chốt bằng NAT chung hay PrivateLink riêng.

### 2.2 NAT Gateway & cái bẫy SNAT (I-060)

NAT GW cho private subnet ra internet: **mỗi connection = một cổng SNAT** — cổng hữu hạn (~64k mỗi địa chỉ đích). Ứng dụng mở hàng chục nghìn connection đồng thời tới **cùng một đích** (S3, API bên ngoài) → cạn cổng → connection lỗi vã lai (I-060: "đôi khi được đôi khi không" — loại sự cố khó nhất để debug). Ba cách xử lý: (1) **connection pool + keep-alive** (tái dùng — đúng mọi ngôn ngữ, →3.3); (2) **PrivateLink/VPC endpoint cho dịch vụ cloud** (không qua NAT — rẻ hơn và không cạn); (3) tăng số IP cho NAT (đắt — lựa chọn cuối). Kèm: **NAT GW tính theo GB xử lý** — log/backup chạy qua NAT có khi tốn hơn cả compute (bảng giá mỗi tháng, bất ngờ kinh điển).

### 2.3 PrivateLink / VPC endpoint — đường riêng không ra phố

Endpoint cho dịch vụ cloud (S3, DynamoDB, ECR...) và **service endpoint của người khác** (service của đối tác cung cấp qua interface): traffic đi trong mạng cloud, không NAT, không internet, không tiền GB (endpoint giờ có phí giờ nhỏ — vẫn rẻ hơn NAT cho lưu lượng lớn). Bảo mật: policy endpoint khoá "chỉ được tới bucket X" — kiểm soát egress theo **đích cụ thể** thay vì "mở hết internet".

### 2.4 DNS — lớp bị coi thường nhất (I-061)

- **ndots:5:** cấu hình resolv.conf của pod (`db.ns.svc.cluster.local` dạng search 5 nhãn): tên ngắn ("db") thử lần lượt từng search domain → **một resolve biến 4–6 truy vấn**; chục nghìn pod × mỗi giây = DNS server bị dập (I-061). Hai đòn: đặt tên **đầy đủ với dấu chấm cuối** (`db.prod.svc.cluster.local.`) hoặc cấu hình **NodeLocal DNSCache** (cache tại node — giảm truy vấn lên resolver hàng chục lần);
- **Split-horizon:** "api.company.com" trong VPC trả IP riêng, ngoài internet trả IP public/LB — chuẩn cho hybrid; sai một bên = "staging gọi production" kiểu kinh điển;
- **DNS là dependency "ma":** mọi thứ chết khi DNS chết nhưng ít ai giám sát DNS — theo dõi query latency/error rate như một dependency bình thường (→11.5).

### 2.5 Topology giữa VPC

Peering (1-1, rẻ, không transitive — A↔B, B↔C không cho A↔C) vs **Transit Gateway** (trục hub — mọi VPC nối một chỗ, trả theo GB qua trục) vs **VPC mesh cho multi-region** (phức tạp, cân nhắc endpoint riêng). Quy tắc: ≤3 VPC và tĩnh → peering; nhiều VPC/tươi mở hoặc cần transitive → TGW; luôn vẽ bản đồ trước khi nối (bản đồ mạng là tài liệu sống, không phải sơ đồ thuyết trình một lần).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Cổng SNAT / IP / đích | ~64k | V | I-060 |
| ndots:5 nhân truy vấn | ×4–6 mỗi tên ngắn | V | |
| NAT GW giá | theo GB + giờ | V | bảng giá cloud |
| PrivateLink | phí giờ nhỏ, không GB | V | |
| DNS TTL nội bộ | 5–30 s (svc) | I | |

---

## 4. Suy luận kiến trúc

- **S1:** Mạng cloud là **bảng định tuyến + chính sách**, không phải cáp — thiết kế = chọn topology trách nhiệm (ai nói chuyện với ai) và mặc định **từ chối** (private-first, egress có ý thức);
- **S2:** Tham số trụ: lỗi/cạn SNAT port, DNS query latency & error, GB qua NAT theo tháng, số endpoint policy cho phép "internet rộng" (càng ít càng tốt).
- **S3:** NAT đổi đơn giản cho linh hoạt; PrivateLink đổi một lớp cấu hình cho giá + an toàn + không nghẽn cổng — mọi đường egress lớn nên kết thúc ở endpoint;
- **S4:** VPC trùng dải là **lỗi không sửa được** chỉ bằng cấu hình — đây là chương duy nhất nhắc "lên kế hoạch CIDR như lên kế hoạch IP công ty năm 1995" (kỹ thuật cũ, hậu quả vĩnh viễn như cũ).
- **S5:** Service mesh (→9.4) đang kéo chính sách "nói chuyện với ai" **lên tầng platform (L7)**: tương lai gần — security group cho workload bất kể subnet — nhưng VPC/địa chỉ vẫn là nền của chi phí & băng thông (không thay thế).
- **S6:** Khi "kết nối lúc được lúc không" (I-060): đo cổng SNAT + tăng pool kết nối client; khi "tên miền không phân giải lúc cao điểm" (I-061): NodeLocal DNSCache + FQDN chấm cuối — hai loại sự cố này gần như không bao giờ là "mạng xấu".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Connection lỗi vã lai ra ngoài (I-060) | Cạn cổng SNAT | metric NAT SNAT port; connection pool | §2.2 |
| DNS chậm/timeout lúc cao điểm (I-061) | ndots × truy vấn dập resolver | NodeLocal + FQDN chấm cuối | §2.4 |
| Hóa đơn NAT tăng vọt | Log/backup qua NAT | endpoint cho S3; route table audit | §2.3 |
| VPC mới không nối được | Trùng dải CIDR | quy hoạch lại (đau) | §2.1 |
| "Staging gọi production" | Split-horizon sai | audit zone nội/ngoài | §2.4 |
| Peering A không tới C | Không transitive | TGW hoặc peering đầy đủ | §2.5 |

---

## 6. Cách đo

```bash
# Đếm truy vấn DNS mỗi request (từ trong pod):
dig db +noall +stats | grep -i 'query time'   # thời gian 1 lần resolve
nslookup db   # xem nó thử mấy tên (search path)

# Trên flow log VPC: lọc traffic ra internet từ private subnet —
#   mỗi dòng là ứng viên cho PrivateLink (giảm NAT)
```

Nguyên tắc: **"ra internet" là danh sách được duyệt, không phải mặc định** — in danh sách đó ra và đưa cho bảo mật duyệt mỗi quý (tài sản an ninh thật của chương này).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay NAT GW:** proxy egress có kiểm soát (squid/Envoy — thêm lớp vận hành nhưng audit được từng request ra); **thay TGW:** full mesh peering (rẻ hơn khi ít VPC, nổ độ phức tạp khi nhiều); **thay split-horizon:** hostname nội bộ hoàn toàn (`.internal`) — đơn giản, bỏ lợi thế "một tên cho mọi môi trường".

Năm thấu kính:
- **Kinh tế:** NAT là "thuế ra phố" tính theo GB — ba khoản lớn thường gặp: backup, image pull, log; ba khoản đều có đường miễn thuế (endpoint) — một buổi audit đổi lại hóa đơn giảm hàng chục %.
- **Vận hành:** Sự cố mạng cloud khó debug vì "không có con rối để căng" — flow log + metric SNAT/DNS phải bật **trước** khi cần (→11.1: đèn đường không dựng lúc cháy).
- **An ninh:** Egress kín = phát hiện dữ liệu rò (data exfiltration qua "đường không ai biết là đang mở"); mỗi endpoint policy là một câu trả lời cho câu hỏi "dữ liệu tôi được phép đi đâu" (→6.7/11.3 cùng chủ đề ở tầng khác).
- **Lịch sử:** Địa chỉ IP riêng + NAT (RFC 1918, thập niên 90 cho doanh nghiệp) → VPC (2010s, "địa chỉ riêng theo giờ") → zero-trust/mesh (hiện tại): mỗi lớp thêm trừu tượng, nhưng **quy hoạch địa chỉ sloppy vẫn trừng phạt y hệt 30 năm trước**.
- **Người dùng:** Người dùng không thấy VPC — họ thấy "app không gọi được API đối tác lúc 9h sáng" (I-060/I-061). Chương này là tầng vô hình giữ những giờ cao điểm đó êm.

---

## 8. Đọc tiếp & bài tập

- LB/mesh: **9.4** · K8s networking (svc/kube-dns): **9.1** · DNS nền: **1.6** · Bảo mật egress: **11.3, 11.6** · Bảng sự cố mạng LAN: **1.6**
- **Bài tập 1:** Vẽ bản đồ VPC (subnet × AZ × route) — nếu vẽ không nổi trong 30 phút, bản đồ chưa tồn tại; đó là rủi ro vận hành định lượng được.
- **Bài tập 2:** Xem flow log tuần này: liệt kê 10 đích internet thường xuyên nhất — từng đích có endpoint thay thế không? Chuyển 3 đích lớn nhất qua endpoint và so hóa đơn tháng sau.
- **Bài tập 3:** Đo I-061 ở cluster bạn: từ pod, resolve 10 tên nội bộ và đếm tổng truy vấn (`dig +stats`). Nhân với QPS DNS ước tính — nếu con số làm bạn giật mình, bật NodeLocal DNSCache tuần này.

