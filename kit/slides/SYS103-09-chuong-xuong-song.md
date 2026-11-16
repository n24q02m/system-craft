# SYS103 — Bộ Slide 09 Chương Xương Sống (★) · Môn 3: Quy mô & Biên giới

> **Ấn bản:** SA-2028.1 · **Phạm vi:** 9 chương ★ của `SYS103` (`8.4, 8.5, 8.7, 11.1, 11.5, 12.2, 12.5, 13.1, 14.10.2`) · **Khổ 16:9**

| Cụm | Chương ★ | Trọng tâm chiến lược & kỹ thuật |
|---|---|---|
| `P8` Phân tán Quy mô lớn | `8.4, 8.5, 8.7` | Sharding/Quorum `NWR`, Retry Budget/Load Shedding, Cell-Based DR |
| `P11` Vận hành & FinOps | `11.1, 11.5` | SLI/SLO, Error Budget Burn Rate, Unit Economics |
| `P12–P14` AI, Playbook & PQC | `12.2, 12.5, 13.1, 14.10.2` | vLLM PagedAttention/Dynamo, Eval Gate & Guardrails, OLTP Ledger, PQC FIPS 203/204/205 |

---

## [8.4] 1/6 — Phân Vùng & Nhân Bản Ở Tầng Hệ Thống (§0–§1)

- **Đọc trước:** `5.5` (Hash ring) · `5.16` (Công thức sizing).
- **Quyết định `D-087`–`D-088`:**
  1. **Sharding key (`D-087`):** Range vs Hash vs Consistent Hashing (+ virtual nodes); truy vấn phổ biến nhất có nằm trong 1 partition không?
  2. **Replication & Quorum (`D-088`):** `RF = 3` (trải đa AZ), đọc/ghi cân bằng theo điều kiện **`W + R > N`** hay đổi consistency lấy latency bằng `LOCAL_QUORUM` / async replica?

---

## [8.4] 2/6 — Consistent Hashing, Resharding & Replica Lag (§2)

- **Consistent Hashing (`Karger et al., 1997`):** Thêm/bớt 1 trong `N` node chỉ di chuyển trung bình **`~1/N`** dữ liệu (với virtual nodes để giảm độ lệch giữa các node vật lý).
- **Chọn sai Shard Key:** Scatter-gather buộc `1` query phải quét toàn bộ `64` shard (`p99` luôn bằng shard chậm nhất!).
- **Đọc ghi nhất quán:** Async replica lag (`ms–trăm ms`) khiến user *"vừa bấm Lưu xong F5 lại không thấy đâu"* → giải bằng read-your-own-writes routing về leader trong cửa sổ vài giây.

---

## [8.4] 3/6 — Bảng Số & Công Thức Quorum (§3)

| Thông số | Giá trị / Điều kiện | Nguồn chính | Ghi chú |
|---|---:|---|---|
| Strict quorum overlap | `W + R > N` | Vogels (CACM 2009 / Dynamo) | `N=3, W=2, R=2` đảm bảo đọc thấy bản ghi mới nhất |
| Consistent hash churn | `~1/N` dữ liệu | Karger et al. (STOC 1997) | Virtual nodes ~100–256/node cân tải |
| RF phổ biến | `3` (2 vùng / đa AZ) | `P` | Chịu mất 1–2 bản sao |

---

## [8.4] 4/6 — Hỏng Thế nào Khi Chia Shard & Nhân Bản (§5)

| Triệu chứng | Nguyên nhân | Hướng chẩn & Xử lý |
|---|---|---|
| Một node CPU 100%, node khác rảnh | Hot partition key / data skew | Đo top keys theo shard; thêm salting / tách VIP |
| Truy vấn bỗng chậm vọt | Scatter-gather chạm mọi shard | Trace số shard đụng; sửa query gắn shard key |
| Mất dữ liệu vừa commit khi failover | Async replication (`RPO > 0`) | Đổi `synchronous_commit` / `W >= 2` cho đường tiền |
| Reshard backfill làm sập prod | Backfill ăn hết IOPS / WAL | Rate-limit throttle luồng migration, tách lịch chạy |

---

## [8.4] 5/6 — Thấu Kính: Chỉ Shard Khi Thật Sự Hết Đường (§7)

- **Quy luật thực chiến (`P15-05`):** Trước khi sharding DB thủ công (hy sinh `JOIN`/`ACID`), hãy kiểm đủ 4 bước rẻ hơn nhiều: sửa N+1/index → bật PgBouncer → chuyển read reporting sang replica/OLAP → chia partitioning bảng theo ngày ngay trên 1 Postgres (`5.2`).

---

## [8.4] 6/6 — Bài Tập Kiểm Tra Đường Chuyển Shard & Lag (§8)

1. Chọn 3 bảng lớn nhất hiện tại: vẽ sơ đồ **shard key ứng viên** và liệt kê truy vấn nào buộc phải scatter-gather.
2. Audit đường đọc ngay sau ghi (profile update, tạo đơn): nếu đang đọc từ read-replica async, định rõ TTL sticky về primary.

