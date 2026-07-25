---
title: "Chống giả mạo khuôn mặt: khi độ chính xác cao là thứ đáng nghi nhất"
description: "Vì sao một mô hình nhận diện tấn công gần như hoàn hảo trong phòng thí nghiệm lại sụp đổ ngoài đời, và vì sao con số dưới mức đoán ngẫu nhiên đôi khi chỉ là lỗi một dòng mã."
lang: "vi"
order: 2
field: "PAD"
topics:
  ["chống giả mạo", "domain generalization", "hiệu chỉnh ngưỡng", "mất cân bằng lớp", "ISO/IEC 30107-3"]
---

Bài toán: cho một ảnh khuôn mặt, quyết định xem đó là người thật đang ngồi trước camera, hay là một
bức ảnh in, một màn hình đang phát video, một chiếc mặt nạ. Trong tiếng Anh nó có tên chuẩn là
*presentation attack detection*. Nghe như một bài phân loại nhị phân bình thường, và đó chính là chỗ
mọi thứ bắt đầu sai.

## Vì sao đây không phải bài phân loại nhị phân bình thường

Với một bài phân loại thông thường, tập huấn luyện và tập kiểm tra được lấy từ cùng một phân phối,
và giả định đó hợp lý. Với chống giả mạo, giả định đó sai về bản chất.

Kẻ tấn công không bị ràng buộc phải dùng đúng loại tấn công có trong tập huấn luyện. Camera triển khai
thực tế không phải camera đã quay tập dữ liệu. Ánh sáng nơi triển khai không phải ánh sáng phòng lab.
Nói cách khác, đây là bài toán mà **phân phối lúc chạy thật chắc chắn khác phân phối lúc huấn luyện**,
và độ khó thật nằm ở chỗ đó chứ không nằm ở việc phân biệt thật–giả trên dữ liệu đã thấy.

Điều này dẫn tới hệ quả trực tiếp về cách đánh giá: một con số đo trên phần dữ liệu giữ lại của
cùng bộ dữ liệu gần như không nói gì về khả năng dùng được. Mô hình có thể đã học đặc điểm của chiếc
máy in cụ thể dùng để tạo ảnh giả, hoặc đặc điểm nén của màn hình cụ thể dùng để phát lại — những
thứ hoàn toàn vô dụng khi gặp thiết bị khác.

## Ngành công nghiệp đã chuẩn hoá việc này

Có một tiêu chuẩn quốc tế riêng cho việc đo lường: **ISO/IEC 30107-3** — *Information technology,
Biometric presentation attack detection, Part 3: Testing and reporting*, bản hiện hành ban hành năm
2023. Tiêu chuẩn này quy định cách đánh giá và cách báo cáo kết quả, chứ không quy định phải dùng
thuật toán nào.

Bộ chỉ số nó chuẩn hoá gồm ba đại lượng:

- **APCER** — tỷ lệ tấn công giả mạo bị phân loại nhầm thành hợp lệ. Đây là chỉ số bảo mật: nó đo
  xem bao nhiêu kẻ tấn công lọt qua.
- **BPCER** — tỷ lệ người dùng thật bị từ chối nhầm. Đây là chỉ số trải nghiệm: nó đo xem hệ thống
  gây phiền toái đến đâu.
- **ACER** — trung bình cộng của hai đại lượng trên.

Việc tách bạch hai loại lỗi này quan trọng hơn nhiều so với một con số độ chính xác gộp chung, vì
hai loại lỗi có hậu quả hoàn toàn khác nhau. Một hệ thống mở khoá điện thoại và một hệ thống xác thực
giao dịch ngân hàng cần hai điểm cân bằng khác nhau trên cùng một đường cong đánh đổi.

Về protocol đánh giá, bộ dữ liệu **OULU-NPU** đưa ra một thiết kế đáng học: bốn protocol, mỗi protocol
cố tình đặt vào tập kiểm tra ít nhất một điều kiện chưa từng xuất hiện trong tập huấn luyện — thiết bị
chụp mới, môi trường mới, hoặc kiểu tấn công mới. Mục đích là ép mô hình phải khái quát hoá thay vì
học thuộc. Các bộ khác như SiW hay CASIA-SURF đi theo cùng tinh thần, và các paper nghiêm túc trong
lĩnh vực đều báo cáo cả kết quả trong cùng bộ dữ liệu lẫn kết quả chéo bộ dữ liệu.

## Cái bẫy: một ngưỡng cứng đặt lên đại lượng chưa được chuyển đổi

Có một lỗi kỹ thuật nhỏ nhưng hậu quả rất lớn, và nó phổ biến hơn nhiều người nghĩ.

Trong PyTorch, cách viết chuẩn cho bài phân loại nhị phân là để lớp cuối của mạng trả về **logit thô**
— một số thực không giới hạn — rồi dùng hàm mất mát `BCEWithLogitsLoss`. Hàm này tự áp sigmoid bên
trong, vừa đúng về mặt số học vừa ổn định hơn khi tính gradient. Đây là cách làm được khuyến nghị.

Vấn đề nảy sinh ở bước đánh giá. Nếu đoạn mã đánh giá lấy thẳng đầu ra của mô hình rồi so với ngưỡng
0,5, nó đang so **một logit** với một ngưỡng vốn chỉ có ý nghĩa với **xác suất**. Logit bằng 0 tương
ứng xác suất 0,5; ngưỡng 0,5 trên thang logit thực chất tương ứng xác suất khoảng 0,62. Ranh giới
quyết định bị dịch đi một cách âm thầm.

