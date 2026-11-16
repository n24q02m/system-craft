# 10.8 — Tuân thủ Pháp lý (CRA/NIS2/DORA/GDPR/PDPD) & Bản quyền OSS

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Tuân thủ · Chọn
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số) · **Lưu ý pháp lý: tóm tắt kỹ thuật, không thay thế tư vấn luật**
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.13 (governance đã dựng) · 10.5 (SBOM, CRA đã gặp).

**Sợi chỉ đỏ:** *Giấy tờ cuối cùng — GDPR/PDPD buộc DM làm gì với dữ liệu khách?* — trả lời: giấy tờ cuối cùng — chương này vẽ bản đồ luật 2024–2027 (EU xương sống, VN theo sau), CRA là luật "kỹ thuật nhất" (SBOM, thời hạn vá — nối 10.5), khung vận hành dữ liệu cá nhân dùng được bất kể luật, NIS2/DORA cho quản trị, và bẫy bản quyền "miễn phí". Câu hỏi để lại cho chương sau: *Hệ thống chạy, có user, có kẻ thù — giờ để nó chạy bền: vận hành đo bằng số gì?*

**Thuật ngữ sẽ gặp:** *GDPR/PDPD* — EU và Nghị định 13 của VN: quyền chủ thể, căn cứ xử lý, phạt theo doanh thu; *CRA* — Cyber Resilience Act: phần mềm bán vào EU phải khai thành phần và vá đúng hạn: luật kỹ thuật nhất; *NIS2/DORA* — quản trị và thử nghiệm cho tổ chức quan trọng: báo cáo sự cố tính bằng giờ; *bản quyền OSS* — MIT, AGPL, BSL: "miễn phí" không đồng nghĩa "tuỳ ý dùng"; *khung vận hành dữ liệu* — phân loại, yêu cầu chủ thể, hợp đồng xử lý: dựng một lần cho mọi luật; *tuân thủ như kỹ thuật* — bằng chứng tự sinh từ pipeline, không screenshot lúc kiểm tra.

**Ví dụ mở đầu:** Khách EU đòi xuất toàn bộ dữ liệu trong 30 ngày, rồi xoá: dữ liệu nằm rải rác bốn mươi hệ không chủ thì hai mươi chín ngày dành để tìm. Chương này dựng khung để deadline thành việc thường ngày, không thành khủng hoảng.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Luật nào áp cho sản phẩm tôi (thị trường nào, vai gì) | Tôi "bán hàng có yếu tố số" vào EU — CRA chạm tôi ở đâu? |
| 2 | Nhãn nghĩa vụ theo vai: nhà sản xuất/nhà nhập khẩu/nhà vận hành | Với mỗi luật, tôi là "ai" — nghĩa vụ theo vai đó |
| 3 | Dữ liệu cá nhân: cơ sở pháp lý, danh mục, thời hạn, xuyên biên giới | Dữ liệu ai, vì sao, giữ bao lâu, gửi đi đâu? |
| 4 | Chính sách license OSS: dùng gì được, CONTRIBUTE thế nào | GPL/AGPL/SSPL trong SaaS của tôi — ai đã duyệt? |

---

## 2. Cơ chế

### 2.1 Bản đồ luật 2024–2027 (EU là xương sống, VN theo sau)

| Luật | Đối tượng | Mốc chính | Nghĩa vụ kỹ thuật tiêu biểu |
|---|---|---|---|
| **GDPR** | xử lý dữ liệu cá nhân (ai chạm EU) | hiệu lực 2018 | cơ sở pháp lý, quyền chủ thể, DPO, **72h** báo vi phạm, DPIA |
| **NIS2** | thực thể thiết yếu/quan trọng (năng lượng, y tế, số...) | chuyển hoá quốc gia ~10/2024 | quản trị rủi ro, **báo cáo sự cố 24h/72h**, danh sách, kiểm toán |
| **DORA** | tài chính EU | áp dụng 17/01/2025 | thử nghiệm phục hồi **TLPT**, quản lý rủi ro nhà cung cấp ICT, báo cáo sự cố lớn |
| **CRA** | sản phẩm có yếu tố số bán EU | hiệu lực 12/2024; nghĩa vụ chính **12/2027** (báo cáo lỗ hổng chủ động từ 2026) | SBOM, hỗ trợ bảo mật theo thời gian hỗ trợ, cập nhật an toàn, **không bán sản phẩm chưa an toàn** |
| **PDPD (VN)** | dữ liệu cá nhân (Nghị định 13/2023; Luật Bảo vệ dữ liệu cá nhân đang lộ trình) | hiệu lực 7/2023 | impact assessment (DPIA-style) nộp, **24h** thông báo một số trường hợp, đại diện bảo vệ dữ liệu, quy tắc xuyên biên giới |

