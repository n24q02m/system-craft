# 5.15 — Ma trận Chọn Datastore, Outbox/CDC & 20 Bẫy

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** ds-26-matrix.md

---

## 0. Nhập môn

**Đọc trước:** Lướt 5.1–5.14 — mỗi loại store một hàng của ma trận.

**Sợi chỉ đỏ:** *Đủ loại store — 'entity này sống ở đâu' chọn theo cái gì?* — trả lời: chọn store theo trục câu hỏi truy vấn — đọc theo hình gì, truy vấn kiểu gì, độ trễ bao nhiêu — chứ không theo "DB mới đang hot"; và khi dữ liệu nằm nhiều nơi thì dual-write là bug, outbox + CDC mới là hợp đồng giữ các bản sao khớp nhau. Câu hỏi để lại cho chương sau: *Chốt hạ tầng dữ liệu: bao nhiêu node, bao nhiêu GB, bao nhiêu tiền — tính kiểu gì?*

**Thuật ngữ sẽ gặp:** *ma trận truy vấn* — hàng workload, cột store: điểm rơi trả lời "entity này sống ở đâu"; *dual-write* — ghi hai store trong một transaction trông như được: là bug phân tán chờ ngày nổ; *outbox* — ghi sự kiện vào DB chính rồi propagate: một nguồn thật; *CDC* — change data capture: đọc WAL phát sự kiện ra ngoài; *polyglot đúng cách* — nhiều store, mỗi store một hợp đồng trục và một chủ sở hữu; *HTAP* — một máy hai workload: trào lưu hợp nhất 2026 và giới hạn của nó.

**Ví dụ mở đầu:** Menu ở document, tồn kho ở KV, đơn ở Postgres, tìm kiếm ở search engine — mỗi câu "dữ liệu này sống ở đâu" đều có lý, cho tới lúc các bản sao lệch nhau: dual-write tối nay ghi Postgres được nhưng cache miss. Outbox + CDC: một nguồn thật, các bản sao theo sau. Chương này chốt ma trận chọn và hai mươi bẫy tổng kết cả chương 5.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Họ datastore cho workload (đọc ma trận, không đọc trend) | Câu hỏi truy vấn + nhất quán + scale của tôi là gì? |
| 2 | Đồng bộ đa store: outbox + CDC hay dual-write | Tôi chấp nhận lệch bao lâu giữa DB và search/cache? |
| 3 | "Một loại cho tất cả" hay "đúng họ cho từng bài" | Ops đội hình của tôi nuôi được mấy loại? |
| 4 | Exit plan (đổi datastore khi sai) | Dữ liệu + query của tôi thoát được không — hay bị khóa? |

---

## 2. Cơ chế

### 2.1 Ma trận chọn — trục câu hỏi truy vấn

| Câu hỏi chính của workload | Họ | Chương |
|---|---|---|
| Giao dịch ACID + quan hệ chặt | RDBMS | 5.2 |
| Đọc theo hình object aggregate | Document | 5.3 |
| Đọc/ghi hot key + TTL | KV/Cache | 5.4 |
| Ghi phân tán rất lớn, availability > nhất quán | Wide-column | 5.5 |
| Full-text + relevance + facet | Search | 5.6 |
| Retain + replay, nhiều consumer độc lập | Log/Stream | 5.7 |
| Quét cột lớn + aggregate | OLAP/Columnar | 5.8 |
| Lưu rẻ + bền + version | Object/Lake | 5.9 |
| Láng giềng ngữ nghĩa (vector) | ANN | 5.10 |
| Đi qua quan hệ biến thiên / chuỗi thời gian | Graph / TS | 5.11 |

Ba câu phượt trước khi chọn: (1) query thật là gì (viết ra 3 câu đại diện); (2) nhất quán cần gì (stale được bao lâu — →8.1); (3) scale thật (GB, QPS — không phải "sẽ to lắm"). **90% hệ mới chỉ cần một RDBMS + một cache + một log** — thêm store phải trả lời được "câu query nào không thể ở store đã có".

