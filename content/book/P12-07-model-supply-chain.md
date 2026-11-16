# 12.7 — Chuỗi cung ứng Model, LoRA & Pháp lý AI

> **Tầng:** AI · **Quyển III** · **Trục đọc:** nền AI · **Động từ liên quan:** Chọn · Tuân thủ
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số) · **Lưu ý pháp lý: tóm tắt kỹ thuật, không thay thế tư vấn luật**
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 10.5 (SBOM) · 10.8 (EU AI Act — khung tuân thủ).

**Sợi chỉ đỏ:** *Model từ đâu tới, ai ký, dữ liệu đi đâu — supply chain của chính AI?* — trả lời: model từ đâu tới, ai ký, dữ liệu đi đâu — ba con đường có năng lực AI (API, open-weight, tự train); bậc thang chi phí cố định Prompt rồi RAG rồi LoRA rồi SFT: leo đúng bậc; AI-BOM là SBOM của thế hệ AI; license "open" có bẫy thật; và EU AI Act là khung đọc pháp lý. Câu hỏi để lại cho chương sau: *DM giờ là platform thật — đầu tiên là tiền: sổ cái double-entry giữ đồng tiền thế nào?*

**Thuật ngữ sẽ gặp:** *ba con đường* — API của hãng, open-weight tự host, tự train: ba mức chi phí và kiểm soát; *bậc thang LoRA/SFT* — chỉnh nhẹ bằng dữ liệu riêng trước khi train lại: chi phí cố định tăng theo bậc; *AI-BOM* — khai báo nguồn model, giấy phép, dữ liệu train, phiên bản: SBOM cho AI (nối 10.5); *license model* — "open weight" chưa chắc tự do thương mại: đọc kỹ điều khoản; *EU AI Act* — phân lớp rủi ro, nghĩa vụ minh bạch (nối 10.8); *data moat* — dữ liệu riêng là thứ khó copy nhất: lợi thế thật nằm ở đây.

**Ví dụ mở đầu:** CTO DM hỏi "tự train model đi": chương trả lời bằng bậc thang — prompt đủ chưa, RAG đủ chưa, LoRA đủ chưa — rồi mới SFT. Như thư viện: mượn sách trước, xây toà nhà sau. Và mọi model vào hệ thống phải có AI-BOM như mọi package npm.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Nguồn model: API đóng / open-weights tự chạy / tự train | Tôi đang "mượn" hay "sở hữu" năng lực AI — và thoát được không? |
| 2 | Tinh chỉnh: prompt/RAG đủ chưa, hay cần LoRA/SFT | Đổi hành vi bằng ngữ cảnh (rẻ) hay bằng trọng số (đắt, cố định)? |
| 3 | AI-BOM: model nào, phiên bản nào, dữ liệu gì, license gì | Bảng kê khai "thành phần AI" của sản phẩm — có chưa? |
| 4 | Pháp lý AI: AI Act lớp rủi ro nào, dữ liệu huấn luyện ai | Sản phẩm của tôi rơi lớp nào — ai ký cam kết? |

---

## 2. Cơ chế

### 2.1 Ba con đường có năng lực AI

| Con đường | Có ngay | Cái giá |
|---|---|---|
| **API managed** | chất lượng cao nhất, zero hạ tầng | trả theo token (đắt khi scale), dữ liệu rời tổ chức, đổi giá theo provider |
| **Open-weights tự chạy** (Llama/Qwen/Mistral-style) | kiểm soát dữ liệu + chi phí biên tại scale | hạ tầng GPU + vận hành (12.2), chất lượng tự chịu, license model phải đọc |
| **Tự train** | lợi thế độc quyền thật | chục–trăm nghìn $ + đội ML + dữ liệu có bản quyền rõ — chỉ khi AI **là** sản phẩm |

Lịch trình phổ biến của một tổ chức: API (chứng minh giá trị) → hybrid (route phần nhạy về self-host — 12.6 gateway) → tự chạy/selective-finetune phần lõi. Tương tự build-vs-buy của 11.7: **tự train chỉ khi 5 năm nữa tôi thắng vì cái này**.

### 2.2 Prompt → RAG → LoRA → SFT — bậc thang chi phí cố định

```
PROMPT/RAG      — đổi ngữ cảnh: giờ, đảo chiều được, không train gì        (đa số nhu cầu)
LoRA (adapter)  — train lớp nhỏ gắn lên model gốc: giờ-GPU, MB weights,
                  dễ hoán đổi/rollback; hợp: phong cách, format, domain hẹp
SFT/full FT     — đổi chính model: đắt, đóng băng hành vi, cần eval lớn
Tự pretrain     — đội + tiền + dữ liệu ở một cấp khác
```
Quy tắc leo thang: **mỗi bậc chỉ khi bậc dưới đo là không đủ** (eval — 12.5); LoRA đáng khi prompt phình to vô hạn hoặc chất lượng chạm trần RAG. LoRA là "PR của AI": version, thử A/B, rollback — adapter là artifact có chữ ký (xuống dòng §2.3).

