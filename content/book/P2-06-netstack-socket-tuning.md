# 2.6 — Linux Network Stack & Socket Tuning (somaxconn, conntrack, XDP)

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền hệ điều hành · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 2.5 · 1.7 (RTT).

**Sợi chỉ đỏ:** *Gói tin từ socket xuống card và ngược lại — netstack có chỗ nghẽn nào theo số lượng?* — trả lời: gói đi từ NIC qua ngắt, IP, TCP tới socket — mỗi chặng có hàng đợi và bể cạn riêng: backlog, cổng ephemeral, bảng conntrack; chỉnh đúng chặng thay vì mù quáng nâng sysctl. Câu hỏi để lại cho chương sau: *Chạy code của người khác (plugin duyệt ảnh món ăn) — cách ly tới đâu là đủ?*

**Thuật ngữ sẽ gặp:** *softirq* — nửa dưới xử gói của kernel, chia theo lõi; *backlog/somaxconn* — hàng đợi connection đã bắt tay chưa được app nhận; *TIME_WAIT* — trạng thái đóng của bên chủ động, giữ khoảng 60 giây; *conntrack* — bảng kernel theo dõi phiên, đầy thì từ chối gói mới; *BBR/cubic* — hai thuật toán kiểm soát tắc nghẽn; *XDP* — xử gói ngay tại driver, trước netstack.

**Ví dụ mở đầu:** Trưa cao điểm, một số request DM treo 3 giây rồi tự thành công. Không lỗi app: hàng đợi accept đầy vì app nhận chậm hơn tốc độ máy bắt tay — khách chờ ở một cánh cửa không ai nhìn thấy. Một dòng ss -lnt cho thấy Recv-Q chạm trần; chỉnh đúng con số ấy, sự cố "ma" biến mất.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Accept queue (somaxconn, backlog) theo tải thật | Recv-Q có chạm trần khi burst không? |
| 2 | TIME_WAIT policy (tw_reuse, port range) cho client nhiều outbound | Tôi cạn cổng ephemeral bao lâu nữa? |
| 3 | Conntrack table size + timeout cho NAT/proxy | Bảng đầy thì ai chết trước? |
| 4 | Congestion control (cubic/BBR) + buffer (tcp_rmem/wmem) | Đường của tôi lossy hay chỉ trễ — BDP đã đủ (→1.7)? |

---

## 2. Cơ chế

### 2.1 Đường đi của một gói: từ NIC tới socket

```
NIC → driver (NAPI poll) → softirq NET_RX → IP/TCP handler → conntrack/NAT
    → socket backlog → wakeup process (epoll — 2.5)
```

Ba hàng đợi không được nhầm:
1. **NIC RX ring** (driver) — tràn = drop ở `ethtool -S` (rx_dropped);
2. **Accept queue** (`somaxconn` ∩ backlog của listen()) — đầy = SYN OK nhưng ACK cuối bị bỏ → client thấy "connection timed out" sau 1 s (kinh điển "không connection refused mà timeout");
3. **Socket receive buffer** (`tcp_rmem`) — nhỏ → window đóng → throughput tụt (→1.7 BDP).

**RSS/RPS** trải softirq theo lõi (chia CPU network); **GRO** gộp gói trước stack (giảm pps xử lý). Không cấu hình chúng trên máy nhiều lõi + nhiều pps = để softirq đè 1 lõi ("CPU 1 luôn 100%").

### 2.2 TIME_WAIT và cạn cổng ephemeral

Kết nối chủ động đóng giữ cổng trong TIME_WAIT (60 s Linux) để gói trễ không phá phiên mới. Server đóng nhiều kết nối ngắn → hàng trăm nghìn TIME_WAIT (tốn bộ nhớ nhỏ, **bình thường** — đừng "chữa"); **client** outbound dồn (proxy, crawler, DB client) mới cạn 64k→28k cổng ephemeral per destination. Thuốc đúng: `tcp_tw_reuse=1` (chỉ áp cho outbound — an toàn với timestamp), nối lại connection (keep-alive pool — →4.2), hoặc `ip_local_port_range` rộng hơn. Thuốc sai (đừng): `tcp_tw_recycle` (đã xoá khỏi kernel — NAT phá), `SO_LINGER 0` (RST — phá dữ liệu).

