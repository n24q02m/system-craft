# 5.5 — Wide-Column: Cassandra & ScyllaDB

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.1 (LSM bên dưới) · 5.3 (hai mô hình đã biết).

**Sợi chỉ đỏ:** *Lịch sử đơn theo chuỗi và theo vùng phình to — wide-column gánh thế nào?* — trả lời: wide-column gánh lịch sử đơn phình to theo vùng và thời gian bằng mô hình hash ring + partition; partition key là thiết kế sống còn — chọn sai là nóng đỏ một node; consistency level là bảng đổi độ trễ lấy độ đúng đắn mỗi lần đọc ghi. Câu hỏi để lại cho chương sau: *Khách gõ 'phở bò giao nhanh' — search engine làm được gì mà SQL không?*

**Thuật ngữ sẽ gặp:** *hash ring* — dữ liệu đi tới partition theo hash của key: không cần master; *partition key* — đơn vị phân tán: mọi hàng cùng key nằm cùng node, đọc chuỗi không tán loạn; *clustering key* — thứ tự bên trong partition: đọc lịch sử nhanh; *consistency level* — ONE/QUORUM/ALL: mỗi lần đọc ghi đổi "cổ phiếu" đúng đắn; *tombstone* — xoá là đánh dấu mộ, compaction mới thật sự dọn: bệnh số một; *Cassandra 5.0 / ScyllaDB 2026.3* — hai hiện thân, verify 10/2026 trong chương.

**Ví dụ mở đầu:** Lịch sử đơn của DM theo thành phố và tháng: partition key (city, tháng) — truy vấn vùng nóng chạy thẳng vào vài node. Chọn sai key (theo user): một "cá voi" đặt nghìn đơn mỗi ngày làm node nóng đỏ cả ring. Chương này là thuật toán của lựa chọn đó, kèm bảng đổi cổ phiếu consistency cho từng loại đọc.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Partition key chống hot partition | Key của tôi trải đều theo token — hay một "đại gia" nuốt một node? |
| 2 | Consistency level theo từng use case | ONE/LOCAL_QUORUM/QUORUM — tôi đổi gì lấy gì cho từng đường đọc/ghi? |
| 3 | Data model theo query (không theo bản thể) | Tôi có bảng cho từng câu hỏi — hay đang "chuẩn hoá" như SQL? |
| 4 | Cassandra vs ScyllaDB (C++ rewrite) | Chi phí ops + hiệu năng/đô-la — đo trên workload của tôi? |

---

## 2. Cơ chế

### 2.1 Mô hình: hash ring + partition = đơn vị phân tán

Dữ liệu chia theo **partition key** (hash → token trên ring); mỗi partition nhân bản N node (RF=3 mặc định). **Không có**: JOIN, ràng buộc chéo partition, transaction đa partition. **Có**: ghi nhanh (LSM — →5.1), read path theo partition, scale tuyến tính thêm node. Tư duy thiết kế đảo ngược SQL: **bảng = câu query**, denormalize có chủ đích, mỗi câu hỏi một bảng (query-first design).

### 2.2 Partition key — thiết kế số một quyết định sống còn

```
PRIMARY KEY ((tenant_id, bucket), event_ts, event_id)
             └── partition ──┘  └── clustering (sắp xếp trong partition)
```

- Partition = đơn vị lưu trữ + đơn vị định tuyến + **đơn vị nóng** — mọi row cùng partition ở một node;
- Hot partition: `tenant_id` lớn chiếm 90% traffic → node đó chết (triệu chứng "một node CPU 100%, cluster khác rảnh");
- Thuốc: thêm bucket/salt vào key (`tenant_id + hour_bucket`), chọn key granularity theo **dung lượng partition** (mục tiêu < 100 MB (I)) và **tải trải đều**.

### 2.3 Consistency level — bảng đổi cổ phiếu

| Level | Ý nghĩa | Đổi lấy | Dùng |
|---|---|---|---|
| ONE | 1 node trả lời | nhanh nhất, có thể đọc stale | metrics, cache-được |
| LOCAL_ONE | 1 node trong DC | nhanh, chịu DC fail | đa số app |
| LOCAL_QUORUM | đa số trong DC | đọc gần nhất mới (mặc định nên) | dữ liệu người dùng |
| QUORUM / ALL | đa số/toàn cluster | chậm, chịu partition kém | hiếm — tài chính nhẹ |

Nhớ luật đọc-ghi: **R + W > RF** mới chắc chắn đọc thấy ghi mới (LOCAL_QUORUM + LOCAL_QUORUM với RF=3 thỏa). Hint (manual read repair) + write repair vá lệch nền.

### 2.4 Tombstone & compaction — bệnh số một của Cassandra

Xoá = ghi **tombstone** (đánh dấu chết); compaction mới dọn thật. Hệ quả hai bệnh:
1. **Tombstone hell:** xoá/hết TTL hàng loạt → đọc phải quét xác → latency vọt (triệu chứng: "read chậm sau khi xoá nhiều"). Thuốc: tránh xoá range rộng; TTL đặt đúng; xoá hẹp theo clustering key (để compaction dọn gọn);
2. **Compaction debt:** ghi > dọn → SST dồn, read amp tăng. Chọn strategy: **STCS** (mặc định, đơn giản), **LCS** (read-heavy — nhiều file nhỏ tốn disk), **TWCS** (TTL time-series — gộp theo window, xoá nguyên file).
   Time-series + TTL → TWCS là combo chuẩn (IoT/log).

### 2.5 Cassandra 5.0 / ScyllaDB 2026.3 (verify 10/2026)

