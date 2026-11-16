# 1.2 — CPU: lõi, cache, SIMD

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** part1-hardware-os.md (một phần)

---

## 0. Nhập môn

**Đọc trước:** 1.1 (thang thời gian).

**Sợi chỉ đỏ:** *Từ nano-giây tới mili-giây là cả một tháp — phần lớn khoảng cách đó nằm ở đâu trong một cái máy?* — trả lời: phần lớn khoảng cách nanogiây tới miligiây nằm ở bộ nhớ — CPU nhanh hơn DRAM hai bậc độ lớn, cache là cầu nối, và người viết code quyết định cầu đó được dùng hiệu quả hay bỏ không. Câu hỏi để lại cho chương sau: *Cache là tầng trên cùng — nhưng RAM lắp thật vào máy có gì mà spec không nói thẳng (NUMA, ECC)?*

**Thuật ngữ sẽ gặp:** *dòng cache* — đơn vị vận chuyển 64 byte giữa CPU và RAM; *L1/L2/L3* — các tầng cache nhỏ dần, chậm dần, chung dần; *gắn kết (locality)* — tính "đứng cạnh nhau" của dữ liệu được dùng liền nhau; *AoS/SoA* — hai cách xếp struct trong bộ nhớ, chọn đúng là tăng tốc miễn phí; *MESI* — bộ bốn trạng thái một dòng cache trên đa lõi; *SIMD* — một lệnh xử lý nhiều số cùng lúc.

**Ví dụ mở đầu:** Cùng một ma trận 4096×4096, duyệt theo hàng 23 ms, duyệt theo cột khoảng 200 ms — cùng máy, cùng thuật toán (số đo thật, xem quiz 1.2). Khác nhau chỉ ở cách dữ liệu chảy qua dòng cache. Ai chưa tin "cách xếp dữ liệu là quyết định hiệu năng số một của phần mềm" chỉ cần chạy hai vòng lặp này một lần.

## 1. Quyết định

Sau chương này bạn phải chọn được bốn thứ. Nếu không chọn được, chương đã thất bại.

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Ước lượng chi phí tính toán của một yêu cầu bằng bậc cache | Vòng lặp nóng của tôi đọc dữ liệu từ L1 hay từ DRAM? Chênh nhau bao nhiêu lần? |
| 2 | Bố cục dữ liệu (AoS/SaS) cho đường đi nóng | Mỗi lần truy cập kéo theo bao nhiêu byte vô ích trên cùng dòng cache 64B? |
| 3 | Có đáng vector hoá (SIMD) phần nóng không | Compiler tự vector hoá được không? Độ rộng thanh ghi tôi nhắm tới là bao nhiêu? |
| 4 | Chọn ISA cho workload mới (x86 / ARM / RISC-V) | Tôi mua lõi, tôi mua hiệu năng/watt, hay tôi mua hệ sinh thái? |

---

## 2. Cơ chế

### 2.1 Vì sao CPU nhanh mà bạn vẫn chậm: khoảng cách tốc độ CPU–DRAM

Tốc độ logic tăng theo Moore nhiều năm liền, còn độ trễ DRAM gần như đứng yên. Khoảng cách đó được lấp bằng **bộ nhớ đệm (cache)** — tức bằng **đoán**, không bằng băng thông thật. Toàn bộ nghệ thuật tối ưu CPU là nghệ thuật làm cho đoán trúng.

Bậc thang cache (xem 1.1 để thấy nó nằm trong toàn cảnh):

```
thao tác                 bậc độ trễ       so với L1
─────────────────────────────────────────────────
L1 hit                   ~4–5 chu kỳ      1×
L2 hit                   ~12–15 chu kỳ    ~3×
L3 hit                   ~40–50 chu kỳ    ~10×
DRAM                     ~200–300 chu kỳ  ~50×
miss sang NUMA xa        ~2× DRAM         ~100×
```

Con số chính xác thay đổi theo thế hệ CPU, nhưng **bậc** thì không. Một vòng lặp đọc tuần tự từ DRAM và một vòng lặp đọc từ L1 khác nhau ~50 lần — không tối ưu thuật toán nào lấp nổi khoảng cách đó bằng phần cứng tốt hơn; chỉ có bố cục dữ liệu tốt hơn mới lấp được.

### 2.2 Dòng cache và sự gắn kết không tự chọn

Cache không nạp từng byte mà nạp từng **dòng cache 64 byte** (x86/ARM chủ lưu; một số ARM dùng 128B). Hệ quả:

