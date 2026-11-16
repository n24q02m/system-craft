# 0.2 — 10 Tiền đề (Axioms) & Điều kiện biên

> **Tầng:** Propaedia · **Mở đầu** · **Trục đọc:** bản đồ · **Động từ liên quan:** Hiểu · Duy trì
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 0.1 (biết 7 trục là gì).

**Sợi chỉ đỏ:** *Đã có toạ độ để cãi cho ra — nhưng cả team đang đứng trên những giả định nào chưa ai nói ra?* — trả lời: mọi cuộc cãi đã chốt bằng 7 trục vẫn phải đứng trên nền — những điều cả team ngầm coi đúng. Chương này nói nền đó ra thành 10 tiên đề, kèm lịch soát lại, để khỏi chứng minh lại mỗi tuần (và chỉ ra 3 tiên đề đang rung mạnh năm 2026). Câu hỏi để lại cho chương sau: *Tiên đề viết xong — nhưng mỗi quyết định cụ thể (kiểu chọn DB hôm qua) duyệt bằng gì cho đều tay?*

**Thuật ngữ sẽ gặp:** *tiên đề* — điều coi đúng trong phạm vi cuốn sách, không chứng minh mỗi lần dùng; *điều kiện biên* — chủ đề tuyên bố là ngoài vũ trụ, ghi rõ thay vì lảng tránh; *rung* — tiên đề bị thực tiễn đe doạ (ví dụ mật mã trước máy lượng tử); *soát lại* — hẹn định kỳ xem tiên đề nào đã chết; *EOL* — ngày hết đời chính thức của một phiên bản phần mềm.

**Ví dụ mở đầu:** Cuộc họp thứ 41 về cache: "Redis luôn nhanh hơn Postgres" — ai đó dán lên wiki như chân lý. Sáu tháng sau dữ liệu nóng 40 GB không còn vừa RAM và chân lý chết. Nếu từ đầu có một dòng "tiên đề: dữ liệu nóng dưới 5 GB (ghi ngày 12/3, người phụ trách A.)" thì cuộc tranh luận hôm nay chỉ mất 5 phút: đo xem tiên đề còn đúng không, thay vì cãi lại từ đầu.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Tuyên bố tường minh 10 giả định nền của toàn atlas | Tôi có biết mình đang đứng trên những định luật nào — và cái nào sắp gãy? |
| 2 | Mỗi tiên đề gắn "điều kiện viết lại" | Tiên đề nào sập thì chương nào phải sửa? |
| 3 | Phạm vi loại trừ (Vòng 3) ghi rõ | Cái gì atlas **không** phủ — để "đủ" có nghĩa đo được? |
| 4 | Cơ chế soát lại tiên đề theo ấn bản | Ai, bao lâu một lần, cập nhật khi có dấu hiệu gì? |

---

## 2. Cơ chế

### 2.1 Vì sao phải viết tiên đề ra

Mọi chương của atlas mặc định 10 điều dưới đây "đúng đủ để dựng hệ thống". Chúng hiếm khi đúng **hoàn toàn** — mỗi tiên đề kèm **độ lệch thực tế** và **điều kiện viết lại** (khi lệch đủ lớn, chương phải đổi). Đây là cách sách **chống lỗi thời có kỷ luật** thay vì im lặng cũ đi.

### 2.2 Mười tiên đề

