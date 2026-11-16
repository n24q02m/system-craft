# 10.1 — Mô hình Đe doạ & Zero Trust

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Bảo vệ · Thiết kế
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 6.7 (zero trust ở client) · 9.4 (chốt chặn gateway).

**Sợi chỉ đỏ:** *DM nổi tiếng rồi — và từ lúc đó có người muốn dữ liệu 4 triệu tài khoản: an ninh bắt đầu từ đâu?* — trả lời: an ninh bắt đầu từ bản đồ, không phải từ tường — threat model trả lời "ai muốn gì của DM, qua đường nào"; thà đo adversary còn hơn "bảo mật mọi thứ" (tệ nạn đắt nhất); zero trust thay mô hình thành trì; assume breach thiết kế cho ngày đen. Câu hỏi để lại cho chương sau: *Ranh giới vẽ xong, lớp khoá — mật mã nào đang dùng, và máy lượng tử đã tới cửa chưa?*

**Thuật ngữ sẽ gặp:** *threat model* — ai, muốn gì, qua đường nào: ba câu trả lời trước khi mua bất kỳ công cụ nào; *zero trust* — không tin theo vị trí mạng: mọi request phải chứng minh (nối 6.7, 9.4); *assume breach* — thiết kế như kẻ đã vào trong: mục tiêu là chặn lan, không phải chặn cửa mãi mãi; *thuộc tính adversary* — bot quét, tội phạm, đối thủ có chủ đích: ngân sách khác nhau cả bậc; *bẫy "một giải pháp"* — mua một sản phẩm là xong: phòng thủ là kim tự tháp nhiều tầng, không phải một điểm.

**Ví dụ mở đầu:** Danh thiếp của DM giờ là 4 triệu tài khoản: câu hỏi đầu tiên không phải "mua WAF hãng nào" mà là "ai thật sự nhắm vào mình". Ba câu trả lời dẫn tới ba ngân sách khác hẳn nhau. Chương này vẽ bản đồ trước khi xây tường.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Phạm vi threat model: STRIDE/LINDDUN, ranh giới tin cậy nào | Tôi có thể vẽ mọi "bức tường tin" của hệ mình trong 10 phút không? |
| 2 | Giả định xấu nhất tôi thiết kế chống lại là gì (insider? APT? bug?) | Kẻ nào, động cơ nào, tay nghề nào — và tôi đáng bị nó để ý tới cỡ nào? |
| 3 | Mô hình tin cậy: vành đai (perimeter) hay zero trust | "Trong mạng nội bộ" còn là lý do bỏ qua kiểm tra không? |
| 4 | Tài sản gì cần bảo vệ, ưu tiên theo thiệt hại | Mất cái gì thì chết: dữ liệu khách, uptime, uy tín, tiền? |

---

## 2. Cơ chế

### 2.1 Threat model — bản đồ trước tường

Không có mô hình đe doạ, "bảo mật" là mua đồ theo quảng cáo. Bộ khung lọc nhanh:

- **STRIDE** (sản phẩm/hệ thống): **S**poofing (giả danh) · **T**ampering (sửa dữ liệu) · **R**epudiation (chối) · **I**nformation disclosure (lộ) · **D**enial of service (phá tính sẵn sàng) · **E**levation of privilege (leo thang);
- **LINDDUN** (quyền riêng tư): Linkability, Identifiability, Non-repudiation, Detectability, Disclosure of information, Unawareness, Non-compliance;
- **Ranh giới tin cậy (trust boundary)**: mọi nơi dữ liệu/điều khiển đi qua đổi chủ (user→app, service→service, process→OS, region→region) là một bức tường phải khai báo: **ai kiểm tra gì ở đây?**

Bài thực hành giá trị nhất: vẽ sơ đồ kiến trúc rồi tô **màu đỏ mọi ranh giới** — mỗi ranh giới không có chữ "kiểm tra X" là một lỗ hổng cấu trúc (không phải bug — lớn hơn bug).

### 2.2 Đo/thuộc tính adversary — tệ nạn của "bảo mật mọi thứ"

Thiết kế chống mọi kẻ = đắt không chịu nổi và vẫn hở (bảo mật không có "tất cả"). Phân lớp đối phương: **bug opportunist** (script kid quét — majority), **tội phạm vì tiền** (ransom, dữ liệu bán được), **APT** (nước nhà/nước ngoài nhắm bạn — hiếm nhưng chết), **insider** (nhân viên — thường bị coi nhẹ nhất nhưng có quyền nhiều nhất). Chọn lớp thiết kế chống = chọn ngân sách; viết giả định này ra (ADR — →11.6): "chống opportunist + tội phạm có tổ chức, KHÔNG cam kết chống APT có nguồn lực quốc gia" là câu trả lời trung thực của 95% doanh nghiệp.

