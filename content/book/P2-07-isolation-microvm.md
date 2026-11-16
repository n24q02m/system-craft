# 2.7 — Cô lập: Namespaces, seccomp, Container vs MicroVM

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.8 (ảo hoá) · 2.3 (cgroup).

**Sợi chỉ đỏ:** *Chạy code của người khác (plugin duyệt ảnh món ăn) — cách ly tới đâu là đủ?* — trả lời: container là namespaces + cgroups + filesystem trên cùng một kernel — nhẹ, nhưng vẫn chung tường nhà; khi chạy code không tin được thì thang cô lập phải lên tới microVM. Câu hỏi để lại cho chương sau: *Muốn nhìn thấy kernel đang làm gì mà không sửa code — eBPF mở được gì?*

**Thuật ngữ sẽ gặp:** *namespace* — làm process thấy hệ thống "của riêng mình": PID, mạng, mount; *cgroup* — giới hạn tài nguyên của nhóm process; *capability* — quyền root cắt nhỏ theo từng loại việc; *seccomp* — lọc syscall process được phép gọi; *microVM* — máy ảo siêu nhẹ kiểu Firecracker, khởi động trong chục miligiây; *rootless* — chạy container mà không cần root thật.

**Ví dụ mở đầu:** DM cho phép quán tải logo và plugin in bill riêng. Ai đó viết "plugin in bill" và mọi người hồ hởi — cho tới khi có người hỏi: code của khách chạy trên máy nào, với quyền gì? "Trong container" chưa phải câu trả lời khi container vẫn dùng chung kernel với toàn bộ phần thanh toán.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Mức cô lập cho code không tin cậy: container / gVisor / Kata / Firecracker | Tôi chống lỗi hay chống tấn công? Chi phí chấp nhận được là bao nhiêu %? |
| 2 | Bộ capabilities & seccomp profile tối thiểu cho workload | Container của tôi chạy với quyền gì VẬT SỰ — có ai đọc lại chưa? |
| 3 | Chạy sidecar trong cùng pod hay microVM riêng | Ranh giới lỗi đặt ở đâu giữa "cùng vận mệnh" và "cách ly"? |
| 4 | Rootless container / user namespace cho CI & tenant | Cho phép chạy mà không cho quyền? |

---

## 2. Cơ chế

### 2.1 Container là gì: namespaces + cgroups + filesystem (nhưng vẫn chung kernel)

Tám **namespaces** cắt "khung nhìn" của process: `mnt` (filesystem), `pid` (thấy process nào), `net` (interface/route/iptables riêng), `uts` (hostname), `ipc`, `user` (uid map — root trong ≠ root ngoài), `cgroup`, `time`. Cộng `cgroups` (→2.3/2.4) giới hạn tài nguyên, `overlayfs` tạo image lớp lớp, và **pivot_root** nhốt root filesystem. Tất cả vẫn dùng **một kernel** — nên một lỗ hổng kernel = lỗ hổng chung (khác VM ở 1.8 §2.1).

### 2.2 Capabilities & seccomp: hai lớp mỏng đáng giá

Mặc định Docker/containerd vẫn cấp cho container một bộ capabilities khá rộng và **không** thu khi app chạy ổn. Bài tập vệ sinh định kỳ: `capsh --print` trong container của bạn; drop hết trừ đúng cái cần (`NET_BIND_SERVICE` cho cổng thấp...). **seccomp-bpf** lọc syscall theo profile (mặc định Docker chặn ~60 calls antiquated); thêm `no_new_privs` chặn leo thang. Đây là lớp rẻ nhất (overhead ~0) nhưng hay bị bỏ qua vì "app vẫn chạy" — app vẫn chạy không nghĩa là attack vẫn thất bại.

### 2.3 Thang cô lập: từ container tới microVM

| Mức | Cơ chế | Overhead | Chống được gì | Không chống |
|---|---|---|---|---|
| Container | namespaces+cgroups | ~0% | lỗi app, tranh tài nguyên | kernel 0-day, container escape |
| gVisor (runsc) | kernel user-space chặn syscall | ~5–25% CPU-heavy | syscall surface thu hẹp mạnh | phần còn lại của host? |
| Kata | VM nhẹ mỗi container | ~giây boot | kernel riêng (như VM 1.8) | VM escape/hypervisor |
| Firecracker | microVM tối giản (~125ms boot) | thấp | như VM + tối thiểu surface | hypervisor |

Quy tắc đáng nhớ: **nội bộ tin cậy → container; code người dùng tải lên (FaaS, plugin) → Firecracker/gVisor; tuân thủ chặt (multi-tenant tài chính/y tế) → Kata/VM.** AWS Lambda/Fargate chạy trên Firecracker từ 2018/2019 (V) — bằng chứng quy mô cho microVM.

### 2.4 Rootless & user namespace

Chạy container bằng user thường: uid map (user namespace) làm "root trong container = user ngoài". Bớt được cả lớp "daemon root là mục tiêu" (những sự cố Docker/CVE daemon history). Chi phí: một số volume/network driver cần cấu hình thêm; K8s support qua `userNamespaces` (beta 1.30+/GA hoá dần — kiểm tra version cụm). CI build image là nơi đáng áp đầu tiên: build code không tin cậy mà daemon root — tổ hợp xấu kinh điển.

### 2.5 Ranh giới sai lầm thường gặp

