# 11.5 — Kinh tế học Kỹ thuật & FinOps

> **Tầng:** Vận hành · **Quyển II** · **Trục đọc:** độ tin cậy · **Động từ liên quan:** Đo · Định giá
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 9.5 (mô hình giá compute) · 9.3 (bảng giá cloud).

**Sợi chỉ đỏ:** *Hóa đơn cloud là SLO thứ hai — FinOps quản tiền theo đơn vị nào?* — trả lời: hóa đơn cloud là SLO thứ hai — FinOps là vòng quản trị chứ không phải "cắt chi phí"; con số trung tâm là unit economics: bao nhiêu đồng cho một đơn giao thành công; mua đúng kiểu cam kết và spot theo loại việc; chi phí là feedback loop: showback rồi chargeback. Câu hỏi để lại cho chương sau: *Hệ thống là tổ chức — Conway, ADR, on-call nói gì về team của DM?*

**Thuật ngữ sẽ gặp:** *unit economics* — chi phí theo đơn vị nghiệp vụ: đồng mỗi đơn giao thành công: con số duy nhất tài chính và kỹ thuật cùng hiểu; *khoản ẩn* — NAT, traffic liên vùng, tài nguyên idle: hóa đơn phình từ dòng nhỏ; *cam kết* — reserved, savings plan: giá rẻ hơn đổi cam kết vài năm: bài dự báo; *spot* — máy thừa giá rẻ đổi bị thu hồi: cho batch, không cho tầng online; *showback/chargeback* — gán chi phí theo team: tiền là thông tin phản hồi, không phải trừng phạt; *kinh tế kiến trúc* — mọi quyết định chương 5 tới 10 có dòng tiền: chương nối lại tất cả.

**Ví dụ mở đầu:** Hóa đơn cloud của DM tăng 40% trong hai quý dù traffic chỉ tăng 10%: không ai làm sai gì lớn, chỉ là không ai nhìn. Unit economics đưa về "đồng mỗi đơn giao". Chương này là vòng quản trị tiền theo nhịp kỹ thuật, không phải đợt cắt giảm một lần.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Unit economics: chi phí / 1k request / tenant / triệu token | Tôi bán một đơn vị giá trị thì **tốn bao nhiêu** — biết trong 1 phút không? |
| 2 | Phân bổ chi phí (showback/chargeback) theo team/feature | Team nào đốt tiền nào — và họ có thấy không? |
| 3 | Chiến dịch tiết kiệm: mua trước (RI/SP) vs spot vs tắt | Tôi đang trả list price bao nhiêu % — và cái gì đáng được mua trước? |
| 4 | Cân bằng tối ưu chi phí ↔ rủi ro ↔ tốc độ | Tiết kiệm nào làm tăng rủi ro (đã định lượng) — ai duyệt? |

---

## 2. Cơ chế

### 2.1 FinOps là quản trị, không phải "cắt chi phí"

Vòng FinOps: **Báo** (nhìn thấy chi phí theo team/service/tài nguyên — tagging chuẩn là điều kiện: không tag = không tồn tại) → **Quyết** (phân bổ + ngân sách + anomaly detection — hóa đơn tăng 20% hôm qua vì ai?) → **Tối ưu** (mua đúng, tắt thừa, scale đúng) → lặp. Chi phí cloud là **biến số vận hành hàng ngày** (dev tạo tài nguyên = chi tiêu), không phải hóa đơn tháng xem một lần — khác biệt căn bản với on-prem.

### 2.2 Unit economics — con số trung tâm

`chi phí / đơn vị giá trị` — chọn đơn vị theo sản phẩm: 1k request, 1 tenant/tháng, 1 đơn hàng, 1 triệu token (AI — →12.x). Ba công dụng: (1) **định giá bán** (giá > chi phí + biên — không biết unit cost thì bán theo cảm giác); (2) **phát hiện trục trặc** (unit cost tăng 15% = có gì hỏng ở kỹ thuật — query tệ, cache hụt →6.5, memory leak →3.x); (3) **đo ROI tối ưu** (campaign tối ưu hạ unit cost 10% = nói được bằng tiền). Unit economics là **SLI của tiền** (→11.1 cùng tư duy, đổi chất liệu).

### 2.3 Bảng giá thật của mấy "khoản ẩn"

