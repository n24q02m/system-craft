# 1.8 — Ảo hoá, cloud, TEE

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.3 (NUMA) · 1.6 (PCIe/NIC).

**Sợi chỉ đỏ:** *Mua máy hay thuê máy ảo cloud — đánh đổi thật là gì, và 'chồng vận hành cloud đọc được dữ liệu của tôi' phải lo tới đâu?* — trả lời: thuê máy ảo đổi tiền lấy elasticity và thêm một lớp trung gian — hypervisor; còn câu "operator cloud có đọc được dữ liệu của tôi không" trả lời bằng phần cứng (TEE) hoặc bằng kiến trúc (mã hoá phía client). Câu hỏi để lại cho chương sau: *Từ hai máy trở đi là hai cái đồng hồ — 'đơn đặt lúc 09:59:59' nghe ở máy nào, và lệch giờ gây họa gì?*

**Thuật ngữ sẽ gặp:** *hypervisor* — phần mềm dựng máy ảo trên máy thật; *vCPU* — một phần CPU vật lý được cắt cho máy ảo; *VM exit* — lần máy ảo phải nhường lại cho hypervisor xử: mỗi lần là tiền; *virtio/SR-IOV* — hai cách nối thiết bị ảo vào thật, đổi độ linh hoạt lấy hiệu năng; *TEE/enclave* — vùng tính toán kín ngay trên máy của người khác; *noisy neighbor* — hàng xóm cùng máy ăn mất tài nguyên của bạn.

**Ví dụ mở đầu:** Hai instance "cùng loại" của DM ở hai availability zone benchmark chênh 15% — khách hỏi vì sao, không ai trả lời nổi. Cloud không bán bạn một máy: nó bán một phần máy thật, chia với những hàng xóm không biết mặt. Biết lớp trung gian tồn tại là điều kiện để đo đúng, đàm phán được và biết khi nào nên tự mua máy.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chọn máy ảo / container / bare-metal cho workload này | Tôi cần isolate gì: process, kernel, hay phần cứng? |
| 2 | Ảo hoá thiết bị: virtio hay SR-IOV passthrough | Tôi cần live-migrate hay tối đa băng thông? (không có cả hai) |
| 3 | Có đặt dịch vụ nhạy cảm vào TEE không | Tôi bảo vệ chống ai — operator cloud, tenant khác, hay cả chuỗi cung ứng? |
| 4 | Chi phí ảo hoá của tôi là bao nhiêu và ai trả | Overhead ~0–10%: nằm ở đâu, khi nào đáng? |

---

## 2. Cơ chế

### 2.1 Ba lớp isolate, ba hứa hẹn khác nhau

```
Container    : chia kernel — nhanh (ms), nhẹ, cách ly YẾU (namespace/cgroup → 2.x)
VM           : mỗi kernel riêng — chậm hơn (s), nặng hơn, cách ly MẠNH (VT-x/EPT)
Bare-metal   : không cách ly — nhanh nhất, ops thủ công
```

Container không phải "VM nhẹ" — nó chia kernel với host: một kernel panic/rce chạm tất cả. VM cho ranh giới lỗi thật (fault isolation), container cho ranh giới **gói phần mềm**. Câu đúng không phải "container hay VM" mà "cần ranh giới loại nào" — nhiều hệ thống dùng cả hai (VM làm sandbox chứa nhiều container).

### 2.2 VT-x/EPT: phần cứng đỡ gánh điều khiển bộ nhớ

Không có EPT (Extended Page Tables), mọi truy cập bộ nhớ khách đều thoát ra hypervisor dịch tay (shadow page table — chậm hơn nhiều lần). Với EPT, phần cứng đi qua **2 bảng** (guest virtual → guest physical → host physical): gần như native cho CPU-bound, nhưng mỗi miss đắt hơn — nên workload bộ nhớ lớn (DB lớn, cache lớn) vẫn thấy vài % khác biệt (I).

Ba nguồn overhead thật của VM:
1. **VM exit** — hủy giao guest sang host (I/O, interrupt, hố lệnh đặc biệt): 1–10 µs mỗi lần (I); workload I/O dày hoặc clock interrupt cao thì cộng dồn;
2. **EPT multi-level walk** (mục trên);
3. **Thiết bị ảo hoá** (mục sau).

### 2.3 virtio vs SR-IOV: không có bữa trưa miễn phí

