---
title: "Quan trắc môi trường: hạ tầng dữ liệu và dự báo chuỗi thời gian"
description: "Lưu trữ dữ liệu vừa có chiều thời gian vừa có chiều không gian, dự báo từng thông số, và cách ngành đo sai số dự báo cho đúng."
lang: "vi"
order: 5
field: "TS"
topics: ["chuỗi thời gian", "dự báo", "dữ liệu không gian", "ARIMA", "MASE"]
---

Bài toán: từ dữ liệu quan trắc chất lượng không khí và chất lượng nước, thu tại nhiều trạm đo trong
nhiều năm, đưa ra dự báo cho những ngày tới và cảnh báo khi có nguy cơ vượt ngưỡng an toàn.

Phần thú vị của bài toán này không nằm ở chỗ ai cũng nghĩ. Trước khi bàn tới mô hình dự báo, phải giải
xong một bài toán hạ tầng — và đó là phần chiếm nhiều công sức nhất.

## Hệ thống đã dựng

### Lưu trữ: dữ liệu hai chiều

Dữ liệu quan trắc có ba đặc tính khiến nó khó lưu và khó truy vấn hơn dữ liệu bảng thông thường.

**Nó vừa có chiều thời gian vừa có chiều không gian.** Mỗi phép đo gắn với một thời điểm và một toạ độ
địa lý. Câu hỏi thường gặp không phải "giá trị tại trạm này hôm qua là bao nhiêu" mà là "trong bán kính
vài chục kilômét quanh điểm này, mức trung bình tuần qua ra sao" — một truy vấn cần cả chỉ mục thời
gian lẫn chỉ mục địa lý.

**Nó thưa và không đều.** Trạm này đo mỗi giờ, trạm kia mỗi ngày; có trạm ngừng hoạt động một thời gian
rồi chạy lại. Giả định "mỗi bước thời gian có đúng một giá trị" — nền tảng của hầu hết mô hình chuỗi
thời gian — không tự nhiên đúng, mà phải được tạo ra bằng bước tái lấy mẫu và điền khuyết.

**Mỗi thông số là một chuỗi riêng.** Nồng độ ô-zôn và nồng độ một kim loại vết có biên độ khác nhau
hàng nghìn lần, chu kỳ khác nhau, và cơ chế vật lý sinh ra chúng cũng khác nhau.

Giải pháp lưu trữ là một cơ sở dữ liệu tài liệu có hỗ trợ sẵn hai thứ cần thiết: **collection kiểu
chuỗi thời gian** (tối ưu cho dữ liệu chỉ ghi thêm, có trục thời gian, nén tốt theo cụm thời gian) và
**chỉ mục địa lý** (cho phép truy vấn theo bán kính, theo đa giác, theo khoảng cách). Hai thứ này giải
quyết đúng hai chiều của bài toán mà không cần tự cài.

### Đường ống dữ liệu

Nguồn là các bộ dữ liệu quan trắc công khai theo chuẩn của cơ quan môi trường: bảng đo chất lượng không
khí với các trường mã bang, mã hạt, mã trạm, toạ độ, tên thông số, giá trị trung bình và chỉ số chất
lượng không khí; bảng đo chất lượng nước với mã tổ chức, mã điểm quan trắc, tên đặc tính đo và giá trị.

Các bước xử lý: chuẩn hoá tên thông số, tái lấy mẫu về lưới thời gian đều, điền khuyết, chuẩn hoá đơn
vị, rồi nạp vào cơ sở dữ liệu theo lược đồ đã thiết kế. Việc điền khuyết là một quyết định mô hình hoá
chứ không phải thao tác dọn dẹp vô hại — cách điền ảnh hưởng trực tiếp tới thứ mô hình học được.

### Dự báo không khí: mạng hồi tiếp cho từng thông số

Thay vì một mô hình chung cho mọi thông số, hệ thống huấn luyện **một mô hình riêng cho mỗi thông số**.
Lý do đã nêu ở trên: các thông số khác nhau về biên độ, chu kỳ và cơ chế, nên gộp chung thường tệ hơn.

Kiến trúc là mạng LSTM nhiều lớp kèm cơ chế chú ý, dropout và chuẩn hoá batch, dừng sớm theo tập kiểm
định. Đầu ra là dự báo cho một cửa sổ vài ngày tới.

