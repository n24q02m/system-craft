# SYSTEM CRAFT — 145 THẺ TRA CỨU NHANH (MICROPAEDIA)

> Tổng hợp tự động từ `§1 Quyết định`, `§3 Số liệu` và `§5 Hỏng & Chẩn đoán` của toàn bộ 145 chương.

## Card 0.1 — Hệ quy chiếu 7 Trục & 4 Vòng Vũ trụ

**Quyết định cốt lõi:** Định vị mọi chủ đề trên cùng một hệ quy chiếu (7 trục) · Mỗi chương thuộc một Vòng đồng tâm (0–3) · Mỗi phần = đúng một trục chủ đạo (bài học audit 2026.11) · Lộ trình đọc theo vai (không tuần tự)
**Con số neo:** Số trục: `7` · Số vòng: `4 (ứng 3 tầng độ sâu + danh mục)` · Số phần: `15 (P0–P14)` · Số chương: `145`
**Bệnh & chẩn đầu tiên:** Họp kỹ thuật xoay vòng không chốt → `vẽ 7 trục, ghim vị trí từng ý` ; "Atlas này thiếu X" → `tra §2.3 + mục lục` ; Đọc tuần tự rồi kiệt sức → `bảng §2.5`

## Card 0.2 — 10 Tiền đề (Axioms) & Điều kiện biên

**Quyết định cốt lõi:** Tuyên bố tường minh 10 giả định nền của toàn atlas · Mỗi tiên đề gắn "điều kiện viết lại" · Phạm vi loại trừ (Vòng 3) ghi rõ · Cơ chế soát lại tiên đề theo ấn bản
**Con số neo:** Số tiên đề: `10` · PQC chuẩn hoá: `FIPS 203/204/205 (8/2024)` · Moore chậm lại: `~2015 trở đi` · Ấn bản đóng băng: `hàng quý`
**Bệnh & chẩn đầu tiên:** Tin số liệu sách đã cũ → `nhịp đóng băng §2.5` ; "Sao không nói về X" → `đọc điều kiện biên` ; Quyết định dựa tiên đề đã gãy → `§2.3 hằng quý`

## Card 0.3 — Ma trận 5 Lăng kính & 9 Động từ

**Quyết định cốt lõi:** Mọi đối tượng kỹ thuật đánh giá qua đủ 5 Lăng kính · Mọi chương gắn Động từ chủ đạo · 5 thấu kính kể chuyện (§7 mỗi chương) là cách hiện thực hoá 5 Lăng kính cho người đọc · Ma trận lens × động từ dùng như checklist review
**Con số neo:** Số Lăng kính: `5` · Số Động từ: `9` · Ma trận review: `45 ô` · Thấu kính kể chuyện: `5 (kinh tế/vận hành/an ninh/lịch sử/người dùng)`
**Bệnh & chẩn đầu tiên:** Kiến trúc "đẹp" nhưng sự cố triền miên → `đưa 5 lens vào ADR` ; Hóa đơn/án phí bất ngờ → `unit economics (11.5)` ; Sự cố an ninh "ai cũng ngạc nhiên" → `threat model (10.1)`

## Card 0.4 — Nhận thức luận: Provenance, 5 Mức Tin cậy & Chống phân rã

**Quyết định cốt lõi:** Mọi con số mang nhãn nguồn P/I/V/E · Mọi mục "số & phiên bản" có ngày kiểm tra · Ấn bản đóng băng hàng quý + errata công khai · Nguyên tắc "thà thiếu hơn sai" áp cho mọi mục chưa verify
**Con số neo:** Số nhãn nguồn: `5 (P/I/V/E/-)` · Số hạng phân rã: `3 (🔥/🌡/🧊)` · Chu kỳ đóng băng: `hàng quý` · versions.csv lần verify: `30/10/2026 (52 hàng)`
**Bệnh & chẩn đầu tiên:** Trích số cũ vào báo cáo → `nhãn 🔥 + ngày` ; Hai nguồn mâu thuẫn, bế tắc → `bảng §2.2` ; "Con số này chắc đâu có sẵn" → `quy tắc E hoặc cắt`

## Card 1.1 — Bậc thang độ trễ

**Quyết định cốt lõi:** **Đặt ranh giới đồng bộ ở đâu** — chỗ nào gọi thẳng, chỗ nào phải bất đồng bộ · **Tầng nào giữ dữ liệu** — cache trong tiến trình, cache ngoài, replica, hay chấp nhận đọc đĩa · **Có bao nhiêu hop mạng trên một request** · **Chọn vùng (region)** — một vùng, nhiều vùng, hay đẩy ra biên
**Con số neo:** Thao tác: `Độ trễ` · L1 cache: `~1 ns` · L2 cache: `~4 ns` · L3 cache: `~10–15 ns`
**Bệnh & chẩn đầu tiên:** p50 ổn, p99 tăng dần theo tải → `đo L = req đang xử lý; nếu L tăng tuyến tính với λ mà W không đổi → thiếu worker` ; Toàn hệ thống chậm đúng một dịp, mọi service cùng lúc → `xem biểu đồ theo thời gian, tìm service có p99 tăng **trước**` ; Độ trễ nhảy bậc, không tăng dần → `RSS so với limit; tỉ lệ cache miss`

## Card 1.2 — CPU: lõi, cache, SIMD

**Quyết định cốt lõi:** Ước lượng chi phí tính toán của một yêu cầu bằng bậc cache · Bố cục dữ liệu (AoS/SaS) cho đường đi nóng · Có đáng vector hoá (SIMD) phần nóng không · Chọn ISA cho workload mới (x86 / ARM / RISC-V)
**Con số neo:** Dòng cache: `64 B` · L1/L2/L3/DRAM: `4–5 / ~12 / ~40–50 / 200–300 chu kỳ` · Retire width lõi server: `4–8 µops/chu kỳ` · Branch mispredict: `~15–20 chu kỳ`
**Bệnh & chẩn đầu tiên:** Chạy song song chậm hơn tuần tự → ``perf c2c record` → HITM bằng 0 nhưng dòng chạm nhau` ; Tối ưu thuật toán xong vẫn không nhanh → ``perf stat` IPC < 0,5 + nhiều `LLC-miss`` ; Vector hoá "rồi mà không nhanh" → `build log `-Rpass=loop-vectorize``

## Card 1.3 — Bộ nhớ: DRAM, NUMA, ECC

**Quyết định cốt lõi:** Dùng loại DDR nào, bao nhiêu kênh cho máy mới · Bố trí tiến trình theo NUMA · Bật hay tắt THP cho dịch vụ nhạy latency · ECC cho máy sản xuất: có hay không bao giờ thắc mắc
**Con số neo:** DDR5-5600 mỗi kênh: `~44,8 GB/s` · Server 2S tổng băng thông: `~350–550 GB/s` · NUMA remote/local: `1,5–2× độ trễ` · THP size: `2 MB`
**Bệnh & chẩn đầu tiên:** Redis/DB spike p99 định kỳ → ``/sys/kernel/mm/transparent_hugepage/enabled`; SLOWLOG` ; Thêm RAM xong vẫn chậm → ``mlc` throughput vs latency curve` ; Latency "vô cớ" trên máy 2S → ``numastat` (Numa_Hit vs Numa_Miss)`

## Card 1.4 — Lưu trữ: SSD, RAID, độ bền

**Quyết định cốt lõi:** Loại SSD cho từng vai trò (write-heavy / read-mostly / cold) · Bảo vệ mất dữ liệu thế nào (RAID/EC/replication) · fsync/commit policy của DB nằm đâu trên trục bền–nhanh · Dùng SMR được chưa (giá rẻ hơn)
**Con số neo:** P/E: SLC/MLC/TLC/QLC: `~100k / ~3k / ~1k / ~300` · Enterprise DWPD: `1–3 (read-intensive), 10+ (write-intensive)` · NVMe Gen4 x4 / Gen5 x4: `~7 / ~14 GB/s` · fsync có PLP: `~10 µs`
**Bệnh & chẩn đầu tiên:** p99 I/O vọt 100× giữa benchmark/production → ``fio` sustained 30 phút; SMART `% wear`` ; Throughput sụp sau vài phút ghi lớn → `sustained write; so datasheet "up to"` ; RAID5 rebuild fail giữa chừng → ``smartctl -a` tất cả đĩa; tính xác suất`

## Card 1.5 — GPU & accelerator: SIMT, roofline, tensor core

**Quyết định cốt lõi:** Workload này có đáng đưa lên GPU không · Chạy shared serving hay dedicated · Precision nào (FP32/FP16/BF16/FP8/FP4) · Cắt GPU thế nào giữa các tenant (MIG / time-slicing / dedicated)
**Con số neo:** Warp / wavefront: `32 / 64 thread` · Băng thông HBM3e (B200): `~8 TB/s · 192 GB` · Băng thông HBM4 (VR200): `~22 TB/s · 288 GB` · FP4 dense (B200): `~2,2 PFLOPS`
**Bệnh & chẩn đầu tiên:** GPU 100% nhưng token/s thấp → `DCGM `SM_ACTIVE` vs `TENSOR_ACTIVE`; profile` ; TTFT cao dù GPU "rảnh" → `vLLM metrics: num_waiting vs num_running` ; Throughput tăng thêm GPU thì giảm → `Nsight Systems: thời gian NCCL all-reduce`

## Card 1.6 — Bus & liên kết: PCIe, NVLink, RDMA

**Quyết định cốt lõi:** Phân bổ lane PCIe giữa GPU/NIC/NVMe · Topo liên GPU (NVLink full / ngày càng nhiều / chỉ PCIe) · Mạng cụm: RoCE hay InfiniBand (hay Ethernet thường) · Có offload xuống NIC/DPU không
**Con số neo:** PCIe Gen4/5/6 mỗi lane: `~2 / ~4 / ~8 GB/s` · Lane mỗi socket server: `80–128` · NVLink4 / 5 / 6: `0,9 / 1,8 TB/s·GPU / 260 TB/s·rack` · NIC production: `100–400 GbE phổ thông; 800G ở AI spine`
**Bệnh & chẩn đầu tiên:** GPU.train chậm hơn spec 2× → ``nvidia-smi topo -m`; NCCL debug log` ; Thêm NIC x8, tốc độ không đổi → ``lspci -vv` (LnkSta vs LnkCap)` ; RoCE throughput thất thường → ``roce_cfg`/debug PFC counters`

## Card 1.7 — Mạng vật lý: quang, RTT, BDP, đệm

**Quyết định cốt lõi:** Kích thước window/batch cho đường trễ đã biết · MTU & jumbo trong cụm · Thiết kế oversubscription của fabric · Đệm switch & chiến lược xếp hàng
**Con số neo:** Tốc độ ánh sáng trong sợi: `~⅔c = 5 µs/km` · RTT nội cụm (cùng DC): `0,1–1 ms` · RTT cùng khu vực (same-region): `1–10 ms` · RTT liên lục địa: `50–300 ms`
**Bệnh & chẩn đầu tiên:** 1 stream chậm, nhiều stream nhanh → ``ss -i` (cwnd, rwnd); iperf -P 1 vs -P 8` ; SSH được, scp/HTTPS treo → ``tracepath host`; test MTU giảm` ; Shuffle/batch sụp theo chu kỳ → `switch drop counter sub-second; đồ thị retrans`

## Card 1.8 — Ảo hoá, cloud, TEE

**Quyết định cốt lõi:** Chọn máy ảo / container / bare-metal cho workload này · Ảo hoá thiết bị: virtio hay SR-IOV passthrough · Có đặt dịch vụ nhạy cảm vào TEE không · Chi phí ảo hoá của tôi là bao nhiêu và ai trả
**Con số neo:** VM exit: `~1–10 µs` · Boot container / VM: `ms / s` · Overhead CPU-bound VM: `0–2%` · Overhead I/O-dense VM: `5–15%`
**Bệnh & chẩn đầu tiên:** Steal% cao trên cloud VM → ``top` (st), `vmstat`; đổi máy đối chứng` ; VM I/O chậm hơn bare-metal 2× → ``perf` vhost thread; RSS/multiqueue config` ; p99 nghẽt theo chu kỳ 1s → ``perf kvm stat``

## Card 1.9 — Đồng hồ: NTP, PTP, leap second

**Quyết định cốt lõi:** Chuẩn thời gian nào cho cụm: NTP hay PTP · Deadline/timeout tính theo đồng hồ nào (mono vs wall) · Timestamp phân tán ghi thế nào (logic clock / hybrid / TrueTime-style) · Xử lý leap second theo hướng nào
**Con số neo:** Thạch anh: `±10–50 ppm` · NTP (chrony, Internet): `~1–10 ms` · PTP hardware: `~0,1–1 µs` · Google/AWS smear: `0,1 ppm gradient ≈ 4,6 ms/h (24h)`
**Bệnh & chẩn đầu tiên:** Bản ghi mới bị bản ghi cũ ghi đè (LWW) → `so `date -u` 2 node; chronyc tracking` ; Timeout "âm"/đồ thị spike 1 lần → `grep chrony log; review code dùng REALTIME` ; Log 2 máy không khớp khi đối chiếu → ``chronyc sources` từng máy`

## Card 1.10 — Điện, nhiệt, làm mát

**Quyết định cốt lõi:** Chế độ hiệu năng cho máy sản xuất (turbo mặc định / cap tần số / perf-governor) · Phương án làm mát cho mật độ công suất tôi nhắm · Topo điện: N+1, 2N, hay chấp nhận downtime · Carbon-aware scheduling có đáng không
**Con số neo:** PL2 / PL1: `1,5–2×, trong vài–chục s (tau)` · Tj-max: `~95–105°C` · Air / RDHx / D2C / immersion: `10–20 / 20–40 / 50–120 / 100–200+ kW/rack` · Rack: Hopper / Blackwell / VR200: `~40 / 120–130 / 190–230 kW`
**Bệnh & chẩn đầu tiên:** Service chậm đúng giờ nắng trưa → ``turbostat` tần số + sensor nhiệt theo giờ` ; p99 ổn định, sau đó tụt vọt định kỳ → ``rapl`/powercap energy theo giây` ; Benchmark không tái lập được → `làm lạnh máy trước khi đo; ghi nhiệt vào log`

## Card 2.1 — Bộ nhớ Ảo, Page Table, TLB, HugePages & OOM Killer

**Quyết định cốt lõi:** Chính sách overcommit (`vm.overcommit_memory` 0/1/2) · Cgroup memory limit + `memory.high` xử phạt · HugePages tĩnh hay THP (→1.3) cho dịch vụ · Fork-heavy workload (Redis BGSAVE, proxy) đặt ở đâu
**Con số neo:** Kích thước trang: `4 KB · huge 2 MB / 1 GB` · TLB mục: `~1–2k/lõi` · Walk 4-tầng khi miss: `~4 lần đọc bộ nhớ` · Python/Go runtime overhead so với C: `2–10× bộ nhớ/tuyến`
**Bệnh & chẩn đầu tiên:** Pod OOMKilled dù RSS < limit → ``dmesg`; so `memory.max` vs `memory.current` (không phải RSS)` ; Hệ thống chậm dần rồi sập (spiral) → ``vmstat 1` (si/so); `/proc/pressure/memory`` ; Redis/DB spike p99 định kỳ → ``SLOWLOG`; `info memory` trong lúc fork`

## Card 2.2 — Stack vs Heap, Allocator & Nguyên lý Đồng bộ cấp thấp

**Quyết định cốt lõi:** Allocator cho workload (glibc / jemalloc / mimalloc / per-runtime) · Ngưỡng "đáng đưa lên heap" của cấu trúc dữ liệu · Khóa mức thấp: mutex, CAS spinlock, hay lock-free queue · Stack size cho service (thread stack × số thread)
**Con số neo:** Stack push/pop: `~1 lệnh` · Thread stack mặc định: `8 MB (ảo) Linux` · malloc không tranh: `~50–100 ns` · CAS không tranh: `~10–20 ns`
**Bệnh & chẩn đầu tiên:** RSS không giảm sau khi "free hết" → ``malloc_stats()`/jemalloc stats; heap profile` ; Latency spike theo số lõi tăng → ``perf lock`; off-CPU flame` ; CPU 100% nhưng throughput sụt → `perf; flame graph đỉnh `__pauser`/`osq_lock``

## Card 2.3 — Process, Thread, Context Switch, EEVDF, cgroups v2 & PSI

