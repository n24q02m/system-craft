# 1.1 — Bậc thang độ trễ

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.11 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)

---

## 0. Nhập môn

**Đọc trước:** Cụm P0 — đủ nhất là 0.1 (biết "trục" là gì).

**Sợi chỉ đỏ:** *Đủ đồ tư duy, làm thật: DM khởi động bằng một máy chủ và một process — điều gì cần cảm bằng tay trước tiên?* — trả lời: điều cần cảm bằng tay trước tiên là thang thời gian — nanogiây, microgiây, miligiây — vì mọi phán đoán "chậm/vội, đáng/không đáng tối ưu" về sau đều là so bậc, không phải so con số tuyệt đối. Câu hỏi để lại cho chương sau: *Từ nano-giây tới mili-giây là cả một tháp — phần lớn khoảng cách đó nằm ở đâu trong một cái máy?*

**Thuật ngữ sẽ gặp:** *độ trễ (latency)* — thời gian một việc trọn vẹn; *throughput* — số việc xong mỗi giây, đại lượng khác hẳn độ trễ; *bậc thang* — các tầng thời gian cách nhau bậc độ lớn, không phải dốc liền; *luật Little* — L = throughput × thời gian trong hệ: hàng đợi tự sinh khi hai bên lệch nhau; *RTT* — thời gian một vòng đi về trên mạng.

**Ví dụ mở đầu:** Khách bấm "Đặt món" và chờ 800 ms. Cả 800 ms đó là một tháp: 0,1 ms có thể là một lần đọc RAM, 1 ms là một vòng SSD, 100 ms là một vòng mạng chéo vùng. Không có thang trong đầu thì mọi con số trôi như nhau — và team tối ưu nhầm tầng: tối ưu cái đo bằng microgiây trong khi khách chờ thứ đo bằng trăm miligiây.

## 1. Quyết định

Sau chương này bạn phải chọn được bốn thứ. Nếu không chọn được, chương đã thất bại.

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| **D1** | **Đặt ranh giới đồng bộ ở đâu** — chỗ nào gọi thẳng, chỗ nào phải bất đồng bộ | "Nếu phép gọi này nằm trên đường tới người dùng, tôi chấp nhận p99 bao nhiêu?" |
| **D2** | **Tầng nào giữ dữ liệu** — cache trong tiến trình, cache ngoài, replica, hay chấp nhận đọc đĩa | "Dữ liệu này có cần đi qua biên mạng không? Vì sao?" |
| **D3** | **Có bao nhiêu hop mạng trên một request** | "Đếm hop. Nhân với 0,5 ms. Con số đó có nằm trong ngân sách độ trễ không?" |
| **D4** | **Chọn vùng (region)** — một vùng, nhiều vùng, hay đẩy ra biên | "Người dùng ở đâu, dữ liệu gốc ở đâu, khoảng cách giữa hai chỗ đó là bao nhiêu ms?" |

Bốn quyết định này là **cùng một quyết định** nhìn từ bốn góc: bạn đang phân bổ **độ trễ**. Mọi tầng trong stack — cache, queue, replica, CDN, edge — tồn tại để phục vụ dữ liệu từ một tầng nhanh hơn trong bậc thang này. Hiểu bậc thang là hiểu vì sao các tầng đó tồn tại; không hiểu thì bạn sẽ thêm cache vì "ai cũng thêm", và mất nhất quán vì không biết mình vừa trả giá bằng gì.

---

## 2. Cơ chế

### 2.1 Vì sao nó là bậc thang, không phải dốc

Mỗi tầng lưu trữ đổi một đặc tính vật lý: **khoảng cách** và **cơ chế truy cập**.

