# 0.3 — Ma trận 5 Lăng kính & 9 Động từ

> **Tầng:** Propaedia · **Mở đầu** · **Trục đọc:** bản đồ · **Động từ liên quan:** Hiểu · Chọn
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 0.1.

**Sợi chỉ đỏ:** *Tiên đề viết xong — nhưng mỗi quyết định cụ thể (kiểu chọn DB hôm qua) duyệt bằng gì cho đều tay?* — trả lời: tiên đề cho biết đứng trên nền nào; chương này cho biết soi một quyết định bằng gì — 5 lăng kính bắt buộc đi qua, 9 động từ phân vai ai làm gì. Hai bộ đó ghép thành ma trận dùng như checklist review. Câu hỏi để lại cho chương sau: *Review đủ lens rồi — con số '99% user hài lòng' trong slide lấy ở đâu, ai kiểm, và nếu nó đã chết thì sao?*

**Thuật ngữ sẽ gặp:** *lăng kính (lens)* — một góc nhìn đánh giá có câu hỏi riêng (hiệu năng, vận hành, tiền…); *động từ* — việc hệ thống làm được với chủ đề: đo, chẩn, kiểm, thiết kế, vận hành, khai tử…; *ma trận lens × động từ* — bàn làm việc: ô trống là chỗ chưa ai nhìn; *ô mù* — lens viết không ra, thường là lens quan trọng nhất; *thấu kính kể chuyện* — cách mỗi chương §7 trình bày đánh đổi bằng ngôn ngữ người.

**Ví dụ mở đầu:** Review thiết kế "thêm Elasticsearch cho tìm kiếm món" của DM: người thì hỏi hiệu năng, người thì hỏi ai trực. Chạy qua 5 lăng kính mới thấy ô trống lớn nhất là khai tử — index này sống 3 năm, ai trả tiền lưu trữ khi log phình gấp mười? Ô không ai soi chính là ô sẽ nổ trước.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Mọi đối tượng kỹ thuật đánh giá qua đủ 5 Lăng kính | Tôi vừa mới nhìn cái này bằng lăng kính nào — và thiếu lăng kính nào? |
| 2 | Mọi chương gắn Động từ chủ đạo | Chương này dạy tôi **làm gì** — chứ không phải **biết gì**? |
| 3 | 5 thấu kính kể chuyện (§7 mỗi chương) là cách hiện thực hoá 5 Lăng kính cho người đọc | Tôi có kể được đánh đổi bằng ngôn ngữ con người không? |
| 4 | Ma trận lens × động từ dùng như checklist review | Kiến trúc này có ô trống nào chưa ai nhìn? |

---

## 2. Cơ chế

### 2.1 Năm Lăng kính đánh giá (5 Lens)

| Lens | Câu hỏi lăng kính | Số liệu đại diện | Chương gắn |
|---|---|---|---|
| **Hiệu năng** | nhanh cỡ nào, cho ai (p50/p95/p99)? | latency, throughput, INP/TTFT | 1.1, 3.x, 12.2 |
| **Tin cậy** | chết thì sao, mất bao nhiêu? | RTO/RPO, error budget, durability | 8.x, 11.1 |
| **Bảo mật** | ai làm gì được với cái này? | attack surface, blast radius, MTTD | 10.x |
| **Vận hành** | 2h sáng ai trực, hiểu gì? | runbook, on-call, observability | 11.x |
| **Chi phí** | bao nhiêu tiền cho một đơn vị giá trị? | unit economics, đ/task, $/GB | 11.5 |

Luật: **một kiến trúc chưa được "đã xem" khi chưa đi qua cả 5 lăng kính** — quyết định thường chỉ thắng ở 2–3 lăng kính và thắng nhờ các lăng kính còn lại không ai hỏi (đó là chỗ nợ thiệt hại tích luỹ).

### 2.2 Chín Động từ