| # | Tiên đề | Độ lệch thật | Sập thì viết lại |
|---|---|---|---|
| A1 | **Nhị phân & von Neumann:** tính toán = logic rời rạc + mã lệnh/dữ liệu chung bộ nhớ | bit-flip soft error (→14.1.3); analog/neuromorphic ở biên nghiên cứu | 1.x, 2.x |
| A2 | **Đồng hồ lệch:** mọi máy có đồng hồ riêng, không đồng bộ tuyệt đối | NTP ms–s; đồng hồ logic là cách thoát (→8.1) | 8.1, 13.1 |
| A3 | **Mạng mất gói:** gói tin có thể mất/trùng/reorder mọi lúc | TCP/QUIC che bớt — nhưng TTL/partial không (→4.1) | 4.x, 8.5 |
| A4 | **Phần cứng hỏng âm thầm:** đĩa hỏng sector, RAM hỏng bit — không báo lỗi | ECC/scrubbing phát hiện một phần (→14.1.3); bit rot còn đó | 5.13, 14.1.3 |
| A5 | **Mật mã bất đối xứng tồn tại và tin được:** trapdoor một chiều còn an toàn | máy lượng tử bẻ RSA/ECC — **PQC là cuộc di dân đang chạy** (→10.2) | 10.2, 14.10 |
| A6 | **CMOS tiếp tục co nhỏ (một thời):** transistor rẻ hơn theo năm | Moore chậm lại từ ~2015; HBM/chi phí wafer là tường thật (→14.1) | 1.x, 14.1 |
| A7 | **Điện sẵn có và rẻ:** cứ cắm là có, tính theo kWh | đỉnh/renewable/cloud region đôi khi **hết điện trước hết máy** (→1.7, 14.3) | 1.7, 14.3 |
| A8 | **Chương trình tất định:** cùng input → cùng output | LLM phá vỡ ở tầng ứng dụng (→12.1); GPU nondeterminism ở tầng thư viện (→14.5.2) | 12.1, 14.5.2 |
| A9 | **Con người vận hành:** có on-call, có tổ chức, có Conway | mô hình thay đổi mỗi khi người nghỉ việc (→11.6) | 11.4–11.7 |
| A10 | **Dữ liệu có chủ:** mọi byte thuộc ai đó chịu trách nhiệm pháp lý | GDPR/PDPD/CRA đang được thực thi chi tiết hoá nhanh (→10.8) | 10.8, 13.6 |

### 2.3 Ba tiên đề đang rung mạnh nhất (2026)

- **A5 (mật mã):** FIPS 203/204/205 chuẩn hoá 2024; hybrid X25519MLKEM768 đang là cấu hình — cuộc di dân PQC là **việc viết lại có lịch trình lớn nhất** trong các tiên đề (10.2);
- **A8 (tất định):** AI xác suất vào nghiệp vụ — 12.1 dựng "vỏ deterministic" chính là **cách atlas đáp ứng việc tiên đề gãy ở tầng ứng dụng**;
- **A6 (co nhỏ):** hiệu năng miễn phí hết; mọi chương 1.x/12.2 nói "dùng đúng tài nguyên khan hiếm" thay vì "đợi CPU nhanh hơn".

### 2.4 Điều kiện biên của cuốn sách (Vòng 3 — loại trừ có tuyên bố)

Atlas **không** phủ: triết học đạo đức/chính trị công nghệ; kinh tế vĩ mô thị trường; nghiên cứu chưa chuẩn hoá (quantum computing beyond PQC, neuromorphic); giáo trình đại học đầy đủ từng ngành (P14 là **hồ sơ biên giới**, không thay syllabus); sự kiện vendor-specific chi tiết đời thường (chỉ giữ primitive + dữ kiện đã verify — nguyên tắc 30/10). "Đủ" = đủ **bản đồ nền tảng đã công bố** (charter từng phần, plan §3a), không tuyên bố "hết vũ trụ tri thức".

### 2.5 Cơ chế soát lại

Ấn bản atlas đóng băng theo quý (ví dụ SA-2028.1, SA-2028.Q2...); mỗi ấn bản: (1) rà 10 tiên đề — dấu hiệu rung (nghiên cứu mới, chuẩn mới, sự cố ngành); (2) cập nhật versions.csv theo nhịp EOL (→11.8 §2.4); (3) errata log công khai (0.4). Người chịu trách nhiệm: chủ biên + kiểm toán 🔥 hằng tháng cho mục "đang rung".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn |
|---|---|---|
| Số tiên đề | 10 | V |
| PQC chuẩn hoá | FIPS 203/204/205 (8/2024) | V |
| Moore chậm lại | ~2015 trở đi | I |
| Ấn bản đóng băng | hàng quý | P |

---

## 4. Suy luận kiến trúc