### 2.3 AI-BOM — SBOM của thế hệ AI

Bảng kê khai thành phần AI của một tính năng: **base model + phiên bản** (hash weights), **adapter/LoRA** (nếu có — cũng hash), **dữ liệu train/eval** (nguồn, license, PII đã xử lý), **prompt bản Q** (có version), **provider/serving config** (region — 10.8), **license chuỗi** (base + adapter + dataset). Dùng khi: khách hỏi "AI của anh chạy gì" (RFP/due diligence ngày càng hỏi), sự cố (model nào gây — rollback đúng thứ), pháp lý (AI Act kê khai), và CVE-model (model bị rút vì lỗi/license — biết mình dùng ở đâu ngay). Sinh tự động trong CI (một file YAML theo artifact — như 10.5 syft).

### 2.4 License model — bẫy của "open"

- **Apache/MIT-style** (một số model nhỏ, toolkit): tự do thật;
- **Community license** (Llama-style của Meta): miễn phí **tới mốc doanh thu/người dùng khổng lồ**, kèm điều khoản thương mại riêng — đọc kỹ mốc và điều khoản marketing/rival;
- **Open-weights khác điều kiện** (Qwen/Gemma/DeepSeek mỗi nhà một giấy phép): hầu hết cho phép thương mại với điều kiện; **kiểm tra từng phiên bản** (license đổi giữa các bản — thật);
- **API provider**: không phải license — **điều khoản dịch vụ** (data retention? train-on-my-data? export?) — đọc như hợp đồng (vì nó là hợp đồng).
Luật tổ chức: mọi model mới vào hệ thống qua **cổng duyệt license một trang** (như allowlist dep — 10.5), ghi vào AI-BOM.

### 2.5 EU AI Act & pháp lý dữ liệu AI (khung đọc)

AI Act phân **lớp rủi ro**: không-chấp-nhận (một số ứng dụng cấm), **rủi ro cao** (y tế, tuyển dụng, tín dụng... — nghĩa vụ tài liệu hóa, giám sát con người, log), rủi ro hạn chế (transparency — nói rõ "đây là AI"), GPAI/model nền tảng (nghĩa vụ nhà phát triển — tài liệu, bản quyền dữ liệu train). Lịch trình áp dụng theo đợt 2025–2027. Ba việc kỹ thuật đáng làm ngay bất kể vị trí lớp: **log quyết định AI** (audit — 12.4/10.7), **kê khai AI cho người dùng** (transparency), **danh mục dữ liệu** vào pipeline (GDPR/PDPD vẫn áp cho dữ liệu train — 10.8). VN: chưa có luật AI riêng (đang định hướng — theo dõi), nhưng PDPD (NĐ 13/2023) áp cho dữ liệu cá nhân trong mọi pipeline AI.

### 2.6 Dữ liệu là thứ thực sự khó copy

Model có sẵn cho mọi người (commodity hoá nhanh); **dữ liệu nghiệp vụ + golden set + eval** là lợi thế còn lại (đã nói 12.6-S5). Ba kỷ luật: quyền dữ liệu rõ ràng **trước** khi train (điều khoản dịch vụ cho phép dùng dữ liệu người dùng? — hỏi luật, đừng hỏi kỹ thuật); **PII/định danh tách** khỏi corpus (→5.13 giả danh hoá); **provenance ghi vào AI-BOM** — "dữ liệu này từ đâu" là câu hỏi pháp lý + đạo đức sẽ được hỏi sau (câu hỏi chậm nhưng chắc tới).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| LoRA train | giờ-GPU, weights MB | I | |
| SFT/full FT | đắt hơn bậc độ lớn | I | |
| AI Act | lớp rủi ro, áp dụng theo đợt 2025–2027 | V | EU |
| License model | đọc từng phiên bản | V | thay đổi thật |
| AI-BOM | file theo artifact, sinh CI | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Năng lực AI là **dependency như mọi dependency** — có nguồn, phiên bản, license, CVE, exit-plan (10.5 + 11.7 áp nguyên); AI-BOM là SBOM mở rộng, sinh cùng CI, dùng cùng lúc cần;
- **S2:** Tham số trụ: số model trong hệ có AI-BOM đầy đủ (mục tiêu 100%), tuổi trung bình kê khai, số lần rollback model (nhanh? đúng?), chi phí theo con đường (API/self — 12.6).
- **S3:** Bậc prompt→LoRA→SFT đổi **chi phí cố định** lấy hành vi ổn định: chọn theo tần suất đổi yêu cầu (thường đổi → ngữ cảnh; ổn định + hiệu năng quan trọng → adapter);
- **S4:** Base model là "platform vendor" mới: rủi ro giá/license/thu hồi tương tự cloud — thiết kế **abstraction mỏng** (gateway 12.6) để đổi được trong tuần, không quý;
- **S5:** Quy định AI đang hội tụ về **tài liệu hoá + log + transparency** — đúng ba thứ kỹ thuật tốt (12.4/12.5 đã dựng nếu làm chuẩn): làm trước luật thì tuân thủ là in ra; như 10.8 đã kết luận;
- **S6:** Khi RFP/khách hỏi "AI anh dùng gì": trả lời từ AI-BOM trong giờ — không có AI-BOM thì câu trả lời là "chúng tôi phải đi hỏi" (và khách ghi nhớ cái đó).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Không biết mình đang chạy model gì | Không AI-BOM | sinh CI + duyệt cổng license | §2.3 |
| Model bị rút/thay license, sập kế hoạch | Theo dõi thủ công | watch release notes + BOM | §2.4 |
| Prompt phình 10k token "để dạy style" | Nên dùng LoRA | bậc thang §2.2 | §2.2 |
| Khách từ chối vì dữ liệu qua provider | Không compliance routing | gateway route theo region/thoả thuận | §2.1, 12.6 |
| Được hỏi "AI Act anh thuộc lớp nào" không trả lời được | Chưa phân lớp | workshop + luật sư | §2.5 |
| Train xong không tái lập được | Dữ liệu train không version | dataset version + provenance | §2.6 |

