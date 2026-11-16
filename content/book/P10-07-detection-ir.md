# 10.7 — Phát hiện & Phản ứng Sự cố An ninh

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Phát hiện · Phản ứng
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.13 (log và retention — nền) · 8.7 (drill, không phải tài liệu).

**Sợi chỉ đỏ:** *Nếu đã bị xâm nhập — phát hiện từ đâu và xử lý ra sao?* — trả lời: nếu đã bị xâm nhập — phát hiện từ đâu: log đáng tin từ nguồn đáng tin là nền; detection engineering viết rule như code; 60 phút đầu quyết định kết quả; "chứa đứng" là bài toán cắt nhánh (cắt gì, giữ gì); và tabletop với purple team là cách tập trước khi có ngày thật. Câu hỏi để lại cho chương sau: *Giấy tờ cuối cùng — GDPR/PDPD buộc DM làm gì với dữ liệu khách?*

**Thuật ngữ sẽ gặp:** *log đáng tin* — thời gian đồng bộ (nối 1.9) và nguồn kẻ tấn công không đụng được: nền của mọi phát hiện; *detection as code* — rule nằm trong git, có test, có review: không phải đoạn regex chui dưới gầm SIEM; *60 phút đầu* — cô lập, báo cáo, gọi đúng người: kịch bản viết sẵn; *chứa đứng* — khoá tài khoản, tách mạng, đóng endpoint: mỗi nhánh cắt đều có giá, chọn theo rủi ro; *tabletop và purple team* — đóng vai sự cố định kỳ; đỏ tấn công, xanh phòng thủ chung một phòng: luyện thay đối đầu (nối 8.7).

**Ví dụ mở đầu:** Tấn công thật thường bắt đầu bằng một email và im lặng nhiều tuần — không cờ đỏ nào tự gắn lên. Cuối tuần ấy: phát hiện từ đâu, ai gọi ai, cắt nhánh nào trước. Chưa tập sẽ tìm câu trả lời giữa cơn hoảng. Chương này viết kịch bản hôm nay.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Detection engineering: rule nào, log nào, ngưỡng nào | Tôi phát hiện kẻ đã vào bằng tín hiệu nào — sau bao lâu (MTTD)? |
| 2 | Phản ứng: ai làm gì trong 60 phút đầu (playbook) | 2h sáng bị ransom — số điện thoại đầu tiên bấm là của ai? |
| 3 | Chứa đứng hay xoá sạch (contain vs eradication) | Kẻ đang ở trong hệ — tôi cắt nhánh nào trước? |
| 4 | Báo cáo/luật: ai phải biết trong bao lâu (72h?) | Nghĩa vụ thông báo của tôi theo GDPR/CRA/PDPD là gì? (→10.8) |

---

## 2. Cơ chế

### 2.1 Nền của phát hiện: log đáng tin từ nguồn đáng tin

Không log thì không detection (OWASP A09:2025 — log mà không alert = camera không băng). Bộ tín hiệu tối thiểu cần có (mỗi nguồn → một loại kẻ):
- **Authn:** đăng nhập thất bại/dồn, đăng nhập từ vị trí lạ, passkey bypass bất thường (→10.3);
- **AuthZ:** 403 đột biến, truy cập object theo mô hình lạ (BOLA probing — →10.4);
- **Workload/secret:** đọc secret bất thường (→10.6 audit vault), pod/service account hành xử khác baseline;
- **Network/egress:** lưu lượng ra ngoài bất thường (data exfil — kết nối dài tới IP hiếm, DNS tunnel), dò SSRF (→10.4);
- **Supply chain:** artifact không chữ ký chạy (→10.5), dependency mới xuất hiện trong SBOM ngoài kênh;
- **Tính toàn vẹn:** file/config đổi ngoài IaC (drift — →9.6), log bị xoá/im.

### 2.2 Detection engineering — rule như code

Rule có owner, có test (dữ liệu giả lập tấn công → phải bắn; dữ liệu bình thường → im), có mô tả "tấn công nào nó phát hiện", và **được đo**: precision (báo thật / tổng báo) và coverage (kịch bản MITRE ATT&CK phủ bao nhiêu). Vòng đời như code: thêm — test — chạy — đo — tinh chỉnh — nghỉ hưu (rule ố không còn đúng hành vi hệ). Alert fatigue là **định lượng được**: > 10 alert/ngày mà không có hành động = mọi alert sắp bị ignore (con người không phải đường ống không giới hạn).

### 2.3 Phản ứng — 60 phút đầu quyết định

