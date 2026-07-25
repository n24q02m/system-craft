---
title: "Phát hiện đối tượng và đường đi xuống thiết bị biên"
description: "Chưng cất tri thức, đánh đổi giữa độ chính xác và kích thước mô hình, và vì sao một con số mAP tổng có thể che mất lớp mà bạn quan tâm nhất."
lang: "vi"
order: 4
field: "DET"
topics: ["phát hiện đối tượng", "chưng cất tri thức", "mAP", "thiết bị biên", "mất cân bằng lớp"]
---

Bài toán: cho một khung hình từ camera, xác định trong đó có những phương tiện nào và chúng nằm ở đâu.
Ràng buộc: mô hình phải chạy được trong điều kiện thực tế — trời mưa, ban đêm, đèn pha loá — và phải
đủ nhẹ để đặt lên thiết bị ngoài hiện trường thay vì máy chủ.

Hai ràng buộc ấy kéo về hai hướng ngược nhau, và phần lớn công việc nằm ở chỗ hoà giải chúng.

## Đo lường: một con số không đủ

Chuẩn đo của lĩnh vực này đến từ bộ dữ liệu COCO, và điều đáng chú ý là **chuẩn ấy cố tình không cho
phép rút gọn về một con số**.

Một dự đoán được tính là đúng khi hộp bao nó vẽ ra chồng lấn đủ nhiều với hộp thật. "Đủ nhiều" được đo
bằng tỷ lệ giao trên hợp. Vấn đề là chọn ngưỡng bao nhiêu: ngưỡng thấp thì dễ dãi với vị trí, ngưỡng
cao thì đòi hỏi định vị rất chính xác. Thay vì chọn một ngưỡng, chuẩn COCO lấy trung bình trên mười
ngưỡng từ 0,5 đến 0,95. Đó là ý nghĩa của con số thường được viết là mAP@0.5:0.95.

Bên cạnh đó, chuẩn này còn tách riêng kết quả theo **kích thước đối tượng** — nhỏ, vừa, lớn — vì phát
hiện vật nhỏ khó hơn hẳn và một con số gộp sẽ che mất điều đó.

Nhưng chi tiết quan trọng nhất, và cũng hay bị bỏ qua nhất, nằm ở chỗ khác: trong công cụ đánh giá
chính thức, **độ chính xác trung bình của từng lớp là kết quả gốc**; con số mAP mà mọi người hay trích
dẫn chỉ là trung bình cộng của chúng ở bước cuối. Nói cách khác, per-class AP không phải một phép tính
phụ thêm — nó là thứ có trước.

## Vì sao điều đó quan trọng với dữ liệu thật

Dữ liệu giao thông thực tế lệch lớp rất mạnh. Ở Việt Nam, xe máy áp đảo về số lượng; xe buýt thì thưa
thớt. Chênh lệch giữa lớp nhiều nhất và lớp ít nhất có thể tới hàng chục lần.

Với phân bố như vậy, mAP tổng gần như là chỉ số của riêng lớp đông nhất. Mô hình có thể phát hiện xe
máy rất tốt và gần như không thấy xe buýt, mà con số tổng vẫn đẹp. Nếu hệ thống được dùng để đếm lưu
lượng theo loại phương tiện thì đó là hỏng ở đúng chỗ quan trọng, nhưng chỉ số không hề báo.

Ngành đã gặp và đặt tên cho vấn đề này. Có những bộ dữ liệu được thiết kế riêng để phơi bày nó, với
hơn một nghìn lớp phân bố theo quy luật đuôi dài tự nhiên; và chúng báo cáo kết quả tách theo nhóm lớp
hiếm, lớp thường, lớp phổ biến thay vì chỉ một con số. Lý do được nêu thẳng: các phương pháp học sâu
hiện đại hoạt động kém trong vùng ít mẫu, và một chỉ số gộp sẽ giấu điều đó đi.

Bài học áp dụng được ngay: **khi dữ liệu lệch lớp, báo cáo per-class AP là bắt buộc, không phải tuỳ chọn.**

## Chưng cất tri thức: học từ một mô hình lớn hơn

Để thoả mãn ràng buộc về kích thước, cách tiếp cận là chưng cất tri thức: huấn luyện một mô hình lớn
làm "thầy", rồi huấn luyện mô hình nhỏ làm "trò" sao cho trò không chỉ khớp nhãn thật mà còn khớp cả
phân phối đầu ra của thầy.

Trực giác đằng sau: nhãn thật chỉ nói "đây là xe máy". Đầu ra của thầy nói thêm "đây là xe máy, nhưng
hơi giống xe đạp, và chắc chắn không phải xe buýt". Thông tin về mức độ giống nhau giữa các lớp — đôi
khi gọi là tri thức tối — là thứ nhãn cứng không có.

Điều đáng nói là **kỹ thuật này không chuyển thẳng từ phân loại sang phát hiện đối tượng được**. Bài
toán phát hiện có ba khác biệt mà các công trình đầu tiên trong lĩnh vực đã phải xử lý riêng:

Thứ nhất, phần lớn diện tích ảnh là nền. Nếu ép trò bắt chước thầy trên toàn bộ bản đồ đặc trưng, gần
như toàn bộ tín hiệu học được sẽ là về nền — thứ không ai quan tâm. Hướng giải quyết hiện đại là chỉ
bắt chước ở những vùng gần đối tượng.