**Quyết định cốt lõi:** Đặt requests/limits CPU & QoS class (Guaranteed/Burstable) · Thread-per-connection hay worker pool cố định · Nhận CPU burst (burstable) hay cam kết riêng · NICE/cpu.weight cho service lẫn nhau
**Con số neo:** Tạo thread / fork: `~10 µs / ~100 µs–ms` · Context switch cùng process: `1–5 µs` · Syscall (post-mitigation): `~100–300 ns+` · CFS period mặc định: `100 ms`
**Bệnh & chẩn đầu tiên:** p99 gấp đôi, CPU host ~60% → ``cpu.stat` nr_throttled, throttled_usec` ; CPU 100%, throughput giảm khi scale thread → ``pidstat -wt`; `vmstat` cs` ; Service tương tác chậm hơn batch → ``cpu.weight` audit`

## Card 2.4 — VFS, Page Cache, Ngữ nghĩa Bền vững (fsync/O_DIRECT)

**Quyết định cốt lõi:** Ngữ nghĩa bền vững: fsync/fdatasync mỗi commit, nhóm, hay không · Buffered I/O hay O_DIRECT (hoà page cache) · Cấu hình dirty writeback (vm.dirty_*) cho workload · Pattern ghi an toàn crash (write-temp + rename + fsync dir)
**Con số neo:** fsync (SSD PLP / không PLP): `~10 µs / ~1–10 ms` · fdatasync vs fsync: `rẻ hơn khi size cố định` · Dirty ratio mặc định: `20% / 10% background` · Page cache hit: `~ns (RAM)`
**Bệnh & chẩn đầu tiên:** write() khựng đột ngột khi ghi nhiều → ``/proc/vmstat` nr_dirty; `iostat` util` ; DB TPS thấp hơn benchmark 10× → ``pg_test_fsync`; fio --fsync=1` ; File mới mất sau crash dù "đã lưu" → `audit code theo checklist §2.5`

## Card 2.5 — Mô hình I/O: epoll, Reactor/Proactor, io_uring & Zero-copy

**Quyết định cốt lõi:** Mô hình I/O: thread-per-conn / epoll+reactor / io_uring · Edge-triggered (ET) hay level-triggered (LT) với epoll · Zero-copy (sendfile/splice) ở đâu trong đường phục vụ · Worker pool cho việc chặn (blocking) còn sót
**Con số neo:** select/poll chi phí: `O(n) mỗi call` · epoll_wait: `O(ready)` · Syscall io_uring: `~1/batch (0 với SQPOLL)` · sendfile tiết kiệm CPU: `30–50% (payload tĩnh lớn, không TLS)`
**Bệnh & chẩn đầu tiên:** Càng nhiều conn càng chậm tuyến tính → ``vmstat` cs; ss -s count` ; Đôi khi "mất" request không lỗi → `strace read pattern; chuyển LT thử` ; CPU cao ở softirq, không phải app → `perf softirq`

## Card 2.6 — Linux Network Stack & Socket Tuning (somaxconn, conntrack, XDP)

**Quyết định cốt lõi:** Accept queue (somaxconn, backlog) theo tải thật · TIME_WAIT policy (tw_reuse, port range) cho client nhiều outbound · Conntrack table size + timeout cho NAT/proxy · Congestion control (cubic/BBR) + buffer (tcp_rmem/wmem)
**Con số neo:** somaxconn mặc định: `4096 (6.x); cũ 128` · TIME_WAIT: `60 s` · Ephemeral range mặc định: `~28k–64k cổng` · nf_conntrack_max: `64k–256k theo RAM`
**Bệnh & chẩn đầu tiên:** Connection refused/timeout khi tải cao → ``ss -lnt` (Recv-Q = Send-Q = trần)` ; Outbound lỗi "cannot assign port" → ``ss -s`; netstat -tan count` ; Gói mất âm thầm sau NAT/Service → ``conntrack -C`; dmesg "table full"`

## Card 2.7 — Cô lập: Namespaces, seccomp, Container vs MicroVM

**Quyết định cốt lõi:** Mức cô lập cho code không tin cậy: container / gVisor / Kata / Firecracker · Bộ capabilities & seccomp profile tối thiểu cho workload · Chạy sidecar trong cùng pod hay microVM riêng · Rootless container / user namespace cho CI & tenant
**Con số neo:** Overhead container vs bare: `~0%` · gVisor overhead: `~5–25% syscall-heavy` · Firecracker boot: `~125 ms` · Kata boot: `~1 s/giây`
**Bệnh & chẩn đầu tiên:** Container "nhìn thấy" process/host khác → ``lsns`; `kubectl get pod -o yaml`` ; App cần quyền lạ để chạy → `audit log cap; thêm đúng 1 cái` ; Seccomp kill syscall mới sau upgrade → `runtime log "seccomp"; profile diff`

## Card 2.8 — eBPF: Lập trình hoá Kernel an toàn

**Quyết định cốt lõi:** Dùng eBPF cho quan sát thay agent sidecar/kernel module? · Dùng cho datapath (XDP/tc — →2.6) khi nào · Ai được phép nạp eBPF vào cụm (signature/allowlist) · Build quản lý phiên bản kernel (CO-RE)
**Con số neo:** Verifier limit lệnh: `1M (5.2+)` · Overhead/program-call: `~tens–hundreds ns` · BTF/CO-RE ổn định: `5.x+` · Bounded loops: `5.3+`
**Bệnh & chẩn đầu tiên:** Verifier reject program → `log verifier; viết lại bounded` ; Tool chết sau upgrade kernel → ``bpftool btf dump`; CO-RE check` ; CPU cao khi bật tracing → `giảm attach; sample thay vì đếm từng`

## Card 3.1 — Lý thuyết Đồng thời & 4 Trường phái Quản lý Bộ nhớ

**Quyết định cốt lõi:** Mô hình đồng thời: event loop / thread pool / green threads / async-await · Trường phái bộ nhớ cho hệ mới: GC tracing / RC / ownership / manual · Mức song song hoá (Amdahl thật sự của bài toán) · Chiến lược backpressure thay xếp hàng vô hạn
**Con số neo:** Stack goroutine/virtual thread: `~KB lúc khởi đầu` · Go GC pause: `< 1 ms thường` · ZGC pause: `< 1 ms (thuật toán thiết kế 10ms max)` · Utilization an toàn: `70–80%`
**Bệnh & chẩn đầu tiên:** Thêm worker không tăng throughput → `profile phần tuần tự; đo lock` ; p99 nổ khi CPU > 80% → `utilization graph + latency` ; "Leak" ở Python/Swift → `gc module/heap snapshot`

## Card 3.2 — Python Runtime (3.11 → 3.15)

**Quyết định cốt lõi:** Song song hoá bằng gì: multiprocess / free-threaded 3.13t+ / C-ext / sang Go · Phiên bản Python cho service mới · ASGI server + framework + JSON path · On-demand import & khởi động lạnh (FaaS)
**Con số neo:** 3.10 EOL: `2026-10-01` · Free-threaded: `3.13 experimental → 3.14+ official track` · orjson vs json: `~5–10×` · pandas import: `~0,5–1 s`
**Bệnh & chẩn đầu tiên:** Multi-thread không ăn CPU → `py-spy (thấy 1 thread chạy)` ; Latency vọt khi parse JSON lớn → `orjson; msgspec` ; Event loop lag cao → `PYTHONASYNCIODEBUG`

## Card 3.3 — Node.js / TypeScript Runtime (18 → 26 LTS)

**Quyết định cốt lõi:** Scale theo process (cluster/PM2) hay container nhiều pod · Cái gì được phép chặn event loop — và chạy ở đâu khi cần · Worker threads cho CPU-bound hay gọi service khác · TypeScript build path (tsc/tsc-go/bundler) & typecheck trong CI
**Con số neo:** Event loop delay khoẻ: `< 10 ms p99` · V8 heap default: `~4 GB (cũ) — đặt tường minh` · Worker thread init: `~ms + MB` · cluster scale: `tuyến tính theo lõi`
**Bệnh & chẩn đầu tiên:** API Node chậm tốn thời mọi request → `loop delay; --prof` ; OOM sau vài ngày → `heap snapshot diff` ; Đôi khi treo không lỗi → `strace; async hooks`

## Card 3.4 — Go Runtime (1.23 → 1.27)

**Quyết định cốt lõi:** GOMAXPROCS & container quota · GC mục tiêu: GOGC / GOMEMLIMIT đặt thế nào · Concurrency nguyên thuỷ nào cho từng bài toán · Việc chặn (CGO/sync/fs) đặt ở đâu để không đói scheduler
**Con số neo:** Goroutine khởi tạo: `~2 KB` · GC pause: `< 1 ms thường` · GOMEMLIMIT: `1.19+` · GOMAXPROCS cgroup-aware: `1.25+`
**Bệnh & chẩn đầu tiên:** Số goroutine tăng đều không giảm → `pprof goroutine (đếm theo trạng thái)` ; p99 spike định kỳ → `gctrace; metrics heap` ; Throughput thấp dù CPU rảnh → `pprof block; trace`

## Card 3.5 — Rust Runtime (1.85 → 1.99)

**Quyết định cốt lõi:** Tokio multi-thread hay current-thread (+ rayon cho CPU) · Async ở đâu, sync ở đâu trong cùng codebase · spawn_blocking cho việc chặn (I/O file, crypto, sleep) · Build/deloy: cargo features, compile time, image
**Con số neo:** Rust stable: `1.99.1 (10/2026); Edition 2024 từ 1.85` · Task async: `~hundreds bytes` · Memory-safety CVE giảm: `~60–70% nhóm bị xoá` · Startup binary: `~ms`
**Bệnh & chẩn đầu tiên:** Tokio task đói (latency cao, CPU thấp) → `tokio-console; tracing` ; Deadlock khó hiểu → `audit pattern; clippy lint` ; Compile chậm kéo dài tuần → `cargo build --timings`

## Card 3.6 — Java / JVM Runtime (8 → 25 LTS / 27)

**Quyết định cốt lõi:** Thread model: virtual threads (21+) hay platform pool · GC: G1 (mặc định) / ZGC generational / Shenandoah · Heap sizing trong container (MaxRAMPercentage, không -Xmx cứng) · Upgrade path LTS 17/21/25 — thời điểm và trở lực
**Con số neo:** LTS hiện hành: `25 (EOL 2031)` · G1 pause mục tiêu: `~ms` · ZGC pause: `< 1 ms (heap TB)` · Virtual threads GA: `21; unpin synchronized JDK 24`
**Bệnh & chẩn đầu tiên:** Pool cạn thread, service treo → `JFR; jstack; pool metrics` ; Pause vài trăm ms định kỳ → `GC log; JFR alloc profile` ; Sau deploy chậm 10 phút → `JFR compiler events`

## Card 3.7 — C / C++ Runtime (C++14 → C++26)

**Quyết định cốt lõi:** Có bắt đầu dự án mới bằng C++ không · Chuẩn hiện đại (20/23/26) + sanitizers trong CI · Mô hình concurrency: std::execution (C++26), Seastar, hay thread pool truyền thống · Phụ thuộc & phân phối (vcpkg/Conan, static link)
**Con số neo:** Chuẩn mới nhất: `C++26 (hoàn tất 2026)` · Sanitizer overhead: `ASan ~2×; TSan ~5–10×` · Seastar: `1 thread/lõi, shared-nothing` · Startup: `~ms`
**Bệnh & chẩn đầu tiên:** Crash khó tái hiện → `ASan/TSan trong CI` ; Prod đúng, staging sai → `UBSan; chuẩn hoá flags` ; Build vỡ theo platform → `container hoá; vcpkg`

## Card 3.8 — WebAssembly & WASI 0.3

**Quyết định cốt lõi:** Wasm dùng ở đâu: edge / plugin / sandbox đa ngôn ngữ · Component Model + WASI 0.2/0.3 cho giao tiếp · Ngôn ngữ biên dịch sang Wasm nào · Runtime mục tiêu (Wasmtime/WasmEdge/edge provider)
**Con số neo:** WASI: `0.3.2 (10/2026)` · Wasmtime: `49.x` · Hiệu năng tính toán: `~80–100% native` · Cold start edge: `~ms`
**Bệnh & chẩn đầu tiên:** Module to bất thường → `wasm-opt -Oz; strip` ; Plugin tốn CPU vô hạn → `cấu hình fuel/epoch` ; Boundary call chậm → `gộp batch; interface thô hơn`

## Card 3.9 — Ma trận 6+1 Runtime, 12 Bẫy xuyên ngôn ngữ & Chi phí vòng đời

**Quyết định cốt lõi:** Chọn runtime cho workload mới · Chuẩn hoá "ít ngôn ngữ" hay đa ngôn ngữ theo đặc thù · Checklist bẫy xuyên ngôn ngữ cho mọi codebase · TCO runtime (không chỉ p99)
**Con số neo:** Startup: Go/Rust vs JVM (không CRaC): `~ms vs ~s` · Footprint RSS hello-world: `Go/Rust ~10–20 MB; JVM ~100+ MB` · p99 tốt nhất (tương đối): `Rust ≥ C++ > Go ≈ Java(GC đúng) > Node ≈ Python` · Đội hình trung bình thị trường 2026: `Python/TS > Java > Go > C++ > Rust`
**Bệnh & chẩn đầu tiên:** Một service chậm, không rõ vì runtime → `py-spy/pprof/JFR/loop-lag` ; Lỗi dữ liệu "lạ" giữa 2 service → `contract test + fixture chung` ; Team chậm, không phải máy → `audit số runtime/đội`

## Card 3.10 — Giải phẫu Tầng Phục vụ (9 Trạm)

**Quyết định cốt lõi:** Số worker/pool mỗi trạm (theo Little) · Timeout budget toàn trình + phân bổ xuống 9 trạm · Mỗi trạm có hàng đợi riêng — sâu bao nhiêu, từ chối khi nào · Retry/phần dư đặt ở trạm nào
**Con số neo:** Số trạm chuẩn: `9` · Queueing phi tuyến từ: `~70–80% util` · Retry factor thực tế: `1,2–2× lúc sự cố` · DB conn cost: `~MB mỗi conn (Postgres)`
**Bệnh & chẩn đầu tiên:** Timeout client nhưng server "xong việc" → `trace span; deadline header` ; Pool cạn định kỳ → `pool wait metric` ; p99 tăng nhưng mọi CPU rảnh → `queue depth per trạm`

## Card 3.11 — HTTP/RPC Stack của 6 Ngôn ngữ (ngang bằng)

**Quyết định cốt lõi:** HTTP stack cho service mới từng ngôn ngữ · JSON path (serializer) + schema-first hay code-first · HTTP/1.1 keep-alive pool hay HTTP/2 multiplexing nội bộ · gRPC/protobuf cho đường nội bộ quan trọng
**Con số neo:** JSON vs protobuf CPU: `~2–5×` · json → orjson: `~5–10×` · Chiếm CPU serialization: `10–40% traffic cao` · HTTP/2 gain nội bộ: `ít conn, multiplex`
**Bệnh & chẩn đầu tiên:** CPU cao bất thường ở traffic lớn → `profile; orjson/proto` ; 502 lẻ tẻ sau deploy → `audit timeout 2 đầu` ; Conntrack đầy (→2.6) → `pool config; HTTP/2`

## Card 4.1 — Transport Hiện đại: TCP (BBRv3), TLS 1.3 & QUIC

**Quyết định cốt lõi:** Bật TLS 1.3 + 0-RTT ở đâu · mTLS nội bộ (service-to-service) · Congestion control (cubic/BBRv3) cho đường ngoài · Cho phép QUIC/HTTP/3 ở edge chưa
**Con số neo:** TLS 1.2 / 1.3 handshake: `2-RTT / 1-RTT (0-RTT resume)` · QUIC + TLS: `handshake gộp 1-RTT` · BBR vs cubic trên đường lossy: `nhiều lần throughput` · Cert lifetime nội bộ: `24h–90 ngày (tự động)`
**Bệnh & chẩn đầu tiên:** CPU cao khi nhiều connection mới → `ssl metrics; session ticket bật chưa` ; POST đôi khi lặp 2 lần → `audit endpoint 0-RTT cho phép` ; H3 không hoạt động một số mạng → `fallback H2 (mặc định); đo tỉ lệ`

## Card 4.2 — Tiến hoá HTTP: HTTP/1.1 → HTTP/2 → HTTP/3

**Quyết định cốt lõi:** Nội cụm chạy HTTP/1.1 hay HTTP/2 · Bật HTTP/3 cho người dùng cuối (qua CDN) · Cấu hình stream concurrency + keep-alive đúng · Compression & header budget
**Con số neo:** H1 connection/host (browser): `~6` · HPACK giảm header: `~90% lặp lại` · H2 HoL: `1–2% loss làm chậm tất cả stream` · H3 cải thiện mạng yếu: `có nghĩa (Google/Meta công bố)`
**Bệnh & chẩn đầu tiên:** Cả trang nghẽn vì 1 request chậm → `retrans; thử H1/H3 đối chứng` ; 502 sau deploy (→3.11) → `audit 2 đầu` ; Conntrack đầy (→2.6) → `chuyển H2 nội bộ + pool`