Khung chơi (chuẩn ngành — NIST IR / SANS): **Chuẩn bị** (playbook + quyền + liên hệ) → **Phát hiện & phân tích** (đây là thật hay nhiễu? phạm vi?) → **Chứa** (cắt: disable account, isolate pod/segment — →8.7 cell chokes lây lan), **Loại bỏ** (đuổi: revoke token/credential — →10.3/10.6, patch lỗ) → **Phục hồi** (restore — →5.13/8.7, theo thứ tự nghiệp vụ) → **Học** (postmortem — →11.4, nhưng riêng tư hơn: security postmortem có phân loại thông tin nhạy). Ba quyết định nóng phải luyện trước: **ai có quyền tắt service cả (kill-switch)**, **restore từ khi nào** (backup sạch trước thời điểm xâm nhập — biết thời điểm xâm nhập mới chọn được), **có gọi bên thứ ba nào** (CSIRT thuê ngoài, cloud support, luật sư).

### 2.4 Chứa đứng — toán của "cắt nhánh"

Giả định bị xâm nhập (→10.1 assume breach): chứa = **thu hẹp đồ thị di chuyển** của kẻ: isolate node/segment (chết cell thay vì chết hệ), revoke credential của vùng nghi (không reboot toàn bộ — reboot xóa chứng cứ volatile!), giữ log nguyên vẹn (snapshot memory + disk trước mọi thao tác phá). Câu hỏi 3 bước của 10.1 giờ thành sách chạy: kẻ đứng ở pod A → danh sách credential A có (→10.6 sổ hộ khẩu) → revoke từng cái → cắt đường tới DB (RLS/quota vẫn chặn truy vấn). Có sổ = cắt nhanh; không sổ = đoán dưới áp lực.

### 2.5 Tabletop & purple team

**Tabletop:** 90 phút, kịch bản giấy ("ransomware mã hoá S3 bucket lúc 2h sáng Chủ nhật"), mọi vai trò (IC — →11.4, kỹ thuật, pháp lý, truyền thông) đi từng bước; ghi chỗ kẹt ("không ai biết số luật", "backup chưa thử restore"). **Purple team:** đỏ tấn công thật (có kiểm soát), xanh phải phát hiện — đo MTTD thật và phủ coverage ATT&CK; mỗi lần chạy là một lần cập nhật rulebook. Tần suất: tabletop quý, purple nửa năm — ít hơn là giấy tờ trang trí.

### 2.6 Báo cáo pháp định (đặt cạnh chương 10.8)

GDPR: thông báo cơ quan bảo vệ **72 giờ** từ khi biết vi phạm dữ liệu (nếu rủi ro cao); PDPD VN (Nghị định 13/2023): thông báo trong **24 giờ** cho một số trường hợp xử lý dữ liệu nhạy cảm — đọc đúng văn bản áp cho mình (→10.8 bảng). Hệ quả kỹ thuật: **phải biết "dữ liệu gì, bao nhiêu người, mức nhạy"** để ước tính trong vài giờ — tức là danh mục dữ liệu (→5.13/5.14) phải có **trước** sự cố, không dựng lúc cháy.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| GDPR 72h | thông báo cơ quan | V | Art. 33 |
| PDPD (NĐ 13/2023) | 24h một số trường hợp | V | VN |
| MTTD/MTR mục tiêu | giờ / giờ–ngày | P | theo adversary giả định (→10.1) |
| Alert ngưỡng mệt | ~10/ngày không action | P | cảnh báo tổ chức |
| MITRE ATT&CK | khung phủ tactics/techniques | V | |

---

## 4. Suy luận kiến trúc

- **S1:** An ninh không phát hiện = không có (assume breach — mọi phòng thủ trước đó chỉ **trì hoãn**); detection là nửa sau của hệ thống an ninh thật.
- **S2:** Tham số trụ: MTTD/MTR (từ purple team), precision của rule, % nguồn log tối thiểu có mặt, số kịch bản ATT&CK phủ, thời gian có danh sách dữ liệu bị ảnh hưởng.
- **S3:** Log an ninh tách khỏi log vận hành (retention khác — năm vs tuần; quyền truy cập khác — SOC vs dev; tính toàn vẹn — append-only/WORM) — cùng collector (→11.2) khác đích.
- **S4:** Mọi chương 10.x sản xuất tín hiệu cho chương này (authn fail, secret read, artifact sign fail, drift...) — thiết kế phát hiện ngay từ khi chọn công cụ, đừng "gắn detection sau";
- **S5:** AI hai mặt cho detection: anomaly detection tự động mạnh hơn rule tay (baseline học được), nhưng cũng tạo cảnh báo giả mới (hệ sinh tín hiệu của AI agent chạy việc lạ là bình thường — cần baseline riêng per actor — →12.7);
- **S6:** Khi "có dấu hiệu bị vào": **đừng vội tắt máy** — thứ tự: chụp chứng cứ (snapshot), đánh phạm vi (log), cắt đường lan (revoke/isolate), rồi mới tính xoá sạch; tắt vội = mất cả chứng cứ lẫn kiến thức thời điểm xâm nhập (mà restore cần nó).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Phát hiện sự cố từ... khách hàng | Không detection coverage | đi ngược §2.1 từng nguồn | §2.1 |
| Alert bắn 100 cái/ngày, ai cũng ignore | Fatigue + rule ồn | precision đo + rule nghỉ hưu | §2.2 |
| Kẹt "backup nào sạch?" | Không biết thời điểm xâm nhập | log toàn vẹn + intel | §2.4 |
| 2h sáng không biết ai quyết gì | Không playbook/vai trò | tabletop + IC (→11.4) | §2.3 |
| Báo cáo 72h trễ | Không có danh mục dữ liệu | →5.13/10.8 trước cháy | §2.6 |
| Sự tái diễn cùng một cách | Postmortem không đóng loop | action item theo dõi (→11.4) | §2.3 |

