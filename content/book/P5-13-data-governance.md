# 5.13 — Quản trị Dữ liệu (DAMA cho kỹ sư)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Quản trị · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.9 (nơi dữ liệu nhân bản) · 4.7 (metadata sự kiện).

**Sợi chỉ đỏ:** *Dữ liệu cá nhân của khách — ai được giữ gì, bao lâu, xoá kiểu gì (governance)?* — trả lời: governance không phải giấy tờ — là metadata vận hành: ai sở hữu, giữ bao lâu, xoá kiểu gì; bài toán khó nhất là "xoá thật" vì dữ liệu nhân bản qua cache, log, lakehouse và cả backup. Câu hỏi để lại cho chương sau: *Nhiều chuỗi nhà hàng dùng chung DM — multi-tenancy tách dữ liệu tới đâu thì đủ?*

**Thuật ngữ sẽ gặp:** *ownership* — mỗi dataset đúng một người chịu trách nhiệm: không có chủ là không ai giữ; *retention theo độ nóng* — hot/ấm/lạnh: TTL giảm dần theo tầng, không mặc định vô hạn; *xoá thật* — GDPR và Nghị định 13: phải tới được mọi bản sao, kể cả backup — là một pipeline, không phải một câu DELETE; *tombstone* — xoá logic đánh dấu chờ dọn: nối 5.5; *catalog* — DataHub/OpenMetadata: nơi "dữ liệu gì, ở đâu, ai giữ" có câu trả lời; *data contract* — schema + SLA giữa producer và consumer: nối 4.3.

**Ví dụ mở đầu:** Khách DM yêu cầu "xoá hết dữ liệu của tôi". Nếu chỉ có DB chính thì dễ — nhưng bản sao nằm ở cache, Kafka giữ bảy ngày, backup chín mươi ngày, bảng silver trong lakehouse. Chương này thiết kế xoá như một pipeline có kiểm chứng, retention theo độ nóng, và chất lượng dữ liệu được test như test code.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Retention policy cho từng loại dữ liệu | Dữ liệu nào giữ bao lâu — ai phê duyệt "giữ mãi mãi"? |
| 2 | Xoá thật (GDPR erasure) xuyên bao nhiêu lớp | DB, cache, log, backup, lake, index — liệt kê đủ chưa? |
| 3 | Catalog + ownership: mỗi dataset có chủ | Ai chịu trách nhiệm chất lượng/xoá/schema của bảng X? |
| 4 | Phân loại dữ liệu (public/internal/confidential/PII) | Dataset của tôi ở mức nào — và điều đó kéo theo gì? |

---

## 2. Cơ chế

### 2.1 Quản trị không phải giấy tờ — là metadata vận hành

Mô hình DAMA rút gọn cho kỹ sư: **quản trị = quyết định có thể tra cứu tự động**. Ba câu cốt lõi: dữ liệu này **là gì** (định nghĩa/schema — →4.3/4.7), **của ai** (owner), **sống bao lâu** (retention/lifecycle). Nếu ba câu trả lời nằm trong đầu ba người — chưa có quản trị, chỉ có hy vọng.

### 2.2 Retention — thiết kế theo "độ nóng", không mặc định vô hạn

| Lớp | Ví dụ | Giữ |
|---|---|---|
| Nóng | telemetry 7 ngày | giờ–tuần (→5.11) |
| Ủng | log ứng dụng, metric 90 ngày | tháng (→5.7/5.9) |
| Lạnh | sự kiện nghiệp vụ, audit | năm (lakehouse — →5.9) |
| Pháp chế | hoá đơn, y tế | theo luật (immutable + WORM) |

Mỗi bậc rẻ hơn bậc trên ~10× (→5.9). "Giữ tất cả trên NVMe 1 năm" là quyết định tài chính ngầm chưa ai ký.

### 2.3 Xoá thật — bài toán khó vì dữ liệu nhân bản

Yêu cầu "xoá dữ liệu người dùng" (GDPR và các luật tương tự) phải xuyên qua: DB chính → replica lag → CDC stream → lake (iceberg delete + rewrite — →5.9) → cache (→5.4: TTL + eviction chủ động) → **backup** (không xoá được trong bản sao cũ — giải pháp: xoá khi restore, hoặc mã hoá per-tenant + huỷ key — **crypto-shredding**) → log & index (→5.6: reindex hoặc delete). Mỗi mũi tên là một lớp dễ quên; **danh sách "nơi dữ liệu này tồn tại" là artifact quản trị quan trọng nhất** — gọi là data map; không có nó, erasure là cam kết không thể kiểm chứng.

### 2.4 Catalog & ownership — minimum viable governance

Không cần công cụ to (Collibra...) để bắt đầu: catalog tối thiểu = bảng trong DB meta: `dataset, owner, classification, retention, nơi nhân bản, PII?`. Quy tắc: **PR tạo dataset mới mà không điền catalog = fail CI** (như spec API — →4.3). Ownership đi theo **domain** (data mesh-lite): team sản xuất dữ liệu sở hữu chất lượng của nó (schema + freshness + chất lượng), team tiêu thụ hợp đồng qua schema registry (→4.7).

### 2.5 Chất lượng dữ liệu: test như test code

