# 1.5 — GPU & accelerator: SIMT, roofline, tensor core

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.2 (cache) · 1.3 (HBM).

**Sợi chỉ đỏ:** *Có việc tính toán mà CPU không gánh nổi — khi nào GPU vào cuộc, và cái gì làm nó đắt?* — trả lời: khi công việc là hàng chục nghìn phép tính giống hệt nhau — gợi ý món, embedding, sinh token — GPU vào cuộc bằng SIMT; và cái làm nó đắt không phải lõi tính, mà là bộ nhớ và băng thông đi kèm. Câu hỏi để lại cho chương sau: *GPU, card mạng, ổ đĩa nói chuyện với CPU và nhau qua đâu — vì sao 'cắm đúng khe' là quyết định hiệu năng?*

**Thuật ngữ sẽ gặp:** *SIMT* — hàng vạn thread chạy cùng một chương trình trên dữ liệu khác nhau; *roofline* — hình vẽ cho biết bài toán bị chặn bởi tính toán hay bộ nhớ; *arithmetic intensity* — số phép tính trên mỗi byte đọc; *tensor core* — khối cứng chuyên nhân ma trận, ruột của AI hiện đại; *thang precision (FP16/FP8)* — đổi số bit cho tốc và rẻ, trả bằng độ chính xác; *MIG* — chia một GPU vật lý thành mấy GPU logic.

**Ví dụ mở đầu:** CEO xem demo gợi ý món chạy GPU rồi hỏi "mua tám cái được không?". Câu hỏi đúng không phải "được không" mà là "bài toán của mình nằm bên nào của roofline": nếu memory-bound thì thêm GPU giúp ít, thêm băng thông mới giúp. Chương này cho một hình vẽ để trả lời câu hỏi tiền bằng số.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Workload này có đáng đưa lên GPU không | Nó compute-bound và song song được không? Roofline của nó nằm đâu? |
| 2 | Chạy shared serving hay dedicated | Tôi cần tối ưu TTFT (throughput) hay throughput tổng (chi phí/token)? |
| 3 | Precision nào (FP32/FP16/BF16/FP8/FP4) | Mất bao nhiêu chất lượng khi đổi lấy 2–16× thông lượng? |
| 4 | Cắt GPU thế nào giữa các tenant (MIG / time-slicing / dedicated) | Tôi cần isolate cứng hay chỉ cần chia sẻ công bằng? |

---

## 2. Cơ chế

### 2.1 SIMT: hàng vạn thread, một chương trình

CPU tối ưu cho **một luồng nhanh** (out-of-order, cache lớn, đoán nhánh); GPU tối ưu cho **hàng vạn luồng chậm** nhưng đồng loạt. Mô hình SIMT: thread nhóm theo **warp** (32 thread NVIDIA / wavefront 64 AMD) — cả warp chạy **cùng một lệnh** trên dữ liệu khác nhau. Phân kì (divergence) — nhánh khác nhau trong warp — làm hai nhánh chạy nối tiếp nhau: đây là "GIL của GPU" (khác quy mô: 2× chứ không phải vô hạn, nhưng cùng bản chất serialization).

Ba hệ quả thiết kế:
1. **Độ trễ đơn lẻ không phải mục tiêu; băng thông + concurrency mới là.** GPU che độ trễ bằng cách chuyển sang warp khác khi warp này chờ nhớ (chỉ cần đủ warp để che — occupancy).
2. **Bộ nhớ hợp nhất (coalescing):** 32 thread đọc 32 địa chỉ liền kề = 1 transaction; đọc rải rác = 32 transaction. Cùng logic dòng cache ở 1.2, ở quy mô lớn hơn.
3. **CPU-side là sếp giao việc:** nếu CPU không kịp nạp batch (data pipeline), GPU ngồi không — và `nvidia-smi` **vẫn báo 100%** (xem §5).

### 2.2 Roofline: một hình nói hết kiến trúc

```
FLOPS đạt được
     ▲          ● tensor-core đỉnh (compute-bound)
     │        ╱
     │      ╱   ← trần FLOPS của GPU
     │    ╱ ●  ridge point
     │  ╱ ╱
     │╱ ╱ ● steeper path — memory-bound
     └────────────────▶ Arithmetic intensity (FLOP/byte)
```

Mọi kernel nằm dưới đường gấp khúc: điểm gãy (**ridge point**) chia "thiếu băng thông" (trái) và "thiếu FLOPS" (phải). Việc của bạn trước khi tối ưu bất cứ gì: đo **arithmetic intensity** của kernel — nếu nó nằm bên trái ridge point thì thêm tensor core vô nghĩa, phải giảm chuyển bộ nhớ (fusion, tiling, quantize).

### 2.3 Prefill vs decode: hai chế độ trái ngược của LLM serving

