# 5.4 — In-Memory KV & Cache: Valkey & Redis

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền dữ liệu · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** đã verify 2026-10-30 (versions.csv)
> **Nguồn migrate:** ds-19-kv-cache.md

---

## 0. Nhập môn

**Đọc trước:** 5.2 (cache đứng trước DB) · 2.1 (OOM).

**Sợi chỉ đỏ:** *Menu và tồn kho đọc lặp hàng triệu lần — cache dạy gì và phản bội gì?* — trả lời: cache dạy — menu đọc lặp hàng triệu lần thì trả lời dưới miligiây mà không chạm DB; cache phản bội — dữ liệu stale, stampede phá cửa, và OOM giết cả instance; bốn pattern kèm một bẫy lớn: cache-aside phổ biến nhất nhưng không vô hại. Câu hỏi để lại cho chương sau: *Lịch sử đơn theo chuỗi và theo vùng phình to — wide-column gánh thế nào?*

**Thuật ngữ sẽ gặp:** *cache-aside* — app tự đọc, thấy thiếu tự điền: phổ biến nhất, bẫy lớn nhất; *write-through / write-behind* — ghi xuyên cache ngay, hoặc trễ sau: đổi tính nhất quán; *TTL* — thời gian sống: van an toàn bắt buộc, kể cả khi nghĩ không cần; *stampede* — key hết hạn đúng lúc nghìn request cùng hỏi: DB hứng trọn; *eviction* — đầy RAM thì ai ra trước: LRU/LFU là lựa chọn vận hành số một; *Redis/Valkey* — hai cái tên một dòng họ sau licence 2024 (verify trong chương).

**Ví dụ mở đầu:** Menu DM được đọc lặp: thêm cache, p99 từ ba con số xuống một. Đêm khuyến mãi: key lớn nhất hết hạn đúng lúc cao điểm — nghìn request cùng phá cửa DB, cache đúng lúc vô dụng nhất. Cache dạy tốc độ và phản bội ngay sau đó. Chương này có bốn pattern, ba ca bệnh nổi tiếng, và cách cấp cứu từng ca.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chiến lược cache (cache-aside/write-through) + TTL + jitter | Hiệu ứng "hết hạn đồng loạt" có thể giết DB của tôi không (stampede)? |
| 2 | Single-flight/lock chống stampede | Ai là người được đi nạp lại cache khi miss? |
| 3 | Redis hay Valkey (giấy phép + module) | Fork BSD-3 2024 — tôi chọn gì cho 3 năm tới? |
| 4 | Eviction policy + maxmemory | Bộ nhớ đầy — ai bị đuổi (allkeys-lru? volatile-ttl?) |

---

## 2. Cơ chế

### 2.1 Mô hình dữ liệu + persistence "đủ dùng"

KV + cấu trúc: string, hash, list, set, **sorted set** (bảng xếp hạng/leaderboard), stream (→5.7 nhánh nhỏ), pub/sub, bitmap/HLL (đếm thô). Persistence: **RDB** (snapshot — fork COW — →2.1) và **AOF** (append log + fsync policy: everysec mặc định). KV in-memory là **ổ đĩa bỏ qua** (→1.1 bậc thang) — nhưng không phải "không mất dữ liệu": everysec vẫn mất ~1 s.

### 2.2 Cache pattern — bốn kiểu, một bẫy lớn

- **Cache-aside (mặc định):** app đọc cache → miss → đọc DB → ghi cache + TTL. Đơn giản, chịu lỗi tốt;
- **Write-through:** ghi cache + DB đồng thời — cache luôn ấm, ghi chậm hơn;
- **Write-behind:** ghi cache, async xuống DB — nhanh, rủi ro mất khi chết — chỉ cho dữ liệu chấp nhận mất;
- **Refresh-ahead:** nạp lại trước khi hết hạn — cho key tốn kém.

