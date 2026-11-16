# 8.4 — Phân vùng & Nhân bản ở Tầng Hệ thống

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** lý thuyết vận hành hoá · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.5 (hash ring — tư duy phân vùng) · 5.16 (sizing).

**Sợi chỉ đỏ:** *Một DB không còn đủ — sharding và replication chia dữ liệu sao cho đều và sống?* — trả lời: một DB hết sức chứa — phân vùng theo khoá (chọn khoá là chọn truy vấn sẽ nhanh) và nhân bản cho sống và đọc; RF với quorum thuyết phục được máy chết (8.2); replica lag quyết định "đọc của bạn cũ tới đâu"; còn resharding là cuộc di cư lớn nhất đời hệ thống. Câu hỏi để lại cho chương sau: *Phụ thuộc cứ chết lúc cao điểm — retry, breaker, shedding giữ hệ đứng bằng gì?*

**Thuật ngữ sẽ gặp:** *shard key* — khoá phân vùng: truy vấn theo khoá chạy thẳng, không theo khoá thì scatter-gather; *scatter-gather* — hỏi mọi shard rồi gộp: chậm theo shard chậm nhất; *resharding* — chia lại khi dữ liệu phình: di chuyển nóng, consistent hashing giảm số chỗ phải dời; *RF + quorum* — nhân bản ba bản, ghi đủ hai là xong: sống qua một máy chết; *replica lag* — bản sao trễ bao nhiêu: đọc "vừa ghi xong" có thể không thấy nó; *placement* — đặt bản sao khác vùng, khác tủ: một tủ cháy không mất cả ba.

**Ví dụ mở đầu:** DB đơn hàng của DM đầy: chia theo thành phố — truy vấn theo vùng chạy nhanh, báo cáo toàn quốc chịu scatter-gather. Phình tiếp: chia lại theo (thành phố, tháng) ngay khi hệ đang chạy. Chương này là bản đồ các lựa chọn đó kèm cái giá thật của từng lựa chọn.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Phân vùng theo: range / hash / directory; khoá gì | Truy vấn của tôi cần cùng-dữ-liệu ở cùng-nơi không (locality)? |
| 2 | Reshard khi nào và đường nào (online hay cửa sổ bảo trì) | Dữ liệu x2 — tôi chấp nhận plan nào, đã drill chưa? |
| 3 | Replication factor & chế độ (sync/semi/async) | Mất node/region — mất bao nhiêu ghi, chấp nhận chưa? |
| 4 | Đọc từ đâu: leader / closest replica / quorum (R+W>N?) | Đọc của tôi cần tươi cỡ nào — trả bằng bao nhiêu RTT? |

---

## 2. Cơ chế

### 2.1 Vì sao phân vùng: vượt giới hạn một máy

Một máy có trần RAM/disk/network (→1.2/1.5) — vượt thì chia. Chia đúng: **hot key** (một phân vùng gánh cả hệ), **skew** (một vùng to gấp trăm lần), **scatter-gather** (một truy vấn đập vào mọi vùng). Ba họ chiến lược:
- **Range:** dữ liệu liền kề cùng chỗ — tốt cho range scan; nóng đầu chuỗi (thời gian tăng đơn điệu — cf. 5.1);
- **Hash:** phẳng tự nhiên, mất range locality; **consistent hashing + virtual nodes** cho phép thêm/bớt máy chỉ di chuyển ~1/N dữ liệu (→5.5 Cassandra/Dynamo-style dùng);
- **Directory/lookup:** bảng ánh xạ riêng (linh hoạt nhất, thêm một hệ truy vấn + cache).

### 2.2 Chọn khoá = chọn truy vấn sẽ nhanh

Khoá phân vùng quyết định **truy vấn nào là điểm (nhanh) và truy vấn nào là quét (chậm)**. Quy trình: liệt kê N mẫu truy vấn hay nhất theo tần suất → chọn khoá phục vụ đa số điểm → kiểm tra skew (top-1% khoá chiếm bao nhiêu % lượng) → chấp nhận scatter-gather cho đường hiếm (và đưa lên hướng đường rẻ — →5.16). Lỗi kinh điển: chọn khoá theo "đẹp về mô hình dữ liệu" thay vì theo truy vấn thật.

### 2.3 Resharding — cuộc di cư lớn nhất đời hệ thống

