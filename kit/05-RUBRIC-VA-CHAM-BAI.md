# RUBRIC CHẤM BÀI — dùng cho cả 3 môn

> **Nguyên tắc gốc:** *không có số thì không có điểm; có số mà không có ngưỡng hành động thì được nửa điểm.*
> Rubric này viết để **chấm nhanh** (60–90 giây/bài) và để **sinh viên tự chấm trước khi nộp** — mỗi bài tập trong sách đã có 3 tiêu chí `Tự chấm`, rubric chỉ là bản mở rộng của chúng thành thang điểm.

---

## 1. Ba loại bài và thang điểm riêng

| Loại bài | Ví dụ | Chấm theo |
|---|---|---|
| **Bài đo** (lab) | throttle ratio, cold start p99, `vmstat` cs/s | số đo có tái lập được không + kết luận đúng + ghi điều kiện |
| **Bài tính** | error budget, pool size, PUE, xác suất rebuild | công thức + đơn vị + kiểm bậc độ lớn |
| **Bài quy trình** | ADR, saga, runbook, threat model, rubric an ninh | đủ trường bắt buộc + có người/ngày + tiêu chí kiểm được |

## 2. Thang 10 điểm cho một bài lab

| Điểm | Tiêu chí | Kiểm nhanh (60 giây) |
|---|---|---|
| 0 | không nộp / chỉ chép kết quả từ sách | trùng nguyên văn số trong sách ⇒ 0 |
| 2 | có lệnh nhưng không có số | không thấy một con số nào có đơn vị ⇒ dừng |
| 4 | có số, **thiếu điều kiện đo** | không ghi máy/tải/phiên bản/cửa sổ thời gian |
| 6 | có số + điều kiện, **kết luận mơ hồ** | câu kết luận không nêu "vậy phải làm gì" |
| 8 | có số + điều kiện + **một hành động đề xuất** | hành động có ngưỡng ("nếu > 5% thì…") |
| 10 | như 8 **+ một lần đo lại sau thay đổi** hoặc **giải thích được kết quả rỗng** | có số trước/sau, hoặc giải thích vì sao không đổi |

**Điểm cộng hiếm (chỉ 1–2 sinh viên/lớp):** phát hiện **dụng cụ đo sai** (ví dụ: dùng `%CPU` khi bị cgroup throttle; đo cold start lẫn warm; `curl` từ máy trong cùng DC rồi kết luận về người dùng). Đây là dấu hiệu của người sẽ làm được việc, đáng ghi lại cho giảng viên.

## 3. Thang 10 điểm cho một bài tính

| Điểm | Tiêu chí |
|---|---|
| 0 | không có công thức, chỉ có đáp số |
| 3 | công thức đúng, **sai đơn vị** (giây/phút, bit/byte, GB/GiB) |
| 5 | đúng số nhưng **không kiểm bậc độ lớn** (không nhận ra kết quả vô lý) |
| 7 | đúng + có kiểm bậc (so với một mốc đã biết) |
| 9 | như 7 **+ nêu giả định** đã dùng (giá điện, URE, tỉ lệ nén) **và ngày tra giá** |
| 10 | như 9 **+ một kết luận quyết định** ("vì vậy chọn RAID10, không RAID5") |

## 4. Rubric riêng: ADR (1 trang) — 15 điểm

| Trường | Điểm | Thiếu thì trừ |
|---|---|---|
| Bối cảnh có **số** (tải, ngân sách, hạn) | 3 | −3 |
| ≥2 phương án, có **phương án bị loại + lý do** | 4 | −4 |
| Quyết định viết ở thể khẳng định, không "cân nhắc" | 2 | −2 |
| Hệ quả: cái gì **dễ đi**, cái gì **khó đi** | 3 | −3 |
| **Hạn xét lại** đo được ("nếu > 5.000 rps hoặc bill > $20k") | 3 | −3 |

## 5. Rubric riêng: luồng ghi không mất dữ liệu — 15 điểm

| Hạng mục | Điểm |
|---|---|
| Bảng bước + **compensation** cho từng bước | 4 |
| Bước **không hoàn tác được** được đánh dấu và dời về **cuối** | 4 |
| Test bơm trùng (cùng `event_id` 3 lần) ⇒ 1 bản ghi | 4 |
| Timeout ở đúng ranh giới + test cho ca timeout | 3 |

## 6. Rubric riêng: ADR an ninh — 15 điểm

| Hạng mục | Điểm |
|---|---|
| Nêu **chống ai** bằng loại kẻ tấn công cụ thể | 3 |
| Nêu **không chống ai** ≥3 mục | 4 |
| ≥1 đường tấn công được đo bằng **số bước** tới dữ liệu | 3 |
| Bằng chứng: test/red-team/log (không phải ý kiến) | 3 |
| Chữ ký người nhận rủi ro + ngày | 2 |

## 7. Chấm thi viết (120 phút, 100 điểm)

Điểm chia theo **loại tư duy**, không theo số câu:

| Loại | Trọng số | Đặc điểm bài làm được điểm cao |
|---|---|---|
| Tính | 32% | có công thức, đơn vị, kiểm bậc, kết luận |
| Chẩn đoán | 28% | nêu 2–3 giả thuyết **và** phép đo phân biệt chúng |
| Phán đoán | 15% | chỉ ra điều kiện khiến tuyên bố sai |
| Kỹ năng | 25% | code chạy được / lược đồ đúng / test đúng chỗ |

**Trừ điểm tự động:** dùng từ "tối ưu", "nhanh", "ổn định", "bảo mật cao" mà không có số hoặc ngưỡng — **−2 điểm/lần**, tối đa −10. Quy tắc này dạy đúng thứ mà nghề cần: nói bằng số.

## 8. Chấm theo tiến bộ (dùng cho lớp đông)

| Mốc | Mô tả | Cách cho điểm |
|---|---|---|
| M1 | Trả lời đúng cơ chế, chưa có số | 50% |
| M2 | Có số, chưa có quyết định | 70% |
| M3 | Có số + quyết định + điều kiện | 90–100% |

Cho sinh viên **tự xếp mốc** trước khi nộp; bài nào tự xếp lệch quá 1 mốc ⇒ 1 buổi nói chuyện 10 phút. Kinh nghiệm: tự chấm sai là tín hiệu sớm nhất của việc hiểu nông, rẻ hơn mọi bài kiểm.