## Card 4.3 — REST, JSON Schema & OpenAPI 3.2

**Quyết định cốt lõi:** Contract-first hay code-first (và ai review) · OpenAPI 3.2 dùng tính mới (SSE, QUERY method) khi nào · JSON Schema nghiêm đến đâu (additionalProperties, required) · Sinh code/docs/mock từ spec (generator pipeline)
**Con số neo:** OpenAPI: `3.2 (09/2025)` · JSON Schema: `2020-12` · Validate cost: `~0,1–1 ms` · Sinh client: `giảm bug biên`
**Bệnh & chẩn đầu tiên:** FE/BE cãi nhau về response → `contract test trong CI` ; Breaking change sập client khác team → `oasdiff trong PR` ; Dữ liệu bẩn vào DB → `JSON Schema strict`

## Card 4.4 — RPC Nhị phân: gRPC, ConnectRPC & Protobuf

**Quyết định cốt lõi:** gRPC hay ConnectRPC cho đường nội bộ · Đặt field number & reserved đúng cách · Compatibility mode: backward/forward/full · Deadline & retry policy ở service config (không phải code rải)
**Con số neo:** Protobuf vs JSON: `~2–5× parse/nhỏ hơn` · gRPC message limit mặc định: `4 MB` · Connect unary: `HTTP/1.1 + JSON hoặc gRPC/H2` · Deadline: `không mặc định — phải đặt`
**Bệnh & chẩn đầu tiên:** Tải không đều qua pod → `grpc metrics per backend` ; Bão request lúc dependency chậm → `audit config` ; Sập sau khi "dọn field" → `protobuf lint (buf)`

## Card 4.5 — Truy vấn Linh hoạt & BFF: GraphQL (Federation) & tRPC

**Quyết định cốt lõi:** GraphQL cho ai: public API hay chỉ BFF nội bộ · Giới hạn độ sâu/chi phí truy vấn (depth & cost limit) · Persisted queries cho production public · DataLoader/N+1 ở mọi resolver
**Con số neo:** N+1 nếu không DataLoader: `10²–10³ query/request` · Round-trip giảm vs REST ghép: `4 → 1` · Persisted queries: `+ cache CDN được` · tRPC biên: `TypeScript-only`
**Bệnh & chẩn đầu tiên:** Server CPU vọt vì 1 client → `cost limit; log complexity` ; p99 tệ dù DB nhanh → `trace: query/request` ; CDN không cache được → `persisted queries`

## Card 4.6 — Thời gian thực: SSE, WebSocket & WebTransport

**Quyết định cốt lõi:** SSE hay WebSocket cho luồng một chiều · WebTransport/WebRTC khi nào · Kết nối dài qua hạ tầng: LB idle timeout, proxy buffering · Trạng thái kết nối & reconnect protocol
**Con số neo:** SSE qua HTTP: `mọi version; H2 hết giới hạn 6 conn` · Ping interval chuẩn: `25–30 s` · WebTransport: `cần HTTP/3` · SSE overhead: `~byte/event + newline`
**Bệnh & chẩn đầu tiên:** SSE client nhận cụm mỗi vài giây → `curl -N trực tiếp vs qua proxy` ; WS đứt đúng chu kỳ (60s/120s) → `capture ping; audit config` ; Reconnect = mất sự kiện → `log sequence gap`

## Card 4.7 — Hợp đồng Bất đồng bộ: AsyncAPI 3.0, CloudEvents & Schema Registry

**Quyết định cốt lõi:** Schema cho sự kiện: JSON Schema trong AsyncAPI hay Avro/Protobuf trong registry · Compatibility mode (backward/forward/full) cho từng topic · Envelope chuẩn hoá (CloudEvents) hay schema riêng · Registry + CI gate cho schema (giống OpenAPI diff — →4.3)
**Con số neo:** AsyncAPI: `3.0 (2024)` · CloudEvents: `1.0 (specversion)` · Compatibility 3 mode: `backward/forward/full` · Cooldown giữa 2 version schema: `theo vận tốc deploy consumer`
**Bệnh & chẩn đầu tiên:** Dữ liệu consumer sai âm thầm → `audit: % topic có schema` ; Consumer mới vỡ sau deploy producer → `registry check log` ; Metadata mỗi team mỗi kiểu → `adopt CloudEvents`

## Card 4.8 — Vòng đời API: Versioning, Idempotency-Key, Rate Limit, Webhooks, RFC 9457

**Quyết định cốt lõi:** Chiến lược versioning (URI /v2, header, date-based) + chính sách deprecate · Idempotency-Key cho POST có hiệu ứng (đặt hàng/thanh toán) · Pagination chuẩn (cursor/keyset) + rate limit (theo tenant/IP/token) · Chuẩn lỗi RFC 9457 + webhook có ký + retry
**Con số neo:** Deprecation headers: `RFC 8594 (Sunset)` · Problem details: `RFC 9457 (2024)` · Idempotency TTL: `24h+ (Stripe-style)` · Cursor vs offset tại 1M rows: `ms vs s`
**Bệnh & chẩn đầu tiên:** Trừ tiền/lập đơn 2 lần → `audit Idempotency-Key` ; Danh sách lặp/mất item khi phân trang → `đổi cursor` ; Một tenant dập API của mọi người → `limit theo tenant`

## Card 4.9 — Ma trận Chọn Giao thức, 10 Bẫy & Gateway/Mesh

**Quyết định cốt lõi:** Họ giao thức cho từng cặp (client-public, service-service, event, realtime) · Gateway (ngõ vào chung) đến đâu thì dừng · Service mesh có đáng cho cụm tôi · Chính sách "một giao thức mặc định" của org
**Con số neo:** Gateway p99 mục tiêu: `< 5 ms` · Mesh sidecar overhead: `~5–15% latency/HTTP (giảm với ambient)` · Ngưỡng mesh đáng: `~15–20+ service` · Số giao thức đồng thời quản lý được: `3–4/org`
**Bệnh & chẩn đầu tiên:** 10 cách gọi API trong 1 org → `bảng §2.5` ; Gateway là SPOF nghẽn → `profile gateway; dời nghiệp vụ` ; Mesh "có nhưng không biết làm gì" → `audit feature dùng thật`

## Card 5.1 — Nền tảng Storage Engine: B-Tree, LSM, WAL, MVCC & Cấu trúc Xác suất

**Quyết định cốt lõi:** Workload đọc hay ghi chủ đạo → B-Tree hay LSM · WAL + fsync policy (→2.4) · MVCC tuning (vacuum/compaction) cho engine tôi dùng · Cấu trúc phụ (bloom/skiplist/bitmap) ở đâu đáng tiền
**Con số neo:** B-Tree cao (tỷ key): `3–4 page` · Page chuẩn: `4–16 KB` · LSM write amp: `5–30× (tuỳ level/compaction)` · Bloom sai số: `~1% cấu hình được`
**Bệnh & chẩn đầu tiên:** Ghi khựng định kỳ (RocksDB/Kafka Streams) → `compaction stats; level score` ; DB phình dù row không tăng (PG) → `pg_stat_user_tables n_dead_tup` ; Đọc latency cao sau ghi lớn → `cache hit ratio; cfstats`

## Card 5.2 — RDBMS: PostgreSQL & MySQL

**Quyết định cốt lõi:** Isolation level cho từng đường giao dịch · Chiến lược index + EXPLAIN trong review · Connection pool (PgBouncer/Odin) + sizing · PG hay MySQL cho hệ mới
**Con số neo:** Pool gốc: `cores × 2–4` · Connection chi phí (PG): `~MB/process` · Autovacuum mặc định: `20% burst` · PG 19 GA: `19/11/2026`
**Bệnh & chẩn đầu tiên:** Replica lag tăng theo ghi → `lag metric; hot standby` ; Cảnh báo wraparound (PG) → `datfrozenxid age` ; Bảng phình dù ít row → `pg_stat_user_tables`

## Card 5.3 — Document & Embedded: MongoDB & SQLite

**Quyết định cốt lõi:** Document vs relational cho domain mới · Embedding vs referencing trong document · SQLite ở đâu trong kiến trúc (edge/embedded/cache-local) · Schema validation mức nào cho document
**Con số neo:** MongoDB: `9.0.4 (10/2026)` · SQLite: `3.54.1 (10/2026)` · Document max (Mongo): `16 MB` · SQLite đọc: `hàng trăm k rows/s`
**Bệnh & chẩn đầu tiên:** Document chạm 16 MB → `schema audit` ; Dữ liệu lệch giữa 2 collection → `audit update path` ; Ghi chậm dần → `mongotop/mongostat`

## Card 5.4 — In-Memory KV & Cache: Valkey & Redis

**Quyết định cốt lõi:** Chiến lược cache (cache-aside/write-through) + TTL + jitter · Single-flight/lock chống stampede · Redis hay Valkey (giấy phép + module) · Eviction policy + maxmemory
**Con số neo:** Redis / Valkey: `8.10.3 / 9.1.3 (10/2026)` · Latency lệnh (local): `~50–100 µs mạng LAN` · AOF everysec mất: `≤ ~1 s khi chết` · THP + fork: `stall ms–s`
**Bệnh & chẩn đầu tiên:** DB lag nổ đúng lúc key hết hạn → `hit ratio + DB metric theo thời gian` ; p99 Redis vọt định kỳ → `SLOWLOG; THP check` ; Một lệnh treo mọi lệnh → `--bigkeys; slowlog`

## Card 5.5 — Wide-Column: Cassandra & ScyllaDB

**Quyết định cốt lõi:** Partition key chống hot partition · Consistency level theo từng use case · Data model theo query (không theo bản thể) · Cassandra vs ScyllaDB (C++ rewrite)
**Con số neo:** Cassandra / ScyllaDB: `5.0.9 / 2026.3 (10/2026)` · Partition mục tiêu: `< 100 MB` · RF mặc định: `3` · Read/Write tuỳ level: `ONE ~ms; QUORUM chậm hơn`
**Bệnh & chẩn đầu tiên:** 1 node nóng, cluster lệch → `nodetool ring/tpstats` ; Read chậm sau xoá lớn → `sstableverify; audit TTL` ; Repair không xong đúng lịch → `nodetool repair history`

## Card 5.6 — Search Engine: Elasticsearch & OpenSearch

**Quyết định cốt lõi:** Lucene-based search hay Postgres FTS/pgvector cho bài toán tôi · Mapping + analyzer cho từng field (kể cả tiếng Việt) · Elasticsearch (giấy phép AGPL từ 8.16+/vendor) hay OpenSearch (Apache-2.0) · Chiến lược reindex + ILM (lifecycle)
**Con số neo:** Elasticsearch / OpenSearch: `9.5.5 (10/2026)` · Shard mục tiêu: `10–50 GB` · Shard max doc: `~2 tỷ (Lucene)` · Refresh mặc định: `1 s`
**Bệnh & chẩn đầu tiên:** Tìm từ đơn không ra → `_analyze` ; Search latency vọt lúc reindex → `throttle; off-peak` ; Cluster "vàng" node rớt → `_cat/shards; heap metric`

## Card 5.7 — Event Log, Stream & Queue: Kafka vs RabbitMQ vs NATS

**Quyết định cốt lõi:** Queue (RabbitMQ) hay log (Kafka) cho bài toán này · Partition & consumer group thiết kế · Delivery semantic: at-most/at-least/exactly-once · DLQ + retry policy + poison message xử lý
**Con số neo:** Kafka / RabbitMQ: `4.4.0 / 4.4.0 (10/2026)` · Latency: RabbitMQ vs Kafka: `ms vs ~ms–chục ms` · Throughput Kafka: `MB/s–GB/s cluster` · Partition & thứ tự: `trong partition`
**Bệnh & chẩn đầu tiên:** Consumer lag tăng đều → `lag trend; partition throughput` ; Cả group khựng định kỳ → `group metric; log member` ; Consumer chết lặp liên tục → `consumer log; DLQ chưa có?`

## Card 5.8 — OLAP & Columnar: ClickHouse & DuckDB

**Quyết định cốt lõi:** OLAP workload tách khỏi OLTP chưa — và chọn columnar nào · MergeTree/partition/order key thiết kế · Nhánh ClickHouse (LTS vs monthly) & DuckDB vai trò (embed/notebook) · Insert pattern (batch ≥ 1k rows)
**Con số neo:** ClickHouse: `26.10 monthly / 26.8 LTS` · DuckDB: `2.0.0 LTS (21/10/2026)` · Nén columnar: `~10× phổ biến` · Insert batch chuẩn: `≥ 1k rows / block`
**Bệnh & chẩn đầu tiên:** "Too many parts" → `system.parts; batch` ; Query chậm dù có "index" → `EXPLAIN reads` ; Đĩa đầy → `system.parts size`

## Card 5.9 — Object Storage & Open Lakehouse: S3 & Iceberg v3

**Quyết định cốt lõi:** Dữ liệu nào xuống object storage (cold/audit/ML corpus) · Table format cho lakehouse (Iceberg/Delta/Hudi) · Partition + sort order + compaction service · Lifecycle (tiering, expiry) + chi phí egress
**Con số neo:** Iceberg: `v3 (1.11.0+, 10/2026)` · Durability S3-class: `11×9` · Object max: `5 TB` · Nén parquet: `~10×`
**Bệnh & chẩn đầu tiên:** Query chậm dần theo tuần → `files count / partition` ; Hóa đơn S3 vọt → `bill theo trục` ; Iceberg commit xung đột → `writer hợp nhất / wap`

## Card 5.10 — Vector Databases & ANN Indexing

**Quyết định cốt lõi:** pgvector hay dedicated store (Qdrant/Milvus/Weaviate) · Index: HNSW / IVF-PQ / DiskANN (hoặc brute force!) · Chunking + embedding model + re-rank pipeline · Quantization (PQ/SQ/binary) + filter strategy
**Con số neo:** HNSW RAM: `N×D×4B×~1,5` · PQ nén: `8–32× RAM giảm` · Recall HNSW/PQ: `~98–99% / 90–95%` · pgvector hợp lệ: `< ~10M vector`
**Bệnh & chẩn đầu tiên:** RAM nổ khi build index → `quantization; DiskANN` ; Kết quả "sai tenant" → `filtered search` ; Recall thấp → `eval set; tuning`

## Card 5.11 — Graph & Time-series: Property Graph & TSDB

**Quyết định cốt lõi:** Cần graph engine chuyên dụng hay SQL đệ quy (CTE) đủ · Graph: Neo4j / Memgraph / property-graph chuẩn (SQL/PGQ 2024) · Time-series: TSDB chuyên dụng (Prometheus/VictoriaMetrics) hay ClickHouse · Cardinality budget cho metric labels
**Con số neo:** SQL/PGQ + GQL: `chuẩn ISO 2023/2024` · Traversal depth thực dụng (graph engine): `3–6 hop thoải mái` · Cardinality lành mạnh (một cụm vừa): `~vài triệu active series` · VictoriaMetrics / Prometheus: `chuẩn observability`
**Bệnh & chẩn đầu tiên:** Traversal chậm đột biến → `profile query; đếm edge` ; Prometheus OOM → `top10 metrics by series` ; Metric "biến mất" sau 2 tuần → `retention config`

## Card 5.12 — Stream Processing (Flink) & Batch Orchestration

**Quyết định cốt lõi:** Stream thật hay micro-batch đủ cho bài toán · Xử lý trễ/đến muộn (watermark + allowed lateness) · Exactly-once: checkpoint + transactional sink · Orchestration (Airflow/dagster) + SLA pipeline
**Con số neo:** Flink độ trễ end-to-end: `ms–s (true stream)` · Checkpoint interval chuẩn: `30s–5min` · Watermark bound: `theo nghiệp vụ (phút)` · Airflow/Dagster: `batch chuẩn ngành`
**Bệnh & chẩn đầu tiên:** Job Flink khựng định kỳ → `checkpoint duration metric` ; Kết quả "thiếu" sự kiện → `late events ratio; side output` ; State phình vô hạn → `state size graph`

## Card 5.13 — Quản trị Dữ liệu (DAMA cho kỹ sư)

**Quyết định cốt lõi:** Retention policy cho từng loại dữ liệu · Xoá thật (GDPR erasure) xuyên bao nhiêu lớp · Catalog + ownership: mỗi dataset có chủ · Phân loại dữ liệu (public/internal/confidential/PII)
**Con số neo:** GDPR erasure deadline: `30 ngày (pháp lý)` · Chi phí nóng vs lạnh: `~10× mỗi bậc` · Data map: `artifact bắt buộc` · Catalog MVP: `1 bảng + CI rule`
**Bệnh & chẩn đầu tiên:** Yêu cầu xoá không hoàn tất → `audit theo §2.3` ; Hóa đơn lưu trữ phình → `cost theo lớp` ; "Bảng này của ai?" im lặng → `catalog query`