**Bẫy lớn: cache stampede** — key nóng hết hạn → hàng trăm request cùng lúc xuống DB (vì cùng miss). Triệu chứng: "DB lag/latency nổ đúng lúc cache hết hạn". Bộ ba thuốc: (1) **TTL jitter** (±10–20% — không flock cùng lúc), (2) **single-flight** (lock/`SET NX`: 1 request đi nạp, số kia chờ/serve stale), (3) **stale-while-revalidate** (serve bản cũ, nạp nền).

### 2.3 Redis 8 vs Valkey 9 (verify 2026-10: Redis 8.10.3, Valkey 9.1.3)

Sự kiện ngành 2024: Redis đổi giấy phép (RSAL/SSPL → từ 8.x thêm **AGPLv3** option), cộng đồng fork **Valkey** (Linux Foundation, BSD-3) — AWS/Google Cloud đứng sau. 2026:
- **Valkey 9.x:** hiệu năng đa lõi cải tiến mạnh (async I/O threading), drop một số lệnh cũ; một số module/ha từ Redis 7.2 tương thích;
- **Redis 8.x:** tiếp tục theo định hướng thương mại + OSS AGPL; tính năng mới (query engine, vector — Redis Stack nhập core) ra trước.

**Quy tắc sách:** chọn theo (a) cloud bạn dùng hỗ trợ gì (ElastiCache/ Memorystore đường nào), (b) nhu cầu module (vector — →5.10), (c) định kiến giấy phép của pháp chế. Cả hai đều "Redis protocol" — client chung, đổi bên sau không tốn rewrite.

### 2.4 Eviction & memory — quyết định vận hành số một

`maxmemory` + policy: `noeviction` (ghi lỗi khi đầy — cho store thật), `allkeys-lru` (cache thuần), `volatile-lru` (chỉ đuổi key có TTL), `allkeys-lfu` (đuổi theo tần suất — thường tốt hơn LRU cho Skew-hot). **Cảnh báo kinh điển:** dùng làm cache mà quên maxmemory → OOM killer (→2.1); hoặc dùng làm store mà đặt allkeys-lru → **mất key yên lặng** (kinh điển "dữ liệu biến mất không rõ lý do").

### 2.5 Ba ca bệnh nổi tiếng

1. **THP + fork (→1.3/2.1):** BGSAVE/AOF rewrite fork chậm → stall toàn server — tắt THP trên máy Redis (khuyến nghị chính thức);
2. **Big key:** value 100 MB (list nghìn phần tử) — một lệnh trên nó block single-thread event loop (→3.3) → tất cả chờ. Tìm: `redis-cli --bigkeys`; xử lý: chunk + hash tag;
3. **Hot key:** 1 key nhận 50% traffic — không shard được (nếu hash tag cố nó). Xử lý: local cache tầng app (30s) + nhân bản key (key:1..N đọc vòng).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Redis / Valkey | 8.10.3 / 9.1.3 (10/2026) | V | versions.csv |
| Latency lệnh (local) | ~50–100 µs mạng LAN | I | phần lớn network hop |
| AOF everysec mất | ≤ ~1 s khi chết | V | |
| THP + fork | stall ms–s | V | cảnh báo chính thức |
| Eviction LFU vs LRU | LFU thắng skew-hot | I | |

---

## 4. Suy luận kiến trúc

