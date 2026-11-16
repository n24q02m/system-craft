# 5.6 — Search Engine: Elasticsearch & OpenSearch

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** ds-21-search-queue.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 5.2 (giới hạn của SQL khi tìm kiếm).

**Sợi chỉ đỏ:** *Khách gõ 'phở bò giao nhanh' — search engine làm được gì mà SQL không?* — trả lời: SQL LIKE quét từng dòng và không hiểu nghĩa; search engine "lộn bảng" — từ đi tới danh sách document chứa nó — nên tìm full-text nhanh bậc magnitude; analyzer (tách token, bỏ dấu, gọt đuôi từ) quyết định "tìm có ra không"; shard là đơn vị phân tán. Câu hỏi để lại cho chương sau: *Các bước xử lý đơn cần bốc xếp đáng tin — stream kiểu Kafka khác queue thường chỗ nào?*

**Thuật ngữ sẽ gặp:** *inverted index* — bảng từ sang danh sách document: trái tim của mọi search engine; *analyzer* — chuỗi xử lý lúc ghi và lúc tìm: hai đầu phải khớp, không khớp là không ra; *relevance score* — xếp hạng kết quả (BM25): thứ SQL không có; *shard* — một Lucene index nhỏ: đơn vị phân tán và cũng đơn vị chết; *node role* — master/data/ingest tách vai cho an toàn; *ES vs OpenSearch* — hai nhánh sau licence 2021 (verify 10/2026 trong chương).

**Ví dụ mở đầu:** Khách gõ "pho bo giao nhanh" không dấu: LIKE khớp từng ký tự nên trượt; analyzer chuẩn hoá dấu và tách token vẫn bắt được món. Còn "giao nhanh" là cụm cần xếp hạng, không phải bộ lọc. Chương này đi từ lộn bảng tới cluster vận hành, và chỉ ra thao tác nguy hiểm nào hay giết cluster production.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Lucene-based search hay Postgres FTS/pgvector cho bài toán tôi | Độ phức tạp query + relevance + scale nào đáng một cluster riêng? |
| 2 | Mapping + analyzer cho từng field (kể cả tiếng Việt) | Ngôn ngữ của tôi tokenise đúng chưa — ai đã test bằng từ thật? |
| 3 | Elasticsearch (giấy phép AGPL từ 8.16+/vendor) hay OpenSearch (Apache-2.0) | Fork 2021 — chọn nhánh nào cho 3 năm tới? |
| 4 | Chiến lược reindex + ILM (lifecycle) | Mapping đổi = reindex — đường nâng cấp có sẵn chưa? |

---

## 2. Cơ chế

### 2.1 Lucene inverted index — tìm chữ nhanh vì "lộn bảng"

Mỗi field văn bản → **analyze** (token → term) → **inverted index** (term → danh sách document). Tìm = tra bảng term, gộp bitmap. Relevance = **BM25** (TF-IDF có chuẩn hoá theo độ dài). Vì thế: tìm full-text **nhanh** (bỏ qua scan), nhưng exact-match/sort trên text **chậm** — field keyword phải map `keyword` (not-analyzed) chứ đừng để `text`.

### 2.2 Analyzer — quyết định "tìm có ra không"

Chuỗi: `char_filter → tokenizer → token filter` (lowercase, stemming, stopword, synonym). **Tiếng Việt:** không có analyzer tiếng Việt builtin chất lượng — thực chiến: `standard` tokenizer (tách theo Unicode word — hoạt động với tiếng Việt có khoảng trắng) + lowercase + **synonym graph** cho thuật ngữ; hoặc `icu` + tự quản từ điển. Test bắt buộc bằng `_analyze` API với câu thật — không đoán.

```
GET /idx/_analyze {"analyzer":"my_vi","text":"Hà Nội - thủ đô"}
```

### 2.3 Cluster: node role + shard — mô hình phân tán

- **Data node** giữ shard; **master-eligible** quản metadata (chọn 3, tránh split-brain — →8.2); **coordinating** gộp kết quả;
- Index = nhiều **primary shard** + **replica**; query gộp từ mọi shard chứa dữ liệu (fan-out);
- **Hot/warm/cold tier + ILM**: log 7 ngày hot (NVMe), 30 ngày warm, sau đó cold/delete — tự động rollover theo size/tuổi — khác biệt chi phí 5–10× (I).

**Sai kinh điển:** shard quá to (giới hạn Lucene ~2 tỷ doc/shard; shard > 30–50 GB khôi phục chậm) hoặc quá nhiều shard nhỏ (mỗi shard = Lucene instance + memory overhead) — mục tiêu ~10–50 GB/shard (I).

### 2.4 ES vs OpenSearch (verify 10/2026: ES 9.5.5)

Fork 2021 (giấy phép): **OpenSearch** Apache-2.0 (AWS → Linux Foundation 2024), **Elasticsearch** AGPL option từ 8.16 (2024) sau khi rút quyết định "không mở". 2026: hai nhánh API tương thích phần lớn (thay index name/feature nhỏ), feature phân kỳ dần (ES: ES|QL query language, vector tốt; OS: riêng roadmap). Chọn theo: giấy phép pháp chế, cloud (OpenSearch Service vs Elastic Cloud), feature vector (→5.10 so sánh). Cả hai đều Lucene lõi — vận hành như nhau 90%.

### 2.5 Thao tác nguy hiểm & thay thế đúng

