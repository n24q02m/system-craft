---
title: "Năm sai lầm lặp lại qua mọi dự án"
description: "Những lỗi không nằm ở kiến trúc hay siêu tham số, mà nằm ở khoảng trống giữa việc chạy được và việc đúng — và chúng xuất hiện lại ở mọi lĩnh vực."
lang: "vi"
order: 6
field: "META"
topics: ["hỏng im lặng", "rò rỉ dữ liệu", "baseline", "chọn chỉ số", "nợ kỹ thuật"]
---

Nhìn lại nhiều hệ thống ở nhiều lĩnh vực khác nhau — gợi ý nội dung, thị giác máy tính, ngôn ngữ, chuỗi
thời gian — có một điều nổi lên: các lỗi nghiêm trọng gần như không bao giờ nằm ở chỗ người ta dành
nhiều thời gian nhất.

Không có lỗi nào trong số này là do chọn sai kiến trúc mạng. Không có lỗi nào do siêu tham số. Chúng
nằm ở những chỗ ít ai kiểm tra, và chúng lặp lại với độ đều đặn đáng ngạc nhiên.

## Một: hệ thống hỏng mà không báo lỗi

Đây là mẫu hình bao trùm. Trong phần lớn các trường hợp, hệ thống hỏng vẫn **chạy trơn tru**: nó nhận
đầu vào, trả về đầu ra đúng định dạng, không ném ngoại lệ, và giao diện hiển thị đầy đủ. Chỉ có điều
kết quả không mang thông tin gì.

Vì sao dạng hỏng này phổ biến đến vậy? Vì học máy khác phần mềm truyền thống ở một điểm căn bản. Trong
phần mềm truyền thống, một hàm sai thường tạo ra hành vi sai quan sát được: chương trình sập, hoặc trả
về giá trị rõ ràng vô lý. Trong học máy, đầu ra luôn nằm trong miền hợp lệ — một xác suất luôn nằm giữa
0 và 1, một danh sách gợi ý luôn có đủ mười mục — nên không có cơ chế tự nhiên nào phát tín hiệu.

Cách phòng thủ là dựng **bất biến kiểm tra được** ở mỗi tầng, và kiểm tra chúng lúc khởi động thay vì
lúc phân tích kết quả. Vài ví dụ cụ thể, rẻ và hiệu quả:

- Chỉ mục vector phải có số phần tử khớp với số mục đang phục vụ. Nếu chỉ mục chỉ chứa một phần nhỏ
  danh mục, dịch vụ nên từ chối khởi động chứ không nên phục vụ im lặng.
- Tỷ lệ mục có biểu diễn rỗng phải được theo dõi như một chỉ số vận hành.
- Đầu ra của hệ gợi ý phải được đo độ đa dạng: nếu phần lớn người dùng nhận cùng một danh sách, hệ
  thống đang không cá nhân hoá, bất kể chỉ số xếp hạng ra sao.
- Mọi mô hình khi nạp lên phải mang theo chỉ số của chính nó và một mốc so sánh; nếu chỉ số đó thấp
  hơn mốc, việc nạp phải thất bại.

Điểm chung của các kiểm tra này: chúng biến một lỗi im lặng thành một lỗi ồn ào. Đó là toàn bộ mục đích.

## Hai: dữ liệu rò rỉ theo những đường không ngờ

Rò rỉ dữ liệu là khi thông tin lẽ ra không được biết lúc dự đoán lại lọt vào tập huấn luyện. Ai cũng
biết dạng cơ bản của nó — chia tập ngẫu nhiên trên dữ liệu có thứ tự thời gian. Nhưng các dạng khác
tinh vi hơn nhiều.

Một dạng đáng nhớ: **dấu thời gian được sinh từ thuộc tính của đối tượng thay vì từ hành vi**. Nếu thời
điểm một người tương tác với một nội dung được suy ra từ ngày nội dung đó xuất hiện, thì mọi chuỗi hành
vi trong hệ thống đều bị ép về cùng một hình dạng, và mô hình chuỗi chỉ cần học hình dạng đó là đạt chỉ
số cao. Không ai cố tình tạo ra rò rỉ này; nó là tác dụng phụ của một dòng mã trông rất vô hại trong
bước sinh dữ liệu.