---

## [8.5] 1/6 — Mẫu Chịu Lỗi & Kiểm Soát Tải Toàn Trình (§0–§1)

- **Đọc trước:** `3.10` (9 trạm phục vụ & retry factor) · `5.16` (headroom).
- **Ba quyết định `D-089`–`D-091`:**
  1. **Retry (`D-089`):** Chỉ retry lỗi an toàn với **Exponential Backoff + Full Jitter + Retry Budget ≤ 10%**.
  2. **Circuit Breaker & Bulkhead (`D-090`):** Cô lập dependency bệnh trước khi nó kéo sập toàn bộ worker pool (`I-051`).
  3. **Load Shedding (`D-091`):** Khi vượt ngưỡng, cứu khách đang giao dịch và **từ chối ngay tại edge (`503 + Retry-After`)**.

---

## [8.5] 2/6 — Cái Chết Theo Tầng Cấp & Tác Dụng Ngược Của Retry (§2)

- **Thác đổ dây chuyền (`I-050`):** Dịch vụ C chậm nhẹ → B timeout retry `3×` → A retry `3×` → traffic vào C nhân lên **`9×`**, giữ kẹt toàn bộ thread pool của B và A!
- **Full Jitter & Retry Budget:** Dùng ngẫu nhiên trải đều (`random(0, min(cap, base * 2^attempt))`) thay vì backoff đều nhau gây sóng đồng bộ (**thundering herd `I-052`**); giới hạn tỷ lệ retry toàn hệ `≤ 10%`.
- **Bulkhead:** Tách connection/thread pool theo từng dịch vụ đích hoặc tier khách để lỗi API phụ không nuốt hết luồng thanh toán.

---

## [8.5] 3/6 — Bảng Số Định Lượng Phòng Thủ (§3)

| Cơ chế | Ngưỡng chuẩn | Nguồn / Nhãn | Lý do |
|---|---:|---|---|
| Retry budget | `≤ 10%` lưu lượng | Google SRE / AWS Architecture | Vượt 10% sẽ tự khuếch đại outage |
| Utilization knee (Little) | `70–80%` | Little (1961) / `M/M/k` | Trên ngưỡng này độ trễ nổ phi tuyến |
| Circuit breaker OPEN | Vài chục giây | `P` | Chuyển half-open thử 1 phần nhỏ traffic |
| Edge shedding | `503 + Retry-After` | `P` | Từ chối sớm ở cửa rẻ gấp 100× chết ở DB |

---

## [8.5] 4/6 — Năm Ca Sập Dây Chuyền Kinh Điển (§5)

| Triệu chứng | Nguyên nhân | Điểm cắt |
|---|---|---|
| Tải tăng 20%, hệ sập 100% (`I-050`) | Retry storm không jitter / không budget | Giảm max retry + thêm Full Jitter + client retry token |
| Dịch vụ khuyến mãi lỗi → login chết theo (`I-051`) | Dùng chung thread/conn pool | Tách **Bulkhead** + **Circuit Breaker** FAIL-FAST |
| Đúng XX:00 giờ chẵn hệ treo | Cron / cache TTL cùng khớp giây | Trộn jitter `±15%` vào TTL & lịch job |
| RAM OOM do hàng đợi phình vô hạn | Unbounded in-memory queue | Bound queue + LIFO/CoDel timeout + `503` |

---

## [8.5] 5/6 — Hedging, Graceful Degradation & Thử Nghiệm Chaos (§7)

- **Hedging (gọi song song backup nếu quá p95):** Chỉ an toàn với lệnh đọc **idempotent** và phải chặn hedging budget `< 5%`, nếu không chính nó thành bão retry thứ hai.
- **Tắt tính năng phụ (Degradation):** Khi Primary chạm ngưỡng, tự động ngắt bảng gợi ý/thống kê để giữ sống `/checkout`.

---

## [8.5] 6/6 — Bài Tập Tự Kiểm Hàng Rào Bảo Vệ (§8)

1. Liệt kê timeout + số retry mặc định của mọi HTTP/gRPC/DB client trong codebase: tính thử nhân chuỗi ở hop thứ 3 là bao nhiêu lần traffic!
2. Đảm bảo hàng đợi job/pool quan trọng đều có **giới hạn cứng (`bounded queue`)** và metric tỷ lệ request bị từ chối.

---

## [8.7] 1/6 — Đa Vùng, Cell-Based Architecture & DR (§0–§1)

- **Đọc trước:** `8.2` (Quorum) · `8.4` (Replication đa vùng).
- **Hai quyết định `D-092`–`D-093`:**
  1. **Topology đa vùng (`D-092`):** Chọn bậc nào trong 4 bậc DR (`Backup & Restore` → `Pilot Light` → `Warm Standby` → `Active-Active`), neo đúng vào hợp đồng **RTO** & **RPO**?
  2. **Kiến trúc Cell (`D-093`):** Cắt nhỏ hệ thống thành các cell độc lập để khống chế **bán kính nổ (`Blast Radius` `I-056`)**.

