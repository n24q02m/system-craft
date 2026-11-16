# 5.10 — Vector Databases & ANN Indexing

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** ds-23-olap-vector-object.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 5.6 (tìm từ khoá — đối chứng).

**Sợi chỉ đỏ:** *Gợi ý món và tìm theo ngữ nghĩa — vector search đổi trò tìm kiếm thế nào?* — trả lời: tìm theo ngữ nghĩa nghĩa là nhúng chữ và ảnh thành vector rồi tìm láng giềng gần; chính xác là quét cả triệu vector mỗi câu hỏi — ANN (HNSW, IVF) đổi chút sai lệc lấy tốc độ; và DB vector chỉ là một phần tư câu chuyện RAG. Câu hỏi để lại cho chương sau: *Quan hệ quán-khách-phố và chuỗi số theo giờ — graph và time-series có xứng một chỗ?*

**Thuật ngữ sẽ gặp:** *embedding* — chữ/ảnh/món thành điểm trong không gian nghìn chiều: gần nhau về toạ độ là gần nhau về nghĩa; *ANN* — approximate nearest neighbor: gần đúng vì chính xác là khắc khe; *HNSW* — đồ thị bậc thang: chỉ số phổ biến nhất 2026; *recall vs latency* — cặp núm đổi nhau: càng chính xác càng chậm; *filter pre vs post* — lọc metadata trước hay sau khi tìm vector: quyết định vận hành bị bỏ quên nhiều nhất; *RAG* — truy hồi rồi sinh: pipeline bốn khâu, DB vector chỉ một.

**Ví dụ mở đầu:** Khách hỏi "món gì hợp người ăn kiêng lowcarb" — không từ khoá nào khớp trực tiếp, nhưng embedding đặt câu hỏi ấy ngay cạnh salad cá hồi về nghĩa. Chương này cho bảng chọn ngưỡng thực chiến (đúng chỗ nào dùng HNSW, chỗ nào đủ brute force), bài filter pre/post, và vị trí thật của DB vector trong pipeline RAG.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | pgvector hay dedicated store (Qdrant/Milvus/Weaviate) | Số vector, QPS, cần filter metadata phức tạp không? |
| 2 | Index: HNSW / IVF-PQ / DiskANN (hoặc brute force!) | Recall vs latency vs RAM — đổi gì lấy gì? |
| 3 | Chunking + embedding model + re-rank pipeline | Chất lượng RAG nằm ở đây nhiều hơn ở DB vector |
| 4 | Quantization (PQ/SQ/binary) + filter strategy | RAM nổ thì thả gì? pre-filter vs post-filter? |

---

## 2. Cơ chế

### 2.1 Bài toán ANN: gần đúng vì chính xác là khắc khe

Tìm k láng giềng trong không gian D chiều: brute force = so mọi vector (chính xác 100%, chậm theo N); ANN đánh đổi **recall** (~95–99%) lấy tốc độ ~100–1000×. Ba họ index:
- **HNSW** (graph): navigation trong đồ thị nhiều tầng — query nhanh (~sub-ms), **RAM đắt** (graph + vector full trong bộ nhớ), build chậm;
- **IVF-PQ** (cluster + nén): chia cụm, Product Quantize nén vector (RAM giảm ~8–32×) — recall giảm theo nén; hợp tập cực lớn chấp nhận sai;
- **DiskANN/Vamana** (Microsoft): graph tối ưu cho SSD — RAM thấp, disk read thông minh — hợp tỷ tỷ vector "không nóng".

### 2.2 Ngưỡng chọn — bảng thực chiến

| Tình huống | Nên |
|---|---|
| < ~100k vector, ít query | **pgvector (brute/IVF)** hoặc thậm chí numpy — đừng xây gì cả |
| ~100k–10M, cần SQL + transaction cùng dữ liệu | pgvector + HNSW |
| > 10M hoặc QPS cao hoặc filter phức tạp | dedicated (Qdrant/Milvus/Weaviate) |
| Tỷ scale, chấp nhận disk | Milvus/DiskANN-style |