---

## 6. Cách đo

```bash
# Đo MTTD thật (purple-lite, nội bộ, có kiểm soát):
#   1. Sinh sự kiện "tấn công giả" (đăng nhập fail ×50 từ IP test, đọc secret ngoài giờ)
#   2. Bấm giờ → alert xuất hiện → người đầu tiên nhìn thấy → hành động
#   Ba mốc = MTTD (kỹ thuật) + MTTA (nhìn) + MTTR (hành động)
#   — mỗi con số một loại bệnh: chậm kỹ thuật sửa rule, chậm người sửa on-call

# Coverage: checklist nguồn §2.1 — tích từng nguồn có log+alert; % là số nói thật
```

Nguyên tắc: **an ninh đo bằng thời gian giữa các mốc** (vào → phát hiện → chứa → phục hồi) — mọi thứ khác là đầu vào cho bốn con số này.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay SOC tự dựng:** dịch vụ SOC managed (24/7 theo dõi — hợp SMB; đọc kỹ SLA MTTD); **thay SIEM đắt:** stack mở (Wazuh-style) hoặc log platform có rule engine (→11.2 — cùng dữ liệu, thêm rule) — đừng để "không đủ tiền SIEM" thành "không detection".

Năm thấu kính:
- **Kinh tế:** Chi phí phát hiện sớm (giờ của SOC) vs chi phí ransom/exfil (hợp đồng pháp lý + uy tín) — bảng giá của các vụ lớn công khai đủ để lập luận; detection là bảo hiểm bắt buộc của thời đại dữ liệu.
- **Vận hành:** Playbook là tài sản sống: mỗi tabletop tạo 3–5 chỉnh sửa; không chạy quý nào là playbook rữa theo tốc độ hệ đổi (mỗi lần 9.6 thêm loại node mới — playbook chứa kẻ mới cần thêm nhánh).
- **An ninh:** Kẻ tấn công cũng đọc cùng khung (ATT&CK) — trò chơi là phủ kỹ thuật **hay gặp và rẻ nhất cho kẻ**; 100% coverage là ảo tưởng, ưu tiên theo giá trị tài sản (→10.1).
- **Lịch sử:** IDS chữ ký (1990s) → SIEM correlation (2000s) → UEBA/threat intel (2010s) → purple team tự động hoá + AI anomaly (2020s): mỗi thế hệ phát hiện nhanh hơn — và kẻ tấn công cũng nhanh tương ứng; MTTD là cuộc đua không có vạch đích.
- **Người dùng:** Người dùng chỉ gặp chương này đúng một lần — email "chúng tôi đã xảy ra sự cố" (hoặc không bao giờ nếu phát hiện kịp). Văn phong của email đó được viết bởi chất lượng của mọi chương trước; đây là chương duyên dáng nhất và buồn nhất của atlas.

---

## 8. Đọc tiếp & bài tập

- Incident command (phiên bản vận hành): **11.4** · Tuân thủ/GDPR/PDPD: **10.8** · Log/OTel: **11.2** · Backup/restore: **5.13** · Cell/cắt lan: **8.7**
- **Bài tập 1:** Checklist 6 nguồn tín hiệu §2.1: tích nguồn nào có log + alert thật. % dưới 50%? Đó là roadmap detection quý tới (và là lời giải cho "vì sao phát hiện muộn").
- **Bài tập 2:** Chạy tabletop 90 phút với kịch bản ransomware (giấy, mọi vai trò, giờ làm việc). Ghi 5 chỗ kẹt — mỗi chỗ một owner một hạn; chạy lại sau 3 tháng để thấy khác biệt.
- **Bài tập 3:** Tạo "thẻ giờ cháy" (khổ túi): 5 số điện thoại (IC, pháp lý, cloud support, CSIR, lãnh đạo) + 5 lệnh chứa nhanh nhất (revoke, isolate, kill-switch) + đường dẫn danh mục dữ liệu. In, dán. Tờ giấy 10.000đ đó là công cụ MTR giảm nhiều nhất trong toàn chương.