## Card 5.14 — Kiến trúc Đa thuê bao ở Tầng Dữ liệu

**Quyết định cốt lõi:** Mô hình: silo / bridge (schema) / pool (share bảng + RLS) · Row-Level Security + tenant_id invariant · Noisy neighbor ở tầng dữ liệu (quota/limit) · Đường "tách tenant lớn" (escape hatch)
**Con số neo:** RLS overhead: `~vài % (đúng kiểu filter)` · Schema/cluster (bridge): `tới vài nghìn` · Pool hợp lệ: `10k+ tenant nhỏ` · Pool → silo migration: `giờ–ngày/tenant`
**Bệnh & chẩn đầu tiên:** Leak dữ liệu xuyên tenant → `audit role + path` ; Tenant nhỏ chậm định kỳ → `metric theo tenant` ; Bảng mới "quên" tenant → `policy diff CI`

## Card 5.15 — Ma trận Chọn Datastore, Outbox/CDC & 20 Bẫy

**Quyết định cốt lõi:** Họ datastore cho workload (đọc ma trận, không đọc trend) · Đồng bộ đa store: outbox + CDC hay dual-write · "Một loại cho tất cả" hay "đúng họ cho từng bài" · Exit plan (đổi datastore khi sai)
**Con số neo:** Số store trung bình hợp lý: `2–4/org` · CDC lag mục tiêu: `s–phút theo use case` · Outbox overhead: `1 insert/tx` · "Chỉ cần RDBMS+cache+log": `90% hệ mới`
**Bệnh & chẩn đầu tiên:** DB và search/cache lệch nhau → `reconciliation job; audit write path` ; "Sẽ scale" chưa từng tới → `review ma trận` ; Đổi model phải dừng dịch vụ → `export/import drill`

## Card 5.16 — Công thức Sizing Datastore

**Quyết định cốt lõi:** Dung lượng + IOPS + throughput mục tiêu 18 tháng · Headroom (đệm) từng lớp: bao nhiêu % là khoa học · Điểm "dừng mua, bắt đầu shard" · Chi phí cho 3 hình: đúng giờ, dư, thiếu
**Con số neo:** Working set/data: `~10–30%` · Peak mùa VN e-com: `3–10× ngày thường` · CPU mục tiêu / ceiling: `50–60% / 70%` · Disk ceiling: `~70%`
**Bệnh & chẩn đầu tiên:** Cache hit tụt dần → `hit trend + data growth` ; Sự cố đúng mùa cao điểm → `history peak` ; Failover chết dây chuyền → `capacity khi mất 1 node`

## Card 6.1 — 8 Ràng buộc Ngược của Tầng Client

**Quyết định cốt lõi:** Chấp nhận ràng buộc nào là chủ đạo cho sản phẩm của tôi · Độ giảm cấp (degradation) thiết kế cho từng điều kiện xấu · Chính sách update & version floor · Ngân sách tài nguyên client (pin, dữ liệu, bộ nhớ)
**Con số neo:** Frame budget: `16 ms (60 fps)` · Cảm giác phản hồi: `< 100 ms` · Radio wake (cellular): `tốn năng lượng gấp ~×wifi` · App store update lan: `tuần; web: reload`
**Bệnh & chẩn đầu tiên:** User phàn nàn "ngốn pin" → `battery historian / energy log` ; App "khóc" khi mạng yếu → `airplane-mode test` ; Lỗi chỉ trên máy cũ → `device-lab test p75`

## Card 6.2 — Bốn Môi trường Thực thi Client

**Quyết định cốt lõi:** Nền tảng mục tiêu: web / iOS / Android / desktop / embedded · Native hay cross-platform (React Native/Flutter/KMP/PWA) · Tầng dùng lại bao nhiêu (logic/UI) giữa các nền tảng · Version floor & chu kỳ nâng cấp toolchain
**Con số neo:** App Store review: `giờ–ngày` · Play targetSdk deadline: `hằng năm` · Electron RAM baseline: `~150–200 MB` · Tauri binary vs Electron: `~10× nhỏ hơn`
**Bệnh & chẩn đầu tiên:** Bug chỉ trên Safari → `test matrix web` ; Từ chối App Store luân phiên → `rejection log; policy checklist` ; App nặng RAM desktop → `đổi Tauri/system webview`

## Card 6.3 — Lưu trữ Cục bộ, Local-First & Đồng bộ Offline (CRDT/Sync)

**Quyết định cốt lõi:** Mức offline: cache-chỉ-đọc / offline-đọc / offline-đọc-viết (local-first) · Giải quyết xung đột: LWW / field-merge / OT / CRDT · Sync engine: tự viết hay dùng (ElectricSQL/RxDB/PowerSync/Yjs) · Ngữ nghĩa hiển thị: stale-while-offline, badge "chưa sync"
**Con số neo:** UI local read: `< 10 ms` · CRDT metadata overhead: `~1,5–3× payload (tệ nhất)` · Conflict hợp lý: `< 0,1–1% bản ghi` · Sync interval nền: `phút (mobile), tức thì khi active`
**Bệnh & chẩn đầu tiên:** "Bản ghi cũ đè mới" → `so timestamp 2 máy` ; Xoá rồi "sống lại" → `audit delete path` ; Metadata CRDT phình → `Automerge compact; snapshot`

## Card 6.4 — Giao tiếp Client, Push Notification & Năng lượng/Mạng

**Quyết định cốt lõi:** Kênh đẩy: APNs/FCM/WebPush — và độ tin cậy cần gì · Tần suất & hợp nhất (collapse/silent push) · Chiến lược nền: poll, long-poll, WebSocket, hay push · Phân loại tin nhắn theo ưu tiên & độ ồn
**Con số neo:** Push latency (đến thiết bị): `s–phút (best-effort)` · Silent push budget: `OS quyết định, giảm nếu ít dùng` · Collapse key: `thay thế thông báo cùng key` · Cellular wake cost: `tốn hơn wifi rõ rệt`
**Bệnh & chẩn đầu tiên:** Push trễ phút–giờ → `delivery log theo chặng` ; Silent push ngừng hoạt động → `iOS metric; cần fallback` ; Người dùng "bom" thông báo → `audit tần suất/người dùng`

## Card 6.5 — Edge Compute & Kiến trúc CDN

**Quyết định cốt lõi:** Cái gì cache ở đâu: browser / CDN / edge / origin · Chiến lược vô hiệu hoá: TTL / surrogate key / purge API · Edge compute: dùng cho việc gì (định tuyến, auth, biến đổi) — và KHÔNG dùng cho việc gì · Ai là origin thật khi có nhiều tầng CDN
**Con số neo:** RTT đến PoP CDN: `~1–30 ms (vs 100–300 ms origin xa)` · TTL asset hash: `1 năm, immutable` · Hit ratio asset: `> 90%` · Purge lan truyền: `s–phút (theo provider)`
**Bệnh & chẩn đầu tiên:** "Dữ liệu cũ" sau khi sửa → `curl -sI từng chặng` ; User thấy nội dung của user khác → `audit khoá cache` ; Origin bị dồn lúc hot key hết hạn → `stale-while-revalidate; lock`

## Card 6.6 — Hệ thống Nhúng & IoT

**Quyết định cốt lõi:** Nền tảng nhúng: MCU (vi điều khiển) hay SBC/edge Linux · Giao thức: MQTT / CoAP / HTTP / Matter / LoRaWAN · Fleet provisioning & danh tính thiết bị · OTA update: kênh nào, rollback thế nào
**Con số neo:** MCU ngủ sâu: `µA–mA` · MQTT header: `~2 byte fixed + nhỏ` · LoRaWAN payload: `~chục byte/tin` · Thread mesh hop: `chục mét/hop`
**Bệnh & chẩn đầu tiên:** Fleet "ngơ" sau deploy OTA → `A/B rollback; canary fleet` ; Thiết bị rớt rồi lên liên tục → `keepalive tune; LWT` ; Broker quá tải → `QoS-1; sharding topic`

## Card 6.7 — Bảo mật Phía Client & Attestation

**Quyết định cốt lõi:** Client giữ gì (không bao giờ giữ gì) · Lưu trữ an toàn: keychain/Keystore/IndexedDB · Mức attest cần: không / Play Integrity / App Attest / web trust signals · Chống lạm dụng nghiệp vụ ở server (không ở client)
**Con số neo:** TTL access token: `phút–giờ` · Attest verdict cache: `giờ` · Passkey (FIDO2/WebAuthn): `chuẩn phủ iOS/Android/browser` · OAuth2.1 + PKCE: `khuyến nghị mặc định cho public client`
**Bệnh & chẩn đầu tiên:** Token bị đọc trộm (web) → `CSP + HttpOnly refresh (→7.7)` ; API bị gọi bởi tool tự viết → `server-side verify + attest` ; Lộ secret trong bundle/app → `quét secret trước release`

## Card 7.1 — Kiến trúc Rendering & Routing (CSR/SSR/ISR/RSC)

**Quyết định cốt lõi:** Chiến lược render theo route: CSR/SSR/SSG/ISR/hybrid · Framework & meta-framework (Next/Nuxt/SvelteKit/Astro) · Routing & data loading ownership (loader/file-based) · Cạnh render ở đâu: build / origin / edge (→6.5)
**Con số neo:** TTFB SSG (CDN): `~10–50 ms` · TTFB SSR origin chậm: `100–500 ms+` · LCP "tốt": `< 2,5 s (p75)` · Hydration cost: `tỉ lệ bundle JS`
**Bệnh & chẩn đầu tiên:** LCP xấu (trắng lâu) → `vitals theo route; waterfall trace` ; SEO kém trang tương tác → `SSG/ISR cho route công khai` ; TTFB SSR cao → `SSR edge; cache partial`

## Card 7.2 — Phân loại Trạng thái & Kiến trúc Data Fetching

**Quyết định cốt lõi:** Phân loại state: server-cache / URL / UI / form / module · Ai là nguồn chân lý cho từng loại · Chiến lược fetch: loader/route, query cache (TanStack/SWR), RSC fetch · Cache & làm mới: staleTime, invalidation, optimistic update
**Con số neo:** staleTime hợp lý: `theo nghiệp vụ (s–phút)` · dedupe window: `~vài s (query cache)` · Zustand vs Redux bundle: `~1 KB vs ~10+ KB` · zod schema dùng 2 nơi: `client + server`
**Bệnh & chẩn đầu tiên:** Lưu xong UI không đổi → `audit mutation→invalidation` ; Refresh mất filter → `chuyển sang search params` ; Request dồn trùng → `query cache keys + stale`

## Card 7.3 — Build Tooling, Bundling & Performance Budget (INP)

**Quyết định cốt lõi:** Performance budget: JS/cơ cấu bundle + INP/LCP target · Bundler & toolchain: Vite/esbuild/Rspack/turbopack · Chiến lược code-split & lazy theo route/tương tác · CI đo vitals & bundle-diff (nếu vượt ngân sách thì fail)
**Con số neo:** JS initial budget: `150–200 KB gzip` · INP "tốt": `< 200 ms (p75)` · LCP "tốt": `< 2,5 s (p75)` · Long task: `> 50 ms chặn`
**Bệnh & chẩn đầu tiên:** JS phình mỗi release → `bundle-diff fail` ; INP xấu khi gõ tìm kiếm → `debounce + worker + trace` ; Trang "nhảy" khi tải → `width/height; preload`

## Card 7.4 — Component API & Design System như Hợp đồng

**Quyết định cốt lõi:** Xây design system riêng hay dùng (Radix/shadcn/MUI...) · Nguyên thủy hợp đồng: tokens → components → patterns · Quy tắc breaking change & versioning cho UI · Ranh giới component: props in/props out, composition
**Con số neo:** Tokens điển hình: `50–150 biến` · Radix/Base UI primitives: `~30–50 headless` · Codemod chi phí: `giờ thay vì quý` · Độ phủ mục tiêu: `≥ 80% màn`
**Bệnh & chẩn đầu tiên:** 47 sắc màu xanh → `audit màu; CSS vars` ; Đổi 1 button sửa 30 chỗ → `gộp; đếm bản sao` ; Form "kỳ kỳ" → `rà value/onChange`

## Card 7.5 — Accessibility (WCAG 2.2/EAA) & i18n/l10n

**Quyết định cốt lõi:** Mức tuân thủ: WCAG 2.2 A / AA / AAA; phạm vi nào · Kiểm thử a11y tự động hoá ở đâu trong pipeline · Ngôn ngữ: bao nhiêu locale, RTL có cần không · Định dạng i18n: ICU MessageFormat, plural/gender/date
**Con số neo:** Tương phản AA: `4,5:1 (text thường)` · Target size: `≥ 24×24 px` · Tự động bắt được: `~30–50% lỗi a11y` · Chuỗi dài (tiếng Đức): `co giãn 2–3×`
**Bệnh & chẩn đầu tiên:** Modal "không đóng được" bằng bàn phím → `tab/esc test mỗi modal` ; Screen reader đọc "button, button" → `NVDA/VoiceOver pass` ; Chuỗi dịch vỡ layout → `audit key`

## Card 7.6 — Kiểm thử & Quan sát Frontend (RUM)

**Quyết định cốt lõi:** Kim tự tháp test FE: unit/component/visual/E2E phân bổ ra sao · RUM: đo gì (vitals, error, hành trình) và lấy mẫu thế nào · Error tracking + source map + release health · Playwright/E2E chạy ở đâu, chặn release hay chỉ báo cáo
**Con số neo:** Thời gian E2E hợp lý: `< 10–15 phút toàn bộ` · Beacon vitals: `~1 KB/lần gửi` · Lấy mẫu replay: `1–5% thường, 100% lỗi` · Crash-free session mục tiêu: `> 99,5%`
**Bệnh & chẩn đầu tiên:** CI đỏ bị ignore → `flake rate per test; cách ly` ; E2E 40 phút → `dồn xuống unit/component` ; Người dùng thấy trắng, dashboard yên → `Sentry + sourcemap + release tag`

## Card 7.7 — Bảo mật Frontend & Mô hình An ninh Trình duyệt

**Quyết định cốt lõi:** Chính sách CSP: strict nonce/hash, report-only trước · Trusted Types + framework escaping · Danh tính & phiên ở FE: cookie HttpOnly vs token storage · Phòng thủ dependency (SBOM, lockfile, audit)
**Con số neo:** CSP report-only giai đoạn: `1–2 tuần trước enforce` · Trusted Types hỗ trợ: `Chrome/Edge nhóm đầu; FF/Safari đang tới` · Access token TTL: `phút–giờ` · các sự cố supply chain npm: `nhiều sự cố lớn công khai 2018–2026`
**Bệnh & chẩn đầu tiên:** Script chèn chạy được → `audit header; report-only` ; Token bị đánh cắp → `chuyển HttpOnly/BFF` ; Form bị gửi từ site khác → `kiểm cookie attrs`

## Card 8.1 — Thời gian, Thứ tự & Định lý Bất khả thi (FLP, CAP, PACELC)

**Quyết định cốt lõi:** Dùng thời gian nào: vật lý (NTP/PTP) hay logic (Lamport/vector/HLC) · Khi mất liên lạc (partition): chọn C hay A — theo nghiệp vụ nào · Độ trễ sẵn sàng trả thường ngày (không partition) · Ngưỡng coi "mất liên lạc" (timeout) đo thế nào
**Con số neo:** NTP sai số: `ms LAN; chục ms+ WAN tệ` · PTP: `sub-ms với HW support` · Lamport/vector overhead: `vài byte–chục byte/sự kiện` · Election timeout (Raft khuyến nghị): `RTT chéo node × ~10`
**Bệnh & chẩn đầu tiên:** Log hai máy không sắp theo thứ tự (I-048) → `so sánh `date -u` + chrony tracking` ; Leader bầu liên tục (flap) → `đo RTT chéo node; tăng timeout` ; Update "mất" ngẫu nhiên → `audit nguồn timestamp`

## Card 8.2 — Đồng thuận (Raft/Paxos), Leases & Fencing Tokens