Một dạng khác: **thông tin toàn cục lọt vào bước tiền xử lý**. Chuẩn hoá bằng trung bình và độ lệch
chuẩn tính trên toàn bộ dữ liệu — bao gồm cả tập kiểm tra — là ví dụ kinh điển. Chọn đặc trưng dựa
trên tương quan với nhãn tính trên toàn bộ dữ liệu cũng vậy.

Đây không phải vấn đề của riêng dự án nhỏ. Một khảo sát quy mô lớn trên các công trình khoa học ứng
dụng học máy đã tìm thấy lỗi rò rỉ ở hàng trăm bài báo trải khắp nhiều lĩnh vực, và phân loại chúng
thành nhiều kiểu khác nhau. Trong một trường hợp được phân tích kỹ, sau khi sửa rò rỉ thì các mô hình
học máy phức tạp **không còn vượt trội** so với một mô hình hồi quy tuyến tính có tuổi đời hàng chục
năm. Toàn bộ kết luận của lĩnh vực đó đã phải xem lại.

Cách phòng thủ tốt nhất là một câu hỏi đơn giản, hỏi cho từng đặc trưng: *thông tin này có thực sự tồn
tại tại thời điểm cần dự đoán không?* Nếu câu trả lời không rõ ràng, đó là chỗ cần đào.

## Ba: không có baseline thì không có ý nghĩa

Một con số tự nó không nói lên điều gì. Nó chỉ có nghĩa khi đặt cạnh một mốc.

Điều này nghe hiển nhiên, nhưng trong thực tế bước dựng baseline hay bị bỏ qua nhất — vì nó không thú
vị, và vì có cảm giác như đang lãng phí thời gian vào thứ chắc chắn sẽ bị thay thế.

Hậu quả thì cụ thể. Một chỉ số nghe có vẻ thấp có thể thực ra là tốt nếu bài toán khó. Một chỉ số nghe
có vẻ cao có thể tệ hơn cả việc đoán theo lớp đông nhất. Không có mốc so sánh, cả hai trường hợp đều
bị đọc sai, và quyết định tiếp theo — đầu tư thêm hay dừng lại — được đưa ra trên nền tảng sai.

Các tài liệu hướng dẫn thực hành của ngành đặt điều này lên rất sớm: giữ mô hình đầu tiên thật đơn giản
và tập trung làm đúng hạ tầng; kiểm thử hạ tầng tách rời khỏi phần học máy; chọn một chỉ số đơn giản,
quan sát được và quy được trách nhiệm cho mục tiêu đầu tiên. Thứ tự này không phải ngẫu nhiên — nó
được viết ra vì thứ tự ngược lại đã gây ra quá nhiều thất bại.

Với mỗi lĩnh vực, baseline hợp lý là khác nhau: dự đoán theo độ phổ biến cho hệ gợi ý, đoán lớp đông
nhất cho phân loại, dự báo bằng giá trị gần nhất cho chuỗi thời gian. Điểm chung là chúng đều mất vài
phút để dựng.

## Bốn: chỉ số được chọn vì dễ, không vì đúng

Mỗi lĩnh vực đều có ít nhất một chỉ số phổ biến nhưng gây hiểu lầm trong điều kiện thường gặp.

**Độ chính xác trên tập lệch lớp.** Khi một lớp chiếm đa số áp đảo, đoán luôn lớp đó đã cho độ chính
xác cao. Đây là lý do các tiêu chuẩn về phát hiện tấn công tách riêng hai loại lỗi thay vì gộp thành
một con số, và là lý do các chỉ số trung bình theo lớp tồn tại bên cạnh chỉ số vi mô.

**Chỉ số gộp che lớp hiếm.** Trong phát hiện đối tượng, chỉ số trung bình trên mọi lớp có thể tăng
trong khi lớp ít mẫu nhất đang tệ đi. Các bộ dữ liệu được thiết kế riêng để phơi bày điều này đều báo
cáo tách theo nhóm tần suất lớp.

**Sai số phần trăm khi giá trị gần 0.** Với dữ liệu mà trạng thái bình thường là giá trị nhỏ, chia cho
giá trị thật tạo ra những con số vô nghĩa. Các chỉ số chuẩn hoá theo baseline được đề xuất chính là để
giải quyết việc này.

