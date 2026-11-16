# MÔN 3 — QUY MÔ & BIÊN GIỚI (4 tín)

### SYS103 · 45 tiết lý thuyết + 45 tiết thực hành · học kỳ 3 (tự chọn) · sách: SYSTEMS ATLAS SA-2028.1, cụm **8.4–8.8 + P11 + P12 + P13 + 18 chương P14**

> **Một câu mô tả môn:** khi hệ thống vượt qua ngưỡng một máy và một đội — vận hành theo SLO, hạ tầng phục vụ AI thực chiến, chọn đúng kiến trúc tải theo kịch bản, và hiểu giới hạn vật lý-pháp lý-mật mã ở biên giới ngành.
> **Điều kiện tiên quyết:** SYS101 và SYS102 (bao gồm `5.5, 5.14–5.16, 6.3, 6.7, 7.6, 8.2, 8.3, 9.3–9.7, 10.2, 10.3, 10.5, 10.7, 10.8`). Toàn bộ 10 chương P14 còn lại (`14.2.2, 14.6.1–14.6.3, 14.7.1–14.7.3, 14.9.1–14.9.3`) nằm trong Phụ lục "Đọc khi cần" của sách.

---

## 1. Chuẩn đầu ra (CLO) — đo được trên hệ quy mô & AI

| # | Sinh viên **làm được** | Kiểm bằng |
|---|---|---|
| CLO1 | Thiết kế cơ chế chịu lỗi, cell-based isolation và **error budget / SLO thực thi được** (không báo động giả) | Bài kiểm 1 (tuần 4) + Lab L11 |
| CLO2 | Đo và giải trình **lượng tử hoá serving LLM** (TTFT/TPS, VRAM, chi phí/1M token) cùng bộ eval + guardrail | Lab L12 |
| CLO3 | Soạn **playbook kiến trúc & sizing có số** cho một lớp tải thật (OLTP/Realtime/Ingest/Lakehouse/AI/Global/SaaS) | Bài tập nhóm + Lab L13 |
| CLO4 | Đọc và đặt ngưỡng cho **biên giới hạ tầng** (chiplet/HBM, PUE/carbon datacenter, PQC/ZK/FHE, timing jitter) mà không bị số benchmark tiếp thị dắt | Lab L14 + Thi cuối |

## 2. Lịch 15 tuần (45 chương không chồng lấn SYS101/SYS102)