**Quyết định cốt lõi:** Có thật sự cần đồng thuận không · Nếu cần: dùng hệ đồng thuận chạy sẵn (etcd/ZooKeeper/Consul) hay tự nhúng (Raft library) · Lock phân tán dùng cho **hiệu năng** hay cho **tính đúng đắn** · Fencing token có hay không (và ai kiểm tra nó)
**Con số neo:** Quorum: `đa số (N=3 chịu 1; N=5 chịu 2)` · Election timeout: `~10× RTT chéo node` · etcd write throughput: `~vài nghìn ops/s (khối nhỏ)` · Kafka KRaft: `thay ZooKeeper hoàn tất (3.x–4.x)`
**Bệnh & chẩn đầu tiên:** Leader flap liên tục (I-054) → `ping chéo node; tăng timeout` ; Dữ liệu bị ghi đè "bởi ma" (I-055) → `GC log + audit token` ; Hai primary cùng nhận ghi (I-053) → `kiểm tra storage có verify token`

## Card 8.3 — Giao dịch Phân tán, Saga, Outbox & "Exactly-Once"

**Quyết định cốt lõi:** Giao dịch xuyên service: 2PC / Saga / Outbox / tránh hẳn · Nếu Saga: choreography hay orchestration · Isolation của Saga (bức màn giữa các bước) · "Exactly-once" tôi hứa với ai, thật ra là gì
**Con số neo:** Outbox lag: `ms–s (poller) / sub-s (CDC)` · XA penalty: `chậm rõ rệt so với tx thường` · Saga step hợp lý: `2–6 bước` · Kafka EOS: `transactional producer (→5.7)`
**Bệnh & chẩn đầu tiên:** Đơn có, downstream không biết → `cài outbox` ; Sự kiện trùng gây đôi kê → `audit id dedupe` ; Saga "kẹt giữa" vĩnh viễn → `state machine audit`

## Card 8.4 — Phân vùng & Nhân bản ở Tầng Hệ thống

**Quyết định cốt lõi:** Phân vùng theo: range / hash / directory; khoá gì · Reshard khi nào và đường nào (online hay cửa sổ bảo trì) · Replication factor & chế độ (sync/semi/async) · Đọc từ đâu: leader / closest replica / quorum (R+W>N?)
**Con số neo:** Consistent hashing di chuyển: `~1/N dữ liệu khi ±1 node` · RF phổ biến: `3 (2 vùng, 1 vùng chéo)` · W+R>N (N=3): `ví dụ W=2, R=2` · Semi-sync ack: `≥1 follower`
**Bệnh & chẩn đầu tiên:** Một node nóng khác hẳn → `đếm top keys theo node` ; Truy vấn chậm vã lai → `trace số phân vùng đụng` ; "Ghi xong đọc không thấy" → `đọc leader hoặc sticky`

## Card 8.5 — Mẫu Chịu lỗi & Kiểm soát Tải Toàn trình

**Quyết định cốt lõi:** Chính sách retry: ai được retry, mấy lần, backoff thế nào · Circuit breaker & bulkhead cho dependency nào · Load shedding: bỏ gì trước khi sập · Timeout từng tầng, tổng ngân sách
**Con số neo:** Retry budget: `≤ ~10% traffic` · Backoff: `full jitter, cap 1–10 s` · Breaker OPEN: `≥ vài chục giây` · Shed chuẩn: `503 + Retry-After, ở edge rẻ nhất`
**Bệnh & chẩn đầu tiên:** Retry storm nhân lên (I-050) → `audit chính sách retry từng client` ; Sập dây chuyền (I-051) → `trace tìm lan truyền tài nguyên` ; Đỉnh tải đồng bộ (I-052) → `jitter hoá + lệch lịch`

## Card 8.6 — Kiến trúc Phần mềm: Monolith, Microservices, DDD, CQRS, Event Sourcing

**Quyết định cốt lõi:** Monolith hay microservices — bây giờ và lộ trình · Ranh giới service vẽ theo gì (DDD bounded context?) · CQRS có đáng không, cho Context nào · Event Sourcing: thật sự cần event là nguồn chân lý?
**Con số neo:** Gọi nội bộ: hàm vs mạng: `ns–µs vs ms (nghìn×)` · Ngưỡng "đáng tách" scale: `~10× khác biệt` · Team/service hợp lý: `1 team sở hữu ≥ 2–5 service` · Event schema sống: `năm (version hoá bắt buộc)`
**Bệnh & chẩn đầu tiên:** Distributed monolith → `vẽ bounded context lại` ; Gọi chéo 10 hops/request → `trace đếm hops (→11.1)` ; "Vừa lưu không thấy" → `projection lag + UI state`

## Card 8.7 — Đa vùng, Cell-Based Architecture & DR

**Quyết định cốt lõi:** Multi-region: active-passive / active-active / theo vùng người dùng · Conflict resolution khi active-active · Kích thước & cấu trúc cell (blast radius) · DR: kịch bản nào được drill, tần suất
**Con số neo:** DNS TTL cho failover: `30–60 s khi cần nhanh` · Replication chéo vùng latency: `50–200 ms một chiều (theo cặp vùng)` · RPO async chéo vùng: `~giây–chục giây` · Drill DR tần suất: `quý–nửa năm`
**Bệnh & chẩn đầu tiên:** Failover kéo dài quá RTO → `đo từng chặng failover` ; Standby lên rồi sập tiếp → `tải thử standby` ; Sau split vùng, dữ liệu đụng nhau → `range ID mỗi vùng`

## Card 8.8 — Tiến hoá Không gián đoạn (Expand-Contract, Strangler, Flags)

**Quyết định cốt lõi:** Migration schema: expand-contract (online) hay cửa sổ bảo trì · Di dời hệ thống: big-bang, song song chạy, hay strangler dần · Feature flag: bộ nào, thời gian sống, ai dọn · Rollback của chính cuộc di dời
**Con số neo:** Backfill batch: `1–10k rows, ngủ giữa lô` · Index online: `CONCURRENTLY-style, không khoá ghi` · Flag TTL: `≤ 1–2 sprint` · Strangler mốc: `"tắt cũ" có ngày công khai`
**Bệnh & chẩn đầu tiên:** DB lag/timeout trong migration → `batch + đo lag` ; Đọc thấy dữ liệu "nửa nạc nửa mỡ" → `mỗi request một nguồn` ; Hệ mới khác kết quả hệ cũ → `parallel-run diff`

## Card 9.1 — Kubernetes Internals (v1.35–1.37)

**Quyết định cốt lõi:** requests vs limits: chính sách cho CPU/mem theo lớp workload · PDB & graceful drain · Topology spread/anti-affinity: trải theo AZ/node như nào · Ai được scheduling "đắt" (GPU, node riêng, taint)
**Con số neo:** K8s bản mới: `1.37 (1.37.2 patch 30/10)` · CFS chu kỳ: `100 ms` · terminationGrace: `30 s mặc định; batch có thể 10 m+` · PDB chuẩn: `≥3 replica, maxUnavailable 1`
**Bệnh & chẩn đầu tiên:** Pod Pending mãi (I-057) → ``describe` đọc events` ; Latency vã lai khắp app → `metric throttled seconds` ; Restart loop → `thêm startupProbe`

## Card 9.2 — Autoscaling (HPA/VPA/KEDA/Karpenter) & Lập lịch GPU

**Quyết định cốt lõi:** Chiều scale chính: pod (HPA) hay node (Karpenter/CA) · Metric scale: CPU/mem, RPS, latency, queue depth · Scale-to-zero & queue-driven (KEDA) cho workload nào · GPU: pool riêng? MIG/time-slicing? queue (Kueue/Volcano)?
**Con số neo:** HPA phản ứng: `~15–60 s (metric + định kỳ)` · Karpenter tạo node: `~30–60 s` · Scale-to-zero wake: `giây–chục giây` · GPU so CPU giá: `~×10–30 mỗi đơn vị tính toán`
**Bệnh & chẩn đầu tiên:** Scale cưa qua lại (I-059) → `đổi metric + behavior` ; Tăng tải nhưng không scale → `audit pipeline metric` ; Pod scale, node không → `Karpenter log/quota`

## Card 9.3 — Mạng Đám mây: VPC, NAT, PrivateLink, DNS

**Quyết định cốt lõi:** Thiết kế CIDR VPC (và dư chỗ cho peering/region mới) · Ra internet thế nào: NAT GW / public subnet / không ra · DNS: resolution nội bộ, split-horizon, ndots · Vào/ra giữa VPC: peering / transit gateway / endpoint
**Con số neo:** Cổng SNAT / IP / đích: `~64k` · ndots:5 nhân truy vấn: `×4–6 mỗi tên ngắn` · NAT GW giá: `theo GB + giờ` · PrivateLink: `phí giờ nhỏ, không GB`
**Bệnh & chẩn đầu tiên:** Connection lỗi vã lai ra ngoài (I-060) → `metric NAT SNAT port; connection pool` ; DNS chậm/timeout lúc cao điểm (I-061) → `NodeLocal + FQDN chấm cuối` ; Hóa đơn NAT tăng vọt → `endpoint cho S3; route table audit`

## Card 9.4 — Cân bằng Tải, Gateway API & Cilium eBPF Mesh

**Quyết định cốt lõi:** LB lớp nào ở đâu: L4 cloud / L7 gateway / service mesh · Ingress→Gateway API (hay còn chờ)? · Mesh: sidecar / ambient / không mesh (Cilium thay kube-proxy) · Health check & draining đúng nghĩa
**Con số neo:** Gateway API: `GA v1, triển khai rộng` · Istio ambient: `GA (từ 1.24, 2024)` · Sidecar overhead: `~50–100 MB RAM/pod` · Cilium: `kube-proxy replacement ổn định`
**Bệnh & chẩn đầu tiên:** 502 vã lai → `synthetic xuyên deploy` ; Deploy rơi request → `audit lifecycle (→9.1)` ; Policy "không ăn" → `kiểm tra CNI + policy audit`

## Card 9.5 — Serverless, FaaS & Mô hình Compute

**Quyết định cốt lõi:** Compute nào cho workload này: VM / container / FaaS / edge · Cold start chấp nhận được bao nhiêu · Scale & giới hạn nền tảng (concurrent, thời gian chạy) · Hoà vốn: giá per-invocation vs luôn-chạy
**Con số neo:** Cold start container FaaS: `~100–300 ms` · V8 isolate (edge): `~ms` · Lambda-style runtime cap: `15 phút` · Concurrent cap mặc định: `~1.000/account (nâng được)`
**Bệnh & chẩn đầu tiên:** Đỉnh tải mất request im lặng → `metric throttle; quota tăng` ; p99 vã lai (lúc nhanh lúc chậm) → `synthetic đo; giữ ấm` ; Đỉnh tải sập cả account → `tách account/region hàm quan trọng`

## Card 9.6 — IaC, GitOps & Internal Developer Platform

**Quyết định cốt lõi:** Công cụ IaC: Terraform/OpenTofu/Pulumi/Crossplane — state ai giữ · Kiểu IaC: mutable (apply chèo) hayGitOps pull (reconcile liên tục) · Phạm vi tự động hoá: chỉ prod, hay cả DNS/quota/team perm · IDP: có cần, và "golden path" đầu tiên là gì
**Con số neo:** Terraform/OpenTofu: `song song cộng đồng (sau licence 2023)` · Argo CD / Flux: `chuẩn GitOps CNCF` · Drift scan chu kỳ: `giờ–ngày` · Time-to-first-deploy IDP: `mục tiêu < 1 ngày`
**Bệnh & chẩn đầu tiên:** State lock/conflict → `remote lock + plan trong CI` ; Tài nguyên "mồ côi" (tiền chảy) → `audit cloud vs state định kỳ` ; Drift tái phát sau reconcile → `tìm nguồn (console/lambda)`

## Card 9.7 — Build Systems & Progressive Delivery

**Quyết định cốt lõi:** Cấu trúc repo & build: monorepo/polyrepo, remote cache, hermetic · Chiến lược nhánh & gate: trunk-based + CI chặt · Progressive delivery: canary % theo SLO, auto-rollback · Artifact & supply chain: một artifact dọn dẹp mọi môi trường
**Con số neo:** CI gate p95: `< 10–15 phút` · Remote cache hit: `> 80–90% (repo lớn)` · Canary bậc chuẩn: `1→5→25→100%` · Cửa sổ metric auto-rollback: `1–5 phút`
**Bệnh & chẩn đầu tiên:** "Merge thứ Sáu" (người merge cuối đi về) → `progressive §2.3` ; CI 40 phút, ai cũng merge chờ → `remote cache + test song song` ; Deploy hỏng tới 100% user → `bật canary bậc`

## Card 10.1 — Mô hình Đe doạ & Zero Trust

**Quyết định cốt lõi:** Phạm vi threat model: STRIDE/LINDDUN, ranh giới tin cậy nào · Giả định xấu nhất tôi thiết kế chống lại là gì (insider? APT? bug?) · Mô hình tin cậy: vành đai (perimeter) hay zero trust · Tài sản gì cần bảo vệ, ưu tiên theo thiệt hại
**Con số neo:** STRIDE: `6 lớp đe doạ` · NIST 800-207: `chuẩn zero trust` · Tỉ lệ sự cố từ nhân viên nội bộ: `~tỷ trọng đáng kể các báo cáo ngành` · Threat model session: `2–4 h cho một hệ vừa`
**Bệnh & chẩn đầu tiên:** "Không biết bắt đầu từ đâu" → `phiên threat model 2–4 h` ; Một lệch cấu hình = lộ toàn bộ → `cell/segment audit (→8.7)` ; Nội bộ gọi nội bộ không kiểm tra → `zero-trust debt metric`

## Card 10.2 — Mật mã Thực hành, KMS & PQC (FIPS 203/204/205)

**Quyết định cốt lõi:** Ai giữ khoá: cloud KMS / self-managed HSM / client-side · Chiến lược khoá: envelope (DEK/KEK), rotation, vùng · Thuật toán chuẩn nào dùng (TLS, at-rest, hash, KDF) · PQC lộ trình: hybrid khi nào, dữ liệu nào "lưu dài nhạy cảm"
**Con số neo:** FIPS 203/204/205: `chuẩn hoá 8/2024` · Hybrid TLS: `X25519MLKEM768 triển khai rộng` · KEK rotation: `90 ngày–1 năm` · Argon2id tham số: `memory-hard ≥ 64 MB, t≥1`
**Bệnh & chẩn đầu tiên:** Khoá lộ qua log/commit (I-063) → `→10.6 vault + scanner` ; Không giải được dữ liệu sau DR → `KMS DR plan (→8.7)` ; Hóa đơn KMS cao bất ngờ → `DEK tại chỗ + envelope`

## Card 10.3 — AuthN & AuthZ: OAuth 2.1, Passkeys, RBAC/ABAC/ReBAC

**Quyết định cốt lõi:** AuthN flow: OAuth 2.1 + PKCE, passkeys, device flow, mTLS · Session vs JWT (server-side session? thu hồi được?) · Mô hình phân quyền: RBAC / ABAC / ReBAC · Đơn giản hoá danh tính (SSO, scim, jit)
**Con số neo:** OAuth 2.1: `draft ổn định, best-practice gộp` · Passkey: `hỗ trợ nền tảng lớn đầy đủ` · Access token TTL: `phút–giờ` · MTTR thu hồi token: `mục tiêu < 5 phút`
**Bệnh & chẩn đầu tiên:** Token lộ không tắt được (I-064) → `refresh reference + logout thật` ; Đọc được order của người khác → `audit query ownership` ; "Tại sao tôi không có quyền?" → `decision point một chỗ + engine giải thích`

## Card 10.4 — An ninh Ứng dụng & API: OWASP Top 10:2025

**Quyết định cốt lõi:** OWASP 10 hạng mục — tôi dọn theo thứ tự rủi ro nào · Validate input ở đâu (schema/edge/service/DB) · Webhook/callback ra vào kiểm soát thế nào (SSRF) · Báo lỗi & logging: fail-closed, không lộ stack
**Con số neo:** OWASP Top 10: `ấn bản 2025 (11/2025)` · A01 tỷ lệ app: `~3,7% có CWE nhóm A01` · Metadata IP cloud: `169.254.169.254` · ASVS: `checklist bảo mật theo cấp`
**Bệnh & chẩn đầu tiên:** Webhook quét nội mạng (I-065) → `egress allowlist + resolve-then-check` ; Cloud credential bị lấy qua SSRF → `chặn 169.254.169.254 + IMDSv2` ; Sửa `?id=` thấy data người khác → `ownership query + test`

## Card 10.5 — An ninh Chuỗi cung ứng: SLSA, Sigstore, SBOM

**Quyết định cốt lõi:** Mức SLSA mục tiêu cho artifact quan trọng (L1–L3) · SBOM: format (CycloneDX/SPDX), sinh ở đâu, lưu bao lâu · Ưu tiên vá theo gì: CVSS / EPSS / KEV · Nguồn phụ thuộc: pin như thế nào, tin ai
**Con số neo:** CycloneDX / SPDX: `chuẩn SBOM (ISO/Chuẩn hoá)` · SLSA v1.0: `khung mức build` · Sigstore/cosign: `ký keyless OIDC` · EPSS: `cập nhật hàng ngày`
**Bệnh & chẩn đầu tiên:** Không biết có package X không → `sinh SBOM transitive ở build` ; CI token bị ăn qua post-install → `isolate runner + không quyền thừa` ; Dependency confusion → `registry nội bộ + scope name`

