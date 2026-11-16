# 12.1 — 5 Giả định Cổ điển bị AI phá vỡ

> **Tầng:** AI · **Quyển III** · **Trục đọc:** nền AI · **Động từ liên quan:** Hiểu · Thiết kế
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.5 (GPU — phần cứng đã biết) · 5.10 (vector — đã biết tìm ngữ nghĩa).

**Sợi chỉ đỏ:** *Mọi tầng đã chạy — DM muốn trợ lý AI trả lời 'tối nay ăn gì': giả định nào của kỹ sư vỡ đầu tiên?* — trả lời: năm giả định của kỹ sư vỡ đầu tiên — cùng input không còn cùng output, độ trễ nhiều đuôi, "bug" sửa bằng dữ liệu chứ không bằng code, chi phí tính theo token, hành vi trôi theo bản model mới; nhưng bốn giả định may mắn vẫn nguyên vẹn (đừng phát minh lại): khung tư duy là "xác suất trong hộp xác định". Câu hỏi để lại cho chương sau: *Đã chấp nhận không tất định — serving LLM: TTFT, KV cache, batch, GPU tính thế nào?*

**Thuật ngữ sẽ gặp:** *xác suất trong hộp xác định* — AI là phần xác suất đặt trong hạ tầng xác định: giám sát cái hộp, chấp nhận phần trong; *năm giả định vỡ* — deterministic, reproducible, latency một đuôi, sửa lỗi bằng code, chi phí cỡ CPU: hết; *bốn giả định còn* — HTTP, cân bằng tải, cache, observability dùng nguyên: Quyển II áp nguyên; *bản đồ P12* — serving, RAG, agent, evals, economics, supply chain: sáu chương xếp sẵn; *đừng phát minh lại* — tầng lõi 2026 đã có: dùng, đừng chế.

**Ví dụ mở đầu:** Trợ lý DM trả lời "tối nay ăn gì": cùng câu hỏi ba lần ba câu trả lời, hóa đơn cloud có thêm dòng "token", một đêm nâng model đổi hẳn hành vi. Chương mở này vẽ khung: kỹ thuật cũ còn đứng được phần nào, phải học lại phần nào.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chấp nhận tính xác suất ở đâu, chèn tính xác định ở đâu | Nghiệp vụ nào **bắt buộc đúng 100%** — đường đó AI được phép vào tới đâu? |
| 2 | Ngân sách trễ mới: TTFT + ITL thay p99 một con | Người dùng tôi chịu đợi "từ chữ đầu" bao lâu và "giữa các chữ" bao lâu? |
| 3 | Đơn vị tài nguyên mới: GPU/HBM/bandwidth — ai quy hoạch | Tôi có "sizing" cho AI chưa hay vẫn đo bằng CPU cũ? |
| 4 | Định nghĩa "chạy đúng" khi không có đáp án duy nhất | Chất lượng đo bằng gì — ai duyệt — gate ở đâu? |

---

## 2. Cơ chế

### 2.1 Vì sao cần chương "mở" cho AI

Quyển I–II dựng trên một thế giới **đ deterministic**: cùng input → cùng output, độ trễ đến từ compute/IO, tài nguyên đo bằng CPU/byte, kiểm thử là so sánh đúng-sai. LLM phá cả bốn chân đó **cùng lúc** — mọi chương P12 là hệ quả của việc dựng lại nền. Nắm 5 giả định bị phá vỡ = hiểu tại sao "kỹ thuật AI" khác "kỹ thuật web" ở gốc, chứ không chỉ ở thư viện.

### 2.2 Năm giả định bị phá vỡ

1. **Determinism:** cùng prompt, hai lần chạy → hai câu trả lời khác nhau (sampling nhiệt độ; cả khi temperature=0, batching số học GPU vẫn làm lệch (I)); hệ quả: **"test pass" không còn là con số nhị phân** — chất lượng là phân phối (→12.5 evals); kết quả quan trọng phải có lớp xác định bọc ngoài (schema, tool, validate — AI đề xuất, code quyết định);
2. **Độ trễ = compute:** sinh token **tuần tự** (mỗi token một bước forward) — tổng thời gian ~ số token × thời gian/bước; giảm p99 không phải "mua máy nhanh hơn" mà là **it token hơn** (model nhỏ, output ngắn, cache) + pipeline song song (prefill/decode — →12.2). Thêm: **tuần tự chờ user đọc** — streaming là mặc định, không phải tối ưu;
3. **Tài nguyên đo bằng CPU:** GPU là cổ chai mới — và trong GPU, **HBM bandwidth** mới là giới hạn thật (decode là memory-bound — đọc toàn bộ trọng số cho mỗi token); "GPU rảnh nhưng chậm" là triệu chứng chuẩn của bệnh memory/queue chứ không phải thiếu FLOPS (I-066 → §5);
4. **Kiểm thử đúng/sai:** không có gold duy nhất — dùng **golden set + judge + phân phối điểm** (→12.5); regression là "chất lượng trượt 3%" chứ không "fail case 7"; nhiều tổ chức bỏ qua điều này và ship model mới theo cảm giác — rồi bất ngờ chất lượng tụt;
5. **Chi phí theo request:** hóa đơn theo **token** (vào/ra riêng giá; model to nhỏ khác bậc; reasoning sinh token suy nghĩ vô hình) — cùng tính năng, đổi model = hóa đơn ×N (I-067 → 12.6); unit economics có đơn vị mới: **đồng/triệu token** và **đồng/task hoàn chỉnh**.