### 2.2 Dual-write là bug; outbox + CDC là hợp đồng

```
SAI: [tx DB] + [publish Kafka] + [update cache]  ← 3 bước, chết giữa chừng = lệch vĩnh viễn
ĐÚNG: [tx: DB write + outbox row] → [CDC/relay đọc outbox → Kafka → consumer cập
       nhật cache/search]  ← 1 bước nguyên tử + eventually consistent có kiểm soát
```

Dual-write lệch khi bước 2/3 fail — không có rollback chéo. **Outbox**: sự kiện nằm trong cùng transaction dữ liệu (guarantee nguyên tử); CDC (Debezium) hoặc relay (poller) bơm ra Kafka; consumer idempotent (→4.8) cập nhật rãnh phụ (search, cache, lake). Lag đo được = "độ lệch chấp nhận được" trở thành **SLA**, không phải may mắn. (Kafka transactional outbox — cùng tư duy 5.7.)

### 2.3 Polyglot đúng cách: hợp đồng trục

Nhiều store = nhiều nợ sync + nhiều ops. Ba kỷ luật giữ polyglot sống: (a) **một nguồn chân lý** cho mỗi entity (các store còn lại là projection — xây lại được); (b) schema registry xuyên suốt (→4.7); (c) mỗi store có owner + runbook. Không đủ ba — nên rút về ít store hơn.

### 2.4 20 bẫy datastore (tổng kết chương 5)

**Chọn sai (5):** 1 chọn theo trend không theo query; 2 dùng OLTP làm analytics (hoặc ngược); 3 thiếu exit plan; 4 thêm store cho bài không cần; 5 "sẽ scale" khi chưa cần.
**Đồng bộ (5):** 6 dual-write; 7 consumer không idempotent; 8 schema đổi không registry; 9 không đo lag CDC; 10 đọc-after-ghi qua projection không tính stale window (→8.1).
**Vận hành (5):** 11 insert nhỏ liên tục vào CH; 12 tombstone/hot-partition wide-column; 13 cardinality nổ TSDB; 14 small-file lakehouse; 15 backup chưa từng restore.
**An toàn dữ liệu (5):** 16 thiếu RLS multi-tenant; 17 erasure không xuyên lớp; 18 cache evict policy sai (mất key im lặng — →5.4); 19 secret/PII trong metric label; 20 "giữ mãi" không ai ký tên.

### 2.5 HTAP & hợp nhất 2026 — trào lưu ngược

Trào lưu "một DB làm tất cả" quay lại: PG + columnar extension / replica CH (hybrid read), ClickHouse thêm transactional nhẹ + vector, lakehouse query engine mạnh thêm (DuckDB/Trino đọc thẳng). Hợp nhất giảm **số hệ ops** nhưng không xoá **chuyên môn theo workload** — quyết định "bao nhiêu store" là bài toán ops, không phải bài toán kỹ thuật thuần.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Số store trung bình hợp lý | 2–4/org | P | hơn = cần platform team |
| CDC lag mục tiêu | s–phút theo use case | P | SLA hoá |
| Outbox overhead | 1 insert/tx | P | rẻ so với dual-write risk |
| "Chỉ cần RDBMS+cache+log" | 90% hệ mới | P | §2.1 |

---

## 4. Suy luận kiến trúc

