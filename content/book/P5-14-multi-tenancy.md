# 5.14 — Kiến trúc Đa thuê bao ở Tầng Dữ liệu

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ loại (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.2 (nơi các bệnh xuất hiện) · 4.7 (sự kiện theo tenant).

**Sợi chỉ đỏ:** *Nhiều chuỗi nhà hàng dùng chung DM — multi-tenancy tách dữ liệu tới đâu thì đủ?* — trả lời: ba mô hình — shared schema (một bảng, cột tenant), schema-per-tenant, database-per-tenant — đổi nhau chi phí vận hành lấy độ cô lập; pool + RLS là khung "tenant cứng" giá rẻ; noisy neighbor ở tầng dữ liệu có cách đo và cách chữa. Câu hỏi để lại cho chương sau: *Đủ loại store — 'entity này sống ở đâu' chọn theo cái gì?*

**Thuật ngữ sẽ gặp:** *shared schema + RLS* — một bảng với cột tenant_id, policy chặn ở chính tầng DB: mặc định của 80% tenant nhỏ; *schema/database-per-tenant* — cô lập thật nhưng vận hành nhân lên: dành tenant to; *noisy neighbor* — một tenant ăn hết IOPS làm chậm cả bảng chung; *chargeback* — đo và phân bổ chi phí theo tenant: không đo thì không đàm phán nổi; *index lồng tenant_id* — composite index đặt tenant_id đầu tiên: nếu không, truy vấn tenant này quét cả tenant khác; *escape hatch* — đường di chuyển mô hình cho tenant phình to: thiết kế sẵn từ ngày đầu.

**Ví dụ mở đầu:** DM phục vụ nhiều chuỗi nhà hàng: chuỗi nhỏ cần rẻ (shared), chuỗi lớn đòi cô lập và tuỳ biến (riêng DB). Bẫy nằm ở chi tiết: index không đặt tenant_id đầu tiên — mọi truy vấn đều chậm lên vì quét của người khác. Chương này cho ba mô hình, bảng đổi, và đường chạy trốn giữa chúng khi tenant phình.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Mô hình: silo / bridge (schema) / pool (share bảng + RLS) | Tốt nghiệp đường nào theo quy mô tenant? |
| 2 | Row-Level Security + tenant_id invariant | Mọi truy vấn có "khung tenant" cứng chưa — kể cả của DBA? |
| 3 | Noisy neighbor ở tầng dữ liệu (quota/limit) | Tenant lớn có dập được tenant nhỏ trong shared DB không? |
| 4 | Đường "tách tenant lớn" (escape hatch) | Từ pool lên silo — quy trình và chi phí đã thiết kế chưa? |

---

## 2. Cơ chế

### 2.1 Ba mô hình — ba đổi khác

| Mô hình | Cách | Đổi lấy | Hợp |
|---|---|---|---|
| **Silo** (DB riêng/tenant) | infra riêng | isolation tuyệt đối + ops ×N | tenant to, y tế/tài chính, số tenant nhỏ |
| **Bridge** (schema riêng) | 1 cụm, schema/tenant | isolation tốt, số schema có giới hạn (vài nghìn) | SaaS vừa, tenant trung bình |
| **Pool** (bảng dùng chung + `tenant_id` + RLS) | 1 lược đồ | chi phí/tenant rẻ nhất, đông tenant (10k+) | SaaS số đông, tenant nhỏ |

Đường thực tế của SaaS: **pool mặc định → bridge cho tenant trả tiền nhiều → silo cho enterprise** — cùng codebase, khác provisioning. Điều kiện để đường này không chết: **tenant_id phải là dimensional key xuyên suốt** (mọi bảng, mọi event — →4.7, mọi index — →5.5 partition key).

### 2.2 Pool + RLS: bộ ba "khung tenant" cứng

```sql
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant')::uuid);

-- BẮT BUỘC: SET app.tenant = '<id>' ở connection checkout (pool middleware)
-- VÔ hiệu: superuser/owner bỏ qua RLS — app user thường, không bao giờ root
```

Ba lớp vô hiệu hóa phổ biến: (1) query quên đi qua path đặt biến; (2) role app là table owner (RLS bị bỏ qua); (3) bảng mới tạo quên policy (CI phải check: **mọi bảng có tenant_id phải có policy**). Quy tắc vàng: **tenant filter là ràng buộc của lớp dữ liệu, không phải điều kiện WHERE trong code** — code là con người, người quên.

### 2.3 Noisy neighbor ở tầng dữ liệu

- **Pool:** tenant lớn chiếm buffer pool/CPU → tenant nhỏ chậm. Thuốc: connection quota theo tenant (pgbouncer per-db/user), statement timeout theo tenant, resource queue;
- **Bridge/silo:** tính toán IOPS/đĩa chia sẻ (→2.4 io.max; →1.4 WAF dồn);
- **Search/vector:** shard theo tenant lớn (→5.6/5.10), index riêng cho top-N tenant — "co-locate với dữ liệu" quyết định p99 của người nhỏ.

### 2.4 Đo lường & phân bổ chi phí theo tenant

Pool rẻ nhưng **chi phí mù**: ai tốn gì? Cần: usage metering (rows, storage, query bytes) theo tenant từ đầu — vì sau này gắn giá phải có; và đây cũng là input cho "đề nghị lên bridge/silo" (tenant vượt ngưỡng X).

### 2.5 Migration giữa mô hình (escape hatch)

Pool → bridge: dump theo tenant → restore schema riêng → đổi routing tenant → đối chiếu (checksum) — **chạy được khi cần là đòi hỏi thiết kế từ đầu**: tenant_id + mọi service đọc routing từ bảng trung tâm (không hard-code), CDC có thể lọc theo tenant (→5.15). Không escape hatch = "tenant lớn nhất sẽ định đoạt kiến trúc của bạn" (một kiểu vendor-lock ngược).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| RLS overhead | ~vài % (đúng kiểu filter) | I | so với WHERE tay |
| Schema/cluster (bridge) | tới vài nghìn | I | catalogue bloat sau đó |
| Pool hợp lệ | 10k+ tenant nhỏ | P | |
| Pool → silo migration | giờ–ngày/tenant | P | nếu escape hatch tốt |

---

## 4. Suy luận kiến trúc

- **S1:** Mô hình multi-tenant là **quyết định 5 năm** (đổi = migration dữ liệu thật) — quyết theo danh mục khách hàng dự kiến, không theo quý hiện tại.
- **S2:** Tham số trụ: p99 phân theo tenant-size (nhỏ vs lớn), RLS coverage (bảng có policy %), cost/tenant.
- **S3:** Mỗi bậc isolation đổi chi phí ops lấy ranh giới an toàn — và đường hai chiều (pool↔silo) phải rẻ, nếu không mô hình "lai" chết ngay ở tenant to đầu tiên.
- **S4:** RLS đã trưởng thành đủ để pool mặc định ở cả PG/MySQL/CH — kỹ năng **thiết kế invariant tenant** thay thế kỹ năng "phân cụm thủ công" thế hệ trước.
- **S5:** AI multi-tenant: ACL-aware retrieval (→5.10/12.5) chính là multi-tenancy của lớp vector; index theo tenant + filter cứng — cùng nguyên tắc "khung tenant ở lớp dữ liệu".
- **S6:** Khi "tenant A thấy dữ liệu tenant B": đó là lỗi mô hình (thiếu invariant), không phải lỗi lập trình viên — sửa ở tầng chính sách (RLS + CI check), không bằng review tay thêm WHERE.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Leak dữ liệu xuyên tenant | Query đường không set biến / owner bỏ RLS | audit role + path | §2.2 |
| Tenant nhỏ chậm định kỳ | Noisy neighbor (tenant lớn) | metric theo tenant | §2.3 |
| Bảng mới "quên" tenant | Không CI check policy | policy diff CI | §2.2 |
| Không trả lời được "tenant nào tốn gì" | Không metering | usage theo tenant | §2.4 |
| Không dám tách tenant lớn | Escape hatch không tồn tại | thiết kế §2.5 | §2.5 |
| Đo lường đếm sai số tenant | tenant_id không xuyên suốt event | schema audit (→4.7) | §2.1 |

---

## 6. Cách đo

```sql
-- RLS coverage: bảng có tenant_id nhưng không có policy (bom nổ chậm)
SELECT t.tablename FROM pg_tables t
JOIN pg_attribute a ON a.attrelid = t.tablename::regclass AND a.attname = 'tenant_id'
WHERE t.schemaname = 'public'
  AND NOT EXISTS (SELECT 1 FROM pg_policies p
                  WHERE p.tablename = t.tablename AND p.schemaname = 'public');

-- p99 theo nhóm tenant (nhỏ vs lớn) — phát hiện noisy neighbor
--   từ query log gắn tenant tag (→11.1 exemplar)
```

Nguyên tắc: **RLS coverage + p99 theo nhóm tenant** là hai con số sống còn của SaaS dữ liệu dùng chung — dashboard trước mọi tối ưu.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay RLS:** app-layer WHERE + code review 100% — không thay được về độ tin (người quên); RLS là "seatbelt" tự động. **Thay pool:** nếu danh mục là 20 khách enterprise — silo thẳng, đừng ép pool; ngược lại 100k tenant nhỏ mà silo = chết ops. **Thay escape tự thiết kế:** một số nền tảng có provisioning tự động (Citus/PlanetScale-style) — mua khi đội platform nhỏ.

Năm thấu kính:
- **Kinh tế:** Pool giảm chi phí/tenant ~10× nhưng chuyển rủi ro sang "một lỗi policy = tất cả khách" — bảo hiểm (CI + audit) là phần bắt buộc của mô hình, không phải tùy chọn.
- **Vận hành:** Checklist "tenant invariant" cho mọi datastore: PG (RLS), Kafka (header + ACL), CH (row policy), vector (filter), log (tag) — in ra, review khi thêm datastore mới.
- **An ninh:** Leak xuyên tenant là sự cố tồi tệ nhất của SaaS (niềm tin + pháp lý) —(red team định kỳ: đăng ký 2 tenant, thử đọc chéo — nên là test CI, không phải kiểm thử xâm nhập hàng năm.
- **Lịch sử:** Từ "một cài đặt trên máy khách" (2000s) → silo cloud → pool SaaS → lai theo tier — mỗi bước được đẩy bởi biên chi phí; chu kỳ chưa dừng ở "lai".
- **Người dùng:** Khách hàng không bao giờ hỏi "mô hình multi-tenant gì" — cho tới ngày họ đọc dữ liệu của nhau. Lúc đó mọi chương này gói lại trong một câu: đã có khung cứng chưa.

---

## 8. Đọc tiếp & bài tập

- Ma trận datastore: **5.15** · RLS thực chiến PG: **5.2** · Vector ACL: **5.10, 12.5** · Quản trị/data map: **5.13** · Sizing: **5.16**
- **Bài tập 1:** Chạy truy vấn RLS coverage (§6). Danh sách trả về  = attack surface đang mở của SaaS bạn.
- **Bài tập 2:** Đăng ký 2 tenant test; dùng token tenant A gọi mọi API đọc, tìm bất kỳ response nào có id của tenant B (tự động hoá thành CI — test xuyên tenant nên chạy mỗi PR).
- **Bài tập 3:** Với tenant to nhất: ước tính thời gian tách pool→silo theo §2.5. Nếu trả lời > 1 tuần — escape hatch chưa tồn tại ngoài giấy.
