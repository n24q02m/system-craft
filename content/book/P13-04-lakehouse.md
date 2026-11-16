# 13.4 — Playbook: Analytics & Open Lakehouse

> **Tầng:** Nghiệp vụ · **Quyển III** · **Trục đọc:** playbook theo miền · **Động từ liên quan:** Áp dụng · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số) · **Đã verify 30/10: DuckDB 2.0 LTS, ClickHouse 26.10/26.8 LTS**
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.9 (lakehouse — nền) · 5.13 (governance).

**Sợi chỉ đỏ:** *Nước lũ dữ liệu — lakehouse phân tích tổ chức thế nào cho tin được?* — trả lời: nước lũ dữ liệu — lakehouse phân tích tổ chức theo medallion bronze-silver-gold, mỗi lớp một hợp đồng; chọn engine theo "câu hỏi nào" chứ không theo engine đang hot; độ tươi là bảng giá (mười phút đắt hơn hôm qua); catalog là xương sống; và chi phí lẫn chất lượng dữ liệu đều đo được. Câu hỏi để lại cho chương sau: *AI trong từng pipeline — AI-native khác 'dán chatbot vào sản phẩm' chỗ nào?*

**Thuật ngữ sẽ gặp:** *medallion* — bronze thô, silver sạch, gold tổng hợp: mỗi lớp một hợp đồng dữ liệu (nối 5.9); *engine theo câu hỏi* — BI ad-hoc, báo cáo định kỳ, huấn luyện ML: ba câu hỏi, ba lựa chọn; *độ tươi* — SLA từng bảng: mười phút, một giờ, hôm qua: mỗi mức một giá; *catalog* — ai sở hữu, nghĩa là gì, nằm ở đâu (nối 5.13): không catalog là không tin được; *chất lượng dữ liệu* — test như test code: null, freshness, anomaly: fail tại pipeline, không fail cuối tháng; *cost per query* — chi phí theo truy vấn và theo tầng: analytics cũng có ngân sách.

**Ví dụ mở đầu:** Dashboard CEO của DM số hôm qua lệch báo cáo tài chính 2%: không ai sai — hai bảng chạy hai đường với freshness khác nhau. Lakehouse chốt hợp đồng từng tầng: số nào ra lúc mấy giờ, ai chịu trách nhiệm. Chương này là playbook phân tích để chữ "tin được" có định nghĩa đo được.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Kiến trúc analytics: warehouse đóng vs open lakehouse | Dữ liệu phân tích của tôi **thoát được khỏi vendor** không — từng GB? |
| 2 | Bảng chuẩn hóa: kim cương (star) / dữ liệu thô + semantic layer | Người phân tích hỏi cùng một câu — mấy chỗ trả khác nhau? |
| 3 | ETL vs ELT vs batch-đêm: độ tươi cho từng câu hỏi | Dashboard "hôm qua" đủ — hay "10 phút trước"? |
| 4 | Catalog & governance: ai thấy bảng nào, data lineage | Dữ liệu nhạy trong analytics — ai kiểm soát? |

---

## 2. Cơ chế

### 2.1 Kiến trúc tham chiếu lakehouse mở

```
[Nguồn OLTP/Event] → [Ingest (13.3)] → [Object storage (S3-style — 5.9)]
   → [Bảng Iceberg (→5.9): Parquet + metadata — ACID, time travel]
      → [Compute tách: DuckDB 2.0 (nhỏ/ad-hoc/edge) · Spark-style (lớn)
        · ClickHouse (user-facing realtime — 5.8)]
   → [dbt-style transform: layers bronze→silver→gold (kinh điển)]
   → [Semantic layer: định nghĩa metric MỘT lần] → BI/dashboard/embedded
```
"Open" nghĩa là: **format mở (Parquet/Iceberg) + storage tiêu chuẩn + compute thay được** — không lock engine; warehouse đóng đổi mọi thứ tiện lấy thoát đắt (11.7 exit-plan).

### 2.2 Lớp lớp dữ liệu (bronze→silver→gold)