| Tầng | Cơ chế | Trần vật lý | Hệ quả |
|---|---|---|---|
| Thanh ghi | Điện trong lõi | 1 chu kỳ | không đếm được bằng ns |
| L1/L2/L3 | SRAM, sát lõi, không gian giới hạn | vài ns | dung lượng tính bằng **KB–MB** → luôn thiếu |
| DRAM | Tụ điện + bus ngoài chip | ~100 ns | dung lượng GB, nhưng **×100** |
| SSD/NVMe | Flash, không có đầu từ | ~100 µs | truy cập ngẫu nhiên **rẻ hơn HDD ~100 lần** |
| HDD | Đầu từ quay | ~10 ms | chỉ còn chỗ cho dữ liệu nguội |
| Mạng trong DC | Chuyển mạch + xếp hàng + ngăn xếp giao thức | ~500 µs | **không phải "gần như miễn phí"** |
| Mạng liên lục địa | Cáp quang + tốc độ ánh sáng | ~150 ms | **không thể tối ưu** — xem §2.3 |

Khoảng cách giữa các tầng **không tuyến tính**: L1 → DRAM là ×100; DRAM → SSD ngẫu nhiên là ×1.000; SSD → HDD là ×100; HDD → liên lục địa là ×15. Vì vậy mọi tối ưu hiệu năng đều là **nhảy tầng**, không phải "làm nhanh hơn một chút". Không có kỹ thuật nào làm DRAM nhanh gấp đôi; có rất nhiều kỹ thuật để **không phải chạm DRAM**.

### 2.2 Hai đại lượng khác nhau mà người ta hay lẫn

ASCII dưới đây là chỗ phần lớn lỗi thiết kế sinh ra:

```
        ĐỘ TRỄ (latency)                 BĂNG THÔNG (throughput)
        "một lần mất bao lâu"            "một giây được bao nhiêu"
        ─────────────────────            ────────────────────────
        ảnh hưởng: p50/p99               ảnh hưởng: chi phí, hàng đợi
        cải thiện bằng: nhảy tầng        cải thiện bằng: song song hoá, nén, batch

        Đường ống 1 m: 1 viên bi mỗi 10 giây   → 6 viên/phút, nhưng 1 viên đi 1 m trong 0,1 s
        Đường ống 1000 m: 1000 viên mỗi 10 s   → 6000 viên/phút, nhưng 1 viên vẫn mất 100 s
        ↑ băng thông gấp 1000, độ trễ vẫn ×1000
```

**Băng thông cao không làm giảm độ trễ.** Một liên kết 100 Gbps xuyên Thái Bình Dương vẫn có RTT ~150 ms. Đây là lý do tồn tại của CDN, replica theo vùng, và edge compute — tất cả đều là **mang dữ liệu tới gần người dùng**, không phải "làm mạng nhanh hơn".

### 2.3 Trần tuyệt đối: tốc độ ánh sáng

Ánh sáng trong sợi quang đi chậm hơn trong chân không, khoảng **2/3 c** ≈ 200.000 km/s (hệ số khúc xạ của silica ~1,47). Với tuyến cáp vòng quanh Trái Đất, khoảng cách vật lý **luôn dài hơn** đường chim bay.

| Chặng | Khoảng cách cáp (xấp xỉ) | RTT tối thiểu (lý thuyết) | RTT thực tế |
|---|---|---|---|
| Trong cùng rack | < 100 m | ~1 µs | **~100–500 µs** (xếp hàng + ngăn xếp giao thức chiếm gần hết) |
| Cùng AZ | vài km | ~50 µs | **~0,5 ms** |
| Khác AZ cùng vùng | 50–100 km | ~0,5–1 ms | **~1–2 ms** |
| Hà Nội ↔ Singapore | ~2.300 km | ~23 ms | **~35–45 ms** |
| Hà Nội ↔ Frankfurt | ~9.000 km | ~90 ms | **~150–190 ms** |
| US ↔ châu Á (vòng Thái Bình Dương) | ~15.000 km | ~150 ms | **~180–250 ms** |

Ba suy luận **không thể tránh**:
1. Không có tối ưu phần mềm nào làm RTT xuyên lục địa xuống dưới ~100 ms. Đây là **hằng số vật lý**, không phải vấn đề kỹ thuật.
2. Mọi API đồng bộ xuyên lục địa là **≥ 3 RTT** (TCP + TLS 1.3 + request/response) → ~450 ms trước khi server làm gì. Cộng thêm một truy vấn DB xuyên vùng → ~600 ms.
3. Hệ quả thiết kế: nếu người dùng và dữ liệu gốc ở hai lục địa, chọn giữa **replica đọc gần người dùng** (trả giá bằng độ trễ nhân bản + dữ liệu cũ) hoặc **chuyển dữ liệu gốc theo vùng** (trả giá bằng phân mảnh + tuân thủ dữ liệu). Không có lựa chọn thứ ba miễn phí.

