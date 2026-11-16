# 5.3 — Document & Embedded: MongoDB & SQLite

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** ds-18-mongo.md

---

## 0. Nhập môn

**Đọc trước:** 5.2 (đối chứng quan hệ).

**Sợi chỉ đỏ:** *Không phải gì cũng quan hệ — menu và giỏ hàng đổi hình dạng hoài: document store khi nào đúng?* — trả lời: khi dữ liệu đọc đúng theo hình ứng dụng và hình đó đổi thường xuyên — menu, giỏ hàng — document store hợp lý; quyết định thiết kế số một là nhúng hay tham chiếu (embedding vs referencing); và SQLite là vua của một vương quốc khác: DB nhúng trong app. Câu hỏi để lại cho chương sau: *Menu và tồn kho đọc lặp hàng triệu lần — cache dạy gì và phản bội gì?*

**Thuật ngữ sẽ gặp:** *document* — JSON có khóa, đọc theo hình ứng dụng: một lần đọc đủ cả cụm; *embedding vs referencing* — nhúng dữ liệu liên quan vào document, hay tách ra tham chiếu: quyết định số một; *shape drift* — hình document đổi theo phiên bản app: bệnh đặc thù phải quản; *schema validation* — bậc thang tự do: từ không ràng buộc tới validator chặt; *MongoDB 9.0* — document store trưởng thành, có transaction (trạng thái verify trong chương); *SQLite* — DB một file nhúng vào app: "phân tán" theo nghĩa đồng bộ file.

**Ví dụ mở đầu:** Giỏ hàng của DM: mỗi nhà hàng có topping, ghi chú, khuyến mãi khác nhau — ép vào bảng quan hệ là JOIN năm tầng mỗi lần đọc. Lưu document: một truy vấn đủ cả giỏ. Nhưng báo cáo tài chính cần chuẩn hoá bắt buộc. Chương này dạy chọn theo câu hỏi đọc nào xuất hiện nhiều nhất — không theo mode.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Document vs relational cho domain mới | Dữ liệu tôi đọc theo "tổng thể một object" hay "mặt cắt nhiều object"? |
| 2 | Embedding vs referencing trong document | Sub-document có vòng đời riêng và cần query riêng không? |
| 3 | SQLite ở đâu trong kiến trúc (edge/embedded/cache-local) | Đâu là nơi "một file DB" thắng hẳn client-server? |
| 4 | Schema validation mức nào cho document | Tự do tuyệt đối hay $jsonSchema ở biên ghi? |

---

## 2. Cơ chế

### 2.1 Tư duy document: đọc theo hình của ứng dụng

Document (BSON/JSON) gộp dữ liệu liên quan vào **một đơn vị lưu/tải** — không JOIN cho use case chính. Thắng khi: đọc theo aggregate (trang profile = 1 document), schema linh hoạt giữa các bản ghi, ghi theo "cả cụm". Thua khi: cần quan hệ chéo + ràng buộc toàn vẹn (ngoại khóa, chuẩn hoá) — document DB lặp dữ liệu để đổi tốc độ đọc, và cập nhật lặp = nhánh sync tay (nợ dữ liệu).

### 2.2 Embedding vs referencing — quyết định thiết kế số một

| Tiêu chí | Nên embed | Nên reference |
|---|---|---|
| Vòng đời | cùng chết với cha | tồn tại độc lập |
| Đọc | luôn đọc cùng cha | query riêng/lọc riêng |
| Số lượng | chục–trăm item | hàng nghìn, không chặn 16 MB |
| Cập nhật | cả cum hiếm khi đổi | item đổi liên tục độc lập |

**Bẫy unbounded array:** nhét comment/post vào mảng user — document 16 MB trần (V MongoDB), mỗi push ghi lại cả vùng — lúc nào đó nghẽn. Quy tắc: mảng có khả năng vô hạn → collection riêng + reference.

### 2.3 MongoDB 9.0 (verify 2026-10: 9.0.4)

Điểm nổi bật thế hệ gần đây: queryable encryption trưởng thành, thời gian sử dụng mảnh (shard) cải tiến, `$search` tích hợp Atlas (nếu dùng Atlas). Lõi vận hành không đổi: **replica set** (primary + secondaries, election — →8.2) + **sharding theo shard key** (phân mảnh — →5.5 áp dụng tương tự). Index: giống như RDBMS (compound, partial, TTL) — nhưng **không có transaction chéo shard giá rẻ** (distributed txn tồn tại, đắt — dùng đúng chỗ).

### 2.4 SQLite: DB phân tán… theo nghĩa khác

Một file, nhúng trong process, không server — **nhanh nhất ở lớp truy vấn** (không network, không IPC): đọc hàng trăm nghìn rows/s dễ (I). Vai trò 2026:
- **Edge/client:** browser (Wasm — OPFS/SQLite WASM), mobile, desktop app — nơi không có server;
- **FaaS/local state:** file theo request/pod (kèm immutable volume);
- **Format dữ liệu khoa học/trao đổi** (thay CSV/parquet nhỏ) — mọi ngôn ngữ đọc được;
- **LiteFS/rqlite/turso** biến SQLite thành cluster (replicate file) — phục vụ read-heavy geo-distributed nhỏ.

**Giới hạn không vượt:** concurrent write cao (một writer — WAL mode cho phép reader song song), traffic client-server lớn (chọn PG). Phiên bản verify: 3.54.1 (10/2026).

