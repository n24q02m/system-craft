# 1.10 — Điện, nhiệt, làm mát

> **Tầng:** Lồng · **Quyển I** · **Trục đọc:** nền vật lý · **Động từ liên quan:** Thiết kế · Chẩn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.1 (bậc thang) · 1.5 (GPU điện nóng).

**Sợi chỉ đỏ:** *Cái máy ấy chạy bằng điện và toả nhiệt — hóa đơn, tần số, throttle đến từ đâu?* — trả lời: hóa đơn đến từ công suất nhân giờ nhân PUE; nhiệt và tần số ghép nhau — nóng thì throttle, throttle thì p99 xấu; và những con số này chuyển mọi cuộc nói "tối ưu code" thành cuộc nói tiền. Câu hỏi để lại cho chương sau: *Một máy một process là trần đầu tiên — process ấy đang được Linux đối xử thế nào với bộ nhớ của nó?*

**Thuật ngữ sẽ gặp:** *TDP* — mức nhiệt thiết kế của chip, không phải mức tiêu thụ thật và cũng không phải trần; *PUE* — tổng điện tiêu chia điện cho máy tính: con số của cả tòa nhà; *turbo/boost* — nâng tần số ngắn hạn khi còn nhiệt độ; *throttle* — hạ tần số để tự vệ khi nóng: p99 xấu từ đây; *carbon-aware* — dời việc nặng sang giờ điện sạch/rẻ thay vì tôn giáo.

**Ví dụ mở đầu:** Phòng máy của DM: 20 kW chạy 24/7 với PUE 1,6 — gần 520 triệu đồng điện mỗi năm (giá Việt Nam). Một đợt tối ưu query tiết kiệm 20% CPU quy ra khoảng 100 triệu mỗi năm, không mua thêm thiết bị nào. Điện là đơn vị hiệu năng duy nhất mà CEO và kỹ sư đọc cùng một cách — chương này dạy đọc.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chế độ hiệu năng cho máy sản xuất (turbo mặc định / cap tần số / perf-governor) | Tôi đổi p99 lấy kWh như thế nào? Ai đang quyết định — BIOS hay tôi? |
| 2 | Phương án làm mát cho mật độ công suất tôi nhắm | Rack của tôi k W/rack? Air còn chịu được không? |
| 3 | Topo điện: N+1, 2N, hay chấp nhận downtime | Mất một đường/feed — hệ thống sống bao lâu? |
| 4 | Carbon-aware scheduling có đáng không | Tỉ lệ PUE và mix lưới điện của tôi là gì? |

---

## 2. Cơ chế

### 2.1 TDP không phải mức tiêu thụ — cũng không phải trần

TDP (Thermal Design Power) là **mốc toả nhiệt để thiết kế làm mát**, không phải mức tiêu thụ tối đa. CPU thực tế có **PL1** (sức bền dài hạn ≈ TDP) và **PL2** (turbo ngắn, thường 1,5–2× PL1 trong vài–chục giây, tham số **tau**), GPU có power limit điều chỉnh được. Máy "350 W CPU" có thể nhỉnh hơn 400 W trong burst — và đây là bài toán thiết kế điện-nhiệt, không phải số liệu trang trí.

Turbo ăn từ **ngân sách điện/nhiệt chung**: lõi này bật turbo, lõi khác giảm; GPU hàng xóm nóng, tần số bạn tụt. Đó là lý do "benchmark khác nhau giữa các lần chạy" và là cầu nối tới 1.2 (AVX-512 downclock): SIMD nặng tiêu điện gấp → vi điều khiển giảm xung toàn chip để giữ gói trong TDP (cũ: nặng, mới: nhẹ — nhưng vẫn hiện diện). **DVFS** (dynamic voltage-frequency scaling) là cơ chế nền: tần số~điện áp², nên giảm xung tiết kiệm phi tuyến.

### 2.2 Nhiệt: kẻ thù số một của độ bền và p99

- **Thermal throttling:** chip chạm Tj-max (~95–105°C) tự giảm tần số — triệu chứng: service "chậm lúc giờ nóng nhất trong ngày" mà CPU% bình thường.
- **Vòng lặp phản hồi điển hình:** nhiệt độ tăng → quạt max → tần số giảm → throughput giảm → hàng chờ tăng → CPU bận hơn → nhiệt tăng. Nhận diện bằng correlation (nhiệt, tần số, latency trên cùng trục thời gian).
- **Vật lý môi trường:** datacenter chuẩn "nhiệt lạnh" 18–27°C đầu vào (ASHRAE); **độ cao** và **độ ẩm** đều thay đổi khả năng làm mát (máy ở Đà Lạt và ở Sài Gòn không cùng trần công suất).

### 2.3 Làm mát: bậc thang không thể đi tắt

