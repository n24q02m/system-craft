# NGÂN HÀNG ĐỀ THI — 40 câu có đáp án

> **Dùng thế nào:** mỗi câu ghi rõ **chương gốc** (sinh viên mở đúng §3 của chương đó sẽ thấy số liệu), **mức** (1 = nhớ/tính · 2 = áp dụng · 3 = phán đoán), và **CLO** tương ứng.
> **Nguyên tắc ra đề của atlas:** không có câu nào trả lời được bằng cách học thuộc mà không hiểu; và **không có câu nào không có số**.

---

## A. Cụm P0–P1: hệ quy chiếu, vật lý (10 câu)

**A1 · [1 · CLO1] Kể 5 mốc độ trễ và một ví dụ mỗi mốc.**
*Đáp:* ~0,5–1 ns: một phép cộng/đọc L1 · ~10 ns: L3 · ~80–100 ns: DRAM · ~100 µs: gói tin trong DC · ~0,5–1 ms: SSD NVMe một lần đọc ngẫu nhiên · ~100–150 ms: RTT xuyên lục địa. (Chấp nhận sai số 1 bậc.)

**A2 · [2 · CLO2] CPU nhanh gấp 10×, ứng dụng chỉ nhanh 2×. Vì sao, và cần đo gì?** *(3.1)*
*Đáp:* có phần tuần tự (I/O, khởi tạo, lock). Amdahl: S = 2 với N = 10 ⇒ phần tuần tự ≈ **90%**. Đo bằng profiler để xác định thời gian nằm ở phần không song song được; nếu phần tuần tự là I/O thì tăng CPU không giúp gì.

**A3 · [1 · CLO2] Amdahl: N = 8, S = 5. Phần tuần tự chiếm bao nhiêu? Speedup tối đa?** *(3.1)*
*Đáp:* serial ≈ **8,6%**; speedup tối đa = 1/0,086 ≈ **11,6×** dù có vô hạn lõi.

**A4 · [2 · CLO2] Cụm 12 đĩa 12 TB, RAID5, URE 10¹⁴. Xác suất rebuild sạch? Nên chọn gì?** *(1.4)*
*Đáp:* phải đọc 11×12 = 132 TB ⇒ xác suất **gặp** URE ≈ **0,999974** (gần chắc chắn) ⇒ RAID5 là ống kính. Cùng ngân sách: **RAID10** (72 TB dùng được) hoặc RAID6.

**A5 · [3 · CLO2] Vì sao đo băng thông DRAM thực tế chỉ được 70–80% spec? Dưới 55% thì nghi gì?** *(1.3)*
*Đáp:* 70–80% là bình thường (overhead refresh, ECC, hiệu suất controller). < 55% ⇒ nghi (a) thiếu DIMM nên **mất kênh**, (b) thread/tiến trình chạy chéo NUMA node, (c) interleaving tắt trong BIOS.

**A6 · [1 · CLO3] 500 kW IT, PUE 1,6 → 1,2, giá 1.850đ/kWh. Tiết kiệm mỗi tháng?** *(1.10)*
*Đáp:* 800 kW → 600 kW; chênh 200 kW × 730 h = 146.000 kWh ⇒ **~270 triệu VND/tháng** (~3,2 tỉ/năm).

**A7 · [2 · CLO2] `iperf3 -P1` = 2,1 Gb/s, `-P16` = 9,4 Gb/s trên đường 10 GbE, RTT 1 ms. Chẩn đoán?** *(1.7)*
*Đáp:* BDP = 10 Gb/s × 1 ms ≈ **1,25 MB**; một luồng không mở đủ cửa sổ và/hoặc queue depth thấp. Đây là "quyết định BDP chưa ai đưa": tăng `tcp_rmem/wmem`, bật BBR, hoặc nhiều luồng ở tầng ứng dụng.

