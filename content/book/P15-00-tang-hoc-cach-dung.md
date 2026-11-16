# P15-00 — Tầng học: Cách dùng SYSTEMS ATLAS để học từ đầu

> **Tầng:** Học · **Tầng học SA-EDU (văn kiện mở đầu)** · **Đối tượng:** người tự học — persona a/b/c (xem P15-01) · **Động từ liên quan:** Hiểu · Định hướng
> **Bản:** SA-2028.1 · **Số liệu:** —

---

## 1. Atlas này dành cho ai — và không dành cho ai

**Điểm vào tối thiểu:** bạn biết gõ code cơ bản — biến, hàm, vòng lặp, bằng bất kỳ ngôn ngữ nào. Không cần hơn thế.

**Không dành cho:** (1) người chưa từng lập trình — dạy lập trình từ số 0 nằm ngoài vũ trụ của atlas, hãy học một giáo trình nhập môn rồi quay lại; (2) người cần bằng cấp tín chỉ — atlas không có người chấm bài, không nền toán hình thức, không chứng nhận; nó là **môn siêu đại cương + bản đồ**: dạy cách *nghĩ và quyết định* của nghề hệ thống, còn độ sâu từng môn nằm ở nguồn bên ngoài mà mỗi chương trỏ tới.

**Đối chiếu chuẩn đại học (ACM/IEEE-CS/AAAI CS2023 — 270 giờ CS Core):**

| Cụm CS2023 | Knowledge area | CS Core (giờ) | Atlas phủ? |
|---|---|---|---|
| **Systems Development** | SF 18 · AR 9 · OS 8 · PDC 9 · NC 7 · SEC 6 · DM 10 | **67** | **Vượt** — P1–P5, P9–P10, P13 phủ sâu hơn nhiều + vận hành/AI/biên giới |
| Software Development | SDF 43 · AL 32 · FPL 21 · SE 6 | 102 | Không (ngoài phạm vi dạy lập trình từ số 0) |
| Mathematical & Statistical | MSF | 55 | Không (không dạy nền toán hình thức) |
| Applications | GIT 4 · AI 12 · HCI 8 · SPD 4 | 28 | Một phần (P7 frontend/client, P12 AI) |
| Society, Ethics & Professionalism | SEP | 18 | Một phần (11.6 ADR/tổ chức, 0.4 nhận thức luận) |

> Atlas thay được track Systems Development của một chương trình CS, cộng phần vận hành/AI mà giáo trình đại học thường không có; không thay phần toán hình thức, lý thuyết tính toán và lập trình nhập môn.

Định vị thẳng: học xong lộ trình 16 tuần (persona a), bạn sẽ **đọc hiểu** một kiến trúc hệ thống, biết đặt câu hỏi đúng, biết đo và biết khi nào cần gọi chuyên gia. Bạn sẽ **không** trở thành chuyên gia từng môn — và biết chính xác mình cần đọc gì tiếp để đi sâu từng môn. Đó là hợp đồng của cuốn sách này.

## 2. Atlas là gì — trong một trang

145 chương, 4 quyển, mở đầu bằng P0 (4 chương nền): hệ quy chiếu 7 trục & 4 vòng (0.1), 10 tiên đề A1–A10 (0.2), ma trận 5 lăng kính & 9 động từ (0.3), nhận thức luận nguồn & chống phân rã tri thức (0.4). Mỗi chương là **một vùng kỹ thuật soi qua cùng một khung 8 mục** — vì thế đọc một chương đúng cách là biết đọc cả 144 chương còn lại.

Điểm khác giáo trình thường: chương nào cũng trả lời **"quyết định gì?"** trước, rồi mới đến cơ chế — vì atlas viết cho người làm hệ thống, nơi kiến thức chỉ có giá trị khi đổi được hành động.

## 3. Giải phẫu một chương — đọc mục nào trước theo mục đích

| Mục | Trả lời | Đọc khi nào |
|---|---|---|
| §0 Nhập môn *(đã hoàn tất cho đủ 145/145 chương + 10 nhịp nối sợi chỉ đỏ)* | cần đọc trước gì, sợi chỉ đỏ, thuật ngữ, ví dụ mở đầu | luôn đọc đầu tiên khi **học**; bỏ qua khi tra cứu |
| §1 Quyết định | quyết định nào bị ảnh hưởng? | tra cứu: vào đây trước |
| §2 Nguyên lý nền | cơ chế vận hành thế nào | học |
| §3 Taxonomy | bản đồ lựa chọn trong vùng | học + tra cứu |
| §4 Giao diện hệ thống | chạm vào hệ thống của bạn ở đâu | học |
| §5 Hỏng & chẩn đoán | triệu chứng → nguyên nhân → câu hỏi đúng | tra cứu + vận hành: vào đây trước |
| §6 Cách đo | lệnh/code chẩn đoán | khi cần bằng chứng |
| §7 Decision boundary + 5 thấu kính | tự quyết tới đâu, khi nào gọi chuyên gia | luôn đọc cuối chương |
| §8 Nguồn, thuật ngữ & bài tập | từ vựng, đọc-gì-tiếp, luyện | ôn + mở rộng |

