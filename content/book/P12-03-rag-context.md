# 12.3 — RAG & Context Engineering

> **Tầng:** AI · **Quyển III** · **Trục đọc:** nền AI · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.10 (vector search) · 10.3 (authz — ACL của RAG).

**Sợi chỉ đỏ:** *Model không biết menu tuần này — RAG đưa tri thức vào ngữ cảnh thế nào cho tin được?* — trả lời: model không biết menu tuần này — RAG gán cho AI một thư viện: tìm đúng mẩu, xếp vào ngữ cảnh, trích dẫn kiểm chứng được; chuỗi retrieval hiện đại có hybrid search và rerank; ACL-aware là lỗ hổng có mã sự cố I-068 — AI có thể tráo quyền; và context engineering là nghề mới bên prompt. Câu hỏi để lại cho chương sau: *Trợ lý phải hành động (đặt bàn, sửa đơn) — agent và MCP vạch ranh gì giữa AI và hệ thống?*

**Thuật ngữ sẽ gặp:** *retrieval* — tìm mẩu liên quan từ kho tri thức: hybrid từ khoá cộng ngữ nghĩa (nối 5.6, 5.10); *rerank* — xếp lại theo liên quan thật trước khi nhét vào hộp: chặt ở đúng chỗ; *chunking* — cắt tài liệu thành mảnh có nghĩa: cắt sai là tìm sai; *ACL-aware retrieval* — lọc theo quyền của người hỏi, không phải quyền của hệ: lỗ hổng I-068; *RAG vs long-context* — nhét cả kho vào context: đắt và vẫn trượt: chương có bảng quyết; *context engineering* — chọn gì vào hộp ngữ cảnh: nghề mới.

**Ví dụ mở đầu:** Trợ lý DM trích menu đã ngừng bán tuần trước: không phải model dở — retrieval cũ. Nguy hơn: trợ lý lộ bảng chiết khấu nội bộ của chuỗi A cho nhân viên chuỗi B, vì retrieval không lọc theo quyền người hỏi. Chương này là chuỗi RAG có khoá ACL, kèm bảng điều khiển đo ba lớp.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | RAG hay long-context (hay cả hai) | Trả lời cần "tìm đúng đoạn" hay "đọc cả kho"? chi phí đổi ra sao? |
| 2 | Pipeline retrieval: hybrid (BM25+vector), rerank, chunking | Tỉ lệ tìm đúng đoạn của tôi là bao nhiêu — đo chưa? |
| 3 | **ACL-aware retrieval**: lọc theo quyền ngay lúc lấy | Agent có thể đọc tài liệu người dùng không được đọc không? (I-068) |
| 4 | Ngữ cảnh: cấu trúc prompt, ưu tiên, ép kích thước | Cái gì vào context — theo thứ tự nào — bỏ gì khi đầy? |

---

## 2. Cơ chế

### 2.1 RAG = gán cho AI một thư viện

Model biết chung chung (tham số đóng băng lúc train); RAG **tra cứu lúc hỏi** rồi nhét kết quả vào context: domain mới/đổi thường xuyên/kiểm chứng được (trích nguồn). Ba tầng chất lượng quyết định theo thứ tự quan trọng: **(1) retrieval tìm đúng đoạn chưa** (rác vào — rác ra, model không cứu được); (2) **đoạn có vừa ngữ cảnh không** (đầy đủ, không cắt dở khái niệm); (3) model tổng hợp. Đa số "AI bịa" thực chất là tầng (1) hỏng — không phải model dở.

### 2.2 Chuỗi retrieval hiện đại

```
query → (a) viết lại query (bóc ý chính, hydrate từ hội thoại)
      → (b) HYBRID: BM25 (từ khoá chính xác) + vector (ngữ nghĩa) — song song
      → (c) fuse (RRF) + RERANK (cross-encoder chấm cặp query-đoạn)
      → (d) LỌC THEO QUYỀN (ACL) — tại đây, trước khi vào prompt
      → (e) top-k vào context, trích nguồn ID
```
Hai điểm hay bỏ quên: **hybrid** — BM25 bắt tên mã/số seri mà embedding miss (→5.6 ES/OpenSearch đã dạy hybrid; →5.10 vector); **rerank** — tăng precision rõ rệt với chi phí nhỏ (mô hình nhỏ chấm điểm). Chunking: theo cấu trúc tài liệu (heading/mục) + overlap; chunk nhỏ đủ để chọn lọc, đủ lớn để có nghĩa — "số ma thuật" không tồn tại, đo recall trên dữ liệu mình.

### 2.3 ACL-aware — lỗ hổng kiểu I-068

