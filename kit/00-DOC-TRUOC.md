# BỘ MÔN HỌC — SA-2028.1 KIT

### Biến bộ sách 145 chương thành **chương trình dạy được trong 1–2 năm**, không phải "tài liệu tham khảo"

> **Gồm:** 1 môn nền tảng (4 tín) · 1 môn hệ thống thực (4 tín) · 1 môn tự chọn (4 tín) · 1 môn siêu đại cương (15 tiết) · ngân hàng đề 40 câu có đáp án · rubric chấm · bộ slide 30 chương xương sống `SYS101–103` (`kit/slides/`).
> **Đi kèm:** `SYSTEMS-ATLAS-LEARNER-SA-2028.1.pdf` (sách + tầng học `P15-02-QA` 60 câu nâng cao) — kit này **không** chứa lại nội dung sách, chỉ chứa **cách dạy**.

---

## 1. Bản đồ chương trình — 145 chương được chia hết, không chồng lấn

| Môn | Tín | Cụm | Số chương | Chương bắt buộc đọc kỹ |
|---|---|---|---|---|
| **SYS101** Nền tảng hệ thống (`01`) | 4 | P0, P1, P2, P3, P4 + 5.1, 5.2, 5.4 | **45** | 11 |
| **SYS102** Hệ thống thực (`02`) | 4 | P5 (13 còn lại), P6, P7, P9, P10, 8.1–8.3 | **45** | 10 |
| **SYS103** Quy mô & biên giới — tự chọn (`02b`) | 4 | 8.4–8.8, P11, P12, P13, 18 chương chọn từ P14 | **45** | 9 |
| **SYS100** Hệ thống quanh ta (siêu đại cương, `03`) | 0 | trích từ toàn sách | 15 tiết | — |

**Cộng: 145/145 chương có chỗ trong chương trình (45 + 45 + 45 = 135 chương giảng chính + 10 chương biên giới `P14` trong phụ lục "đọc khi cần" của sách).** Tương thích khung chuẩn ACM/IEEE/AAAI CS2023 (AR/OS/NC/SF/PDC/DM/SE/SEC/AI). Không chương nào bị bỏ rơi.

## 2. Vì sao chia như vậy (tiêu chí phân vùng, không phải sở thích)

1. **Theo câu hỏi nghề, không theo môn học cũ.** SYS101 trả lời "cái gì nhanh/chậm và vì sao"; SYS102 trả lời "làm sao để hệ sống được với người dùng thật"; SYS103 trả lời "làm sao để hệ sống được với quy mô, tiền, và thế giới bên ngoài".
2. **Theo tiên quyết thật.** Mỗi môn chỉ dùng kiến thức của môn trước — sách có `P15-01` (đồ thị tiên quyết) và `facts/prereq-edges.csv` để kiểm: mọi cạnh "Đọc trước" đều nằm trong môn trước hoặc cùng môn.
3. **Theo khối lượng giảng dạy được.** 45 chương / 45 tiết = ~1 chương/tiết, thực tế giảng sâu 11–12 chương và *định vị* phần còn lại ("biết nó ở đâu, khi cần thì mở") — đúng cách một bác sĩ đa khoa học 900 trang nội khoa.

## 3. Ba cách dùng kit

| Bạn là | Dùng |
|---|---|
| **Giảng viên đại học** | `01`, `02`, `02b`, `04`, `05`, `slides/`: giáo trình 2–3 học kỳ, lịch tuần, đề thi, rubric và slide mẫu |
| **Trưởng nhóm kỹ thuật / mentor** | `01` (rút còn 8 tuần: tuần 3–12), `05`: onboarding nhân viên mới, chấm bài tập nội bộ |
| **Người ngoài ngành / quản lý** | `03` (15 tiết) + `04` phần A + E: đủ để không bị dắt khi mua và giám sát hệ thống |

## 4. Điều kit này **không** làm (nói trước để khỏi kỳ vọng sai)

- **Slide có mẫu khởi điểm cho 30 chương `★` của cả ba môn `SYS101–103` (`11` của SYS101 + `10` của SYS102 + `9` của SYS103 trong `kit/slides/`), không làm thay toàn bộ 145 chương.** Các chương còn lại (`34`/`35`/`36` tuỳ môn) do giảng viên tự chọn số từ §0 + §3 khi giảng.
- **Không có đề thi đóng kín.** Ngân hàng 40 câu là **mẫu và chuẩn chất lượng**; mỗi học kỳ nên đổi 30%, giữ nguyên 5 câu "kinh điển" (kèm `P15-02-QA` 60 câu nâng cao trong sách).
- **Không thay được lab có người hướng dẫn.** 15 bộ lab (`15/15` từ `L00` đến `L14`) cần một người biết cách đọc số đo — đó là chi phí thật của môn này, không phải sách.

## 5. Ba việc phải làm trước buổi đầu tiên

1. **Dựng VM Linux 2 vCPU** (hoặc một máy yếu) và chạy thử 3 lab: L1 (cache vs RAM), L2 (`memory.high`), L3 (`orjson`). Nếu chạy được trên 2 vCPU thì sinh viên nào cũng chạy được.
2. **Chọn 5 chương "★" của học kỳ** và đọc lại §3 của chúng — giảng viên phải biết trước con số nào sẽ hỏi.
3. **In rubric (§05) và phát từ tuần 1.** Sinh viên biết mình bị chấm bằng "có số + có ngưỡng" ngay từ buổi đầu sẽ viết khác hẳn từ bài số 1 — đây là can thiệp rẻ nhất trong cả học kỳ.

## 6. Đánh giá song song: kit có tự dùng được không?

| Câu hỏi | Trả lời đo được |
|---|---|
| Một giảng viên chưa từng đọc sách có dạy được tuần 1 bằng kit? | Có — tuần 1 chỉ cần 0.1–0.3 + rubric §05; 90 phút chuẩn bị |
| Sinh viên có biết mình được chấm thế nào từ tuần 1? | Có — rubric phát tuần 1, mọi bài tập trong sách đã có 3 tiêu chí `Tự chấm` |
| Có chương nào không có chỗ trong chương trình? | **0** — 145/145 được phân; 38 chương nằm ở mức "định vị + đọc khi cần" |
| Có môn nào dạy trùng chương? | **0** — bản đồ chia hết, không chồng lấn (kiểm bằng danh sách chương mỗi môn) |
