# 13.6 — Playbook: Toàn cầu, Offline-First & Edge

> **Tầng:** Nghiệp vụ · **Quyển III** · **Trục đọc:** playbook theo miền · **Động từ liên quan:** Áp dụng · Chọn
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.7 (multi-region DR) · 6.3 (bậc thang offline).

**Sợi chỉ đỏ:** *Khách ở hai bên bán cầu — đa vùng, residency, offline tính ra sao?* — trả lời: khách hai bên bán cầu — "home region" là mẫu active-active thực chiến: dữ liệu về nhà vùng của nó; offline-first chọn bậc theo dòng máu sản phẩm; cái gì đáng đẩy lên edge; residency là ràng buộc pháp lý xuyên vùng; và vận hành toàn cầu là ba đồng hồ khác nhau. Câu hỏi để lại cho chương sau: *Bán cho doanh nghiệp (chuỗi lớn) — SaaS B2B phân tầng tenant thế nào?*

**Thuật ngữ sẽ gặp:** *home region* — mỗi user và dữ liệu có vùng nhà: ghi về nhà, đọc gần chỗ: active-active không đối xứng; *residency* — luật giữ dữ liệu trong biên giới: ràng buộc kiến trúc thật, không phải câu hỏi tuỳ chọn; *offline-first theo bậc* — shipper cần bậc cao, khách duyệt menu cần thấp: chọn theo dòng máu (nối 6.3); *edge* — personalization nhẹ và cắt latency: cái gì đáng lên (nối 6.5); *ba đồng hồ* — maintain window ba vùng, deploy chạy theo mặt trời: on-call không rét cả địa cầu; *xung đột đa vùng* — ba con đường của 8.7, giờ có địa lý thật.

**Ví dụ mở đầu:** DM mở châu Âu: dữ liệu khách Đức phải nằm trong EU vì residency, nhưng app vẫn phải nhanh ở Singapore. Home region: ghi ở EU, cache đọc đặt gần người; lịch bảo trì chạy theo mặt trời qua ba vùng. Chương này là playbook toàn cầu, mọi quyết định có đánh số.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Đa vùng theo người dùng (active-active per region) | Người dùng của tôi ở đâu (số thật — 11.5) và chấp nhận trễ chéo vùng cỡ nào? |
| 2 | Offline-first cho luồng nào (6.3 bậc thang) | Mạng yếu là thị trường chính hay rủi ro hiếm của tôi? |
| 3 | Edge compute cho phần nào (6.5) | Đường nào cần RTT ~ms — và cái gì bắt buộc về region dữ liệu? |
| 4 | Dữ liệu & luật theo vùng (10.8 + 8.7) | Data residency: lưu/XL xử lý ở đâu — ai đã ký cam kết đó? |

---

## 2. Cơ chế

### 2.1 Kiến trúc tham chiếu toàn cầu

```
[User VN/EU/US]
   ↓ DNS geo + anycast/CDN (6.5)
[Edge PoP: static + auth verify + biến đổi nhẹ (6.5)]
   ↓ route theo "home region" của user
[Region VN/EU/US: cell đầy đủ (8.7): app + DB + cache]
   ↕ replication chéo vùng: theo nghiệp vụ per-entity (8.7 §2.3)
[Control plane toàn cầu: định tuyến user→region + fleet (8.2 đồng thuận)]
```

### 2.2 "Home region" — mẫu active-active thực chiến

Mỗi user/tổ chức có **vùng nhà** (ghi lúc tạo; đổi khi chuyển vùng lâu dài): ghi vào vùng nhà (quorum tại đó — nhanh), đọc tươi từ vùng nhà; vùng khác chỉ **cache/serving readonly** của dữ liệu công khai. Xung đột chỉ xảy ra lúc "đang chuyển vùng giữa chừng" — hẹp hóa bài toán conflict (8.7 §2.3) thay vì mở full multi-master. Kèm: **route bám user** (session token mang region — client retry không rơi vùng khác), và URL/locale per region (7.5 i18n — ngôn ngữ + định dạng theo vùng).

### 2.3 Offline-first — chọn bậc theo dòng máu sản phẩm