### 2.3 Bốn giả định may mắn còn nguyên (đừng phát minh lại)

Đừng vứt Quyển I–II: **mạng vẫn chậm** (→1.6 — đặt inference gần user vẫn đáng tiền), **độ trễ người dùng vẫn 16 ms/frame cho UI** (AI streaming vào UI vẫn phải mượt), **hệ phân tán vẫn khó** (→8.x — serving cluster AI là bài 8.4/8.5 đúng bài bản), **quan sát vẫn cần** (→11.2 — trace giờ thêm span gen_ai). AI thay nền của một số chương, không thay nghề.

### 2.4 Bản đồ phần P12

```
12.1 nền tảng giả định      12.5 evals + guardrails + quan sát
12.2 serving (GPU)          12.6 token economics + routing
12.3 RAG + context          12.7 supply chain model + pháp lý
12.4 agent + MCP            (13.5 gộp lại thành playbook AI-native)
```

### 2.5 Khung tư duy "xác suất trong hộp xác định"

Mô hình tham chiếu dùng lại toàn atlas: **vỏ deterministic + lõi xác suất** — AI sinh đề xuất/thêm số/soạn text, nhưng: schema validate output (structured output/JSON mode), **tool gọi hàm đã test** (AI không tự ghi DB), quyền theo actor (→10.3), kết quả nhạy có xác nhận người. Cùng triết lý "client không tin cậy" (→6.7): AI là nhân viên mới nhiệt tình nhưng hay bịa — giao việc trong khung, không giao chìa khóa.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Token/s decode (serve thật) | chục–trăm/s (model lớn) | I | theo model/GPU |
| TTFT hợp lý | ~200 ms–2 s | I | theo prompt/model |
| Giá vào vs ra | ra đắt hơn rõ rệt | V | bảng giá provider |
| Giải bài model nhỏ vs lớn | chênh bậc độ lớn | I | →12.6 |
| HBM là cổ chai decode | memory-bound | V | hiểu biết chuẩn ngành |

---

## 4. Suy luận kiến trúc

- **S1:** AI-native không phải "thêm AI vào stack" — là **chấp nhận phân phối ở tầng đúng** (chất lượng, trễ, chi phí) và giữ deterministic ở nơi nghiệp vụ cần; biết vẽ đường đó là việc của kiến trúc sư 2026.
- **S2:** Tham số trụ: phân phối điểm chất lượng (không trung bình), TTFT/ITL p95, token/task, chi phí/task — bốn con số thay cho "model ngon không".
- **S3:** Mỗi giả định bị phá tương ứng một chương đầu tư: determinism→12.5, trễ→12.2, tài nguyên→12.2/12.6, kiểm thử→12.5, chi phí→12.6 — phần P12 tự tổ chức quanh bảng §2.2.
- **S4:** Vỏ-deterministic (§2.5) là lý do các chương 8–11 (idempotency, SLO, tracing, FinOps) vẫn nguyên giá trị — chúng là "vỏ"; P12 là "lõi" mới.
- **S5:** Vòng lặp lịch sử lặp lại: DB quan hệ từng là "gói tin cậy" bọc bên ngoài thực hành mù mờ; AI cần cùng một hành trình — **chuẩn hoá hợp đồng** (schema output, MCP cho tool — 12.4, eval làm test — 12.5) đang diễn ra đúng nhịp đó.
- **S6:** Khi thảo luận "AI có đáng tin không": câu hỏi sai — đúng là **"tôi cần tin cậy cỡ nào ở đầu ra này"** (gợi ý sản phẩm 70%? mã ICD-10 100%?) — trả lời được thì chương 12 còn lại là kỹ thuật làm cho đúng mức đó.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| "Test pass" mà khách phàn nàn | Đo nhị phân thay phân phối | evals golden set (→12.5) | §2.2-4 |
| Chậm dù GPU khỏe | Decode tuần tự + queue (I-066) | →12.2 §5 | §2.2-2,3 |
| Hóa đơn AI bất ngờ | Token suy nghĩ + model to (I-067) | →12.6 | §2.2-5 |
| AI "bịa" dữ liệu đúng format | Tin vỏ, quên validate ngữ nghĩa | dual-check + tool (→12.4) | §2.5 |
| Đổi model, tất cả lệch | Không regression eval | eval gate CI (→12.5) | §2.2-4 |
| Team cãi "AI có ổn không" | Thiếu mức tin theo nghiệp vụ | bảng đường-tin ADR | §2.5 |