### 2.3 Zero Trust — ba từ thay mô hình thành trì

Nguyên lý: **không tin theo vị trí mạng** — mọi request chứng minh danh tính + quyền, mọi lần (mỗi lần gọi, không phải một lần login). Ba trụ:
1. **Danh tính mạnh** cho người (passkey/MFA — →10.3) **và máy** (workload identity — →10.6);
2. **Kiểm tra từng request**: authn + authz ở service đích (hoặc sidecar/mesh làm giúp — →9.4 mTLS);
3. **Chính sách theo danh tính**, không theo IP/subnet ("10.0.0.0/8 được vào" là di sản cần khai tử dần).

Đừng nhầm: zero trust **không xoá** VLAN/firewall — hạ tầng mạng vẫn cần (blast radius — →8.7); nó **thêm** lớp "không tin mặc định" phía trên. Tương quan lịch sử: perimeter model sinh ra thời "mạng nội bộ = nhân viên" (1990s); cloud + laptop nhà + SaaS giết giả định đó — zero trust là lời đáp của thập niên 2020 (NIST 800-207 là tài liệu chuẩn đọc thêm).

### 2.4 Assume breach — thiết kế cho ngày đen

Chấp nhận "sẽ bị xâm nhập một phần" và thiết kế cho điều đó: **phân vùng** (cell — →8.7: vào được cell QA không vào được cell production), **danh tính ngắn hạn** (token phút — →10.3), **giám sát bên trong** (không chỉ cổng vào — →10.7 detection), **encrypt nội bộ** (mTLS — →9.4), **không đường tắt trusting nội bộ cho dữ liệu nóng** (DB không chấp nhận "nội bộ gọi thoải mái" — RLS/quota vẫn bật — →5.14). Câu hỏi kiểm tra: "kẻ tấn công đã đứng trong một pod/service — nó đi được tới đâu trong 3 bước?" — trả lời được bằng sơ đồ là có assume-breach thật.

### 2.5 Kim tự tháp phòng thủ & bẫy "một giải pháp"

| Tầng | Công cụ | Chương |
|---|---|---|
| Ranh giới | VPC/SG/firewall, WAF, rate limit | 9.3, 11.3 |
| Danh tính | OAuth 2.1, passkey, workload ID | 10.3, 10.6 |
| Dữ liệu | mã hoá at-rest/in-transit, KMS, PQC | 10.2 |
| Ứng dụng | OWASP 10, validate, CSP | 10.4, 7.7 |
| Chuỗi cung ứng | SBOM, SLSA, ký artifact | 10.5, 9.7 |
| Phát hiện | log, alert, IR | 10.7, 11.2 |

Mua một sản phẩm "giải quyết bảo mật" thường thay một tầng bằng hộp đen — kiểm tra nó thay tầng nào và tầng đó giờ ai chịu trách nhiệm.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| STRIDE | 6 lớp đe doạ | V | Microsoft khung |
| NIST 800-207 | chuẩn zero trust | V | 2020 |
| Tỉ lệ sự cố từ nhân viên nội bộ | ~tỷ trọng đáng kể các báo cáo ngành | I | verizon-style DBIR |
| Threat model session | 2–4 h cho một hệ vừa | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Bảo mật là **thuộc tính của ranh giới được khai báo**, không phải của sản phẩm được mua — mọi chương 10.x là chuyên môn hoá từng ranh giới; chương này là bản đồ.
- **S2:** Tham số trụ: số ranh giới tin cậy đã được khai báo/kiểm tra (audit), thời gian từ "vẽ mô hình" đến "cải tạo xong lỗ hổng cấu trúc", tỉ lệ service gọi nhau không qua authn (zero-trust debt).
- **S3:** Chọn lớp đối phương = chọn ngân sách: viết giả định vào ADR — không viết thì mỗi cuộc họp ngân sách lại tranh luận lại từ đầu (và "an ninh tuyệt đối" luôn thắng về khẩu hiệu, thua về số học).
- **S4:** Zero trust hội tụ với các quyết định khác của atlas: mTLS nội bộ (9.4), token ngắn (10.3), workload identity (10.6), cell (8.7) — một mô hình tin cậy nhất quán kéo theo cả chục quyết định kỹ thuật; đây là lý do nó là chương mở đầu.
- **S5:** AI tạo mặt mới: agent tự đọc/ghi dữ liệu với quyền của người dùng (→12.7) — threat model 2026+ bắt buộc thêm lớp "actor không phải người": audit từng hành động agent, quyền riêng cho agent hẹp hơn người (đừng kế thừa token user cho tác vụ nền).
- **S6:** Khi rà soát an ninh: bắt đầu từ **sơ đồ + tô đỏ ranh giới** (2.3 của chương 10.1 gốc) — không từ checklist công cụ; checklist sau bản đồ, không thay bản đồ.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| "Không biết bắt đầu từ đâu" | Chưa vẽ trust boundary | phiên threat model 2–4 h | §2.1 |
| Một lệch cấu hình = lộ toàn bộ | Không phân vùng (blast radius) | cell/segment audit (→8.7) | §2.4 |
| Nội bộ gọi nội bộ không kiểm tra | Perimeter-model di sản | zero-trust debt metric | §2.3 |
| Ngân sách an ninh tranh cãi mãi | Giả định adversary không ghi | ADR adversary (→11.6) | §2.2 |
| Mua công cụ mà vẫn sự cố | Công cụ thay một tầng, không thay trách nhiệm | đối chiếu bảng §2.5 | §2.5 |
| Audit xã hội xâm nhập dễ dàng | Insider bị coi nhẹ | quyền tối thiểu + audit hành động | §2.2 |