Đọc đúng: đây là **lưới chồng nhau** theo vai trò — một SaaS y tế bán EU+VN có thể đồng thời dính GDPR + NIS2 + DORA (nếu chạm tài chính) + CRA (phần mềm như sản phẩm) + PDPD. Việc đầu tiên: **bảng vai-trị giá** (tôi là ai trong mỗi luật) — phần lớn tranh luận nội bộ tan biến khi vai được xác định.

### 2.2 CRA — luật "kỹ thuật nhất" (đọc kỹ nếu bán phần mềm)

Vì sao kỹ thuật quan tâm: CRA biến **thói quen an ninh của atlas** thành nghĩa vụ pháp lý: hỗ trợ bảo mật trong "thời gian hỗ trợ" công bố (không bỏ rơi sản phẩm — →6.6 EOL công bố), cập nhật an toàn trong thời hạn, **SBOM duy trì** (→10.5), quy trình báo cáo lỗ hổng đang bị khai thác (24h biết → báo cơ quan, 72h bản vá/thúc tiến — chi tiết đọc văn bản), không giao hàng có lỗ hổng "biết rồi còn bán". Miễn/thu hẹp: phần mềm nội bộ không bán, OSS phi thương mại. Hành động: nếu bán vào EU — dựng **tờ kê khai phù hợp (CE marking cho phần mềm)** + bảng thời gian hỗ trợ công khai; nếu chỉ dùng nội bộ — ghi ADR "không trong phạm vi + tại sao".

### 2.3 Dữ liệu cá nhân — khung vận hành (bất kể luật nào)

1. **Danh mục dữ liệu (ROPA-style):** loại dữ liệu × mục đích × cơ sở pháp lý × giữ bao lâu × ở đâu (region) × ai truy cập — bảng này phục GDPR/PDPD/CRA kiểm tra và **sự cố 10.7** ("dữ liệu gì bị ảnh hưởng — trả lời trong giờ");
2. **Tối thiểu hoá & giả danh** (→5.13/5.14: token hoá PII, RLS theo tenant, retention job thật sự chạy);
3. **Quyền chủ thể:** xuất (export), xoá (crypto-shred — →5.13), sửa — **API-level feature**, không phải dự án 6 tháng khi có yêu cầu đầu tiên;
4. **Xuyên biên giới:** dữ liệu ở region nào (→8.7 kiến trúc đặt vùng theo luật, không chỉ theo latency); VN có quy định chuyển dữ liệu ra nước ngoài theo PDPD — kiểm tra khi lưu trữ/backup/logs vắt region.

### 2.4 NIS2/DORA — khung quản trị & thử nghiệm

Cả hai cùng hình: **quản trị rủi ro có trách nhiệm ban lãnh đạo** (đào tạo, phê duyệt), **chuỗi nhà cung cấp** (danh sách + rủi ro tập trung — cloud nào chết thì tôi thế nào — →8.7), **báo cáo sự cố theo tầng** (cảnh báo sớm 24h → báo cáo đầy đủ 72h → kết luận 1 tháng — NIS2), **thử nghiệm phục hồi định kỳ** (DORA TLPT: penetration + scenario kiểu 8.7 game day). Điểm chung với atlas: mọi thứ luật đòi (danh mục, drill, báo cáo, drill khôi phục) **đã là kỹ thuật tốt** — luật chỉ ép lịch; làm trước luật thì phần "tuân thủ" là in tờ báo cáo.

### 2.5 Bản quyền OSS — bẫy của "miễn phí"

