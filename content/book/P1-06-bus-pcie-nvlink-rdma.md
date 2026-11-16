# 1.6 — Bus & liên kết: PCIe, NVLink, RDMA

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.3 (topo bộ nhớ) · 1.5 (GPU).

**Sợi chỉ đỏ:** *GPU, card mạng, ổ đĩa nói chuyện với CPU và nhau qua đâu — vì sao 'cắm đúng khe' là quyết định hiệu năng?* — trả lời: mọi thiết bị nói chuyện qua PCIe theo đơn vị lane, GPU nói với nhau qua NVLink, RDMA cho phép đi tắt bỏ kernel — "cắm đúng khe" là bài toán chia lane có số, không phải may rủi. Câu hỏi để lại cho chương sau: *Trong máy đã rõ — còn đoạn đường từ điện thoại khách tới server: RTT và băng thông ràng buộc gì?*

**Thuật ngữ sẽ gặp:** *lane* — một đường PCIe, băng thông đơn vị của mọi card; *PCIe gen* — thế hệ lane: cùng x16 nhưng gen mới nhanh gấp đôi cũ; *DMA/P2P* — thiết bị tự chép dữ liệu, không qua CPU; *NVLink* — dây riêng giữa các GPU, rộng hơn PCIe; *RDMA* — card mạng ghi thẳng vào bộ nhớ ứng dụng, bỏ kernel; *DPU* — processor dồn việc hạ tầng ra khỏi CPU.

**Ví dụ mở đầu:** Máy chủ mới của DM cắm card 25 GbE vào khe x16 dùng chung đường với GPU: benchmark mạng chỉ đạt 40% kỳ vọng. Không hỏng gì cả — chỉ là tổng lane của chip có hạn và người lắp không đọc bảng chia lane. Một dòng lspci đọc đúng tiết kiệm một tuần debug và một cuộc cãi với nhà cung cấp.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Phân bổ lane PCIe giữa GPU/NIC/NVMe | Ai cần bao nhiêu GB/s thật? Tôi đã dành lane cho thiết bị nào mà quên? |
| 2 | Topo liên GPU (NVLink full / ngày càng nhiều / chỉ PCIe) | Workload của tôi cần all-reduce bao nhiêu GB/s? P2P được không? |
| 3 | Mạng cụm: RoCE hay InfiniBand (hay Ethernet thường) | Tôi cần lossless thật không? Ngân sách vận hành theo được không? |
| 4 | Có offload xuống NIC/DPU không | Vấn đề của tôi là băng thông, pps, hay CPU hệ thống? |

---

## 2. Cơ chế

### 2.1 PCIe: đơn vị lane, mọi thiết bị chia chung

PCIe là **nội tạng chung** của máy chủ: GPU, NVMe, NIC, accelerator, CXL memory — tất cả treo trên cùng cây root-complex. Đơn vị là **lane** (cặp dây serial); băng thông mỗi lane theo thế hệ:

```
Gen3  ~1 GB/s/lane   (16 lane = ~16 GB/s)
Gen4  ~2 GB/s/lane
Gen5  ~4 GB/s/lane
Gen6  ~8 GB/s/lane   (PAM4 — đang rollout 2026)
```

(Cả hai hướng; bậc "gấp đôi mỗi thế hệ" (V).) Điểm mấu chốt: **lane là ngân sách hữu hạn** — socket server hiện đại có 80–128 lane usable (I). GPU x16 + NVMe x4 + NIC x8 + ... là bài toán xếp binh; card bổ sung (FPGA, DPU, CXL) dễ làm cả cây chật. Nạp thiếu lane (x8 thay vì x16) thường **không làm giảm thực đo** nhiều trừ khi workload bão hoà (GPU training large-model là ngoại lệ — đo xem).

### 2.2 P2P và DMA: dữ liệu nên đi đường ngắn

Mặc định, GPU↔NIC hoặc GPU↔NVMe đi qua **BAR/thư ký CPU** (bounce buffer) — tốn băng thông DRAM và chu kỳ CPU. Ba cách tốt hơn:
1. **P2P DMA** (GPU ghi thẳng vào bộ nhớ NIC): `nvidia-peermem` — đường ngắn cho RDMA/NCCL;
2. **GPUDirect Storage**: NVMe → thẳng VRAM cho checkpoint/data loading;
3. **IOMMU group** phải cấu hình đúng (`vfio`, ACS) — và lưu ý: bật ACS để isolate có khi chặn P2P — trade-off an ninh/hiệu năng thật (→10.7 leakage lớn hơn cần thiết nếu tắt bừa).