Kết quả từ các mô hình riêng lẻ được gộp thành một **chỉ số rủi ro sức khoẻ tổng hợp**: mỗi thông số
được gán trọng số theo mức độ nguy hại, quy về thang chung rồi cộng lại, và ánh xạ sang các mức cảnh
báo. Chỉ số này cũng được phân rã theo hệ cơ quan chịu ảnh hưởng — hô hấp, tim mạch, thần kinh — để
cảnh báo có ý nghĩa với người đọc.

### Dự báo nước: thống kê cổ điển và phân cụm không gian

Nhánh chất lượng nước đi hướng khác hẳn: không dùng học sâu.

**Phân cụm không gian** bằng thuật toán gom cụm theo mật độ. Điểm hay của thuật toán này với dữ liệu
địa lý là nó không cần biết trước số cụm, tự phát hiện được cụm hình dạng bất kỳ, và đánh dấu các điểm
nằm ngoài mọi cụm là nhiễu — phù hợp với các trạm quan trắc rải rác không đều.

**Dự báo bằng ARIMA với chọn bậc tự động.** ARIMA là mô hình thống kê kết hợp ba thành phần: tự hồi
quy (giá trị hiện tại phụ thuộc tuyến tính vào các giá trị trước), sai phân (lấy hiệu để khử xu hướng,
đưa chuỗi về dạng dừng), và trung bình trượt (phụ thuộc vào các sai số dự báo trước). Việc chọn ba bậc
này thường làm thủ công bằng cách nhìn đồ thị tự tương quan; thư viện dùng ở đây tự dò trên một lưới
tham số và chọn theo tiêu chí thông tin.

Ngoài dự báo, nhánh này còn tính **tỷ lệ vượt ngưỡng** cho từng đặc tính — bao nhiêu phần trăm số đo
nằm ngoài khoảng an toàn — và cảnh báo khi dự báo cho thấy xu hướng vượt ngưỡng kéo dài.

## Kiến thức nền

### Vì sao chuỗi thời gian khác các bài toán học máy khác

Điểm khác biệt căn bản: **giá trị gần nhất đã là một dự báo rất tốt.** Nhiệt độ ngày mai gần với nhiệt
độ hôm nay. Với dữ liệu có mùa vụ, giá trị cùng kỳ mùa trước còn tốt hơn nữa.

Hai phương pháp này — dự báo ngây thơ và dự báo ngây thơ theo mùa — không có tham số nào để học và chạy
tức thì. Chúng là điểm khởi đầu bắt buộc, không phải vì chúng tốt, mà vì không có chúng thì không tồn
tại khái niệm "tốt" hay "tệ" cho mọi con số về sau.

### Tính dừng

Phần lớn mô hình thống kê cho chuỗi thời gian giả định chuỗi **dừng**: các tính chất thống kê như trung
bình và phương sai không đổi theo thời gian. Dữ liệu thật hiếm khi dừng — nó có xu hướng tăng giảm dài
hạn và có chu kỳ mùa. Bước sai phân trong ARIMA chính là để khử xu hướng, và các biến thể có thành phần
mùa vụ để khử chu kỳ.

Với mạng nơ-ron thì giả định này không bắt buộc, nhưng đổi lại chúng cần nhiều dữ liệu hơn nhiều để
tự học được cấu trúc mà mô hình thống kê được cho biết trước.

### Khi nào học sâu có lợi thế, khi nào không

Mô hình học sâu cần **nhiều điểm quan sát trên mỗi chuỗi** để vượt các phương pháp thống kê. Khi mỗi
chuỗi chỉ có vài trăm điểm, số tham số của mạng vượt xa lượng thông tin trong dữ liệu, và thứ nó học
được chủ yếu là nhiễu.

Lợi thế của học sâu xuất hiện khi có nhiều chuỗi liên quan để học chung một biểu diễn, khi có biến
ngoại sinh phức tạp, hoặc khi quan hệ phi tuyến rõ rệt. Với một tập trạm quan trắc quy mô vừa, đó
không hiển nhiên là trường hợp tốt cho học sâu.

## Ngành công nghiệp làm việc này ra sao

### Chọn thước đo sai số