**A8 · [3 · CLO3] Một máy "cùng loại instance" chậm hơn 12%. Hai nguyên nhân khả dĩ và cách kiểm?** *(1.8)*
*Đáp:* (a) host đời cũ/noisy neighbour → benchmark cùng loại ở 2 AZ, so 3 lần; (b) khác **stepping/microcode** → `lscpu`, `/proc/cpuinfo`, `dmidecode -t processor`. Ghi vào sổ placement.

**A9 · [2 · CLO1] Ba máy chênh offset 120 ms. Hệ quả với `created_at` và last-write-wins?** *(1.9, 8.1)*
*Đáp:* LWW dùng timestamp là **xúc xắc** — hai ghi cách nhau 120 ms có thể đảo thứ tự; log không ghép được. Đúng: thứ tự do node chủ/version (Lamport) quyết, timestamp chỉ để quan sát; hoặc siết offset < 10 ms (PTP trong DC).

**A10 · [3 · CLO5] "Chúng tôi dùng ECC nên dữ liệu luôn đúng." Chỉ ra 2 chỗ còn bit-flip.** *(1.3, 2.4)*
*Đáp:* (1) ECC bảo vệ **RAM**, không bảo vệ buffer ứng dụng/logic (bit flip trong thanh ghi hoặc trong vùng đệm rồi ghi xuống đĩa thành "dữ liệu đúng nhưng sai"); (2) đường **mạng/ổ đĩa không có checksum end-to-end** ở tầng ứng dụng ⇒ phải tự thêm CRC cho thứ không tái tạo được (backup, sổ cái).

## B. Cụm P2–P3: kernel & runtime (10 câu)

**B1 · [2 · CLO3] Container bị OOM-kill dù RSS thấp hơn limit. Hai nghi phạm?** *(2.1)*
*Đáp:* (a) bộ nhớ **ngoài heap** (page cache, mmap, stack, cgo) đẩy `memory.current` vượt; (b) `oom_score_adj` = 0 cho mọi process ⇒ kernel chọn theo mức dùng, thường giết process to nhất chứ không phải quan trọng nhất.

**B2 · [1 · CLO3] CFS throttle ratio 12% ở service latency-critical. Hệ quả và cách sửa?** *(9.1)*
*Đáp:* p99 bị **bóp méo bởi cgroup**: request 20 ms bị throttle 3 kỳ (300 ms) thành 320 ms. Sửa: tăng limit hoặc **bỏ CPU limit, giữ request** (quota gây "burst bị phạt"), đo lại throttle ratio + p99.

**B3 · [2 · CLO2] `vmstat`: tải 4× nhưng `cs` tăng 9×. Nghĩa là gì?** *(2.3)*
*Đáp:* nhiều chuyển ngữ cảnh hơn cho cùng lượng việc ⇒ **tới trần concurrency**: lock contention, thread pool quá lớn, hoặc wakeup storm. Kiểm: cs/request tăng, p99 tăng phi tuyến.

**B4 · [3 · CLO3] Ghi config quan trọng, 4 bước. Thiếu bước nào thì mất file?** *(2.4)*
*Đáp:* (1) ghi file tạm cùng thư mục → (2) `fsync(file)` → (3) `rename` → (4) `fsync(thư mục)`. Thiếu (2) ⇒ file rỗng sau crash; thiếu (4) ⇒ mất tên file dù đã rename; ghi thẳng vào file thật ⇒ người đọc thấy file cụt.

**B5 · [2 · CLO3] Node: p99 của **mọi** request nhảy lên 800 ms trong 3 giây, CPU 15%. Chẩn đoán?** *(3.3, 2.5)*
*Đáp:* **event loop bị chặn** (một handler đồng bộ: `JSON.parse` 10 MB, sort lớn, `fs.readFileSync`). Kiểm bằng `perf_hooks.monitorEventLoopDelay()` (p99 > 50 ms = có vấn đề) và đưa việc nặng sang worker.