| Khoản | Bậc | Ghi chú |
|---|---|---|
| **Băng thông ra (egress)** | đắt rõ so với vào | thiết kế: CDN (→6.5), PrivateLink (→9.3), nén, giữ dữ liệu gần người dùng |
| **Cross-region traffic** | trả hai chiều | multi-region (→8.7) có giá mạng thật — tính trước |
| **NAT GB** | theo GB | →9.3 endpoint hoá |
| **Log/metrics đầy** | theo GB ingest + lưu | sampling + retention (→11.2) |
| **Idle** (máy chạy 0% tải) | 100% lãng phí | scale-to-zero (→9.2), kiểm idle report |
| **List price vs cam kết** | chênh 30–70% (I) | RI/SP/commit — mua đúng mức dùng thật |

Bài học lặp: ba khoản đầu (egress, cross-region, NAT) đều là **thiết kế kiến trúc**, không phải điều chỉnh config — FinOps giỏi ngồi trong cuộc họp kiến trúc (→8.6/8.7), không trong bảng tính cuối tháng.

### 2.4 Mua đúng — cam kết, spot, và "cầu thang tiết kiệm"

- **On-demand** (list price): cho phần tải không dự đoán được;
- **Cam kết 1–3 năm** (RI/Savings Plan/CUD): giảm 30–70% cho phần nền ổn định — mua theo **mức đã tối ưu xong** (mua cam kết cho máy thừa = khóa lãng phí);
- **Spot** (giảm 60–90%): cho workload gián đoạn được (batch, CI, stateless có checkpoint — →9.2/12.3);
- **Tắt** (công việc lớn nhất, rẻ nhất): môi trường dev cuối tuần, cluster demo, snapshot cổ, volume rời.
Thứ tự làm: **tắt → đúng size → cam kết** — làm ngược thứ tự là mua cam kết cho sự lãng phí.

### 2.5 Chargeback/showback — chi phí là feedback loop

Showback (cho xem, không trừ) là bước đầu an toàn: mỗi team thấy hóa đơn mình, văn hoá "tài nguyên là của công ty miễn phí" tan trong 2–3 tháng. Chargeback (trừ ngân sách thật) khi tổ chức trưởng thành — làm sớm gây chiến tranh nội bộ. Điều kiện kỹ thuật: **tag chuẩn bắt buộc** (policy IaC — →9.6 chèn tag tự động; tài nguyên không tag = bị "vô chủ" báo mỗi tuần), một shared-cost model rõ (bạclisted: security, platform — ai trả?).

### 2.6 Kinh tế của các quyết định kiến trúc (nối mọi chương)

- Đa vùng active-active (→8.7): x2–3 infra + egress chéo — chỉ khi downtime đắt hơn thế;
- Multi-AZ: +~10–20% — gần như luôn đáng (bảng giá 9 của 11.1);
- Chậm giết service chết: chi phí vận hành + phiền trí — 11.6 sunset là mục FinOps;
- Dữ liệu: retention thật (→5.13) — mỗi GB sống 3 năm là thuê nhà cho dữ liệu không ai thăm;
- AI (→12.x): triệu token là đơn vị mới — inference cache (→6.5 tư duy cache) + model chọn đúng cỡ là hai đòn lớn nhất của 2026.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Egress vs ingress | chênh rõ bậc | V | bảng giá cloud |
| Cam kết giảm giá | 30–70% | I | theo loại/thời hạn |
| Spot giảm | 60–90% | I | gián đoạn được |
| Idle điển hình (không quản) | 20–40% chi phí (I) | I | nghiên cứu ngành |
| Tag coverage mục tiêu | > 95% tài nguyên | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Chi phí là **tham số thiết kế như latency/availability** — quyết định kiến trúc mà không có cột giá là thiết kế mù một chiều; chương này không "đi sau" các chương 8–9 mà ngồi trong cùng cuộc họp.
- **S2:** Tham số trụ: unit cost theo tuần (trend), % list price thực trả, tag coverage, % chi phí không giải thích được (unattributed), số anomaly phát hiện trong 24 h.
- **S3:** Cam kết đổi linh hoạt lấy giá — mua sau khi tối ưu, mức bằng usage p50–p70 của phần ổn định; mua theo đỉnh là trả cam kết cho giờ thấp.
- **S4:** Showback đổi văn hoá lấy 2–3 quý — rẻ nhất trong các can thiệp FinOps mà hiệu quả dài nhất (mọi người sửa hành vi khi thấy con số của mình);
- **S5:** AI làm unit economics thêm đơn vị mới: triệu token có giá đầu vào khác đầu ra (cache/reasoning), và model to nhỏ khác bậc — chọn model theo task (→12.4) là "đúng size" của thế hệ mới; tổ chức không có số này sẽ không biết mình lỗ ở đâu;
- **S6:** Khi "hóa đơn tăng bất ngờ": anomaly detection theo tài nguyên (tăng ở đâu — không phải tổng số) — 80% là một trong: quên tắt, vòng lặp retry (→8.5), log/metric phình (→11.2), hoặc AI endpoint bị gọi bừa (→12.7).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Hóa đơn "to mà không biết của ai" | Tag thiếu | policy tag IaC + báo vô chủ | §2.5 |
| Trả list price ~100% | Không cam kết | sau tối ưu, mua SP/RI | §2.4 |
| Egress phình | Thiết kế kéo dữ liệu sai chỗ | CDN/PrivateLink/locality | §2.3 |
| Idle 30% không ai thấy | Không báo idle | idle report tuần | §2.4 |
| Unit cost tăng dần quý | Trục trặc kỹ thuật chậm (cache hụt, query tệ) | trend unit cost + đối chiếu thay đổi | §2.2 |
| Mỗi tối ưu một lần rồi tuột | Không vòng lặp | FinOps cadence tháng | §2.1 |

