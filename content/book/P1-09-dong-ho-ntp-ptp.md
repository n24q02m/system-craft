# 1.9 — Đồng hồ: NTP, PTP, leap second

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** không có (chương mới hoàn toàn)

---

## 0. Nhập môn

**Đọc trước:** 1.1 (độ trễ).

**Sợi chỉ đỏ:** *Từ hai máy trở đi là hai cái đồng hồ — 'đơn đặt lúc 09:59:59' nghe ở máy nào, và lệch giờ gây họa gì?* — trả lời: mỗi máy đếm thời gian theo nhịp riêng và rung; NTP kéo mọi máy về cùng miligiây, PTP — cần phần cứng — về microgiây; thứ tự sự kiện chỉ đáng tin khi độ lệch nhỏ hơn khoảng thời gian cần phân biệt. Câu hỏi để lại cho chương sau: *Cái máy ấy chạy bằng điện và toả nhiệt — hóa đơn, tần số, throttle đến từ đâu?*

**Thuật ngữ sẽ gặp:** *NTP* — giao thức chỉnh đồng hồ qua mạng, đúng tới vài miligiây, chỉnh từ từ; *PTP* — chuẩn IEEE 1588 tới microgiây, cần card mạng hỗ trợ; *offset/drift* — độ lệch hiện tại và tốc độ lệch thêm dần; *đồng hồ đơn điệu* — bộ đếm chỉ tiến, dùng để đo khoảng, miễn nhiễm chỉnh giờ; *thứ tự sự kiện* — ai xảy ra trước ai, câu hỏi khác "ai xảy ra lúc mấy"; *leap second* — giây nhuần làm phút có 61 giây.

**Ví dụ mở đầu:** Khách đặt món lúc 23:59:59 theo đồng hồ quán, máy DM nhận lúc 00:00:03 — ưu đãi "đơn cuối ngày" tính cho ai? Hai dòng log "cách nhau 3 giây" thực ra là hai cái đồng hồ lệch nhau. Mọi hệ thống dùng timestamp để ra quyết định đều đang thầm tin rằng đồng hồ không lệch; chương này dạy đo niềm tin đó.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Chuẩn thời gian nào cho cụm: NTP hay PTP | Tôi cần đúng tới ms hay µs? Ai tiêu thụ con số đó? |
| 2 | Deadline/timeout tính theo đồng hồ nào (mono vs wall) | Code tôi có đọc wall-clock để ra quyết định không? |
| 3 | Timestamp phân tán ghi thế nào (logic clock / hybrid / TrueTime-style) | Hai sự kiện ở 2 máy — thứ tự nào đúng? Ai cần biết? |
| 4 | Xử lý leap second theo hướng nào | Hệ tôi có panic khi 23:59:60 xuất hiện không? |

---

## 2. Cơ chế

### 2.1 Đồng hồ là con số đếm — và con số đó rung

- **Thạch anh:** máy tính đếm dao động tinh thể; sai số **±10–50 ppm** (I) = 1–5 s/ngày nếu không chấn chỉnh; nhiệt độ làm lệch (máy nóng chạy nhanh hơn — vì vậy CDC máy chủ có "clock skew" thay đổi theo tải nhiệt, →1.10).
- **monotonic vs wall:** `CLOCK_MONOTONIC` chỉ tăng (đo khoảng — đúng cho timeout/deadline); `CLOCK_REALTIME` là lịch (đọc được — nhưng NTP có thể nhảy). **Quy tắc số một của chương: hết thảy deadline/elapsed dùng mono; wall chỉ để hiển thị và ghi log.** Phần mềm vi phạm quy tắc này tạo ra lỗi "timeout âm", "diff timestamp 2 sự kiện là −3 s" — tìm mãi không ra.

### 2.2 NTP: đúng tới miligiây, bằng cách từ từ

NTP so với server (stratum layering: GPS/atomic → stratum 1 → ...) và **slew** — kéo nhỏ giọt (500 ppm max) thay vì nhảy, chỉ **step** khi lệch lớn. Kết quả: đồng bộ ~1–10 ms trong điều kiện tốt (I), đúng cho hầu hết mọi thứ: log, TLS cert validity, cron, billing phút-cấp.

Chrony (chuẩn de-facto Linux hiện đại) tốt hơn ntpd: hội tụ nhanh, xử lý-network jitter tốt hơn. Metrics quan trọng: `offset`, `root delay` — lên alert khi |offset| > ngưỡng (ví dụ 50 ms).

### 2.3 PTP (IEEE 1588): micro giây cần phần cứng

