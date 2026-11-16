# 5.11 — Graph & Time-series: Property Graph & TSDB

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.2 (SQL chịu thua chỗ nào) · 5.8 (dữ liệu chuỗi).

**Sợi chỉ đỏ:** *Quan hệ quán-khách-phố và chuỗi số theo giờ — graph và time-series có xứng một chỗ?* — trả lời: hai bài toán đặc thù đứng chung một chương vì cùng lý do tồn tại — câu hỏi mà SQL làm vá víu: quan hệ nhiều tầng (graph) và chuỗi số theo giờ (time-series); và cùng một bệnh nổi tiếng phải quản như ngân sách: cardinality. Câu hỏi để lại cho chương sau: *Tính toán chảy liên tục hay gom theo mẻ — stream và batch ăn khớp nhau thế nào?*

**Thuật ngữ sẽ gặp:** *graph* — đỉnh và cạnh khi chính quan hệ là dữ liệu: "quán nào bạn của bạn hay đi"; *traversal* — đi theo cạnh nhiều tầng: chỗ JOIN sâu của SQL gãy lưng; *time-series* — chuỗi (timestamp, giá trị) tần số cao, ghi chỉ thêm vào; *cardinality* — số chuỗi khác nhau đang sống: phình là cháy ngân sách; *downsampling/retention* — làm thô dữ liệu cũ và xoá theo tuổi: hai van tiết kiệm bắt buộc; *metric-native vs bảng cột* — hai họ giải time-series 2026 (trạng thái verify trong chương).

**Ví dụ mở đầu:** Gợi ý "quán mà bạn của bạn hay đi" cần đi ba tầng quan hệ quán-khách-phố: SQL JOIN sáu bảng. Chuỗi đơn-phút theo từng thành phố cần ghi mỗi giây và query "tuần này so tuần trước": bảng thường phình tới gãy. Hai workload đặc thù, hai quyết định tách riêng: chương này cho biết khi nào xứng đáng tách và cái giá của việc tách.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Cần graph engine chuyên dụng hay SQL đệ quy (CTE) đủ | Độ sâu traversall + độ phức tạp pattern của tôi tới đâu? |
| 2 | Graph: Neo4j / Memgraph / property-graph chuẩn (SQL/PGQ 2024) | Query language + vận hành + giấy phép? |
| 3 | Time-series: TSDB chuyên dụng (Prometheus/VictoriaMetrics) hay ClickHouse | Độ phân giải, retention, cardinality? |
| 4 | Cardinality budget cho metric labels | Ai kiểm soát số series — và nó đang nổ ở đâu? |

---

## 2. Cơ chế

### 2.1 Graph: khi quan hệ là dữ liệu chính

Property graph = node + edge (cÓ thuộc tính). Traversal depth-k: index-free adjacency (mỗi node trỏ hàng xóm — đọc locality →1.2) — nhanh khi "bắt đầu từ node rồi đi". Ngược lại SQL JOIN depth-k cần k JOIN (kế hoạch truy vấn không cục bộ). Thắng: fraud ring (chuỗi giao dịch liên quan), recommendation (bạn-của-bạn), lineage dữ liệu, dependency graph. Thua: dữ liệu phẳng thống kê theo cột (OLAP — →5.8), điểm-toán CRUD (RDBMS).

**Ngưỡng thực dụng:** cần pattern 3+ hop với biến thiên (depth không cố định)? → graph engine. Chỉ cây 2 cấp (organization → team)? → SQL `WITH RECURSIVE` đủ (PG rất giỏi); nhảy graph engine cho cây đơn giản là trả ops cho vẻ.

### 2.2 Trạng thái graph 2026

- **Neo4j:** đại diện chủ lưu (Cypher) — giấy phép thương mại + community;
- **Memgraph:** in-memory, streaming (Bolt protocol tương thích);
- **Chuẩn hoá ISO: GQL (2024) và SQL/PGQ (SQL:2023)** — property graph là "tính năng SQL chuẩn" — PG/Oracle/MySQL thêm dần (`MATCH` syntax); hướng đi: **graph là kiểu truy vấn, không nhất thiết engine riêng**;
- **Bản đồ tri thức AI:** graph + vector (GraphRAG — →12.5) đang kéo graph về trung tâm: "quan hệ + ngữ nghĩa" hai chân của retrieval 2026.

### 2.3 Time-series: workload đặc thù, bệnh đặc danh

Đặc trưng: ghi append-only theo thời gian; query cửa sổ thời gian + aggregate (rollup); **xóa theo tuổi** (downsample/retention); **cardinality là kẻ thù** — mỗi label combination duy nhất = 1 series cần RAM index.

| Giải pháp | Hợp khi |
|---|---|
| **VictoriaMetrics** | metric_obs phục vụ quy mô lớn, rẻ hơn Prometheus tự vận hành; đã có cluster |
| **Prometheus** | giám sát K8s chuẩn (mặc định →11.1); retention ngắn + remote-write ra TSDB khác |
| **ClickHouse** | log/event + metric cùng một hệ; retention/TTL linh hoạt (→5.8) |
| **TimescaleDB** | SQL + time-series trong PG (kiểu dữ liệu hypertable) |
| **M3DB/InfluxDB** | ngách: siêu quy mô / IoT legacy |

**Quy tắc:** metric quan sát → VM/Prometheus; log+metric chung → CH; SQL analytic thời gian → Timescale/CH. Đừng dựng InfluxDB cho 5k series.

### 2.4 Cardinality — quản trị như ngân sách

`http_requests_total{path="/user/12345"}` — path unique mỗi user → **triệu series** → RAM nổ + query chậm (triệu chứng TSDB kinh điển: "Prometheus OOM", "active series vọt"). Ngân sách cardinality: (a) label chỉ cho **chiều có nghĩa tổng hợp** (method, status — không phải id); (b) metering theo tenant (→5.14) đưa id xuống **exemplar**/log không phải label; (c) alert active-series growth rate.

