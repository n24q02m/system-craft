# 9.6 — IaC, GitOps & Internal Developer Platform

> **Tầng:** Nền tảng · **Quyển II** · **Trục đọc:** điều phối · **Động từ liên quan:** Tự động hoá · Duy trì
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.8 (mọi bước có đường lùi) · 5.15 (một nguồn thật — tư duy).

**Sợi chỉ đỏ:** *Hạ tầng bằng code — IaC và GitOps: ai là sự thật khi hai bên khác nhau?* — trả lời: hạ tầng thành mã thì hạ tầng có đủ mọi hệ quả của mã — review, version, test; GitOps là bộ ba: khai báo, Git làm nguồn chân lý, và vòng reconcile; drift (thực tại khác mô hình) được phát hiện thay vì giấu; IDP là sản phẩm cho dev. Câu hỏi để lại cho chương sau: *Niềm tin vào từng bản build — CI/CD, artifact, DORA đo thế nào?*

**Thuật ngữ sẽ gặp:** *IaC* — khai báo trạng thái mong muốn, công cụ tính diff: đổi hạ tầng như đổi code; *bốn công cụ bốn triết lý* — Terraform, Pulumi, CDK, config thuần: chương chấm từng em; *Git là nguồn chân lý* — mọi thay đổi qua pull request: sửa tay ngoài Git là nợ hạ tầng; *reconcile* — agent liên tục kéo thực tại về mô hình (nối 9.1): không áp dụng một lần rồi thôi; *drift* — hotfix bấm console lúc nửa đêm: reconcile sẽ lộ; chính sách xử lý là câu hỏi tổ chức; *IDP* — internal developer platform: golden path cho dev, dùng như sản phẩm thật.

**Ví dụ mở đầu:** Nửa đêm hotfix, admin bấm console tăng RAM: hệ về, ai cũng quên. Ba tuần sau pipeline kéo thực tại về mô hình cũ — sự cố tái phát lúc ba giờ sáng. GitOps trả lời "ai là sự thật khi hai bên khác nhau": Git — mọi khác biệt phải hiện ra, không ai được giấu tay.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Công cụ IaC: Terraform/OpenTofu/Pulumi/Crossplane — state ai giữ | Vấn đề state/drift đã được trả lời bằng cơ chế chưa? |
| 2 | Kiểu IaC: mutable (apply chèo) hayGitOps pull (reconcile liên tục) | Ai/cái gì quyết định "cái gì đang chạy": một lần, hay mãi mãi? |
| 3 | Phạm vi tự động hoá: chỉ prod, hay cả DNS/quota/team perm | Ranh giới "cái gì được tạo bằng tay" ở đâu — còn hợp lệ không? |
| 4 | IDP: có cần, và "golden path" đầu tiên là gì | Dev tự phục vụ được gì trong < 1 ngày, không cần ticket? |

---

## 2. Cơ chế

### 2.1 IaC — hạ tầng thành mã (và mọi hệ quả của mã)

Hạ tầng viết trong file: review được, version được, tái tạo được, **diff được trước khi áp** (thay đổi thế giới chạy qua "plan" trước). Ba hệ quả phải tổ chức: (1) **state** (file ánh xạ tài nguyên thật ↔ mã — đặt remote + lock, mất state = mù giữa sa mạc tài nguyên); (2) **module hoá** (băng-đải lặp lại thành thư viện nội bộ — "VPC chuẩn", "service chuẩn" — như design system 7.4 của hạ tầng); (3) **đời tư của secrets** (state/không được chứa secret — dùng secret store + reference — →11.6).

### 2.2 Bốn công cụ — bốn triết lý

| | **Terraform/OpenTofu** | **Pulumi** | **Crossplane** | **CloudFormation/CDK** |
|---|---|---|---|---|
| Ngôn ngữ | HCL | ngôn ngữ thật (TS/Py/Go) | YAML/K8s API | YAML hoặc ngôn ngữ |
| Mô hình | apply theo lệnh | apply theo lệnh | **reconcile liên tục trong K8s** | theo lệnh |
| Nơi sống state | file remote | service | etcd (→8.2!) | cloud giữ |
| Hợp nhất khi | imperative orchestration nhiều cloud | code logic phức tạp | đã tin K8s làm trung tâm | một cloud sâu |

Chọn ít sai: Terraform/OpenTofu (đa cloud, hệ sinh thái module lớn nhất, OpenTofu là nhánh open-source sau khi Terraform đổi giấy phép (2023) — cả hai đang chạy song song cộng đồng); Pulumi khi logic provision phức tạp (vòng lặp, điều kiện thật); Crossplane khi **K8s đã là trung tâm vũ trụ** của bạn (control plane reconcile — tinh thần 9.1 mở rộng ra hạ tầng cloud).