**Chỉ số so sánh được giữa các cấu hình khác nhau.** Độ bối rối của hai mô hình ngôn ngữ chỉ so được
khi chúng dùng chung bộ từ vựng — một điều kiện được nêu rõ trong giáo trình chuẩn của lĩnh vực nhưng
rất hay bị bỏ qua khi người ta thay tokenizer giữa các lần thí nghiệm.

Mẫu hình chung: **chỉ số nào cũng có điều kiện áp dụng, và điều kiện ấy thường không được viết cạnh
con số.** Khi hai chỉ số cùng đo một mô hình mà cho kết luận trái ngược, sự chênh lệch đó là thông tin
cần điều tra, không phải thứ để chọn bên nào nghe thuận tai hơn.

## Năm: cấu hình để chạy thử rồi quên đặt lại

Đây là lỗi tầm thường nhất trong danh sách, và cũng là lỗi gây thiệt hại nhiều nhất tính trên mỗi dòng
mã.

Trong hầu hết mã nghiên cứu đều có một tham số kiểu "dùng bao nhiêu phần trăm dữ liệu". Nó tồn tại vì
lý do chính đáng: khi đang gỡ lỗi đường ống, chạy trên một phần nhỏ dữ liệu tiết kiệm rất nhiều thời
gian. Vấn đề là nó có giá trị mặc định nhỏ, và khi chuyển sang chạy thật, người ta quên đặt lại.

Hậu quả không dừng ở "mô hình hơi kém hơn". Với một phần nhỏ dữ liệu, mô hình có thể không học được
gì hết, hoặc học được nhưng thất bại theo cách khó truy ngược. Và vì mọi thứ vẫn chạy, vẫn ra số, vẫn
lưu được mô hình, không có tín hiệu nào cho thấy có vấn đề. Đây chính là dạng hỏng im lặng ở mục một,
nhưng với nguyên nhân tầm thường nhất có thể.

Nguy hiểm hơn nữa: khi tham số này khác nhau giữa các lần thí nghiệm, mọi so sánh đều mất giá trị.
Nếu thế hệ mô hình sau dùng ít dữ liệu hơn thế hệ trước, kết quả kém hơn không nói gì về kiến trúc —
nhưng rất dễ bị đọc thành "kiến trúc mới tệ hơn".

Phòng thủ đơn giản đến mức gần như buồn cười, nhưng hiệu quả: in ra cấu hình thực tế ở đầu mỗi lần
chạy, và ghi nó vào cùng chỗ với mô hình đã lưu. Nếu một hiện vật không mang theo cấu hình sinh ra nó,
sáu tháng sau nó là một tệp nhị phân không diễn giải được.

## Sợi chỉ xuyên suốt

Năm mục trên nhìn thì rời rạc, nhưng chúng có chung một gốc: **khoảng cách giữa "chạy được" và "đúng"
trong học máy rộng hơn nhiều so với trong phần mềm thông thường, và không có cơ chế tự nhiên nào lấp
khoảng cách ấy.**

Trong phần mềm thông thường, phần lớn lỗi tự phơi bày. Trong học máy, hệ thống có xu hướng hấp thụ lỗi
và tiếp tục sản xuất ra thứ trông giống kết quả. Điều này đã được mô tả từ lâu dưới góc nhìn nợ kỹ
thuật: các hệ học máy tích luỹ một loại nợ đặc thù mà công cụ kỹ thuật phần mềm truyền thống không
nhìn thấy, và cái giá phải trả đến muộn.

Vì vậy phần lớn công việc kỹ thuật thực sự trong một dự án học máy không phải là chọn mô hình. Nó là
dựng đủ điểm quan sát để biết mô hình đang thực sự làm gì — và dựng chúng **trước** khi cần đến, chứ
không phải sau khi đã nghi ngờ.

Nếu chỉ giữ lại một thói quen từ tất cả những điều trên: trước khi huấn luyện bất cứ thứ gì, hãy bỏ ra
một buổi chứng minh rằng tín hiệu cần học thực sự tồn tại trong dữ liệu — bằng thống kê đơn giản, bằng
việc tự tay xem vài chục mẫu, bằng một baseline ngớ ngẩn. Buổi đó rẻ hơn rất nhiều so với những gì nó
tránh được.