---

## 6. Cách đo

```bash
# Đo tính xác suất của chính model bạn đang dùng (5 phút):
#   chạy cùng prompt 20 lần (temperature mặc định) —
#   đếm: bao nhiêu câu trả lời khác nhau? Điểm chất lượng lệch bao nhiêu?
#   → con số đó là "độ nhiễu nền" mọi test sau này phải tính tới

# Token thật của một tính năng: log input+output token mỗi call (→12.6)
#   — "tính năng tốn bao nhiêu nghìn token" là số mà PM cần biết như số giờ dev
```

Nguyên tắc: **đo nhiễu nền trước khi đo bất kỳ điều gì khác** — không biết nhiễu thì mọi "cải thiện 5%" là ảo ảnh.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay LLM chỗ cần 100% đúng:** không thay — dùng tool/code truyền thống (phân loại quy tắc, lookup) và chỉ gọi LLM cho phần mềm (I); **thay eval tự dựng:** dịch vụ eval managed (đáng khi chưa có chuyên gia — nhưng golden set nghiệp vụ vẫn phải tự viết: không ai hiểu nghiệp vụ giùm bạn).

Năm thấu kính:
- **Kinh tế:** Mỗi giả định bị phá là một **dạng hóa đơn mới** (nhiễu = chi phí soát; tuần tự = chi phí trễ; token = chi phí biên) — đặt tên được thì quản được, không thì chúng vẫn đến cuối tháng;
- **Vận hành:** Chạy AI trong tổ chức = thêm một "runtime" vào bảng vận hành (như từng thêm browser, rồi container): on-call cho AI cần runbook riêng (→11.8) — model đổi, pipeline đỏ, chi phí nhảy;
- **An ninh:** Giả định "input bị kiểm soát" chết với prompt injection (→12.4/12.5): ngữ liệu AI đọc là **vùng zero-trust mới** — mọi chương 10 áp xuống không giảm;
- **Lịch sử:** Máy tính 70 năm dạy thế giới "máy chính xác, người sáng tạo" — LLM đảo vai (máy sáng tạo, người chính xác); so sánh công nghiệp: động lực hơi nước thay cơ bắp (thế kỷ 18), AI thay "cognitive cơ bắp" (phân loại, tóm tắt, soạn thảo) — mỗi lần thay thế đều tạo nghề mới quanh **giám sát chất lượng đầu ra**;
- **Người dùng:** Người dùng không biết "hallucination" là gì — họ biết "con AI này nói sai một cách tự tin". Niềm tin là tài sản tích lũy qua mỗi lần đúng + mỗi lần sai được sửa nhanh; chương P12 là kỹ thuật nuôi tài sản đó.

---

## 8. Đọc tiếp & bài tập

- Serving: **12.2** · RAG: **12.3** · Agent: **12.4** · Evals: **12.5** · Tiền: **12.6** · Playbook gộp: **13.5**
- **Bài tập 1:** Với 3 tính năng AI (định làm/đã làm), viết mức tin yêu cầu (70/95/100%) + cơ chế đạt mức đó (người soát/schema/tool). Bảng này là ADR phân quyền giữa AI và code.
- **Bài tập 2:** Chạy thí nghiệm nhiễu nền (§6) với model đang dùng và prompt quan trọng nhất. 20 lần — ghi tỉ lệ khác biệt. Từ giờ mọi cải thiện dưới ngưỡng đó là nhiễu, không phải tiến bộ.
- **Bài tập 3:** Đo token/task của một tính năng (log trong một ngày). Nhân giá — viết "giá/vnd một task" lên bảng tính unit economics (→11.5): đây là con số lãnh đạo sẽ hỏi trước khi mở rộng.