- **Refresh interval** mặc định 1s — log index 10k/s đổi refresh 30s + bulk → thông lượng tăng nhiều lần (I);
- **Deep pagination** (`from: 10000`) — memory bomb; dùng `search_after` + PIT;
- **Wildcard đầu chuỗi** (`*abc`) — quét toàn term; đổi analyzer hoặc n-gram;
- **Aggregation trên field cardinality cực cao** — memory; đổi composite aggregation.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Elasticsearch / OpenSearch | 9.5.5 (10/2026) | V | versions.csv |
| Shard mục tiêu | 10–50 GB | I | |
| Shard max doc | ~2 tỷ (Lucene) | V | |
| Refresh mặc định | 1 s | V | |
| Deep pagination | dùng search_after | V | |

---

## 4. Suy luận kiến trúc

- **S1:** Search engine bán **relevance + query phức tạp trên text** — không phải storage chính: hệ "search index" là **trích xuất** (projection) của nguồn chân lý (DB — CDC — →5.15), luôn xây lại được.
- **S2:** Tham số trụ: indexing lag (CDC→searchable), query p99, shard balance, heap usage/GC (Lucene nặng off-heap — đừng nhầm).
- **S3:** Hot/warm/cold đổi hiệu năng lấy chi phí (5–10×); refresh/replica đổi độ tươi lấy throughput — mọi núm đều là trade-off có số.
- **S4:** Vector search (kNN, HNSW trong Lucene — →5.10) đang nhập lõi search engine — "text + vector hybrid" một hệ: Search engine hợp nhất RAG infrastructure (→12.5).
- **S5:** SQL FTS + pgvector đủ cho đa số nhỏ/vừa — đừng nuôi cluster Lucene cho 100k documents; chỉ lên khi query phức tạp/replication/scale thật.
- **S6:** Khi "tìm không ra": analyzer trước (dùng _analyze soi token), rồi mapping (text vs keyword), rồi data (CDC lag) — theo thứ tự đó.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Tìm từ đơn không ra | Analyzer/token sai | _analyze | §2.2 |
| Search latency vọt lúc reindex | Reindex cắn I/O + CPU | throttle; off-peak | §2.4 |
| Cluster "vàng" node rớt | Heap/OOM — shard quá nhiều | _cat/shards; heap metric | §2.3 |
| Phân trang sâu timeout | from/size lớn | search_after | §2.5 |
| Log đắt bất thường | Không ILM — tất cả hot | ilm policy | §2.3 |
| ES và DB lệch nhau | CDC/outbox tụt (→5.15) | indexing lag metric | §2.1 |

---

## 6. Cách đo

```bash
# Sức khỏe cluster 1 câu
curl -s localhost:9200/_cluster/health?pretty

# Shard to/nhỏ + phân bổ
curl -s localhost:9200/_cat/shards?v&s=store:desc | head -15

# Query chậm + heap
curl -s localhost:9200/_nodes/stats/jvm,indices | jq '.nodes[] | .jvm.mem'

# Analyzer thật của field:
curl -s localhost:9200/idx/_analyze -H 'Content-Type: application/json' \
     -d '{"field":"title","text":"học máy"}'
```

Nguyên tắc: **_analyze là đèn pin của relevance** — mọi bug "tìm không ra" bắt đầu bằng việc soi token, không phải chỉnh BM25.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay cluster ES:** Postgres FTS + pgvector (đến vài triệu docs), ClickHouse cho log analytics (→5.8 — rẻ hơn nhiều cho log thuần), typesense/meilisearch cho search box nhỏ (đơn giản vận hành). **Thay reindex thủ công:** index alias + dual-write qua CDC — zero-downtime nâng cấp mapping.

Năm thấu kính:
- **Kinh tế:** Cluster search 3 node nóng + warm tier = hóa đơn thật; log về ClickHouse/S3 (→5.8/5.9) thường giảm 5–10× cho use case log thuần.
- **Vận hành:** ILM nên là policy mặc định của mọi index mới — không có policy = chương trình "nuôi mọi thứ trên NVMe mãi mãi".
- **An ninh:** Search endpoint thường phơi query DSL ra client — scoped search (filter theo tenant bắt buộc — →5.14) chống cross-tenant leak (bẫy #1 search).
- **Lịch sử:** 2010-2021 một mình Elasticsearch; 2021 fork OpenSearch (giấy phép); 2024 Elasticsearch mở lại (AGPL) — cú giáo huấn: "mở" là phổ biến giữ khách, đóng là mời fork.
- **Người dùng:** Người dùng gõ sai chính tả vẫn tìm ra món muốn — chương này là phép màu có cấu trúc đằng sau (analyzer + BM25 + synonym); gõ đúng mà không ra là lỗi của người dựng, không của người dùng.

---

## 8. Đọc tiếp & bài tập

- Vector/hybrid: **5.10** · CDC/đồng bộ: **5.15** · Log rẻ hơn: **5.8, 5.9** · Multi-tenant filter: **5.14** · RAG: **12.5**
- **Bài tập 1:** `_analyze` field tiêu đề với 3 câu tiếng Việt thật. Token giống kỳ vọng? Synonym cần thêm gì? 30 phút này quyết định relevance cả năm.
- **Bài tập 2:** `_cat/shards` — đếm shard > 50 GB và < 1 GB. Hai nhóm đó là "kế hoạch reindex/merge" đang chờ.
- **Bài tập 3:** Kiểm tra ILM policy của mọi index log. Index nào không có = storage bill phình thầm lặng — liệt kê và gắn policy tuần này.