- Expectation theo cột: not-null, range, referential, freshness (dbt tests / Great Expectations / soda);
- Chạy trong pipeline (→5.12): fail → chặn xuống gold + alert — dữ liệu xấu **không được lan**;
- Data quality SLA: "độ trễ", "tỉ lệ null", "số bản ghi ngoài vùng" — metric như p99.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| GDPR erasure deadline | 30 ngày (pháp lý) | V | cơ sở EU |
| Chi phí nóng vs lạnh | ~10× mỗi bậc | I | →5.9 |
| Data map | artifact bắt buộc | P | §2.3 |
| Catalog MVP | 1 bảng + CI rule | P | §2.4 |

---

## 4. Suy luận kiến trúc

- **S1:** Mọi dữ liệu không có retention là **nợ pháp lý + tài chính lãi kép** — thiết kế lifecycle là bài toán kiến trúc, không phải việc "sau này dọn".
- **S2:** Tham số trụ: số dataset có owner/retention đầy đủ (%), PII dataset có data map, freshness SLA pass rate.
- **S3:** Crypto-shredding đổi chi phí mã hoá lấy khả năng xoá backup — thường là cách duy nhất xoá được dữ liệu đã backup.
- **S4:** Luật (GDPR nay + các luật data locality Đông Nam Á/Trung Quốc) đang thành ràng buộc kiến trúc như PCI từng là — thiết kế phân loại + residency từ ngày đầu rẻ hơn tái cấu trúc sau.
- **S5:** AI làm quản trị cấp bách hơn: RAG đưa dữ liệu nội bộ vào output — PII lọt qua retrieval là sự cố compliance **và** an ninh (→12.5); lineage (graph — →5.11) là nền audit AI.
- **S6:** Khi "dữ liệu ai đó xoá vẫn hiện": đi theo data map từng lớp — gần như chắc chắn thiếu một lớp trong danh sách, không phải DB chính.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Yêu cầu xoá không hoàn tất | Thiếu lớp trong data map | audit theo §2.3 | §2.3 |
| Hóa đơn lưu trữ phình | Không retention phân tầng | cost theo lớp | §2.2 |
| "Bảng này của ai?" im lặng | Không catalog/owner | catalog query | §2.4 |
| Dữ liệu xấu vào báo cáo | Không data test | dbt test trong pipeline | §2.5 |
| Restore backup lòi dữ liệu đã "xoá" | Không crypto-shred | per-tenant key | §2.3 |
| Metric PII lộ trong label | Không quy ước phân loại | label audit (→5.11) | §2.4 |

---

## 6. Cách đo

```sql
-- Catalog coverage — con số quản trị thật duy nhất
SELECT count(*) FILTER (WHERE owner IS NOT NULL AND retention IS NOT NULL)::float
     / count(*) AS coverage FROM meta.datasets;
-- < 80%: việc quý này có tên

-- Data map kiểm chứng: chọn 1 PII dataset, đếm nơi lưu thật
-- (DB + replica + CDC topic + lake + cache + log + backup) vs danh sách trong map
```

Nguyên tắc: **quản trị đo bằng coverage và kiểm chứng chéo**, không bằng số cuộc họp.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay công cụ to:** catalog MVP (bảng + CI) + registry (→4.7) + freshness metric — 80% giá trị với 1% giấy phép; công cụ khi > ~50 team. **Thay xoá xuyên lớp:** pseudonym hoá ngay tại nhập (token vault) — xoá = xoá vault, phần còn lại vô nghĩa.

Năm thấu kính:
- **Kinh tế:** Phân tầng retention là tiết kiệm 5–10× vô điều kiện (vật lý giá — →5.9); "giữ mãi" phải là quyết định có chữ ký của người trả tiền.
- **Vận hành:** Data map nên là **code** (file trong repo — review như schema), không phải diagram cập nhật bằng trí nhớ.
- **An ninh:** Phân loại dữ liệu quyết định mã hoá/audit/access (→10.x) — phân loại sai là lỗ hổng cấu trúc, không phải config.
- **Lịch sử:** "Data governance" từng là phòng ban thủ công; 2020s chuyển thành metadata trong pipeline (dbt/catalog/lineage) — quản trị tự động hoá được sống sót, còn lại là PDF.
- **Người dùng:** Người dùng thấy "xin xoá dữ liệu — 30 ngày sau thật sự sạch" — đó là niềm tin sản phẩm 2026, xây từ data map + retention + shredding, không từ chính sách bảo mật PDF.

---

## 8. Đọc tiếp & bài tập

- Lakehouse lifecycle: **5.9** · Schema registry: **4.7** · Pipeline test: **5.12** · PII & security: **10.6** · AI compliance: **12.6**
- **Bài tập 1:** Tính catalog coverage (§6). Con số đó là "nhiệt độ quản trị" — công bố trong retro, đặt mục tiêu quý.
- **Bài tập 2:** Chọn 1 dataset PII: liệt kê nơi nó tồn tại (data map). So với danh sách "chính thức" — mỗi chênh lệch là một erasure sẽ thất bại.
- **Bài tập 3:** Đề xuất phân tầng retention cho 5 dataset to nhất. Ước tính tiết kiệm/tháng — bản trình bày đó thường được duyệt nhanh bất ngờ.