Phản xạ tự nhiên khi báo cáo sai số dự báo là dùng sai số phần trăm tuyệt đối trung bình. Nó trực quan
và ai cũng hiểu. Nhưng nó có một chỗ hỏng nghiêm trọng với đúng loại dữ liệu này: **nó chia cho giá trị
thật**, mà nhiều thông số môi trường có giá trị rất gần 0 trong phần lớn thời gian — đó chính là trạng
thái bình thường, không phải dữ liệu lỗi. Khi mẫu số gần 0, tỷ số nổ tung.

Công trình chuẩn về vấn đề này, đăng trên tạp chí chuyên ngành về dự báo, chỉ ra rằng ngay cả biến thể
"đối xứng" của chỉ số ấy cũng không cứu được: nó vẫn chia cho một đại lượng có thể rất nhỏ, và bất chấp
cái tên có chữ "tuyệt đối", nó vẫn có thể nhận giá trị âm. Bài báo minh hoạ bằng các chuỗi thật có chứa
giá trị bằng 0 hoặc âm, ở đó chỉ số này cho ra vô cực hoặc không xác định.

Giải pháp được đề xuất là **MASE** — sai số tuyệt đối chuẩn hoá theo thang. Thay vì chia cho giá trị
thật, chia sai số cho sai số trung bình của phương pháp ngây thơ tính trên tập huấn luyện. Ba tính chất
làm nó phù hợp: không phụ thuộc thang đo nên so được giữa các thông số khác nhau; không bao giờ vô định
trừ khi chuỗi là hằng số; và có mốc diễn giải tự nhiên — dưới một nghĩa là tốt hơn phép dự báo ngây thơ,
trên một nghĩa là tệ hơn.

### Benchmark của lĩnh vực

Các cuộc thi dự báo quy mô lớn của ngành đặt ra chuẩn thực hành. Một cuộc thi dùng hàng trăm nghìn chuỗi
thuộc nhiều lĩnh vực khác nhau và hàng chục phương pháp dự thi, đánh giá bằng các chỉ số chuẩn hoá theo
baseline và yêu cầu cả khoảng dự báo chứ không chỉ giá trị điểm. Một cuộc thi khác dùng dữ liệu doanh
số bán lẻ có cấu trúc phân cấp, với hàng chục nghìn chuỗi, và báo cáo mức cải thiện so với benchmark
tốt nhất thay vì sai số trần trụi.

Giáo trình chuẩn của lĩnh vực, do chính đồng tác giả của MASE viết và công bố miễn phí, nhấn mạnh thêm
hai điều: phải so với phương pháp ngây thơ trước khi kết luận một mô hình phức tạp có giá trị; và phải
đánh giá bằng dự báo thật trên tập kiểm tra, vì một mô hình khớp dữ liệu huấn luyện rất tốt không đảm
bảo sẽ dự báo tốt.

## Vài điều rút ra

**Baseline là hệ quy chiếu, không phải nghi thức.** Với chuỗi thời gian, baseline mạnh một cách bất
ngờ, nên bỏ qua bước này dễ dẫn tới việc ăn mừng một kết quả thực ra tệ hơn không làm gì.

**Chọn chỉ số phải khớp với đặc tính dữ liệu.** Một chỉ số không phù hợp vẫn tính ra số, và đó chính là
chỗ nguy hiểm: nó không báo lỗi, chỉ đưa ra con số vô nghĩa để người đọc tin.

**Thêm dữ liệu tổng hợp không mặc nhiên có lợi.** Nếu quá trình sinh không phản ánh đúng cơ chế tạo ra
dữ liệu thật, mô hình sẽ học phân phối của bộ sinh. Cách kiểm tra rẻ: luôn giữ một nhánh chỉ dùng dữ
liệu thật và so hai nhánh trên cùng một tập kiểm tra thật.

**Chỉ số tổng hợp cần ghi rõ giả định.** Trọng số của từng thông số và các ngưỡng cảnh báo là phán đoán
chuyên môn, không phải lựa chọn kỹ thuật. Ghi chúng thành tài liệu kèm nguồn là điều kiện để người khác
kiểm chứng được.

**Hạ tầng dữ liệu là phần đầu tư có tuổi thọ dài nhất.** Mô hình sẽ được thay; lược đồ lưu trữ, chỉ mục
và đường ống làm sạch thì ở lại lâu hơn nhiều.