Thứ hai, phát hiện đối tượng có thành phần hồi quy toạ độ hộp bao, không chỉ phân loại. Ép trò khớp
hoàn toàn với thầy ở đây có thể phản tác dụng khi thầy sai; cách làm hợp lý là chỉ dùng thầy làm cận
trên, tức chỉ phạt trò khi nó tệ hơn thầy.

Thứ ba, mất cân bằng giữa lớp nền và lớp đối tượng nghiêm trọng hơn nhiều so với bài phân loại thông
thường, nên hàm mất mát cần có trọng số tương ứng.

Nói cách khác, "áp dụng chưng cất tri thức" không phải một thao tác duy nhất mà là một họ kỹ thuật cần
điều chỉnh theo bài toán.

## Tăng cường dữ liệu: nướng sẵn hay sinh lúc chạy

Có một quyết định kiến trúc nhỏ nhưng ảnh hưởng lâu dài: các phép biến đổi tăng cường dữ liệu nên
được áp trước và lưu thành ảnh, hay sinh ngẫu nhiên trong lúc huấn luyện?

Sinh lúc chạy là mặc định của hầu hết framework, và có lý do chính đáng: mỗi vòng lặp mô hình thấy một
biến thể khác nhau, nên hiệu quả chống quá khớp cao hơn với cùng dung lượng lưu trữ.

Áp trước có ưu thế khác: các phép biến đổi phức tạp và tốn kém — thêm mưa, thêm sương mù, giả lập loá
đèn — chỉ phải tính một lần thay vì mỗi epoch. Với một pipeline hướng tới điều kiện thời tiết xấu cụ
thể, đây là đánh đổi hợp lý.

Cái bẫy nằm ở chỗ trộn lẫn: nếu đã nướng sẵn biến thể vào dữ liệu rồi mà vẫn bật tăng cường lúc chạy,
tổng mức biến dạng có thể vượt xa dự định, và ảnh huấn luyện trôi xa khỏi phân phối thật. Còn nếu tắt
hết tăng cường lúc chạy thì phải chắc rằng phần nướng sẵn đã đủ đa dạng. Điều quan trọng là **quyết định
có ý thức và ghi lại**, vì sáu tháng sau không ai nhớ vì sao một nhóm tham số bị đặt về 0.

## Ba điều học được về việc đưa mô hình lên thiết bị

**Chuyển đổi định dạng là một bước có rủi ro riêng.** Đưa một mô hình từ framework huấn luyện sang
runtime trên thiết bị đi qua nhiều lần chuyển đổi, mỗi lần đều có thể làm lệch kết quả — do toán tử
không được hỗ trợ nên bị thay thế, do khác biệt cách làm tròn, do thứ tự kênh màu khác nhau. Bước
kiểm tra bắt buộc là chạy cùng một ảnh qua cả hai phiên bản và so đầu ra. Nếu không có bước này, mô
hình có thể im lặng kém đi mà không ai biết.

**Kịch bản triển khai cần được ghi lại cùng mô hình.** Một tệp trọng số không tự nói nó được huấn
luyện cho bao nhiêu lớp, kích thước đầu vào bao nhiêu, chuẩn hoá thế nào. Khi những thông tin đó chỉ
tồn tại trong đầu người làm, việc thay mô hình mới vào một ứng dụng có sẵn trở thành trò đoán mò. Cách
làm đúng là để danh sách lớp và tham số tiền xử lý đi kèm trọng số như một phần của hiện vật.

**Chuẩn đo tốc độ có tồn tại.** Việc đo hiệu năng suy luận trên thiết bị đã được chuẩn hoá: có bộ
benchmark công nghiệp cho máy chủ và cho thiết bị nhỏ, quy định rõ kịch bản tải, cách báo cáo, và điều
kiện để hai kết quả so sánh được với nhau — kể cả phiên bản đo cả điện năng tiêu thụ. Nếu tốc độ là
một yêu cầu của dự án, nó nên được đo và ghi lại theo cách người khác lặp lại được, chứ không phải
bằng cảm nhận "chạy thấy mượt".

## Điều còn đọng lại

Ba điều đáng mang theo.

**Chỉ số gộp che giấu thất bại cục bộ.** Với dữ liệu lệch lớp, mAP tổng có thể tăng trong khi lớp bạn
quan tâm nhất đang tệ đi. Luôn nhìn per-class.

**Ràng buộc triển khai phải là ràng buộc thiết kế từ đầu.** Nếu mô hình cuối cùng phải chạy trên thiết
bị hạn chế, điều đó quyết định kiến trúc, quyết định việc có dùng chưng cất hay không, và quyết định cả
cách đo. Gắn ràng buộc ấy vào cuối dự án luôn đắt hơn nhiều so với đặt nó ở đầu.

**Ngân sách tính toán là một siêu tham số ẩn.** Khi việc huấn luyện dừng vì hết thời gian chứ không
phải vì hội tụ, mọi so sánh giữa các lần chạy đều bị nhiễu bởi biến số ấy. Nếu buộc phải làm vậy — và
thường là buộc — thì ít nhất hãy ghi lại rằng con số thu được là kết quả tốt nhất trong một ngân sách
nhất định, chứ không phải kết quả cuối cùng của phương pháp.
