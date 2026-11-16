# 10.5 — An ninh Chuỗi cung ứng: SLSA, Sigstore, SBOM

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Bảo vệ · Kiểm chứng
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 9.7 (SBOM, digest đã gặp) · 7.3 (cây phụ thuộc npm).

**Sợi chỉ đỏ:** *Code của DM thật ra là của hàng nghìn package người khác — supply chain giữ sao?* — trả lời: code của DM thật ra là của hàng nghìn người viết package — supply chain giữ bằng SBOM (danh sách thành phần, sắp thành nghĩa vụ pháp lý theo CRA), SLSA (chứng minh build không bị bẩn), và vá theo rủi ro thật: điểm CVSS cao chưa chắc là việc đáng làm đêm. Câu hỏi để lại cho chương sau: *Máy cần bí mật để nói với nhau — secrets và workload identity quản thế nào cho khỏi lộ?*

**Thuật ngữ sẽ gặp:** *SBOM* — danh sách thành phần phần mềm: không thể bảo vệ thứ mình không biết là có; bắt buộc theo CRA (nối 10.8); *SLSA* — khung chứng minh nguồn gốc build: từ commit tới artifact không có bàn tay lạ chen vào; *CVSS* — điểm nghiêm trọng 0 tới 10: đo độ nặng lý thuyết, không đo "đang bị khai thác không"; *EPSS + KEV* — xác suất bị khai thác 30 ngày cộng danh sách đang bị đánh thật: vá trước; *pin và lock* — ghim phiên bản, khoá checksum: bản cập nhật lén im là rủi ro;

**Ví dụ mở đầu:** Vụ event-stream 2018: package npm triệu lượt tải mỗi tuần được giao cho người lạ — kẻ đó cài mã độc nhắm ví Bitcoin. DM có nghìn phụ thuộc trực tiếp, chục nghìn gián tiếp: câu hỏi là "có biết mình đang chạy gì không". SBOM cộng SLSA trả lời bằng chứng cứ, không niềm tin.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Mức SLSA mục tiêu cho artifact quan trọng (L1–L3) | Build của tôi có thể bị chèn mã không — và ai chứng minh không? |
| 2 | SBOM: format (CycloneDX/SPDX), sinh ở đâu, lưu bao lâu | "Có log4shell không?" — tôi trả lời trong bao lâu? |
| 3 | Ưu tiên vá theo gì: CVSS / EPSS / KEV | Tôi vá cái "điểm cao" hay cái "đang bị khai thác thật"? |
| 4 | Nguồn phụ thuộc: pin như thế nào, tin ai | Dependency mới vào codebase — qua cánh cửa nào? |

---

## 2. Cơ chế

### 2.1 Vì sao hạng này lên #3 (OWASP A03:2025)

Code bạn = code bạn + **hàng trăm người lạ** (npm/pypi/cargo trung bình chục–trăm phụ thuộc trực tiếp, hàng nghìn transitively (I)). Sự kiện thật 2024–2026: mã độc ẩn trong package phổ biến (Shai Hulud trong npm — chuỗi transitive lây (I)), dependency confusion (đăng package trùng tên nội bộ trên registry công), CI token bị ăn trộm qua post-install script. Chuỗi cung ứng = bề mặt tấn công mà **code bạn không sai vẫn bị**.

### 2.2 SBOM — danh sách thành phần (bắt buộc theo CRA — →10.8)

Máy đọc được: **CycloneDX** (an ninh-hướng) hoặc **SPDX** (giấy phép-hướng). Ba quy tắc: sinh **tại build** (tự động — không tay), **đủ sâu** (transitive, không chỉ direct), **lưu theo artifact** (biết image nào chứa gì — tra trong phút, không "ọ ọe" cả ngày). Câu hỏi kiểm thử sẵn sàng: CVE mới tung ra — **bao lâu** bạn liệt kê được mọi artifact đang chạy có chứa? Đó là SLO của SBOM (mục tiêu: phút–giờ).

### 2.3 SLSA — chứng minh build không bị bẩn

