# 12.5 — Evals, Quan sát gen_ai & Guardrails

> **Tầng:** AI · **Quyển III** · **Trục đọc:** nền AI · **Động từ liên quan:** Đo · Bảo vệ
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 7.6 (kim tự tháp test) · 11.2 (bốn tín hiệu).

**Sợi chỉ đỏ:** *AI sai thì ai chặn — evals và guardrails là cổng nào của pipeline?* — trả lời: AI sai thì ai chặn — eval là kiểm thử cho thế hệ không deterministic: không có đáp án đúng, có rubric chấm; LLM-judge là thợ chấm rẻ nhưng phải được soát; guardrails ba lớp quanh vòng đời (vào, trong, ra); và quan sát gen_ai gắn span vào bốn bảng điều khiển. Câu hỏi để lại cho chương sau: *Mỗi câu trả lời tốn tiền — token economics và routing tính sao cho lãi?*

**Thuật ngữ sẽ gặp:** *eval* — bộ câu hỏi cộng rubric thay cho assert: chạy mỗi lần đổi model hay prompt; *rubric* — tiêu chí chấm nhiều mức có ví dụ neo: thay cho expected output; *LLM-judge* — model chấm model: rẻ và scale được, nhưng phải soát bằng mẫu người chấm; *guardrails* — ba lớp: lọc vào, kiểm trong (tool, ngân sách), soi ra (PII, chất lượng); *golden set* — bộ vàng vài trăm ca: mọi thay đổi phải qua trước prod; *văn hoá eval* — không đo thì đừng đổi: prompt cũng là code, cũng cần test.

**Ví dụ mở đầu:** Đổi prompt một tối cho vui: chatbot DM lịch sự hơn — và từ chối 30% đơn hợp lệ vì "nhạy cảm". Không eval thì phát hiện bằng phàn nàn của khách. Golden set chạy mỗi pull request như unit test, chỉ khác cách chấm: theo rubric. Chương này là cổng chất lượng của cả quyển AI.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Eval gate: golden set + ngưỡng — chặn CI/CD khi trượt (D-130) | Model/prompt đổi — hệ thống nào **từ chối deploy** khi chất lượng tụt? |
| 2 | LLM-judge: chấm gì tự động, chấm gì bằng người | Ai phán "câu trả lời này tốt" — và judge có được đánh giá không? |
| 3 | Guardrails: chống injection, PII, nội dung cấm — ở mấy lớp | Bức tường thật của tôi nằm ở đâu (input/output/tool)? |
| 4 | Quan sát gen_ai: span, token, chi phí theo feature/tenant | Tôi có dashboard "AI đang khoẻ không" như dashboard service không? |

---

## 2. Cơ chế

### 2.1 Eval — kiểm thử cho thế hệ không deterministic

Ba lớp theo tốc độ phản hồi:
- **Unit-style (mỗi PR):** golden set (50–500 case đại diện) + assert cấu trúc (JSON schema, có trích nguồn, độ dài); ngưỡng điểm (ví dụ: faithfulness ≥ 0,85 — trượt = **chặn merge** như test đỏ (D-130));
- **Eval batch (mỗi khi đổi model/prompt/RAG):** LLM-judge chấm thang + so phiên bản (A/B chất lượng); regression report "rơi từ 0,87 → 0,82 ở nhóm câu hỏi X" — nhóm X là chỗ sửa;
- **Online (production):** sampling câu trả lời thật + judge + user feedback (👍/👎, task hoàn tất — 12.4) — bắt trôi dạt theo dữ liệu thật.
Ba lớp cùng golden set gốc (đóng băng tập, phiên bản hoá khi nghiệp vụ đổi) — eval không có golden set là "cảm giác có kiểm tra".

### 2.2 LLM-judge — thợ chấm rẻ, phải được soát

Judge (model chấm model) scale được nhưng có bias đã biết: **thiên vị dài** (câu dài điểm cao), **thiên vị tự dạng** (model khoái câu trả lời giống giọng mình), **thiên vị thứ tự** (A/B đổi chỗ đổi điểm). Ba kỷ luật: rubric chặt (tiêu chí từng điểm + thang rõ, không đánh giá chung chung); **chấm mù hai chiều + random thứ tự**; định kỳ **so judge với nhãn người** (mẫu 50 — đồng thuận thấp thì judge chưa đáng tin để chấm ai). Judge đúng chỗ: faithfulness (bám nguồn), format, độc hại; sai chỗ: sự thật tuyệt đối (judge cũng bịa — ground truth phải từ nguồn).