### 2.3 NVLink: mức độ liên kết cao

PCIe nối **máy tính với thiết bị**; NVLink nối **GPU với GPU** — mesh trong node. Bậc số (đã verify 30/10):
- NVLink4 (Hopper): 900 GB/s tổng/GPU;
- **NVLink5 (Blackwell)**: 1,8 TB/s/GPU;
- **NVLink6 (VR200 NVL72, 2026)**: 260 TB/s tổng cho 72 GPU trên rack + NVSwitch — coi rack như **một GPU logic** với 288 GB HBM4 đồng nhất.

Tại sao quan trọng với người không làm AI: vì nó dịch **ranh giới "node"** — băng thông trong rack NVL72 vượt xa mọi thứ bạn có thể gắn qua PCIe, nên các khái niệm "local/remote" của tầng 8 (→8.2) phải viết lại theo topo thật, không theo "số máy chủ".

Đối thủ mở: UALink (consortium 2024+, cho accelerator AMD/Intel...) và Ethernet scale-up (Ultra Ethernet) — đang chặng đầu, theo dõi nhưng chưa mua.

### 2.4 RDMA: bỏ kernel khỏi đường dữ liệu

Bypass kernel: NIC đọc/ghi thẳng bộ nhớ application qua verben. Hai họ:
- **InfiniBand:** lossless theo thiết kế, thư viện riêng (fastest, đắt, khóa vendor);
- **RoCEv2:** RDMA trên Ethernet — cần lossless: PFC (priority flow control) + ECN. Đây là điểm vận hành rắc rối nhất: PFC misconfigure → deadlock/head-of-line; nhiều cụm "RoCE" thực ra đang chạy chậm vì backoff.

Một câu hỏi quan trọng: **cụm của tôi cần RDMA không?** Không phải vì AI nói vậy; mà vì: cần GPU P2P tới băng thông ~hàng trăm GB/s (có), cần < 2 µs RPC (không chắc), hoặc cần storage trực tiếp fast path (khác — có thể dùng NVMe/TCP).

### 2.5 DPU và offload

DPU/SmartNIC dời việc (mạng vxlan, IPsec, storage) khỏi CPU. Hai lý do thật: (a) pps cao (th > 10–20 Mpps) để CPU không theo kịp; (b) isolate — control plane cụm khỏi host CPU. Còn lại thường là marketing; đo CPU cycles thật của network stack trước khi mua.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| PCIe Gen4/5/6 mỗi lane | ~2 / ~4 / ~8 GB/s | V | hai hướng |
| Lane mỗi socket server | 80–128 | I | sau khi trừ chipset |
| NVLink4 / 5 / 6 | 0,9 / 1,8 TB/s·GPU / 260 TB/s·rack | V | Hopper / Blackwell / VR200 |
| NIC production | 100–400 GbE phổ thông; 800G ở AI spine | I | |
| RDMA latency (verben) | ~1–2 µs một chiều | I | so ~20–50 µs kernel TCP |
| NVMe Gen5 x4 | ~14 GB/s | V | →1.4 |

---

## 4. Suy luận kiến trúc

- **S1:** Lane PCIe, băng thông switch, số NVLink — đều là **hằng số sinh lý** của một lần mua phần cứng; phần mềm chỉ lựa chọn cách dùng, không tạo thêm.
- **S2:** Tham số trụ: GB/s mỗi thiết bị đo bằng `lspci` capability vs đo throughput; độ bão hoà từng hop.
- **S3:** Offload đổi CPU lấy độ phức tạp; P2P đổi isolate lấy băng thông; scale-up interconnect (NVLink) đổi tiền lấy ranh giới node mới — mỗi cái đều có giá đo được.
- **S4:** Băng thông liên chip tăng nhanh hơn băng thông DRAM/kênh → kiến trúc "thiết bị tự xử lý + liên kết mỏng" thắng dần "CPU trung tâm + bus chung" trong các cụm lớn.
- **S5:** CXL (bộ nhớ qua PCIe, →1.3) đang phình thành lớp "tier ấm" — cùng cây lane với GPU/NIC, do đó **ngân sách lane sẽ ngày càng căng**: kế hoạch 3 năm nên tính trước.
- **S6:** Khi thấy "mạng chậm", hỏi: chậm ở hop nào — cây PCIe trong máy, liên GPU, hay Ethernet ngoài rack? Ba câu khác nhau ba chương khác nhau (1.5, đây, 1.7).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| GPU.train chậm hơn spec 2× | All-reduce đi PCIe thay vì NVLink/P2P | `nvidia-smi topo -m`; NCCL debug log | §2.3 |
| Thêm NIC x8, tốc độ không đổi | Lane thiếu / chia switch uplink | `lspci -vv` (LnkSta vs LnkCap) | §2.1 |
| RoCE throughput thất thường | PFC/ECN cấu hình lệch | `roce_cfg`/debug PFC counters | §2.4 |
| Copy GPU→host chậm bất thường | Thiếu pinned memory / peermem | cudaMemcpy pageable vs pinned benchmark | §2.2 |
| CPU cao chỉ vì mạng | Kernel path, không offload | `perf` trên softirq; so pps | §2.5 |
| VM không thấy thiết bị passthrough | IOMMU group dính chung thiết bị khác | `iommu_groups` listing | §2.2 |

