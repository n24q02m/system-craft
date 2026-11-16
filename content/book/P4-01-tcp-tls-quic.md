# 4.1 — Transport Hiện đại: TCP (BBRv3), TLS 1.3 & QUIC

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** giao thức · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 2.6 (netstack) · 1.7 (RTT/BDP).

**Sợi chỉ đỏ:** *Service chạy ngon trong máy — giờ mở cửa cho thế giới: transport an toàn và nhanh là gì?* — trả lời: mở cửa cho thế giới nghĩa là mỗi miligiây đi dây và mỗi lần rớt mạng đều thành tiền — TLS 1.3 rút bắt tay xuống một vòng, QUIC dời tin cậy lên UDP để sửa tận gốc hai bệnh của TCP (gói mất chặn cả hàng, đổi mạng là đứt kết nối), kèm bảng chọn transport theo use case. Câu hỏi để lại cho chương sau: *Trên transport đó, HTTP/1.1, H2, H3 khác nhau chỗ nào — app DM nên thương lượng gì?*

**Thuật ngữ sẽ gặp:** *TLS 1.3* — bắt tay một vòng; quay lại được 0-RTT nhưng kèm rủi ro replay; *0-RTT* — gửi dữ liệu ngay vòng đầu, chỉ dùng cho yêu cầu an toàn khi lặp lại; *QUIC* — transport chạy trên UDP: tin cậy + mã hoá + stream độc lập; *stream* — luồng có thứ tự riêng, một luồng nghẽn không chặn luồng khác; *connection ID* — định danh kết nối sống qua cả khi đổi IP; *congestion control* — thuật toán nhả gói của phía gửi: BBR, CUBIC.

**Ví dụ mở đầu:** Ứng dụng DM mở cửa cho cả nước: khách trong thang máy nhảy wifi sang 4G. Trên TCP, kết nối đứt và bắt tay làm lại từ đầu — nửa giây màn hình treo. Trên QUIC, connection ID còn nguyên, kết nối đi tiếp như chưa có chuyện gì. Chương này tách cái thật sự thay đổi ở tầng transport 2026 khỏi cái chỉ là quảng cáo.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Bật TLS 1.3 + 0-RTT ở đâu | Đổi 1 RTT lấy rủi ro replay — endpoint nào chấp nhận? |
| 2 | mTLS nội bộ (service-to-service) | Xác nhận danh tính hay chỉ "mật mã đường hầm"? Ai phát cert? |
| 3 | Congestion control (cubic/BBRv3) cho đường ngoài | Đường tôi lossy không — đo chưa (→1.7)? |
| 4 | Cho phép QUIC/HTTP/3 ở edge chưa | Người dùng mobile/di động chiếm bao nhiêu %? |

---

## 2. Cơ chế

### 2.1 TCP 2026: vẫn là xương sống, giờ có lựa chọn cách "đặt gạch"

TCP Reliable + ordered + congestion control (→2.6 netstack, →1.7 BDP). Điều mới trong thập kỷ: **BBR** thay loss-based bằng model băng thông×RTT — tốt cho đường yếu (→2.6 §2.4). Cũ mà vẫn đúng: mọi connection là máy trạng thái; TIME_WAIT/conntrack là chi phí vận hành (→2.6). TCP không giải được: head-of-line ở đường lossy (một gói mất = mọi stream chờ), handshake + TLS tốn 2–3 RTT cho kết nối ngắn — đó là chỗ QUIC ra đời.

### 2.2 TLS 1.3: ít vòng, nhanh hơn, an toàn hơn

So với 1.2: handshake 2-RTT → **1-RTT** (0-RTT cho phiên quay lại), bỏ hết thuật toán yếu (RSA key transport, CBC, RC4, SHA-1), encrypt phần lớn handshake, session resumption chuẩn hoá. Kết quả đo được: connection mới tiết kiệm ~1 RTT (→1.7 — với người dùng 100 ms RTT = nhanh thấy được ở kết nối ngắn).

