# 12.2 — Giải phẫu LLM Inference Serving (vLLM/SGLang/Dynamo)

> **Tầng:** AI · **Quyển III** · **Trục đọc:** nền AI · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số) · **Đã verify 30/10: vLLM v0.32.0, SGLang v0.5.22, Dynamo 1.5.0**
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 11.2 (SLO, telemetry) · 1.5 (GPU).

**Sợi chỉ đỏ:** *Đã chấp nhận không tất định — serving LLM: TTFT, KV cache, batch, GPU tính thế nào?* — trả lời: serving LLM — mỗi request hai pha prefill và decode với đặc tính đối nghịch; continuous batching và PagedAttention là nền của vLLM; disaggregation tách hai pha hẳn sang máy riêng; quantization là bảng đổi chất lấy tốc độ; và SLO serving là ba con số chứ không phải một. Câu hỏi để lại cho chương sau: *Model không biết menu tuần này — RAG đưa tri thức vào ngữ cảnh thế nào cho tin được?*

**Thuật ngữ sẽ gặp:** *prefill/decode* — đọc prompt (kẹt compute) và sinh token từng chiếc (kẹt băng thông): hai pha đối nghịch; *TTFT* — thời gian tới token đầu: khách thấy "đang gõ" nhanh cỡ nào; *TPOT* — thời gian mỗi token tiếp theo: chữ tuôn nhanh cỡ nào: hai SLO, hai bệnh, hai thuốc; *continuous batching* — hàng vào ra liên tục theo token: GPU hết ngồi chờ cả mẻ cứng; *PagedAttention* — KV cache chia trang như bộ nhớ ảo: hết phân mảnh; *quantization* — FP8, INT4: đổi chút chất lấy giá và tốc độ: bảng giá rõ.

**Ví dụ mở đầu:** p99 chatbot DM: khách chờ nhiều giây mới thấy chữ đầu — nhưng đã thấy thì tuôn nhanh: TTFT xấu, TPOT tốt. Continuous batching kéo utilization GPU lên; PagedAttention hết phân mảnh KV cache. Chương này đọc serving như đọc một cluster bình thường: Quyển II áp nguyên, chỉ thêm ba con số SLO.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Serving engine: vLLM / SGLang / TensorRT-LLM / Dynamo disaggregated | Ai chạy model của tôi — và tối ưu cho TTFT hay throughput? |
| 2 | Batching + prefix cache: continuous batching, RadixAttention | Cùng system prompt hàng nghìn lần — tôi cache chưa? |
| 3 | Quantization: FP8 / NVFP4 / AWQ — đổi chính xác lấy gì | Chất lượng đầu ra tôi chấp nhận giảm bao nhiêu % cho giá ×1/n? |
| 4 | Prefill/decode tách hay chung; đặt serving ở đâu (cloud/own GPU) | Đỉnh TTFT hay đỉnh throughput — và dữ liệu được phép đi đâu? |

---

## 2. Cơ chế

### 2.1 Hai pha của mỗi request — chìa khóa hiểu mọi thứ

```
PREFILL (đọc prompt):   song song — dồn FLOPS, quyết định TTFT (chữ đầu tới sau bao lâu)
DECODE (sinh token):    tuần tự — mỗi token đọc toàn bộ trọng số, memory-bound
```
Cùng một GPU, hai pha **đói tài nguyên khác nhau** — gộp chung (pai chung request) dẫn tới "phanh ga cùng lúc": prefill dài làm TTFT người khác tăng (chờ); decode dài làm GPU "rảnh CPU" nhưng chậm (I-066). Mọi quyết định serving về cơ bản là **phân pha và xếp hàng** hai việc này.

### 2.2 Continuous batching & PagedAttention — nền của vLLM

- **Batching tĩnh cũ:** gom 32 request, chờ chậm nhất — GPU lãng khi kẻ ngắn rời;
- **Continuous batching:** request vào/ra **liên tục** theo từng bước token — throughput tăng nhiều lần (đây là lý do vLLM thắng ở giai đoạn 2023);
- **PagedAttention:** KV-cache chia trang như OS paging (→2.2 họ hàng khái niệm!) — hết phân mảnh bộ nhớ KV, chạy được batch lớn hơn;
- **Prefix cache / RadixAttention (SGLang):** phần đầu prompt giống nhau (system + RAG header) → KV cache **dùng lại được** — prefix dài + lặp cao (agent gọi vòng — 12.4) tiết kiệm rõ rệt. Quy tắc: **system prompt đặt đầu, phần đổi đặt cuối** (cache hit theo prefix).

### 2.3 Disaggregation (Dynamo) — tách prefill/decode hẳn ra máy riêng