---

## 6. Cách đo

```bash
lspci -vv | grep -A20 Lnk    # LnkCap (năng lực) vs LnkSta (đang chạy) mỗi thiết bị
nvidia-smi topo -m           # ma trận liên GPU: NV# / PIX / PHB / SYS
ib_write_bw -d <dev>          # băng thông RDMA thật giữa 2 node
ibv_devinfo                   # trạng thái verben/prefetch từng port
ethtool -S eth0 | grep -iE 'drop|pause|ecn'   # PFC/ECN drops (RoCE)
iperf3 -c host -P 8 -t 30     # TCP song song — chỉ để đối chiếu, không phải biên trên
```

Nguyên tắc: **topo trước, benchmark sau.** Đa số "mạng chậm" là "topo khác với điều tôi tưởng" — NVLink tưởng mà thực ra SYS (qua CPU), lane tưởng x16 mà chạy x4, PFC tưởng bật mà thực ra drop.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay NVLink/NVL72:** nhiều node Ethernet + FSDP/TP nhỏ hơn — đổi throughput lấy chi phí vốn và tính độc lập vendor; đúng khi model vừa phải và utilization tốt. **Thay RoCE/IB:** TCP thường + tối ưu ứng dụng (đa số dịch vụ không cần < 5 µs); hoặc NVMe/TCP cho storage. **Thay DPU:** đơn giản hoá — giảm pps (batch, cache), chấp nhận CPU network stack.

Năm thấu kính:
- **Kinh tế:** Interconnect là chi phí ẩn lớn nhất cụm AI (cây switch + optics có khi ~30%CAPEX (I)); bảng giá chỉ có nghĩa khi kèm topo.
- **Vận hành:** Mọi thiết bị hot-plug/repair đều làm cây lane thay đổi — cấu hình nên declarative (đối chiếu `lspci` với inventory mong muốn).
- **An ninh:** P2P và tắt ACS mở lối side-channel giữa thiết bị; trong multi-tenant, isolation (→1.8 IOMMU) đáng giá hơn vài µs.
- **Lịch sử:** "Ethernet sẽ chết vì ..." được nói mỗi 5 năm (ATM, FC, IB scale-out); Ethernet vẫn thắng bằng vì nó rẻ và đủ tốt — ngoại lệ hiện tại là scale-up GPU, nơi NVLink đang giữ ngai (đến khi UALink/UEC kịp).
- **Người dùng:** Người dùng không thấy bus; họ thấy "reload lại model mất 10 phút" — đó là checkpoint qua NVMe/PCIe/NVLink (GPUDirect Storage — §2.2), một quyết định của chương này.

---

## 8. Đọc tiếp & bài tập

- Mạng ngoài rack: **1.7** · CXL memory: **1.3** · Passthrough/IOMMU/TEE: **1.8** · Collective & topo cho training: **12.4**
- **Bài tập 1:** Trên máy bạn: `nvidia-smi topo -m`. Đếm bao nhiêu cặp GPU là SYS/PHB (tệ) vs NV (tốt). Nếu không có GPU: `lspci -vv` — mỗi thiết bị đang chạy LnkSta bao nhiêu lane, đúng cap chưa?
- **Bài tập 2:** Đo `ib_write_bw` (hoặc iperf3 -P8) giữa 2 máy, rồi bật thêm stream song song tới khi tổng không tăng — đó là bão hoà thật của đường; so với con số trên hộp.
- **Bài tập 3:** Vẽ ngân sách lane của một máy chủ bạn quản lý (theo `lspci -t`). Còn dư bao nhiêu lane? Đủ cho một card CXL 2 năm nữa không?