```
Air (gió)          ~10–20 kW/rack      — chuẩn phòng máy truyền thống
Rear-door HX       ~20–40 kW/rack      — gắn tấm trao đổi nhiệt sau rack
Direct-to-chip     ~50–120 kW/rack     — nước lạnh/tỏa nhiệt tới chip
Immersion          ~100–200+ kW/rack   — ngập chất lỏng điện môi
```

(I, bậc; ranh giới mềm theo thiết kế.) Timeline rack AI đã verify: Hopper ~40 kW → Blackwell rack 120–130 kW → VR200 NVL72 190–230 kW (V). Nghĩa là: **không có con đường nào từ phòng air-cool tới rack AI** ngoài build mới cơ sở. Đây là lý do "AI datacenter" 2026 là ngành xây dựng nhiều như là ngành máy tính (→14.5 HPC chapter về vật lý tầng này).

Chất làm mát không nước: dielectric liquid ít phổ biến vì chi phí + bảo trì; direct-to-chip hiện chiếm ưu thế cho rack AI. **Rò rỉ** là rủi ro vận hành số một của lớp này — sensor + quy trình thay thế nóng phải có trước khi nhận rack đầu tiên.

### 2.4 Điện: đo bằng tin cậy, không bằng công suất

- **PUE** = tổng điện cơ sở / điện IT: truyền thống 1,5–1,9; hiện đại 1,1–1,3 (I); con số này quyết định "hóa đơn thật" của bạn và của cloud.
- **Redundancy:** N+1 (thừa một đường) vs 2N (nhân đôi toàn bộ) vs 2N+1 — chi phí tăng gần tuyến tính với chữ N; chọn theo downtime chấp nhận được × giá mỗi phút.
- **UPS**: hóa đơn nhỏ, bài toán lớn — pin chở tới khi diesel nổ; **kiểm thử định kỳ bằng cắt điện thật** (như các gã khổng lồ làm shutdown drill) là cách duy nhất biết hệ thống hoạt động.
- Một chi tiết bị bỏ quên: **chất lượng điện** (sag, surge, harmonic) giết nguồn máy theo kiểu tích luỹ; cơ sở xấu cần điều hòa tuyến (AVR/STS).

### 2.5 Carbon-aware: quyết định giờ, không phải tôn giáo

Lưới điện có mix thay đổi theo giờ (tối nhiều điện mặt trời trưa ở lưới có solar). **Carbon-aware scheduling** = dời batch (training, ETL, rebuild index) sang khung giờ carbon thấp — không dời latency-sensitive. Lợi ích thật ở lưới có biến động lớn (bậc vài–20% footprint tính toán được di dời (I)); không phải "cờ xanh" marketing. Google đã chạy hằng ngày từ 2021 (V). Với VN: lưới chủ lực than/hydro/thiện — dữ liệu giờ-điểm công khai còn yếu, vì vậy quyết định nên bắt đầu từ **đo PUE + ghi nhận nguồn** rồi mới tối ưu.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| PL2 / PL1 | 1,5–2×, trong vài–chục s (tau) | I | cấu hình BIOS/OEM |
| Tj-max | ~95–105°C | I | throttling threshold |
| Air / RDHx / D2C / immersion | 10–20 / 20–40 / 50–120 / 100–200+ kW/rack | I | bậc — ranh giới mềm |
| Rack: Hopper / Blackwell / VR200 | ~40 / 120–130 / 190–230 kW | V | verify 2026-10 |
| PUE truyền thống / hiện đại | 1,5–1,9 / 1,1–1,3 | I | |
| ASHRAE đầu vào | 18–27°C | V | khuyến nghị |

---

## 4. Suy luận kiến trúc

- **S1:** Điện và nhiệt là ràng buộc **cứng nhất** của cụm AI — không mua GPU nếu không có kế hoạch kW và kW còn thiếu thì không dùng được.
- **S2:** Tham số trụ: kW/rack thiết kế, nhiệt độ đầu vào, tần số trung bình chip (bằng turbo budget index), PUE.
- **S3:** Cap tần số đổi kWh + p99 ổn định lấy throughput tối đa; carbon-aware đổi giờ chạy batch lấy footprint — cả hai đều "miễn phí nếu biết đặt lịch đúng".
- **S4:** Rack 100–200 kW là **điểm gãy cơ sở hạ tầng**: làm mát + điện + sàn tải trở thành chi phí chính của AI — phần "không phải chip" quyết định tốc độ triển khai 2026–2028.
- **S5:** D2C/immersion + telemetry nhiệt chi tiết đang phình thành lớp ops mới (sensor/điều khiển thời gian thực) — kỹ năng "SRE nhiệt" sẽ phổ biến.
- **S6:** Khi máy chậm không rõ lý do, trục chẩn nên gồm: nhiệt → tần số → điện (tuần tự theo giá đo rẻ→đắt) trước khi đổ lỗi phần mềm.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Service chậm đúng giờ nắng trưa | Nhiệt phòng tăng → throttle | `turbostat` tần số + sensor nhiệt theo giờ | §2.2 |
| p99 ổn định, sau đó tụt vọt định kỳ | Power budget chạm trần (PL2 hết) | `rapl`/powercap energy theo giây | §2.1 |
| Benchmark không tái lập được | Turbo khác nhau theo nhiệt lịch sử máy | làm lạnh máy trước khi đo; ghi nhiệt vào log | §2.1 |
| Rack mới "không lên đủ công suất" | Phần điện làm mát chưa theo kịp thiết kế IT | đối chiếu kW thiết kế vs đo; CFD/flow check | §2.3 |
| Rò rỉ chất làm mát | D2C fitting/aging | leak sensor; drill thay thế nóng | §2.3 |
| Máy sập lúc cắt điện thử | UPS/ATS chưa từng drill thật | drill có kế hoạch; ghi RTO thực | §2.4 |

