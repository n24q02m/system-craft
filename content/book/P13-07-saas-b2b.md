# 13.7 — Playbook: B2B Multi-Tenant SaaS

> **Tầng:** Nghiệp vụ · **Quyển III** · **Trục đọc:** playbook theo miền · **Động từ liên quan:** Áp dụng · Thiết kế
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.14 (multi-tenancy) · 11.7 (bán cho doanh nghiệp).

**Sợi chỉ đỏ:** *Bán cho doanh nghiệp (chuỗi lớn) — SaaS B2B phân tầng tenant thế nào?* — trả lời: bán cho chuỗi lớn — ba mức isolation (5.14 mở rộng thành playbook), RLS cộng phòng thủ ở mọi tầng, noisy neighbor giới hạn ở bốn tầng, metering và billing tự sinh số hóa đơn, tenant lifecycle trọn vòng đời — kết bằng checklist enterprise-ready để bán được cho khách lớn. Câu hỏi để lại cho chương sau: *Mọi tầng phía trên đều đứng trên silicon — transistor, '3nm', EUV nghĩa là gì?*

**Thuật ngữ sẽ gặp:** *ba mức isolation* — shared, schema-per-tenant, database-per-tenant: playbook có bảng đổi (nối 5.14); *RLS mọi tầng* — policy DB là lớp cuối, không phải duy nhất: app, API, cache cùng chặn; *noisy neighbor bốn tầng* — DB, app, mạng, chi phí: giới hạn từng tầng một; *metering* — đo tiêu thụ theo tenant tự động: hóa đơn sinh từ số đo, không từ bảng tính; *tenant lifecycle* — onboard, nâng plan, xuất dữ liệu, offboard: đường ra phải có từ ngày đầu (nối 5.13); *enterprise-ready* — SSO, audit log, tuân thủ: checklist cuối chương.

**Ví dụ mở đầu:** Chuỗi 500 cửa hàng hỏi mua DM: "có SSO không, audit log giữ bao lâu, dữ liệu chúng tôi xoá thế nào?" — ba câu ấy rơi thẳng vào checklist cuối chương. Metering đúng nghĩa: hóa đơn tự sinh từ số đo, không ai ngồi tính cuối tháng. Đây là playbook cuối của P13 — và của cả atlas kiến trúc.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Isolation: Pool → Bridge → Silo theo tier (D-136) | Khách enterprise trả nhiều tiền đòi "riêng" — tôi có cung cấp được đường lên silo không? |
| 2 | Noisy neighbor & quota per tenant | Một tenant 100 GB query làm chậm 200 tenant kia — chặn ở đâu? |
| 3 | Metering & billing: đo gì, xuất hoá đơn thế nào | Tôi tính phí theo gì (seat/usage/AI token) — số đó sinh từ đâu? |
| 4 | Tenant lifecycle: onboarding/migration/offboarding | Tenant mới lên trong bao lâu; tenant đi — dữ liệu xoá thật không (10.8)? |

---

## 2. Cơ chế

### 2.1 Ba mức isolation (5.14 mở rộng thành playbook)

| Mức | Dữ liệu | Chi phí | Ai xứng |
|---|---|---|---|
| **Pool** (shared schema + `tenant_id`) | chung | rẻ nhất | đa số SMB |
| **Bridge** (schema riêng trong DB chung / cluster riêng theo nhóm) | nửa | giữa | tier trung; compliance nhẹ |
| **Silo** (DB/cluster/deployment riêng) | riêng | đắt (8.6 từng "service" giờ là "tenant") | enterprise + luật (y tế/tài chính/residency 13.6) |
Chiến lược **escrow path**: thiết kế pool chuẩn hoá để **một tenant leo lên silo không viết lại** (mã không biết/hoặc biết rất ít tenant ở đâu — mọi truy cập qua tầng dữ liệu chen `tenant_id`/router). Nâng cấp tenant = **copy + CDC theo dõi + cutover** (8.8 expand-contract của tenant!) — drill được, không phải "dự án một quý mỗi lần".

### 2.2 RLS + defense ở mọi tầng

DB: Row-Level Security theo `tenant_id` (5.14 — query quên WHERE vẫn an toàn); app: middleware chèn tenant context vào mọi request (không tin client gửi `tenant_id` — **lấy từ token** — 10.3); cache: khoá theo tenant (6.5/12.3 — lỗi chéo qua cache là thật); log/telemetry: gắn tenant để phân tích + **đảm bảo không leak ngang trong log** (11.2). BOLA-test hai-tenant tự động (10.3 §6) trong CI — ở SaaS đây là **kiểm tra sống còn**, không phải nice-to-have.