### 2.5 Graph + time-series = hai bài toán AI 2026

- Graph: **lineage dữ liệu** (tái tạo đường dữ liệu — audit AI), **knowledge graph RAG** (→12.5);
- Time-series: **telemetry GPU/cụm AI** (→12.4 — utilization, MFU), **anomaly detection** (tự động alert — →11.1).
Hai mô hình này từng "ngách" đang là hai chân của hệ vận hành AI.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| SQL/PGQ + GQL | chuẩn ISO 2023/2024 | V | |
| Traversal depth thực dụng (graph engine) | 3–6 hop thoải mái | I | |
| Cardinality lành mạnh (một cụm vừa) | ~vài triệu active series | I | VM/Prometheus phụ thuộc |
| VictoriaMetrics / Prometheus | chuẩn observability | V | →11.1 |
| CH retention TTL | drop partition nguyên khối | V | →5.8 |

---

## 4. Suy luận kiến trúc

- **S1:** Chọn graph/TSDB chuyên dụng = chọn theo **hình truy vấn** (traversal biến thiên / cửa sổ thời gian + cardinality), không phải theo mô hình "dữ liệu liên quan nhau".
- **S2:** Tham số trụ (graph): hop-count query p99, đếm node/edge theo loại; (TS): active series, ingest rate, query p99 theo cửa sổ.
- **S3:** SQL recursive đổi ops đơn giản lấy trần thấp; TSDB chuyên đổi ops riêng lấy cardinality/retention đúng nghề — mỗi lần "lên chuyên dụng" phải kèm bài toán thật.
- **S4:** Graph đang bị SQL chuẩn hoá (PGQ) giống vector bị DB nuốt (→5.10) — ranh giới "cần engine riêng" n narrow dần; đầu tư ngôn ngữ truy vấn (Cypher/MATCH) an toàn hơn đầu tư engine.
- **S5:** AI amplifies cả hai (GraphRAG + GPU telemetry) — kỹ năng cardinality budget & graph modeling trở thành kỹ năng nền của platform AI.
- **S6:** Khi graph chậm: kiểm tra "supernode" (node hàng triệu edge — traversal phát nổ, cần capping/bidirectional); khi TS chậm: cardinality trước, sau mới là capacity.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Traversal chậm đột biến | Supernode (user nổi tiếng) | profile query; đếm edge | §2.1 |
| Prometheus OOM | Cardinality nổ | top10 metrics by series | §2.4 |
| Metric "biến mất" sau 2 tuần | Retention mặc định | retention config | §2.3 |
| Query đồ thị 2 cấp chậm | Sai công cụ/câu query | thử SQL CTE | §2.1 |
| TS ingest tụt giờ cao điểm | Cardinality + write amp | ingest metric theo cardinality | §2.4 |
| GraphRAG kém | Graph model tệ (không phải engine) | audit ontology | §2.5 |

---

## 6. Cách đo

```cypher
// Graph: đếm bậc node — tìm supernode
MATCH (n:User)-[r:KNOWS]->() RETURN n.id, count(r) AS deg
ORDER BY deg DESC LIMIT 10;
```

```promql
# TS: cardinality to nhất (Prometheus/VM)
topk(10, count by (__name__)({__name__=~".+"}))
topk(10, count by (job)({__name__!=""}))
```

Nguyên tắc: **supernode và cardinality là hai "hot key" của hai mô hình này** — dashboard hai con số đó trước mọi tối ưu khác.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay graph engine:** SQL recursive CTE (độ sâu ≤ 3 cố định); adjacency list trong RDBMS + app-side BFS; DuckDB/CH với graph extension (ngách). **Thay TSDB:** ClickHouse cho tất cả (log + metric — giảm số hệ); BigQuery/S3 cho phân tích dài hạn.

Năm thấu kính:
- **Kinh tế:** TSDB chuyên dụng rẻ hơn "rác thải Prometheus không giới hạn" — cardinality budget là bảng lương của hóa đơn giám sát.
- **Vận hành:** Đặt quy ước label "được phép" (allowlist) trong CI cho metric mới — như review schema (→4.3).
- **An ninh:** Graph quyền truy cập chính là model an ninh (zero-trust quan hệ); metric label có thể lộ PII (email trong label) — quy ước cấm (→5.13).
- **Lịch sử:** 2010s "mọi thứ sẽ là graph DB"; 2020s "mọi thứ là vector"; thực tại: mô hình dữ liệu là câu hỏi **hình truy vấn**, xu hướng chỉ là nhịp quảng cáo — bài học xuyên atlas.
- **Người dùng:** "Gợi ý bạn chung chính xác" (graph) và "dashboard không chết giờ cao điểm" (cardinality) — hai trải nghiệm này là sản phẩm của chương này.

---

## 8. Đọc tiếp & bài tập

- Observability stack: **11.1** · GraphRAG: **12.5** · GPU telemetry: **12.4** · Ma trận: **5.15** · Cardinality/chi phí: **5.16**
- **Bài tập 1:** Chạy `topk(10, count by (__name__)...)` trên hệ giám sát của bạn. Metric nào chiếm > 50% series? Label id ẩn trong đó chưa?
- **Bài tập 2:** Viết cùng một truy vấn 3-hop bằng SQL recursive và Cypher; đo + so độ phức tạp code. Con số riêng của bạn cho ngưỡng §2.1.
- **Bài tập 3:** Kiểm tra retention metric hiện tại. Nếu mọi metric lưu cùng một thời gian — bạn đang trả NVMe cho dữ liệu 6 tuần không ai nhìn.