---

## 6. Cách đo

```bash
# Tần số + nhiệt + điện — tất cả trong một
turbostat --interval 5     # Bzy_MHz, PkgTmp, PkgWatt, CORWatt

# Powercap/RAPL từ sysfs (không cần cài gì)
cat /sys/class/powercap/intel-rapl:0/energy_uj   # đọc 2 lần, chia khoảng thời gian

# Nhiệt từng vùng
sensors                     # chipset + NVMe + CPU package

# GPU
nvidia-smi --query-gpu=temperature.gpu,clocks.sm,power.draw --format=csv -l 5

# Ở tầng phòng: PDU/cảm biến nhiệt — theo kWh, không theo "cảm giác"
```

Nguyên tắc: **ghi ba thứ cùng nhịp thời gian — tần số, nhiệt, p99** — rồi mới liên quan. Đa số "mystery latency" tại tầng này chỉ thấy khi cả ba đường lên cùng một trục.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay xây phòng máy mới:** thuê colocation D2C-ready; hoặc thả workload xuống cloud (PUE họ tốt hơn bạn — quyết định bằng số, không theo tinh thần). **Thay làm mát thêm:** giảm nhiệt phát sinh — cap tần số, sleep/consolidate máy, scheduler dời batch (thường rẻ hơn 1 tấm RDHx). **Thay carbon-aware:** mua điện xanh hợp đồng (PPA) — quan trọng về báo cáo hơn là về bản chất giờ-điểm.

Năm thấu kính:
- **Kinh tế:** Hóa đơn điện là chi phí vận hành lớn nhất của cụm sau nhân sự; 10% PUE = tiền thật mỗi tháng. Rack AI: điện 10 năm có khi vượt giá rack.
- **Vận hành:** Drill (cắt điện, rò rỉ, nóng cục bộ) giống backup: không drill = không có. Lịch drill nửa năm.
- **An ninh:** Điện-nhiệt là bề mặt tấn công vật lý thật (cắt điện, phá làm mát — các sự cố cáp/điện 2025–2026 ở châu Âu) — kế hoạch liên tục (BC/DR →11.2) phải tính nhánh "điện/nhiệt mất".

- **Lịch sử:** Từ mainframe (làm mát nước 1980s) → air (PC era) → nước trở lại (AI era): công nghệ xoay vòng theo mật độ; ai học 1.4 (write cliff) sẽ nhận ra pattern: mật độ tăng → ngưỡng vật lý cũ sụp.
- **Người dùng:** Người dùng thấy "AI chậm giờ cao điểm" và tưởng model tệ — thật ra có khi chỉ là rack đang 95°C. Kết nối trải nghiệm người dùng với kWh là điều chưa ai làm tốt — kể cả các cloud lớn.

---

## 8. Đọc tiếp & bài tập

- Cấp Rack/NVL72 & interconnect: **1.6** · HPC datacenter: **14.5** · BC/DR: **11.2** · Giám sát toàn cảnh: **11.1**
- **Bài tập 1:** Chạy `turbostat -i 5` trong 1 giờ workload thật của bạn; ghi PkgWatt p50/p99 và tần số trung bình. Nếu chưa từng thấy các số này, bạn chưa từng thực sự biết máy mình chạy thế nào.
- **Bài tập 2:** Tính: nếu cụm 500 kW chạy 24/7 với PUE 1,6, hóa đơn/tháng ở giá VN (~1.700–2.000 VND/kWh ca cao điểm bậc) là bao nhiêu? PUE 1,2 tiết kiệm bao nhiêu/năm? Đem số này đi nói chuyện với sếp.
- **Bài tập 3:** Kiểm tra hôm nay: khi nào lần cuối bạn drill mất điện? Nếu "chưa bao giờ", thì UPS của bạn là linh kiện tưởng tượng.
