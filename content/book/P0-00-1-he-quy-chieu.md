# 0.1 — Hệ quy chiếu 7 Trục & 4 Vòng Vũ trụ

> **Tầng:** Propaedia · **Mở đầu** · **Trục đọc:** bản đồ · **Động từ liên quan:** Hiểu · Định hướng
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** Không cần — chương mở đầu của cả atlas; chỉ cần biết gõ code cơ bản.

**Sợi chỉ đỏ:** *Hai đồng sáng lập DM cãi nhau 'monolith hay microservices' ba tuần không đi tới đâu — chuyện gì thật sự đang diễn ra trong cuộc cãi đó?* — cuốn sách mở ra bằng chính câu hỏi đó: hai người kỹ thuật cãi nhau ba tuần thường vì đứng ở hai toạ độ khác nhau, không phải vì thiếu sự thật. Chương này dựng hệ quy chiếu 7 trục để cuộc cãi trở thành cuộc đo. Câu hỏi để lại cho chương sau: *Đã có toạ độ để cãi cho ra — nhưng cả team đang đứng trên những giả định nào chưa ai nói ra?*

**Thuật ngữ sẽ gặp:** *hệ quy chiếu* — bộ cách đặt tên và đo một vấn đề để tranh luận trên cùng một nền; *trục* — một chiều phân loại, như trục ngang/dọc của đồ thị; *vòng* — nhóm chương cùng độ gần biên giới của bản đồ; *tiên đề* — điều coi đúng ban đầu, không chứng minh lại mỗi lần (chương 0.2); *lăng kính (lens)* — góc nhìn chuẩn hoá khi soi một hệ thống (chương 0.3).

**Ví dụ mở đầu:** Ba kỹ sư DM họp vì "app chậm": người nghĩ tới CPU, người nghĩ tới truy vấn DB, người nghĩ tới quy trình deploy. Cả ba có thể cùng đúng — nhưng họp đi vòng vì mỗi người đứng trên một bản đồ khác nhau. Chương này vẽ bản đồ dùng chung cho 144 chương phía sau: có quy chiếu thì "chậm vì đâu" trả lời bằng số đo, không bằng cảm tính.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Định vị mọi chủ đề trên cùng một hệ quy chiếu (7 trục) | Tôi đang nói về tầng nào — nói cùng ngôn ngữ vị trí với đồng nghiệp chưa? |
| 2 | Mỗi chương thuộc một Vòng đồng tâm (0–3) | Chương này tôi cần **làm nghề** hay chỉ cần **đọc hiểu để quyết**? |
| 3 | Mỗi phần = đúng một trục chủ đạo (bài học audit 2026.11) | Câu chuyện này có bị trộn hai trục (phân tán + nền tảng) không? |
| 4 | Lộ trình đọc theo vai (không tuần tự) | Tôi là ai — Dev/SRE/Data/Lead — và đường đọc của tôi là gì? |

---

## 2. Cơ chế

### 2.1 Vì sao cần hệ quy chiếu trước 145 chương

Không có toạ độ, mọi tranh luận kỹ thuật là hai người đứng ở hai tầng khác nhau chỉ trỏ nhau "chậm", "đắt", "không an toàn". Atlas dựng **7 trục toạ độ** để mọi chương (và mọi cuộc họp) trả lời được: *chủ đề này nằm ở đâu, đổi tham số nào của hệ tôi?*

### 2.2 Bảy trục toạ độ

| Trục | Câu hỏi của trục | Chương đại diện |
|---|---|---|
| **Vật chất** | Năng lượng/diện/vật liệu giới hạn gì? | 1.x, 14.1, 14.3 |
| **Thời gian vòng đời** | Thứ gì đổi theo giờ/tháng/năm? | 4.8, 8.8, 11.6 |
| **Phạm vi thực thi** | Chạy ở đâu: chip/máy/pod/region/client? | 2.x, 6.x, 8.7, 9.x |
| **Trạng thái dữ liệu** | Sống ở đâu, tươi cỡ nào, của ai? | 5.x, 6.3, 8.3–8.4 |
| **Giao tiếp** | Ai nói với ai, bằng giao thức gì? | 4.x, 14.2 |
| **Con người/Tổ chức** | Ai sở hữu, ai vận hành, ai trả tiền? | 11.5–11.7 |
| **Ràng buộc** | Luật/định lý/tiền/thời gian ép gì? | 0.2, 8.1, 10.8 |