### 2.3 Noisy neighbor — giới hạn ở bốn tầng

1. **App:** rate limit + concurrency limit per tenant (8.5/11.3 — pool riêng theo tier);
2. **DB:** quota/priority (workload management — 5.8 CH có user profile/quota; PG có role + statement timeout); query đắt → giết + báo;
3. **Queue/Kafka:** quota partition/throughput per tenant (13.3 — tenant spam không dồn chung dòng);
4. **Compute:** K8s namespace + ResourceQuota per tenant lớn (9.1 — silo mềm).
Dashboard "top tenant theo tài nguyên" (11.5 showback nội bộ) — tenant nào liên tục đầu bảng là **cuộc họp bán hàng** (nâng tier) chứ không chỉ vấn đề kỹ thuật.

### 2.4 Metering & billing — số hóa đơn phải sinh tự động

Mọi thứ tính phí (seat, request, GB, **token AI — 12.6**, PHIÊN) đi qua **một pipeline metering**: event usage → Kafka (13.3) → aggregate (5.12) → bảng usage → invoicing. Bất biến: **số gửi khách đối soát được với nguồn** (13.1 tư duy — churn vì "hóa đơn lạ" là churn dễ tránh nhất); usage data latency = SLA billing (không "cuối tháng mới biết"); grace/overage policy rõ (vượt quota: chặn hay tính thêm — quyết định sản phẩm 8.5/12.6).

### 2.5 Tenant lifecycle

- **Onboarding:** self-serve (thẻ + tenant tạo tự động — IDP 9.6 golden path) hoặc assisted (enterprise: contract → provision qua IaC 9.6 — giờ không tuần);
- **Migration** (tier lên/xuống, region đổi — 13.6): dual-run + cutover theo 8.8; tenant offboarding: **xoá thật** (crypto-shred 5.13 — GDPR/PDPD quyền của khách; "xoá" mà backup vẫn giữ phải có policy + nói thật trong hợp đồng);
- **Config per tenant** (feature flag theo tenant — 8.8): mọi tính năng mới bật theo cohort tenant (canary 9.7) — SaaS release = lưới tenant, không công tắc toàn cục.

### 2.6 Enterprise-ready checklist (bán được cho khách lớn)

SSO (SAML/OIDC) + SCIM (10.3) · audit log export (SIEM của khách — 10.7) · RBAC/ReBAC trong tenant (10.3) · residency (13.6) · SLA + status page (11.1/11.4) · báo cáo SOC2/ISO (10.8 — kiểm toán bằng export) · DPA ký · support tier. Mỗi dòng là **cổng doanh thu** — thiếu dòng nào, thương hiệu khách lớn rơi đúng dòng đó (11.7 bảng dịch thuật: bán hàng cần biết câu nào).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| RLS | mọi query; tenant từ token | P | |
| Escrow path | pool→silo không viết lại | P | |
| Metering latency | ≤ giờ-ngày | P | |
| Offboard xoá | crypto-shred + policy backup | P | |
| Feature flag per tenant | mặc định | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Multi-tenant là **kiến trúc kinh doanh hoá** (tier = kiến trúc; isolation = giá bán; metering = doanh thu) — P13 khép lại bằng chương "sự kiện" này vì nó dùng gần như mọi chương trước;
- **S2:** Tham số trụ: BOLA-test pass rate (100%), sự chênh tài nguyên top-tenant/c trung vị, độ trễ metering, thời gian onboarding enterprise (giờ? ngày?), số tenant có escrow path đã drill.
- **S3:** Escrow path đổi kỷ luật tầng dữ liệu (tenant-aware mọi nơi) lấy khả năng thương mại (bán silo không viết lại) — **đầu tư sớm rẻ hơn mong muốn** và muộn đắt hơn tưởng tượng;
- **S4:** Metering là **pipeline dữ liệu có SLO** (13.3/13.4 áp xuống tiền) — mọi tranh chấp hóa đơn là bug của pipeline này, xử như bug dữ liệu;
- **S5:** AI per-tenant: quota token + model routing theo tier (12.6) + **dữ liệu tenant trong RAG/adapter tách tuyệt đối** (12.3 ACL; 12.7 LoRA per-tenant chỉ khi khách trả — costs thật);
- **S6:** Khi "một khách làm chậm cả hệ": xác định tầng nút cổ chai (2.3 bốn tầng) — giới hạn đúng tầng đó, rồi **cuộc họp bán hàng**; không bao giờ chỉ "im lặng chịu" (mất 200 khách) hay "đuổi thẳng" (mất 1 khách lớn) — playbook tồn tại cho lựa chọn thứ ba.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Thấy dữ liệu tenant khác | BOLA/RLS hở (5.14/10.3) | test hai-tenant CI | §2.2 |
| Một tenant làm chậm chung | Không quota tầng nào | 4 tầng §2.3 | §2.3 |
| Hóa đơn tranh cãi | Metering pipeline yếu | đối soát nguồn (13.1) | §2.4 |
| Khách enterprise không chốt deal | Thiếu checklist §2.6 | gap list → roadmap | §2.6 |
| Nâng tier = dự án quý | Không escrow path | CDC + cutover (8.8) | §2.1 |
| Offboard vẫn còn dữ liệu | Backup không policy | shred + policy nói thật | §2.5 |