### 2.4 Luật Little: vì sao hệ thống sụp nhanh hơn bạn tưởng

```
L = λ × W
L = số request đang trong hệ thống
λ = tốc độ đến (req/s)
W = thời gian phục vụ trung bình (s)
```

Một service xử lý 1.000 req/s với 50 ms/request ⇒ **L = 50 request đồng thời**. Không có gì đáng lo. Nhưng khi W tăng lên 500 ms (đĩa chậm, GC, khoá), L = 500. Khi số worker < L, request **xếp hàng**, thời gian chờ cộng vào W, W tăng tiếp ⇒ **vòng xoáy**. Đây là lý do một sự cố "chậm 10 lần" thường biến thành "sập", chứ không phải "chậm 10 lần".

Suy ra: khi thiết kế theo bậc thang độ trễ, câu hỏi đúng không phải "request này nhanh không" mà là "**nếu tầng này chậm gấp 10, cái gì xếp hàng, và ai bị chặn**".

---

## 3. Bảng số

> **Cách đọc số:** đây là **bậc độ lớn** trên phần cứng phổ thông 2025–2026, không phải số đo trên máy bạn. Hai nguồn độc lập khớp nhau về bậc: bảng gốc của Jeff Dean (gist `jboner`) và bảng cập nhật 2025–2026 cho NVMe/cloud (calibreos, kunwar.page). Sai khác thực tế trên máy cụ thể: ×2–×5 ở tầng cache, ×1,5–×3 ở tầng mạng. **Đừng trích số của người khác làm SLO của mình — hãy đo.**

| Thao tác | Độ trễ | Tỉ lệ so với L1 | Ghi chú |
|---|---|---|---|
| L1 cache | ~1 ns | 1× | |
| L2 cache | ~4 ns | 4× | |
| L3 cache | ~10–15 ns | ~10–15× | dùng chung giữa các lõi; NUMA làm nó tệ hơn |
| Branch mispredict | ~3–5 ns | ~5× | |
| DRAM | ~100 ns | **100×** | "cache miss" nghĩa là trả giá này |
| Nén 1 KB (zstd) | ~1–2 µs | ~1.500× | nén rẻ hơn truyền, trên đường truyền chậm |
| Đọc 4 KB ngẫu nhiên trên NVMe | ~100 µs | **100.000×** | |
| Đọc tuần tự 1 MB trên NVMe | ~100–200 µs | ~150.000× | băng thông ~10 GB/s |
| RTT trong cùng DC | ~500 µs | 500.000× | **chuẩn cho mọi hop microservice** |
| RTT khác AZ cùng vùng | ~1–2 ms | ~1,5 triệu× | đồng bộ hoá ghi giữa AZ trả giá này mỗi lần |
| Seek HDD | ~10 ms | 10 triệu× | |
| RTT xuyên lục địa | ~150 ms | 150 triệu× | |

### Bảng quy đổi: nếu 1 ns = 1 giây

Đây không phải trò vui — nó là cách duy nhất để **cảm nhận** bậc thang.

| Thao tác | Nếu 1 ns = 1 s |
|---|---|
| L1 cache | 1 giây |
| DRAM | 1 phút 40 giây |
| Đọc ngẫu nhiên NVMe | **27,7 giờ** |
| RTT trong DC | **5,8 ngày** |
| Seek HDD | **3,8 tháng** |
| RTT Hà Nội ↔ Frankfurt | **4,8 năm** |

Đọc bảng này theo chiều ngược: khi bạn viết một vòng lặp có `await db.query()` bên trong cho mỗi item, bạn vừa đặt **27,7 giờ** (theo thang trên) vào giữa hai dòng code. Khi bạn gọi 5 microservice nối tiếp, bạn vừa đặt **29 ngày** vào đường tới người dùng.

---

## 4. Suy luận — những gì bảng số ép ra

Bảng số chỉ có giá trị nếu nó **thay đổi quyết định**. Sáu suy luận dưới đây là phần thực sự dùng được.

