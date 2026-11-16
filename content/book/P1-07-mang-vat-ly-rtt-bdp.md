# 1.7 — Mạng vật lý: quang, RTT, BDP, đệm

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.1 (thang thời gian, RTT).

**Sợi chỉ đỏ:** *Trong máy đã rõ — còn đoạn đường từ điện thoại khách tới server: RTT và băng thông ràng buộc gì?* — trả lời: ánh sáng trong thuỷ tinh đặt cận dưới cho RTT; BDP = băng thông × RTT là số byte đang bay trên đường tại một thời điểm — cửa sổ truyền nhỏ hơn BDP thì tự thắt cổ chai mình, dù đường trống. Câu hỏi để lại cho chương sau: *Mua máy hay thuê máy ảo cloud — đánh đổi thật là gì, và 'chồng vận hành cloud đọc được dữ liệu của tôi' phải lo tới đâu?*

**Thuật ngữ sẽ gặp:** *RTT* — thời gian một gói đi và về; *BDP* — bandwidth-delay product: số byte lấp đầy đường ống; *cửa sổ (window)* — số byte bên gửi được phép thả ra trước khi chờ xác nhận; *MTU* — kích thước gói lớn nhất trên đường; *PMTUD* — tự dò MTU, chết khi bị firewall chặn báo; *đệm switch* — chỗ đứng chờ của gói tại nút giao.

**Ví dụ mở đầu:** Sao chép dữ liệu DM sang Singapore: đường 10 Gbps, RTT 40 ms — copy file lớn chỉ đạt khoảng 100 MB/s dù đường trống trơn. Không mất gói: cửa sổ TCP mặc định (~4 MB) nhỏ hơn BDP (50 MB), nên bên gửi luôn chờ xác nhận. Một dòng sysctl — hoặc hiểu BDP ngay từ đầu.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Kích thước window/batch cho đường trễ đã biết | BDP của tôi là bao nhiêu byte? Tôi đã set window/parallelism theo đó chưa? |
| 2 | MTU & jumbo trong cụm | Tôi đổi gì lấy gì với MTU 9000? Ai không đọc được jumbo? |
| 3 | Thiết kế oversubscription của fabric | Tỉ lệ nghẽn ở đâu là chấp nhận được với workload tôi? |
| 4 | Đệm switch & chiến lược xếp hàng | Workload incast/microburst của tôi cần gì? |

---

## 2. Cơ chế

### 2.1 Ánh sáng trong thuỷ tinh: giới hạn vật lý đầu tiên

Tín hiệu trong sợi quang đi ~⅔ tốc độ ánh sáng (~200.000 km/s) → **~5 µs mỗi km một chiều** (V, bậc). Hệ quả: RTT Hà Nội–Singapore (~2.700 km cáp, không thẳng) ~14–20 ms lý thuyết, thực đo 30–60 ms (định tuyến, đệm, hàng chờ). Không phần mềm nào sửa được số này — chỉ có **dời dữ liệu đến gần người dùng** (CDN, edge, replication địa lý — →5.9/→8.6).

Cáp biển (hơn 500 cáp đang hoạt động, ~140 quốc gia) mang >95% dữ liệu liên lục địa (I). DWDM cho nhiều bước sóng cùng một sợi — vì vậy "hết cáp" hiếm khi là vấn đề vật lý; thường là vấn tốn kém/băng thông ở đầu cuối.

### 2.2 RTT là số nhân của mọi thứ

Độ trễ mạng = lan truyền (physic) + xử lý router + **hàng chờ** (queueing). Bạn chỉ điều khiển được phần thứ ba. RTT là "số phận" của:
- **TLS handshake:** ~2 RTT (TLS 1.3: 1 RTT, 0-RTT resume) (→4.1);
- **mỗi transaction request-response:** tải trang = n RTT;
- **thông qua TCP:** window / RTT = throughput (mục sau).

Vì vậy "giảm latency" trong kiến trúc thường đồng nghĩa: bớt vòng qua lại (pipelining, batching, connection reuse, HTTP/2 — →4.2), hoặc bớt khoảng cách (geo-replication — →5.9).

### 2.3 BDP: công thức một dòng đáng nhớ cả đời

```
Throughput ≤ Window / RTT        (per connection)

BDP = Bandwidth × RTT = số byte "đang bay" cần để đổ đầy đường ống
```