## Card 10.6 — Quản lý Bí mật & Danh tính Workload

**Quyết định cốt lõi:** Secrets động (Vault-style sinh theo nhu cầu) hay tĩnh (config/ENV) · Workload identity: service "chứng minh mình là mình" bằng gì · Phân phối: ai được đọc secret nào (policy theo workload) · Phòng chống lộ: scan, audit, rotation
**Con số neo:** DB credential động TTL: `30 phút–1 giờ` · Cloud STS token: `15 phút–1 giờ` · K8s projected SA token: `TTL ngắn, audience-bound` · Rotation tĩnh: `≤ 90 ngày (nếu còn tồn tại)`
**Bệnh & chẩn đầu tiên:** Secret lộ qua log/commit (I-063) → `pre-commit + CI scan + xoay ngay` ; Không biết service nào dùng key nào → `một workload một bộ + audit` ; Xoay key = dự án 6 tháng → `dynamic vault + config trung tâm`

## Card 10.7 — Phát hiện & Phản ứng Sự cố An ninh

**Quyết định cốt lõi:** Detection engineering: rule nào, log nào, ngưỡng nào · Phản ứng: ai làm gì trong 60 phút đầu (playbook) · Chứa đứng hay xoá sạch (contain vs eradication) · Báo cáo/luật: ai phải biết trong bao lâu (72h?)
**Con số neo:** GDPR 72h: `thông báo cơ quan` · PDPD (NĐ 13/2023): `24h một số trường hợp` · MTTD/MTR mục tiêu: `giờ / giờ–ngày` · Alert ngưỡng mệt: `~10/ngày không action`
**Bệnh & chẩn đầu tiên:** Phát hiện sự cố từ... khách hàng → `đi ngược §2.1 từng nguồn` ; Alert bắn 100 cái/ngày, ai cũng ignore → `precision đo + rule nghỉ hưu` ; Kẹt "backup nào sạch?" → `log toàn vẹn + intel`

## Card 10.8 — Tuân thủ Pháp lý (CRA/NIS2/DORA/GDPR/PDPD) & Bản quyền OSS

**Quyết định cốt lõi:** Luật nào áp cho sản phẩm tôi (thị trường nào, vai gì) · Nhãn nghĩa vụ theo vai: nhà sản xuất/nhà nhập khẩu/nhà vận hành · Dữ liệu cá nhân: cơ sở pháp lý, danh mục, thời hạn, xuyên biên giới · Chính sách license OSS: dùng gì được, CONTRIBUTE thế nào
**Con số neo:** GDPR báo vi phạm: `72h` · NIS2: `chuyển hoá ~10/2024; báo 24h/72h` · DORA: `áp dụng 17/01/2025` · CRA: `hiệu lực 12/2024; nghĩa vụ chính 12/2027`
**Bệnh & chẩn đầu tiên:** "Không biết luật nào áp" → `workshop 2h với luật sư + bảng` ; Audit = 3 tháng dở chứng → `log/drift/SBOM → export` ; Phải từ chối yêu cầu xoá dữ liệu → `crypto-shred + API (→5.13)`

## Card 11.1 — SLI, SLO, SLA & Error Budget

**Quyết định cốt lõi:** Chọn SLI: tín hiệu nào phản ánh **nỗi đau người dùng** · Đặt SLO: bao nhiêu 9, cho SLI nào · Chính sách tiêu error budget: ngừng release khi nào · Cảnh báo theo burn rate (multi-window) thay ngưỡng tĩnh
**Con số neo:** 99,9%: `43,8 phút/30 ngày` · Multi-window: `14,4× (1 h+5 m); 1× (3 d+6 h)` · SLO per journey: `2–5 bộ cho một sản phẩm` · SLA < SLO: `chênh 0,2–0,5%`
**Bệnh & chẩn đầu tiên:** "SLO có mà chẳng ai nhìn" → `3 câu kiểm §2.2` ; Alert 2h sáng là nhiễu → `multi-window burn` ; Budget cháy nhưng vẫn ship như thường → `viết + ký + drill`

## Card 11.2 — OpenTelemetry & 4 Tín hiệu

**Quyết định cốt lõi:** Bốn tín hiệu (trace/metric/log/profile) — cái nào trước, cái nào trả tiền · Sampling trace: head vs tail, tỉ lệ · Cardinality: cái gì được làm label · Vận hành: tự chạy collector/backend hay managed
**Con số neo:** OTel trace/metric/log: `stable; profiling đang chuẩn hoá` · Tail sampling chuẩn: `100% lỗi + 100% p99-chậm + 1–10% thường` · Cardinality an toàn: `< ~vài chục chuỗi/metric thường` · Overhead telemetry: `vài % CPU (SDK+collector)`
**Bệnh & chẩn đầu tiên:** Trace đứt giữa các service → `propagate header chuẩn` ; Lỗi xảy ra mà không có trace → `tail sampling giữ lỗi` ; Prometheus OOM → `audit label + budget`

## Card 11.3 — Đo lường, Capacity Planning & Chaos Engineering

**Quyết định cốt lõi:** Mô hình capacity: Little + USL dự báo theo tải nào · Headroom mục tiêu (bao nhiêu % dư) · Chaos: thử cái gì, tần suất nào, ở đâu · Đo giới hạn thật (load test định kỳ)
**Con số neo:** Headroom: `20–50%` · Load test định kỳ: `quý` · Soak test: `6–24 h` · USL α, β: `fit từ đo`
**Bệnh & chẩn đầu tiên:** Thêm máy mà không nhanh hơn → `fit USL; tách state` ; Đỉnh giờ cao điểm chết nối tiếp → `headroom + kế hoạch` ; Chậm sau 12 h chạy → `soak test`

## Card 11.4 — Chỉ huy Sự cố & Postmortem

**Quyết định cốt lõi:** Vai trò khi sự cố: IC / Ops / Comms / Scribe · Mitigate trước hay điều tra trước · Sev level & đường kích hoạt (ai được đánh thức) · Postmortem: blameless, action item theo dõi thế nào
**Con số neo:** Cập nhật comms: `30–60 phút/lần khi Sev` · Postmortemdeadline: `5 ngày làm việc sau sự cố` · Action item có chủ+hạn: `100%` · MTTD/MTTR: `metric trụ của 11.4`
**Bệnh & chẩn đầu tiên:** Sự cố kéo dài vì 20 người "cùng cứu" → `cài vai + đào tạo` ; Mitigate chậm vì tranh luận nguyên nhân → `mitigate-first + drill` ; Postmortem thành tổ họp đổ lỗi → `template blameless + lãnh đạo mở đầu`

## Card 11.5 — Kinh tế học Kỹ thuật & FinOps

**Quyết định cốt lõi:** Unit economics: chi phí / 1k request / tenant / triệu token · Phân bổ chi phí (showback/chargeback) theo team/feature · Chiến dịch tiết kiệm: mua trước (RI/SP) vs spot vs tắt · Cân bằng tối ưu chi phí ↔ rủi ro ↔ tốc độ
**Con số neo:** Egress vs ingress: `chênh rõ bậc` · Cam kết giảm giá: `30–70%` · Spot giảm: `60–90%` · Idle điển hình (không quản): `20–40% chi phí (I)`
**Bệnh & chẩn đầu tiên:** Hóa đơn "to mà không biết của ai" → `policy tag IaC + báo vô chủ` ; Trả list price ~100% → `sau tối ưu, mua SP/RI` ; Egress phình → `CDN/PrivateLink/locality`

## Card 11.6 — Kiến trúc Tổ chức: Conway, Team Topologies, ADR/RFC, Tech Debt

**Quyết định cốt lõi:** Team topology: stream-aligned / platform / enabling / complicated-subsystem · Quy trình quyết định kiến trúc: ADR/RFC nhẹ hay ủy ban · Quản trị tech debt: danh sách, lãi, trả theo lịch · Sunset/khai tử hệ thống: tiêu chuẩn và can đảm
**Con số neo:** Conway: `quan sát 1967` · Team Topologies: `sách 2020, phổ biến hoá khung` · ADR ~1 trang: `template chuẩn mở` · Ngân sách trả nợ: `10–20% capacity`
**Bệnh & chẩn đầu tiên:** Microservice theo layer → `inverse Conway` ; Platform thành helpdesk → `golden path (→9.6)` ; "Vì sao thế này?" không ai biết → `ADR + review quá khứ`

## Card 11.7 — Vành Liên ngành: PM, Pháp lý, Tài chính, Mua sắm

**Quyết định cốt lõi:** Làm–mua–thuê (build/buy/rent) theo ma trận nào · Hợp tác PM-kỹ thuật: ai dịch yêu cầu thành SLI/journey · Mua sắm/nhà cung cấp: ràng buộc thoát (exit) đặt ở đâu · Bảng dịch thuật nghề: kỹ thuật ↔ tài chính ↔ pháp lý
**Con số neo:** Ma trận build/buy: `2×2 lợi thế × đặc thù` · Exit drill: `1–2 vendor quan trọng/năm` · Review vendor: `nửa năm` · Pháp lý vào sớm: `giai đoạn thiết kế`
**Bệnh & chẩn đầu tiên:** Tự viết CRM/auth/email → `2×2 + câu 5 năm` ; Pháp lý đỏ toàn bộ thiết kế → `mời ở giai đoạn thiết kế` ; Vendor tăng giá ×3, không thoát được → `exit drill + điều khoản`

## Card 11.8 — Lộ trình Học & 24+ Lab

**Quyết định cốt lõi:** Lộ trình học của tôi/tổ chức: 6 tuần hay theo phần · Lab: cái nào làm trước theo vai của tôi · Giữ kiến thức tươi: nhịp theo dõi phiên bản nào · Runbook 1 trang cho hệ mình dùng
**Con số neo:** Lab mỗi cái: `≤ 30 phút` · Runbook: `1 trang, 6 mục` · Hội thảo tuần: `15 phút, có lab` · Verify EOL: `mỗi quý`
**Bệnh & chẩn đầu tiên:** Đọc xong quên sạch → `1 lab/tuần + runbook` ; Tin số cũ (phiên bản đã đổi) → `lịch quý EOL` ; On-call mới luống cuống → `viết theo template §2.3`

## Card 12.1 — 5 Giả định Cổ điển bị AI phá vỡ

**Quyết định cốt lõi:** Chấp nhận tính xác suất ở đâu, chèn tính xác định ở đâu · Ngân sách trễ mới: TTFT + ITL thay p99 một con · Đơn vị tài nguyên mới: GPU/HBM/bandwidth — ai quy hoạch · Định nghĩa "chạy đúng" khi không có đáp án duy nhất
**Con số neo:** Token/s decode (serve thật): `chục–trăm/s (model lớn)` · TTFT hợp lý: `~200 ms–2 s` · Giá vào vs ra: `ra đắt hơn rõ rệt` · Giải bài model nhỏ vs lớn: `chênh bậc độ lớn`
**Bệnh & chẩn đầu tiên:** "Test pass" mà khách phàn nàn → `evals golden set (→12.5)` ; Chậm dù GPU khỏe → `→12.2 §5` ; Hóa đơn AI bất ngờ → `→12.6`

## Card 12.2 — Giải phẫu LLM Inference Serving (vLLM/SGLang/Dynamo)

**Quyết định cốt lõi:** Serving engine: vLLM / SGLang / TensorRT-LLM / Dynamo disaggregated · Batching + prefix cache: continuous batching, RadixAttention · Quantization: FP8 / NVFP4 / AWQ — đổi chính xác lấy gì · Prefill/decode tách hay chung; đặt serving ở đâu (cloud/own GPU)
**Con số neo:** vLLM / SGLang: `v0.32.0 (18/10) / v0.5.22 (19/10)` · NVIDIA Dynamo: `1.5.0 (21/09) — P/D disaggregated` · Continuous batching: `throughput × nhiều lần so tĩnh` · TTFT chat mục tiêu: `~1 s p95`
**Bệnh & chẩn đầu tiên:** TTFT cao, GPU rảnh (I-066) → `3 hướng §4-S6` ; Throughput thấp → `continuous batching + PagedAttention` ; Chất lượng rớt sau quantize → `FP8 hoặc về BF16 (đo eval)`

## Card 12.3 — RAG & Context Engineering

**Quyết định cốt lõi:** RAG hay long-context (hay cả hai) · Pipeline retrieval: hybrid (BM25+vector), rerank, chunking · **ACL-aware retrieval**: lọc theo quyền ngay lúc lấy · Ngữ cảnh: cấu trúc prompt, ưu tiên, ép kích thước
**Con số neo:** Chunk điển hình: `vài trăm–1k token + overlap` · Rerank chi phí: `model nhỏ, ms–chục ms/query` · Context dài hiện đại: `trăm nghìn token` · Recall@k mục tiêu: `> 0,8–0,9 trên golden set`
**Bệnh & chẩn đầu tiên:** AI bịa khi có dữ liệu → `đo recall@k golden` ; Đọc tài liệu lân phòng (I-068) → `metadata + filter trước prompt` ; Sai tên mã/số hiệu → `hybrid search`

## Card 12.4 — Agentic Systems & MCP

**Quyết định cốt lõi:** Agent phạm vi: trợ lý 1 bước / luồng dài / đa agent · Tool & MCP server: chuẩn nào, auth thế nào (D-133) · Sandbox cho code exec & hành động phụ · Bộ nhớ (memory) ngắn/dài, giới hạn chi phí
**Con số neo:** MCP revision: `2026-07-28 (stateless + OAuth 2.1 RS)` · Agent loop cap: `~10–30 bước (mặc định an toàn)` · Token budget/ task: `đặt theo loại task` · Sandbox: `container/microVM + egress allowlist`
**Bệnh & chẩn đầu tiên:** Agent lặp vô hạn / tiêu tiền → `cap + budget + kill-switch` ; Agent "quên" tool giữa chừng → `ưu tiên nén khác` ; Tool gọi sai tham số → `enum + validate + lỗi thân thiện`

## Card 12.5 — Evals, Quan sát gen_ai & Guardrails

**Quyết định cốt lõi:** Eval gate: golden set + ngưỡng — chặn CI/CD khi trượt (D-130) · LLM-judge: chấm gì tự động, chấm gì bằng người · Guardrails: chống injection, PII, nội dung cấm — ở mấy lớp · Quan sát gen_ai: span, token, chi phí theo feature/tenant
**Con số neo:** Golden set: `50–500 case, có phiên bản` · Ngưỡng eval gate: `theo nghiệp vụ, ghi trong repo` · Judge-vs-human: `đồng thuận mẫu 50 định kỳ` · Span gen_ai: `model, token, TTFT, cost`
**Bệnh & chẩn đầu tiên:** Đổi model, chất lượng ám ảnh tụt → `golden set + CI chặn` ; Judge chấm "nghe cũng được" → `rubric + so human` ; Guardrail im luôn → `test canary (chèn case xấu)`

## Card 12.6 — AI FinOps, Model Routing & AI Gateway

**Quyết định cốt lõi:** Model routing: cascading nhỏ→lớn, route theo gì (D-131) · Semantic cache: cache gì, TTL theo nghiệp vụ · AI Gateway: một cổng cho model/provider — tự dựng hay mua · Quản trị ngân sách: theo tenant/feature/ngày — tắt khi vượt
**Con số neo:** Giá vào vs ra: `ra đắt hơn rõ` · Model to vs nhỏ: `chênh bậc độ lớn` · Semantic cache tiết kiệm: `cao với workload lặp` · Batch API giảm giá: `đáng kể (đổi trễ)`
**Bệnh & chẩn đầu tiên:** Bill ×10 sau upgrade (I-067) → `canary tài chính + log token` ; Câu dễ vẫn đắt → `router + self-report` ; Câu lặp trả tiền lại → `cache + TTL nghiệp vụ`

## Card 12.7 — Chuỗi cung ứng Model, LoRA & Pháp lý AI