Tình huống: agent RAG được quyền đọc kho tài liệu để trả lời; kho có tài liệu phòng khác; **retrieval trả về đúng nhu cầu ngữ nghĩa nhưng sai quyền truy cập** — agent đọc và nhắc nội dung lân phòng (I-068: "Agent truy cập dữ liệu lân phòng qua RAG"). Chữa đúng chỗ: **filter quyền TRƯỚC khi vào context** — (a) metadata tenant/user gắn từng chunk lúc ingest (→5.14 RLS tư duy), (b) truy vấn chỉ lấy chunk khớp ACL, (c) defense-in-depth: system prompt + kiểm tra sau xuất (guardrail 12.5) — nhưng (a)+(b) là bức tường thật, prompt chỉ là biển báo. Bài học tổng quát: **RAG là một API dữ liệu** — mọi chương 10.3/10.4 (authZ, BOLA) áp nguyên văn cho retrieval.

### 2.4 RAG vs long-context

Context dài (trăm nghìn token) làm câu hỏi "cần RAG không?" hợp lệ lại: đọc 10 tài liệu trực tiếp — đúng hơn (không mất bước retrieval), đắt hơn (token mỗi lần gọi), chậm hơn (prefill dài — 12.2), không scale kho (vài nghìn tài liệu thì thôi). Quy tắc: **kho nhỏ + quan trọng đúng tuyệt đối → context; kho lớn/đổi/ACL phức tạp → RAG**; thực chiến: RAG để **chọn** 10 tài liệu rồi nhét đầy đủ (best of both). Long-context không giết RAG — nó nâng RAG thành "chọn ít hơn, đọc kỹ hơn".

### 2.5 Context engineering — nghề mới bên prompt

Context là **ngân sách có thứ tự**: system (quy tắc) → tool định nghĩa → ngữ cảnh hội thoại → tài liệu RAG (theo ưu tiên relevancy) → câu hỏi. Bốn kỷ luật: (1) **đầu cố định** để prefix cache hit (→12.2); (2) **cắt đúng chỗ** khi tràn (một vụng về cắt làm mất tool định nghĩa → agent "quên" cách gọi — bug khó hiểu); (3) **nguồn trích dẫn ID** trong context để output nói được "từ tài liệu nào" (kiểm chứng — và guardrail bắt lệch); (4) **tối thiểu hoá PII trong context** (điều vào prompt là điều đã rời "kho an toàn" — log + retention áp xuống — 11.2/10.8).

### 2.6 Đo RAG — bảng điều khiển ba lớp

- **Retrieval:** recall@k (tỉ lệ câu hỏi có đúng đoạn trong top-k) trên golden set; latency;
- **Tổng hợp:** đúng-thực-tế (faithfulness — câu trả lời có bám đoạn không; LLM-judge — 12.5); trích nguồn đúng;
- **Nghiệp vụ:** tỉ lệ "tôi không biết" (RAG được phép — và nên — nói không biết thay vì bịa); user feedback.
Ba lớp tách nhau: retrieval tốt + tổng hợp tệ → sửa prompt/model; retrieval tệ → sửa pipeline §2.2. Không đo ba lớp là mù cả ba.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Chunk điển hình | vài trăm–1k token + overlap | P | theo tài liệu |
| Rerank chi phí | model nhỏ, ms–chục ms/query | I | |
| Context dài hiện đại | trăm nghìn token | V | theo model |
| Recall@k mục tiêu | > 0,8–0,9 trên golden set | P | |
| ACL filter | trước khi vào prompt | P | I-068 |

---

## 4. Suy luận kiến trúc

- **S1:** RAG là **hệ thông tin có model ở đầu ra** — chất lượng trội theo tầng retrieval → tổng hợp; đầu tư đúng tầng (đo recall trước khi đổi model);
- **S2:** Tham số trụ: recall@k, faithfulness, tỉ lệ từ chối-trả-lời, context token trung bình (tiền — 12.6), ACL-violation bắt được (phải = 0).
- **S3:** Long-context đổi tiền lấy chính xác cho kho nhỏ — RAG đổi phức tạp pipeline lấy scale + ACL + freshness; kết hợp (RAG chọn, context đọc) là điểm cân bằng 2026.
- **S4:** Retrieval với ACL là **thanh tra quyền mở rộng** — dùng lại hạ tầng authZ có sẵn (→10.3: cùng policy engine) thay vì phát minh bảng quyền riêng cho RAG (hai bảng quyền = chỗ lọt);
- **S5:** Agent (→12.4) làm context turnover nhanh (mỗi bước gọi tool mới dữ liệu) — context engineering trở thành **bài quản lý bộ nhớ có giới hạn**: tóm tắt cuộn (rolling summary), tool kết quả nén, thứ tự ưu tiên — kỹ thuật sẽ định hình hệ agentic nhiều hơn model;
- **S6:** Khi "AI trả lời sai/bịa": tách ba lớp §2.6 bằng log (đoạn nào được lấy? câu trả lời bám đoạn chưa?) — 80% trường hợp retrieval là thủ phạm; sửa model trước retrieval là thuốc sai bệnh.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| AI bịa khi có dữ liệu | Retrieval miss (recall thấp) | đo recall@k golden | §2.2 |
| Đọc tài liệu lân phòng (I-068) | ACL không filter lúc retrieve | metadata + filter trước prompt | §2.3 |
| Sai tên mã/số hiệu | Thiếu BM25 (chỉ vector) | hybrid search | §2.2 |
| "Quên" tool giữa chừng | Context tràn cắt nhầm | ưu tiên cắt + nén | §2.5 |
| Đắt vô lý | Nhét cả kho mỗi lần | RAG chọn + context đọc | §2.4 |
| Câu trả lời đúng đoạn nhưng sai ý | Rerank thiếu/tệ | rerank + faithfulness check | §2.2 |