---

## [8.7] 2/6 — RTO/RPO, Cell Isolation & Active-Active (§2)

- **Bẫy Active-Active ảo tưởng:** Triển khai Active-Active hai lục địa cho dữ liệu cần ghi chặt (`OLTP`) làm độ trễ mỗi giao dịch vọt lên `100–250 ms` RTT — lại dễ **xung đột dữ liệu chéo vùng** nếu không phân vùng chủ sở hữu theo từng `tenant`/`cell`.
- **Cell-Based Architecture (`AWS Builders Library`):** Toàn hệ chia thành nhiều **Cell hoàn chỉnh** phục vụ `1–10%` tập khách mỗi cell; lớp router siêu mỏng định tuyến từ ngoài cửa. Một bug cấu hình sai khi rollout theo cell chỉ chạm tối đa 1 cell!

---

## [8.7] 3/6 — Bảng Số Hợp Đồng Thảm Hoạ & Cell (§3)

| Thông số | Giá trị bậc | Nguồn / Nhãn | Ghi chú |
|---|---:|---|---|
| DNS failover TTL | `30–60 s` | `IETF RFC 1035 / 2181` | Resolver hạ tầng vẫn có thể cache nhẹ |
| Cross-region replication RTT | `50–200 ms` | Vật lý sợi quang (`1.7`) | Chi phí bắt buộc của sync quorum xa |
| Single-cell blast radius mục tiêu | `1–10%` users | AWS Cell-Based Architecture | Rollout từng cell một trước khi ra toàn cầu |

---

## [8.7] 4/6 — Hỏng Thế nào Khi Disaster Recovery Không Tập Dượt (§5)

| Triệu chứng | Nguyên nhân | Cách khắc phục |
|---|---|---|
| Failover mất 4 giờ dù tài liệu ghi "15p" | DNS/pool treo; runbook lỗi thời chưa drill | Tổ chức **DR GameDay / Drill** định kỳ quý–nửa năm |
| Chuyển qua Standby là sập tiếp | Standby provision bằng 20% năng lực Prod | Cân kích thước đủ gánh tải + thử tải standby trước |
| Hai vùng chia tách sinh trùng ID | Dùng sequence `1, 2, 3...` cục bộ | Dùng UUIDv7 / range ID tách theo `region_id` |
| Một cấu hình sai giết 100% khách (`I-056`) | Mọi khách chung 1 control/data plane lớn | Tách cell rõ ràng, canary từng cell |

---

## [8.7] 5/6 — Thấu Kính Kinh Tế DR & Quy Định Pháp Lý (§7)

- **Chống ảo vọng:** Nhân đôi toàn bộ infra Active-Active tăng gấp `> 2×` hóa đơn + độ phức tạp nhân sự trực — phần lớn SaaS chỉ cần **Warm Standby đa vùng** đạt RTO 5–15 phút với giá bằng 1/3, trừ tài chính/hạ tầng quốc gia bắt buộc `RPO ≈ 0`.

---

## [8.7] 6/6 — Bài Tập Đo RTO Thực Tế & Vạch Ranh Cell (§8)

1. Viết ra con số **RTO** (thời gian phục hồi tối đa) & **RPO** (dữ liệu mất tối đa) mà kinh doanh thật sự sẵn sàng trả tiền mua hạ tầng tương ứng.
2. Vẽ phương án cắt 100% người dùng hiện tại thành `10` cell dựa trên `tenant_id` hoặc `user_id` bucket — nút thắt chia sẻ chung còn sót là gì (Auth? Billing?)?

---

## [11.1] 1/6 — SLI, SLO, SLA & Error Budget (§0–§1)

- **Đọc trước:** `8.7` (RTO/RPO) · `9.7` (DORA metrics).
- **Ba quyết định `D-116`–`D-118`:**
  1. **SLI (`D-116`):** Chọn thước đo phản ánh **đúng nỗi đau người dùng** (`successful request / total valid`, `TTFT`, `p95` thực).
  2. **SLO & Error Budget (`D-117`):** Đặt `99,9%` hay `99,99%`? Ký văn bản xử lý gì khi ngân sách lỗi bị cháy hết (`freeze feature` để gia cố)?
  3. **Alert (`D-118`):** Alert theo **Multi-Window Burn Rate**, xoá sạch alert ngưỡng tĩnh (`2h sáng kêu oan`).

---

## [11.1] 2/6 — Chuỗi SLI → SLO → SLA & Bảng Giá Số 9 (§2)

- **Error Budget = `1 - SLO`:** Không phải chỉ tiêu "càng ít downtime càng tốt" (gây tâm lý đóng băng phát hành), mà là **ngân sách rủi ro hợp pháp** để đội kỹ sư dùng đổi lấy tốc độ ship tính năng!
- **Multi-window burn rate (`Google SRE Workbook`):** Cảnh báo pager khi vừa **cháy nhanh** vừa **đang cháy lúc này** (vd cửa sổ `1h` & `5m` ở tốc độ `14.4×` → cháy hết `2%` budget tháng trong 1 giờ), tránh thức dậy vì nhiễu 30 giây đã tự lành!