- **virtio (paravirtual):** guest chạy driver "biết mình đang ảo", đẩy/vào hàng đợi chia sẻ — mềm dẻo: **live-migrate được**, snapshot được, filter được. Chi phí: CPU host đóng gói/giao (vhost), throughput bị trần bởi 1–2 lõi.
- **SR-IOV (passthrough):** NIC/GPU cắt VF, gán thẳng vào VM qua IOMMU — gần native throughput, gần-zero CPU host. Chi phí: **mất live-migrate** (bộ nhớ thiết bị không thể snapshot), topology gắn chặt máy vật lý.

Đây là một trong những trade-off sạch nhất của ngành: **mềm dẻo vận hành đổi hiệu năng**. Cloud lớn chạy tự động hoá quanh virtio chính vì sống sót của fleet phụ thuộc migrate; HPC/AI thuê bare-metal hoặc SR-IOV vì cần băng thông và không muốn phụ thuộc sao lưu nóng.

### 2.4 TEE: tính toán kín trên máy người khác

Ba họ TEE máy chủ:
- **Intel TDX** (máy ảo trust domain) và **AMD SEV-SNP** (mã hoá RAM VM, guest xác minh host không đọc được): chạy workload thường trong vùng kín; chứng minh qua **attestation** (measurement ký).
- **NVIDIA confidential GPU (Hopper/Blackwell, mode "confidential computing")**: mã hoá dữ liệu qua PCIe vào VRAM — chống operator/host-read; với chuỗi AI (→12.x) đây là điều kiện để chạy model/dữ liệu nhạy cảm trên hạ tầng thuê.
- **TEE vi kiến trúc (SGX enclave)**: thư viện nhỏ, đã thu hẹp vai trò trên server sau nhiều side-channel (→14.11) — dùng cho secret cụ thể hơn là cả ứng dụng.

Câu hỏi thiết kế: **chống ai?** TEE chống operator/mất kiểm soát vật lý; nó không chống code bugs trong enclave, không chống side-channel mọi loại, và không thay thế mã hoá at-rest/in-transit (→10.5). Kèm chi phí: TEE/SEV-SNP thường ~0–7% (I), confidential GPU có thể ~10–30% tuỳ workload (I) — đo trước khi mặc định.

### 2.5 Chi phí ảo hoá tổng thể & bẫy đa thuê

Bảng bậc (I, CPU-bound → I/O-bound):

| Workload | Overhead VM (virtio) | Ghi chú |
|---|---|---|
| Compute thuần | 0–2% | gần như native |
| Web/API vừa | 2–5% | network softirq |
| DB nặng I/O, fsync dày | 5–15% | exits + queueing kép |
| Network/pps cao | 5–20% | trừ khi SR-IOV/DPU |

Và "noisy neighbor" — Cloud bản chất là máy chung: CPU steal (→2.3), băng thông burst bị throttle (token bucket của hypervisor), cache pollution (→1.2). Kinh điển: cùng instance-type chạy nhanh chậm khác nhau theo host — **đo theoTopology-aware placement** (placement group) hoặc chạy lại benchmark khi đổi máy.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| VM exit | ~1–10 µs | I | I/O, interrupt |
| Boot container / VM | ms / s | I | khác biệt căn bản |
| Overhead CPU-bound VM | 0–2% | I | |
| Overhead I/O-dense VM | 5–15% | I | virtio, không SR-IOV |
| SR-IOV throughput | ~native | I | mất live-migrate |
| TDX/SEV-SNP overhead | ~0–7% | I | theo Intel/AMD công bố + đo ngoài |
| Confidential GPU overhead | ~10–30% | I | tuỳ workload; đo |

---

## 4. Suy luận kiến trúc

- **S1:** Ranh giới isolate là quyết định **an ninh + độ bền**, không phải hiệu năng: chọn theo "lỗi gì lan tới đâu", hiệu năng là hoá đơn theo sau.
- **S2:** Tham số trụ: exit/s, steal%, network pps mỗi lõi, chi phí migrate (thời gian đồng bộ bitmap).
- **S3:** virtio vs SR-IOV; TEE vs mã hoá ứng dụng; multi-tenant gộp vs dedicated — mọi lựa chọn ở tầng này đều là tiền đổi tính chất, không phải tiền đổi số.
- **S4:** Chiplet + CXL + accelerator đang làm "máy vật lý" to hơn (rack logic — NVL72, →1.6): ảo hoá dịch từ "máy chủ" sang "pod tài nguyên"; API orchestration (→9.x) theo kịp chậm hơn thực tế.
- **S5:** Attestation đang trở thành glue của supply-chain (ứng dụng → OS → model → GPU measurement) — kỹ năng đọc/verify attestation sẽ phổ biến như đọc cert TLS hôm nay.
- **S6:** Khi "máy ảo chậm", hỏi: exits, EPT, hay thiết bị ảo? Ba loại ba thuốc (mục 5).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Steal% cao trên cloud VM | Noisy neighbor cùng host | `top` (st), `vmstat`; đổi máy đối chứng | §2.5 |
| VM I/O chậm hơn bare-metal 2× | virtio + vhost đơn lõi chạm trần | `perf` vhost thread; RSS/multiqueue config | §2.3 |
| p99 nghẽt theo chu kỳ 1s | Interrupt/vmexit dồn (timer tick) | `perf kvm stat` | §2.2 |
| Migrate failed liên tục | VF passthrough gắn máy | checklist thiết bị; bỏ SR-IOV | §2.3 |
| Enclave chậm bất thường | TEE overhead + page fault trên path mã hoá | đo A/B trong/out TEE | §2.4 |
| Benchmark khác nhau giữa 2 máy "giống nhau" | Host khác nhau (steal, cache, NUMA) | `lscpu`, `numactl -H` hai máy so | §2.5 |