- **S1:** Datastore là **hợp đồng 5 năm với workload** — đổi loại = migration dữ liệu + code + ops; lựa chọn đáng sợ nhất trong hệ thống, đáng chậm nhất.
- **S2:** Tham số trụ: query p99 theo họ store, CDC lag, số projection/  entity, ops burden (số runbook).
- **S3:** Mỗi store thêm đổi "đúng nghề cho một query" lấy "một hệ nữa để vận hành + sync" — phép cộng phải dương sau khi trừ ops.
- **S4:** Hợp nhất (HTAP, lakehouse query) và chuyên môn hoá (vector, graph) diễn ra **đồng thời** — chu kỳ 5–7 năm; kế hoạch nên ghi rõ đứng đâu và thoát thế nào.
- **S5:** AI kéo dữ liệu về các hình mới (embedding là projection; graph là quan hệ tri thức) — nhưng nguyên tắc §2.2–2.3 (một nguồn chân lý + registry + idempotent) phủ luôn lớp AI (→12.5 corpus).
- **S6:** Khi "hệ dữ liệu rối": vẽ ma trận thật (store × entity × sync path) — gần như luôn tìm thấy dual-write và projection không chủ.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| DB và search/cache lệch nhau | Dual-write (không outbox) | reconciliation job; audit write path | §2.2 |
| "Sẽ scale" chưa từng tới | Chọn sớm store phức tạp | review ma trận | §2.1 |
| Đổi model phải dừng dịch vụ | Thiếu exit plan | export/import drill | §2.1 |
| Ops quá tải nhiều store | Polyglot không kỷ luật | rút về 3 store | §2.3 |
| Không biết độ lệch hiện tại | Không đo CDC lag | lag metric | §2.2 |

---

## 6. Cách đo

```bash
# Reconciliation (sự thật phơi bày sync):
#   đếm/checksum entity trong DB vs projection (search/cache/lake)
#   chạy định kỳ — lệch > ngưỡng = bug §2.2 đang sống

# CDC lag: timestamp CDC event - event_time (Debezium metric / consumer)
# Outbox depth: outbox chưa relay (chờ > 1 phút = relay chết?)
```

Nguyên tắc: **mọi quan hệ sync giữa store phải có reconciliation** — như mọi cache phải có cold-start plan (→5.4): không kiểm chứng được = không có gì.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay polyglot:** RDBMS làm nguồn + ít projection nhất (pgvector thay vector DB, FTS thay ES tới ngưỡng nào đó — ngưỡng ở 5.6/5.10 có số). **Thay outbox tự dựng:** Debezium (CDC từ WAL — không đổi schema), hoặc transactional messaging của broker nếu đã dùng. **Thay ma trận:** ADR (architecture decision record) cho mỗi lần thêm store — chống " creep theo trend".

Năm thấu kính:
- **Kinh tế:** Chi phí datastore = hạ tầng + ops + sync + rủi ro migration; bảng tính 3 năm với 4 dòng đó thường giết "công nghệ hot" trong 10 phút.
- **Vận hành:** Runbook mỗi store (restore, upgrade, sự cố thường gặp) — không viết nổi runbook = chưa sẵn có store đó.
- **An ninh:** Mỗi store thêm một bề mặt (auth, mã hoá, leak — 20 bẫy mục 4); inventory store + dữ liệu PII = điều kiện compliance (→5.13).
- **Lịch sử:** 2010s NoSQL "SQL đã chết"; 2015s NewSQL; 2020s đặc hoá (vector/graph/log); SQL vẫn ở giữa mọi làn sóng — vì "giao dịch + quan hệ + khai báo" là bài toán không hết.
- **Người dùng:** Người dùng không biết có bao nhiêu datastore — họ biết "tìm ra, thấy đúng, không mất". Ma trận này là bản đồ để giữ ba từ đó với chi phí thấp nhất.

---

## 8. Đọc tiếp & bài tập

- Toàn bộ 5.1–5.14 là chi tiết của ma trận này · Sync/consistency sâu hơn: **8.1** · Outbox vận hành: **5.7** · Registry: **4.7** · Sizing: **5.16**
- **Bài tập 1:** Vẽ ma trận store × entity của hệ bạn (thật, từ config). Đánh dấu từng quan hệ sync: outbox hay dual-write? Mỗi dual-write là P1 ẩn.
- **Bài tập 2:** Chạy reconciliation một entity (checksum DB vs search). Lệch hiện tại bao nhiêu? Con số đó là SLA thật (không cam kết) của hệ.
- **Bài tập 3:** Với store "mới toanh nhất" của org: viết 5 dòng ADR — query nào không thể ở store cũ? Nếu viết không ra — đó là creep, không là kiến trúc.