**B6 · [1 · CLO4] `GOMEMLIMIT` nên đặt bao nhiêu % container limit và vì sao không 100%?** *(3.4)*
*Đáp:* **85%** — chừa chỗ cho bộ nhớ Go runtime **không tính vào heap** (goroutine stack, mmap, cgo, buffer). Đặt 100% ⇒ vẫn OOM.

**B7 · [2 · CLO4] `go test -race` ra 3 cảnh báo. Có nên sửa hết trước khi ship? Vì sao?** *(3.4)*
*Đáp:* 3 cảnh báo là race **đã thực sự xảy ra** trong lần chạy ⇒ mỗi cái là một bug "không tái lập" tương lai ⇒ sửa hết (hoặc che bằng mutex/atomic có chủ đích). Nếu chạy `-race` chỉ trong CI đêm, đặt job riêng để không chặn mọi PR.

**B8 · [3 · CLO5] Đồng nghiệp nói "WebAssembly chậm gấp 10 lần native". Phản biện bằng số và bằng điều kiện.** *(3.8)*
*Đáp:* với phép tính thuần CPU, Wasm thường chỉ chậm **1,1–2×**; chậm 10–100× xuất hiện khi **mỗi lần gọi phải qua biên** (copy chuỗi, cấp phát). Câu hỏi đúng: "biên gọi bao nhiêu lần, dữ liệu copy bao nhiêu byte?" — và API nên batch thay vì gọi từng phần tử.

**B9 · [1 · CLO3] Hai service (Python ↔ Node) trao đổi `int64` qua JSON. Ca nào hỏng?** *(3.9)*
*Đáp:* số > 2⁵³ (9.007.199.254.740.991) — JavaScript mất chính xác (int64 > 2⁵³ **mất 1**). Sửa: dùng **string** cho int64 trong JSON, hoặc protobuf; thêm contract test 5 ca (số thập phân, emoji, DST, rỗng, số lớn).

**B10 · [2 · CLO2] Pool 500 req/s × 20 ms, retry 10%, safety 1,5. Cần bao nhiêu connection?** *(3.10)*
*Đáp:* 500 × 0,02 = 10 → ×1,1 = 11 → ×1,5 ≈ **17 conn**. Nếu đang đặt 100 conn ⇒ đang trả tiền cho context switch + RAM (mỗi conn vài MB) và làm DB chậm đi.

## C. Cụm P5: dữ liệu (8 câu)

**C1 · [2 · CLO1] Bảng ghi 5.000/s có 8 index. Chi phí của mỗi index?** *(5.1)*
*Đáp:* mỗi INSERT cập nhật cả 8 index ⇒ ~40.000 thao tác index/giây (WAL + I/O). Index `idx_scan = 0` trong 30 ngày là index **không dùng** ⇒ xoá; kỳ vọng giảm ghi 15–40%.

**C2 · [1 · CLO1] 20 pod × pool 20 = 400 conn, DB 8 core. Sai ở đâu?** *(5.2)*
*Đáp:* quy tắc OLTP `cores × 2–4` ⇒ ~16–32 conn là đủ; 400 gấp ~12× ⇒ context switch, RAM (~5–10 MB/conn), lock manager nặng. Sửa: pool theo Little (B10) + PgBouncer.

**C3 · [2 · CLO2] `DELETE FROM logs WHERE day < 30` trên Cassandra 10⁶ hàng. Chuyện gì xảy ra?** *(5.5)*
*Đáp:* sinh **tombstone cho từng hàng** (hoặc range tombstone) ⇒ đọc sau phải bỏ qua 10⁶ tombstone trước khi thấy dữ liệu sống ⇒ p99 nổ; merge không kịp. Đúng: **TTL** khi ghi, hoặc xoá theo **partition**, và `gc_grace_seconds` hợp lý.

**C4 · [2 · CLO3] Poison message vào topic: consumer cần gì để "sống sót"?** *(5.7)*
*Đáp:* (1) try/catch quanh xử lý; (2) retry **có giới hạn** (3–5, backoff); (3) **DLQ** + metric độ sâu; (4) alert khi DLQ > 0; (5) runbook replay. Thiếu (3) ⇒ message hỏng **chặn cả partition**.

