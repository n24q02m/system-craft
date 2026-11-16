# 10.6 — Quản lý Bí mật & Danh tính Workload

> **Tầng:** An ninh · **Quyển II** · **Trục đọc:** phòng thủ · **Động từ liên quan:** Bảo vệ · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.2 (fencing token — tư duy chứng minh) · 9.6 (IaC: bí mật trong mã là nợ).

**Sợi chỉ đỏ:** *Máy cần bí mật để nói với nhau — secrets và workload identity quản thế nào cho khỏi lộ?* — trả lời: máy nói chuyện với máy cũng cần bí mật — credentials tĩnh là "khoá chì": copy đi hết hệ thống và không bao giờ chết; giải pháp là dynamic secrets sinh khi cần, và tận cùng là workload identity: pod tự chứng minh qua nền tảng, không credential dài hạn để lộ. Câu hỏi để lại cho chương sau: *Nếu đã bị xâm nhập — phát hiện từ đâu và xử lý ra sao?*

**Thuật ngữ sẽ gặp:** *credential tĩnh* — API key nằm trong file config: khoá chì ai cũng copy được, sống mãi mãi; *dynamic secrets* — Vault sinh khi workload xin, TTL ngắn: hết việc là tự chết; *workload identity* — K8s service account đổi token ngắn hạn: không có chuỗi dài hạn để rò rỉ; *đúng workload, đúng field* — phân phối theo danh tính: không "một bucket chung mọi bí mật" cho cả cụm; *ba lớp chống lộ* — quét repo, soi log, phát hiện dùng khoá bất thường: lộ phải thấy trong giờ; *SPIFFE* — chuẩn danh tính cho workload: cấp "CMND" cho máy như cho người.

**Ví dụ mở đầu:** Bí mật của DM nằm trong config, được copy qua ba môi trường, hai repo backup và một tài liệu onboarding: khoá chì in ra nhiều bản. Dynamic secret và workload identity: mỗi pod danh tính riêng, token mười phút, không còn gì để copy. Đây là đường từ "khoá chì" tới "không credential".

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Secrets động (Vault-style sinh theo nhu cầu) hay tĩnh (config/ENV) | Mỗi secret của tôi sống bao lâu — và lộ thì thu hồi bao lâu? |
| 2 | Workload identity: service "chứng minh mình là mình" bằng gì | Pod xác thực với DB/S3 bằng credentials phát ra hay danh tính nền tảng? |
| 3 | Phân phối: ai được đọc secret nào (policy theo workload) | Secret DB nằm ở bao nhiêu config/file/repos? |
| 4 | Phòng chống lộ: scan, audit, rotation | Lộ qua log/commit (I-063) — phát hiện trong bao lâu? |

---

## 2. Cơ chế

### 2.1 Vấn đề: credentials tĩnh là "khoá chì"

API key dài hạn trong ENV/config/repos: lặp (mọi env một bản), sống mãi (không ai xoay — xoay là dự án), lan truyền (copy vào script, wiki, máy dev), và **lộ âm thầm** (log, commit history, screenshot). Mọi chương trước đã gặp hậu quả (I-063 lộ qua log/commit; I-064 token không thu hồi nổi). Hai hướng giải: **rút ngắn tuổi** (động) và **bỏ credential** (danh tính nền tảng).

### 2.2 Dynamic secrets — sinh khi cần, chết khi hết

Vault-style flow: workload xác thực với vault → **xin** credential (DB user riêng, TTL 1 giờ; cloud STS token 15 phút–1 giờ) → dùng → hết hạn tự chết → xin lại. Lợi: mỗi workload một bộ (audit được ai làm gì ở DB), lộ thì **TTL tự sát** thay vì thu hồi tay, không "đại sứ" credentials chung. Giá: vault là hạ tầng HA phải nuôi (→8.2/8.7 — lại một control plane), ứng dụng phải xử lý refresh (không phải "đọc ENV một lần lúc khởi động").

### 2.3 Workload identity — không credential cả

