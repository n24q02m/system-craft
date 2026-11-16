# 2.8 — eBPF: Lập trình hoá Kernel an toàn

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Quan sát · Hạn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 2.6 (netstack).

**Sợi chỉ đỏ:** *Muốn nhìn thấy kernel đang làm gì mà không sửa code — eBPF mở được gì?* — trả lời: eBPF cho phép nạp chương trình nhỏ đã được kiểm chứng an toàn, chạy ngay trong kernel — nhìn thấy mọi syscall, mọi gói tin, mà không sửa code ứng dụng và không cho kernel crash. Câu hỏi để lại cho chương sau: *Hiểu máy và OS rồi — DM viết lại bằng ngôn ngữ nào, và đồng thời cùng GC dạy bài học đầu tiên gì?*

**Thuật ngữ sẽ gặp:** *eBPF* — khung nạp chương trình nhỏ chạy an toàn trong kernel; *verifier* — duyệt từng đường thực thi trước khi cho chạy; *attach point* — chỗ cắm: kprobe, tracepoint, uprobe, XDP; *bpftrace* — ngôn ngữ tra cứu kernel một dòng kiểu SQL; *CO-RE* — cùng một binary chạy trên nhiều phiên bản kernel; *JIT* — biên dịch sang mã máy ngay khi nạp.

**Ví dụ mở đầu:** Khách phàn nàn "đôi lúc chậm" lúc 2 giờ sáng, log không thấy gì. Một dòng bpftrace đo thời lượng mọi openat() của process DB — thấy đỉnh đúng 2h: backup quét thư mục. Không restart, không deploy, không sửa code — thứ vừa làm được việc đó là eBPF.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Dùng eBPF cho quan sát thay agent sidecar/kernel module? | Tôi trả 1 chương trình chạy trong kernel thay N agent userspace? |
| 2 | Dùng cho datapath (XDP/tc — →2.6) khi nào | Sau khi đã thất bại với các cách thường? |
| 3 | Ai được phép nạp eBPF vào cụm (signature/allowlist) | Chương trình chạy trong kernel = quyền gần tuyệt đối — ai giữ chìa? |
| 4 | Build quản lý phiên bản kernel (CO-RE) | Same binary chạy trên 5.x–6.x — tôi đã kiểm chứng chưa? |

---

## 2. Cơ chế

### 2.1 Mô hình: verify trước, JIT sau

eBPF nạp **bytecode** vào kernel; **verifier** chứng minh an toàn trước khi chạy: mọi đường đều thoát (không treo), mọi truy cập bộ nhớ đều kiểm tra bounds, không vượt số lệnh (1M từ 5.2+). Sau đó **JIT** biên dịch ra lệnh máy — chạy gần native. **Maps** (hash/array/ring/perf) là kênh dữ liệu với userspace. **Helpers** cung cấp API kernel giới hạn. Ràng buộc để nhớ: chương trình **stateless giữa các lần gọi** (trừ map), **không gọi tùy tiện kernel** — đó chính là lý do "an toàn để chạy trong kernel".

### 2.2 Attach points: bốn họ công việc

| Họ | Attach | Việc |
|---|---|---|
| Tracing | kprobe/uprobe/tracepoint | đo hàm bất kỳ (kernel/user), latency, flame |
| Networking | XDP/tc/cgroup-hooks | drop/redirect/rewrite gói (→2.6) |
| Observability nền | perf-event/BPF iterator | metric theo process |
| Security/LSM | BPF LSM | chính sách truy cập |

### 2.3 CO-RE & BTF: một binary, mọi kernel

**BTF** (BPF Type Format) mô tả cấu trúc dữ liệu kernel; **CO-RE** (Compile Once – Run Everywhere) dùng BTF để **tự chỉnh** truy cập field theo layout kernel đích (relocations). Trước CO-RE: mỗi kernel một build (headers exact). Sau (5.x+): bpftrace/libbpf binary chạy đa kernel — điều kiện để shipping công cụ production (Falco, Cilium, Pixie) mà không phải compile tại chỗ.

### 2.4 Chương trình một dòng: bpftrace là "SQL của kernel"

```bash
# Latency của openat() theo process — 30 giây sở hữu câu trả lời
bpftrace -e 'kprobe:__x64_sys_openat { @start[tid] = nsecs; }
             kretprobe:__x64_sys_openat /@start[tid]/ {
               @us = hist((nsecs - @start[tid]) / 1000); delete(@start[tid]); }'

# Ai đang chặn I/O lâu? (kèm off-CPU time)
bpftrace -e 'tracepoint:block:block_rq_issue { @[comm] = count(); }'
```

Công cụ trước khi viết: `bpftrace`, BCC (`biolatency`, `tcpretrans`, `offcputime` — dùng ở 2.3–2.6), `perf` (đã dùng eBPF dưới mui xe). **Đừng viết C eBPF khi bpftrace trả lời được** — đó là quy tắc 80/20 của ngành.

### 2.5 Giới hạn thật (để khỏi thất vọng)