**Quyết định cốt lõi:** Nguồn model: API đóng / open-weights tự chạy / tự train · Tinh chỉnh: prompt/RAG đủ chưa, hay cần LoRA/SFT · AI-BOM: model nào, phiên bản nào, dữ liệu gì, license gì · Pháp lý AI: AI Act lớp rủi ro nào, dữ liệu huấn luyện ai
**Con số neo:** LoRA train: `giờ-GPU, weights MB` · SFT/full FT: `đắt hơn bậc độ lớn` · AI Act: `lớp rủi ro, áp dụng theo đợt 2025–2027` · License model: `đọc từng phiên bản`
**Bệnh & chẩn đầu tiên:** Không biết mình đang chạy model gì → `sinh CI + duyệt cổng license` ; Model bị rút/thay license, sập kế hoạch → `watch release notes + BOM` ; Prompt phình 10k token "để dạy style" → `bậc thang §2.2`

## Card 13.1 — Playbook: OLTP, Thanh toán & Sổ cái

**Quyết định cốt lõi:** Sổ cái: double-entry + đối soát thế nào (D-134) · Idempotency toàn trình: từ nút bấm tới sổ · Kiến trúc thanh toán: provider nào, lưu card ở đâu · Đối soát (reconciliation) hằng ngày với ai
**Con số neo:** Idempotency TTL: `≥ 24 h (theo retry window)` · Đối soát: `đêm, hàng ngày` · Journal cân: `SUM=0 bất biến` · Webhook latency: `phút (best-effort — →6.4)`
**Bệnh & chẩn đầu tiên:** Trừ tiền 2 lần → `audit chuỗi key (→4.8)` ; Số dư "không hiểu sao lệch" → `dựng journal + bất biến SUM=0` ; Webhook mất, đơn treo → `pull bù + đối soát`

## Card 13.2 — Playbook: Realtime, Chat & Cộng tác

**Quyết định cốt lõi:** Fan-out realtime quy mô lớn: broadcast vs per-connection (D-135) · Transport: WebSocket / SSE / polling (theo nền tảng — →4.6) · Reconnect & đồng bộ lại sau gián đoạn · Presence/typing: tần suất, TTL, lưu ở đâu
**Con số neo:** Connection/node: `~chục–trăm nghìn (tùy stack)` · Typing throttle: `2–3 s` · Presence TTL: `30–60 s` · Reconnect backoff: `jitter, cap 30–60 s`
**Bệnh & chẩn đầu tiên:** Nhóm to lag nặng → `lai on-read + cache` ; Mất mạng 30 s mất tin → `last_event_id + sync API` ; Restart node → sóng sập → `jitter + rate limit + drill`

## Card 13.3 — Playbook: Ingest, Telemetry & Stream

**Quyết định cốt lõi:** Hàng rào giữa ingest nghiệp vụ vs telemetry (mỗi loại một chuẩn sống) · Backpressure: chậm hay bỏ, ở đâu · Schema & evolution: registry, compatible-check ở CI · Buffer & đỉnh: Kafka partition/retention bao nhiêu cho "ngày tồi tệ"
**Con số neo:** Kafka throughput/partition: `MB/s bậc` · Retention nghiệp vụ: `≥ vài × MTTR` · Consumer lag alert: `leo thang + sắp hết retention` · Sampling telemetry: `theo lớp (→11.2)`
**Bệnh & chẩn đầu tiên:** Telemetry phình, tắc fact → `tách topic/cluster` ; Consumer chết 2 h mất dữ liệu → `tăng retention + drill` ; Đếm bị đôi → `8.3 chuỗi chuẩn`

## Card 13.4 — Playbook: Analytics & Open Lakehouse

**Quyết định cốt lõi:** Kiến trúc analytics: warehouse đóng vs open lakehouse · Bảng chuẩn hóa: kim cương (star) / dữ liệu thô + semantic layer · ETL vs ELT vs batch-đêm: độ tươi cho từng câu hỏi · Catalog & governance: ai thấy bảng nào, data lineage
**Con số neo:** DuckDB: `2.0 LTS (21/10) — server mode, agent mode` · ClickHouse: `26.10 monthly / 26.8 LTS (EOL 8/2027)` · Iceberg: `v3 (→5.9)` · Micro-batch điển hình: `5–15 phút`
**Bệnh & chẩn đầu tiên:** Hai dashboard hai số → `một định nghĩa + refresh` ; Query đắt quái quỷ → `partition + sort + prune` ; Đổi engine = di dân cả kho → `bảng Iceberg tách`

## Card 13.5 — Playbook: AI-Native, RAG & Multi-Agent

**Quyết định cốt lõi:** Sản phẩm AI: copilot (người chính) vs agent (AI chính) · Kiến trúc RAG theo miền dữ liệu (12.3) + ACL theo tenant · Multi-agent (12.4) — tách theo quyền hay giữ 1 agent + tools · Vòng đời: eval + rollback + chi phí theo tính năng
**Con số neo:** Golden set per tính năng: `50–500 case (12.5)` · Canary tài chính: `1% × 24 h trước full (12.6)` · Human-gate: `ngưỡng rủi ro viết ra (12.4)` · ACL retrieval: `filter trước prompt (12.3)`
**Bệnh & chẩn đầu tiên:** AI bịa trước khách (copilot lạm quyền) → `kéo về human-gate` ; Đọc dữ liệu lân phòng (I-068) → `filter + metadata (12.3)` ; Tài liệu cũ, trả lời cũ → `CDC-style + version index`

## Card 13.6 — Playbook: Toàn cầu, Offline-First & Edge

**Quyết định cốt lõi:** Đa vùng theo người dùng (active-active per region) · Offline-first cho luồng nào (6.3 bậc thang) · Edge compute cho phần nào (6.5) · Dữ liệu & luật theo vùng (10.8 + 8.7)
**Con số neo:** RTT chéo vùng: `50–300 ms một chiều` · Edge RTT: `~1–30 ms` · Replication chéo vùng: `async ~s (RPO theo cặp vùng)` · Home region pin: `theo tenant config`
**Bệnh & chẩn đầu tiên:** User EU thấy chậm → `trace + home region check` ; Dữ liệu "văng" qua region khác → `audit backup path` ; Chuyển vùng giữa chừng mất ghi → `8.7 §2.3 từng entity`

## Card 13.7 — Playbook: B2B Multi-Tenant SaaS

**Quyết định cốt lõi:** Isolation: Pool → Bridge → Silo theo tier (D-136) · Noisy neighbor & quota per tenant · Metering & billing: đo gì, xuất hoá đơn thế nào · Tenant lifecycle: onboarding/migration/offboarding
**Con số neo:** RLS: `mọi query; tenant từ token` · Escrow path: `pool→silo không viết lại` · Metering latency: `≤ giờ-ngày` · Offboard xoá: `crypto-shred + policy backup`
**Bệnh & chẩn đầu tiên:** Thấy dữ liệu tenant khác → `test hai-tenant CI` ; Một tenant làm chậm chung → `4 tầng §2.3` ; Hóa đơn tranh cãi → `đối soát nguồn (13.1)`

## Card 14.1.1 — Bán dẫn I: Vật liệu, CMOS, Transistor & Lithography

**Quyết định cốt lõi:** Đọc đúng "tên node" (5 nm/3 nm) khi chọn SKU · Hiểu vì sao hiệu năng miễn phí hết (post-2015) · Hiểu interconnect/vật liệu thay transistor là chiến trường mới · Biết chạy khi thấy "process/stepping/erratum"
**Bệnh & chẩn đầu tiên:** "Máy mới không nhanh tương ứng tiền" → `tôi dùng được bao nhiêu lõi/SIMD? (1.2/1.3)` ; Sự cố treo mơ hồ sau đổi thế hệ CPU → `có erratum nào cho stepping này chưa? (P)` ; Nhiệt đỉnh cao bất thường → `governor/thermal design đúng chưa? (1.7/2.3)`

## Card 14.1.2 — Bán dẫn II: Yield, Binning, Chiplets & CoWoS

**Quyết định cốt lõi:** Hiểu vì sao cùng SKU khác hiệu năng (binning/variability) · Hiểu chiplet/CoWoS đổi ý nghĩa "một CPU" · Dự trù khan hiếm khi chọn thế hệ chip · Đọc đúng "thế hệ"/"bước nhảy" khi chuẩn hoá platform
**Bệnh & chẩn đầu tiên:** Benchmark lệch giữa máy cùng SKU → `đo ≥3 máy + ghi stepping (I)` ; Đặt GPU AI chờ 6 tháng → `kịch bản không-GPU cho roadmap? (12.6)` ; "Sao CPU có 2 die nóng lệch nhau" → `làm mát theo die, không theo "chip" (14.3.1)`

## Card 14.1.3 — Bán dẫn III: SRAM, DRAM, HBM, Độ tin cậy & Kinh tế bộ nhớ

**Quyết định cốt lõi:** Chọn cấu hình bộ nhớ cho workload (băng thông vs dung lượng) · Sizing ECC/bảo vệ cho cụm chạy dài · Hiểu giá "chip AI" phần lớn là giá bộ nhớ · Hiểu DRAM có refresh/nhiễu — không phải "đọc ghi đúng luôn"
**Con số neo:** Loại: `Đặc trưng` · SRAM (cache): `nhanh, đắt, trong die` · DDR (DIMM): `rẻ/GB, băng thông vừa, có thể thêm/nâng` · LPDDR: `hàn chặt, tiết kiệm năng lượng`
**Bệnh & chẩn đầu tiên:** Job lớn corrupt dữ liệu thỉnh thoảng → `có ECC ở tầng này chưa? checkpoint bao lâu/lần? (14.5.2)` ; Thêm RAM không nhanh hơn → `p95 là do miss hay do băng thông? (1.5)` ; Inference GPU không theo FLOPS → `tokens/s per GB-bandwidth?`

## Card 14.2.1 — RF I: Truyền sóng, Link Budget & MIMO

**Quyết định cốt lõi:** Chọn công nghệ không dây cho vị trí/link cụ thể · Tính toán/link budget khi thiết kế vùng phủ · Hiểu vì sao "sóng yếu" là sự cố khó (thay đổi theo thời gian) · Hiểu băng tần/spectrum là tài nguyên quản trị
**Con số neo:** Băng: `Đặc trưng` · <1 GHz: `xa, xuyên tốt, băng thông thấp` · 2.4 GHz: `rẻ, tệ vì đông` · 5/6 GHz: `nhanh, ít xuyên`
**Bệnh & chẩn đầu tiên:** Wi-Fi "1 vạch" góc phòng → `đo SNR tại chỗ; thêm AP hay dịch chỗ? (link budget)` ; Tốc độ sụt giờ cao điểm → `scan kênh; kênh nào sạch? (I)` ; 5 GHz không qua được sàn nhà → `lặp mesh/wired backhaul (P)`

## Card 14.3.1 — Datacenter I: Nhiệt, Làm mát & Cấp điện

**Quyết định cốt lõi:** Chọn hướng làm mát cho cụm mới (air/liquid) · Thiết kế mức dư điện (redundancy) cho tier cần · Đặt workload theo giới hạn nhiệt/điện (không chỉ CPU) · Xử lý sự cố hạ tầng vật lý (mất điện/mất mát)
**Con số neo:** Lớp: `Phạm vi` · Air + aisle chứa: `kW/rack vừa` · Rear-door HX: `nâng cấp air` · Direct-to-chip liquid: `chục kW/rack`
**Bệnh & chẩn đầu tiên:** Throughput cụm sụt buổi trưa → `nhiệt vào/xung GPU có log không? (2.3)` ; Server tự reset, log sạch → `nguồn nào dùng chung? có log PDU/UPS không?` ; Rack mới "không bật được" → `PDU bao nhiêu A — tính lại tổng?`

## Card 14.4.1 — ML I: Objective, Optimizer & Kiến trúc Mô hình

**Quyết định cốt lõi:** Chọn họ mô hình cho bài toán (Transformer/MoE/SSM/cây/hồi quy) · Định nghĩa objective đúng với sản phẩm · Hiểu vòng lặp huấn luyện (optimizer/batch/epoch) để đọc log đúng · Biết ranh giới trách nhiệm với đội ML (→P12)
**Con số neo:** Họ: `Thế mạnh` · Hồi quy/cây/GBM: `bảng dữ liệu, giải thích, rẻ` · CNN: `ảnh/tín hiệu cục bộ` · Transformer/attention: `chuỗi, tổng hợp ngữ cảnh`
**Bệnh & chẩn đầu tiên:** Mô hình "khéo" nhưng người dùng ghét → `đo sản phẩm nào ngoài loss? (12.4)` ; Serving chậm dù GPU to → `băng thông/byte per token? (12.2)` ; MoE này nhanh lúc đông lúc vắng → `load-balance expert thế nào? (12.5)`

## Card 14.4.2 — ML II: Scaling, Pre/Post-training & Song song

**Quyết định cốt lõi:** Ướp chi phí huấn luyện vs mua/rent mô hình · Chọn phương án tinh chỉnh (full fine-tune/LoRA/prompt) · Thiết kế song song huấn luyện (data/tensor/pipeline) · Lên kế hoạch dự phòng khi cụm huấn luyện hỏng giữa chừng
**Con số neo:** Chiến lược: `Chi phí` · Prompt/in-context: `~0` · RAG (12.4): `hạ tầng tìm kiếm` · LoRA/adapter: `thấp`
**Bệnh & chẩn đầu tiên:** Thêm GPU nhưng không nhanh → `đo băng thông link + thời gian bước (2.3)` ; Job tuần chết, mất toàn bộ → `tần suất + thời gian lưu checkpoint? (14.5.2)` ; Fine-tune làm mô hình "ngớ" → `eval trước-sau trên tập ngoài? (12.4)`

## Card 14.4.3 — ML III: Đánh giá, Lượng tử hoá & Ranh giới với Serving

**Quyết định cốt lõi:** Xây bộ đánh giá (eval) trước khi chọn/mua mô hình · Chọn precision lượng tử hoá cho serving (FP16→INT8/4) · Quyết định promote/rollback mô hình mới · Vẽ ranh giới trách nhiệm với cụm 12
**Con số neo:** Loại đo: `Công cụ` · Benchmark công khai: `tập chuẩn` · Hold-out riêng: `dữ liệu bạn` · Người chấm (rubric): `panel`
**Bệnh & chẩn đầu tiên:** Mô hình mới tệ thật ra rất nhanh → `eval set có tác vụ này chưa?` ; INT4 tệ một kiểu lạ → `từng tác vụ so từng mức quant chưa?` ; "Benchmark tốt" nhưng user phàn nàn → `có hold-out riêng + feedback loop không? (12.4)`

## Card 14.5.1 — HPC I: Phân rã Bài toán, MPI & Interconnect

**Quyết định cốt lõi:** Chọn mô hình phân rã (dữ liệu/nhiệm vụ/luồng) cho bài toán tính toán · Chọn giao tiếp (MPI/PGAS/MapReduce-style) · Chuẩn bị interconnect (bandwidth/độ trễ/topology) cho cụm · Quyết định job nào đáng đưa lên cụm vs cloud burst
**Con số neo:** Mô hình: `Giao tiếp` · MPI (message passing): `tường minh send/collective` · PGAS/chia bộ nhớ: `bộ nhớ "xuyên nút"` · MapReduce/Spark-style: `shuffle qua đĩa`
**Bệnh & chẩn đầu tiên:** Thêm nút không nhanh hơn → `đo strong scaling 1→8 nút (3.2)` ; Job chờ mãi không chạy → `yêu cầu topology có slack không?` ; Chạy chập chờn không rõ → `log link error/failure ở interconnect?`

## Card 14.5.2 — HPC II: IEEE 754, Lan truyền Sai số & Tái lập

**Quyết định cốt lõi:** Chọn precision (FP64/32/16/bf16) cho từng tầng hệ thống · Đảm bảo kết quả tái lập được (reproducibility) · Xử lý kết quả phân tán khác nhau giữa lần chạy · Thiết kế checkpoint cho job dài
**Con số neo:** Khái niệm: `Ý nghĩa hệ thống` · ulp/epsilon máy: `"sai số một phép" — đơn vị đàm phán` · cancellation: `trừ gần-bằng-nhau — thuật toán phải tránh` · condition number: `mức thổi-phồng sai số của bài toán`
**Bệnh & chẩn đầu tiên:** Hai lần chạy lệch số cuối → `cần bit-exact không, ai cần?` ; Kết quả "vô lý" sau phép trừ → `viết lại công thức (P)` ; Training ML không tái lập được → `seed + chế độ deterministic bật chưa?`

## Card 14.8.2 — Chuẩn II: Compatibility, Versioning & Chọn draft vs stable

**Quyết định cốt lõi:** Thiết kế hợp đồng phiên bản (API/format/protocol) · Chọn dùng bản draft hay stable trong sản phẩm · Chính sách hỗ trợ bản cũ (window) · Quyết định ngừng (deprecate → remove) một tính năng
**Con số neo:** Công cụ: `Giải quyết gì` · Semver + changelog: `truyền thông đổi` · Additive-only: `không break cũ` · v1/v2 song song: `di dời từ từ`
**Bệnh & chẩn đầu tiên:** Khách vỡ sau nâng "nhỏ" → `hợp đồng ghi ở đâu? changelog nói gì?` ; Cứ sợ xoá field cũ → `window + lộ trình khai tử ở đâu?` ; Kẹt draft cũ không lên được → `lớp cách ly chạm draft ở đâu?`

