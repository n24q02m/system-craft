# 13.5 — Playbook: AI-Native, RAG & Multi-Agent

> **Tầng:** Nghiệp vụ · **Quyển III** · **Trục đọc:** playbook theo miền · **Động từ liên quan:** Áp dụng · Thiết kế
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** P12 trọn (12.1–12.7) · 12.3 (RAG là lõi).

**Sợi chỉ đỏ:** *AI trong từng pipeline — AI-native khác 'dán chatbot vào sản phẩm' chỗ nào?* — trả lời: AI-native khác "dán chatbot vào sản phẩm" — copilot (đề xuất, người quyết) hay agent (tự hành động) là quyết định định hình mọi thứ; RAG doanh nghiệp thêm ba thứ so với RAG công khai; multi-agent tách theo quyền, không theo vui; vòng đời tính năng AI là cỗ máy nhận model mới; và biên lợi nhuận tính theo từng tính năng. Câu hỏi để lại cho chương sau: *Khách ở hai bên bán cầu — đa vùng, residency, offline tính ra sao?*

**Thuật ngữ sẽ gặp:** *copilot vs agent* — người giữ quyết định hay AI tự quyết: ranh giới trách nhiệm và pháp lý; *RAG doanh nghiệp* — ACL, freshness, nguồn tường minh: ba thứ thêm vào 12.3; *multi-agent theo quyền* — mỗi agent một scope quyền như một service account: tách vì an toàn; *cỗ máy đổi model* — model mới mỗi quý: tính năng phải đổi model như đổi thư viện, không phải viết lại; *biên theo tính năng* — mỗi tính năng AI có lãi-lỗ riêng: âm thì tắt hoặc đổi thiết kế; *kiến trúc tham chiếu* — gộp cả P12 vào một bản vẽ.

**Ví dụ mở đầu:** "Thêm AI vào DM" bắt đầu từ đâu: copilot cho quản trị viên gõ lệnh tự nhiên trước, agent tự huỷ đơn sau. Và mỗi model mới ra mắt là một đợt hồi quy: bộ eval (12.5) phải chạy tự động như CI. Chương này là bản vẽ gộp — P12 từ sáu chương rời thành một kiến trúc đứng được.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Sản phẩm AI: copilot (người chính) vs agent (AI chính) | Trách nhiệm cuối cùng của bước này — người hay máy? |
| 2 | Kiến trúc RAG theo miền dữ liệu (12.3) + ACL theo tenant | Dữ liệu doanh nghiệp vào context — đã qua sân ACL chưa? |
| 3 | Multi-agent (12.4) — tách theo quyền hay giữ 1 agent + tools | Bao nhiêu agent thì đủ — và đường hot-line người ở đâu? |
| 4 | Vòng đời: eval + rollback + chi phí theo tính năng | Tính năng AI của tôi "sống" nhờ gì — số nào chứng minh? |

---

## 2. Cơ chế

### 2.1 Kiến trúc tham chiếu AI-native (gộp P12)

```
[User/Agent client] → [AI Gateway (12.6): auth, budget, cache, guardrail-in]
   → [Router/cascade: model nhỏ → lớn (12.6)]
   → [App agent-runtime (12.4): loop + tools + sandbox]
        ├→ [MCP servers (12.4): tools có OAuth 2.1 RS]
        ├→ [RAG (12.3): hybrid retrieval + ACL + rerank]
        └→ [Serving (12.2): vLLM/SGLang hoặc API provider]
[Observability (12.5): span gen_ai + eval online + cost/tenant]
[Evals CI (12.5): golden set chặn merge]
```

### 2.2 Copilot vs agent — quyết định định hình mọi thứ

- **Copilot** (người bấm nút cuối): draft câu trả lời/tóm tắt/gợi ý — sai thì người sửa trước khi tới khách; rủi ro thấp, giá trị "nhanh hơn";
- **Agent** (AI thực thi): đặt đơn, gửi mail, đổi cấu hình — rủi ro thật (12.4 sandbox + human-in-loop theo ngưỡng);
- Thực chiến: **bắt đầu copilot cho mọi nơi, agent cho khe hẹp có kiểm chứng** (nghiệp vụ lặp + kiểm được kết quả + thiệt hại giới hạn). Sản phẩm tuyên bố "agent toàn quyền" trước khi có eval + audit là nợ sự cố (12.1 §2.5 vỏ-xác-định).