**S1 — Ngân sách độ trễ là phép chia, không phải cảm hứng.**
Người dùng cảm nhận độ trễ ở mốc ~100 ms (còn "tức thì"), ~300 ms (bắt đầu chậm), ~1 s (mất mạch suy nghĩ), ~10 s (bỏ đi). Nếu bạn có ngân sách 300 ms cho một trang có 8 lượt gọi backend và 1 truy vấn DB:
```
300 ms  −  8 × 0,5 ms (hop trong DC)  −  1 × 2 ms (DB khác AZ)  =  ~296 ms còn lại
```
Trông thoải mái — cho tới khi một hop đi xuyên vùng: `+150 ms`. Ngân sách bị ăn một nửa bởi **một quyết định triển khai**, không bởi code.

**S2 — Mỗi hop đồng bộ phải được trả bằng lý do.**
Không có "sạch kiến trúc" nào đáng giá 500 µs trên đường tới người dùng. Nếu hop không đổi quyết định của người dùng, nó phải thành bất đồng bộ.

**S3 — Cache là quyết định về tính nhất quán, không phải về tốc độ.**
Thêm cache DRAM trước một truy vấn DB (100 µs) tiết kiệm 100 µs nhưng tạo ra cửa sổ dữ liệu cũ. Câu hỏi đúng không phải "cache có nhanh hơn không" (luôn có) mà "**dữ liệu cũ bao lâu thì nghiệp vụ vẫn đúng**". Trả lời được con số đó thì mới chọn được TTL.

**S4 — Batch thắng theo bậc thang, không theo phần trăm.**
100 truy vấn riêng lẻ = 100 × 100 µs = 10 ms. Một truy vấn trả 100 dòng = ~200 µs. Đây là **×50**, không phải ×1,2. Quy tắc: nếu bạn thấy một vòng lặp chứa I/O, đó là lỗi thiết kế chứ không phải lỗi tối ưu.

**S5 — Đặt tính toán ở đâu phụ thuộc dữ liệu ở đâu.**
Tính toán ở CPU ~1 ns/lệnh. Kéo 1 GB từ DC khác ~ vài giây. Nếu bạn đang "gọi API để lấy dữ liệu rồi lọc ở client", bạn đang trả giá băng thông để tiết kiệm CPU — chỉ đúng khi dữ liệu nhỏ hoặc mạng gần.

**S6 — p99 không phải p50 nhân ba.**
Phân phối độ trễ hệ thống thật có **đuôi dài**: GC, khoá, hàng đợi, retry, cold cache. p99 thường gấp 10–100 lần p50. Và với một trang gọi 20 service song song, xác suất ít nhất một service ở p99 là `1 − 0,99²⁰ ≈ 18%`. **Một phần năm lượt xem của người dùng là p99 của bạn.** Đây là lý do phải cắt hop, không chỉ tối ưu từng hop.

---

## 5. Hỏng thế nào

Bảng sự cố — dùng khi đang chữa cháy, không phải khi thiết kế.

| Triệu chứng | Nguyên nhân theo bậc thang | Cách xác nhận | Sửa |
|---|---|---|---|
| p50 ổn, p99 tăng dần theo tải | Hàng đợi phình (Little) | đo L = req đang xử lý; nếu L tăng tuyến tính với λ mà W không đổi → thiếu worker | thêm song song, hoặc **giảm W** (bỏ hop) |
| Toàn hệ thống chậm đúng một dịp, mọi service cùng lúc | Một tầng chung (DB, DNS, NTP, auth) | xem biểu đồ theo thời gian, tìm service có p99 tăng **trước** | cắt phụ thuộc chung khỏi đường tới người dùng |
| Độ trễ nhảy bậc, không tăng dần | Vượt ngưỡng bộ nhớ → swap hoặc evict cache | RSS so với limit; tỉ lệ cache miss | đặt limit đúng; tách cache khỏi heap |
| Request nhanh bất thường rồi lỗi | Timeout ngắn hơn thời gian phục vụ thật | so timeout với p99 thật | timeout phải **theo bậc thang**, không theo cảm tính |
| Chậm chỉ ở một vùng | Khoảng cách tới dữ liệu gốc | đo RTT client→vùng | replica đọc theo vùng, hoặc chuyển dữ liệu gốc |
| Chậm sau khi "tối ưu bằng cache" | Mất nhất quán gây retry/tính lại | đếm tỉ lệ cache hit **và** tỉ lệ nghi vấn dữ liệu cũ | xem lại D2/S3 |