Bậc tin cậy của **quy trình build** (tóm tắt): **L1** có tài liệu quy trình (script build trong VCS + tự sinh provenance) → **L2** build trên host quản lý (CI là chủ, provenance ký) → **L3** build cách ly khó xâm phạm (isolated, sign provenance, nguồn không thể giả mạo). Hành động thật: CI chạy trong runner riêng (không share), **không script vị lai** chạy với quyền ghi registry, provenance ký bằng **Sigstore/cosign** (keyless — danh tính OIDC của CI), deploy **verify chữ ký** trước khi chạy (admission control K8s kiểm cosign — →9.1). L3 dành cho artifact "gốc tin" (base image, thư viện nội bộ dùng mọi nơi); đa số service nội bộ dừng L2 hợp lý.

### 2.4 Vá theo rủi ro thật: CVSS↛hành động, EPSS+KEV↛hành động

- **CVSS** (0–10): mức nặng lý thuyết — nhược: nửa số CVE 9+ chưa từng thấy trong khai thác (I);
- **EPSS** (0–1): xác suất bị khai thác **trong 30 ngày tới** (học từ dữ liệu thật — model cập nhật hàng ngày);
- **KEV** (CISA): danh sách **đang bị khai thác biết chắc**.
Quy trình chuẩn: **(KEV → vá ngay) > (EPSS cao + có mặt trong hệ) > CVSS cao còn lại**. Đi kèm: **ngữ cảnh phơi bày của app** (thư viện build-time không chạy trong production — exposure khác runtime) và thời gian sống SLA vá (KEV: giờ–ngày; EPSS cao: tuần; còn lại: theo quý).

### 2.5 Pin & khóa nguồn vào

- **Lockfile bất biến** (`npm ci`, `pip install -r` từ hash, `Cargo.lock` commit) — build lặp được (→9.7 hermetic);
- **Registry nội bộ/proxy** (chặn dependency confusion: tên nội bộ chỉ resolve nội bộ; cache ngoài và soát trước khi vào);
- **Quy trình thêm dependency mới**: PR riêng, review như code (SBOM diff hiện rõ thêm gì), nhu cầu thật (đếm KB — →7.3 cùng luật);
- **Renovate/Dependabot** nâng cấp tự động theo nhóm — nhỏ, đều, review được (thay cho đợi tới bản phát hành lớn rồi sửa cả chất đống).

### 2.6 Vòng của cả chương

```
code + lockfile → CI riêng (SLSA L2+) → build sinh SBOM + ký provenance (Sigstore)
  → registry nội bộ (verify chữ ký) → deploy chỉ chạy artifact đã ký + quét CVE
  → CVE mới: tra SBOM (phút) → xếp hạng KEV/EPSS → vá theo SLA → về đầu vòng
```
Mỗi mũi tên là một kiểm soát; thiếu mũi tên nào là cửa đó mở — và vòng này chính là "A03 defended".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| CycloneDX / SPDX | chuẩn SBOM (ISO/Chuẩn hoá) | V | |
| SLSA v1.0 | khung mức build | V | 2023+ |
| Sigstore/cosign | ký keyless OIDC | V | |
| EPSS | cập nhật hàng ngày | V | FIRST |
| KEV | CISA catalog | V | cập nhật liên tục |
| SLA tra SBOM khi CVE | phút–giờ | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Chuỗi cung ứng là **bề mặt bạn không viết** — kiểm soát bằng **bằng chứng có thể kiểm chứng** (SBOM, chữ ký, provenance), không bằng niềm tin vào "package nổi tiếng";
- **S2:** Tham số trụ: thời gian trả lời "artifact nào chứa CVE-X", tuổi trung bình dependency (security debt), % artifact deploy có chữ ký được verify, số CVE-KEV mở > SLA.
- **S3:** EPSS/KEV đổi "và cái gì" lấy "đang bị đánh thật" — nguồn lực vá luôn thiếu; bài toán là phân bổ, và dữ liệu khai thác thật là dữ liệu tốt nhất có.
- **S4:** Vòng §2.6 gắn chặt 9.7 (một artifact promote, hermetic) — an ninh chuỗi cung ứng và delivery có trách nhiệm **chung hạ tầng**: cùng CI, cùng ký, cùng registry; làm một lần dùng hai phen.
- **S5:** AI làm chuỗi dài hơn nữa (model + dataset + agent tool là "dependency" mới: model card, nguồn dữ liệu, phiên bản prompt — →12.x): SBOM đang mở rộng thành AI-BOM (model, weights nguồn) — khung cũ (danh sách+chữ ký) áp được, chất liệu mới.
- **S6:** Khi nghe "package X bị nhiễm": việc đầu tiên là **tra SBOM**, không phải đọc tin — 10 phút đầu quyết định bạn là tổ chức có danh sách hay tổ chức đoán.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Không biết có package X không | Không SBOM (hoặc direct-only) | sinh SBOM transitive ở build | §2.2 |
| CI token bị ăn qua post-install | Script chạy với quyền ghi registry | isolate runner + không quyền thừa | §2.3 |
| Dependency confusion | Resolve public trước internal | registry nội bộ + scope name | §2.5 |
| Vá bừa theo CVSS, vẫn dính KEV | Không xếp hạng theo khai thác | pipeline KEV/EPSS | §2.4 |
| Image chạy không ai biết nguồn | Deploy không verify chữ ký | cosign verify + admission | §2.3 |
| "Cũ lắm rồi không dám nâng" | Không nâng đều theo nhóm | Renovate + nhóm nhỏ | §2.5 |