### 2.3 RAG doanh nghiệp — thêm ba thứ so với RAG công khai

(1) **ACL theo tenant/user ở retrieval** (12.3 — I-068 là ví dụ tốn tiền); (2) **nguồn tươi**: tài liệu doanh nghiệp đổi hàng giờ — ingest pipeline CDC-style cho docs (13.3 tư duy) + version chỉ mục; (3) **trích nguồn bắt buộc** (mọi câu trả lời doanh nghiệp phải "từ tài liệu nào" — kiểm chứng + pháp lý + tin tưởng). Golden set cho RAG nội bộ: lấy từ **câu hỏi thật của nhân viên** (log + PM tuyển — không bịa).

### 2.4 Multi-agent doanh nghiệp — tách theo quyền, không theo vui

Template phổ biến: **research agent** (đọc rộng, không ghi) → **builder agent** (ghi trong sandbox) → **reviewer/validator** (đối chiếu kết quả với tiêu chí — LLM-judge 12.5) → **human gate** cho ngưỡng rủi ro. Tách theo quyền tự nhiên tạo bức tường (12.4 §2.6) và dễ audit từng giai đoạn. Anti-pattern: orchestration "đẹp diagram" nhiều agent ngang quyền gọi nhau — khó debug, tốn token, lỗi lan không rõ ai.

### 2.5 Vòng đời tính năng AI (cỗ máy đổi mô hình)

```
thiết kế (mức tin 12.1) → golden set + eval gate (12.5)
  → deploy canary tài chính 1% (12.6) → online eval + 👎 theo dõi
  → model mới ra: chạy lại toàn chuỗi (đổi model = deploy, không phải "nâng cấp")
```
Tổ chức có cỗ máy này đổi model trong tuần; tổ chức không có — dính I-067 (bill ×10) và "chất lượng tụt không rõ vì sao". Đây là lợi thế cạnh tranh thật 2026 (12.6-S5: model commodity hoá — vòng đời + data + eval là của mình).

### 2.6 Chi phí & biên theo tính năng

Unit: đ/task (12.6) — với cascading + cache + prompt-gọn (ba đòn không đổi chất lượng). Ngân sách theo tenant (13.7 gắn pricing: AI feature tính phí theo usage — cần metering chuẩn từ span). Dashboard: **chất lượng (eval) — chi phí (đ) — tốc độ (TTFT)** trên cùng đồ thị: ba trục là quyết định routing mỗi quý.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Golden set per tính năng | 50–500 case (12.5) | P | |
| Canary tài chính | 1% × 24 h trước full (12.6) | P | |
| Human-gate | ngưỡng rủi ro viết ra (12.4) | P | |
| ACL retrieval | filter trước prompt (12.3) | P | I-068 |
| Đ/task | metric sống theo tính năng (12.6) | P | |

---

## 4. Suy luận kiến trúc

- **S1:** AI-native = **P12 xếp vào kiến trúc quen** (gateway/routing/eval chiếm vị trí của LB/cache/test) — không phải hành tinh mới; ai vẽ được 13.1–13.4 sẽ vẽ được 13.5;
- **S2:** Tham số trụ: tỉ lệ task hoàn tất đúng (agent), điểm eval online, đ/task, cache hit %, số lần human-gate từ chối (chất lượng phán đoán), I-068-style violation (= 0).
- **S3:** Copilot-first đổi tốc độ ra mắt lấy rủi ro thấp; agent-for-khe đổi độ sâu tự động lấy yêu cầu vận hành (audit + eval + rollback) — cả hai đều hợp lệ ở đúng chỗ (bảng 11.7 build-vs-buy tư duy);
- **S4:** Vòng đời §2.5 là **pipeline CI/CD của model** — tái dùng hạ tầng 9.7 (canary/rollback/progressive) thay vì phát minh mới: AI đổi nhanh, hạ tầng delivery thì không cần đổi;
- **S5:** Multi-agent + MCP chuẩn (12.4) khiến "tool nội bộ" thành **sản phẩm có API** (mỗi tool giờ là resource server có khách hàng là agent) — chất lượng schema tool lên cấp độ hợp đồng public (4.3);
- **S6:** Khi "tính năng AI không ai dùng": đo hai bước — user có thấy không (TTFT/UX), và có tin không (👎 + task bỏ dở + eval phân nhóm) — 80% thất bại AI-native là thất bại niềm tin (bịa một lần đủ), chữa bằng RAG + trích nguồn + thu hẹp phạm vi.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| AI bịa trước khách (copilot lạm quyền) | Cấu trúc copilot→agent nhầm | kéo về human-gate | §2.2 |
| Đọc dữ liệu lân phòng (I-068) | ACL retrieval thiếu | filter + metadata (12.3) | §2.3 |
| Tài liệu cũ, trả lời cũ | Ingest không tươi | CDC-style + version index | §2.3 |
| Agent nhiều nhưng không debug nổi | Tách theo diagram đẹp | tách theo quyền + trace | §2.4 |
| Đổi model là sự cố (tiền/chất lượng) | Không cỗ máy §2.5 | eval gate + canary tài chính | §2.5 |
| AI feature lỗ không rõ | Không đ/task metering | span + metering theo tenant | §2.6 |