Prefill ăn GPU mạnh (compute), decode ăn băng thông HBM + có thể chạy máy "mỏng" hơn — **P/D disaggregation** (NVIDIA Dynamo là bộ orchestrator cho kiến trúc này): ra quyết định đặt pha khác máy, KV chuyển qua mạng nhanh (NVLink/IB). Hợp: cluster lớn, yêu cầu TTFT nghiêm ngặt (trò chuyện), model lớn đồng thời decode dài. Chưa hợp (chi phí phức tạp mạng + vận hành): cluster nhỏ — continuous batching + prefix cache đủ.

### 2.4 Quantization — bảng giá đổi

| Mức | Ý nghĩa | Đổi bằng |
|---|---|---|
| BF16 (gốc) | tham chiếu | — |
| FP8 | nửa | rủi ro chất lượng nhỏ (đa số workload OK), được GPU thế hệ mới hỗ trợ native |
| INT4/AWQ/GPTQ | ~1/4 | rớt chất lượng thấy được ở task khó; model nhỏ + INT4 = dùng khi cần rẻ/tươi |
| NVFP4 | thế hệ mới cho phần cứng mới | đang giai đoạn sớm — đo kỹ eval trước khi tin |

Quy tắc quyết định (không mặc định): **đo eval chất lượng (→12.5) trước/sau quantize trên golden set của chính bạn** — giảm 1–3% điểm ở task quan trọng có thể chấp (hoặc không); đừng lấy benchmark chung làm quyết định cuối.

### 2.5 SLO serving — ba con số, không phải một

- **TTFT** (time-to-first-token): cảm giác "máy nghe mình" — p95 mục tiêu theo UX (chat ~1 s);
- **ITL/TPOT** (inter-token latency): cảm giác "đang gõ" — ~30–80 ms/token cho cảm giác mượt như người đánh máy nhanh;
- **Throughput (token/s tổng)**: chi phí — quyết định hóa đơn GPU.
Ba con số **đánh nhau**: batching to tăng throughput nhưng tăng TTFT (chờ gom) — chọn điểm cân bằng theo sản phẩm (chat tối ưu TTFT/ITL; batch phân tích tối ưu throughput, TTFT vô nghĩa). Đây là PACELC (→8.1) phiên bản AI: **không có cả ba**.

### 2.6 Vận hành như một cluster bình thường (Quyển II áp nguyên)

Serving AI vẫn là hệ phân tán: **autoscale theo độ dài hàng chờ** (queue depth của engine — KEDA-style →9.2), **chịu lỗi** (engine chết → request retry idempotent; model là state lớn — load chậm, canary cẩn thận), **quan sát** (span gen_ai: token, TTFT, cache hit — →11.2/12.5), **tách phiên bản model như API version** (model tag trong trace; rollback model = đổi tag — 12.7). GPU đắt: **thống kê dùng theo giờ** (đêm vắng → batch job giá rẻ chạy đêm — spot/batch →11.5).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| vLLM / SGLang | v0.32.0 (18/10) / v0.5.22 (19/10) | V | versions.csv |
| NVIDIA Dynamo | 1.5.0 (21/09) — P/D disaggregated | V | versions.csv |
| Continuous batching | throughput × nhiều lần so tĩnh | I | paper vLLM |
| TTFT chat mục tiêu | ~1 s p95 | P | |
| ITL mượt | 30–80 ms/token | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Inference serving là **bài xếp hàng hai pha** (prefill/decode) trên tài nguyên không đối xứng — mọi tối ưu thật sự là xếp hàng/cache/tách pha; "mua thêm GPU" là trả lời của người chưa vẽ sơ đồ hai pha.
- **S2:** Tham số trụ: TTFT p95, ITL p95, token/s/GPU, prefix cache hit rate, queue depth theo giờ, chi phí/triệu token (đi kèm 12.6).
- **S3:** Quantization đổi chất lượng lấy giá — quyết định bằng **eval trên dữ liệu mình**, không benchmark chung; kèm đường lùi (đổi lại BF16 bằng config, không cài lại hạ tầng).
- **S4:** Prefix cache là **cache-control của AI** (→6.5 cùng toán): khoá là prefix prompt, hit = bỏ prefill — thiết kế prompt theo cấu trúc cố định-đầu/thay-đổi-cuối là "cache key design" của thế hệ mới.
- **S5:** Suy đoán/thinking token (reasoning model) đổi bài toán serving: output dài = decode dài = tiền (I-067 một mặt) — nhưng **cắt bớt thinking** bằng cấu hình là đòn tiết kiệm lớn nhất nhiều hệ (→12.6 cascading).
- **S6:** Khi "TTFT cao nhưng GPU rảnh" (I-066): tra theo thứ tự — hàng chờ gom batch (batch size nhỏ/chờ), prefix cache miss (prompt lặp không hit — cấu trúc sai), prefill của người khác chặn (chưa tách P/D), **không** phải "GPU yếu" — bảng quyết định 4 dòng này định xong chiều điều tra.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| TTFT cao, GPU rảnh (I-066) | Queue gom batch / cache miss / prefill chặn | 3 hướng §4-S6 | §2.5 |
| Throughput thấp | Batching tĩnh / KV phân mảnh | continuous batching + PagedAttention | §2.2 |
| Chất lượng rớt sau quantize | INT4 không chịu nổi task | FP8 hoặc về BF16 (đo eval) | §2.4 |
| Chat "khựng" từng đợt | ITL không đều (batch chênh) | scheduler tuning / P/D tách | §2.3 |
| Agent gọi vòng tốn tiền | Prefix không hit | cố định header + RadixAttention | §2.2 |
| Đêm GPU ngủ ngày nghẹt | Không lịch batch | batch đêm + autoscale (→9.2) | §2.6 |