Bài học lịch sử của chính atlas: kế hoạch 2026.11 từng **trộn 4 trục trong một phần** (phân tán + cloud + an ninh + vận hành chung "kiến trúc") — audit theo 6 khung chuẩn ngành (ACM/IEEE CS2023, SWEBOK v4, INCOSE SEBoK, Well-Architected, DAMA-DMBOK2, NIST CSF 2.0) buộc tách lại mỗi phần **một trục chủ đạo**. Đó là lý sao P8/P9/P10/P11 là bốn phần riêng.

### 2.3 Bốn Vòng đồng tâm

```
VÒNG 3 — NGOÀI VŨ TRỤ: giá trị đạo đức/chính trị/thị trường thuần tuý → loại trừ có tuyên bố
VÒNG 2 — VŨ TRỤ BIÊN GIỚI: 11 ngành lân cận (P14, 28 ch) — đọc hiểu để quyết & biết gọi chuyên gia
VÒNG 1 — VÀNH LIÊN NGÀNH: kinh tế, tổ chức, PM/pháp lý (11.5–11.7) — hệ điều hành con người
VÒNG 0 — LÕI: silicon → kernel → runtime → giao thức → dữ liệu → client → phân tán → cloud → an ninh → SRE → AI (P1–P13)
```
Tiêu chí phân vòng không phải "khó/dễ" mà là **mức bạn phải hành nghề**: Vòng 0 = quyết định hằng tuần bằng tay bạn; Vòng 1 = quyết định hằng tuần bằng tổ chức; Vòng 2 = quyết định khi chạm biên — phần còn lại là của chuyên gia (D-137).

### 2.4 Ba tầng độ sâu

- **Tầng 0 (Propaedia):** P0 — bản đồ, tiên đề, nhận thức luận (chính phần này);
- **Tầng 1 (Lồng/Deep):** P1–P13 — khung 8 mục, 2.500–6.000 từ/chương;
- **Tầng 2 (Biên giới):** P14 — cụm hồ sơ ngành theo Khung B;
- **Tầng 3 (Danh mục):** phạm vi loại trừ — ghi rõ để "đủ" có nghĩa đo được (§7 0.2, nguyên tắc N1).

### 2.5 Lộ trình đọc theo vai

| Vai | Đường đọc ưu tiên |
|---|---|
| Dev backend mới | 0.1–0.4 → 3.x (runtime mình) → 4.x → 8.3/8.5 → 11.1–11.2 |
| SRE/Ops | 0.x → 1.x → 2.x → 8.5/8.7 → 9.x → 11.x → 10.7 |
| Kiến trúc sư/Lead | 0.x → đọc §1+§4 mọi phần → đào sâu nơi dự án chạm → 11.6–11.7 |
| Data/AI | 5.x → 8.3–8.4 → 12.x → 13.3–13.5 → 14.4 |
| FE/Mobile | 6.x → 7.x → 4.x → 11.1–11.2 → 10.3–10.4 |

Chi tiết hơn (kèm lab) ở **11.8**. Quy tắc: mỗi chương mở đầu bằng **bảng quyết định §1** — đọc bảng trước; chương không chứa quyết định của đời bạn thì để sau.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn |
|---|---|---|
| Số trục | 7 | V |
| Số vòng | 4 (ứng 3 tầng độ sâu + danh mục) | V |
| Số phần | 15 (P0–P14) | V |
| Số chương | 145 | V |
| Số quyết định nghiệm thu | 139 (CSV) | V |

---

## 4. Suy luận kiến trúc