| Động từ | Nghĩa | Phần đại diện |
|---|---|---|
| **Chọn** | quyết giữa các phương án | 3.9, 5.15, 11.7 |
| **Thiết kế** | dựng cấu trúc mới | 8.x, 6.3 |
| **Dựng** | biến thiết kế thành thứ chạy được | 9.6, 9.7 |
| **Kiểm** | chứng minh nó đúng/đủ/an toàn | 12.5, 7.6 |
| **Chạy** | vận hành hằng ngày | 9.1, 11.2 |
| **Chẩn** | tìm bệnh khi có triệu chứng | mọi chương §5 |
| **Bảo vệ** | chống kẻ xấu/vô tình phá | 10.x |
| **Quản trị** | tổ chức, tiền, tiến hoá | 11.5–11.7 |
| **Khai tử** | tắt cái cũ một cách đẹp | 8.8, 11.6 |

Mỗi chương mở đầu ghi **Động từ liên quan** — đọc theo nhu cầu động từ ("tuần này tôi phải *chẩn*", tìm chương gắn Chẩn + đọc §5) là cách dùng atlas hiệu quả hơn đọc tuần tự.

### 2.3 Ma trận lens × động từ — bàn làm việc của review

```
              Chọn   Thiết kế   Dựng   Kiểm   Chạy   Chẩn   Bảo vệ   Quản trị   Khai tử
Hiệu năng      •        •         •      •      •       •                
Tin cậy                          •      •      •       •                         •
Bảo mật        •        •                •              •      •
Vận hành                          •             •       •                •
Chi phí        •        •         •                    •                •          •
```
Cách dùng: đặt kiến trúc/sự cố lên ma trận — ô nào chưa ai trả lời là ô cần một người có tên (không phải "cả team"). Ví dụ kinh điển: *Khai tử × Bảo mật* (hệ sắp tắt vẫn cần vá tới ngày cuối — 11.6 đã chửi); *Chẩn × Chi phí* (vụ "hóa đơn tăng không rõ vì sao" — 11.5).

### 2.4 Năm thấu kính kể chuyện (§7 của mọi chương)

Mỗi chương kết §7 bằng bộ 5: **Kinh tế · Vận hành · An ninh · Lịch sử · Người dùng** — không phải lăng kính đánh giá mà là **ngôn ngữ chuyển dịch**: lấy đánh đổi kỹ thuật kể lại bằng tiền, ca trực, kẻ tấn công, dòng thời gian, và trải nghiệm con người. Lý do tồn tại: quyết định kỹ thuật cần được **người không phải kỹ thuật** phê (11.7) — bản dịch là điều kiện của phê duyệt.

### 2.5 Bộ ba định vị: trục (0.1) × lens (0.3) × động từ (0.3)

Một chương = một điểm trên 7 trục + bộ động từ + 5 lens xuyên suốt. Ba lớp này là **hệ toạ độ 3 chiều** của atlas: vị trí (chương nằm đâu), hành động (động từ), đánh giá (lens). Người viết kỹ thuật tài giỏi là người tự giác đủ ba lớp — người đọc giỏi cũng vậy.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn |
|---|---|---|
| Số Lăng kính | 5 | V |
| Số Động từ | 9 | V |
| Ma trận review | 45 ô | V |
| Thấu kính kể chuyện | 5 (kinh tế/vận hành/an ninh/lịch sử/người dùng) | V |

---

## 4. Suy luận kiến trúc