Hướng đẹp nhất: **danh tính do nền tảng chứng minh**, credential không bao giờ tồn tại dưới dạng "giá trị":
- **K8s:** ServiceAccount token projeted (audience-bound, TTL ngắn) + **OIDC federation** ("cluster này có SA X" → cloud cấp role);
- **Cloud:** instance/pod **identity gắn nền tảng** (IAM role cho pod — IRSA-style; workload identity GKE-style) — cloud cấp token tạm cho đúng workload;
- **SPIFFE/SPIRE** cho đa nền tảng (SVID — danh tính crypto cho mọi process).
Kết cấu: pod không giữ "chìa khóa S3" — nó **là** một danh tính được cấp quyền (→10.1 zero trust cho máy). Bỏ được: secret phân phát, xoay, thu hồi — cả danh mục biến mất.

### 2.4 Phân phối & policy — nguyên tắc "đúng workload, đúng field"

Vault/KMS policy theo **danh tính workload** (không theo "ai cũng đọc được vault chung"): service A chỉ đọc được secret của A (DB user riêng — →5.14 cùng triết lý tenant). Chuẩn hoá: **một workload = một danh tính = một bộ quyền nhỏ** (→10.3 least privilege áp xuống máy). Anti-pattern đo được: đếm số nơi một secret DB xuất hiện (config repos, wiki, script deploy...) — > 1 là nợ; đếm số workload chia chung một credential — > 1 là mù audit.

### 2.5 Chống lộ — ba lớp phát hiện

1. **Scan:** pre-commit + CI quét secret (gitleaks/trufflehog — đã hẹn ở 6.7/10.2) — bắt trước khi vào history; commit history cũ cũng quét định kỳ (secret nằm đó năm năm vẫn sống);
2. **Audit access:** log mọi lần đọc secret (ai-workload nào, lúc nào) — đọc bất thường (workload lạ, giờ lạ) là tín hiệu;
3. **Rotation làm giới hạn thiệt hại:** tuổi secret là **cửa sổ lộ không phát hiện**; xoay định kỳ = thu hẹp cửa sổ (secret sống 90 ngày → lộ tối đa 90 ngày không ai biết); dynamic làm cửa sổ thành 1 giờ.

### 2.6 Secret trong các tầng đặc biệt

- **CI/CD:** runner cần registry/cloud — dùng **OIDC federation** (GitHub Actions → cloud role, không lưu key dài hạn trong secrets setting);
- **Dev local:** môi trường dev không nên có secret prod (dịch vụ giả/mật mã hoá cột nhạy — →5.13); nếu bắt buộc: vault dev riêng + quyền tách;
- **Log/metrics:** redact trước khi ghi (pattern token/Authorization header — →11.5 log hygiene; lỗi số một của I-063);
- **AI pipeline:** API key model (OpenAI-style) là secret nóng mới — quy tắc như DB: vault + theo workload + quota (→12.7).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| DB credential động TTL | 30 phút–1 giờ | P | |
| Cloud STS token | 15 phút–1 giờ | V | |
| K8s projected SA token | TTL ngắn, audience-bound | V | |
| Rotation tĩnh | ≤ 90 ngày (nếu còn tồn tại) | P | |
| SPIFFE/SPIRE | chuẩn danh tính workload mở | V | |

---

## 4. Suy luận kiến trúc

- **S1:** Quản lý bí mật = **quản lý tuổi thọ + quyền** (ngắn, hẹp, đo được) — không phải "giấu chỗ nào khó tìm";
- **S2:** Tham số trụ: tuổi trung bình secret (động %), số nơi một secret xuất hiện, số workload dùng chung credential, thời gian phát hiện secret lộ (drill scan).
- **S3:** Workload identity đổi "phát secret" lấy "cấp danh tính" — kiến trúc sạch hơn một bậc (không có giá trị để lộ) nhưng phụ thuộc nền tảng (K8s/cloud — portable kém hơn vault tự quản).
- **S4:** Vault/identity là **control plane an ninh** — cùng họ etcd/KMS (→8.2/10.2): HA, backup, drill phục hồi; mất vault = mất khả năng khởi động lại service (không xin được credential) — một dạng chết im lặng.
- **S5:** AI agent cần credential (gọi tool, API) — **không kế thừa token người dùng** cho việc nền: danh tính agent riêng + scope từng tool (→12.7) — đây là lỗi thiết kế phổ biến nhất 2026 của hệ có agent.
- **S6:** Khi "có gì đó lạ trong log access": đối chiếu audit vault (ai đọc gì khi nào) với hành vi thật — secret management tốt biến điều tra từ "đoán" thành "đối chiếu hai bảng".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Secret lộ qua log/commit (I-063) | Quản tay + không scan | pre-commit + CI scan + xoay ngay | §2.5 |
| Không biết service nào dùng key nào | Credentials dùng chung | một workload một bộ + audit | §2.4 |
| Xoay key = dự án 6 tháng | Static + rải config | dynamic vault + config trung tâm | §2.2 |
| Pod giữ AWS key trong ENV | Chưa dùng workload identity | IRSA/OIDC federation | §2.3 |
| Vault chết → service không khởi động lại | Control plane không HA/DR | HA + drill + break-glass | §2.2, §4 |
| Dev có secret prod | Môi trường không tách | dịch vụ giả + vault dev | §2.6 |