PTP dùng timestamp **trên NIC** (hardware timestamping) + switch hỗ trợ (transparent clock/boundary clock) bỏ trừ độ trễ trong switch: đạt **sub-µs** trong cụm (I). Ai cần: telecom (5G TDD), finance (sequencing sự kiện cho tuân thủ — SEC/FINRA yêu cầu timestamp ±1 ms hoặc tốt hơn), đo lưới điện, media sync. Không ai khác cần — nhưng khi cần thì NTP không thay được.

GNSS (GPS) cho stratum-0: rẻ, đúng — và là mặt trời của rủi ro: **jam/spoof** khu vực cảng, chiến sự là hiện tượng thật (các sự kiện 2024–2026 ở Baltic/Đông Âu) (V). Vài stratum-0 là biên pháp; multi-source (GNSS + eLoran + PTP từ ISP) là biên pháp nghiêm túc.

### 2.4 Thứ tự sự kiện: vấn đề thật của hệ phân tán

Hai máy ghi "giao dịch A trước B" theo đồng hồ riêng — lệch nhau vài ms là thứ tự đảo. Ba hướng thoát (chi tiết →8.1):
1. **Logical/log vector:** đếm quan hệ nhân-quả, không đếm giây — đúng cho "ai causally trước ai";
2. **Hybrid (đề xuất cho hầu hết):** timestamp vật lý + counter (HLC): gần như wall-clock dễ đọc, gần như logic an toàn thứ tự;
3. **TrueTime-style (Spanner):** API trả về **khoảng** [earliest, latest] + đợi chắc chắn (commit-wait vài ms) — chắc tuyệt đối cho thứ tự toàn cục, giá là độ trễ.

Kịch bản phải cân nhắc ngay từ thiết kế: LWW conflict resolution (→5.9) với skew = **mất update âm thầm** — triệu chứng "bản ghi cũ ghi đè mới" không ai báo động.

### 2.5 Leap second: 60 giây phút 61

Trái đất trễ, giây nhuận chèn vào 23:59:60. Phần mềm giả định 86400 s/ngày gặp thần chú xui: Java/Java-cấp phút lặp, kernel POSIX lặp second, một số DB lock. Sự cố thật: nhiều dịch vụ lớn sập 2012 (Linux kernel leap bug), Cloudflare 2017 (RRDNS so sánh hiệu mono-wall âm → panic) (V). Hệ thống hiện đại xử lý bằng **smear** — dàn đều 24 h (Google, AWS style) hoặc bỏ qua (utc-sls, đề xuất IEC). Trước 2035, ITU đã bỏ phiếu **có thể chấm dứt leap second** — quyết định chưa chốt (V); đừng đặt cược kiến trúc vào cả hai hướng, đặt cược vào "code tôi không giả định phút có 60 giây".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Thạch anh | ±10–50 ppm | I | 1–5 s/ngày drift |
| NTP (chrony, Internet) | ~1–10 ms | I | phụ thuộc mạng |
| PTP hardware | ~0,1–1 µs | I | cần NIC + switch hỗ trợ |
| Google/AWS smear | 0,1 ppm gradient ≈ 4,6 ms/h (24h) | V | dàn đều |
| Spanner TrueTime | ε ~1–7 ms; commit-wait ~ε | V | khoảng tin cậy |
| Leap second | có thể loại bỏ sau 2035 | V | ITU 2022 quyết định nghiên cứu — chưa chốt |

---

## 4. Suy luận kiến trúc

- **S1:** Đồng hồ không bao giờ đồng bộ tuyệt đối trên cụm — đây là ràng buộc vật lý (tốc độ ánh sáng + drift), mọi thiết kế phải ngầm định "có sai số ε".
- **S2:** Tham số trụ: |offset| mỗi máy, tỉ lệ step, phân phối lệch giữa cặp máy ghi cùng bản ghi.
- **S3:** PTP đổi phần cứng + vận hành lấy µs; TrueTime đổi commit-wait latency lấy thứ tuyệt đối; hybrid clock đổi vài byte metadata lấy an toàn nhân quả — mỗi mức đều đúng cho ai đó.
- **S4:** AI training/inference phân cụm lớn làm đồng bộ thời gian càng quan trọng (distributed tracing xuyên cụm, tee lake log) — PTP trong cụm AI đang trở thành mặc định của hạ tầng nghiêm túc.
- **S5:** Regulations (FINRA CAT, MiFID II ±100 µs..1 ms — tuỳ asset class (V)) đang kéo ngành tài chính vào PTP + GNSS — hiệu ứng lan sang các ngành dữ liệu nhạy khác.
- **S6:** Khi thấy "thứ tự sự kiện sai" hoặc "dữ liệu cũ đè mới", lùi một tầng: đồng hồ — và chọn hướng thoát theo mục 2.4 thay vì vá từng chỗ.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Bản ghi mới bị bản ghi cũ ghi đè (LWW) | Clock skew giữa app servers | so `date -u` 2 node; chronyc tracking | §2.4 |
| Timeout "âm"/đồ thị spike 1 lần | Wall-clock bị step giữa chừng | grep chrony log; review code dùng REALTIME | §2.1 |
| Log 2 máy không khớp khi đối chiếu | Offset khác nguồn NTP | `chronyc sources` từng máy | §2.2 |
| Cron chạy 2 lần / 0 lần | Step thời gian qua nửa đêm | lịch chạy theo UTC; mono guard | §2.2 |
| Sập lúc 23:59:60 | Leap second không smear | kiểm tra smear policy; patch kernel | §2.5 |
| Kiểm toán tài chính lỗi lệch thứ tự | Không PTP/mono sequence number | deploy PTP + sequence per-book | §2.3 |