---

## 6. Cách đo

```bash
# Dashboard "sức khoẻ AI-native" (4 ô, cập nhật ngày):
#   1) task hoàn tất đúng % (tổng hợp eval online + user 👍)
#   2) đ/task + đ/ngày theo (feature × tenant × model)
#   3) TTFT/ITL p95 (12.2)        4) guardrail bắt + human-gate từ chối
# — bốn ô này là "SLO + FinOps" của sản phẩm AI (11.1 + 11.5 nhại lại)
```

Nguyên tắc: **tính năng AI không có bốn số thì chưa ra mắt** — như tính năng thường không ra mắt không có test.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự dựng agent-runtime:** framework agent + MCP server có sẵn (hệ sinh thái 2026 đủ dày — chọn như chọn web framework 4.x); **thay RAG tự làm:** nền tảng RAG managed (mua nhanh — nhớ ACL vẫn là của bạn: 12.3 không outsource được trách nhiệm); **thay multi-agent:** 1 agent + tool kỷ luật (đa số đủ — 12.4 quy tắc).

Năm thấu kính:
- **Kinh tế:** AI-native có **đường cong học tổ chức** — tính năng thứ nhất đắt (hạ tầng + eval + sai), tính năng thứ N rẻ (tái dùng cỗ máy §2.5): đo đầu tư theo cỗ máy, không theo feature;
- **Vận hành:** Runbook AI (11.8): model đổi, provider chết, hóa đơn nhảy, chất lượng trôi — bốn sự cố riêng với bốn lệnh chẩn riêng; on-call AI cần đào tạo như on-call DB;
- **An ninh:** Prompt injection + dữ liệu qua bên thứ ba + agent có quyền = **ba mặt trận 2026** (10.1/12.4/12.7); tổ chức thiếu 10.x sẽ cảm nhận qua AI đầu tiên;
- **Lịch sử:** "AI-native" là vòng quay thứ ba của "smart" (expert system 1980s — rules; ML 2010s — features; LLM 2020s — ngôn ngữ): mỗi vòng thêm **độ gần với con người** vào giao diện máy; mỗi vòng cũng học lại cùng bài "xác suất cần vỏ deterministic";
- **Người dùng:** Người dùng doanh nghiệp hỏi đúng một câu: "con AI này có tiết kiệm giờ tôi không — và nó bịa thì ai chịu?" Playbook này là kiến trúc của hai vế: tự động hoá (giờ) + kiểm soát (ai chịu) — một vế thiếu thì sản phẩm không bán được.

---

## 8. Đọc tiếp & bài tập

- P12 trọn: **12.1–12.7** · Gateway/CDN tư duy: **6.5, 12.6** · Progressive/canary: **9.7** · OTel: **11.2** · SaaS tenant: **13.7**
- **Bài tập 1:** Với mỗi tính năng AI (có/thiếu): điền 4 ô dashboard §6. Ô nào trống — đó là lý do "không dám mở rộng" hiện tại; đủ 4 ô = đủ dữ liệu cho quyết định route/rollback/định giá;
- **Bài tập 2:** Chạy penetration nội bộ ACL (tài khoản test, câu hỏi ngoài quyền — 12.3 bt2): nếu agent trả lời được nội dung ngoài quyền — sửa trước mọi tính năng mới (I-068 không chờ ai xong đâu);
- **Bài tập 3:** Viết "ADR copilot vs agent" cho tính năng kế tiếp: mức tin yêu cầu, human-gate ở đâu, thiệt hại tối đa nếu AI sai. Một trang — chuyển cuộc tranh luận "AI được không" thành quyết định có cấu trúc.