Ví dụ: 10 Gbps × 30 ms = ~37,5 MB mỗi kết nối. Nếu window mặc định nhỏ hơn (hoặc buffer nhận nhỏ hơn), bạn **không bao giờ** đạt được 10 Gbps trên 1 connection — bất kể mạng "rảnh". Đây là câu trả lời cho hàng nghìn tickets "sao iperf một stream chậm mà 10 stream nhanh". Giải pháp theo thứ tự: tăng window (`net.ipv4.tcp_rmem/wmem` scale), nhiều stream song song (SFTP/HTTP range), hoặc giao thức quên window (QUIC/HTTP3 kiểm soát tốt hơn — →4.2), hoặc gửi ít qua lại (nén, batching).

### 2.4 MTU, PMTUD và hố đen

Gói quá lớn cho chặng nào đó sẽ bị bỏ (hoặc phân mảnh). Path MTU Discovery dựa trên ICMP "Fragmentation Needed" — nhưng nhiều firewall **chặn ICMP vô phân biệt** → gói lớn biến mất âm thầm trong khi gói nhỏ (handshake, ping) vẫn chạy: **PMTUD black hole**. Triệu chứng kinh điển: "SSH vào được, nhưng `scp`/HTTPS treo". Vì SSH interactive dùng gói nhỏ; scp đẩy gói lớn. Chẩn: `tracepath`, hoặc giảm MTU thử. Quy tắc ops: **đừng chặn ICMP type 3 code 4**; cloud overlay (VXLAN) trừ thêm ~50–100 byte overhead — MTU nội cụm phải đặt tương ứng (nhiều cụm K8s đau vì chuyện này).

Jumbo frame (MTU 9000) trong cụm: giảm pps, giảm CPU — nhưng chỉ khi **mọi hop cùng bật**; một hop lệch là đen. Lợi ích thật cho storage/RDMA; nguy cơ thật cho mạng hỗn hợp.

### 2.5 Đệm switch: nông là đúng, nhưng phải biết mình đang chơi gì

Đệm switch lớn ("deep buffer") làm throughput TCP dài hạn tốt nhưng **cộng thêm độ trễ cho mọi người** (bufferbloat — bệnh kinh niên của Internet thập niên 2010, cứu bằng AQM/fq_codel/CAKE). Đệm nông (datacenter switch ~ vài MB chia chung) đúng cho đa số; nhưng hai workload làm nó tràn:
- **Incast:** N server cùng trả lời 1 collector → cổng collector nhận N×line-rate trong microsecond → drop → TCP timeout × N (cơn bão timeout là dạng sụp cụm của MapReduce/Shuffle). Thuốc: giảm đồng bộ (jitter, backoff), ECN + nhiều queue, hoặc pacing chậm hơn.
- **Microburst:** tổng taux đặt trước vượt line-rate trong vài ms — monitoring theo giây **không thấy** (trung bình phẳng), chỉ thấy drop. Phải đo theo cấp sub-second hoặc dùng telemetry switch (INT/gNMI).

ECMP hashing có thể **polarize**: các flow lớn cùng hash về một uplink trong khi uplink khác rảnh (voting giữa "resilient hashing" và đợi). Oversubscription (nghẽn có chủ đích, ví dụ 3:1 ở leaf-spine) là quyết định kinh tế bình thường — nhưng phải là **quyết định**, kèm workload đã biết.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Tốc độ ánh sáng trong sợi | ~⅔c = 5 µs/km | V | vật lý, không đàm phán |
| RTT nội cụm (cùng DC) | 0,1–1 ms | I | |
| RTT cùng khu vực (same-region) | 1–10 ms | I | |
| RTT liên lục địa | 50–300 ms | I | vệ tinh LEO: 20–50 ms |
| BDP 10 Gbps × 30 ms | ~37,5 MB | V | window phải ≥ BDP |
| MTU Ethernet | 1500 B (jumbo 9000) | V | VXLAN trừ ~50 B |
| Buffer datacenter switch | ~MB-scale chia chung | I | router WAN: GB-scale |

---

## 4. Suy luận kiến trúc