---

## [11.1] 3/6 — Bảng Số Error Budget & Burn-Rate (§3)

| Mức SLO | Downtime cho phép / 30 ngày | Burn Alert (`Page`) | Burn Alert (`Ticket`) |
|---|---|---|---|
| `99%` | `7 giờ 12 phút` | `14.4×` (1h + 5m: đốt 2%) | `3×` (1 ngày: đốt 10%) |
| **`99,9%`** | **`43,2 phút`** (`43.8m`/30.4d) | **`14.4×`** / `6×` (6h+30m) | `1×` (3 ngày + 6h) |
| `99,99%` | `4,32 phút` | Chi phí hạ tầng Multi-AZ/Cell nhảy vọt | Không đặt bừa khi backend phụ thuộc thấp hơn |

---

## [11.1] 4/6 — Năm Bẫy SLO Hay Gặp Trong Tổ Chức (§5)

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| SLO xanh 99,99% nhưng khách vẫn chửi | SLI đo nhầm nội bộ (`200 OK` tại nginx thay vì thành công logic/RUM) | Áp 3 câu kiểm tra SLI chạm hành trình khách hàng |
| Alert kêu giữa đêm liên tục | Đặt ngưỡng tĩnh CPU/latency 5 phút | Chuyển sang **Multi-Window Multi-Burn-Rate** |
| Budget cháy âm 200% vẫn ép ship tính năng | Error budget policy không có chữ ký đồng thuận PM + Eng | Ký cam kết: hết budget → auto chuyển 100% sang reliability |
| Một SLO chung toàn công ty | Lười phân rã | Tách `2–5` Critical User Journeys (Login, Checkout, Feed) |

---

## [11.1] 5/6 — Thấu Kính: SLA Phải Thấp Hơn SLO (§7)

- **Kinh tế & Hợp đồng:** Hợp đồng pháp lý (**SLA** bồi thường tiền với khách) luôn phải chừa đệm ít nhất `0.2–0.5%` thấp hơn mục tiêu kỹ thuật nội bộ (**SLO** `99.9%` → cam kết SLA `99.5%`), để đội ngũ kịp phản ứng trước khi vi phạm hợp đồng!

---

## [11.1] 6/6 — Thực Hành Viết SLO & Burn-Rate (`P15-03-L11`) (§8)

1. Chọn `1` Critical User Journey quan trọng nhất: viết đủ 1 cặp `(Availability SLI, Latency SLI)` cùng ngưỡng SLO và chính sách đóng băng feature nếu error budget `< 0%`.
2. **Gắn Lab:** **`P15-03-L11`** — dựng Prometheus + recording rule `burn_rate`, bắn tải lỗi để kiểm chứng alert tự kích hoạt đúng cửa sổ!

---

## [11.5] 1/6 — Kinh Tế Học Kỹ Thuật & FinOps (§0–§1)

- **Đọc trước:** `9.5` (Pricing compute) · `9.3` (Egress & VPC NAT pricing).
- **Quyết định `D-123` & `D-139`:**
  1. **Unit Economics (`D-123`):** Con số tối thượng không phải tổng hóa đơn USD/tháng, mà là **`Cost per 1k requests` / `per Active Tenant` / `per 1M tokens`**.
  2. **Build vs Buy (`D-139`):** Tính **TCO 3 năm** bao gồm lương trực on-call + bảo trì, đừng chỉ đếm giá licence `$0`!

---

## [11.5] 2/6 — Cầu Thang FinOps & Ba Khoản Tiền Ẩn (§2)

- **Ba hố đen chi phí hay bị quên:** **NAT Gateway + Cross-AZ Egress** (dùng `VPC Endpoint / PrivateLink` & locality ưu tiên cùng AZ), **Storage retention & Log cardinality explosion** (`11.2`), và **Resource Idle 20–40%** khi không right-sizing/scale-to-zero.
- **Thứ tự đúng của "Cầu thang Tiết kiệm":**
  **(1) Tag & Đo unit cost → (2) Xoá rác/Idle + Tối ưu query/cache → (3) Spot cho stateless/batch (`60–90%` off) → (4) Savings Plan / RI (`30–70%` off)**. *(Mua RI cho cụm đang lãng phí 40% là khoá cứng sự lãng phí!)*

---

## [11.5] 3/6 — Bảng Số Kinh Tế Cloud & LLM (`labs/cost.py`) (§3)

| Hạng mục | Giá trị tham chiếu | Nguồn / Nhãn | Ý nghĩa FinOps |
|---|---:|---|---|
| Tài nguyên nhàn rỗi điển hình | `20–40%` chi phí | FinOps Foundation | Right-size trước khi cam kết hợp đồng |
| Spot / Preemptible discount | `60–90%` giảm | Vendor specs (`11.5`) | Hợp batch / stateless / inference fallback |
| Savings Plan / RI discount | `30–70%` giảm | Cloud pricing models | Mua cho baseline tải ổn định |
| Tag allocation coverage | `> 95%` tài nguyên | `P` | Thiếu tag = vô chủ khi chia showback |