Bậc thang 6.3 (cache → offline-đọc → outbox → local-first CRDT): sản phẩm cho **mạng yếu là thị trường** (VN đường dài, tàu, kho vận, hiện trường) → bậc 3–4 cho luồng lõi (soạn, quét, giỏ); SaaS văn phòng mạng ổn → bậc 1–2 đủ. Chi phí thật của bậc 4 (sync engine + conflict) — chỉ trả khi thị trường bắt (6.3 đã tính); đừng làm local-first vì "hay".

### 2.4 Edge — cái gì đáng lên trên

Đáng (6.5): auth/JWT verify + rate limit, personalised header/redirect, A/B, resize ảnh, **response AI ngắn** (gợi ý tĩnh/FAQ — semantic cache ở edge!). Không đáng: nghiệp vụ đọc/ghi DB region (vòng Trái Đất mất lợi ích), decisions cần dữ liệu miền khác. Quy tắc đo: **p95 của đường người dùng** — cái nào chỉ đạt được khi đặt gần (và không cần dữ liệu xa) thì lên edge.

### 2.5 Residency & tuân thủ xuyên vùng

EU dữ liệu ở EU (GDPR — 10.8), VN cần cân nhắc quy định chuyển dữ liệu (PDPD): kiến trúc **region-pinned theo tenant** (13.7 gắn tầng tenant: tenant EU có home region EU bắt buộc — config, không phải hy vọng); backup/log/telemetry **cũng** theo vùng (hay quên — backup chéo vùng trái luật là lỗi thật); nhân viên support truy cập xuyên vùng qua **proxy audit** (ai xem dữ liệu ai — 10.6/10.7).

### 2.6 Vận hành toàn cầu — ba đồng hồ khác nhau

- **Giờ thấp điểm khác nhau** (VN 2h sáng ≠ US 2h sáng): maintenance window per region — deploy cuộn theo mặt trời (9.7 progressive × vùng);
- **Sự cố vùng**: failover theo 8.7 (RTO/RPO/RHO đã ký) — nhưng **luôn kiểm tra luật trước khi chuyển dữ liệu khẩn cấp** (residency có ngoại lệ khẩn cấp? — hỏi pháp lý trước, không phải lúc cháy);
- **Ngôn ngữ sự cố**: status page đa ngôn ngữ (7.5) — thông báo 2h sáng phải đọc được cho người đọc tiếng Việt/tiếng Anh của chính vùng đó.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| RTT chéo vùng | 50–300 ms một chiều | I | →1.6 |
| Edge RTT | ~1–30 ms | I | 6.5 |
| Replication chéo vùng | async ~s (RPO theo cặp vùng) | I | 8.7 |
| Home region pin | theo tenant config | P | residency |
| Deploy cuộn | region theo region, không big-bang giờ toàn cầu | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Toàn cầu = **đặt đúng thứ đúng chỗ theo người dùng + luật** (latency → 1.6/6.5; luật → 10.8; chịu lỗi → 8.7) — playbook này chỉ là phép nhân của ba chương, không có kỹ thuật mới; vậy nó dạy **thứ tự nhân**;
- **S2:** Tham số trụ: p95 per region (so — không trộn), tỉ lệ user phải route chéo vùng (vàng cho capacity vùng), RPO thực đo (drill), chi phí egress chéo (11.5 — tiền thật).
- **S3:** Home-region pin đổi xung đột rộng cho route hẹp — đơn giản hoá một bậc so với multi-master thật; đáng mặc định cho 90% SaaS;
- **S4:** Residency là **ràng buộc kiến trúc cứng** (không phải chính sách giấy): region-pinned tenant + backup theo vùng + audit xuyên vùng — bỏ một thứ là cam kết pháp lý sập lúc sự cố;
- **S5:** AI toàn cầu = **route model theo region** (compliance + latency — 12.6 gateway đã có policy; inference tự chạy per-region khi dữ liệu không được đi) + semantic cache edge (câu FAQ trả lời ~ms mọi vùng);
- **S6:** Khi "khách ở xa complaining chậm": đối chiếu vùng user với vùng serving (trace) — thường là **route lệch** (VPN/DNS/cấu hình) chứ không phải "mạng xa không làm gì được"; sửa route trước khi mua thêm vùng.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| User EU thấy chậm | Serving từ VN (route lệch) | trace + home region check | §2.2 |
| Dữ liệu "văng" qua region khác | Backup/log không pin | audit backup path | §2.5 |
| Chuyển vùng giữa chừng mất ghi | Conflict path hở | 8.7 §2.3 từng entity | §2.2 |
| Edge đắt mà không nhanh hơn | Đặt nhầm thứ (cần DB) | rút về region | §2.4 |
| Deploy 2h sáng VN đánh thức US | Một window toàn cầu | cuộn theo mặt trời | §2.6 |
| Offline làm xong không sync | Bậc offline thiếu (6.3) | outbox + drill airplane | §2.3 |