RAM ước tính (HNSW, không quantize): `N × D × 4 bytes × ~1,5` (graph overhead) — 10M × 768 chiều ≈ ~46 GB (I) — con số này là lý do quantization tồn tại.

### 2.3 RAG pipeline: DB vector chỉ là 1/4 câu chuyện

```
Document → chunk (size 256–1024 token, overlap ~15%) → embedding model
   → index (kèm metadata filter: tenant, ACL, thời gian)
Query → embed → ANN top-50 → **filter ACL** → **re-rank (cross-encoder)** → top-5 → LLM
```

Hai điểm chết chất lượng thật sự: (1) **chunking sai** (cắt đôi bảng/đoạn mã); (2) **thiếu re-rank** (ANN lấy gần đúng — re-ranker chính xác sắp lại). DB vector nhanh thêm 2 ms không cứu chunk tệ. **ACL ở retrieval (không chỉ ở prompt!)** — lỗ hổng RAG số một: rag truy cập dữ liệu lân phòng (→12.5/10.4).

### 2.4 Filter: pre vs post — quyết định vận hành bị bỏ quên

- **Post-filter:** ANN top-k rồi lọc — kết quả có thể rỗng (top-k toàn "sai tenant");
- **Pre-filter:** lọc trước rồi ANN — đúng nhưng chậm nếu filter chọn ít rows (index vô dụng);
- **Filtered search HNSW** (Qdrant/weaviate) hoặc **partial index** (pgvector): graph đi có "máu" filter — cân bằng hai cực. Multi-tenant (→5.14): **collection/index theo tenant lớn**, filter cho số còn lại.

### 2.5 Trạng thái 2026

- **pgvector:** đã vào mainstream PG (0.7+/0.8: HNSW iterative scan, quantization halves);
- **Dedicated:** Qdrant (Rust, filter-first), Milvus (scale, disk), Weaviate (module hoá), Elasticsearch/OpenSearch (kNN + hybrid text — →5.6), **ClickHouse vector index** (verify 2026: vector search trong CH);
- **Redis 8 vector set** (verify 2026) — vector trong KV in-memory: hợp real-time nhỏ;
- Xu hướng hợp nhất: **hybrid search** (BM25 + vector, fusion RRF) và quantization mặc định — "một hệ cho text + vector" (→12.5).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| HNSW RAM | N×D×4B×~1,5 | I | 10M×768d ≈ 46 GB |
| PQ nén | 8–32× RAM giảm | I | recall giảm |
| Recall HNSW/PQ | ~98–99% / 90–95% | I | theo cấu hình |
| pgvector hợp lệ | < ~10M vector | P | |
| Re-rank gain chất lượng | lớn (top-k đúng thứ tự) | I | đo trên bộ eval |

---

## 4. Suy luận kiến trúc

- **S1:** Vector index là **đường truy vấn thứ hai** của dữ liệu (keyword → semantic) — quyết định lưu ở đâu phải tính cả hai + ACL + transaction (pgvector thắng khi dữ liệu nguồn đã ở PG).
- **S2:** Tham số trụ: recall@k (đo trên eval set!), latency p99, RAM/index, filter selectivity.
- **S3:** HNSW đổi RAM lấy tốc; PQ đổi recall lấy RAM; disk-ANN đổi latency lấy scale — không có "index tốt nhất", chỉ có trade đúng workload.
- **S4:** Embedded model + chunking đổi model đời mới (nâng chất lượng biểu diễn) → **re-embed toàn bộ** là chi phí ẩn lớn: pipeline re-embed (CDC-style — →5.15) phải thiết kế từ đầu.
- **S5:** Vector đang nhập vào DB có sẵn (PG/CH/ES/Redis) — "vector database" như danh từ riêng có thể mờ đi; "vector như một kiểu dữ liệu + index" ở lại (giận dòng chữ observation của 5.15).
- **S6:** Khi RAG "trả lời tệ": đánh giá chunk → embedding → recall (đo!) → re-rank → mới tới DB. Đổi DB vector là phương án cuối, và thường sai chỗ.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| RAM nổ khi build index | HNSW full-precision | quantization; DiskANN | §2.1 |
| Kết quả "sai tenant" | Post-filter + ANN | filtered search | §2.4 |
| Recall thấp | PQ nén quá / ef_search thấp | eval set; tuning | §2.1 |
| RAG trả lời kém dù recall cao | Chunk/re-rank (không phải DB) | audit pipeline | §2.3 |
| Query chậm sau khi data lớn | Brute-force chưa index | EXPLAIN (pgvector) | §2.2 |
| Re-embed toàn bộ mỗi deploy model | Không có version embedding | embedding_version field | §2.3 |