| Tuần | Lý thuyết (chương sách) | Thực hành | Nộp |
|---|---|---|---|
| 1 | 8.4 Phân vùng & nhân bản tầng hệ thống · 8.5 Mẫu chịu lỗi & kiểm soát tải · 8.6 Monolith, Microservices, DDD, CQRS & Event | Lab mô phỏng backpressure & load shedding | Sơ đồ partition + ngưỡng shed |
| 2 | 8.7 Đa vùng, Cell-Based Architecture & DR · 8.8 Tiến hoá không gián đoạn (Expand-Contract, Strangler) · 11.1 SLI, SLO, SLA & Error Budget | Lab tính blast radius theo cell & lập bảng error budget | Bảng RPO/RTO + chính sách SLO |
| 3 | 11.2 OpenTelemetry & 4 tín hiệu · 11.3 Capacity Planning & Chaos Engineering · 11.4 Chỉ huy Sự cố & Postmortem | **Lab L11**: Prometheus, p99 và Alert tự bắn | Dashboard p99 + 1 alert + postmortem |
| 4 | 11.5 Kinh tế học kỹ thuật & FinOps · 11.6 Kiến trúc Tổ chức (Conway, Team Topologies, ADR/RFC) · 11.7 Vành liên ngành · 11.8 Lộ trình 24+ Lab | Lab phân tích unit-economics & thẩm định điều khoản mua sắm | **Bài kiểm 1** (CLO1) |
| 5 | 12.1 5 giả định cổ điển bị AI phá vỡ · 12.2 Giải phẫu LLM Inference Serving (vLLM/SGLang/Dynamo) · 12.3 RAG & Context Engineering | **Lab L12**: Serving LLM ở hai mức quant — đo latency & chi phí | Bảng TTFT/TPOT/TPS + cost/1M token |
| 6 | 12.4 Agentic Systems & MCP · 12.5 Evals, quan sát `gen_ai` & Guardrails · 12.6 AI FinOps, Model Routing & AI Gateway | Lab chạy bộ eval & đo tỷ lệ chặn guardrail / định tuyến tier | Báo cáo eval + router rule |
| 7 | 12.7 Chuỗi cung ứng Model, LoRA & Pháp lý AI · 13.1 Playbook: OLTP, Thanh toán & Sổ cái · 13.2 Playbook: Realtime, Chat & Cộng tác | Lab kiểm tra sổ cái kép + ước lượng fanout realtime | **Bài tập nhóm playbook** (tuần 7) |
| 8 | 13.3 Playbook: Ingest, Telemetry & Stream · 13.4 Playbook: Analytics & Open Lakehouse · 13.5 Playbook: AI-Native, RAG & Multi-Agent | **Lab L13**: Chọn một lớp tải — sơ đồ, sizing và bảng sự cố | **ADR quy mô / AI** (tuần 8) |
| 9 | 13.6 Playbook: Toàn cầu, Offline-First & Edge · 13.7 Playbook: B2B Multi-Tenant SaaS | Lab cô lập noisy-neighbor & tính độ trễ edge toàn cầu | Bảng tenant isolation + SLA |
| 10 | 14.1.1 Bán dẫn I (CMOS/Lithography) · 14.1.2 Bán dẫn II (Yield/Chiplets/CoWoS) · 14.1.3 Bán dẫn III (SRAM/DRAM/HBM) | Bài tập roofline: tính điểm nghẽn HBM bandwidth vs FLOPs | Bảng trần phần cứng GPU/HBM |
| 11 | 14.2.1 RF I: Link Budget & MIMO · 14.3.1 Datacenter I: Nhiệt, Làm mát & Cấp điện · 14.3.2 Datacenter II: PUE, Carbon & Failure Domain | Lab tính PUE, công suất rack AI & link budget vô tuyến | Hồ sơ capacity & failure domain |
| 12 | 14.4.1 ML I: Objective & Kiến trúc · 14.4.2 ML II: Scaling & Song song · 14.4.3 ML III: Đánh giá, Lượng tử hoá & Serving | Lab tính bộ nhớ DP/TP/PP và tác động quant lên perplexity | Ma trận VRAM + ngân sách train/serve |
| 13 | 14.5.1 HPC I: Phân rã, MPI & Interconnect · 14.5.2 HPC II: IEEE 754 & Tái lập · 14.8.1 Chuẩn I: RFC & Governance · 14.8.2 Chuẩn II: Compatibility & Versioning | **Lab L14**: Vòng 100 Hz đo jitter và Reproducible Build | Phân tích p99.9 jitter + SHA-256 build |
| 14 | 14.10.1 Mật mã I: Primitives & Lattices · 14.10.2 Mật mã II: PQC (FIPS 203/204/205) & Constant-time · 14.10.3 Mật mã III: ZK, MPC, FHE | Lab đo chi phí PQC handshake & đối chiếu ngưỡng khả thi ZK/FHE | Bảng chọn nguyên thuỷ mật mã |
| 15 | 14.11.1 Side-channel I: Timing, Speculation & Rowhammer · 14.11.2 Side-channel II: Mitigation, Residual Risk & Isolation | Ôn tổng hợp 9 chương `★` + **Thi thực hành / Đồ án cuối kỳ** | **Thi cuối** (CLO4) |

**Chín chương bắt buộc đọc kỹ (★):** 8.4 · 8.5 · 8.7 · 11.1 · 11.5 · 12.2 · 12.5 · 13.1 · 14.10.2.

---

## 3. Đánh giá

| Thành phần | Trọng số | Hình thức |
|---|---|---|
| Bài kiểm 1 (tuần 4) | 10% | Thiết kế SLO, error budget & phản biện phân vùng tổ chức (Conway) |
| Chuỗi Lab L11–L14 | 30% | Đo đủ Prometheus alert, LLM quant TTFT/TPS, sizing playbook, 100 Hz jitter |
| Bài tập nhóm playbook + ADR (tuần 7–8) | 25% | 1 playbook đầy đủ 7 trục + bảng sự cố + phương án bị loại |
| Thi cuối / bảo vệ đồ án biên giới | 35% | 3 bài tính (finops/VRAM/PUE) + 2 câu phân tích trade-off + 1 đánh giá rủi ro mật mã/phần cứng |

---

## 4. Học liệu và lưu ý giảng dạy

- **Sách:** `SYSTEMS-ATLAS-LEARNER-SA-2028.1.pdf` (Tập 3 & Tập 4 phân phần trong `volumes/`), `P15-02-Q08/11/12/13/14`, `P15-02-QA` (20 câu nâng cao cho cụm 8–14), lab `L11–L14`, lời giải `S11–S14` *(cụm P8 từ `8.4–8.8` nối tiếp `L08/S08` đã học ở `SYS102`)*.
- **Thực hành không cần GPU đắt tiền:** Lab L12 và phần định cỡ ML/HPC cung cấp số đo tham chiếu cho phần chạy CPU/4-bit local + bảng tính analytical để lớp học đại học không bị kẹt chi phí phần cứng.