### 2.3 Guardrails — ba lớp quanh vòng đời

```
[INPUT]   lọc PII/secret (→10.6 redact), phát hiện injection trực tiếp,
          giới hạn độ dài/attachment
[PROCESS] tool schema chặt + egress allowlist (→12.4), sandbox,
          context tách channel dữ liệu/lệnh
[OUTPUT]  schema validate, quét PII/secret rò, kiểm tra trích nguồn,
          policy nội dung; Human-in-loop cho ngưỡng rủi ro
```
Nguyên tắc phân bổ: **lớp INPUT/OUTPUT rẻ và rộng; lớp PROCESS là tường thật** (quyền + sandbox + egress — 12.4); prompt "đừng lộ dữ liệu" là biển báo, không phải tường. Guardrail tự nó là hệ thống: có version, có eval (tỉ lệ bắt đúng / báo nhầm), có metric "số lần chặn theo loại" — im lặng tuyệt đối thường là guardrail chết, không phải thế giới hoà bình.

### 2.4 Quan sát gen_ai — span + bốn bảng

OTel GenAI semantic convention (→11.2 cùng nền): mỗi call gen_ai span mang **model, prompt_tokens, output_tokens, TTFT, cache hit, chi phí (tính tại chỗ theo bảng giá), feature/tenant**. Bốn dashboard bắt buộc: chất lượng (điểm eval online + tỉ lệ 👎), hiệu năng (TTFT/ITL p95 — 12.2), **chi phí theo feature/tenant/ngày** (→12.6), an ninh (injection bắt, PII chặn, hành động bị human từ chối). Không có bốn bảng này, vận hành AI là kể chuyện.

### 2.5 Eval cho agent — khó hơn, nhưng cùng xương

Agent eval = **tác vụ hoàn tất đúng** (không chỉ câu chữ): kịch bản có kết cục kiểm chứng được (đơn đặt đúng, file tạo đúng chỗ, câu trả lời khớp nguồn) + **số bước/token tới đích** (hiệu quả) + không-tác-hại (không đụng tài nguyên ngoài phạm vi — kiểm bằng audit log 12.4). Tự động hoá: môi trường sandbox dựng lại + kịch bản chạy đêm — là "E2E test" của agentic (→7.6 kim tự tháp áp được nguyên).

### 2.6 Văn hoá eval — không đo thì đừng đổi

Hai quy tắc tổ chức: (1) **đổi model/prompt/RAG mà không chạy eval batch = deploy lên production mù** — CI chặn (D-130); (2) golden set là **tài sản nghiệp vụ** (chủ sản phẩm + kỹ thuật cùng duyệt) — không phải file kỹ thuật tự tạo rồi quên. Tổ chức có hai quy tắc này nói "chất lượng tụt 2% vì model mới" trước khi khách nói.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Golden set | 50–500 case, có phiên bản | P | |
| Ngưỡng eval gate | theo nghiệp vụ, ghi trong repo | P | |
| Judge-vs-human | đồng thuận mẫu 50 định kỳ | P | |
| Span gen_ai | model, token, TTFT, cost | V | OTel convention |
| Guardrail metric | bắt/tổng + báo nhầm | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Eval là **CI/CD của chất lượng AI** — cùng vị trí trong pipeline (chặn merge), cùng kỷ luật (golden set như test suite, regression như bug);
- **S2:** Tham số trụ: điểm eval theo phiên bản (trend), tỉ lệ guardrail bắt theo loại, chi phí/feature, judge-human agreement, tỉ lệ 👎 theo tính năng.
- **S3:** Judge đổi tiền người lấy scale — đáng ở faithfulness/format; ground truth mới phải người; **soát judge định kỳ** giữ cho hệ thống đáng tin;
- **S4:** Guardrails nhiều lớp theo quyền lực thật (sandbox > schema > prompt) — defense-in-depth của 10.1; metric chặn là **tín hiệu sống**, không phải phiền toái;
- **S5:** Điểm eval online + chi phí trên cùng dashboard buộc câu hỏi đúng: "tính năng này đáng chất lượng đó không?" — nối thẳng 12.6 (routing theo giá trị câu hỏi);
- **S6:** Khi "chất lượng tụt sau đổi gì đó": so eval report trước/sau (bắt buộc có nếu quy tắc §2.6 sống) — nhóm câu hỏi rơi nhất chỉ chỗ bệnh; không có report thì chẩn đoán là khảo sát ý kiến.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Đổi model, chất lượng ám ảnh tụt | Không eval gate | golden set + CI chặn | §2.1 |
| Judge chấm "nghe cũng được" | Rubric lỏng + bias | rubric + so human | §2.2 |
| Guardrail im luôn | Guardrail chết/bypass | test canary (chèn case xấu) | §2.3 |
| Agent đọc dữ liệu lân phòng (I-068) | ACL thiếu ở retrieval (→12.3) | filter trước prompt | §2.3 |
| Không biết AI tốn bao nhiêu theo feature | Span thiếu cost/tenant | gen_ai span + dashboard | §2.4 |
| Eval "xanh" nhưng khách chê | Golden set lệch thế giới thật | bổ sung từ log production | §2.1 |