Điều làm lỗi này nguy hiểm là nó không gây ra lỗi chạy. Mã vẫn chạy, vẫn ra số, và số đó vẫn nằm
trong khoảng hợp lệ. Nó chỉ sai.

Có một cách phát hiện rất gọn: so con số độ chính xác tại ngưỡng cố định với **EER** — mức lỗi tại
điểm mà hai loại lỗi bằng nhau, tính từ đường cong ROC nên không phụ thuộc vào việc đầu ra đang ở
thang nào. Nếu độ chính xác tại ngưỡng cố định tệ hơn hẳn so với mức EER cho thấy là khả thi, thì
vấn đề nằm ở ngưỡng chứ không nằm ở mô hình. Mô hình vẫn xếp hạng đúng; chỉ có vạch cắt là sai chỗ.

Đây cũng chính là lý do ngành đo bằng **đường cong** chứ không bằng một điểm. Ngoài ROC còn có
**đường cong DET**, được đề xuất từ năm 1997 cho đúng lớp bài toán có đánh đổi hai loại lỗi: nó vẽ
trên thang log nên phần quan trọng — vùng quanh điểm cân bằng — được giãn ra và dễ so sánh hơn.
Báo cáo một con số tại một ngưỡng là báo cáo đúng một điểm trên đường cong ấy, và điểm đó có thể
được chọn có lợi hoặc chọn nhầm.

## Khi tập kiểm tra lệch lớp, độ chính xác kể chuyện sai

Còn một tầng nữa làm con số méo thêm. Các bộ dữ liệu chống giả mạo thường lệch lớp mạnh, vì tạo mẫu
tấn công dễ hơn nhiều so với thu thập mẫu thật: một khuôn mặt thật có thể sinh ra hàng chục biến thể
tấn công khác nhau.

Khi tập kiểm tra có phần lớn là mẫu tấn công, một mô hình thiên về việc đoán "thật" sẽ sai trên đa số
mẫu, và độ chính xác tụt xuống dưới mức của phép đoán ngẫu nhiên. Nhìn con số đó, phản xạ tự nhiên là
kết luận mô hình vô dụng. Nhưng nếu diện tích dưới đường cong ROC vẫn cao rõ rệt so với mức 0,5, thì
kết luận đó sai: mô hình vẫn phân biệt được, chỉ là vạch cắt đặt sai và tập kiểm tra khuếch đại hậu
quả lên.

Hai điều rút ra. Thứ nhất, độ chính xác là chỉ số tệ khi lớp không cân bằng — đây là lý do tiêu chuẩn
ISO tách APCER và BPCER thay vì gộp. Thứ hai, khi các chỉ số mâu thuẫn nhau, chỉ số **không phụ thuộc
ngưỡng** đáng tin hơn: nó nói về chất lượng của mô hình, còn chỉ số phụ thuộc ngưỡng nói về chất lượng
của một quyết định vận hành.

## Về việc đóng băng mô hình nền

Một chi tiết nhỏ nhưng đáng ghi lại: khi dùng một mô hình thị giác lớn đã huấn luyện sẵn và đóng băng
toàn bộ phần nền, chỉ huấn luyện phần đầu phân loại, số tham số thực sự được cập nhật có thể chỉ còn
một phần rất nhỏ so với tổng.

Cách làm này hợp lý khi dữ liệu ít và đặc trưng cần dùng gần với đặc trưng mà mô hình nền đã học.
Nhưng chống giả mạo phụ thuộc vào **tín hiệu kết cấu bề mặt tần số cao** — vệt moiré của màn hình,
hạt giấy in, phản xạ không tự nhiên — mà một mô hình huấn luyện cho phân loại vật thể có xu hướng
loại bỏ, vì với bài toán đó chúng chỉ là nhiễu. Đóng băng phần nền ở đây đồng nghĩa với việc khoá
mô hình vào một không gian đặc trưng đã bỏ mất đúng thứ cần dùng.

Đây là một dạng lệch giả định thầm lặng: kỹ thuật đúng, áp vào sai bài toán.

## Điều còn đọng lại

Chống giả mạo là bài toán mà **cách đo quan trọng ngang với cách mô hình hoá**. Ba điều đáng mang theo:

Báo cáo trong cùng bộ dữ liệu gần như vô nghĩa. Nếu chỉ được chọn một con số để báo cáo, hãy chọn con
số đo trên bộ dữ liệu mà mô hình chưa từng thấy khi huấn luyện.

Tách hai loại lỗi ra, đừng gộp. Tiêu chuẩn quốc tế tách chúng vì hậu quả của chúng khác nhau, và điểm
vận hành phù hợp phụ thuộc vào việc hệ thống bảo vệ cái gì.

Và trước khi kết luận một mô hình đã hỏng, hãy kiểm tra xem đại lượng đang so với ngưỡng có đúng là
đại lượng mà ngưỡng ấy được định nghĩa cho hay không. Khoảng cách giữa "mô hình vô dụng" và "mô hình
dùng được" đôi khi chỉ là một lời gọi hàm bị thiếu.