---

## 6. Cách đo

```bash
# AI-BOM check (mỗi release tự sinh):
#   - model + hash weights? adapter + hash? dataset + license?
#   - provider + region? prompt version? → thiếu trường nào là đỏ
# Drill thoát: đổi 1 tính năng sang model dự phòng trong 1 buổi —
#   làm nổi = gateway/abstraction sống; làm không nổi = vendor-lock thật
```

Nguyên tắc: **mọi câu "dùng model gì, dữ liệu gì, license gì" trả lời từ file trong ≤ 5 phút** — lâu hơn là thiếu AI-BOM, không phải thiếu trí nhớ.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay AI-BOM tự sinh:** bảng tay trong wiki (dễ bắt đầu — nhưng mục như mọi bảng tay); **thay tự chạy open-weights:** cứ dùng API tới khi số học (12.6) hoặc pháp lý (dữ liệu) ép — đừng self-host vì tự hào; **thay LoRA tự train:** dịch vụ fine-tune managed (đầy trong hệ sinh thái — vẫn cần golden set + quyền dữ liệu của bạn).

Năm thấu kính:
- **Kinh tế:** Điểm hoà vốn API-vs-self là **đường cong không phải con số** (giá token đổi, GPU đổi) — review nửa năm bằng chính số mình (11.5); thoát sớm bằng gateway rẻ hơn thoát muộn;
- **Vận hành:** Model version = API version (4.8 additive-first không áp được — model đổi là hành vi đổi): chiến lược là **pin + canary + rollback nhanh** (12.5 gate + 12.6 canary tài chính), không phải "đóng băng không đổi";
- **An ninh:** Weights + adapter + prompt là **tài sản mã nguồn nhạy** (leak prompt system = lộ "mã nguồn" sản phẩm AI); dataset là tài sản PII — hai thứ này vào vault/quarantine quyền (10.6);
- **Lịch sử:** OSS license wars (2000s — 10.8 đã kể) đang tái hiện trong AI với tốc độ nhanh hơn: "open-weights" vs "open-source" tranh luận xanh đỏ — vị trí kỹ thuật an toàn: **đọc giấy phép từng phiên bản, ghi BOM, đừng dựa vào nhãn**;
- **Người dùng:** Người dùng cuối ngày càng được hỏi "chấp nhận AI không" — câu đó chỉ có nghĩa khi tổ chức trả lời được "AI của anh là gì, dữ liệu gì, ai chịu trách nhiệm khi sai"; chương này là ba câu trả lời đó bằng file có thể kiểm tra.

---

## 8. Đọc tiếp & bài tập

- Supply chain phần mềm: **10.5** · Pháp lý dữ liệu: **10.8** · Gateway/exit: **12.6** · Evals cho adapter: **12.5** · Playbook AI-native: **13.5**
- **Bài tập 1:** Lập AI-BOM cho mọi tính năng AI đang chạy (một buổi): model, version, dữ liệu, license, provider, region. Ô trống nhiều bất ngờ — mỗi ô là rủi ro chưa có chủ;
- **Bài tập 2:** Chạy drill thoát (§6): đổi một tính năng sang model dự phòng (cùng họ hoặc API khác) trong một buổi. Không nổi — viết kế hoạch gateway (12.6) lên roadmap quý;
- **Bài tập 3:** Đối chiếu điều khoản provider đang dùng: data retention? train-on-data? region? — một trang; nếu có điều khoản không trả lời được "dữ liệu khách của tôi đi đâu" — escalate lên pháp lý tuần này (đừng chờ khách hỏi).