### 2.5 Schema validation document — bậc thang tự do

1. Không validate (prototype);
2. `$jsonSchema` validator ở collection: bắt field bắt buộc + type lúc ghi — **đề xuất mặc định cho production** (bẫy số 12 →3.9 giảm);
3. Validation ở tầng ứng dụng (Zod/Pydantic — →4.3) trước khi ghi.

Lựa chọn 2+3 kết hợp: validator DB là "lưới cuối", app validate cho thông báo đẹp.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| MongoDB | 9.0.4 (10/2026) | V | versions.csv |
| SQLite | 3.54.1 (10/2026) | V | |
| Document max (Mongo) | 16 MB | V | |
| SQLite đọc | hàng trăm k rows/s | I | trong process |
| SQLite writer | 1 (WAL mode: reader song song) | V | |

---

## 4. Suy luận kiến trúc

- **S1:** Document đổi chuẩn hoá (đổi thiếu nhất quán) lấy tốc độ đọc aggregate — chỉ đáng khi **đọc đúng hình ghi**; sai hình thì nợ dữ liệu sinh lãi kép.
- **S2:** Tham số trụ: document size p99, số collection "rác" không validator, cache hit (WiredTiger), oplog lag replica.
- **S3:** SQLite đổi tính concurrent-write lấy zero-ops — từng vai trò (edge/embedded) thay vì "DB chính" là câu trả lời đúng.
- **S4:** Edge computing + Wasm (→3.8) kéo SQLite về vị trí "DB mặc định của client" — xu hướng tích cực từ 2023, chưa có dấu hiệu dừng.
- **S5:** AI local (cache hội thoại, metadata model) dùng SQLite/duckdb file — dạng "database nhỏ nhiều node" ăn theo edge AI (→12.x).
- **S6:** Khi document DB "chậm": kiểm tra unbounded array + missing index + working set > RAM — ba thủ phạm phổ biến nhất theo thứ tự.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Document chạm 16 MB | Unbounded array | schema audit | §2.2 |
| Dữ liệu lệch giữa 2 collection | Lặp dữ liệu không có sync | audit update path | §2.1 |
| Ghi chậm dần | Working set > RAM / index thiếu | mongotop/mongostat | §2.3 |
| SQLite "database is locked" | Nhiều writer | WAL mode; hàng đợi ghi | §2.4 |
| Field "biến mất" trong document | Không validator + code cũ | $jsonSchema | §2.5 |
| Query chéo collection chậm | Nên reference/embed lại | $lookup frequency | §2.2 |

---

## 6. Cách đo

```bash
# MongoDB: kích thước document + query chậm
db.coll.aggregate([{$project: {sz: {$bsonSize: "$$ROOT"}}}, {$sort: {sz: -1}}, {$limit: 5}])
db.setProfilingLevel(1, {slowms: 100})   # log query > 100ms

# SQLite: integrity + hiệu năng
sqlite3 app.db 'PRAGMA integrity_check;'
sqlite3 app.db 'PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;'
time sqlite3 app.db 'SELECT count(*) FROM events;'
```

Nguyên tắc: **đo hình document trước khi tối ưu query** — 90% vấn đề Mongo là hình (embed/reference), không phải index.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Mongo:** PostgreSQL + JSONB (một DB hai thế giới — transaction + document; mở rộng pgvector — →5.10). **Thay SQLite ở edge:** DuckDB cho analytics cục bộ (→5.8); file thường/parquet cho data lớn nhất quán. **Thay document model:** chuẩn hoá lại trong RDBMS khi ràng buộc quan hệ xuất hiện dày — biết quay về cũng là kỹ năng.

Năm thấu kính:
- **Kinh tế:** Mongo Atlas (managed) đắt theo dữ liệu lưu — tính lifecycle (TTL/archive — →5.13) từ ngày một để tránh hóa đơn phình.
- **Vận hành:** Replica set election (→8.2) xảy ra lúc network chập chờn — runbook phải có nhánh "primary đổi trong lúc đang deploy".
- **An ninh:** NoSQL injection (cho object query từ input thô) là họ hàng SQL injection — validate/parameter hoá query builder (→10.4).
- **Lịch sử:** Mongo "web scale" (2010s meme) → tỉnh lặng → vị thế thật: agile schema + aggregate reads; SQLite đồng thời đi từ "thứ của mobile" thành "format dữ liệu phổ quát" — hai bài học về kỳ vọng vs hiện thực.
- **Người dùng:** Người dùng thấy "màn hình profile load một phát" (document đúng hình) — hoặc "dữ liệu hai nơi không khớp" (document sai hình). Chương này là về hai trải nghiệm đó.

---

## 8. Đọc tiếp & bài tập

- Ma trận datastore: **5.15** · Sharding sâu: **5.5** · JSONB trong PG: **5.2** · Edge/Wasm: **3.8** · TTL/retention: **5.13**
- **Bài tập 1:** Với collection chính: đo $bsonSize p99 (§6). > 100 KB? Tìm mảng vô hạn — tái cấu trúc theo bảng §2.2.
- **Bài tập 2:** Đếm collection không có $jsonSchema. Mỗi cái là một "đường ống không van" cho dữ liệu bẩn.
- **Bài tập 3:** Viết poc SQLite WAL + 4 thread đọc + 1 thread ghi cho use case cache cục bộ. So với file JSON nạp mỗi lần — số liệu sẽ tự thuyết phục team.