---

## 6. Cách đo

```bash
# BOLA test tự động (CI, 5 phút): hai tenant thử đọc/sửa của nhau
#   qua 10 endpoint giàu dữ liệu — 200 nào là đỏ

# Showback per tenant: tài nguyên (DB ms, queue GB, token AI) theo tenant/tuần
#   — top 10 đầu bảng: vừa là alert noisy-neighbor vừa là lead bán hàng

# Onboarding clock: từ "khách ký" → "tenant sống" — đo từng bước (IaC? tay? ai chờ?)
```

Nguyên tắc: **mỗi tenant có thể trả lời "tôi dùng bao nhiêu, ai thấy dữ liệu tôi, tôi ở đâu"** — bằng số từ hệ thống, không bằng lời hứa.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay pool-first:** silo-first (mỗi tenant một stack — đơn giản, đắt, không scale SMB — hợp khi 10 khách enterprise trả đủ); **thay RLS:** WHERE thủ công + review (vỡ ở đúng lần quên — SaaS lớn nào cũng có vết sẹo này công khai); **thay metering tự dựng:** billing platform + usage API (11.7 mua — vẫn phải tự sinh event chuẩn).

Năm thấu kính:
- **Kinh tế:** Isolation là **bậc thang giá** — cùng phần mềm, ba mức chi phí/ba mức giá: biên SaaS sống ở sự thành thạo leo thang này; metering chuẩn là tiền về thẳng (tranh chấp ít, upsell có số);
- **Vận hành:** "Fleet tenant" như fleet IoT (6.6): inventory, version (feature flag per tenant — 8.8 TTL!), health per tenant — thiếu ba thứ là hỗ trợ khách bằng email cá nhân;
- **An ninh:** Lỗi chéo tenant là **sự cố báo chí của SaaS** (mọi trường hợp lớn đều công khai) — BOLA-test CI + RLS là hai lớp rẻ nhất để không lên báo;
- **Lịch sử:** Từ "cài phần mềm tại chỗ từng khách" (1990s — silo tuyệt đối) → SaaS pool (2000s) → hybrid tier (hiện tại): vòng lặp silo↔pool lặp lại 30 năm ở tầng khách hàng như 7.1 lặp ở tầng render — lịch sử không lặp y hệt, nhưng gieo;
- **Người dùng:** Khách B2B mua hai thứ: **chức năng** và **sự yên tâm** (dữ liệu tôi ở đâu, ai thấy, có nói thật không). Playbook cuối của Quyển III khép lại ở đó — mọi chương trước đó là cách nói "chúng tôi xứng đáng được tin" bằng kiến trúc.

---

## 8. Đọc tiếp & bài tập

- Isolation dữ liệu: **5.14** · AuthN/Z: **10.3** · Metering stream: **13.3** · Billing đối soát: **13.1** · Escrow/8.8: **8.8** · Residency: **13.6** · AI per-tenant: **12.6**
- **Bài tập 1:** Chạy BOLA test hai-tenant trên 10 endpoint chính (CI). Mỗi lỗ là A01:2025 nguyên mẫu — ở SaaS là sự cố báo chí chờ ngày; sửa hết trước mọi tính năng mới;
- **Bài tập 2:** Vẽ escrow path: từ pool hiện tại lên silo cho một tenant — các bước (copy/CDC/cutover) và chỗ nào viết lại mã? Chỗ viết lại là nợ kiến trúc hôm nay của bạn;
- **Bài tập 3:** Showback per tenant tuần này (DB ms + queue GB + token AI): gửi cho team bán hàng kèm "top 3 dùng nhiều nhất". Cuộc họp tier/upsell tuần sau sẽ có dữ liệu thay vì cảm giác — và tech finally nói cùng ngôn ngữ doanh thu (11.7).