- Cassandra 5.0 (2024, hiện 5.0.9): RAFT cho transactional metadata (thay gossip/Paxos cho các thao tác schema), SAI index cải tiến; 6.x đang theo lộ trình;
- ScyllaDB (C++, shard-per-core — →3.10 pattern): hiệu năng/máy cao hơn ~x (đo riêng), driver SHARD-aware; 2026.3 theo chu kỳ quý.

Cả hai cùng protocol (CQL) — migration giữa hai bên là ops chứ không phải rewrite app.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Cassandra / ScyllaDB | 5.0.9 / 2026.3 (10/2026) | V | versions.csv |
| Partition mục tiêu | < 100 MB | I | |
| RF mặc định | 3 | V | |
| Read/Write tuỳ level | ONE ~ms; QUORUM chậm hơn | I | network bound |
| Tombstone danger | read quét > 100k | I | heap pressure |

---

## 4. Suy luận kiến trúc

- **S1:** Wide-column bán **ghi phân tán tuyến tính** — giá là mô hình query-first không có JOIN/txn: chỉ đáng khi write-throughput và tính sẵn sàng là yêu cầu số một.
- **S2:** Tham số trụ: partition size p99, tombstone/read-amp, compaction pending, node skew (token load).
- **S3:** Consistency level là "gắn per-query" — cùng app có thể ONE cho counter không quan trọng và LOCAL_QUORUM cho profile; không chọn một cho tất cả.
- **S4:** Quan hệ hệ sinh thái: Cassandra lo feature (RAFT, SAI); Scylla lo hiệu năng — cạnh tranh canonical làm khách hưởng (giống Redis/Valkey — →5.4).
- **S5:** Time-series/log workload đang dịch về object+lakehouse rẻ hơn (→5.9) — wide-column giữ đúng cái nóng cần query latency thấp.
- **S6:** Khi "cluster chậm": node skew (một node nóng) → tombstone → compaction debt — theo thứ tự khả năng cao nhất.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| 1 node nóng, cluster lệch | Hot partition | nodetool ring/tpstats | §2.2 |
| Read chậm sau xoá lớn | Tombstone hell | sstableverify; audit TTL | §2.4 |
| Repair không xong đúng lịch | Bandwidth đầy | nodetool repair history | §2.3 |
| p99 tăng dần theo tuần | Compaction debt | compaction metrics | §2.4 |
| Đọc thỉnh thoảng "mất" data | ONE + replication lag | dùng LOCAL_QUORUM | §2.3 |
| Schema change treo | (cũ) gossip/Paxos vấn đề | 5.0 RAFT đã giảm | §2.5 |

---

## 6. Cách đo

```bash
nodetool tpstats                    # hàng đợi nội bộ theo stage
nodetool tablestats -H | grep -E 'Table|Space used|Compaction' | head -40
nodetool compactionstats            # đang nén gì, bao lâu

# Partition to nhất (trên mỗi node):
#   sstablepartitions / tablehistograms — đọc p99 theo partition

# Tải ring có đều không:
nodetool ring | awk '{print $NF}' | sort | uniq -c
```

Nguyên tắc: **ring đều + compaction theo kịp + tombstone kiểm soát** = cluster khỏe; một trong ba lệch là bệnh có tên ở §2.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Cassandra:** PostgreSQL + partitioning (đến vài TB vẫn ổn — đừng nhảy vội), Kafka + lakehouse cho log (→5.7/5.9), ScyllaDB nếu đúng vấn đề hiệu năng. **Thay wide-column cho time-series:** ClickHouse (→5.8) — thường gấp bội cho analytics query; wide-column thắng ở write-HT và availability SLA.

Năm thấu kính:
- **Kinh tế:** Cluster wide-column cần ops chuyên (repair/vụcring) — tính headcount trước hardware; Scylla đổi effort port lấy bill máy giảm (đo!).
- **Vận hành:** Repair định kỳ (hinted handoff + anti-entropy) là "nha sĩ" của cluster — bỏ lịch = sâu răng âm thầm.
- **An ninh:** Row-level security không có sẵn — multi-tenant (→5.14) phải mã hoá theo tenant hoặc silo; audit ghi theo app.
- **Lịch sử:** Cassandra từ Facebook inbox (2008) — sinh ra cho đúng bài toán (inbox write-hot, availability > consistency); dùng nó cho bài toán khác và trả giá — công nghệ đúng ngữ cảnh là bài học xuyên bộ atlas này.
- **Người dùng:** Người dùng thấy "tin nhắn gửi là có — kể cả lúc máy chết" — đó là availability-first của chương này làm việc; ngược lại "đôi khi tin cũ hiện lại" là cái giá consistency-one.

---

## 8. Đọc tiếp & bài tập

- LSM/compaction nền: **5.1** · Consistency/replica toán: **8.1–8.2** · Time-series chọn: **5.11** · Log → lakehouse: **5.9** · Sizing: **5.16**
- **Bài tập 1:** Với bảng nóng nhất: tính phân phối kích thước partition (theo partition key). p99 > 100 MB? Thiết kế lại key với bucket — hôm nay chứ không phải sau sự cố.
- **Bài tập 2:** Audit mọi câu DELETE trong codebase Cassandra: range delete nào có thể sinh 10⁶ tombstone? Mỗi cái là một latency bomb có đồng hồ đếm ngược.
- **Bài tập 3:** Liệt kê consistency level của từng đường đọc/ghi chính. Không ai trả lời được "vì sao level này"? — quyết định chưa được đưa ra, chỉ được mặc định.