---

## 6. Cách đo

```bash
# Sinh SBOM từ image đã build (một dòng, giờ phút):
syft <image> -o cyclonedx-json > sbom.json
grype sbom:cyclonedx-json        # quét CVE trên SBOM

# Đo SLO: từ lúc CVE công bố → danh sách artifact chứa (tra SBOM, không rebuild)
#   — bấm giờ drill này mỗi quý; > 1 giờ là phải tự động hoá thêm
```

Nguyên tắc: **"có bị không" phải là truy vấn 30 giây** — dài hơn là thiếu SBOM, không phải thiếu nỗ lực.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Sigstore:** KMS nội bộ ký (kiểm soát nhiều hơn, quản lý khoá nhiều hơn — →10.2); **thay SBOM tooling tự dựng:** dịch vụ scanner managed (đỡ vận hành, khóa vendor); **thay Renovate:** nâng tay theo lịch tháng (đủ khi ít repo — nhớ nợ lãi).

Năm thấu kính:
- **Kinh tế:** Thời gian trả lời CVE là **thời gian giảm rủi ro** — SBOM 30 giây vs 2 ngày lùng súng: chênh lệch đó tính bằng xác suất bị khai thác × thiệt hại; công cụ rẻ hơn một buổi tuân thủ.
- **Vận hành:** Mỗi khâu vòng §2.6 có owner và alert (KEV mới mở > SLA → trang dashboard đỏ); chuỗi cung ứng không có "xong" — chỉ có "đang sạch".
- **An ninh:** Kẻ tấn công đã học: đánh CI/registry dễ hơn đánh code (một lần trúng, nạn nhân là mọi downstream) — phòng thủ cũng phải chuyển trọng tâm tương ứng; đây là cuộc đua vũ trang của thập niên này.
- **Lịch sử:** "Left-pad" (2016 — 11 dòng gỡ làm gãy internet) → SolarWinds (2020, build bị chèn) → Log4Shell (2021, quét toàn cầu) → xz-backdoor (2024, kẻ tấn công kiên nhẫn làm maintainer!) → npm campaign (2025): mỗi sự kiện thêm một lớp chuẩn (lockfile → provenance → SBOM → verify) — tiền lương của chương này trả bằng tiền của nạn nhân trước.
- **Người dùng:** Người dùng cuối không biết dependency là gì — họ biết "cái app này của công ty lớn mà lại dính mã độc". Uy tín là tài sản bạn mượn của hàng trăm người lạ; chương này là cách quản lý khoản mượn đó.

---

## 8. Đọc tiếp & bài tập

- Hermetic/promote: **9.7** · Tuân thủ CRA: **10.8** · Secrets CI: **10.6** · Ký PQC lộ trình: **10.2** · Dependency & bundle FE: **7.3, 7.7**
- **Bài tập 1:** Chạy `syft+grype` (§6) trên image production chính. Ghi: số dependency, số CVE-KEV đang mở. Không làm nổi bước này = mọi chính sách vá của bạn đang đứng trên bùn.
- **Bài tập 2:** Bấm giờ drill: "package X bị nhiễm, hệ tôi có ở đâu không?" — không nhìn code, chỉ SBOM. > 30 phút? Tự động hoá tuần này.
- **Bài tập 3:** Kiểm tra CI: runner riêng? script install chạy với quyền gì? provenance ký chưa? Mỗi câu "không" là một bước lên SLSA kế tiếp — viết thành ticket có tên mức L.