---

## 6. Cách đo

```sql
-- pgvector: index đang dùng? (seq scan = chưa có HNSW)
EXPLAIN ANALYZE SELECT id FROM docs
  ORDER BY embedding <=> $1 LIMIT 20;

-- Recall đo trên eval set (bắt buộc — không đo = mù):
--   brute-force top-100 (ground truth) vs index top-100 → recall@100
```

Nguyên tắc: **recall là metric hợp đồng của ANN** — không có eval set + con số recall thì mọi tuning chỉ là cảm giác; 95% là sàn, 98%+ là mục tiêu thường thấy.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay dedicated store:** pgvector (SQL + một hệ ít hơn), CH/ES vector (đã có cluster text), Redis vector (đã có KV, real-time nhỏ). **Thay vector search hoàn toàn:** keyword + re-rank (BM25 đủ tốt cho corpus có cấu trúc); full-text cho code/ID chính xác. **Thay tự xây embedding:** API (đổi phụ thuộc lấy chất lượng/DModel) — cân nhắc latency + chi phí (→12.6).

Năm thấu kính:
- **Kinh tế:** RAM là chi phí chính của vector — quantization giảm 8–32× = bill giảm tương ứng; tính RAM theo công thức §2.2 trước khi chọn kiến trúc.
- **Vận hành:** Re-embed pipeline + embedding_version là "nợ kép": model đổi (chất lượng) vs giá re-embed (toàn bộ corpus) — lên lịch như migration schema (→4.7).
- **An ninh:** ACL ở retrieval (§2.3) — vector "gần nhau" không quan hệ quyền hạn; tenant filter phải là **ràng buộc cứng** (RLS — →5.14), không phải gợi ý.
- **Lịch sử:** 2019-2022 bùng nổ "vector DB startup"; 2023-2026 DB có sẵn nuốt dần (pgvector/CH/ES) — motif "tính năng hay thành công quá mức thành cột riêng": lặp lại của NoSQL decade trước (→5.2 lịch sử).
- **Người dùng:** Người dùng thấy "hệ thống hiểu ý tôi" (semantic hit) và "không lộ tài liệu người khác" (ACL đúng) — chương này là hai mặt của một lời hứa sản phẩm RAG.

---

## 8. Đọc tiếp & bài tập

- RAG toàn cảnh: **12.5** · Hybrid text+vector: **5.6** · pgvector trong PG: **5.2** · Multi-tenant: **5.14** · Ma trận: **5.15**
- **Bài tập 1:** Tính RAM index của bạn: N × D × 4 × 1,5. So với node hiện tại — còn dư bao nhiêu cho 1 năm nữa? Đó là kế hoạch quantization/re-architect.
- **Bài tập 2:** Xây eval set 50 câu + ground truth; đo recall@10 của hệ thống hiện tại. Con số này — không phải demo — là baseline mọi thay đổi sau này.
- **Bài tập 3:** Gửi query với filter tenant lạ (red team — →12.5): có kết quả trả về không? Nếu có, ACL đang ở prompt chứ không ở retrieval — sửa hôm nay.