| Họ license | Ví dụ | SaaS dùng được | Bẫy |
|---|---|---|---|
| Permissive | MIT/BSD/Apache-2.0/ISC | ✓ tự do (giữ attribution + license notice) | Apache + NOTICE phải giữ đúng |
| Copyleft yếu | LGPL/MPL/EPL | ✓ điều kiện (link, file-level) | sửa library phải mở phần đó |
| Copyleft mạnh | GPL | phân phối thì mở mã **cả app link** | SaaS không "phân phối" → lách được (trừ AGPL) |
| **AGPL** | AGPL-3.0 | **nguy hiểm**: phục vụ qua mạng = nghĩa vụ mở mã** | firewall chính sách: không dùng trong sản phẩm, trừ duyệt đặc biệt |
| **SSPL/BSL/Elastic-style** | Mongo/Redis lịch sử, Cockroach | "source-available", hạn chế competitor | đọc điều khoản thương mại; đổi license giữa chừng là rủi ro thật (đã xảy ra với Redis→RSALV2/AGPL song song 2024 — Valkey fork sinh ra từ đó — →5.4) |

Chính sách tối thiểu viết ra: (1) allowlist họ license cho dep mới (CI kiểm — →10.5 SBOM có license!); (2) AGPL/SSPL cần duyệt bằng tên người; (3) đóng góp ngược (contribute) lên repo ngoài: kiểm NDA/IP của hợp đồng lao động; (4) công ty nội bộ mở mã? — luật riêng. SBOM chở luôn license — một công cụ hai việc.

### 2.6 Tuân thủ như kỹ thuật (không như giấy tờ)

Ba nguyên tắc biến compliance thành by-product: **mặc định đúng** (golden path — →9.6 — template đã đúng luật: retention, region, SBOM); **bằng chứng tự sinh** (log/drift/audit từ 10.x + 9.6 = hồ sơ kiểm tra không soạn tay); **một bảng vai-áp dụng** sống trong repo (ADR) — luật đổi (CRA các mốc 2026–2027) thì bảng đổi theo PR. Kiểm toán mà "chuẩn bị 3 tháng" = thiếu ba nguyên tắc; có ba nguyên tắc thì kiểm toán là export.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| GDPR báo vi phạm | 72h | V | Art. 33 |
| NIS2 | chuyển hoá ~10/2024; báo 24h/72h | V | Directive 2022/2555 |
| DORA | áp dụng 17/01/2025 | V | tài chính EU |
| CRA | hiệu lực 12/2024; nghĩa vụ chính 12/2027 | V | Regulation 2024/2847 |
| PDPD VN | NĐ 13/2023 hiệu lực 7/2023 | V | Luật BVDLCN đang lộ trình |
| OSS allowlist | CI kiểm license SBOM | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Pháp lý là **ràng buộc kiến trúc thật** (region của dữ liệu, retention, SBOM, drill, thời gian hỗ trợ) — quyết định sớm trong IaC/schema; retrofit pháp lý tốn như retrofit i18n (→7.5 đã học cùng bài).
- **S2:** Tham số trụ: % template có tuân thủ mặc định, thời gian xuất bằng chứng khi audit, số dep ngoài allowlist, % sản phẩm có bảng thời gian hỗ trợ công khai.
- **S3:** License = dependency metadata: kiểm tự động trong cùng pipeline CVE (→10.5) — rủi ro pháp lý và rủi ro an ninh cùng đường vào, cùng chi phí kiểm soát.
- **S4:** AGPL/SSPL là **rủi ro kiến trúc thương mại**: chọn DB năm nay quyết định khả năng bán công ty năm sau (due diligence đọc license trước mua) — quyết định có CFO trong phòng, không chỉ kỹ thuật.
- **S5:** AI mở lớp pháp lý mới (→12.x): dữ liệu huấn luyện (quyền tác giả? GDPR cho dữ liệu cá nhân trong corpus), model memorize dữ liệu, luật AI (EU AI Act lộ trình 2025–2027 theo rủi ro) — chương 12 phải đọc cùng chương này;
- **S6:** Khi "kiểm toán/đối tác hỏi giấy tờ": xuất từ hệ (log, SBOM, bảng vai, drill report) — nếu phải "soạn" thì đó là tín hiệu nợ kỹ thuật trá hình pháp lý; trả lời bằng PR vào repo.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| "Không biết luật nào áp" | Chưa lập bảng vai | workshop 2h với luật sư + bảng | §2.1 |
| Audit = 3 tháng dở chứng | Bằng chứng không tự sinh | log/drift/SBOM → export | §2.6 |
| Phải từ chối yêu cầu xoá dữ liệu | Không có tính năng xoá | crypto-shred + API (→5.13) | §2.3 |
| Dính AGPL trong SaaS | Cho phép dep tự do | allowlist + CI kiểm license | §2.5 |
| Backup/log vắt region trái luật | Kiến trúc chỉ theo latency | region policy + PDPD/GDPR | §2.3 |
| CRA mốc 2027 tới mà chưa ai lo | Nghĩa vụ sản phẩm bị bỏ quên | bảng thời gian hỗ trợ + SBOM | §2.2 |