---

## 6. Cách đo

```bash
# Đếm "độ rải" của secret quan trọng nhất:
#   grep -r "<secret-prefix>" --include='*.{yml,env,sh,md}' . | wc -l
#   (đặt prefix nhận diện được; > 3 nơi = nợ dồn về vault)

# Drill lộ: cài một "canary secret" (giả) vào repo staging —
#   scan có bắt trong CI không? Sau bao lâu (cả lịch sử cũ)?
#   — con số đó là thời gian phát hiện lộ thật của tổ chức
```

Nguyên tắc: **mọi secret có sổ hộ khẩu** (nơi ở, tuổi, ai đọc, thu hồi thế nào — như 6.7 đã yêu cầu với token client; chương này là bản platform của cùng luật).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Vault tự dựng:** cloud KMS/Secrets Manager (managed — nhanh, khóa nhẹ); External Secrets Operator (K8s đồng bộ từ cloud vault vào pod — giữ UX ENV cho app cũ); **thay SPIFFE:** cloud workload identity (đủ nếu một cloud — SPIFFE đáng khi đa nền/đa cloud).

Năm thấu kính:
- **Kinh tế:** Static secret rẻ hôm nay, đắt ngày lộ (sự cố + dự án xoay khẩn cấp); dynamic đắt vận hành hôm nay, rẻ trong mọi kịch bản xấu — bảo hiểm đúng nghĩa.
- **Vận hành:** Mỗi service mới phải "tự nhận danh tính + xin quyền" theo golden path (→9.6 IDP) — làm đúng một lần trong template thì mọi service sau miễn phí; làm tay từng service thì nợ lãi.
- **An ninh:** Kẻ tấn công sau khi vào pod, việc đầu tiên là **săn credential** (ENV, file, /proc) — workload identity làm môi trường trống rỗng (không có gì để nhặt) — phòng thủ bằng nghèo đói.
- **Lịch sử:** Password trong config file (2000s) → ENV var (2010s, vẫn tĩnh) → vault (2015+) → cloud identity federation (2020s): mỗi thế hệ **rút credential ra khỏi tay ứng dụng** một bước; đích đến không có secret để quản lý.
- **Người dùng:** Người dùng giao mật khẩu của họ cho bạn một lần — chương này (cùng 10.2/10.3) là cách bạn không làm họ tiếc việc đó. "Bị hack vì một API key quên trong repo" là câu chuyện không ai muốn giải thích cho khách.

---

## 8. Đọc tiếp & bài tập

- Khoá & envelope: **10.2** · Token người dùng: **10.3** · Zero trust: **10.1** · Detection từ audit: **10.7** · IDP golden path: **9.6** · Agent credential: **12.7**
- **Bài tập 1:** Liệt kê 5 secret quan trọng nhất hệ thống: tuổi, số nơi xuất hiện, ai đọc được, lộ thì thu hồi bao lâu. Bảng này gần như luôn có ít nhất một ô làm bạn giật mình — đó là ticket đầu tiên.
- **Bài tập 2:** Cài canary secret drill (§6). Thời gian phát hiện là con số duy nhất nói thật về năng lực chống-lộ của tổ chức (mọi chính sách trên giấy đều "nhanh").
- **Bài tập 3:** Chuyển một service (chọn service ít rủi ro) sang dynamic credentials tuần này: vault sinh DB user TTL 1h + app refresh. Bài học vận hành từ một service sẽ rút ngắn lộ trình cho hai chục service còn lại.