- **Bronze:** thô như nguồn (append, có lineage — phục hồi/audit);
- **Silver:** sạch + chuẩn hoá (đổi type, nối khoá, ghép event);
- **Gold:** bảng phục vụ câu hỏi (aggregate theo nghiệp vụ — "doanh thu theo ngày").
Quy tắc vàng: **business logic sống ở đúng một lớp** (gold) và **một semantic layer** — nếu 4 dashboard tự tính "doanh thu" 4 cách (điều xảy ra ở mọi tổ chức chưa có lớp này), mỗi cuộc họp là một cuộc tranh luận số liệu.

### 2.3 Chọn engine theo "câu hỏi nào"

| Câu hỏi | Engine | Ghi chú |
|---|---|---|
| Dashboard realtime user-facing | **ClickHouse** (5.8) | gộp + tốc |
| Ad-hoc phân tích file/bảng vừa | **DuckDB 2.0** (5.8) | một binary, không server; 2.0 có server mode + agent mode |
| Batch lớn/ETL | Spark-style | phân tán |
| BI chính thống + tài liệu hoá | Warehouse đóng | nếu chấp chi phí lock |
Luật: **cùng bảng Iceberg ở dưới** — đổi/tậu thêm engine là cấu hình, không di dân (đây là toàn bộ điểm của lakehouse).

### 2.4 Độ tươi — bảng giá "10 phút vs hôm qua"

Streaming ingest + ClickHouse: gần-realtime (đắt hạ tầng); micro-batch 15 phút: đa số dashboard đủ; batch đêm: báo cáo chuẩn hoá (rẻ, dễ audit). Chọn theo **hành vi quyết định**: số liệu để vận hành (cảnh báo) cần tươi; số liệu để họp tuần — hôm qua ổn. Đừng trả tiền tươi cho câu hỏi không cần.

### 2.5 Governance & catalog

Danh mục bảng (catalog — Iceberg REST catalog): schema, chủ sở hữu, nhãn nhạy cảm (PII/financial), lineage (bảng này từ đâu — 5.15 tư duy), **quyền theo vai** (10.3 ABAC áp xuống analytics: "phòng X thấy cột doanh thu phòng X"). Kèm chu kỳ sống: retention theo luật (5.13 — analytics không phải vùng luật bỏ qua: bảng dọn dần, query log có PII phải redact).

### 2.6 Cost & chất lượng dữ liệu

- **Chi phí:** object storage rẻ + compute tách (tắt khi không dùng — 11.5): lakehouse thắng warehouse ở "đôi lúc mới query"; warehouse thắng ở "query dày đều + quản lý ít người". Đo bằng đ/query (11.5 unit);
- **Chất lượng dữ liệu là SLO** (11.1 tư duy): test dữ liệu (null bất thường, tổng khớp nguồn — đối soát 13.1-style) chạy trong pipeline — fail = cảnh báo, không "dashboard đẹp nhưng sai".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| DuckDB | 2.0 LTS (21/10) — server mode, agent mode | V | versions.csv |
| ClickHouse | 26.10 monthly / 26.8 LTS (EOL 8/2027) | V | versions.csv |
| Iceberg | v3 (→5.9) | V | |
| Micro-batch điển hình | 5–15 phút | P | |
| Data test | trong pipeline, fail = alert | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Lakehouse mở = **tách lưu trữ khỏi compute** (5.9 → 13.4 ứng dụng): mỗi tầng thay độc lập — đây là kiến trúc "exit-plan hoá" cho analytics (11.7);
- **S2:** Tham số trụ: đ/query, độ tươi per dashboard (đo thật — không nhãn), số metric định nghĩa trùng lặp (semantic debt — mục tiêu 1), data test pass rate.
- **S3:** Semantic layer đổi kỷ luật tổ chức lấy "một con số cho một câu hỏi" — phần khó nhất không phải kỹ thuật mà là thỏa thuận (ADR — 11.6);
- **S4:** Analytics là **vùng PII lây lan nhanh nhất** (copy dữ liệu khắp nơi — 5.13/5.14): nhãn + quyền + retention phải theo kịp từng lớp bronze→gold;
- **S5:** DuckDB 2.0 "agent mode" (đã verify) + AI phân tích dữ liệu = **query từ agent tăng vọt**: rate limit + cost-per-query cho agent như user (12.6/12.4) — analytics giờ có "người dùng không phải người" cần chi phí & quyền riêng;
- **S6:** Khi "hai dashboard báo hai số": tra semantic layer — thiếu (ai cũng tự tính) hay lệch (một bên cũ)? Chữa ở lớp định nghĩa, không phải ở từng dashboard.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Hai dashboard hai số | Không semantic layer / stale | một định nghĩa + refresh | §2.2 |
| Query đắt quái quỷ | Scan Parquet không partition | partition + sort + prune | §2.1 |
| Đổi engine = di dân cả kho | Compute dính storage | bảng Iceberg tách | §2.3 |
| Bảng nhạy ai cũng select | Không catalog/quyền | nhãn + quyền theo vai | §2.5 |
| Dashboard "đẹp mà sai" | Không data test | test trong pipeline | §2.6 |
| Hóa đơn analytics leo thang | Query thừa (ai cũng scan) | cost per query + limit | §2.6 |