- **S1:** Hệ quy chiếu là **hợp đồng ngôn ngữ** của tổ chức — cùng toạ độ thì tranh luận thành quyết định; khác toạ độ thì tranh luận thành khẩu vị;
- **S2:** Mỗi phần một trục chủ đạo là **ràng buộc chống ô nhiễm** — đổi trục phải tách phần (như 2026.11 → 2026.13 đã làm), không "thêm vào cho đủ";
- **S3:** Vòng đồng tâm trả lời **hợp đồng đào tạo**: Vòng 0 là nghề, Vòng 2 là ngoại ngữ — allocate giờ học theo vòng (11.8 §2.1);
- **S4:** P14 "biên giới" không phải phụ lục trang trí — mọi chương Vòng 0 đều gọi tới nó khi chạm giới hạn vật lý (băng thông HBM ở 12.2, nhiệt ở 14.3, RF ở 6.4);
- **S5:** AI kéo một chủ đề mới (agent) đi **xuyên mọi vòng** (runtime 12.4, tổ chức 11.6, biên giới 14.4) — hệ quy chiếu là cách atlas theo kịp mà không viết lại;
- **S6:** Khi tranh luận "chưa thấy ai nói về X": đặt X lên 7 trục — hoặc X nằm Vòng 3 (loại trừ có chủ ý), hoặc X thuộc chương nào đó (tra mục lục), hoặc **X là lỗ hổng** (báo errata — 0.4).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân | Lệnh chẩn |
|---|---|---|
| Họp kỹ thuật xoay vòng không chốt | Hai bên khác trục | vẽ 7 trục, ghim vị trí từng ý |
| "Atlas này thiếu X" | X ở Vòng 3 / ở chương khác | tra §2.3 + mục lục |
| Đọc tuần tự rồi kiệt sức | Sai đường theo vai | bảng §2.5 |
| Câu chuyện trộn hai phần | Phần đang hai trục | tách theo audit 2026.11 |
| P14 đọc như phụ lục | Quên nó là biên giới quyết định | đọc §4 B.4 mỗi cụm |

---

## 6. Cách đo

```bash
# Thí nghiệm toạ độ (5 phút đầu mọi cuộc họp kiến trúc):
#   viết câu tranh luận ra, rồi chấm: trục nào? vòng nào? tầng nào?
#   90% "bất đồng kỹ thuật" là hai dòng khác trục — phát hiện sớm đổi
#   cuộc họp từ cãi nhau thành chia việc
```

Nguyên tắc: **toạ độ trước, ý kiến sau**.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay hệ quy chiếu riêng:** dùng một khung chuẩn ngành làm xương (SWEBOK/CS2023) — hợp lệ, ít "của mình" hơn; atlas đối chiếu cả sáu khung ở khâu audit. **Thay 4 vòng:** phân tầng theo "tầng OSI mở rộng" (quen thuộc nhưng chỉ phủ trục giao tiếp).

Năm thấu kính:
- **Kinh tế:** Hệ quy chiếu giảm **giờ họp** — chi phí lớn nhất của tổ chức kỹ thuật là các cuộc họp không cùng toạ độ;
- **Vận hành:** On-call cần biết "lỗi này tầng nào" trong 30 giây — chính là trục phạm vi thực thi;
- **An ninh:** Trust boundary (10.1) là **trục ranh giới hiện thân** — vẽ đúng ranh giới là nửa an ninh;
- **Lịch sử:** Từ sơ đồ OSI 7 tầng (1984) → taxonomy DAMA/NIST → "khung" Well-Architected: ngành lặp lại cùng một nhu cầu **đặt tên cho vị trí** mỗi khi hệ phức thêm một bậc;
- **Người dùng:** Người đọc là người dùng của chương này — mục tiêu thiết kế: *tìm được chương cần đọc trong ≤ 2 phút* (mục lục + 7 trục + lộ trình vai).

---

## 8. Đọc tiếp & bài tập

- Tiên đề: **0.2** · Lăng kính & động từ: **0.3** · Nhận thức luận: **0.4** · Lộ trình + lab: **11.8** · Audit độ phủ: `facts/coverage-decisions.csv` & `facts/coverage-incidents.csv`
- **Bài tập 1:** Lấy 3 bất đồng kỹ thuật gần nhất của team, chấm trục + vòng cho mỗi bên — bao nhiêu % là khác toạ độ (không phải khác sự thật)?
- **Bài tập 2:** Viết đường đọc của chính bạn (5 phần, thứ tự, vì sao) — rồi cho 1 đồng nghiệp mới dùng thử;
- **Bài tập 3:** Chọn 1 chủ đề bạn hay tranh cãi (cache? mesh? test?), viết nó lên 7 trục — chủ đề sẽ tự "hồ sơ hoá" và cuộc tranh luận tới sẽ ngắn hơn một nửa.