- **Tính cục bộ không gian là miễn phí.** Duyệt mảng theo thứ tự nằm trong bộ nhớ = mỗi dòng cache dùng được ~8 double trước khi trả tiền một lần DRAM. Duyệt ngược cột của ma trận hàng-major = mỗi phần tử một lần DRAM. Cùng số phép nhân, chênh nhau ~10×.
- **False sharing.** Hai thread ghi hai biến khác nhau nhưng nằm chung một dòng 64B: về logic không chia sẻ gì, về phần cứng thì dòng đó bị hai lõi "đá" qua lại (coherence traffic, ping-pong invalidate). Triệu chứng: chương trình song song chậm hơn tuần tự. Thuốc: `alignas(64)` từng biến mỗi thread (C/C++), hoặc pad mảng đếm.

### 2.3 AoS vs SoA: quyết định bố cục quan trọng nhất đời bạn (trong phần mềm)

```c
// AoS — Array of Structs: tự nhiên với người đọc
struct Particle { double x, y, z; double vx, vy, vz; };
Particle ps[N];          // 48 byte/particle = 0.75 dòng cache

// SoA — Struct of Arrays: tự nhiên với dòng cache
struct Particles { double x[N], y[N], z[N], vx[N], vy[N], vz[N]; };
```

Nếu đường nóng chỉ tính `x[i] + vx[i]*dt` thì SoA nạp đúng 2 dòng cho 8 particle; AoS kéo theo cả `y, z, vy, vz` — gấp ~3 lần băng thông thật cần thiết. Ngược lại, nếu đường nóng đọc **toàn bộ** trường của một phần tử thì AoS thắng. Quy tắc chọn: **đi theo truy vấn, không đi theo bản thể** — hệ cơ sở dữ liệu dùng columnar (5.8) vì đúng lý do này ở tầng lớn hơn.

### 2.4 MESI: bốn trạng thái của một dòng cache

Đa lõi ăn khớp nhau nhờ giao thức coherence. MESI đặt mỗi dòng ở một trong bốn trạng thái: **M**odified (tôi có bản đúng duy nhất, đã sửa), **E**xclusive (tôi có bản đúng duy nhất, chưa sửa), **S**hared (nhiều lõi cùng giữ bản đọc), **I**nvalid. Ghi vào dòng Shared buộc phải phát invalidate lên bus cho các lõi khác — chính cái giá đó sinh ra false sharing ở §2.2, và sinh ra chi phí của atomic chốt lock (một `lock cmpxchg` chạm dòng cache ~20–50 chu kỳ, còn contented thì gấp nhiều lần vì phải đợi dòng di chuyển giữa lõi).

Chuẩn đoán thực dụng: **lock contention trong userspace nhìn ở tầng MESI là đường cache di chuyển qua lại giữa các core** — bạn sẽ thấy nó trong `perf c2c` (mục 6) trước khi thấy nó trong code.

### 2.5 Song song trong một lõi: pipeline, superscalar, SIMD

Lõi hiện đại làm nhiều việc cùng lúc theo ba trục:

1. **Pipeline + superscalar:** mỗi chu kỳ retire ~4–8 lệnh µops. IPC (instructions per cycle) của code bạn là con số đầu tiên đáng xem: IPC < 1 gần như chắc chắn đang chờ nhớ (stall); IPC ~2+ là đang tính thật.
2. **Branch prediction:** nhánh sai trả giá ~15–20 chu kỳ (flush pipeline). Vòng lặp thường đoán trứng vì mẫu lặp; nhánh phụ thuộc dữ liệu ngẫu nhiên (ví dụ `if (hash % 2)`) là kịch bản tệ — và là lý do sort đôi khi nhanh hơn unsorted branch (nổi tiếng: "processing a sorted array is faster").
3. **SIMD (vector):** một lệnh xử lý nhiều phần tử. Độ rộng: SSE 128-bit, AVX2 256-bit (8 float), AVX-512 / SVE2 tới 512-bit (16 float). Compiler tự vector hoá vòng lặp thẳng, không phụ thuộc, nếu bạn không cản nó bằng aliasing (dùng `restrict`, kiểm tra bằng `-Rpass=loop-vectorize`).

AVX-512 từng làm CPU giảm xung nặng (Skylake-SP era, →1.10); từ Ice Lake/Sapphire Rapids và Zen 4/5 chi phí này gần như biến mất. Đừng lấy huyền thoại cũ làm quyết định mới — nhưng hãy đo lại trên chính CPU của bạn.

### 2.6 Ba ISA: mua gì khi chọn x86, ARM, RISC-V

