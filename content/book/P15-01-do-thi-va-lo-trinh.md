# P15-01 — Đồ thị Tiên quyết & Ba Lộ trình Persona

> **Tầng:** Học · **Tầng học SA-EDU** · **Đối tượng:** người tự học · **Động từ liên quan:** Định hướng · Chọn
> **Bản:** SA-2028.1 · **Dữ kiện:** `facts/prereq-edges.csv` (trích tự động) + `facts/learning-paths.csv` (lộ trình lõi, máy đọc được)

---

## 1. Đồ thị tiên quyết — dữ kiện thật

Toàn bộ cross-ref `→x.y` của 145 chương được trích tự động (`tools/prereq_graph.py`): **1.237 lượt tham chiếu → 894 cạnh riêng biệt → 129 đích**. Mười chương được trỏ nhiều nhất — nơi nhiều vùng của atlas neo vào:

| Chương | Được trỏ | Ý nghĩa |
|---|---|---|
| 4.8 Vòng đời API | 38 lượt / 22 chương | hợp đồng giao tiếp là nền của mọi thứ gọi nhau |
| 11.1 SLI/SLO | 32 / 21 | ngôn ngữ chung của "tốt hay chưa" |
| 11.2 OpenTelemetry | 27 / 18 | cách nhìn thấy hệ thống |
| 5.7 Event/Stream | 26 / 20 | xương sống dữ liệu di chuyển |
| 8.5 Chịu lỗi | 25 / 17 | mẫu thiết kế dùng lại nhiều nhất |
| 10.5 Chuỗi cung ứng | 24 / 15 | mọi hệ đều đứng trên dependency |
| 8.7 Đa vùng/DR | 24 / 14 | ranh giới cuối của tính sẵn sàng |
| 12.2 Inference serving | 21 / 11 | cổ chai mới của hệ hiện đại |
| 5.13 Quản trị dữ liệu | 21 / 17 | dữ liệu là tài sản có quy |
| 12.5 Evals | 21 lượt | AI phải đo được mới ra sản phẩm |

**Lưu ý quan trọng:** các tham chiếu trong atlas là "xem thêm" **hai chiều** (sách tra cứu), không phải tiên quyết tuyệt đối — chương 5.2 trỏ 11.1 không có nghĩa là không đọc được 5.2 trước 11.1. Vì thế bản đồ **không tự** thành lộ trình; cần một tuyến học dựng tay — đó là việc của tài liệu này.

## 2. Cách đọc bảng lộ trình

- **Lõi** = chương bắt buộc của tuần (2–6 chương). **Mở rộng** = đọc theo nhu cầu, không chặn tuần sau.
- **Checkpoint** = quiz cụm (P15-02-Qxx) sau khi cụm đã học đủ lõi; quy tắc ≥6/8 ở P15-00 §7.
- **Co giãn:** gấp đôi thời gian nếu cần — lộ trình giữ nguyên thứ tự; chỉ học lõi nếu thiếu giờ; thêm toàn bộ mở rộng nếu đang đúng nghề.
- **Hoán đổi theo nghề** được ghi sau mỗi bảng.

## 3. Persona (a) — Người mới biết code cơ bản · 16 tuần

Học từ dưới lên theo đúng thứ tự sách: vật lý → kernel → runtime → giao tiếp → dữ liệu → client → phân tán → cloud/an ninh → vận hành → AI. Lõi 48 chương; mở rộng + nhảy đưa người mới qua 121/145 chương — phần còn lại (playbook P13 13.2–13.7 và P14 chuyên sâu) theo ngả "Sau tuần cuối" (§6).

| Tuần | Lõi | Mở rộng | Checkpoint |
|---|---|---|---|
| 1 | 0.1 · 0.2 · 0.3 · 0.4 · 1.1 | — | Q00 |
| 2 | 1.2 · 1.3 · 1.4 | 1.5 · 14.1.1 | — |
| 3 | 1.6 · 1.7 · 1.8 | 1.9 · 1.10 · 14.1.3 (nhảy §0–§2) · 14.3.1 | Q01 |
| 4 | 2.1 · 2.2 · 2.3 | — | — |
| 5 | 2.4 · 2.5 · 3.1 | 2.6 · 2.7 · 2.8 | Q02 |
| 6 | 3.9 · 3.10 | runtime bạn dùng (một trong 3.2–3.7) · 3.8 · 3.11 | Q03 |
| 7 | 4.1 · 4.2 · 4.3 | 4.4 · 14.2.1 | — |
| 8 | 4.7 · 4.8 · 4.9 | 4.5 · 4.6 | Q04 |
| 9 | 5.1 · 5.2 | 5.3 · 5.4 | — |
| 10 | 5.7 · 5.15 · 5.16 | 5.5 · 5.6 · 5.8–5.14 chọn theo nhu cầu | Q05 |
| 11 | 6.1 · 6.2 · 6.3 | 6.4–6.7 · cả P7 nếu làm web | Q06 (Q07 nếu học P7) |
| 12 | 8.1 · 8.2 · 8.5 | 8.3 · 8.4 · 8.6 · 8.7 · 8.8 · 14.8.2 | — |
| 13 | 9.1 · 9.4 · 10.1 | 9.2 · 9.3 · 9.5–9.7 | Q09 |
| 14 | 10.3 · 10.4 · 11.1 | 10.2 · 10.5 · 10.8 · 14.10.1 · 14.11.1 | Q10 |
| 15 | 11.2 · 11.3 · 11.4 | 10.7 · 11.5 · 11.6 | Q11 |
| 16 | 12.1 · 12.2 · 13.1 (hoặc playbook gần việc bạn) | 12.3–12.7 · 14.4.1 → 14.4.2 → 14.5.1 → 14.5.2 (chuỗi HPC) · 11.7 · 11.8 | Q12 · Q13 |