---

## 6. Cách đo

```bash
# Chi phí per query (đơn giản): log scan-bytes + thời gian mỗi query;
#   top 10 query đắt nhất tuần — mỗi query một cách tối ưu (partition? materialize?)
# Data test mẫu (chạy sau ingest):
#   assert: row_count hôm qua trong [0.5×, 2×] trung bình 7 ngày
#   assert: tổng doanh thu gold ≈ ledger (13.1 đối soát chéo — kim cương của playbook)
```

Nguyên tắc: **số liệu trong họp phải truy được nguồn trong ≤ 5 phút** (lineage + catalog) — không truy được thì cuộc họp đang quyết trên tín ngưỡng.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay lakehouse tự dựng:** warehouse đóng managed (nhanh, gọn, tiện — trả bằng lock + giá theo GB tăng năm thứ 3 — 11.7 bảng giá exit); **thay dbt-style:** SQL script + cron (được lúc 5 bảng — vỡ ở 50 khi không có lineage/test); **thay semantic layer:** "wiki định nghĩa metric" (văn hoá thay công cụ — yếu hơn nhưng khởi đầu trung thực).

Năm thấu kính:
- **Kinh tế:** Phân tích là **nơiROI của dữ liệu hiện ra** (mỗi insight → quyết định → tiền) — cũng là nơi đốt tiền vô hình (query vô nghĩa scan TB): đo hai chiều;
- **Vận hành:** Pipeline dữ liệu có on-call riêng khi "số sáng nay không ra" (11.4 vai — data incident là sự cố thật: quyết định sai vì dữ liệu trễ vẫn là sự cố);
- **An ninh:** Analytics = **bản sao dữ liệu nhạy nhân bản** (5.13/5.14 nguyên tắc theo từng lớp); audit "ai đã query bảng nhạy" là yêu cầu pháp lý thật (10.8);
- **Lịch sử:** EDW/Teradata (1980–90s) → Hadoop (2010s, hứa nhiều vận hành địa ngục) → cloud warehouse (2015+) → open lakehouse (2020s): mỗi thế hệ thề "một nơi cho mọi dữ liệu" rồi bị thế hệ sau thay — khác biệt lần này: **format mở** được chuẩn hoá trước khi lock — dấu hiệu ngành học được bài (hy vọng);
- **Người dùng:** Người dùng cuối của analytics là **người ra quyết định** (CEO, trưởng phòng) — họ không quan tâm Iceberg là gì; họ cần "con số này tin được không?" — lineage + test + một định nghĩa là ba từ kỹ thuật đứng sau câu đó.

---

## 8. Đọc tiếp & bài tập

- Iceberg/S3: **5.9** · OLAP engines: **5.8** · Ingest: **13.3** · Governance dữ liệu: **5.13, 5.14** · Semantic/API contract: **4.3** · Agent query: **12.6**
- **Bài tập 1:** Liệt kê 5 metric quan trọng nhất công ty — mỗi cái: định nghĩa ở đâu (file? wiki? đầu ai?) — hơn một nơi = semantic debt định lượng được (và là dự án có ROI rõ);
- **Bài tập 2:** Đối soát chéo một metric gold với nguồn sự thật (ledger 13.1 / OLTP): khớp không? lệch bao nhiêu %? Con số lệch đó là "chất lượng analytics" thật của tổ chức;
- **Bài tập 3:** Lấy top 10 query đắt nhất tuần (log): tối ưu 3 query đầu (partition/materialize) — thường trả tiền cho buổi làm này trong tháng.