---

## [11.5] 4/6 — Hỏng Thế nào Về Mặt Chi Phí Kỹ Thuật (§5)

| Triệu chứng | Nguyên nhân | Cách bắt bệnh |
|---|---|---|
| Bill tăng nhanh hơn doanh thu | Unit cost trượt ngầm (N+1 query, prompt bloat `I-067`) | Ghép biểu đồ Cost chung biểu đồ Requests/Business metric |
| Phí NAT Gateway vọt (`I-060`) | Kéo S3/image qua public NAT | Gắn Gateway Endpoint / PrivateLink ngay (`9.3`) |
| Hóa đơn AI tăng `10×` (`I-067`) | Bật model quá lớn / reasoning không giới hạn | Model routing (`12.6`) + semantic cache |
| Hoá đơn không biết đội nào tiêu | Thiếu tag IaC | Chặn Terraform plan/CI nếu thiếu tag `owner/service` |

---

## [11.5] 5/6 — Chi Phí là Một Tín Hiệu Kiến Trúc (§7)

- **Vòng phản hồi Showback:** Kỹ sư chỉ tối ưu đúng thứ giúp khách hàng và công ty khi họ nhìn thấy **độ trễ p99** lẫn **chi phí/1.000 request** ngay trên cùng dashboard sau mỗi lần deploy (`9.7`).

---

## [11.5] 6/6 — Bài Tập Đo Unit Cost & Khoản Ẩn (§8)

1. Chọn 1 dịch vụ chính: chia tổng hóa đơn compute + DB + network tháng vừa rồi cho số request thành công — con số **Unit Cost** hiện tại là bao nhiêu?
2. Kiểm tra trên hóa đơn cloud mục **Data Transfer (Egress / Cross-AZ / NAT)**: có dòng nào vượt > 10% tổng bill không?

---

## [12.2] 1/6 — Giải Phẫu LLM Inference Serving (vLLM / SGLang / Dynamo) (§0–§1)

- **Đọc trước:** `1.5` (GPU HBM bandwidth vs Tensor Core Compute) · `11.2` (Telemetry & SLO).
- **Ba quyết định `D-126`–`D-128`:**
  1. Chọn engine serving (`vLLM` Continuous Batching + PagedAttention, `SGLang` RadixAttention, `Dynamo` Disaggregated Prefill/Decode).
  2. Tận dụng **Prefix Caching** cho system prompt / tài liệu RAG dùng lặp.
  3. Cân bằng **Quantization** (`BF16` → `FP8` → `INT4/AWQ`) trên thước đo tốc độ vs độ rớt chất lượng theo eval gate (`12.5`).

---

## [12.2] 2/6 — Hai Pha Prefill vs Decode & PagedAttention (§2)

- **Prefill (Compute-bound):** Xử lý song song toàn bộ input prompt → quyết định **TTFT** (*Time To First Token*).
- **Decode (Memory-Bandwidth-bound):** Sinh từng token nối tiếp, mỗi bước phải đọc toàn bộ weights + KV Cache từ HBM (`labs/cost.py`!) → quyết định **ITL** (*Inter-Token Latency*).
- **PagedAttention (`Kwon et al., SOSP 2023`):** Chia KV Cache thành trang ảo không liền kề như OS paging (`2.1`) → triệt tiêu phân mảnh nội bộ, giúp gộp hàng trăm request vào **Continuous Batching** mà vẫn tiết kiệm VRAM!
- **Disaggregated Serving (`Dynamo`):** Tách riêng cụm GPU Prefill và cụm GPU Decode để prompt `32k` không làm "khựng" toàn bộ chat streaming đang chạy trên cùng GPU.

---

## [12.2] 3/6 — Bảng Số Roofline & SLO Serving (`labs/cost.py`) (§3)

| Thông số | Giá trị bậc | Nguồn chính | Ý nghĩa |
|---|---:|---|---|
| Chat TTFT mục tiêu | `~1 s` (`p95`) | `P` | Nghẽn prefill / hàng đợi làm tăng vọt (`I-066`) |
| Smooth ITL band | `30–80 ms/token` | `P` | Vượt > 150 ms/token người đọc cảm nhận giật |
| HBM3 Bandwidth (H100 SXM) | `3,35 TB/s` (`labs/cost.py`) | NVIDIA Spec | Trần cứng tốc độ sinh token ở batch nhỏ |
| PagedAttention | Near-zero internal KV waste | Kwon et al. (SOSP 2023) | Tăng 2–4× serving throughput |

---

## [12.2] 4/6 — Hỏng Thế nào ở Cụm Serving LLM (§5)