---

## 6. Cách đo

```bash
# Per-region synthetic (chạy từ 3 châu, mỗi 5 phút):
#   curl -w '{ttfb:%{time_starttransfer}}' -o /dev/null -s https://app.example.com/api/health
#   → dashboard 3 đường — đường nào tách hẳn = vùng đó có bệnh riêng

# Drill residency: chọn 1 tenant EU — truy vệt (backup, log, telemetry,
#   support access) 24 h: mọi byte của tenant đó chạm region ngoài EU chưa?
#   — "không chạm" phải chứng minh được, không phải đoán
```

Nguyên tắc: **toàn cầu đo per-region và chứng minh per-tenant** — tổng toàn cầu che mất đúng thứ cần thấy.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay đa vùng:** một vùng + CDN (đủ cho đa số đến một quy mô thật — 11.5 tính trước khi "nghiêm túng toàn cầu"); **thay home-region pin:** multi-master đầy đủ (mạnh + phức tạp + conflict thật — chỉ khi sản phẩm cần ghi đồng thời đa vùng); **thay offline-first:** progressive web + retry lịch (bậc 1–2 của 6.3 — trung thực với nhu cầu).

Năm thấu kính:
- **Kinh tế:** Mỗi vùng là **bộ infra riêng + standby + egress chéo** (8.7/11.5) — mở vùng vì "sếp muốn có" không vì số người dùng vùng đó là tiền đốt có văn hoá;
- **Vận hành:** Fleet toàn cầu = N lần runbook (mỗi vùng một drill — 8.7); đừng tin "multi-region" tới khi từng vùng từng được tắt thử;
- **An ninh:** Residency + xuyên-vùng truy cập là mặt diện pháp lý-an ninh chung (10.6/10.8); audit xuyên vùng là yêu cầu tăng nhanh 2026 với EU;
- **Lịch sử:** CDN (1998) → edge compute (2017+) → data residency (2018+, GDPR sinh ra) → AI region routing (2025+): mỗi bước vẽ lại bản đồ "dữ liệu ở đâu" — và bản đồ chính trị ngày càng có ý nghĩa kỹ thuật (latency biến thành luật);
- **Người dùng:** Người dùng Tokyo và Houston cùng hỏi "app này nhanh với tôi không?" — hai câu trả lời khác nhau, và cả hai đúng; playbook này là kỹ thuật trả lời từng người một cách riêng.

---

## 8. Đọc tiếp & bài tập

- Đa vùng/DR: **8.7** · Edge/CDN: **6.5** · Offline: **6.3** · Residency: **10.8** · Multi-tenant: **13.7** · Global latency: **1.6**
- **Bài tập 1:** Đo % người dùng theo vùng (số thật — billing/analytics) và p95 per region hôm nay. Nếu 90% một vùng — đa vùng là kế hoạch, không phải hiện tại (ghi ADR "khi nào mở vùng thứ hai");
- **Bài tập 2:** Chạy drill residency (§6) cho một tenant nhạy: mọi byte 24 h ở đúng vùng? Kết quả (kể cả "chưa") là tài liệu pháp lý nội bộ đáng giá;
- **Bài tập 3:** Liệt kê mọi đường "user chờ RTT chéo vùng" (API xuyên vùng, redirect, S3 lấy file xa) — mỗi dòng một cách đưa về vùng nhà; top 3 là PR tuần này.