---

## 6. Cách đo

```bash
# Benchmark engine thật trên chính workload của bạn (không synthetic):
#   vllm bench serve --model <m> --dataset <log-prompt-thật> ...
#   đo: TTFT p50/p95, ITL, throughput — với/ không prefix cache
#   → khác biệt cache hit là con số thuyết phục cấu trúc prompt

# Chạy production: span mỗi request (gen_ai): prompt_tokens, output_tokens,
#   ttft_ms, cache_hit — dashboard theo model × giờ (→11.2)
```

Nguyên tắc: **benchmark bằng prompt thật của mình** — prompt công khai benchmark không có độ dài/phân bố prefix giống bạn, số sai dẫn quyết định sai.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự chạy vLLM:** API managed (OpenAI/Anthropic-style — không hạ tầng, trả theo token đắt hơn khi scale, dữ liệu rời tổ chức — →12.7 pháp lý); **thay GPU đắt:** model nhỏ/Ollama-style tại chỗ cho use case nhẹ (llama.cpp v0.5.0, Ollama v0.35.0 — đã verify 30/10) — đủ cho prototype/nội bộ; **thay Dynamo:** không thay — nếu chưa tới quy mô thì chưa cần (Yagni).

Năm thấu kính:
- **Kinh tế:** Token API vs tự serve có **điểm hoà vốn** (thường khi đều đặn nhiều tỷ token/tháng hoặc dữ liệu không được rời) — tính bằng chính số mình (→12.6); "tự chạy vì ngầu" trả lãi negatif.
- **Vận hành:** Cluster GPU có runbook riêng (model load chậm — drain phải tính; SM collector/GPU metric khác CPU) — 11.8 template runbook áp nguyên;
- **An ninh:** Model + weights là tài sản (leak = mất lợi thế + pháp lý license — 12.7); prompt/kết quả là dữ liệu người dùng (log hygiene — →11.2 áp xuống, redact PII trước khi lưu).
- **Lịch sử:** Batch→continuous (2023, vLLM) → RadixAttention/prefix (2024, SGLang) → P/D disaggregation + KV chuyển máy (2025–26, Dynamo): ba bước cùng một hướng — **tận dụng lại cái đã tính** (KV của token đã đọc); giống mọi tầng cache trong atlas: page cache (2.4), CDN (6.5), query cache (5.4) — AI vừa học lại bài 30 năm.
- **Người dùng:** Người dùng cảm nhận serving qua hai khoảnh khắc: "sao lâu thế mới chữ đầu" (TTFT) và "gõ lắm bậc cà phê" (ITL) — hai con số đó là UX thật; throughput chỉ là hóa đơn của bạn.

---

## 8. Đọc tiếp & bài tập

- Tiền token: **12.6** · Evals quyết quantize: **12.5** · Agent loop dùng prefix: **12.4** · GPU scheduling K8s: **9.2** · Trace gen_ai: **11.2, 12.5**
- **Bài tập 1:** Đo TTFT/ITL p95 hiện tại (hoặc benchmark nếu chưa chạy). Viết hai con số lên dashboard cạnh SLO cũ — chúng là "p99 của thế hệ AI".
- **Bài tập 2:** Kiểm prefix cache hit rate trên workload thật (log prompt đầu/cuối). < 50% với system prompt cố định? Cấu trúc lại prompt (đầu cố định, cuối thay đổi) — thường là PR nhỏ, tiết kiệm lớn.
- **Bài tập 3:** Nếu đang quantize: chạy golden set (→12.5) BF16 vs lượng tử hoá — so điểm. Chênh > ngưỡng chấp nhận → một trong hai đường (về FP8 hoặc chấp nhận giảm giá) phải là quyết định có chữ ký, không phải mặc định.