Các con đường, theo thứ tự an toàn tăng dần: (a) **double-write + backfill + switch đọc + xóa cũ** — chuẩn (→5.15 dual-write có chi tiết/bẫy); (b) **copy + CDC theo dõi lag + cutover** — chuyên nghiệp hơn, cần pipeline CDC (→5.15); (c) **consistent hashing tự cân** — hạ tầng lo (Cassandra-style), chỉ còn việc theo dõi token movement; (d) **tắt máy di chuyển** — cửa sổ bảo trì: hợp lệ khi downtime 30 phút rẻ hơn 3 tuần kỹ thuật rủi ro — **quyết định kinh tế, đừng xấu hổ** (→5.16 sizing cùng tư duy).

### 2.4 Nhân bản: RF, đồng bộ, và quorum

- **Đồng bộ:** leader chờ mọi follower ACK — không mất ghi, chậm nhất, mất 1 node là dừng (nếu RF=2);
- **Bán đồng bộ (semi-sync):** chờ ≥K follower — cân bằng phổ biến của relational (→5.2);
- **Bất đồng bộ:** trả ngay — nhanh, **mất dữ liệu khi leader chết trước khi lan** (RPO > 0 — ghi rõ bao nhiêu giây);
- **Quorum read/write:** W + R > N ⇒ ghi rồi đọc thấy mình (→5.5 sloppy quorum/ hinted handoff là biến thể khả dụng hơn, yếu freshness hơn);
- **Cấu trúc phổ biến:** leader-follower (điểm ghi đơn — dễ suy luận) vs leaderless/multi-leader (ghi nhiều nơi — conflict resolution như 6.3/8.1).

### 2.5 Replica lag & đọc của bạn

Follower chậm (ms–giờ tuỳ tải) — ba lựa chọn đọc: (1) **đọc từ leader** (chuẩn cho "đọc-ngay-sau-khi-viết" — read-your-writes); (2) **đọc replica gần** (tươi trễ, nhanh, rẻ); (3) **session sticky/token version** (client ghi nhớ mốc ghi, replica đủ mới mới phục vụ — kỹ thuật phổ biến trong DB tối ưu hóa consistency kiểu monotonic reads). Anti-pattern: hiển thị "đã lưu" rồi đọc từ replica cũ — người dùng thấy dữ liệu "mất" (đã gặp ở 6.3 với client cache).

### 2.6 Đặt vùng với placement

Phân vùng × nhân bản × **định vị**: rack/AZ/region. Bất biến: các bản sao của một phân vùng **không cùng failure domain** (cùng rack = một chiếc tủ điện đem cả ba xuống mồ). Đây là lý do trong mọi hệ đặt bảng (→9.1 topology spread là họ hàng Kubernetes của khái niệm này).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Consistent hashing di chuyển | ~1/N dữ liệu khi ±1 node | V | |
| RF phổ biến | 3 (2 vùng, 1 vùng chéo) | P | |
| W+R>N (N=3) | ví dụ W=2, R=2 | V | |
| Semi-sync ack | ≥1 follower | V | MySQL/PG cấu hình |
| Replica lag bình thường | ms–trăm ms | I | theo tải |

---

## 4. Suy luận kiến trúc