## 4. Ba tốc độ đọc

1. **Tra cứu (5–15 phút):** vào bằng mục lục hoặc trục (0.1) → đọc §1 → §5 → §7. Không đọc tuần tự.
2. **Học (60–90 phút/chương):** §0 → §1 → §2 → §4 → §5 → §6 → làm 1–2 bài tập → §8 ghi "đọc gì tiếp" cho riêng bạn.
3. **Ôn (15–30 phút):** §8 từ vựng che nghĩa → §5 bảng sự cố → quiz cụm (P15-02-Qxx).

## 5. Bộ điều hướng: nhãn & ký hiệu

- **Tốc độ đổi của tri thức** (từ 0.4): 🔥 thay đổi trong ~4 tuần (hằng tháng phải verify) · 🌡 ~1 quý · 🧊 ~1 năm. Chương 🔥 đọc số hiện hành bằng versions.csv; chương 🧊 học nguyên lý là chính.
- **Nhãn nguồn:** **P** sơ cấp (docs/RFC/chuẩn/paper — thắng khi mâu thuẫn) · **I** độc lập đo lường (ghi điều kiện đo) · **V** vendor (chỉ tin cho hành vi sản phẩm cụ thể) · **E** ước tính (phải ghi cơ sở). Khi hai nguồn cãi nhau: tìm P; không có P thì ≥2 nguồn I đồng hướng, ghi bậc độ lớn.
- **Cross-ref `→x.y`:** mũi tên trỏ chương ngữ cảnh. Khi học tuần: gặp ref chưa đọc thì ghi lại — lộ trình sẽ đưa bạn tới; khi tra cứu: chỉ nhảy theo khi thực sự cần.

## 6. Làm bài tập & tự chấm

Mỗi chương có 3 bài tập, thiết kế để làm **bằng máy và dữ liệu của chính bạn**. Trình tự:

1. Làm trước — không nhìn gợi ý; kẹt quá 20 phút thì đọc §2 lại, rồi mới đối chiếu lời giải ở `P15-02-Qxx` (bài 1) hoặc `P15-04-Sxx` (bài 2–3);
2. Bài **đo**: ghi con số + điều kiện (máy, dữ liệu, giờ, phiên bản). Con số bạn đo được luôn đáng hơn con số trong sách — sách chỉ cho bậc độ lớn;
3. Bài **quy trình/tính**: so với khung đáp án, tự chấm bằng 3 tiêu chí bài đó nêu;
4. Chênh lệch giữa lời giải của bạn và đáp án là chỗ đáng ghi lại — đó là kiến thức của riêng bạn.

Không có giáo viên chấm thay bạn — nên quy tắc của cả atlas áp luôn cho chính bạn: **thà thiếu đúng còn hơn đủ sai**. Không chắc → truy nguồn P/I, đừng tự bịa con số.

## 7. Checkpoint & nhịp học

- **Cuối mỗi cụm:** quiz 8 câu (`P15-02-Qxx`, đủ 15/15 cụm). **≥6/8 → đi tiếp; <6 → đọc lại §2 và §5 của cụm**, không đọc thêm chương mới. Sau khi xong toàn bộ, kiểm tra chéo quyết định bằng bộ quiz nâng cao 60 câu (`P15-02-QA`).
- **Lab tay:** mỗi cụm có 1 lab một trang (`P15-03-L00..L14`, đủ 15/15 cụm) — làm **sau quiz** của cụm, khi có 1–2 giờ; kết quả lab là "con số bạn đo được" (quy tắc §6.2: ghi kèm máy, phiên bản, ngày). Lab không chặn tuần sau — kẹt thì bỏ qua và quay lại.
- **Nhịp bền:** 3–6 chương lõi mỗi tuần (bảng tuần ở P15-01). Nhanh hơn → hiểu lơ mơ; chậm hơn → mất đà. Lộ trình là defaults, không phải deadline.
- Thấy atlas sai chỗ nào → ghi errata (0.4). Học mà phản biện lại tài liệu là kỹ năng cao nhất cuốn sách này dạy.

## 8. Sau lộ trình

Bạn sẽ đứng ở lối ra của bản đồ: 11.8 có 24+ lab để tay; P14 mở 11 ngành biên giới theo hướng nghề; P13 là playbook theo lớp tải; versions.csv là con số hiện hành khi cần. **Atlas thành công khi bạn không còn cần nó mỗi ngày** — vì bản đồ đã nằm trong đầu, và bạn biết mình phải đọc gì tiếp.