---

## 6. Cách đo

```bash
# Golden set retrieval (một buổi dựng, dùng mãi):
#   50 câu hỏi + đoạn-đúng-đánh-dấu. Chạy pipeline:
#   recall@5 = (số câu có đúng đoạn trong top5) / 50
#   → dưới 0,7: sửa chunking/hybrid trước khi đụng model

# Faithfulness spot-check: lấy 10 câu trả lời production tuần này,
#   cho judge chấm "câu này bám đoạn nào?" — không bám = bịa (dù nghe đắn đo)
```

Nguyên tắc: **mọi cải thiện RAG phải qua golden set** — không có nó, mỗi thay đổi là mồi xúc xắc trên cảm giác.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay RAG tự dựng:** dịch vụ retrieval managed (vector + hybrid + filter — khóa nhẹ, nhanh ra mắt); **thay chunking thủ công:** parse cấu trúc (heading/paragraph) + layout-aware cho PDF — chất lượng chunk là nửa trận; **thay vector DB riêng:** extension lên DB có sẵn (pgvector-style →5.10) khi quy mô vừa — ít hệ phải nuôi.

Năm thấu kính:
- **Kinh tế:** Mỗi câu hỏi RAG trả tiền theo token context — **retrieval chọn lọc là tiết kiệm lớn nhất** (bớt 50% context thừa = giảm 50% hóa đơn gen_AI — 12.6); chất lượng retrieval là chi phí vận hành, không chỉ chất lượng.
- **Vận hành:** Kho tài liệu đổi liên tục → pipeline ingest (re-index theo thay đổi — CDC cho tài liệu, →5.15 tư duy) + version chỉ mục (rollback được khi index xấu);
- **An ninh:** Chunk là **đơn vị phân quyền** (không phải tài liệu — nửa tài liệu vẫn lộ nửa thông tin); metadata ACL viết lúc ingest và **kiểm tra penetration-style** định kỳ (→10.4 lab SSRF cùng kỷ luật);
- **Lịch sử:** Thư viện + thủ thư (thế kỷ trước) → search engine (→5.6) → RAG: mỗi thế hệ thêm lớp "hiểu ngữ nghĩa" vào việc tìm; rerank là "thủ thư chấm lại kệ sách" — nghề cũ quay lại tên mới;
- **Người dùng:** Người dùng chỉ hỏi một câu: "con AI này có đọc đúng tài liệu của tôi không?" — recall + ACL + trích nguồn là ba từ kỹ thuật đứng sau câu đó; một trong ba hỏng thì niềm tan.

---

## 8. Đọc tiếp & bài tập

- Vector/ANN: **5.10** · Search engine hybrid: **5.6** · Agent dùng context: **12.4** · Evals/judge: **12.5** · Token tiền: **12.6** · Playbook AI-native: **13.5**
- **Bài tập 1:** Dựng golden set 50 câu hỏi (nửa buổi) cho kho của bạn, đo recall@5 hôm nay. Con số đó là baseline của mọi cải thiện RAG sắp tới — không có nó, mọi "tốt hơn" là chuyện kể;
- **Bài tập 2:** Kiểm ACL-style: dùng tài khoản test quyền hạn hẹp, hỏi agent về nội dung ngoài quyền. Trả lời được nội dung = I-068 sống trong hệ bạn — sửa filter trước prompt (§2.3);
- **Bài tập 3:** Log context token trung bình mỗi loại câu hỏi trong một tuần; tìm loại câu hỏi "phình" nhất — nén/chunk lại đúng loại đó (một PR nhỏ, hóa đơn giảm thấy được).