**Cạm bẫy phổ biến nhất:** tối ưu tầng nhanh nhất. Người ta dành một tuần để giảm 20 ns trong một hàm — trong khi một hop mạng thừa tốn 500 µs, tức **25.000 lần** nhiều hơn. Luôn tìm tầng chậm nhất trên đường tới người dùng **trước khi** mở profiler.

---

## 6. Đo

| Cần biết | Cách đo | Đừng dùng |
|---|---|---|
| Độ trễ người dùng cảm nhận | RUM (Real User Monitoring) — đo ở trình duyệt/thiết bị | log server (bỏ mất mạng + render) |
| Độ trễ từng hop | OpenTelemetry span + histogram | log "request took X ms" |
| Đuôi phân phối | **histogram** với bucket tới 10 s, hoặc HDR | trung bình, hoặc `avg()` trong dashboard |
| Hàng đợi | độ sâu queue, thời gian chờ, số đang xử lý | CPU utilisation |
| Tầng nào chậm | thử **thay** tầng bằng hằng số (trả `0` giả) rồi đo lại | suy đoán |

**Nguyên tắc:** độ trễ là **phân phối**, không phải số. Một con số duy nhất luôn nói dối. Báo cáo tối thiểu phải là `p50 / p90 / p99 / max` kèm **số lượng request** — p99 của 20 request là vô nghĩa.

---

## 7. Lựa chọn khác, và vì sao không

| Lựa chọn | Được | Mất | Khi nào vẫn nên chọn |
|---|---|---|---|
| **Thêm cache ở mọi tầng** | giảm p50 nhanh, rẻ công | mất nhất quán, khó chẩn đoán ("cache ở đâu?") | dữ liệu đọc nhiều, chấp nhận cũ vài giây |
| **Batch mọi thứ** | ×50 như S4 | tăng độ trễ một request đơn lẻ; phức tạp khi lỗi một phần | tải cao, dữ liệu ghi nhiều |
| **Bất đồng bộ hoá toàn bộ** | cắt hop khỏi đường người dùng | khó biết "đã xong chưa"; cần idempotency + outbox | tác vụ không cần kết quả tức thì |
| **Đẩy ra edge** | cắt RTT vật lý | dữ liệu gốc vẫn xa; khó debug; chi phí | nội dung tĩnh, cá nhân hoá nhẹ |
| **Một vùng duy nhất, tối ưu trong vùng** | đơn giản, nhất quán tuyệt đối | trần ~RTT tới người dùng xa | người dùng tập trung một khu vực |
| **Nhiều vùng active-active** | RTT thấp cho mọi người | đồng thuận xuyên vùng, xung đột ghi, chi phí ×N | quy mô lớn, yêu cầu DR nghiêm ngặt |

Không có lựa chọn nào "đúng". Có lựa chọn **khớp với phân bố người dùng và mức nhất quán mà nghiệp vụ chịu được** — đó là nội dung của D1–D4.

---

## 8. Đọc gì tiếp

- **Trong atlas:** 1.2 (bộ nhớ & phân cấp cache) — vì sao ×100 giữa L1 và DRAM; 5.x (dữ liệu) cho S3; 8.x (hệ phân tán) cho S6 và trần vật lý khi nhân bản xuyên vùng.
- **Ngoài atlas:** bảng gốc *Latency Numbers Every Programmer Should Know* (Jeff Dean / gist `jboner`) — đọc để thấy số đã lệch thế nào sau 15 năm; `systems-performance` của Brendan Gregg cho phần đo.
- **Bài tập kiểm tra hiểu:** lấy một endpoint thật của bạn, đếm hop mạng, nhân 0,5 ms, so với p99 đo được. Chênh lệch chính là **phần chưa biết** — và đó là chỗ cần đo trước.