- **Prefill** (xử lý prompt): ma trận-ma trận, **compute-bound** — GPU gần trần FLOPS.
- **Decode** (sinh token từng cái): ma trận-vector, **memory-bound** — mỗi token phải đọc **toàn bộ trọng số**; FLOPS gần như ngồi không. Băng thông HBM quyết định tốc độ decode (token/s ≈ băng thông / kích thước mô hình).

Đây là lý do tồn tại **paged KV cache** (vLLM) và **chained/continuous batching** (→12.2): chúng tối ưu việc chia sẻ băng thông giữa các request; và là lý do **FP8/FP4 quantization** tăng tốc decode gần đúng tuyến tính — mỗi token đọc ít byte hơn.

### 2.4 Tensor core & precision ladder

Đơn vị tính ma trận chuyên dụng (NVIDIA từ Volta 2017). Bậc thang precision (mỗi bậc ~2×):
FP32 → TF32 → FP16/BF16 → FP8 → **FP4/NVFP4** (Blackwell). Sản phẩm: B200 ~2,2 PFLOPS NVFP4 dense (V); rack VR200 NVL72 ~50 PFLOPS NVFP4 inference lý thuyết với 288 GB HBM4 @ ~22 TB/s (V). Bậc để nhớ cho reasoning model: **mô hình lớn → decode gắn chặt băng thông HBM; mô hình nhỏ + quantize → gắn FLOPS tensor core.**

Precision nào dùng được quyết định bằng **đo chất lượng trên task của bạn** (loss/eval), không phải theo mode mặc định của framework — FP8 với mô hình nhỏ có khi tệ, FP4 với reasoning + KV cache FP8 là vùng đang chạy đua 2026.

### 2.5 Chia GPU: MIG, time-slicing, dedicated

| Cách | Isolation | Chi phí | Khi nào |
|---|---|---|---|
| Dedicated | cứng nhất | lãng phí khi util thấp | dịch vụ quan trọng, model lớn |
| **MIG** (chia 7 instance vật lý) | cứng (bộ nhớ, SM, L2, băng thông) | không live-resize được | multi-tenant inference, SLA rõ |
| Time-slicing (MPS/context switch) | mềm — noise neighbor | context-switch overhead | nội bộ, dev/test |
| Batch multi-tenant trong 1 process (serving engine) | theo engine | phức tạp ops | chi phí/token thấp nhất (→12.2) |

Quy tắc: **tenant ngoài công ty → MIG hoặc dedicated; tenant nội bộ → serving engine gộp batch.**

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Warp / wavefront | 32 / 64 thread | V | NVIDIA / AMD |
| Băng thông HBM3e (B200) | ~8 TB/s · 192 GB | V | |
| Băng thông HBM4 (VR200) | ~22 TB/s · 288 GB | V | NVL72 tổng; per-GPU tương ứng |
| FP4 dense (B200) | ~2,2 PFLOPS | V | dense; sparse gấp đôi marketing |
| MIG instances | tối đa 7/GPU | V | Hopper/Blackwell |
| MFU training tốt | 35–45% | I | trên nền FLOPS lý thuyết |
| NVLink5 / NVLink6 | 1,8 TB/s / 260 TB/s rack | V | →1.6 |

---

## 4. Suy luận kiến trúc

- **S1:** GPU không làm cho thuật toán tuần tự nhanh hơn; nó làm cho **song song** khả thi. Ràng buộc thật là cấu trúc bài toán (arithmetic intensity), không phải tiền.
- **S2:** Tham số trụ: MFU, token/s/GPU, băng thông HBM sử dụng, tỉ lệ GPU idle vì thiếu batch.
- **S3:** Quantization đổi chất lượng lấy chi phí; MIG đổi hiệu suất trung bình lấy isolation; disaggregated serving (prefill/decode tách máy) đổi độ phức tạp ops lấy throughput — mỗi lựa chọn đều phải đo lại trên workload thật.
- **S4:** Tăng trưởng băng thông HBM (~2×/2–3 năm) và FLOPS (~2×/năm) lệch nhau → **decode ngày càng rẻ tương đối**, prefill và KV-cache truyền tin (→12.2) trở thành cổ chai mới — kiến trúc đang dịch chuyển theo đúng cạnh lệch đó.
- **S5:** Trong cụm AI, **mạng liên-GPU (NVLink/IB)** phình nhanh hơn tính toán đơn thuần; phần "không phải GPU" của cụm (mạng, điện, làm mát →1.10) quyết định p99 của bước collective (all-reduce).
- **S6:** Câu hỏi lùi một bậc: bài toán có cần GPU không? Rất nhiều "AI feature" là embedding + lookup — chạy tốt trên CPU (→1.2) với chi phí/latency tốt hơn.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| GPU 100% nhưng token/s thấp | CPU-side/DataPipeline đói GPU; hoặc kernel memory-bound (bình thường với decode) | DCGM `SM_ACTIVE` vs `TENSOR_ACTIVE`; profile | §2.1, §2.2 |
| TTFT cao dù GPU "rảnh" | Queueing — batching config sai; waiting queue dài | vLLM metrics: num_waiting vs num_running | →12.2 |
| Throughput tăng thêm GPU thì giảm | Thao tác collective chiếm tỉ trọng (topo chậm) | Nsight Systems: thời gian NCCL all-reduce | →1.6 |
| Chất lượng output tụt sau quantize | FP8/FP4 không hợp model/task | eval A/B trên task thật trước khi ship | §2.4 |
| Tenant này làm tenant kia chậm | Time-slicing không isolate | chuyển MIG; đo lại | §2.5 |
| GPU "mất" giữa chừng / treo ECC | Bộ nhớ lỗi tích luỹ, driver reset | DCGM/XID log; `nvidia-smi -q` ECC | →1.3 |