**C5 · [2 · CLO2] ClickHouse: block size trung vị 300 rows/INSERT. Hệ quả?** *(5.8)*
*Đáp:* "**too many parts**" tương lai: mỗi INSERT tạo part, merge không theo kịp ⇒ lỗi từ chối ghi và đọc chậm. Sửa: batch 10.000–100.000 dòng hoặc `async_insert`.

**C6 · [3 · CLO1] "Dữ liệu báo cáo mới trong 30 phút" — đo thế nào?** *(5.12)*
*Đáp:* `now() − max(event_time)` trong store, lấy **p95** trong 7 ngày, so với **SLA nghiệp vụ**. p95 thường gấp 3–10× con số trong slide; đo như một SLI và alert khi vượt.

**C7 · [3 · CLO3] RAG trả về dữ liệu của tenant khác. Lỗi ở đâu và sửa ở đâu?** *(5.10, 12.3)*
*Đáp:* lỗi ở **retrieval** không ở prompt — ACL đặt trong prompt là trang trí. Sửa: filter theo tenant **bắt buộc ở tầng truy vấn** (namespace/partition/pre-filter vector), cộng test xuyên tenant trong CI.

**C8 · [1 · CLO1] Ten-silo cho tenant lớn nhất mất > 1 tuần. Nghĩa là gì về mặt thương mại?** *(5.14, 13.7)*
*Đáp:* **escape hatch chưa tồn tại** ngoài giấy: khi khách doanh nghiệp yêu cầu tách (tuân thủ hoặc sự cố), bạn không có gì để bán. Rehearsal trên staging trong quý này cho **một** tenant nhỏ.

## D. Cụm P8–P9–P11: chạy thật (7 câu)

**D1 · [1 · CLO2] Error budget 30 ngày của SLO 99,9% là bao nhiêu phút?** *(11.1)*
*Đáp:* **43,2 phút** (99,95% ⇒ 21,6; 99,5% ⇒ 216).

**D2 · [3 · CLO2] Vì sao cần cả alert burn-rate **nhanh** và **chậm**?** *(11.1)*
*Đáp:* nhanh (14,4× / 1 h) bắt sự cố rõ; chậm (6× / 6 h) bắt **rò rỉ** (1% lỗi kéo dài 3 ngày) mà ngưỡng tuyệt đối không bắt, nhưng vẫn cháy hết budget.

**D3 · [2 · CLO3] Cluster etcd: RTT p99 giữa node 250 ms, election timeout 1.000 ms. Đánh giá?** *(8.2)*
*Đáp:* tỉ lệ 1:4 < 5× ⇒ **đang mời leader flap** (một GC pause là mất leader). Sửa: timeout ≥ 5× p99 hoặc sửa mạng/đặt node cùng AZ.