**0-RTT:** client gửi data ngay trong lần bay đầu — nhưng dữ liệu đó **có thể bị replay** (kẻ đứng giữa bắt gói gửi lại). Quy tắc: 0-RTT chỉ cho request **idempotent** (GET, query) — **không bao giờ** cho POST đặt hàng/thanh toán (→4.8 idempotency như lớp cứu, nhưng đừng dựa). Tắt bằng cách không cấp session ticket sớm nếu chưa cần.

**mTLS nội bộ:** mỗi service có cert (SPIFFE/SPIRE, cert-manager + mesh issue) — xác nhận danh tính + mã hoá đường nội bộ. Chi phí: vòng quay cert (ngắn ngày, tự động — 24h–90d); lợi ích: zero-trust thật thay vì "mạng nội bộ tin được" (→10.2).

### 2.3 QUIC: mang HTTP/3 qua UDP, sửa gốc rễ TCP

QUIC (RFC 9000, 2021; HTTP/3 RFC 9114) chạy trên UDP, mang theo: handshake **kết hợp TLS 1.3** (1-RTT, 0-RTT), **stream độc lập** (mất gói chỉ chặn stream đó — hết HoL giữa streams), **connection migration** (đổi IP/wifi→LTE mà connection sống — Connection ID thay IP:port), theo dõi RTT/loss chính xác hơn (monotonic timestamps).

Chi phí: UDP ở một số middlebox/enterprise bị chặn hoặc throttle (firewall cũ); CPU cao hơn TCP kernel path (userspace crypto — đang giảm khi offload tới NIC); conntrack không theo dõi như TCP (thường tốt — bớt bảng đầy →2.6). Triển khai thực tế 2026: **HTTP/3 tại CDN/edge** (Cloudflare/Google/Fastly bật mặc định), origin nội bộ vẫn HTTP/2/TCP — đúng chỗ: mobile user hưởng lợi (đổi mạng, lossy), nội cụm ít lợi.

### 2.4 Bảng chọn transport theo use case

| Use case | Nên | Vì sao |
|---|---|---|
| API công khai, mobile nhiều | HTTPS + H3 (QUIC) nếu CDN hỗ trợ | migration + lossy + 1-RTT |
| Nội cụm, throughput | HTTP/2 trên TCP | ổn định, offload, công cụ chẩn đã trưởng thành |
| RPC chặn latency | gRPC over H2; QUIC nếu control cả 2 đầu | |
| Đường vệ tinh/3G yếu | BBR + QUIC | loss không phạt |
| Legacy enterprise firewall | TCP + TLS 1.3 | UDP có thể bị chặn |

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| TLS 1.2 / 1.3 handshake | 2-RTT / 1-RTT (0-RTT resume) | V | RFC 8446 |
| QUIC + TLS | handshake gộp 1-RTT | V | RFC 9001 |
| BBR vs cubic trên đường lossy | nhiều lần throughput | I | tuỳ đường |
| Cert lifetime nội bộ | 24h–90 ngày (tự động) | I | SPIFFE/mesh |
| TLS handshake CPU | ~ms mỗi conn mới (không resume) | I | →2.6/5.4 |

---

## 4. Suy luận kiến trúc

