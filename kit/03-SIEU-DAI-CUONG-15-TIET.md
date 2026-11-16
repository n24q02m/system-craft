# MÔN SIÊU ĐẠI CƯƠNG — HỆ THỐNG QUANH TA (15 tiết)

### SYS100 · 15 tiết · không tiên quyết · cho **mọi** ngành (kinh tế, y, luật, truyền thông, quản trị)

> **Một câu mô tả:** sau 15 tiết, người học **không viết được code hệ thống**, nhưng **không bị dắt** khi ai đó nói "chỉ cần thêm server", "chỉ cần microservices", "AI sẽ lo", "chỉ cần mua cloud".
> **Định dạng:** mỗi tiết = 1 câu hỏi + 1 con số + 1 quyết định. Không có tiết nào chỉ có khái niệm.

---

## 1. Chuẩn đầu ra (5 câu, kiểm bằng 5 câu hỏi trong bài kiểm 45 phút)

| # | Người học trả lời được |
|---|---|
| CLO1 | "Nhanh" nghĩa là bao nhiêu? Kể 5 mốc độ trễ và một ví dụ mỗi mốc |
| CLO2 | Vì sao "thêm máy" không luôn nhanh hơn? Cho một con số về giới hạn |
| CLO3 | Một hệ thống tốn tiền ở đâu, và **một** cách cắt 30% mà không giảm chất lượng |
| CLO4 | Khi nào dữ liệu của bạn có thể mất, và vì sao "đã backup" chưa đủ |
| CLO5 | Một tuyên bố kỹ thuật ("hệ chịu được 10.000 người dùng") cần **ba** thông tin gì mới kiểm được |

## 2. Mười lăm tiết

| Tiết | Câu hỏi mở đầu | Con số neo | Chương sách |
|---|---|---|---|
| 1 | Một cú click đi qua bao nhiêu thứ? | 0,5 ns (L1) → 100 ms (RTT xuyên lục địa) → 1 s (con người thấy chậm) | 1.1 |
| 2 | Vì sao máy nhanh hơn 10× mà app chỉ nhanh hơn 2×? | Amdahl: 8 lõi, speedup 5 ⇒ 8,6% tuần tự | 3.1 |
| 3 | Bộ nhớ đắt hay CPU đắt? | 1 GB RAM ≈ 2 giây thu nhập của một kỹ sư; 1 GB qua mạng di động ≈ 5–20× giá đó | 1.3 |
| 4 | Dữ liệu nằm ở đâu là **quyết định**, không phải chi tiết | p99 đọc SSD nhanh hơn HDD ~100×; nhưng cache trong RAM nhanh hơn SSD ~1.000× | 1.4, 5.4 |
| 5 | Vì sao "mất điện là mất dữ liệu"? | 4 bước ghi an toàn; thiếu 1 bước ⇒ mất file sau crash | 2.4 |
| 6 | Cloud rẻ hay đắt? | Một máy chủ thuê 1 năm ≈ 8.760 giờ × giá giờ; **thuê thì trả cho giờ ngủ** | 9.3, 11.5 |
| 7 | Tiền điện của một datacenter | 500 kW, PUE 1,6 ⇒ **~1,08 tỉ VND/tháng**; PUE 1,2 ⇒ ~810 triệu | 1.10 |
| 8 | Vì sao hệ "sập" khi chỉ một thứ chậm? | 1 dependency chậm 500 ms × 200 thread = hết khả năng phục vụ | 8.5 |
| 9 | "Hệ chịu 10.000 người dùng" nghĩa là gì? | Cần: người dùng **đồng thời**, hành động/giây, và p99 chấp nhận | 11.1 |
| 10 | Vì sao không thể vừa nhất quán vừa sẵn sàng khi mạng đứt? | CAP nói bằng ví dụ: bán vé cuối cùng cho 2 người | 8.2 |
| 11 | Tiền chuộc dữ liệu: vì sao backup **online** không cứu được | Backup phải **offline/immutable** + đã thử restore (bấm giờ!) | 10.7 |
| 12 | Dữ liệu cá nhân của bạn đi đâu? | 1 hành vi người dùng có thể tồn tại ở 8–15 nơi (DB, log, backup, vendor) | 5.13 |
| 13 | AI làm được gì và **không** làm được trong hệ thống | AI không sửa được dữ liệu sai; chất lượng phụ thuộc retrieval, không phụ thuộc prompt | 12.3, 12.5 |
| 14 | Vì sao "chỉ cần mua thêm" thường là câu trả lời sai | Scale ngang có trần: hiệu quả **52,5%** ở 8 bản sao khi có tài nguyên chung | 11.3 |
| 15 | Làm sao biết một tuyên bố kỹ thuật là thật? | 3 câu hỏi: **đo bằng gì · ở tải nào · trong điều kiện nào** | 0.4, 14.9.3 |

## 3. Đánh giá (45 phút, không tài liệu)

| Câu | Nội dung | Điểm |
|---|---|---|
| 1 | 5 mốc độ trễ + ví dụ | 20 |
| 2 | Cho một hệ 4 thành phần, chỉ ra nút thắt và **một** phép đo để chứng minh | 25 |
| 3 | Một tuyên bố marketing kỹ thuật: viết 3 câu hỏi để kiểm chứng | 25 |
| 4 | Bài tính: 200 kW, PUE 1,5 → 1,3, giá 1.800đ/kWh ⇒ tiết kiệm/tháng | 15 |
| 5 | "Backup có thì đã an toàn chưa?" — trả lời trong 5 dòng | 15 |

## 4. Vì sao môn này đáng 15 tiết của bất kỳ ngành nào

Vì **mọi ngành** giờ đều mua, thuê, hoặc giám sát một hệ thống: bệnh viện mua HIS, ngân hàng thuê cloud, toà án cần bằng chứng số, marketing chạy campaign trên app. Người ra quyết định trong các nơi đó thường **không** đọc được một tuyên bố kỹ thuật — và cái giá của việc đó là hợp đồng 5 năm cho một kiến trúc sai.

Môn này không đào tạo kỹ sư. Nó đào tạo **người mua, người giám sát, và người đặt câu hỏi** — và đó là thứ hiếm hơn kỹ sư.