---

## 6. Cách đo

```bash
# Bài "1 phút unit cost": dashboards trả lời trong 60 giây —
#   "chi phí/tổng request tuần này vs tuần trước?" (chi phí API cloud ÷ request)
#   Nếu trả không được → thiếu join giữa billing tags và telemetry (việc đầu tiên)

# Idle hunt (tuần): list máy có CPU p95 < 5% và không phải standby-DR (→8.7)
#   — mỗi cái là câu hỏi: tắt? scale-to-zero? hay nó là "bảo hiểm" có chủ đích?
```

Nguyên tắc: **mọi tài nguyên có tag chủ, mọi chủ thấy hóa đơn, mọi thay đổi lớn có ước tính giá** — ba câu này là "SLO của tiền".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay FinOps đầy đủ:** hóa đơn tháng + họp hàng quý (không đủ ở quy mô lớn — nhưng tốt hơn không nhìn); **thay chargeback:** ngân sách theo team với showback (đủ cho đa số tổ chức tới vài trăm người); **thay tool FinOps mua:** cloud-native cost explorer + alert budget (miễn phí, đủ để bắt đầu cả chương).

Năm thấu kính:
- **Kinh tế:** Tối ưu 20–30% chi phí cloud là **nhanh nhất trong các khoản tiết kiệm CNTT** (idle + cam kết + đúng size) — thường bằng vài FTE-lương mỗi tháng; làm một đợt kỷ luật, thu về mỗi tháng.
- **Vận hành:** Chi phí là **telemetry thứ 5** (→11.2): cùng pipeline alert/anomaly, cùng văn hoá metric — không phải bộ phận kế toán riêng biệt;
- **An ninh:** Tài nguyên vô chủ (không tag) cũng là **lỗ hổng an ninh** (máy không ai chăm = không vá — →10.5); bài hunt idle phục hai chương;
- **Lịch sử:** Trung tâm dữ liệu (CAPEX, mua trước 3 năm) → cloud (OPEX, trả theo giờ) → FinOps (2018+, ngành mới vì ai cũng tối ưu hóa đơn) → AI-era unit (triệu token — 2024+): mỗi mô hình tính tiền mới đẻ ra một nghề tối ưu;
- **Người dùng:** "Người dùng" của chương này là lãnh đạo + khách hàng: người đầu cần biết **biên lợi nhuận thật** theo sản phẩm, người sau hưởng giá hợp lý (hoặc chịu giá bù cho sự lãng phí — một trong hai). Minh bạch chi phí là trung thực với cả hai.

---

## 8. Đọc tiếp & bài tập

- Đo lường: **11.2, 11.3** · Kiến trúc có giá: **8.6, 8.7, 9.5** · Sunset hệ thống: **11.6** · Data retention: **5.13** · Unit kinh tế AI: **12.4, 12.6**
- **Bài tập 1:** Đo tag coverage hôm nay (% tài nguyên có tag chủ-team). Mỗi % thiếu là % hóa đơn vô chủ — đề nghị policy IaC chèn tag bắt buộc (→9.6) trong sprint tới.
- **Bài tập 2:** Tính unit cost của một sản phẩm (chi phí cloud theo tag ÷ đơn vị giá trị) tuần này vs tháng trước. Trend là tín hiệu sớm của nợ kỹ thuật — tăng liên tục 3 tuần = có gì đang mòn;
- **Bài tập 3:** Chạy idle hunt (§6): list + quyết từng máy (tắt / giữ có lý do). Ước tính tiết kiệm/tháng — gửi kèm kế hoạch mua cam kết phần còn lại: hai bước này là chiến dịch FinOps đầu tiên trọn vẹn.