**D4 · [2 · CLO2] Throughput 1/2/4/8 replica: 1.000/1.900/3.400/4.200 rps. Kết luận?** *(11.3)*
*Đáp:* hiệu quả 100/95/85/**52,5%** ⇒ có **tài nguyên tranh chấp chung** (DB/cache/lock). Ở 8 replica, gấp đôi máy chỉ thêm ~24% ⇒ phải tách state, không thêm máy.

**D5 · [1 · CLO3] ALB idle timeout 60 s. Ping websocket nên đặt bao nhiêu và vì sao không 59 s?** *(4.6)*
*Đáp:* **35–40 s** (≤ 0,8 × 60) — chừa chỗ cho jitter và cho các lớp khác (nginx/CF) có thể cắt sớm hơn.

**D6 · [2 · CLO3] Cold start p99/p50 = 9× trên đường thanh toán. Hai cách chữa, chọn cách nào trước?** *(9.5)*
*Đáp:* (a) provisioned concurrency cho một lớp nhỏ (10–20% lưu lượng) — rẻ, sửa đúng đường nóng; (b) chuyển hẳn sang container. Trước hết: đo % request bị ảnh hưởng; nếu là request đầu phiên thì (a) là đủ.

**D7 · [3 · CLO4] Drill rollback mất 14 phút và phải gọi người khác. Kết luận?** *(9.7)*
*Đáp:* đường lùi **chưa sẵn sàng cho 2 giờ sáng**. Nguyên nhân thường: rollback phải build lại, migration không lùi được, không ai có quyền. Sửa: promote artifact (digest) + rollback = đổi tag + migration expand/contract.

## E. Cụm P10–P12–P14: an ninh, AI, biên giới (5 câu)

**E1 · [3 · CLO5] "Không chống ai" trong adversary ADR — vì sao đây là dòng quan trọng nhất?** *(10.1)*
*Đáp:* vì nó biến tranh luận ngân sách thành quyết định có biên: nếu đã tuyên bố không chống APT thì mua EDR cấp 3 thay vì vá IDOR là tiêu tiền sai. Dòng này thường không ai viết ⇒ hai năm sau mua trùng và vẫn hở.

**E2 · [2 · CLO3] Token app bị copy ra máy khác mà API vẫn trả 200. Thiếu lớp gì?** *(6.7)*
*Đáp:* token **không ràng buộc thiết bị** và không có attestation. Thêm: DPoP/mTLS binding, Play Integrity/App Attest cho endpoint nhạy cảm, rate limit theo thiết bị, và bước xác nhận server-side cho hành động tiền/ký.

**E3 · [2 · CLO1] LLM trả lời khác nhau ở 2 lần chạy, temp = 0. Bình thường không?** *(12.1)*
*Đáp:* có: nhiễu nền **5–15%** ở temp 0 (batching, phiên bản model, phần cứng), 10–40% khi temp > 0. Hệ quả: mọi "cải thiện" nhỏ hơn ngưỡng nhiễu là nhiễu; A/B test cần 200–1.000 mẫu/lớp.

**E4 · [2 · CLO3] Prompt cache hit chỉ 42%. Nghi gì và sửa thế nào?** *(12.2)*
*Đáp:* prompt **cấu trúc sai thứ tự**: phần tĩnh (system, tài liệu, few-shot) phải đứng **trước**, phần động sau. < 50% hit ở hệ có 60% token tĩnh = đang trả giá đầy đủ.

**E5 · [2 · CLO2] FHE chậm ~1.000×. Nó dùng được cho loại bài toán nào?** *(14.10.3)*
*Đáp:* chỉ **batch, độ trễ cao, khối lượng thấp** (1.000 req/ngày = 16 phút/ngày). Với 1.000 req/s ⇒ cần ~1.000 lõi ⇒ không khả thi. Kết luận đúng là "đúng cho đúng một lớp bài toán", không phải "chưa chín".

---

## Thang điểm gợi ý (thi 120 phút, 100 điểm)

| Phần | Câu | Điểm |
|---|---|---|
| Tính toán (A3, A4, A6, B10, C2, D1, D4) | chọn 4/7 | 8 điểm/câu = 32 |
| Chẩn đoán (B1, B5, D3, D6) | chọn 2/4 | 14 điểm/câu = 28 |
| Phán đoán (A10, B8, E1) | chọn 1/3 | 15 điểm = 15 |
| Kỹ năng (viết test IDOR 20 dòng + giải thích tầng sửa) | bắt buộc | 25 |

**Câu hỏi "tốt nghiệp" (dùng cho vấn đáp, không có đáp án duy nhất):** *"Hãy kể một con số trong sách mà bạn cho là **sai hoặc đã cũ**, và trình bày cách bạn kiểm chứng lại nó."* — Sinh viên giỏi sẽ mở `facts/versions.csv` và nêu ngày; sinh viên trung bình sẽ đoán.