### 2.3 GitOps — declarative + Git là nguồn chân lý + reconcile

- **Push** (CI chạy `apply`): quen thuộc, đơn giản — CI cần quyền viết hạ tầng (bề mặt to);
- **Pull** (Argo CD/Flux trong cluster): cluster **tự kéo** Git về và converge — Git là nguồn chân lý thật sự (ai đổi tay ở cluster → bị reconcile kéo lại = **tự phát hiện drift**); quyền riêng thu nhỏ; audit tự nhiên (mọi thay đổi qua PR).

Chu kỳ chuẩn: PR (plan comment) → review → merge → controller reconcile → drift bị phát hiện hàng giờ. Đây là vòng reconcile của 9.1/8.2 giáng xuống quy trình con người — **cùng một ý tưởng, ba tầng** (etcd giữ K8s, Git giữ app+infra, Argo giữ hội tụ).

### 2.4 Drift — khi thực tại không giống mô hình

Nguồn: tay sửa trong console ("chỉ lần này thôi"), API ngoài mặt (console/CLI/lambda của cloud đổi thuộc tính), module đổi. Đối phó: **drift detection định kỳ** (plan không áp dụng + alert chênh lệch) — và văn hoá: mọi "hotfix bằng tay" phải kết thúc bằng commit lại (hoặc bị xóa ngay lần reconcile sau — chọn một trong hai, đừng sống giữa).

### 2.5 IDP — nền tảng cho dev, như sản phẩm

Internal Developer Platform = lớp tự phục vụ phía trên IaC/GitOps: **golden path** (tạo service mới: repo + CI + deploy + dashboard + alert chỉ bằng một lệnh — Backstage-style template); **self-service có rào** (dev được làm trong biên platform đặt: namespace, quota, network policy có sẵn). Nguyên tắc sản phẩm: đo **time-to-first-deploy** của dev mới (giờ — không tuần); đường vàng cần **vận hành như sản phẩm** (roadmap, user research nội bộ, roi đo bằng giờ tiết kiệm). IDP không phải "portal đẹp" — là **chuẩn hoá con đường phổ biến nhất** (cùng tinh thần design system 7.4: hợp đồng + mặc định khôn ngoan).

### 2.6 Bậc thang trưởng thành tự động hoá

```
1. Console + wiki "cách làm"         — không lặp lại được
2. Script chạy tay (bash/ansible)    — lặp được, không audit
3. Terraform + CI                    — version, review; state là cơn đau đầu tiên
4. GitOps pull + module chuẩn        — drift tự phát hiện, PR là cửa
5. IDP golden path                   — dev tự phục vụ < 1 ngày
```
Đừng nhảy theo mốt: mỗi bậc giải vấn đề của bậc trước; tổ chức 5 người ở bậc 2 có thể hạnh phúc mãi (định luật Yagni — mọi chương đều nhắc).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Terraform/OpenTofu | song song cộng đồng (sau licence 2023) | V | |
| Argo CD / Flux | chuẩn GitOps CNCF | V | |
| Drift scan chu kỳ | giờ–ngày | P | |
| Time-to-first-deploy IDP | mục tiêu < 1 ngày | P | |
| PR → production (đường vàng) | phút–giờ | P | |

---

## 4. Suy luận kiến trúc

- **S1:** IaC chuyển hạ tầng từ **thao tác** thành **tài sản review được** — mọi lý do "review code" (4.8) áp nguyên vẹn cho hạ tầng: PR hạ tầng cũng cần plan + người duyệt.
- **S2:** Tham số trụ: số tài nguyên ngoài IaC (audit định kỳ), số drift phát hiện/tuần, time-to-first-deploy, tỉ lệ thay đổi qua PR (vs console).
- **S3:** Pull GitOps đổi một lớp controller (vận hành thêm) lấy drift-detection + thu nhỏ quyền — đáng khi cluster nhiều/team đông; push đơn giản đủ khi ít người.
- **S4:** Module IaC nội bộ là **design system của hạ tầng**: cùng luật version/deprecate (→7.4/4.8) — module "ai cũng dùng" đổi một dòng là sự cố toàn công ty (quản trị như thư viện thật).
- **S5:** AI sinh IaC khá giỏi (cú pháp học được) nhưng **state/quyền/tiền** vẫn là trách nhiệm con người: review plan kỹ hơn review code — vì "apply" chạm thế giới thật ngay lập tức (→12.7).
- **S6:** Khi "hạ tầng ai cũng sửa được nhưng chẳng ai biết tại sao": đó là triệu chứng thiếu module/state chuẩn — chẩn bằng đếm tài nguyên trùng lặp + audit đường tạo; sửa bằng bậc 4 (§2.6), không bằng "thêm quy trình duyệt tay".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| State lock/conflict | Apply song song/lost state | remote lock + plan trong CI | §2.1 |
| Tài nguyên "mồ côi" (tiền chảy) | Xóa code không xóa tài nguyên | audit cloud vs state định kỳ | §2.4 |
| Drift tái phát sau reconcile | Có thứ ngoài Git vẫn thay | tìm nguồn (console/lambda) | §2.4 |
| Secrets lộ trong state | Nhét secret trực tiếp | vault + reference | §2.1 |
| Platform thành cổ chai | Mọi ticket chờ team platform | golden path tự phục vụ | §2.5 |
| Module chuẩn "ai cũng sợ nâng" | Không version breaking policy | semver module + deprecate lịch | §2.4 |

