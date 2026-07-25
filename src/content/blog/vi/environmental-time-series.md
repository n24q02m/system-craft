---
title: "Dữ liệu quan trắc môi trường: hạ tầng trước, mô hình sau"
description: "Vì sao phần khó nhất của một hệ dự báo không nằm ở mô hình, vì sao sai số phần trăm hỏng khi giá trị gần 0, và vì sao đôi khi một phương pháp thống kê cổ điển lại thắng mạng nơ-ron."
lang: "vi"
order: 5
field: "TS"
topics: ["chuỗi thời gian", "dự báo", "chọn chỉ số", "baseline", "dữ liệu không gian"]
---

Bài toán: từ dữ liệu quan trắc chất lượng không khí và chất lượng nước theo thời gian tại nhiều trạm
đo, đưa ra dự báo cho những ngày tới và cảnh báo khi có nguy cơ vượt ngưỡng.

Nghe như một bài dự báo chuỗi thời gian tiêu chuẩn. Nhưng phần lớn công sức thực tế lại rơi vào chỗ
khác — và đó chính là bài học đầu tiên.

## Phần khó nhất không nằm ở mô hình

Dữ liệu quan trắc có ba đặc tính khiến nó khó lưu trữ và truy vấn hơn dữ liệu bảng thông thường.

**Nó vừa có chiều thời gian vừa có chiều không gian.** Mỗi phép đo gắn với một thời điểm và một toạ độ.
Câu hỏi thường gặp không phải "giá trị tại trạm này hôm qua là bao nhiêu" mà là "trong bán kính vài chục
kilômét quanh điểm này, mức trung bình tuần qua ra sao" — một truy vấn cần cả chỉ mục thời gian lẫn chỉ
mục địa lý.

**Nó thưa và không đều.** Trạm này đo mỗi giờ, trạm kia mỗi ngày; có trạm ngừng hoạt động một thời gian
rồi chạy lại. Giả định "mỗi bước thời gian có đúng một giá trị" — nền tảng của hầu hết mô hình chuỗi
thời gian — không tự nhiên đúng, mà phải được tạo ra bằng bước tái lấy mẫu và điền khuyết. Và cách điền
khuyết là một quyết định mô hình hoá, không phải thao tác dọn dẹp vô hại.

**Mỗi thông số là một chuỗi riêng.** Nồng độ ô-zôn và nồng độ một kim loại vết có biên độ khác nhau
hàng nghìn lần, chu kỳ khác nhau, và cơ chế vật lý khác nhau. Gộp chúng vào một mô hình chung thường
tệ hơn là huấn luyện riêng từng chuỗi.

Kết quả là phần lớn thời gian dự án đi vào thiết kế lược đồ lưu trữ, chỉ mục, và đường ống tiền xử lý.
Điều này khớp với một quan sát đã được ghi nhận trong nghiên cứu về thực hành ngành: ai cũng muốn làm
phần mô hình, ít ai muốn làm phần dữ liệu — trong khi phần lớn sự cố lại bắt nguồn từ chính phần dữ
liệu bị coi nhẹ.

## Chọn sai chỉ số thì mọi kết luận sau đó đều lung lay

Đây là bài học kỹ thuật rõ ràng nhất của dự án này.

Phản xạ tự nhiên khi báo cáo sai số dự báo là dùng sai số phần trăm tuyệt đối trung bình. Nó trực quan:
"sai trung bình mười mấy phần trăm" thì ai cũng hiểu. Nhưng nó có một chỗ hỏng nghiêm trọng: nó chia
cho giá trị thật.

Với dữ liệu quan trắc môi trường, nhiều thông số có giá trị **rất gần 0** trong phần lớn thời gian —
đó chính là trạng thái bình thường, không phải dữ liệu lỗi. Khi mẫu số gần 0, tỷ số nổ tung. Một con
số phần trăm khổng lồ xuất hiện trong bảng kết quả, và nó không mang thông tin gì về chất lượng dự báo.

Vấn đề này đã được phân tích kỹ trong tài liệu chuyên ngành. Công trình đề xuất giải pháp chuẩn cho nó
chỉ ra rằng ngay cả biến thể "đối xứng" của chỉ số này cũng không cứu được: nó vẫn chia cho một đại
lượng có thể rất nhỏ, và bất chấp cái tên có chữ "tuyệt đối", nó vẫn có thể nhận giá trị âm.

Giải pháp được đề xuất là **MASE** — sai số tuyệt đối được chuẩn hoá theo thang. Thay vì chia sai số
cho giá trị thật, chia nó cho sai số trung bình của một phương pháp ngây thơ, cụ thể là phương pháp
"dự báo ngày mai bằng giá trị hôm nay", tính trên tập huấn luyện. Cách chuẩn hoá này có ba tính chất
tốt: không phụ thuộc thang đo nên so được giữa các thông số khác nhau; không bao giờ vô định trừ khi
chuỗi là hằng số; và có một mốc diễn giải tự nhiên — dưới 1 nghĩa là tốt hơn phép dự báo ngây thơ,
trên 1 nghĩa là tệ hơn.

Tính chất thứ ba mới là điều quan trọng nhất, và nó dẫn thẳng tới bài học tiếp theo.

## Baseline ngây thơ mạnh hơn nhiều người nghĩ