---

## 6. Cách đo

```bash
# KVM exits theo lý do
perf kvm stat live -p <pid_qemu>

# Steal trên cloud
grep -E 'cpu ' /proc/stat    # cột steal (thứ 8)
mpstat 1                     # %steal

# So sánh thật: 2 máy, cùng benchmark, 3 lần
# (đây là cách duy nhất tin được cloud instance của bạn)

# IOMMU groups (trước khi passthrough)
for g in /sys/kernel/iommu_groups/*; do echo $g; ls $g/devices/; done

# Attestation
# TDX: td attestation qua tsme/SGX SDK tuỳ gen; SEV-SNP: sev-guest device + report
```

Nguyên tắc: trên hạ tầng thuê, **A/B theo máy là thử nghiệm chuẩn vàng** — mọi kết luận "loại instance này nhanh" chỉ đúng với máy bạn vừa đo, hôm nay.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay TEE cho dữ liệu nhạy cảm:** mã hoá ứng dụng (E2E, field-level — →10.5) + key không nằm trên host đó (KMS ngoài, →10.3); TEE cho phần "cần tính toán trên dữ liệu mờ". **Thay VM isolate:** gVisor/Kata (container có sandbox kernel) — trung gian tốt cho untrusted code (→9.6 sandbox multi-tenant). **Thay tự vận hành:** Cloud managed services đổi chi phí biên lấy ops-nhẹ — quyết định bằng TCO 3 năm, không bằng giá bảng.

Năm thấu kính:
- **Kinh tế:** Overhead ảo hoá 5% trên fleet 1.000 máy = 50 máy — thời gian dev 6 tháng; chi phí đó phải có chủ sở hữu tên trong quyết định.
- **Vận hành:** Live-migrate là khoản bảo hiểm dịch vụ (patch host không restart) — giá của nó chính là virtio; chỉ bỏ khi thật sự cần băng thông.
- **An ninh:** Mô hình đe đồng thời: cloud operator không đáng tin (TEE) nhưng TEE cũng không miễn nhiễm side-channel (→14.11) — chống đến đâu, ghi rõ trong threat model (→10.1).
- **Lịch sử:** 1960s IBM CP-40 đã có VM; 2000s "ảo hoá đã chết" (đùa của EMC); 2010s container "giết VM"; 2020s confidential VM + sandbox hồi sinh — bài học: isolate quay vòng mô hình, không mất đi.
- **Người dùng:** Người dùng không biết mình chạy trong VM; họ chỉ biết "hôm qua nhanh hôm nay chậm" — trên cloud, đó thường là topology/neighbor, và chương này dạy cách chứng minh thay vì đoán.

---

## 8. Đọc tiếp & bài tập

- Cgroup/namespace (chương container scheduler): **2.1–2.3** · Sandbox multi-tenant: **9.6** · Mã hoá & key: **10.3, 10.5** · Side-channel: **14.11**
- **Bài tập 1:** Trên KVM host, chạy `perf kvm stat live` trong lúc workload chạy; lý do exit nào nhiều nhất? Đổi multiqueue/RSS rồi đo lại.
- **Bài tập 2:** Thuê 2 instance cùng loại ở 2 AZ, benchmark CPU + mạng 3 lần mỗi máy. Ghi chênh lệch — nếu > 10%, viết vào sổ tay placement của team.
- **Bài tập 3:** Viết threat model 1 trang: dữ liệu gì của bạn cần chống operator cloud? Nếu câu trả lời là "không gì" — bạn vừa tiết kiệm được cả một lớp phức tạp TEE.