- **S1:** Khoá phân vùng là **tối ưu hoá truy vấn phổ biến nhất**, không phải thuộc tính logic của dữ liệu — đổi truy vấn phổ biến (thêm tính năng) là tới lúc xem lại khoá.
- **S2:** Tham số trụ: phân phối kích thước phân vùng (p99/top-1%), replica lag p95, tỉ lệ scatter-gather theo endpoint, thời gian reshard drill.
- **S3:** Đồng bộ tăng = mất ghi giảm + độ trễ tăng: đây là PACELC (→8.1) hiện thân ở tầng lưu trữ; chọn theo nghiệp vụ từng loại ghi (tiền: sync; log hành vi: async).
- **S4:** Hạ tầng "tự sharding" (Cassandra-style, Mongo sharded, Vitess, Citus — →5.x) đổi chi phí vận hành thấp lấy mô hình dữ liệu/biện luận khó hơn: nửa đường "DB thường + phân vùng logic ứng dụng" (tenant theo schema/cluster) là điểm cân bằng của nhiều SaaS (→5.14 silo/pool).
- **S5:** Cell/sharding theo tenant (→8.7) đang là "sharding cấp kiến trúc": chia cả state lẫn compute theo khách — vì phân vùng dữ liệu thuần không giải được blast radius.
- **S6:** Khi "truy vấn đôi khi chậm vã lai": đo scatter-gather ratio — thường là truy vấn mới không có khoá phù hợp; thêm phụ mục (secondary index) hoặc chấp nhận + cache (→6.5).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Một node nóng khác hẳn | Hot key / skew | đếm top keys theo node | §2.1–2.2 |
| Truy vấn chậm vã lai | Scatter-gather | trace số phân vùng đụng | §2.2 |
| "Ghi xong đọc không thấy" | Đọc replica lag | đọc leader hoặc sticky | §2.5 |
| Mất ghi sau failover | Async replication RPO>0 | audit chế độ sync | §2.4 |
| Reshard làm sập hệ | Backfill dập origin | throttle + đo (→5.15) | §2.3 |
| Cả cụm chết cùng lúc | Replica cùng rack/AZ | placement audit | §2.6 |

---

## 6. Cách đo

```sql
-- Skew: kích thước phân vùng
-- SELECT node, count(*), sum(bytes) FROM partitions GROUP BY node ORDER BY 3 DESC;
--   — tỉ lệ node max/mean > 2–3× là skew thật

-- Replica lag (PG ví dụ — mỗi hệ có lệnh riêng):
--   SELECT now() - pg_last_xact_replay_timestamp();   -- trên standby
```

Nguyên tắc: **dashboard hai con số: skew ratio và replica lag p95** — không có hai con số này, mọi tranh luận "có nên thêm máy" là cảm giác.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự sharding:** mua DB phân tán (Cassandra/Scylla — →5.5) hoặc middleware (Vitess/Citus) — trả tiền/độ phức tạp để khỏi tự lo reshard; **thay RF=3:** backup + restore (RPO theo lịch backup — rẻ, chậm; phù hợp dữ liệu tái tạo được như cache/derived data).

Năm thấu kính:
- **Kinh tế:** Reshard là dự án 6 tuần ẩn trong "thêm máy đi"; mua hạ tầng sharding sẵn là chuyển chi phí tư duy CAPEX sang hóa đơn OPEX — tính NPV như mọi chương khác.
- **Vận hành:** Thêm bớt node phải là **thao tác nhàm chán** (drill hàng quý); nếu mỗi lần thêm máy là dự án đặc biệt, hệ thống đang "scale bằng dũng khí".
- **An ninh:** Phân vùng theo tenant là cả biện pháp cô lập dữ liệu (nhiễu loạn blast radius + residency — →5.13/5.14): sharding vì bảo mật là use case thật.
- **Lịch sử:** Consistent hashing sinh ra cho web cache (Akamai/Dynamo lineage, 1997/2001) rồi lên ngôi trong NoSQL (2010s) rồi quay về cache + service mesh — kỹ thuật đẹp được tái dùng mỗi tầng mới xuất hiện.
- **Người dùng:** Người dùng không biết shard — họ biết "app nhanh đều, không lúc nhanh lúc chậm"; công bằng (fairness) trễ giữa người dùng là sản phẩm của phân phối khoá đều tay.

---

## 8. Đọc tiếp & bài tập

- Sharding ở DB cụ thể: **5.5** · Outbox/backfill: **5.15** · Cell architecture: **8.7** · Consistent hashing: **5.5** · Sizing: **5.16**
- **Bài tập 1:** Đo skew hiện tại (lệnh §6): node nóng nhất gấp node trung bình bao nhiêu lần? > 2× là khoá phân vùng đang lệch theo một chiều (thường: theo thời gian hoặc theo tenant lớn).
- **Bài tập 2:** Chọn endpoint chậm nhất, đếm số phân vùng nó đụng mỗi lần gọi. > 10? Đó là scatter-gather — liệt kê xem khoá nào sẽ làm nó thành điểm.
- **Bài tập 3:** Với sự kiện "một AZ cháy": viết ra (trên giấy) hệ của bạn mất gì, bao lâu phục hồi, ai làm gì. Nếu không viết nổi trong 15 phút — đó chính là câu trả lời: chưa ai thiết kế cho nó (→8.7 drill).