Chuỗi thời gian có một đặc điểm khiến nó khác hẳn các bài toán học máy khác: **giá trị gần nhất đã là
một dự báo rất tốt**. Nhiệt độ ngày mai gần với nhiệt độ hôm nay. Với dữ liệu có mùa vụ, giá trị cùng
kỳ mùa trước còn tốt hơn nữa.

Hai phương pháp này — dự báo ngây thơ và dự báo ngây thơ theo mùa — không có tham số nào để học, chạy
tức thì, và thường xuyên đánh bại các mô hình phức tạp hơn trên chuỗi ngắn hoặc nhiễu. Giáo trình chuẩn
về dự báo, do chính đồng tác giả của MASE viết, đưa ra ví dụ minh hoạ trong đó phương pháp ngây thơ
theo mùa thắng cả ba phương pháp phức tạp hơn được đem ra so.

Hệ quả thực hành rất rõ: **chạy baseline trước, luôn luôn.** Nó tốn vài phút và nó định nghĩa ý nghĩa
của mọi con số sau đó. Không có nó, một sai số nghe có vẻ nhỏ vẫn có thể tệ hơn việc không làm gì cả.

Cùng tinh thần đó, các cuộc thi dự báo quy mô lớn của ngành — hàng chục nghìn đến hàng trăm nghìn chuỗi,
hàng chục phương pháp dự thi — đều đánh giá bằng các chỉ số chuẩn hoá theo baseline, và đều báo cáo mức
cải thiện so với benchmark tốt nhất chứ không báo cáo sai số trần trụi.

Giáo trình ấy còn nhấn mạnh một điểm nữa đáng nhắc lại: phải đánh giá bằng dự báo thật trên tập kiểm
tra, không dùng độ khớp trên tập huấn luyện làm căn cứ — vì một mô hình khớp dữ liệu huấn luyện rất
tốt không đảm bảo sẽ dự báo tốt.

## Khi mô hình đơn giản thắng mô hình phức tạp

Trong dự án này có một quan sát đáng nhớ: với một nhóm dữ liệu, một phương pháp thống kê cổ điển tự
động chọn bậc mô hình cho kết quả ổn định hơn so với mạng nơ-ron hồi tiếp áp cho nhóm dữ liệu còn lại.

Điều này không có nghĩa mạng nơ-ron kém hơn. Nó phản ánh một nguyên tắc chọn công cụ: mô hình học sâu
cần **nhiều dữ liệu trên mỗi chuỗi** để vượt được các phương pháp thống kê. Khi mỗi chuỗi chỉ có vài
trăm điểm quan sát, số tham số của mạng vượt xa lượng thông tin có trong dữ liệu, và thứ mô hình học
được chủ yếu là nhiễu.

Có một hệ quả đi kèm mà dự án cũng gặp: **thêm dữ liệu sinh nhân tạo không phải lúc nào cũng giúp.**
Khi dữ liệu thật ít, bù thêm bằng dữ liệu tổng hợp là ý tưởng tự nhiên. Nhưng nếu quá trình sinh không
phản ánh đúng cơ chế tạo ra dữ liệu thật, mô hình sẽ học phân phối của bộ sinh chứ không phải phân phối
của hiện tượng. Kết quả có thể tệ đi so với khi chỉ dùng dữ liệu thật ít ỏi.

Cách kiểm tra rẻ tiền: luôn giữ một nhánh thí nghiệm chỉ dùng dữ liệu thật, và so hai nhánh trên cùng
một tập kiểm tra thật. Nếu nhánh có dữ liệu tổng hợp không tốt hơn, thì dữ liệu tổng hợp đang gây hại
chứ không phải trung tính.

## Chỉ số tổng hợp cần được định nghĩa cẩn thận

Phần cuối của hệ thống là gộp nhiều thông số thành một chỉ số cảnh báo duy nhất cho người dùng cuối.
Đây là bước dễ bị xem là thuần kỹ thuật nhưng thực ra mang rất nhiều giả định.

Trọng số của từng thông số phản ánh mức độ nguy hại tương đối — đó là một phán đoán chuyên môn y tế
hoặc môi trường, không phải một lựa chọn kỹ thuật. Ngưỡng phân mức cảnh báo cũng vậy. Và khi các thông
số có thang đo khác nhau, cách chuẩn hoá trước khi gộp sẽ quyết định thông số nào thực sự chi phối
kết quả cuối cùng.

Điều nên làm là ghi rõ các giả định ấy thành tài liệu, kèm nguồn cho mỗi trọng số và mỗi ngưỡng. Một
chỉ số tổng hợp thiếu phần này thì không kiểm chứng được, và người đọc không có cách nào biết nó đang
nói gì.

## Điều còn đọng lại

**Chọn chỉ số là một quyết định kỹ thuật thực sự, không phải thủ tục.** Một chỉ số không phù hợp với
đặc tính dữ liệu sẽ tạo ra những con số vẫn tính được nhưng vô nghĩa — và tệ hơn, có thể dẫn tới việc
chọn sai mô hình.

**Baseline không phải nghi thức, nó là hệ quy chiếu.** Không có nó thì không tồn tại khái niệm tốt hay
xấu.

**Hạ tầng dữ liệu là phần đầu tư có tuổi thọ dài nhất.** Mô hình sẽ được thay; lược đồ lưu trữ, chỉ mục
và đường ống làm sạch thì ở lại. Trong một dự án dữ liệu quan trắc, làm tốt phần này có giá trị lâu hơn
bất kỳ kiến trúc mạng nào được chọn tại thời điểm đó.