---

## 6. Cách đo

```bash
# Tuân thủ đo được (mẫu checklist chạy CI/đêm):
#   - % artifact có SBOM kèm license (→10.5) — mục tiêu 100%
#   - số dependency ngoài allowlist (mục tiêu 0)
#   - retention job chạy thật? (đếm bản ghi > TTL trong DB — số ≠ 0 là đỏ)
#   - thời gian xuất "danh mục dữ liệu" khi hỏi — < 1 giờ là khỏe
```

Nguyên tắc: **tuân thủ là trạng thái của repo + pipeline, không phải tài liệu Word** — mọi thứ "soạn khi cần" sẽ trễ đúng lúc cần nhất.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự theo dõi luật:** thuê tư vấn/managed compliance (đắt nhưng đúng lúc thay đổi — hợp khi không có pháp lý nội bộ); **thay CI license check:** review tay từng PR dep (được lúc 5 người — vỡ ở 50); **thay bảng vai:** hỏi từng luật một khi sự cố (đừng — đó là cách trễ hạn).

Năm thấu kính:
- **Kinh tế:** Phạt GDPR đến 4% doanh thu toàn cầu; CRA phạt tới 15M€ hoặc 2,5% (nhóm); so với chi phí template đúng luật — bảo hiểm rẻ nhất trong các chương an ninh; lách luật đắt hơn tuân thủ ở mọi kịch bản có thật.
- **Vận hành:** Luật có nhịp riêng (CRA mốc 2026/2027, AI Act theo rủi ro lớp) — calendar riêng review nửa năm, chủ sự là **một người có tên** (không phải "cả team");
- **An ninh:** Ba luật (NIS2/DORA/CRA) đều xoay về **cùng hạt nhân kỹ thuật**: SBOM, drill, báo cáo sự cố, thời gian hỗ trợ — 10.5/10.7/9.7 làm tốt thì tuân thủ là paperwork; làm không thì paperwork cũng không cứu.
- **Lịch sử:** "Self-regulation" (1990s) → GDPR (2018, thiết chuẩn toàn cầu de-facto) → NIS2/DORA/CRA (2024–25, từ quyền riêng tư sang **an ninh+trách nhiệm sản phẩm**) → AI Act (2026+, rủi ro theo lớp): mỗi vòng mở rộng "phần mềm là thứ bị điều tiết như điện/nước/thuốc";
- **Người dùng:** Người dùng cuối không đọc luật — nhưng họ nhận được quyền thật (xin dữ liệu, đòi xoá, biết bị lộ trong 72h) nhờ những dòng chữ đó; chương này là nơi kỹ thuật gặp xã hội, và cũng là nơi atlas trả lời "vì sao làm cho đúng" bằng lý do ngoài kỹ thuật.

---

## 8. Đọc tiếp & bài tập

- SBOM/license CI: **10.5** · Báo cáo sự cố: **10.7, 11.4** · Retention/crypto-shred: **5.13** · Region/DR: **8.7** · AI & luật: **12.8**
- **Bài tập 1:** Lập bảng vai-áp-dụng (một trang): mỗi luật (GDPR/NIS2/DORA/CRA/PDPD) — tôi là vai gì, áp/không áp vì sao, mốc gần nhất. Có bảng này, 80% câu hỏi compliance nội bộ có câu trả lời trong 5 phút.
- **Bài tập 2:** Chạy `syft` lấy license từ SBOM image chính (→10.5): đếm dep ngoài allowlist (đặc biệt AGPL/SSPL). Mỗi cái ngoài — quyết định: loại, thay, hoặc duyệt bằng tên.
- **Bài tập 3:** Đo "thời gian xuất danh mục dữ liệu": hỏi chính mình "dữ liệu cá nhân gì, ở đâu, giữ bao lâu" — bấm giờ tới khi có bảng đầy đủ. > 1 ngày? Đó là rủi ro phạt và rủi ro sự cố (10.7 cần chính bảng đó) — dựng tuần này.