---

## 6. Cách đo

```bash
# Eval gate trong CI (bản mộc — chạy được luôn):
#   pytest test_eval.py  # case: gọi model với golden set, judge chấm,
#                        # assert mean >= threshold; fail → chặn merge
# Canary guardrail: cài 5 "case xấu" (injection/PII) vào traffic thật
#   (đánh dấu) — nếu không bị chặn: guardrail chết, sửa trước kỳ nghỉ
```

Nguyên tắc: **eval giống test — chạy trong CI, đỏ thì dừng**; mọi phiên bản "eval ở đâu đó trong tài liệu" là không tồn tại.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay LLM-judge:** chấm người toàn bộ (chuẩn nhất, không scale — dùng cho mẫu + ground truth mới); **thay guardrail tự viết:** dịch vụ managed (cân nhắc: guardrail thấy nội dung — →12.7 pháp lý); **thay golden set tự nuôi:** benchmark chung (chỉ để so model với ngành — **không** thay golden set nghiệp vụ: thế giới bạn không giống benchmark).

Năm thấu kính:
- **Kinh tế:** Eval rẻ hơn một lần rollback model tồi (một ca trực + uy tín); judge tự động giảm giờ người bậc độ lớn — nhưng eval + guardrail là chi phí **thường trực**, vào ngân sách AI từ đầu;
- **Vận hành:** Golden set rác — rác (dữ liệu đổi theo sản phẩm): review mỗi quý cùng PM; guardrail rule như code — version, owner, test;
- **An ninh:** Guardrail metric là **telemetry an ninh lớp mới** (→10.7 thêm nguồn tín hiệu) — đưa vào dashboard SOC;
- **Lịch sử:** Compiler warning (1970s) → unit test (1990s) → code review + CI (2000s) → eval + judge (2024+): mỗi thế hệ non trẻ đều phải tự chế "máy soi" trước khi tin được mình;
- **Người dùng:** Người dùng không xem điểm eval — nhưng họ là **eval online lớn nhất** (👍, task hoàn tất, bỏ giữa chừng). Đo hành vi đó tử tế là nghe được điều họ không nói ra.

---

## 8. Đọc tiếp & bài tập

- Serving & quantize: **12.2** · Agent & sandbox: **12.4** · Token kinh tế: **12.6** · OTel: **11.2** · RAG ACL: **12.3** · Playbook: **13.5**
- **Bài tập 1:** Dựng golden set 50 case cho tính năng AI chính (nửa buổi với PM). Chạy hôm nay — ghi điểm. Đó là "baseline v0"; từ giờ mọi thay đổi AI phải qua cổng này trong CI;
- **Bài tập 2:** Chèn 5 canary xấu (§6) vào luồng staging: injection giả, PII, yêu cầu ngoài phạm vi. Đếm bị chặn — dưới 4/5 là guardrail đang là trang trí;
- **Bài tập 3:** Thêm cost + tenant vào span gen_ai (nếu chưa) và vẽ dashboard chi phí/feature/ngày. Bảng này sẽ là thứ PM nhìn nhiều nhất trong quý tới.