---

## 6. Cách đo

```bash
nvidia-smi dmon -s ucm           # util, bộ nhớ, clock — mỗi giây
nvidia-smi --query-gpu=utilization.gpu,utilization.memory,power.draw --format=csv -l 1

# Thước thật (không phải util%):
dcgm diag -r 1                   # health check đầy đủ
# trong serving engine: num_waiting, token/s, KV cache usage — theo engine

nsys profile ./app               # timeline CPU↔GPU: gap = đói
ncu --set roofline ./kernel      # per-kernel: FLOPS vs bytes → roofline vị trí
```

Nguyên tắc: **util% nói dối, roofline không.** "GPU 100%" nghĩa là có cái gì đó đang chạy, không nghĩa là có ích. Luôn hỏi: tensor active? memory bandwidth bao nhiêu %? bao nhiêu token ra?

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay GPU đắt cho inference:** (a) CPU serving cho model nhỏ/quantize (llama.cpp — đủ tốt ở Q4 cho nhiều use case nội bộ); (b) API bên ngoài khi volume thấp (đổi vận hành đơn giản lấy chi phí biên); (c) cache kết quả/prompt (→5.4) — mô hình đắt nhất là mô hình chạy hai lần cho cùng câu hỏi. Với training quy mô nhỏ: thuê theo giờ; chỉ mua khi utilization đo được > ~40% (I).

Năm thấu kính:
- **Kinh tế:** Đơn vị đúng là **chi phí/token hoặc chi phí/giờ-task**, không phải giá GPU. Mô hình to + GPU to + utilized thấp thường thua mô hình nhỏ + quantize + utilized cao.
- **Vận hành:** Cụm GPU = điện + làm mát + driver + XID reset + topology; monitoring XID/ECC/temperature là hygiene tối thiểu (DCGM → Prometheus).
- **An ninh:** Multi-tenant trên GPU còn non trẻ: side-channel giữa tenant, model extraction qua API — MIG isolate hiệu năng, **không** tự động isolate an ninh dữ liệu; Zero Trust vẫn phải áp ở tầng serving (→10.4).
- **Lịch sử:** Mỗi thế hệ GPU đổi "giao diện tối ưu": CUDA cores → tensor cores → transformer engine; code nhanh hôm nay là code chậm 3 năm nữa nếu viết sát kim loại. Viết theo abstraction (Triton, torch.compile) trừ khi đo ra là cần.
- **Người dùng:** Người dùng thấy token chảy ra. TTFT là cảm giác "nó nghĩ lâu", decode speed là cảm giác "nó gõ chậm" (→12.2). Cả hai đều là quyết định của bạn ở chương này, không phải "do AI thế".

---

## 8. Đọc tiếp & bài tập

- Serving LLM chi tiết (batching, KV cache, disaggregation): **12.2** · Mạng liên-GPU: **1.6** · Điện/nhiệt rack 100kW+: **1.10** · Quantization & nén model: **12.3**
- **Bài tập 1:** Viết kernel nhân ma trận naïve; đo arithmetic intensity bằng `ncu`; xác định nó nằm bên nào ridge point. Tối ưu coalescing + tiling; vẽ lại.
- **Bài tập 2:** Đo chi phí/token của bạn hôm nay (API hoặc self-host). Tìm xem bao nhiêu % token là cache-hit được. Đó thường là chỗ tiết kiệm lớn nhất, không phải GPU mới.
- **Bài tập 3:** Chạy 1 model FP16 rồi FP8 trên task đánh giá thật của bạn; so chất lượng. Nếu lệch < 1% trên metric bạn quan tâm — mọi lập luận về "cần GPU x2" vừa mất căn cứ.