| Triệu chứng | Nguyên nhân | Cách chẩn / Sửa |
|---|---|---|
| TTFT vọt `8s`, GPU compute chưa bão hoà (`I-066`) | Prefill dài chặn batch decode / preemption hết KV | Kiểm `num_requests_waiting`, `gpu_cache_usage_perc`; bật Prefix Caching / tách P-D |
| Token sinh ra khựng từng cục | Mixed batch prefill dài chen giữa decode | Tune `max_num_batched_tokens` / chunked prefill |
| Chi phí/token gấp 5 lần dự kiến | Prompt không cố định header → cache miss | Khoá prefix bất biến ở đầu prompt cho **RadixAttention** |
| Model bị "ngáo" sau quantize | W4A16/INT4 làm sập suy luận/tool-call | Quay lại **FP8** & kiểm chứng bằng Golden Eval (`12.5`) |

---

## [12.2] 5/6 — Thấu Kính Kinh Tế Token & Quy Mô (`P15-05`) (§7)

- **Self-host hay API Gateway (`P15-05`):** Nếu lưu lượng đều đặn không lấp được `> 55%` công suất GPU 24/7, tiền thuê GPU nhàn rỗi + nhân lực vận hành đắt hơn trả theo token qua Gateway có Model Routing (`12.6`)!

---

## [12.2] 6/6 — Thực Hành Rooflining LLM (`P15-03-L12` & `labs/cost.py`) (§8)

1. Chạy **`uv run python labs/cost.py`** quan sát giới hạn băng thông HBM `fp16` vs `int8` vs `int4` trên `H100 / L40S / RTX 4090` và nghịch lý batch=1!
2. **Gắn Lab:** **`P15-03-L12`** — đo trực tiếp TTFT, ITL & cost ở hai mức quantization trên tải mẫu.

---

## [12.5] 1/6 — Evals, Quan Sát `gen_ai` & Guardrails (§0–§1)

- **Đọc trước:** `7.6` (Tháp kiểm thử) · `11.2` (OpenTelemetry 4 tín hiệu).
- **Quyết định `D-130` & `D-132`:**
  1. **Eval Gate (`D-130`):** Dùng **Golden Set (`50–500` ca có version)** + **LLM-as-a-Judge** đã hiệu chuẩn với người chấm để **chặn CI/CD** trước khi đổi model hoặc prompt.
  2. **Guardrails (`D-132`):** Chống prompt injection trực tiếp/gián tiếp, kiểm soát rò PII & ACL (`I-068`).

---

## [12.5] 2/6 — Ba Lớp Bảo Vệ & Chuẩn Span `gen_ai` (§2)

- **Ba lớp thực chiến:** (1) Deterministic input validation & **pre-filter ACL ngay ở Vector/Keyword Retriever**; (2) LLM Guardrail / PII redaction song song; (3) Tool Sandbox + human-in-the-loop cho action thay đổi trạng thái (`12.4`).
- **Hiệu chuẩn LLM-Judge:** Không tin tuyệt đối "model to chấm model nhỏ" (position bias, verbosity bias) — định kỳ lấy mẫu ngẫu nhiên **50 ca đối chiếu đồng thuận với chuyên gia người thật**.
- **OTel `gen_ai.*`:** Mọi lời gọi model & agent tool đều phát trace chứa model id, `input_tokens`, `output_tokens`, TTFT, cost và `tenant_id`.

---

## [12.5] 3/6 — Bảng Số & Checklist Eval (§3, §6)

| Thành phần | Mức khuyến nghị | Nguồn / Nhãn | Mục tiêu |
|---|---|---|---|
| Golden evaluation set | `50–500` cases | `P` | Chạy tự động mỗi PR chạm prompt/model |
| Human calibration sample | `50` mẫu / kỳ | `P` | Kiểm độ khớp Cohen's kappa của LLM-judge |
| Telemetry standard | `gen_ai.*` | OpenTelemetry GenAI Spec | Đếm token, cache hit & unit cost theo feature |

---

## [12.5] 4/6 — Hỏng Thế nào ở Hệ Thống AI Production (§5)

| Triệu chứng | Nguyên nhân | Điểm vá bắt buộc |
|---|---|---|
| Đổi prompt/model xong tụt điểm âm thầm | Thiếu Golden Eval Gate trong CI | Cấm ship sửa prompt mà chưa pass golden set |
| Agent kéo dữ liệu lương HR trả cho Sales (`I-068`) | Dán prompt *"cấm tiết lộ"* thay vì **pre-filter ACL ở retrieval** | Lọc metadata `acl_groups` bắt buộc tại engine tìm kiếm |
| Guardrail tự tắt lỗi im lặng | Không có synthetic test định kỳ | Chạy canary injection test hàng giờ |
| Không biết tính năng nào đốt tiền | Thiếu `gen_ai` span & attribute `feature` | Gắn trace context + budget alert theo tenant (`12.6`) |

---

## [12.5] 5/6 — Thấu Kính Quản Trị Rủi Ro AI (§7)

- **Văn hoá đo trước sửa:** Thế hệ non-deterministic biến *"trông có vẻ hay trên 3 prompt thử tay"* thành cái bẫy lớn nhất; không có eval số liệu thì không biết lần tối ưu mới đang tiến hay lùi!

---