- **S1:** 5 lens là **bộ lọc bắt buộc** cho mọi ADR — thiếu một lens là thiếu một cuộc phê duyệt (ADR template nên có 5 ô);
- **S2:** Động từ định hình **cấu trúc chương**: chương "Chẩn" giàu bảng sự cố (§5), chương "Chọn" giàu ma trận so sánh (§7) — đọc nhanh bằng cách nhìn động từ;
- **S3:** Ma trận 45 ô là **phân công người**: mỗi ô có chủ là tổ chức trưởng thành; ô "ai cũng" = ô "không ai";
- **S4:** Bộ kể chuyện (§7) là **API giữa kỹ thuật và tổ chức** — cùng nguyên tắc 11.7 (bảng dịch thuật): interface tốt thì quyết nhanh;
- **S5:** AI copilot sinh thiết kế mặc định mạnh ở Hiệu năng, yếu ở Vận hành/Khai tử (dữ liệu huấn luyện thiên về "mới") — ma trận lens là checklist review AI output tốt nhất hiện có;
- **S6:** Khi một quyết định "nghe hợp lý nhưng khó chịu": chạy 5 lens — khó chịu thường là một lens đang báo đỏ mà cuộc họp chưa gọi tên.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân | Lệnh chẩn |
|---|---|---|
| Kiến trúc "đẹp" nhưng sự cố triền miên | Thiếu lens Vận hành lúc quyết | đưa 5 lens vào ADR |
| Hóa đơn/án phí bất ngờ | Thiếu lens Chi phí | unit economics (11.5) |
| Sự cố an ninh "ai cũng ngạc nhiên" | Thiếu lens Bảo mật | threat model (10.1) |
| Chương đọc xong "biết thêm nhưng không làm được gì" | Thiếu động từ rõ | đọc §1 bảng quyết định |
| Quyết định kỹ thuật bị phê duyệt chậm | Thiếu bản dịch §7 | bảng dịch thuật (11.7) |

---

## 6. Cách đo

```bash
# Bài "ô trống" (30 phút, mỗi quý): lấy 3 quyết định lớn nhất quý —
#   chấm 5 lens × 9 động từ: ô nào không trả lời được = rủi ro định vị được
#   (thường lộ: Khai tử chưa ai nghĩ, Chẩn×Chi phí không có metric)
```

Nguyên tắc: **quyết định tốt = 45 ô không sợ soi**.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay 5 lens:** dùng 6 pillar của Well-Architected (AWS/GCP) — tương đương, thêm "sustainability"; atlas giữ 5 để đồng bộ §7 mọi chương. **Thay 9 động từ:** Bloom taxonomy (học thuật hơn, kém vận hành).

Năm thấu kính (đệ quy — chương về lăng kính cũng phải qua lăng kính):
- **Kinh tế:** 30 phút ma trận tránh một quyết định một chiều — ROI của chính chương này;
- **Vận hành:** On-call dùng ma trận làm **bảng phân công ca trực** (ai ô Chẩn nào);
- **An ninh:** lens Bảo mật đứng riêng vì **kẻ tấn công không chia trình bày của bạn** — luôn có ô người ta không hỏi;
- **Lịch sử:** "Trade-off analysis" từ kiến trúc phần mềm thập niên 90 → Well-Architected 2018 → lens ma trận: ngành cố gắng đưa "nghĩ đủ điều" thành checklist suốt 30 năm — vì não người chỉ hỏi câu được hỏi;
- **Người dùng:** Người dùng cuối của ma trận là **đồng nghiệp bạn** — mỗi ô trống là một đêm mất ngủ của ai đó chưa biết mình chịu trách nhiệm.

---

## 8. Đọc tiếp & bài tập

- Trục & vòng: **0.1** · Tiên đề: **0.2** · Provenance: **0.4** · ADR: **11.6** · Đánh đổi kể chuyện: **11.7** · Chú giải biên tập & độ phủ: `facts/ERRATA.md` & `facts/coverage-decisions.csv`
- **Bài tập 1:** Lấy quyết định gần nhất của bạn, đi 5 lens — viết mỗi lens 1 câu; lens nào viết không ra là "ô mù" (và thường là lens quan trọng nhất);
- **Bài tập 2:** Team bạn chia 9 động từ cho mọi người (ai mạnh động từ nào) — rồi đối chiếu với on-call thực tế: động từ Chẩn ai gánh?
- **Bài tập 3:** Thêm 5 ô lens vào template ADR (11.6) tuần này — 5 dòng, đổi chất lượng phê duyệt của cả quý.