---

## 6. Cách đo

```bash
# Bài tập "3 bước của kẻ xâm nhập" (đo blast radius logic):
#   Chọn 1 service bất kỳ (giả định bị chiếm pod):
#   - Nó giữ token/secret gì? (→10.6)
#   - Nó gọi được những service nào không cần authn mới?
#   - Nó đọc được DB/schema nào không qua RLS?
#   Mỗi câu trả lời là một cạnh trong đồ thị "lan toả" — vẽ và đếm.

# Zero-trust debt: từ service mesh/network log, đếm gọi nội bộ
#   không mang danh tính có thể xác minh — con số tuần này vs tháng trước
```

Nguyên tắc: **bảo mật đo bằng "kẻ xấu đi được bao xa"** — con số bước, không phải số công cụ đã mua.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay full zero trust:** tăng cường perimeter + VPN + phân đoạn VLAN (hợp lệ cho hạ tầng tĩnh, ít kết nối ngoài — "đúng vấn đề cũ"); **thay threat model đầy đủ:** checklist OWASP ASVS + review theo hạng mục (tốt hơn không gì, mù hơn bản đồ).

Năm thấu kính:
- **Kinh tế:** Thiết kế chống đúng lớp đối phương tiết kiệm 50–90% so với "chống tất cả"; bỏ qua insider/bug opportunist vì "không ai thèm" là tính sai kỳ vọng, không phải tiết kiệm.
- **Vận hành:** Trust boundary mới xuất hiện mỗi lần thêm SaaS/AI/integration — threat model là tài liệu **sống** review mỗi quý (ADR hóa từng thay đổi — →11.6).
- **An ninh:** Bản thân chương này là "kim chỉ nam" của Quyển II-an ninh: mọi chương sau (10.2–10.8) là một ranh giới được chuyên môn hoá; đọc thiếu chương này thì các chương sau là công cụ không bản đồ.
- **Lịch sử:** Castle-and-moat (tường thành+hào — mạng nội bộ thập niên 90) → de-perimeterisation (Jericho Forum, 2004) → BeyondCorp (Google triển khai 2011+) → NIST 800-207 + "zero trust" marketing (2020s): ý tưởng 20 năm, hạ tầng (identity mọi nơi, mesh) chỉ vừa đủ chín trong 5 năm gần đây.
- **Người dùng:** Người dùng không thấy zero trust — họ thấy "đăng nhập một lần nhưng một số thao tác hỏi lại" và đôi khi khó chịu; giao tiếp rõ "tại sao hỏi lại" (đáng tiền của bạn) là một phần của thiết kế, không phải lỗi UX.

---

## 8. Đọc tiếp & bài tập

- Mật mã/KMS/PQC: **10.2** · Danh tính: **10.3** · Workload: **10.6** · Detection: **10.7** · Cell/blast radius: **8.7** · mTLS: **9.4**
- **Bài tập 1:** Vẽ sơ đồ hệ thống bạn, tô đỏ mọi ranh giới tin cậy. Đếm: bao nhiêu ranh giới có "kiểm tra" ghi rõ, bao nhiêu không? Tỉ lệ đó là điểm khởi đầu của roadmap an ninh 6 tháng.
- **Bài tập 2:** Viết ADR "adversary giả định" (một trang): chống ai, không chống ai, tại sao. Gửi lãnh đạo ký — có chữ ký, mọi cuộc tranh luận ngân sách sau đó ngắn hơn một bậc độ lớn.
- **Bài tập 3:** Chạy "3 bước của kẻ xâm nhập" (§6) với một service quan trọng. Ghi số bước tới dữ liệu khách; nếu ≤ 2, ưu tiên sửa tuần này (phân vùng + token ngắn).