- **S1:** Cache là **lớp tuỳ chọn có nghĩa lý hẹp** — DB vẫn phải sống được khi cache sạch (cold start là bài toán thiết kế, không phải sự cố).
- **S2:** Tham số trụ: hit ratio, miss latency (đo tới DB), evicted keys/s, big/hot key list, stall (latency p99 lệnh).
- **S3:** TTL jitter + single-flight đổi vài dòng code lấy một lớp chống sập DB — ROI thuộc hàng cao nhất hệ thống.
- **S4:** Fork Valkey chia hệ sinh thái nhưng giữ protocol — "vendor lock giảm, feature race tăng" — kế hoạch 3 năm nên ghi rõ bên nào module nào.
- **S5:** Vector + AI kéo Redis/Valkey thêm vai trò (vector set, session AI, rate-limit token bucket cho LLM — →12.6) — KV in-memory thành "keo" của hệ AI.
- **S6:** Khi "cache chậm": đo latency lệnh đơn (redis-cli --latency) — tách network/app/bigkey trước khi đổ lỗi server.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| DB lag nổ đúng lúc key hết hạn | Stampede | hit ratio + DB metric theo thời gian | §2.2 |
| p99 Redis vọt định kỳ | THP/fork stall | SLOWLOG; THP check | §2.5 |
| Một lệnh treo mọi lệnh | Big key blocking | --bigkeys; slowlog | §2.5 |
| Key "biến mất" | allkeys-lru trên store | config audit | §2.4 |
| OOMKill (→2.1) | maxmemory không đặt | memory usage | §2.4 |
| 1 shard nóng dồn | Hot key + hash tag | --hotkeys; cli-mon | §2.5 |

---

## 6. Cách đo

```bash
redis-cli --latency -h host          # RTT thô
redis-cli --bigkeys -i 5             # quét key to (chạy giờ thấp điểm)
redis-cli --hotkeys                  # nếu LFU policy
redis-cli info memory | grep -E 'used_memory_human|maxmemory_human|evicted'
redis-cli slowlog get 10             # lệnh chậm nhất

# Hit ratio thật (từ app hoặc proxy metric) — con số quan trọng nhất
#   miss = 1 query DB đắt — vẽ miss/s cùng DB CPU trên cùng trục
```

Nguyên tắc: **hit ratio là metric của DB, không phải của cache** — vẽ miss rate cùng tải DB để thấy cache đang "cứu" hay "bơm".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay Redis/Valkey:** memory của app (Caffeine/local LRU — không network hop, không phụ thuộc) cho key nhỏ tự sao; CDN cho asset; DB materialized view cho query đắt. **Thay cluster to:** shard client-side theo key (nhẹ hơn cluster mode) + replica. **Thay session store:** JWT/stateless (→10.3) đổi revoke khó — cân nhắc theo use case.

Năm thấu kính:
- **Kinh tế:** Cache giảm chi phí DB tuyến tính theo hit ratio — 95% hit = 20× giảm tải DB (về query đó); tính bằng hóa đơn thật.
- **Vận hành:** maxmemory + eviction + THP là "bộ ba cấu hình sống còn" — checklist cho mọi instance mới.
- **An ninh:** Redis trần trên Internet bị quét liên tục (cryptominer); bind nội bộ + AUTH + ACL (từ 6.x) — không ngoại lệ.
- **Lịch sử:** 2024 fork Valkey là bài học giấy phép mới nhất (sau Terraform/OpenSearch): "công cụ mở đủ lớn sẽ tự tìm đường nếu chủ nhân đóng cửa" — theo dõi 2 nhánh thay vì chọn phe vĩnh viễn.
- **Người dùng:** Người dùng không biết cache tồn tại — họ chỉ biết "giờ cao điểm sập" (stampede) hoặc "mượt như thường" (tất cả bài học §2.2 đã được áp).

---

## 8. Đọc tiếp & bài tập

- Stampede/retry bão: **8.5** · THP/fork: **1.3, 2.1** · Vector set: **5.10** · Session/token: **10.3** · Sizing: **5.16**
- **Bài tập 1:** Vẽ miss rate của 5 key đắt nhất cùng DB CPU 7 ngày. Thấy tương quan hình bậc thang? Đó là stampede chưa chữa — TTL jitter + single-flight là PR ngày mai.
- **Bài tập 2:** `redis-cli --bigkeys` trên cluster production (giờ thấp điểm). Key > 1 MB: viết kế hoạch chunk.
- **Bài tập 3:** Audit: instance nào dùng làm store nhưng có allkeys-lru (hoặc ngược lại)? Mỗi sai là một sự cố im lặng tương lai.