| | x86-64 | ARM (v9, Neoverse) | RISC-V (RV64GC) |
|---|---|---|---|
| Thế mạnh | đơn lõi tối đa, hệ sinh thái dữ liệu lớn nhất | hiệu năng/watt, tùy biến vi kiến trúc, đám mây (Graviton, Axion) | mở, không phí bản quyền, tùy biến cho embedded/accelerator |
| SIMD | AVX2/AVX-512 | NEON/SVE2 (vector dài vô hạn được) | V extension (128–1024-bit) |
| Ai nên chọn mặc định | workload doanh nghiệp sẵn x86 | dịch vụ mới tính theo chi phí/watt ở cloud | sản phẩm chip, hệ nhúng đặc thù |
| Bẫy | tuân thủ nhị phân cũ, lõi to | dữ liệu benchmark hiện đại thay đổi nhanh, đòi test lại | hệ sinh thái phần mềm còn non (thiếu distro/driver chính thức cho một số stack) |

Ba ISA đều đủ nhanh cho 99% workload; khác biệt nằm ở chi phí tổng thể và hệ sinh thái, không ở "RISC nhanh hơn CISC" — lời khẳng định đó đã chết từ thập niên 90 khi x86 dịch lệnh sang µops nội bộ.

---

## 3. Bảng số & phiên bản

> Số liệu là **bậc độ lớn**, lấy từ tài liệu nhà sản xuất và đo đạc công khai; nhãn: **V** = verified có nguồn, **I** = ước lượng công nghiệp, **P** = trải nghiệm thực tiễn. Số cũ hơn 2 năm cần đối chiếu lại trước khi dùng ra quyết định.

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Dòng cache | 64 B | V | x86 & ARM server; một số ARM 128B |
| L1/L2/L3/DRAM | 4–5 / ~12 / ~40–50 / 200–300 chu kỳ | I | bậc ổn định nhiều thế hệ |
| Retire width lõi server | 4–8 µops/chu kỳ | I | Golden Cove, Zen 4/5 |
| Branch mispredict | ~15–20 chu kỳ | I | |
| AVX2 / AVX-512 rộng | 256 / 512 bit | V | SVE2: VL vô hạn cấu hình được |
`lock cmpxchg` không contend | ~20–50 chu kỳ | I | contented: phụ thuộc số lõi |
| NUMA remote | ~1,5–2× DRAM local | I | →1.3 |

---

## 4. Suy luận kiến trúc (áp S1–S6 cho tầng này)

- **S1 — Ràng buộc trên quyết định công nghệ:** "CPU nhanh hơn" không phải là một ràng buộc bạn điều khiển được ở tầng phần mềm; bậc cache mới là. Chuyển mọi tranh luận "máy này chậm" thành "dữ liệu nóng của tôi nằm ở bậc nào".
- **S2 — Tham số hóa:** Khi sizing (→11.3), đừng tính "số core × GHz"; tính **số dòng cache công việc** và **băng thông DRAM mỗi core**. Server 2-socket hiện đại có tổng băng thông DRAM ~400–600 GB/s chia cho 100+ lõi: mỗi lõi chỉ được ~4–5 GB/s — nhiều vòng lặp stream chạy 10 lõi đã làm bão hoà DRAM, thêm lõi chỉ thêm hàng chờ.
- **S3 — Đổi công lấy công:** SoA đổi tính dễ đọc của code lấy 2–3× băng thông; SIMD đổi tính chung chung của code lấy 4–16× thông lượng; lock-free đổi tính đúng dễ chứng minh lấy độ trễ đuôi. Mỗi cái chỉ đáng khi đo ra là cổ chai thật.
- **S4 — Chuyển dịch lệch:** Số lõi/socket tăng nhanh hơn băng thông DRAM → mỗi thế hệ, "băng thông mỗi lõi" giảm dần → các quyết định tối ưu băng thông (SoA, columnar, compression) mỗi năm lại đáng tiền hơn.
- **S5 — Thành phần phình:** AI training chuyển sang GPU (→1.5); nhưng tầng **CPU phục vụ** (serving, tokenization, data pipeline) vẫn phình — và vẫn là chỗ tốn tiền ẩn của hệ AI.
- **S6 — Cân bằng lại:** Khi mọi chuyện ở phần mềm đã tối ưu mà vẫn chậm, câu hỏi tự nhiên lùi một bậc: phải chăng vấn đề nằm ở bố cục dữ liệu, rồi ở loại bộ nhớ (CXL? HBM?), rồi ở chỗ dữ liệu được tính (near-data computing). Tầng lồng nhường câu trả lời cho tầng trên.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Chạy song song chậm hơn tuần tự | False sharing | `perf c2c record` → HITM bằng 0 nhưng dòng chạm nhau | §2.2 |
| Tối ưu thuật toán xong vẫn không nhanh | Đã stall ở DRAM từ đầu | `perf stat` IPC < 0,5 + nhiều `LLC-miss` | §2.1 |
| Vector hoá "rồi mà không nhanh" | Compiler không vector hoá được (aliasing/branch trong vòng) | build log `-Rpass=loop-vectorize` | §2.5 |
| Có service khác chạy thì service tôi chậm | AVX-512 downclock (CPU cũ) hoặc turbo budget chung | `turbostat` trong 2 tình huống | →1.10 |
| Lock chiếm đa số profile | Coherence traffic giữa lõi | `perf c2c`; off-CPU flamegraph | §2.4 |

