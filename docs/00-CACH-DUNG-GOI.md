# SYSTEMS ATLAS — SA-2028.1 · Gói Học (LEARNER)

> **Đây là gì:** một *bách khoa* hệ thống/backend/platform, **145 chương**, viết để **dạy được từ số 0** và dùng được như **một môn học nhiều tín** thay cả một chương trình.
> **Đóng băng:** 2026-11-16 · **Quy mô:** 50 văn kiện tầng học (15 quiz + 1 quiz nâng cao 60 câu + 15 lab + 15 lời giải + 2 sổ tay ranh giới & điều tra sự cố) · **433 mục bài tập, đã có lời giải 100%**.
> **Bốn định dạng:** `.md` (nguồn, đọc trên máy) · `.html` (đọc/tra trong trình duyệt) · `.docx` (in, chấm bài, sửa) · `.pdf` (phát cho người học).

---

## 1. Hai tầng của cuốn sách — và đừng trộn chúng

| Tầng | Là gì | Ở đâu trong gói |
|---|---|---|
| **Thân sách** (145 chương) | Bản thân kiến thức: P0 → P14, mỗi chương có §0 nhập môn, thân, §vận hành, **§3 số liệu**, và bài tập | xen kẽ theo tuyến học |
| **Tầng học** (50 văn kiện) | Đồ thị + lộ trình, 15 bộ quiz theo cụm, 15 lab tay (`L00–L14`), 1 quiz nâng cao 60 câu (`P15-02-QA`), **15 tệp lời giải**, `P15-05` ranh giới & `P15-06` điều tra sự cố | chèn ngay sau cụm / cuối phụ lục |

Tầng học **không** phải phụ lục: nó nằm đúng chỗ để người đọc không phải nhảy. Nếu bạn chỉ muốn tra cứu, đọc `DRAFT-tham-chieu.md` (tầng học dồn về cuối) — nội dung thân chương **giống hệt** (đã kiểm: 0 khác biệt trên 145/145).

## 2. Đọc theo vai — 4 tuyến có sẵn trong sách

| Bạn là | Tuyến | Thời lượng gợi ý |
|---|---|---|
| Kỹ sư backend 1–3 năm | P1 → P2 → P3 (một nhánh) → P5 → P11 | 6–10 tuần, 2 h/ngày |
| Người mới hoàn toàn (sinh viên năm 3) | P0 → P1 → P4 → P5 → P6 → P7 → P8 → P11 | 2 học kỳ (P15-01 có lộ trình tuần-by-tuần) |
| Kỹ sư hệ thống / platform | P1 → P2 → P9 → P10 → P11 → P13 | 8 tuần + lab L09–L11 |
| Lãnh đạo kỹ thuật / kiến trúc sư | P0 → P11 (đọc §3 số liệu từng chương) → P13 → P14 | 3–4 tuần, 1 h/ngày |

## 3. Cách học một chương (đúng thứ tự, đừng đảo)

1. **§0 Nhập môn** — biết mình đang ở đâu, cần đọc trước gì.
2. **Thân chương** — hiểu cơ chế. Đừng ghi nhớ số ở bước này.
3. **§3 Số liệu** — chỉ đọc *sau* khi hiểu; đây là nơi con số có nghĩa.
4. **Quiz cụm (Bài tập 1)** — tự trả lời *trước* khi mở `P15-02-Q<xx>`.
5. **Bài tập 2–3** — làm, rồi mở `P15-04-S<xx>`. Mỗi lời giải có **3 tiêu chí `Tự chấm`**; đạt 2/3 là đủ để đi tiếp.
6. **Lab nhóm tương ứng** (`P15-03-L<xx>`) — chỉ lab nào chạm hệ bạn thật.

Quy tắc duy nhất cần nhớ: **làm trước, mở sau**. Mở lời giải trước khi làm là đọc tiểu thuyết trinh thám từ trang cuối.

## 4. Chấm điểm (nếu dùng như một môn học)

| Thành phần | Trọng số | Đo bằng |
|---|---|---|
| Quiz theo cụm (15 bộ, 145 câu) | 30% | đáp án ở `P15-02-Q*` |
| Bài tập 2–3 (288 bài) | 40% | `Tự chấm` trong `P15-04-S*` (3 tiêu chí/bài) |
| Lab (`L00–L14`, 15 bộ) | 20% | kết quả đo ghi lại được (số, không phải "đã làm") |
| Bài tổng hợp cuối (1 chương bất kỳ viết lại §3 bằng số của hệ mình) | 10% | có số + có ngày + có nguồn |

Một môn **4 tín**: 45 tiết lý thuyết ánh xạ vào P0–P5 + 45 tiết thực hành vào quiz/lab. "Môn siêu đại cương": P0 + §3 số liệu của mọi chương + P11 — dạy được trong 15 tiết cho người ngoài ngành.

## 5. Thứ không có trong gói (nói rõ để không kỳ vọng sai)

- **Không** có hệ LMS, khoá học video, hay đề thi đóng kín; gói này là *nội dung tự học* (nếu cần giáo trình giảng dạy, bộ kit `SA-2028.1-KIT` có sẵn ngân hàng 40 câu đề mẫu kèm đáp án tại `kit/04-NGAN-HANG-DE-THI.md`).
- **Không** có mã nguồn ví dụ chạy sẵn cho mọi chương — chỉ các bài/lab có lệnh và số đo tái lập được.
- Số liệu có **ngày** và **nguồn**; thứ gì không kiểm được thì đã ghi là "chưa kiểm" hoặc cắt. Nếu bạn đọc lại sau 6 tháng, xem `facts/versions.csv` trước khi tin bất kỳ con số phiên bản nào.

## 6. Ba tệp bạn sẽ dùng nhiều nhất

| Tệp | Dùng khi |
|---|---|
| `QA-RECEIPT.md` | cần chứng minh "không thiếu bài nào" (bảng đếm + 3 lệnh tự kiểm) |
| `FREEZE-MANIFEST.md` | cần biết bản này là bản nào (sha256, kết quả 5 cổng, lệnh build) |
| `P15-01` (chương Đồ thị và Lộ trình) | cần một đường đọc cụ thể tới từng chương, có tiên quyết |