- **S1:** Tiên đề tường minh biến "kiến thức nền" thành **tài sản kiểm soát được** — biết mình giả định gì là điều kiện của mọi tranh luận "có nên thay đổi";
- **S2:** "Điều kiện viết lại" là **bảo trì cuốn sách như bảo trì hệ thống** — có owner, có nhịp, có runbook (ấn bản);
- **S3:** Ba tiên đề đang rung (A5/A6/A8) là **chỉ báo đầu tư nội dung** — PQC, tài nguyên khan hiếm, AI-deterministic chiếm nhiều trang nhất vì đó là nơi quyết định đang đổi;
- **S4:** Loại trừ có tuyên bố (§2.4) là **phép đo lường độ trung thực** — sách không kê "hết"; sách kê "hết trong charter này";
- **S5:** Tiên đề A9 (con người) thường bị quên nhất — mọi chương 11.x tồn tại vì nó; thiết kế bỏ con người là thiết kế vi phạm tiên đề của chính hệ;
- **S6:** Khi một kỹ thuật mới tuyên bố "xoá bỏ" một tiên đề (đặt tên: blockchain xoá A2? quantum xoá A5?): kiểm tra **độ lệch thật** trước — hầu hết chỉ thu hẹp lệch, không xoá tiên đề; chương liên quan cập nhật "độ lệch" chứ chưa chắc phải viết lại.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân | Lệnh chẩn |
|---|---|---|
| Tin số liệu sách đã cũ | Không soát theo ấn bản | nhịp đóng băng §2.5 |
| "Sao không nói về X" | X thuộc loại trừ §2.4 | đọc điều kiện biên |
| Quyết định dựa tiên đề đã gãy | Không theo dõi dấu hiệu rung | §2.3 hằng quý |
| Tranh luận "định luật" không hồi kết | Hai tiên đề khác nhau được mặc định | đưa về bảng A1–A10 |

---

## 6. Cách đo

```bash
# Bài "thu thập giả định" cho team (15 phút):
#   mỗi người viết 3 giả định ngầm trong kiến trúc hiện tại —
#   gắn A1–A10 vào từng cái; ô không gắn được = giả định chưa ai thừa nhận
#   (thường là chỗ rủi ro lớn nhất của hệ)
```

Nguyên tắc: **hệ thống của bạn cũng có 10 tiên đề — viết chúng ra** giống atlas đã làm.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay bảng tiên đề riêng:** nhận tiền đề từ một khung chuẩn (NIST/ACM) — ít công sức, ít khớp hệ mình; **thay đóng băng theo quý:** wiki sống liên tục (tươi hơn, mất khả năng trích dẫn "ấn bản" — 0.4 lý do tồn tại của errata).

Năm thấu kính:
- **Kinh tế:** Mỗi tiên đề gãy = thị trường mới (PQC → ngành bảo mật di dân; A8 gãy → ngành eval AI) — đọc bảng §2.2 như bảng đầu tư;
- **Vận hành:** Sign rung là checklist đánh giá kiến trúc quý (cùng chu kỳ 11.1 review budget);
- **An ninh:** A4/A5 là hai tiên đề an ninh trực tiếp — chương 10.2/14.1.3 là "kho dự trữ" của chúng;
- **Lịch sử:** Tiên đề của Euclid đứng 2000 năm tới hình học phi-Euclid; của Newton tới Einstein — khoa học tiến bộ bằng **khai tử tiền đề có lễ trang trọng**, không bằng im lặng đổi;
- **Người dùng:** Người đọc xứng đáng biết nền nhà mình đứng — chương này là lời cam kết trung thực đầu tiên của cuốn sách với người đọc.

---

## 8. Đọc tiếp & bài tập

- Nhận thức luận & errata: **0.4** · PQC: **10.2** · AI & tính tất định: **12.1** · Bán dẫn & tường Moore: **14.1** · Nhiệt/điện: **14.3** · Người vận hành: **11.6**
- **Bài tập 1:** Viết 10 tiên đề của **hệ thống bạn** (dùng bảng A1–A10 làm khung, sửa theo thực tế) — treo ở wiki; quý sau, soát xem cái nào rung;
- **Bài tập 2:** Chọn 1 quyết định kiến trúc lớn 6 tháng qua: truy nó về tiên đề nào (A2? A9? A10?) — viết 2 dòng "vì tiên đề X, ta chọn Y" vào ADR;
- **Bài tập 3:** Đặt lịch soát EOL + tiên đề hằng quý (11.8 §2.4) — 30 phút, dùng bảng §2.2 làm checklist; đúng một quý bạn sẽ bắt được ít nhất một con số đã chết.