- **S1:** RTT và băng thông là ràng buộc **vật lý + kinh tế** (cáp, tần số, quyền đi dây); phần mềm chỉ được chọn cách xoay quanh (cache, replicate, batch).
- **S2:** Tham số trụ: RTT p50/p99 từng cặp dịch vụ, BDP các đường chính, tỉ lệ drop theo sub-second.
- **S3:** Jumbo đổi rủi ro cấu hình lấy pps; đệm sâu đổi latency lấy throughput; geo-replication đổi nhất quán (→8.1) lấy RTT người dùng — không có lựa chọn miễn phí.
- **S4:** LLM inference đang kéo topology "chụm lại" (prefill/decode cùng cụm, cross-DC cho model lớn còn hạn chế vì BDP + chi phí GPU nhàn rỗi) — trong khi user-facing lại "dàn ra" (edge, CDN). Hai lực ngược chiều; topo 2027+ khác 2023.
- **S5:** Đo telemetry theo sub-second, gNMI/INT đang phình thay SNMP 5 phút — vì microburst là hình thức nghẽn thật của cụm hiện đại.
- **S6:** Khi "mạng chậm", phân tách trước: vật lý (RTT), hàng chờ (queue), hay window (BDP)? Ba cái đó có thuốc khác nhau và thuộc ba chương khác nhau (đây, 1.6, 4.2).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| 1 stream chậm, nhiều stream nhanh | Window < BDP | `ss -i` (cwnd, rwnd); iperf -P 1 vs -P 8 | §2.3 |
| SSH được, scp/HTTPS treo | PMTUD black hole (ICMP bị chặn) | `tracepath host`; test MTU giảm | §2.4 |
| Shuffle/batch sụp theo chu kỳ | Incast → drop → timeout | switch drop counter sub-second; đồ thị retrans | §2.5 |
| p99 mạng cao, trung bình thấp | Microburst/đệm cạn | gNMI/INT; iperf nền + đo drop theo 10ms | §2.5 |
| Vùng mạng này chậm hơn vùng khác | ECMP polarization | `ecmp` counters theo từng uplink | §2.5 |
| Cross-DC replication lag tăng | Window + khoảng cách, không phải "mạng xấu" | `ss -i` cwnd có chạm trần không | §2.3 |

---

## 6. Cách đo

```bash
# RTT thật (không ping — đo theo ứng dụng)
mtr -ezbw -c 100 host           # từng hop: loss ở hop nào, có worsening dần không

# Throughput 1 vs N stream — phát hiện BDP trong 2 phút
iperf3 -c host -t 10             # 1 stream
iperf3 -c host -t 10 -P 16       # nhiều stream

# Window thật của kết nối đang chạy
ss -ti dst :443                  # cwnd, rwnd, rtt, retrans — đọc trên chính flow

# MTU path
tracepath host                   # "pmtu" nó báo

# Drop theo thiết bị (sub-second nếu switch hỗ trợ)
ethtool -S eth0 | grep -iE 'drop|discard|pause'
```

Nguyên tắc: **đo từng hop, theo hướng flow, ở đúng độ phân giải thời gian của hiện tượng.** Nghẽn 5 ms không hiện trên graph 1 phút, như sao biến mất ban ngày.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay "nâng băng thông":** nén (trade CPU), cache ở gần (→5.4/→5.9), bớt vòng qua lại (connection reuse, HTTP/2/3, batching), async hoá (queue — →5.7) để RTT rời khỏi đường người dùng. Băng thông là thứ **mua được cuối cùng** nên mua sau cùng.

Năm thấu kính:
- **Kinh tế:** Băng thông quốc tế là hàng hóa địa-chính-trị (cáp cắt, transit pricing); hợp đồng commit 95th-percentile là dạng tính tiền cần hiểu trước khi scale.
- **Vận hành:** MTU/ICMP/vxlan overhead là lớp "config drift" hay bị quên nhất — checklist cho mọi cụm mới.
- **An ninh:** Chặn ICMP vô duyện vừa gây hố đen MTU (§2.4) vừa làm hệ thống tự vá (PMTUD) tê liệt — an ninh tốt không phải là chặn hết.
- **Lịch sử:** Bufferbloat → AQM; incast → ECN/pacing; mỗi thế hệ fabric sinh bệnh riêng rồi thuốc riêng — đọc lịch sử để khỏi ngạc nhiên bệnh kế tiếp.
- **Người dùng:** 30 ms vs 300 ms là cảm giác "trang này biết việc" vs "chờ mãi". Bạn không thể sửa ánh sáng, nhưng bạn có thể chọn dữ liệu sống ở đâu.

---

## 8. Đọc tiếp & bài tập

- Giao thức trên nền này (TCP/TLS/HTTP): **4.1–4.2** · Geo-replication & trade-off nhất quán: **5.9, 8.1** · Đo lường end-to-end: **11.1**
- **Bài tập 1:** Tính BDP của: (a) replication cross-DC 10 Gbps × 40 ms; (b) home user 100 Mbps × 20 ms. Kiểm tra `net.ipv4.tcp_wmem` có cho phép window đó không.
- **Bài tập 2:** Trong cụm của bạn, chạy `iperf3 -P 1` rồi `-P 16` giữa 2 máy lệch rack. Nếu chênh > 4×, bạn vừa phát hiện một quyết định BDP chưa ai đưa ra.
- **Bài tập 3:** Tìm một firewall trong hệ thống của bạn đang chặn ICMP type 3. Mỗi ngày nó mở là một ngày PMTUD có thể hố đen — viết ticket kèm lệnh tái hiện `tracepath`.