**8 cửa Quyển IV** (đọc khi muốn thấy biên giới ngành): 14.1.1 · 14.2.1 · 14.3.1 · 14.4.1 · 14.5.2 · 14.8.2 · 14.10.1 · 14.11.1 — rải ở cột mở rộng đúng tuần gắn kết. Hai cửa có điều kiện: chuỗi HPC (14.5.2) cần 14.4.2 → 14.5.1 trước đó nên cả chuỗi nằm ở tuần 16, sau 14.4.1; cửa 14.3.1 cần nhảy nhanh 14.1.3 §0–§2 (HBM — mật độ nhiệt).

## 4. Persona (b) — Dev ứng dụng chuyển hướng hệ thống · 12 tuần

Đã viết sản phẩm, đã dùng DB/cloud ở mức người dùng; cần hiểu bên dưới để thiết kế và sửa sự cố.

| Tuần | Lõi | Mở rộng | Checkpoint |
|---|---|---|---|
| 1 | 0.1–0.4 (nhanh) · 1.1 | — | Q00 |
| 2 | 2.1 · 2.2 · 2.3 | 2.4 · 2.5 | — |
| 3 | 3.1 · 3.9 | runtime bạn dùng · 3.10 · 3.11 · 2.6 | Q02 · Q03 |
| 4 | 4.1 · 4.2 · 4.3 | 4.4–4.6 | — |
| 5 | 4.8 · 4.9 · 5.1 | 4.7 | Q04 |
| 6 | 5.2 · 5.4 · 5.7 | 5.15 | Q05 |
| 7 | 8.1 · 8.2 · 8.5 | 8.3 · 8.4 | — |
| 8 | 9.1 · 9.4 · 10.1 | 9.6 · 9.7 · cả P7 nếu làm web | Q09 |
| 9 | 10.3 · 10.4 | 10.5 · 14.10.1 | Q10 |
| 10 | 11.1 · 11.2 · 11.3 | 11.4 | Q11 (nửa) |
| 11 | 11.6 · 12.1 · 12.2 | 11.5 | Q11 · Q12 |
| 12 | 13.1 · 13.x (chọn thêm một playbook gần sản phẩm bạn) | 8.8 · 12.3 · 12.7 · 14.8.2 | Q13 |

## 5. Persona (c) — Ops/SRE mở rộng kiến trúc & AI · 10 tuần

Đã vận hành hệ thống; cần chiều sâu kiến trúc, dữ liệu và lớp AI.

| Tuần | Lõi | Mở rộng | Checkpoint |
|---|---|---|---|
| 1 | 0.1–0.4 (nhanh) · 1.1 · 1.7 | 1.9 · 1.10 · 14.3.1 | Q00 |
| 2 | 2.3 · 2.6 · 2.7 | 2.8 | Q02 (nửa) |
| 3 | 4.1 · 4.8 · 4.9 | 5.7 | Q04 |
| 4 | 5.1 · 5.15 | 5.16 · 5.4 | Q05 (nửa) |
| 5 | 8.1 · 8.2 · 8.5 | 8.4 | Q08 (nửa) |
| 6 | 8.7 · 8.8 · 9.1 | 9.4 | Q08 · Q09 |
| 7 | 10.1 · 10.2 · 10.5 | 10.7 · 14.10.1 | Q10 |
| 8 | 11.1 · 11.2 · 11.6 | 11.3 · 11.4 · 11.5 | Q11 |
| 9 | 11.7 · 12.1 · 12.2 | 14.4.1 · 14.4.3 | Q12 (nửa) |
| 10 | 12.6 · 13.1 (hoặc playbook gần hệ của bạn) | 12.3 · 12.7 | Q12 · Q13 |

## 6. Sau tuần cuối

Ba ngả chung: (1) **làm tay** — 11.8 có 24+ lab; (2) **đi ngang biên giới** — P14 theo ngành bạn chạm (game/robot/mật mã…); (3) **đi sâu lớp tải** — P13 playbook đúng loại hệ thống bạn vận hành. Nơi nào cũng giữ bộ điều hướng của P15-00.

## 7. Dữ kiện máy đọc được

`facts/learning-paths.csv` (persona · tuần · chương · lõi/mở rộng/nhảy) ghi **đầy đủ** lõi + mở rộng của ba lộ trình. Tuyến học chuẩn hóa tại `facts/edu-order.csv`, kiểm `tools/edu_order_check.py`: không chương nào đứng trước tiên quyết "Đọc trước" của nó). Walkthrough kiểm bằng `tools/persona_walkthrough.py` (mô phỏng đọc tối đa — mở rộng + nhảy đều đọc, trong tuần đọc theo thứ tự tuyến): **persona (a) — người mới — không đứt khái niệm ở tuần nào**; persona (b)/(c) là lộ trình chuyên gia: khoảng hở với "Đọc trước" là chủ đích, bù bằng kinh nghiệm hoặc nhảy "đọc khi cần" (Ba tốc độ đọc, P15-00 §4).