- "Có container = an toàn": container là **đóng gói**, không phải **bunker**; escape qua kernel CVE có tiền lệ (Dirty Pipe 2022, Dirty COW 2016 (V)).
- Umount/network namespace dùng chung cho sidecar "tiện": sidecar proxy lỗi → đoạt traffic của container chính — ranh giới phải theo **độ tin cậy**, không theo "tiện deploy".
- Secret mount vào mọi container "cho chắc": mỗi mount là một bản sao dữ liệu nhạy — thu hẹp theo 10.6.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Overhead container vs bare | ~0% | I | trừ storage/network driver |
| gVisor overhead | ~5–25% syscall-heavy | I | |
| Firecracker boot | ~125 ms | V | paper/production AWS |
| Kata boot | ~1 s/giây | I | katacontainers docs |
| Số syscall blocked Docker default | ~60 | I | profile lịch sử |
| Container escape tiền lệ | Dirty COW/Dirty Pipe | V | kernel-bound |

---

## 4. Suy luận kiến trúc

- **S1:** Mức cô lập là quyết định **threat model** (→10.1), không phải mặc định kỹ thuật; mọi sự tiện của "chạy chung" đều là nợ phải trả khi có sự cố.
- **S2:** Tham số trụ: capabilities thật sự (audit định kỳ), syscall bị từ chối (seccomp alerts), mật độ tenant/vm.
- **S3:** Mỗi bậc thang cô lập đổi overhead lấy bề mặt tấn công nhỏ hơn; không có bậc "miễn phí và tuyệt đối" — kể cả VM (→1.8 side-channel).
- **S4:** FaaS/plugin platform đẩy microVM thành chủ lưu — "boot máy ảo mỗi request" từ vô lý (2010) thành bình thường (Firecracker) vì boot về ms.
- **S5:** User namespace/rootless đang từ "nice to have" thành mặc định của stack mới (podman đã vậy; K8s theo) — kế hoạch dài hạn nên đặt nó là đích.
- **S6:** Khi gỡ sự cố "lan sang tenant khác", hỏi ranh giới nào đã thất bại: namespace, cgroup, network policy (→9.6), hay chính heuristic "tin tưởng lẫn nhau"?

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Container "nhìn thấy" process/host khác | Namespace config lệch (shared pid/hostNetwork) | `lsns`; `kubectl get pod -o yaml` | §2.1 |
| App cần quyền lạ để chạy | Capabilities bị drop quá tay | audit log cap; thêm đúng 1 cái | §2.2 |
| Seccomp kill syscall mới sau upgrade | Profile cũ không cập nhật | runtime log "seccomp"; profile diff | §2.2 |
| Node bị thoát qua container | Kernel CVE (escape) | kernel patch audit; `uname -r` | §2.5 |
| CI build bị cài mã lạ vào image | Build không tin cậy + daemon root | chuyển rootless/podman | §2.4 |

---

## 6. Cách đo

```bash
# Trong container: tôi là ai, tôi có gì?
capsh --print                     # capabilities
grep Seccomp /proc/self/status    # 2 = filter đang bật
lsns -p <pid>                     # namespaces đang chia sẻ

# So sánh profile seccomp trước/sau upgrade
docker info | grep -i seccomp     # profile mặc định

# Trên node: có bao nhiêu "thế giới" đang chạy?
lsns --type user | wc -l
crictl pods -o wide               # mật độ pod/node
```

Nguyên tắc: **audit cô lập bằng câu hỏi tấn công** ("nếu tôi là process này, tôi phá được gì?") — metric tài nguyên không trả lời được câu đó.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay gVisor/Kata (khi p99 là ưu tiên số một):** tách node vật lý cho tenant không tin cậy (đổi chi phí máy lấy độ đơn giản); hoặc pipeline hoá — code người dùng chạy batch một lần trong VM rồi huỷ (không giữ state). **Thay rootless ngay:** giảm bề mặt bằng không cấp docker socket (mấu chốt của nhiều sự cố supply-chain — →10.4), secret tối thiểu (→10.6).

Năm thấu kính:
- **Kinh tế:** Overhead gVisor 10% trên fleet 500 máy = 50 máy — nhưng một sự cố thoát container multi-tenant thường đắt hơn cả fleet; bài toán bảo hiểm, không phải hiệu năng.
- **Vận hành:** Audit capabilities/seccomp nửa năm một lần (sau mỗi lần "thêm cho chạy được" là lúc profile mục nát nhất).
- **An ninh:** Namespace là lớp đầu, không phải lớp cuối — bảo vệ theo chiều sâu: capabilities → seccomp → LSM/AppArmor → MAC network policy → cuối cùng là microVM.
- **Lịch sử:** Jails (FreeBSD 2000) → Solaris Zones (2004) → LXC (2008) → Docker (2013) → microVM (2018): mỗi lần là "đóng gói tiện hơn" xen kẽ "cô lập chắc hơn" — vòng lặp chưa có dấu hiệu dừng.
- **Người dùng:** Người dùng chỉ hỏi một câu: "dữ liệu của tôi có nằm chung với người khác không?" — chương này là bản dịch kỹ thuật của câu trả lời.

---

## 8. Đọc tiếp & bài tập

- VM/TEE: **1.8** · Sandbox multi-tenant ở tầng orchestration: **9.6** · Threat model: **10.1** · Supply chain: **10.4**
- **Bài tập 1:** Với container production quan trọng nhất của bạn: `capsh --print`. Mỗi capability chưa dùng — xoá, redeploy, xem gì vỡ. Lặp lại tới khi danh sách ngắn.
- **Bài tập 2:** Đếm workload trong hệ thống chạy code không tin cậy (FaaS, plugin, render file user). Với mỗi cái, trả lời: ranh giới là gì? Nếu câu trả lời là "container" — viết kế hoạch microVM.
- **Bài tập 3:** Bật audit mode cho seccomp trong staging một tuần; danh sách syscall bị gọi nhưng không có trong profile là "nợ ẩn" của bạn với lần upgrade kế tiếp.