### 2.3 Conntrack: bảng "đoán phiên" của NAT/firewall

Mọi gói qua iptables/nftables/IPVS/K8s Service đi qua **conntrack** — bảng ánh xạ (src,dst,proto,ports). Đầy (`nf_conntrack_max`, mặc định ~64k–256k theo RAM) → gói mới **drop âm thầm**: triệu chứng "kết nối lúc được lúc không", chỉ thấy trong `dmesg` ("table full, dropping packet"). Trên cụm K8s lớn đây là sự cố số một của node (→9.3). Thuốc: nâng max + hạ timeout các trạng thái không cần (`nf_conntrack_tcp_timeout_established` 5 ngày mặc định — quá dài cho dịch vụ ngắn), hoặc tách đường không cần NAT.

### 2.4 Congestion control: cubic vs BBR

- **cubic** (mặc định Linux): loss-based — giảm cửa sổ khi mất gói; tệ trên đường lossy (wifi/quang kém): cứ drop là tụt window;
- **BBR** (Google, 4.9+): đo băng thông × RTT thật để tính sending rate — không sợ loss, dùng tốt cho đường trễ cao/mất gói. Kết quả: throughput đường kém tăng nhiều lần (I).

**Lưu ý vận hành:** BBR khiên router middlebox không thấy loss có hành vi lạ; BBRv3 có tính công bằng tốt hơn (đang lên mặc định một số distro). Bật: `sysctl net.ipv4.tcp_congestion_control=bbr` (cần module) — đo trước/sau bằng iperf3 + RTT thật (→1.7).

### 2.5 XDP/eBPF: đường rẽ ngắn trước kernel

**XDP** chạy chương trình eBPF **ngay tại driver** — trước allocate skb: drop/redirect/rewrite với giá ~50–100 ns/gói (I). Use production: DDoS filter (drop trước khi tốn CPU), load balancing (redirect), custom protocol. **TC/eBPF** ở tầng traffic control: shaping/classification. Đây là lớp "lập trình hoá netstack" — nối sang 2.8; với 99% service, đúng vị trí của nó là **công cụ của platform team**, không phải của ứng dụng.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| somaxconn mặc định | 4096 (6.x); cũ 128 | V | Listen backlog ∩ |
| TIME_WAIT | 60 s | V | 2×MSL |
| Ephemeral range mặc định | ~28k–64k cổng | V | ip_local_port_range |
| nf_conntrack_max | 64k–256k theo RAM | V | full = drop âm thầm |
| Established timeout | 5 ngày | V | hạ cho service ngắn |
| XDP cost/gói | ~50–100 ns | I | driver mode |

---

## 4. Suy luận kiến trúc

- **S1:** Netstack là chuỗi hàng đợi — mọi sự cố đều là "hàng đợi nào đầy"; nhiệm vụ chẩn là đặt tên đúng hàng đợi, không phải "mạng chậm".
- **S2:** Tham số trụ: Recv-Q vs Send-Q của listen socket, drops (NIC/conntrack), retrans/s, pps mỗi lõi.
- **S3:** tw_reuse đổi ngữ nghĩa TIME_WAIT lấy cổng; BBR đổi công bằng lấy throughput; conntrack timeout đổi bộ nhớ lấy ngân sách phiên — ba đòn phải đo kèm tải thật.
- **S4:** 100/400G NIC làm pps vượt khả năng softirq 1 lõi — RSS/RPS/XDP từ "tuning" thành "bắt buộc" ở máy hiện đại.
- **S5:** Service mesh/sidecar nhân thêm conntrack hop — mỗi lớp proxy thêm một bảng có thể đầy (→9.3 mesh trade-off).
- **S6:** "Connection refused/timeout" là triệu chứng của **ba tầng khác nhau**: app (4.2), kernel (chương này), mạng vật lý (1.7) — chẩn theo dấu hiệu từ chối để phân tầng.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Connection refused/timeout khi tải cao | Accept queue đầy | `ss -lnt` (Recv-Q = Send-Q = trần) | §2.1 |
| Outbound lỗi "cannot assign port" | Cạn ephemeral (TIME_WAIT) | `ss -s`; netstat -tan count | §2.2 |
| Gói mất âm thầm sau NAT/Service | Conntrack đầy | `conntrack -C`; dmesg "table full" | §2.3 |
| 1 lõi 100% (si) khi tải mạng | softirq không trải (RSS/RPS) | `mpstat -P ALL`; /proc/interrupts | §2.1 |
| Throughput kém trên đường lossy | cubic loss-based | `ss -i` retrans; thử bbr | §2.4 |
| DDoS/scan đốt CPU | Không có XDP filter | ethtool -S rx lỗi; eBPF drop | §2.5 |