## [12.5] 6/6 — Bài Tập Xây Cửa Eval & Red-Team ACL (§8)

1. Gom `50` câu hỏi/ca thật từ production lỗi trong 2 tuần qua thành `golden_set.jsonl` cho 1 pipeline AI.
2. Viết 1 bài test `I-068`: user A hỏi đúng từ khoá đặc trưng của tài liệu chỉ thuộc user B → assertion retriever phải trả về **`0` document**.

---

## [13.1] 1/6 — Playbook: OLTP, Thanh Toán & Sổ Cái (§0–§1)

- **Đọc trước:** `8.3` (Transactional Outbox & Saga) · `4.8` (`Idempotency-Key` & RFC 9457).
- **Quyết định `D-134`:** Ghép trọn bộ luật sắt cho mọi hệ có dòng tiền hoặc tồn kho không được phép sai lệch:
  1. **Double-entry journal (`SUM(Nợ - Có) == 0` bất biến).**
  2. **Idempotency-Key từ client tới tận constraint DB.**
  3. **Outbox gửi webhook + job đối soát hàng đêm.**

---

## [13.1] 2/6 — Ba Luật Sắt Của Tiền Trong Cơ Sở Dữ Liệu (§2)

- **Không bao giờ dùng `UPDATE account SET balance = balance - 100` làm nguồn chân lý duy nhất:** Nguồn chân lý phải là bảng nhật ký bất biến **`ledger_entries` (ghi Nợ/Có cặp đối ứng cân bằng 0)**; `balance` chỉ là view/snapshot cache có kiểm tra `balance >= 0` với khoá hàng theo thứ tự ID!
- **Kiểu dữ liệu tiền:** Tuyệt đối **KHÔNG dùng IEEE-754 `float`/`double`** (`0.1 + 0.2 != 0.3`, `labs/svc2.py`!) — lưu **integer theo đơn vị nhỏ nhất** (đồng/cents) hoặc `NUMERIC(19, 4)`.
- **Idempotency-Key (`TTL >= 24h`):** Khoá duy nhất trong DB gắn cùng trạng thái request + hash payload (cùng key khác payload → trả `422`).

---

## [13.1] 3/6 — Bảng Số & Chế Độ Giao Dịch Tiền (§3)

| Bất biến / Tham số | Giá trị chuẩn | Nguồn / Nhãn | Ý nghĩa |
|---|---:|---|---|
| Ledger balance invariant | `SUM == 0` | Pacioli Double-Entry | Phát hiện lệch tức thì bằng truy vấn kiểm toán |
| Idempotency key retention | `≥ 24 giờ` | `P` | Phủ trọn cửa sổ retry webhook & app mobile |
| Số thập phân & ID lớn | Int64 string / Decimal | `labs/svc.py`, `svc2.py` | JS mất độ chính xác số nguyên `> 2^53` |
| Chu kỳ đối soát ngoài | Hàng đêm (Daily) | `P` | Không đợi cuối tháng/quý mới khớp ngân hàng |

---

## [13.1] 4/6 — Hỏng Thế nào Trong Thanh Toán Thực Tế (§5)

| Triệu chứng | Nguyên nhân | Cách vá dứt điểm |
|---|---|---|
| Khách bấm đúp bị trừ 2 lần (`I-049`) | Thiếu `Idempotency-Key` khoá ở DB | Unique key `(client_id, idempotency_key)` trong transaction |
| Tổng số dư tổng không khớp lịch sử | Cập nhật balance tại chỗ, thiếu double-entry | Đổi sang append-only journal với 2 dòng Có/Nợ |
| Khách chuyển khoản xong nhưng đơn treo | Tin mỗi redirect trình duyệt, webhook rớt | Webhook **+** cron pull query trạng thái cổng thanh toán |
| Đơn hàng đã chốt, ví chưa trừ | Dual-write | Đặt vào cùng DB transaction + Outbox (`8.3`) |

---

## [13.1] 5/6 — Thấu Kính Pháp Lý & Bảo Mật PCI (`10.x`) (§7)

- **PCI Scope Reduction:** Tuyệt đối không cho thẻ PAN gốc chạm backend nghiệp vụ của mình — dùng tokenization / hosted field của PSP ngay từ client (`10.1`, `13.1`).
- **Tạo cảm giác tin cậy (`Người dùng`):** Tiền đi đâu phải truy vết được từng cent ngay cả khi 2 retry chạy đồng thời giữa lúc đứt mạng.

---

## [13.1] 6/6 — Thực Hành Lab Sổ Cái & Roundtrip (`P15-03-L13`) (§8)

1. Chạy **`uv run python labs/svc2.py`** xem tận mắt JSON JS chặt mất chữ số cuối của `id_don = 9007199254740993` (`> 2^53`) và `0.1 + 0.2`!
2. **Gắn Lab:** **`P15-03-L13`** — hoàn thiện sơ đồ sizing + checklist đối soát cho một lớp tải OLTP sổ cái thực tế.

---

## [14.10.2] 1/6 — Mật Mã II: PQC (FIPS 203/204/205) & Constant-Time (§0–§1)