---

## 6. Cách đo

```bash
# 1. IPC và stall — bước đầu tiên, luôn
perf stat -d ./program
# nhìn: IPC, LLC-load-misses, L1-dcache-load-misses

# 2. False sharing / coherence
sudo perf c2c record -- ./program && sudo perf c2c report --stdio
# tìm dòng có HITM cao — cho biết địa chỉ và offset trong dòng 64B

# 3. Chỗ nóng thực sự (sample, không xen kẽ)
perf record -g ./program && perf report
# off-CPU (đợi lock/IO): dùng offcputime (BCC) hoặc eBPF

# 4. Kiểm chứng giả thuyết cache bằng brute force
valgrind --tool=cachegrind ./program   # mô phỏng L1/L2/L3 chính xác tới từng dòng
```

Nguyên tắc đọc: **IPC + tỉ lệ miss LLC** trả lời "đang chờ nhớ hay đang tính"; `c2c` trả lời "ai đá dòng cache của ai"; còn flamegraph trả lời "đang chạy code gì". Ba câu trả lời đó phủ ~90% chẩn đoán tầng CPU.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay thế cho "tối ưu CPU thủ công":** (a) đổi thuật toán — gần như luôn rẻ hơn tối ưu vi mô; (b) đổi bố cục dữ liệu — ăn sâu vào §2.3; (c) thuê cứng: tăng băng thông DRAM, thêm kênh, chuyển sang máy HBM (→1.3); (d) dời sang GPU nếu thật sự tính dày (→1.5). Thứ tự đúng là (a)→(b)→(d)→(c); đảo thứ tự là đốt tiền.

Năm thấu kính:
- **Kinh tế:** 1 giờ tối ưu SoA ở đường nóng ăn tiền hơn 1 tuần tinh chỉnh khác; phần cứng đắt hơn nhân sự chỉ khi workload scale theo doanh thu.
- **Vận hành:** IPC/miss-rate nên lên dashboard cùng latency — metric phần cứng ẩn dưới metric dịch vụ.
- **An ninh:** Spectre/Meltdown và họ hàng là hoá đơn của đoán (speculation) — patch giảm IPC vài đến vài chục % tùy workload; đừng ngạc nhiên khi cùng code chậm hơn sau bản vá kernel.
- **Lịch sử:** Câu chuyện "x86 sắp chết" lặp lại mỗi 5 năm từ 1995; như mọi lần, đúng một phần (đứt đoạn ở phía cloud-side và embedded), sai ở phần đơn lõi.
- **Người dùng:** Mọi "máy chậm" mà người dùng cuối cảm nhận được đều hạ cánh về một trong: đợi DRAM, đợi lock, đợi mạng (→1.7), hoặc đợi disk (→1.4). Tầng CPU hiếm khi là thủ phạm cuối cùng.

---

## 8. Đọc tiếp & bài tập

- Bố cục dữ liệu lớn hơn (bảng cột, nén): **5.8** · Bộ nhớ thật (DDR5, NUMA, CXL, HBM): **1.3** · Xung-nhiệt-điện: **1.10** · Tính dày chuyển GPU: **1.5**
- **Bài tập 1:** Viết vòng duyệt ma trận 4096×4096 theo hàng rồi theo cột; đo và giải thích chênh lệch bằng `perf stat`.
- **Bài tập 2:** Viết chương trình đếm từ 4 thread có và không có `alignas(64)`; dùng `perf c2c` chỉ ra dòng shared.
- **Bài tập 3:** Lấy một service thật của bạn, trả lời: đường nóng đọc bao nhiêu byte mỗi yêu cầu? Bao nhiêu phần trăm rơi vào miss LLC? Nếu không trả lời được trong 30 phút — đó chính là khoảng trống chương này muốn lấp.