## Card 14.10.1 — Mật mã I: Định nghĩa, Primitives & Lattices

**Quyết định cốt lõi:** Chọn primitives đúng việc (hash/symmetric/asymmetric/MAC/signature) · Không tự chế thuật toán (chỉ chọn tham số chuẩn) · Đọc đúng mức an toàn (bit security, key size) · Hiểu nền toán (số học mod / lattices) đủ để theo dõi PQC
**Con số neo:** Primitive: `Đưa ra` · Symmetric (AEAD): `bí mật + toàn vẹn, nhanh` · Hash: `vân tay công khai` · MAC: `toàn vẹn có khoá`
**Bệnh & chẩn đầu tiên:** Mã hoá mà vẫn lộ metadata → `cần mã hoá gì *thật sự*? (13.x)` ; Nonce lặp → vỡ toàn bộ → `CSPRNG + counter + khoá-riêng?` ; "Băm mật khẩu" nhanh → `argon2/bcrypt + salt chưa?`

## Card 14.10.2 — Mật mã II: PQC (FIPS 203/204/205) & Constant-time

**Quyết định cốt lõi:** Lập kế hoạch di dời hậu lượng tử cho hệ thống mình · Chọn thuật toán/kích cỡ theo chuẩn mới (không tự pha trộn) · Yêu cầu constant-time cho code crypto chạm secret · Thiết kế crypto-agility (thay thuật toán = cấu hình)
**Con số neo:** Thành phần: `Hôm nay` · Trao đổi khoá: `ECDH/X25519` · Chữ ký: `ECDSA/RSA` · Đối xứng: `AES/ChaCha`
**Bệnh & chẩn đầu tiên:** "Chưa cần lo, chưa có máy tính lượng tử" → `dữ liệu tôi cần bí mật bao lâu nữa?` ; Handshake chậm/gói to sau PQC → `hybrid + đo MTU/round-trip thật` ; Timing leak trong code crypto → `thư viện audit? có nhánh theo secret không?`

## Card 14.11.1 — Side-channel I: Timing, Speculation & Rowhammer

**Quyết định cốt lõi:** Nhận diện kênh rò trong thiết kế (thời gian/cache/nhiệt/điện) · Đánh giá rủi ro code crypto chạm secret trên máy chia sẻ · Quyết định cập nhật/merge khi có CVE side-channel mới · Thiết kế co-tenant/thời gian phẳng cho dịch vụ nhạy cảm
**Con số neo:** Kênh: `Đo gì` · Timing: `thời gian phản hồi` · Cache: `thời gian truy cập bộ nhớ` · Speculation: `dấu vết đoán nhánh`
**Bệnh & chẩn đầu tiên:** Login sai/sai khác thời gian → `so sánh constant-time chưa? (14.10.2)` ; "Username tồn tại" lộ qua message → `thông báo có trung lập không?` ; Cloud cảnh báo cross-VM → `cô lập/miễn giảm theo vendor chưa?`

## Card 14.11.2 — Side-channel II: Mitigation, Residual Risk & Isolation

**Quyết định cốt lõi:** Chọn mức phòng thủ theo giá trị tài sản (không max mọi thứ) · Thiết kế cách ly theo lớp (tiến trình/VM/enclave/máy riêng) · Quản lý rủi ro dư (residual) một cách minh bạch · Đóng atlas: gọi chuyên gia ngành khi nào (D-137)
**Con số neo:** Lớp phòng thủ: `Chống được` · Constant-time/trung lập: `timing/enum` · Tách tiến trình/VM: `cache/tenant` · Tắt speculate/prefetch: `Spectre-họ`
**Bệnh & chẩn đầu tiên:** CVE speculative: không ai biết làm gì → `kịch bản 72-giờ ở đâu? (2.7)` ; "An toàn" nhưng không chỉ ra cái gì → `rủi ro dư ghi ở đâu, ai ký?` ; Dịch vụ mật chạy chung cụm dev → `tài sản này đáng lớp cách ly nào?`

## Card 14.2.2 — RF II: Di động, Handover, LEO & GNSS

**Quyết định cốt lõi:** Thiết kế cho thiết bị di động (mạng thay đổi giữa các lúc) · Chọn liên kết cho vị trí xa (LEO vs GEO vs terrestrial) · Dùng vị trí GNSS đúng độ tin cậy · Chọn giao thức cho mạng "xấu"
**Con số neo:** Liên kết: `RTT` · Cellular 4G/5G: `chục ms` · LEO satellite: `chục ms` · GEO satellite: `~500+ ms`
**Bệnh & chẩn đầu tiên:** App "đứt" khi đi thang máy → `state có recover tự động không? (5.2/11.5)` ; Upload lớn thất bại trên di động → `chunk/resume? QUIC migration?` ; "GPS sai trong nhà" → `nguồn vị trí phụ (wifi) chưa?`

## Card 14.3.2 — Datacenter II: PUE, Capacity, Failure Domain & Carbon

**Quyết định cốt lõi:** Ướp chi phí điện/nước khi đặt & vận hành cụm · Phân vùng failure domain khi đặt workload · Lập kế hoạch capacity (điện/không gian/lạnh) theo tăng trưởng · Báo cáo carbon/energy của hệ thống
**Con số neo:** Khái niệm: `Đo bằng` · PUE: `điện tổng/điện IT` · WUE: `lít/kWh` · Failure domain: `danh sách tài sản chung`
**Bệnh & chẩn đầu tiên:** HA "3 bản sao" chết cùng lúc → `kiểm metadata: AZ/PDU/trạm nào? (3.5)` ; Mở rộng cụm bị chậm không rõ lý do → `headroom kW còn bao nhiêu? (I)` ; Bill điện tăng gấp đôi sau dự án → `đo per-rack kWh — ai đang ngốn?`

## Card 14.6.1 — Game I: Frame Budget, Pipeline & ECS

**Quyết định cốt lõi:** Phân bổ ngân sách khung hình (frame budget) giữa các hệ thống · Chọn kiến trúc tổ chức mã (OOP thừa kế vs ECS) · Chọn pipeline render/threading (một luồng vs job system) · Quyết định cắt tính năng khi framerate không đạt
**Con số neo:** Mô hình: `Đặc trưng` · OOP thừa kế: `trực quan, chết ở quy mô lớn` · ECS thuần: `dữ liệu phẳng, system quét khối` · Hybrid: `GameObject + component`
**Bệnh & chẩn đầu tiên:** Fps thấp, CPU 100% → `luồng chính đang chạy hệ thống nào? (profiler)` ; GPU đợi, CPU rảnh → `pipeline stalls ở đâu?` ; "Vù vù" lúc đông entity → `layout dữ liệu theo cột chưa? (ECS)`

## Card 14.6.2 — Game II: Prediction, Reconciliation & Lockstep

**Quyết định cốt lõi:** Chọn mô hình mạng game (authoritative server vs lockstep P2P) · Thiết kế client-side prediction + reconciliation · Xử lý mất gói/lag (interpolation, lag compensation) · Chọn tick rate & bước mô phỏng cố định
**Con số neo:** Mô hình: `Sự thật nằm ở` · Authoritative + prediction: `server` · Lockstep P2P: `mô phỏng xác định chung` · Relay/rollback: `server chuyển tiếp + quay lại`
**Bệnh & chẩn đầu tiên:** Nhân vật "nhảy vọt" liên tục → `RTT/jitter người này bao nhiêu? (2.3)` ; "Bắn trúng mà không chết" → `server bù bao nhiêu ms? ai ưu tiên?` ; Cả trận khựng theo một người → `timeout/mở khoá người lag chưa?`

## Card 14.6.3 — Game III: Replication, Anti-cheat & Profiling

**Quyết định cốt lõi:** Chọn cái gì replicate cho client nào (interest mgmt) · Thiết kế bài toán "client là kẻ thù" (server authority + kiểm chứng) · Chọn hệ phòng chống gian lận (heuristics/report/ban) · Lên vòng lặp profiler + telemetry cho live game
**Con số neo:** Lớp phòng chống: `Bắt cái gì` · Server authority + kiểm biên: `state/timing cheat` · Replication lọc AOI: `information cheat` · Phân tích thống kê hành vi: `aim-bot/macro`
**Bệnh & chẩn đầu tiên:** Wall-hack xuất hiện → `AOI lọc server-side chưa?` ; Speed-hack trong quan hệ → `kiểm biên vận tốc server chưa?` ; Kinh tế game lạm phát → `đồ thị giao dịch có bất thường chưa? (2.3)`

## Card 14.7.1 — Robotics I: Sensor, Kinematics & Control

**Quyết định cốt lõi:** Chọn tổ hợp sensor cho nhiệm vụ (camera/LiDAR/IMU/encoder) · Thiết kế vòng điều khiển (tần số, cảm biến nào tham gia) · Xử lý sai số/độ trễ cảm biến (fusion, lọc) · Quyết định hành vi an toàn khi "mù" (mất/không chắc tín hiệu)
**Con số neo:** Thành phần: `Tuỳ chọn chính` · Cảm biến vị trí: `GPS/SLAM/vision/encoder` · Tư thế: `IMU + fusion` · Điều khiển: `PID/LQR/MPC/learned`
**Bệnh & chẩn đầu tiên:** Robot dao động/rung quanh mục tiêu → `giảm gain hay giảm trễ? đo trễ vòng` ; Trôi dần khỏi đường đi → `fusion nguồn tuyệt đối có chưa?` ; Đẹp trong mô phỏng, tệ thật → `calibration thực tế đã làm chưa?`

## Card 14.7.2 — Robotics II: WCET, Jitter & RTOS

**Quyết định cốt lõi:** Chọn nền tảng vòng cứng (RTOS vs Linux preempt vs MCU trần) · Bố trí task ưu tiên & phân bố tính toán · Kiểm chứng deadline (WCET — xấu nhất) · Thiết kế truyền thông giữa vòng cứng và phần mềm thường
**Con số neo:** Nền tảng: `Độ trễ điều độ` · MCU trần (superloop): `không điều độ` · RTOS (FreeRTOS/Zephyr-class): `µs, cận trên rõ` · Linux + PREEMPT_RT: `chục µs–100 µs`
**Bệnh & chẩn đầu tiên:** "Đôi khi" trễ vòng, không tái hiện → `đếm miss bằng timer HW + histogram` ; Task cao vẫn bị chặn → `inheritance bật chưa? ai giữ khóa?` ; Thêm log thì hết lỗi → `log async (hàng đợi) — luôn`

## Card 14.7.3 — Robotics III: Safety Lifecycle (ISO 26262/IEC 61508)

**Quyết định cốt lõi:** Xác định mức an toàn cần (SIL/ASIL) cho chức năng · Phân bổ kiến trúc an toàn (redundancy/degradation/fail-safe) · Quyết định quy trình phát triển kèm chứng cứ (V-model, trace) · Ranh giới trách nhiệm với chứng nhận/third party
**Con số neo:** Khái niệm: `Chuẩn nhà` · SIL 1–4: `IEC 61508 (công nghiệp)` · ASIL A–D: `ISO 26262 (ô tô)` · HARA: `cả hai`
**Bệnh & chẩn đầu tiên:** Hệ "an toàn" chết toàn bộ khi một cảm biến hỏng → `hành vi hỏng từng phần định nghĩa chưa?` ; Redundancy chết chung → `gì chung giữa hai kênh? (14.3.2)` ; Người vận hành bấm nhầm chế độ → `trạng thái hiển thị thế nào?`

## Card 14.8.1 — Chuẩn I: Quy trình RFC & Governance

**Quyết định cốt lõi:** Chọn theo chuẩn nào khi thiết kế giao diện/protocol · Đọc/hiểu trạng thái chuẩn (draft/PS/Final/withdrawn) · Tham gia hoặc theo dõi quy trình chuẩn hoá (IETF/W3C/ISO) · Nội bộ: mượn mô hình RFC cho quyết định kiến trúc
**Con số neo:** Loại chuẩn: `Ví dụ` · Giao thức mở, process mở: `HTTP, QUIC (IETF)` · Ngôn ngữ/nền tảng: `SQL (ISO), C++` · De-facto: `x86, API nhà dẫn dắt`
**Bệnh & chẩn đầu tiên:** Cài theo chuẩn, không kết nối được → `trạng thái RFC hôm nay là gì? (2.4)` ; "Chuẩn không nói rõ" chỗ quan trọng → `errata/interop test của họ là gì?` ; Vendor "hỗ trợ chuẩn" nhưng lệch → `test tuân thủ (conformance) chạy chưa?`

## Card 14.9.1 — PL I: Semantics, Type Systems & IR/SSA

**Quyết định cốt lõi:** Chọn ngôn ngữ cho tầng hệ thống (tĩnh/động, GC/thu thủ công) · Đọc/hiểu thông báo lỗi kiểu để tự sửa · Thiết kế DSL/schema nội bộ (mini-language) · Hiểu trình biên dịch làm gì để đánh giá toolchain (build time, tối ưu)
**Con số neo:** Hệ: `Thế mạnh` · Động (Python/JS): `nhanh viết, REPL` · Tĩnh đơn giản (Go): `đọc dễ, build nhanh` · Generics (Java/C#/TS): `tái sử dụng`
**Bệnh & chẩn đầu tiên:** Lỗi production không thấy khi compile → `lỗi này thuộc loại gì — có kiểu hoá được không?` ; Null/None lan tràn → `Option + match bắt buộc chưa?` ; "Nó là gì?" khi đọc code mình → `ranh giới API có kiểu rõ chưa?`

## Card 14.9.2 — PL II: Optimization, Alias Analysis & Codegen/ABI

**Quyết định cốt lõi:** Bật/dùng cờ tối ưu đúng mức (O0–O3, LTO) · Viết code thân thiện tối ưu (alias,_branch, layout) · Chọn build target/ABI (múi ABI, calling convention) · Quyết định khi nào tự tối ưu tay vs tin compiler
**Con số neo:** Bậc: `Ví dụ` · Thuật toán: `O(n²) → O(n log n)` · Cấu trúc/layout: `SoA, cache-line, pool` · Cờ build: `-O2/-O3, LTO, PGO`
**Bệnh & chẩn đầu tiên:** Release khác Debug (không chỉ nhanh) → `code có dựa UB không? (ubsan!)` ; Thêm hàm getter "không tốn" → `compiler thấy đích chưa?` ; Vectorize không chịu → `restrict/SoA/đếm bước rõ`

## Card 14.9.3 — PL III: Đọc Benchmark đúng & Reproducible Builds

**Quyết định cốt lõi:** Thiết kế benchmark nội bộ đáng tin · Đọc benchmark công khai (blog/so sánh ngôn ngữ) mà không bị lừa · Cài đặt reproducible builds cho artifact quan trọng · Trả lời "bản mới nhanh/chậm hơn?" bằng quy trình
**Con số neo:** Loại benchmark: `Trả lời câu hỏi` · Micro (một hàm): `chi phí nguyên tố` · Macro (workload thật): `trải nghiệm người dùng` · So sánh A/B: `chọn phương án`
**Bệnh & chẩn đầu tiên:** "Nhanh 2×" không thấy ở prod → `benchmark đo cái prod làm không?` ; Kết quả nhảy mỗi lần chạy → `warmup + n lần + min/median chưa?` ; Hai build "giống nhau" khác hash → `deterministic mode + cố định env chưa?`

## Card 14.10.3 — Mật mã III: ZK, MPC, FHE & Ma trận Độ trưởng thành

**Quyết định cốt lõi:** Nhận diện khi nào bài toán của tôi thật sự cần ZK/MPC/FHE · Đánh giá độ trưởng thành trước khi chọn nền công nghệ này · Hiểu chi phí bậc số để phản biện đề xuất "dùng ZK cho mọi thứ" · Đặt ranh giới trách nhiệm (đội crypto/đối tác audit)
**Con số neo:** Công nghệ: `Bài toán` · ZK-SNARK: `chứng minh không lộ` · ZK-STARK: `chứng minh, không setup, kháng Q` · zkVM: `chứng minh "chạy đúng mã"`
**Bệnh & chẩn đầu tiên:** "Privacy" dự án trễ 6 tháng → `threat model thật là gì?` ; Prover tốn GPU đốt chi phí → `bài toán đáng giá proven không?` ; Trusted setup ai cũng gật đầu mà không hiểu → `tham số setup ai kiểm — bao giờ?`