- **S1:** Transport quyết định "trần vật lý" của trải nghiệm (RTT × số vòng) — không tầng framework nào sửa được 3 RTT handshake dư.
- **S2:** Tham số trụ: RTT từng segment người dùng, TLS handshake/s (CPU), tỉ lệ H3 vs H2, retrans.
- **S3:** 0-RTT đổi tốc độ lấy replay-risk; mTLS đổi ops cert lấy danh tính; QUIC đổi tương thích middlebox lấy trải nghiệm mobile — ba cái đều "đúng chỗ" chứ không "đúng mọi nơi".
- **S4:** HTTP/3 ở edge + H2 nội bộ đang thành topology chuẩn — đừng chiến nội bộ H3 (lợi ít, công cụ chẩn ít).
- **S5:** Post-quantum (X25519MLKEM768 mặc định Chrome 2024+, mở rộng dần) đang tiến vào TLS mặc định — inventory thư viện crypto của bạn là bài tập sớm (→10.5).
- **S6:** Khi "kết nối chậm": đếm RTT cần trước byte đầu (DNS+TCP+TLS+TTFB) — mỗi bậc thuộc một chương khác nhau (1.7, đây, 4.2).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| CPU cao khi nhiều connection mới | TLS handshake (không resume) | ssl metrics; session ticket bật chưa | §2.2 |
| POST đôi khi lặp 2 lần | 0-RTT replay | audit endpoint 0-RTT cho phép | §2.2 |
| H3 không hoạt động một số mạng | Middlebox chặn UDP | fallback H2 (mặc định); đo tỉ lệ | §2.3 |
| Đường vệ tinh/3G chậm | cubic loss-based | thử BBR; đo retrans | §2.1 |
| Cert nội bộ hết → service chết | Không xoay tự động | alert expiry; auto-rotation | §2.2 |

---

## 6. Cách đo

```bash
# Đếm RTT handshake thực tế từ client
curl -w 'dns=%{time_namelookup} tcp=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer}\n' \
     -so /dev/null https://api.example.com

# Protocol thực sự đang dùng
curl -sI --http3 https://svc -o /dev/null -w '%{http_version}\n'

# TLS config audit (điểm + thuật toán)
sslyze --regular api.example.com | head -30

# Trong node: handshake/s, session resume rate — metric client lib
```

Nguyên tắc: **đo thời gian tới byte đầu rồi phân bổ** — dns/tcp/tls/ttfb — mỗi mili giây có địa chỉ và chương riêng.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay nâng transport:** giữ kết nối lâu hơn (keep-alive pool — →3.11), giảm số vòng (in-process/BFF gộp gọi), cache ở gần (→5.4). Mỗi cái "giảm RTT" mà không cần đổi giao thức. **Thay mTS mesh:** cert + service account + network policy đôi khi đủ — mesh khi cần quan sát+policy đồng loạt (→9.4).

Năm thấu kính:
- **Kinh tế:** 1 RTT với 200 ms người dùng Á-Âu = tiền chuyển đổi thật (nghiên cứu lớn: +100 ms latency → ~1% doanh thu (I)) — TLS 1.3 không phải chi tiết kỹ thuật mà là dòng doanh thu.
- **Vận hành:** Inventory cert + expiry alert là hygiene; tự động hoá xoay trước khi tin "mặc định an toàn".
- **An ninh:** TLS bảo mật đường truyền — không bảo vệ application (token, idempotency, authorization vẫn là việc của 4.8/10.x); đừng nhầm lớp.
- **Lịch sử:** SSLv2 (1995) → TLS 1.3 (2018) → PQ mặc định (2024+): mỗi thế hệ bỏ "đồ chơi" của thế hệ trước; protocol cũ tồn tại vì compatibility, không vì tốt.
- **Người dùng:** Người dùng thấy "app mở nhanh khi đổi wifi" (QUIC) và "không bị hack giữa đường" (TLS) — cả hai đều vô hình khi đúng, rất hữu hình khi sai.

---

## 8. Đọc tiếp & bài tập

- HTTP ngữ nghĩa: **4.2** · Netstack/kernel: **2.6** · Vật lý RTT: **1.7** · Crypto nền: **10.5, 14.10** · QUIC cho agent streaming: **12.5**
- **Bài tập 1:** curl -w breakdown (§6) cho 3 API chính từ 3 vùng. Bao nhiêu % thời gian là TLS? Nếu > 20% — resume/keep-alive là ưu tiên.
- **Bài tập 2:** Kiểm tra mọi endpoint POST: có cho phép 0-RTT replay không? Lập danh sách cần chặn.
- **Bài tập 3:** Đếm thời gian còn lại của cert có tuổi thọ ngắn nhất còn lại trong cụm. Nếu < 30 ngày và không tự xoay — đó là timer của một sự cố tương lai.