---

## 6. Cách đo

```bash
chronyc tracking           # offset, root delay, stratum
chronyc sources -v         # nguồn, reachable, offset từng nguồn
timedatectl                # sync on? NTP active?
ptp4l -i eth0 -m           # PTP trên interface (nếu có HW timestamp)
pmc -u -b 0 'GET TIME_STATUS_NP'   # offset PTP hiện tại
phc2sys -s eth0 -c CLOCK_REALTIME -w   # đồng bộ PHC → system

# Đo lệch giữa 2 máy không cần dịch vụ:
# cùng curl "http://time.is/api" trong 1 giây, so sánh — chẩn nhanh
```

Nguyên tắc: **đồng hồ là số liệu vận hành** — lên dashboard như CPU/RAM; offset bất thường thường là triệu chứng đầu tiên của: mạng kém (NTP không đạt được), máy quá nóng (drift), hoặc VM bị migrate (đồng hồ vọt).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay PTP:** NTP đủ cho 99% (log, cron, cert); sequence number cục bộ (Kafka offset, LSN — →5.5) cho thứ tự trong một log; mono-time cho khoảng. Đừng mua PTP khi một counter giải quyết. **Thay TrueTime-style:** HLC + đề bài chấp nhận "gần đúng" (hầu hết sản phẩm), hoặc sequencer trung tâm (đổi SPOF/throughput lấy đơn giản).

Năm thấu kính:
- **Kinh tế:** PTP cần NIC + switch + chuyên môn: chi phí thật; chỉ đáng khi compliance/telecom/media hoặc telemetry phân cụm đòi hỏi.
- **Vận hành:** Monitoring offset nên alert theo **trend**, không phải ngưỡng tuyệt đối — trend tăng là NIC sắp hỏng hoặc mạng đang xuống.
- **An ninh:** Time spoof là vector tấn công (hết hạn cert, OTP window, audit trail); NTP nên trỏ vào nguồn kiểm soát được + authentication (NTS — RFC 8915).
- **Lịch sử:** Lỗi 2012/2017 dạy cùng bài học: không giả định 86400 s; smear ra đời từ sự cố — lần đầu Google công bố "dàn đều" nội bộ từ 2008. Đọc lịch sử để khỏi tái diễn.
- **Người dùng:** Người dùng thấy "bài đăng hiện thị sai giờ" hoặc "đơn đặt bị trễ 1 phút" — cả hai đều là quyết định timezone/đồng bộ của bạn, không phải "lỗi internet".

---

## 8. Đọc tiếp & bài tập

- Nhất quán & thứ tự sự kiện: **8.1** · Tracing phân tán (đọc timestamp chéo máy): **11.1** · LWW conflict: **5.9** · Crypto cần nonce/thời gian: **10.3**
- **Bài tập 1:** Audit code của bạn: grep `CLOCK_REALTIME`/`new Date()`/`time.Now()` trong đường quyết định (timeout, dedup, ordering). Mỗi chỗ là một lỗi tiềm ẩn — chuyển sang mono/counter.
- **Bài tập 2:** Trên 3 máy, chạy `chronyc tracking` cùng lúc, chụp offset. Nếu chênh nhau > 50 ms, bạn đang sống với rủi ro LWW mà không biết.
- **Bài tập 3:** Thiết kế lại một bảng "created_at" của bạn: nếu hai máy cùng ghi, thứ tự ai thắng? Nếu không trả lời được trong 5 phút — đó là thiết kế chưa xong.