---

## 6. Cách đo

```bash
# Hàng đợi accept — chạy đúng lúc tải cao
ss -lnt sport = :443          # Recv-Q/Send-Q

# Toàn cảnh socket
ss -s                          # tổng: ESTAB/TIME_WAIT...
nstat -az | grep -iE 'retrans|drop|listen'   # counters TCP/IP

# Conntrack
conntrack -C                   # hiện dùng / max
dmesg | grep conntrack

# Drops theo thiết bị & hàng đợi
ethtool -S eth0 | grep -iE 'drop|err|fifo'
cat /proc/net/softnet_stat     # cột 2 = dropped (backlog)

# Phân bổ softirq
mpstat -P ALL 1                # %soft theo lõi
```

Nguyên tắc: **drop luôn được đếm ở đâu đó** — NIC, softnet, conntrack, accept queue; việc của bạn là biết chỗ nhìn, không phải đoán.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tuning somaxconn:** giảm burst (client retries có jitter — →8.5), connection pooling (→4.2), hoặc đặt LB/ingress trước (→9.4). **Thay nâng conntrack:** host network cho pod quan trọng (bỏ overlay), hoặc tách node cho traffic lớn — topology giải quyết cái mà sysctl chỉ trì hoãn. **Thay BBR:** sửa đường (→1.7 MTU/loss) — công bằng với mọi user của đường đó.

Năm thấu kính:
- **Kinh tế:** Một sysctl conntrack sai làm sập cụm 100 node — chi phí của "không ai sở hữu kernel tuning" là lớn nhất trong các chi phí bị bỏ quên.
- **Vận hành:** Mọi node nên export softnet drops + conntrack count — hai graph này dự báo 80% sự cố mạng của node.
- **An ninh:** TIME_WAIT/SYN flood là DoS cổ điển; SYN cookies bật sẵn (mặc định) + XDP là lớp phản ứng; rate limit ở LB (→9.4).
- **Lịch sử:** Tw_recycle bị xoá (2017→4.12) sau khi phá NAT — "tuning từ Internet cũ" là nợ kỹ thuật ẩn; kiểm tra tuổi của mọi sysctl bạn copy.
- **Người dùng:** "Trang lúc mở lúc không mở" — khi nghe câu này, hãy mở `ss -lnt` trước khi mở ticket với nhà mạng.

---

## 8. Đọc tiếp & bài tập

- TCP/TLS/HTTP trên socket: **4.1–4.2** · eBPF nền tảng: **2.8** · DNS trong K8s: **9.3** · LB edge: **9.4**
- **Bài tập 1:** Lúc tải cao nhất: `ss -lnt` cho cổng chính. Recv-Q chạm Send-Q chưa? Nếu bằng — somaxconn đã là giới hạn throughput của bạn.
- **Bài tập 2:** Đếm TIME_WAIT theo cặp (src:port→dst) bằng `ss -tan state time-wait`. Nếu một đích chiếm > 50% — đó là chỗ cần connection pool, không phải sysctl.
- **Bài tập 3:** `cat /proc/net/softnet_stat | awk '$2>0'` — đếm lõi đang drop. Con số khác 0 trên máy "bình thường" là việc cần giải thích hôm nay.