- **Đọc trước:** `14.10.1` (Primitives & Lattices) · `10.2` (KMS & vòng đời mật mã).
- **Quyết định `D-107` & Trọng tâm biên giới:**
  1. Dữ liệu nào có **tuổi bí mật dài hơn 10 năm** phải ưu tiên chuyển sang **Hybrid TLS (`X25519 + ML-KEM-768`) ngay bây giờ** vì mối đe doạ **Harvest Now, Decrypt Later**.
  2. Tuyệt đối hiểu ranh giới **khi nào tự cấu hình chuẩn** vs **khi nào phải chuyển chuyên gia mật mã (`D-137`)**.

---

## [14.10.2] 2/6 — Chuẩn NIST 2024 & Crypto-Agility (§2)

- **Cái gì thay, cái gì sống:**
  - *Bị phá bởi thuật toán Shor (bất đối xứng cổ điển):* **ECDH/RSA trao đổi khoá → ML-KEM (`FIPS 203`)**; **ECDSA/RSA chữ ký → ML-DSA (`FIPS 204`) / SLH-DSA (`FIPS 205`)**.
  - *Sống sót (đối xứng & băm, tăng độ dài khoá nếu cần chống Grover):* **AES-256-GCM / ChaCha20-Poly1305** & **SHA-256/384/SHA-3**.
- **Crypto-agility:** Thuật toán không nằm rải ở 40 microservice — tập trung cấu hình qua TLS termination, KMS envelope và version tag trên ciphertext.
- **Constant-Time (`14.11`):** Một vòng `memcmp()` kết thúc sớm hay nhánh `if (secret_bit)` để lộ khoá bí mật qua side-channel thời gian bất kể kích thước khoá lớn tới đâu!

---

## [14.10.2] 3/6 — Bảng Ánh Xạ Chuẩn PQC Hiện Hành (§3)

| Chức năng | Thuật toán cổ điển | Chuẩn NIST PQC (8/2024) | Khuyến nghị triển khai |
|---|---|---|---|
| Trao đổi khoá (KEM) | X25519 / ECDH / RSA | **ML-KEM (`FIPS 203`)** | Hybrid `X25519MLKEM768` trong TLS 1.3 |
| Chữ ký số (chính) | ECDSA / Ed25519 / RSA | **ML-DSA (`FIPS 204`)** | Cần đo kích thước cert/chữ ký lớn hơn |
| Chữ ký dự phòng (hash) | RSA / ECDSA | **SLH-DSA (`FIPS 205`)** | Chậm/chữ ký to, làm gốc neo an toàn |
| Mã hoá đối xứng | AES-128 → AES-256 | Giữ nguyên (256-bit) | An toàn trước Grover |

---

## [14.10.2] 4/6 — Bốn Hiểu Lầm & Bốn Ca Hỏng Về PQC (§5)

| Hiểu lầm / Triệu chứng | Sự thật thực tế | Kiểm chứng & Xử lý |
|---|---|---|
| *"Chưa có máy tính lượng tử, lo sau"* | Kẻ tấn công đang **lưu ciphertext hôm nay** chờ 2035 giải mã | Phân loại tuổi bí mật dữ liệu; hybrid ngay cho dữ liệu > 10 năm |
| Bật PQC làm TLS handshake chậm / MTU split | Khoá & chữ ký lattice kích thước vài KB | Thử hybrid trên canary service, đo p50/p99 & MTU thật |
| *"Constant-time là tối ưu tốc độ"* | Ngược lại: **ép nhánh nhanh chạy chậm đều bằng nhánh chậm** | Không tự cài phép so sánh/cryptographic math; dùng lib chuẩn audit |
| Đổi thuật toán = vá 40 nơi | Thiếu **Crypto Inventory & Agility** | Tập trung tại Gateway/KMS & gắn `key_id` + `alg` header |

---

## [14.10.2] 5/6 — Ranh Giới Quyền Quyết Định (`D-137`) (§7)

- **Tự quyết của kỹ sư:** Lập Crypto Inventory, phân loại dữ liệu theo tuổi bí mật, nâng cấp thư viện TLS/OpenSSL/Go hỗ trợ **X25519MLKEM768**, bật `AES-256`.
- **Phải có Chuyên gia Mật mã:** Bất cứ khi nào động vào thiết kế protocol mới, chỉnh tham số lattice, cài đặt primitive không nhánh phụ thuộc secret hoặc tự viết code constant-time.

---

## [14.10.2] 6/6 — Bài Tập Lập Crypto Inventory & Lab Side-Channel (§8)

1. Lập bảng 1 trang **Crypto Inventory** hệ thống hiện tại: chỗ nào dùng RSA/ECC/JWT, chủ sở hữu là ai, và dữ liệu bảo vệ cần bí mật bao nhiêu năm.
2. Kiểm tra OpenSSL / cloud CDN / TLS proxy đang dùng đã bật hybrid `X25519MLKEM768` (`FIPS 203`) hay chưa.