---

## 6. Cách đo

```bash
# Audit tài nguyên mồ côi (đối chiếu hai chiều):
#   cloud CLI list tài nguyên (tag theo module)  vs  terraform state list
#   — mỗi tài nguyên có tag không nằm trong state = ứng viên xoá (tiền thật)

# Drift định kỳ: terraform plan -detailed-exitcode (CI đêm) —
#   exit != 0 && != 2: có khác biệt — alert, không apply tự động
```

Nguyên tắc: **sự khác biệt giữa Git và thực tại phải là một metric** — con số này tăng dần tuần này chính là "nợ vận hành" đo được (mọi chương trước đều có metric tương ứng — đây là của hạ tầng).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Terraform:** Pulumi (dev quen ngôn ngữ thật) hoặc Crossplane (đã sống trong K8s) — chọn theo kỹ năng đội; **thay IDP Backstage:** README + template repo (khởi đầu trung thực — golden path v0 là một repo mẫu copy được); **thay GitOps:** CI push + kỷ luật (đủ khi nhỏ — đừng mua reconcile khi chưa có drift).

Năm thấu kính:
- **Kinh tế:** Mỗi tài nguyên mồ côi là tiền chảy không ai thấy (audit trên trả tiền buổi đầu tiên); IaC review còn **giảm chi phí sự cố** (đổi hạ tầng giờ có diff như code).
- **Vận hành:** Bậc thang §2.6 là lộ trình đào tạo nhân sự ngầm — mỗi bậc đòi kỹ năng mới (state → GitOps → product thinking); lên bậc khi người đã sẵn sàng, không khi mốt đã sẵn sàng.
- **An ninh:** GitOps thu nhỏ quyền (CI không giữ chìa hạ tầng — controller giữ trong cluster); audit "ai đổi gì khi nào" = git log — bằng chứng tự nhiên cho compliance (→11.6).
- **Lịch sử:** "Pets vs cattle" (2012, meme cloud) → IaC (2014+) → GitOps (2017, Weaveworks đặt tên) → platform engineering (2023+ phản ứng "DevOps mọi người làm hết"): mỗi giai đoạn tách một lớp chuyên trách — kết luận bất biến: tự động hoá không xoá việc vận hành, nó **nâng việc lên tầng trừu tượng cao hơn**.
- **Người dùng:** "Người dùng" của chương này là dev nội bộ — và họ xứng đáng có trải nghiệm như khách hàng: repo mới sáng tạo chiều đã chạy được với dashboard. IDP là sản phẩm bán nội bộ có ROI đo bằng giờ của đồng nghiệp.

---

## 8. Đọc tiếp & bài tập

- Reconcile/etcd: **8.2, 9.1** · Module như design system: **7.4** · Version additive: **4.8** · Progressive delivery trên GitOps: **9.7** · Secrets: **11.6** · DevOps metrics: **11.4**
- **Bài tập 1:** Đếm tài nguyên nằm ngoài IaC (console tạo tay): lập danh sách + lý do từng cái. Mỗi dòng không có lý do thuyết phục = nợ (hoặc tiền mồ côi).
- **Bài tập 2:** Cài drift scan đêm (lệnh §6) một tuần — đếm lần lệch và nguyên nhân. Con số này là "mức độ module hoá thật" của tổ chức.
- **Bài tập 3:** Đo time-to-first-deploy: cho dev mới repo trống → deploy thành công lên staging. > 1 ngày? Viết golden path v0 (repo mẫu + 10 bước README) — đó là dự án IDP đầu tiên đáng làm.