- Verifier từ chối code "hợp lệ nhưng không chứng minh được" — viết lại vòng lặp vẫn khó ở vài pattern (bounded loops ổn từ 5.3);
- Không sửa được mọi thứ: gói đã vào stack thì kịp tốn CPU (XDP sớm hơn — →2.6);
- Kernel ≥ 4.18–5.x cho phần lớn use production; từng distro tắt io_uring/bpf qua sysctl — inventory kernel cụm trước khi hứa;
- Chi phí mỗi event ~tens–hundreds ns (I) — ở triệu event/s, overhead thành %CPU thật: đo trước khi theo dõi "mọi thứ".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Verifier limit lệnh | 1M (5.2+) | V | từng 4096 |
| Overhead/program-call | ~tens–hundreds ns | I | |
| BTF/CO-RE ổn định | 5.x+ | V | |
| Bounded loops | 5.3+ | V | |
| kprobe stability | theo symbol, hay đổi | I | tracepoint ổn hơn |

---

## 4. Suy luận kiến trúc

- **S1:** eBPF đưa chi phí quan sát từ "sidecar + log" về "sự kiện kernel trực tiếp" — nhưng vẫn là chi phí; nguyên tắc "đo ít, đo đúng chỗ" không đổi.
- **S2:** Tham số trụ: số chương trình/attach điểm, event rate, CPU % của các agent eBPF (thay sidecar CPU).
- **S3:** eBPF quan sát đổi "không phải deploy app" lấy "phải quản kernel version"; eBPF datapath đổi latency lấy rủi ro ở tầng privileged nhất.
- **S4:** Hệ sinh thái đã dồn về eBPF làm nền (Cilium networking, Falco security, Pixie/Parca profiling) — kỹ năng đọc program + maps là kỹ năng platform kỷ niệm 2020s.
- **S5:** eBPF làm mờ biên kernel/userspace — cùng lúc mở bề mặt **chính trị quyền hạn** (ai nạp được = ai điều khiển máy) — khóa bằng signature/GP — mục 1 bảng quyết định của chương này.
- **S6:** Khi cần nhìn thấy mà không thể sửa code, eBPF là đáp án mặc định của thập kỷ — còn khi cần thay đổi hành vi, ưu tiên userspace (→8.x retry/timeout) trước khi nhảy vào datapath.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Verifier reject program | pattern không chứng minh được | log verifier; viết lại bounded | §2.1, §2.5 |
| Tool chết sau upgrade kernel | kprobe symbol đổi / thiếu BTF | `bpftool btf dump`; CO-RE check | §2.3 |
| CPU cao khi bật tracing | event rate quá lớn | giảm attach; sample thay vì đếm từng | §2.5 |
| Không nạp được (EPERM) | lockdown/unprivileged_bpf_disabled | sysctl; `dmesg` | §2.5 |
| Map đầy mất events | ring buffer tràn | tăng size; giảm producer | §2.1 |

---

## 6. Cách đo

```bash
# Có gì đang chạy trong kernel của tôi?
bpftool prog show
bpftool map show

# Kernel có BTF không (CO-RE được chưa)?
ls /sys/kernel/btf/vmlinux

# Quyền nạp?
sysctl kernel.unprivileged_bpf_disabled

# Bắt đầu từ bpftrace one-liners (xem §2.4) — rồi mới tính tới viết C
```

Nguyên tắc: **kiểm kê trước khi tin** — `bpftool prog show` cho biết cụm đang chạy bao nhiêu chương trình của ai; không ai biết câu trả lời thì cụm không có chủ.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay eBPF tracing:** static instrumentation (metric trong app — vẫn là nguồn thật nhất), `perf` (đủ cho profile định kỳ), strace (một process, chấp nhận chậm). **Thay eBPF datapath:** kernel stack + sysctl (chương 2.6) đủ cho 95%; eBPF-XDP chỉ đáng khi pps/ddos thực sự.

Năm thấu kính:
- **Kinh tế:** Thay 5 agent sidecar/node bằng 1 daemon eBPF: tiết kiệm CPU+tồn tại hình thức — nhưng tính cả chi phí "nâng cấp theo kernel" trước khi ghi "tiết kiệm".
- **Vận hành:** Mọi node cần kernel đủ mới + BTF — inventory kernel là điều kiện tiên quyết của mọi dự án eBPF (và thường là lý do dự án dời lại 6 tháng).
- **An ninh:** eBPF vừa là công cụ phòng thủ (Falco) vừa là vũ khí sau xâm nhập (rootkit eBPF có tiền lệ) — kiểm soát quyền nạp là biên giới thật.
- **Lịch sử:** Từ "filter gói" (1992, BPF cổ điển) tới "vết chương trình" (2014+): một ý tưởng 30 năm tuổi trở thành nền của observability/networking/security — vì ý tưởng đúng (verifier + JIT) chỉ chờ phần cứng/kernel theo kịp.
- **Người dùng:** Người dùng không thấy eBPF; họ thấy "metric tự sinh ra dù app không code gì" — và đó chính là lời hứa chương này giữ.

---

## 8. Đọc tiếp & bài tập

- XDP/netstack: **2.6** · Quan sát toàn cảnh: **11.1** · Security runtime: **10.4** · Cilium/mesh: **9.4**
- **Bài tập 1:** Chạy `bpftool prog show` trên 3 node. Ai đang chạy gì trong kernel bạn? Ghi kết quả — đó là tài sản (hoặc nợ) chưa ai kiểm kê.
- **Bài tập 2:** Dùng bpftrace đo phân phối `openat()` của DB process 5 phút. Có cái đuôi > 1 ms không? Nếu có — bạn vừa tìm được câu hỏi cho 1.4/2.4.
- **Bài tập 3:** Viết chính sách 1 trang: ai được ký/nạp chương trình eBPF lên cụm, theo đường nào. Không có văn bản đó, câu trả lời mặc định là "ai cũng".
