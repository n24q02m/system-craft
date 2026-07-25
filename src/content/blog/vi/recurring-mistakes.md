---
title: "Năm nguyên tắc dùng chung cho mọi hệ học máy"
description: "Những thói quen kỹ thuật giữ nguyên giá trị qua mọi lĩnh vực: dựng bất biến kiểm tra được, phòng rò rỉ dữ liệu, đặt hệ quy chiếu, chọn thước đo, và giữ cấu hình đi cùng hiện vật."
lang: "vi"
order: 6
field: "META"
topics: ["thực hành ML", "rò rỉ dữ liệu", "baseline", "chọn chỉ số", "nợ kỹ thuật"]
---

Năm bài trước đi qua năm lĩnh vực khác nhau: gợi ý nội dung, sinh trắc học, ngôn ngữ, thị giác máy tính, chuỗi thời gian. Chúng khác nhau về dữ liệu, về kiến trúc, về cách đo. Nhưng có một nhóm nguyên tắc xuất hiện lại ở cả năm, và chúng không liên quan gì tới việc chọn mô hình.

Bài này gom chúng lại. Điểm chung: tất cả đều là **thói quen về quy trình**, rẻ để áp dụng, và giá trị của chúng tăng theo độ phức tạp của hệ thống.

## Nguyên tắc một: dựng bất biến kiểm tra được ở mỗi tầng

<figure class="diagram">
<svg viewBox="0 0 640 178" role="img" aria-label="So sánh cách lỗi biểu hiện trong phần mềm thường và trong hệ học máy">
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">PHẦN MỀM THÔNG THƯỜNG</text>
    <text class="lbl" x="340" y="14" font-size="9.5">HỆ HỌC MÁY</text>
  </g>
  <rect class="box" x="0" y="24" width="300" height="130"/>
  <rect class="box-accent" x="340" y="24" width="300" height="130"/>
  <g font-size="11.5">
    <text x="14" y="48">Lỗi thường tự phơi bày</text>
    <text x="354" y="48">Lỗi thường bị hấp thụ</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="14" y="74">chương trình dừng</text>
    <text x="14" y="94">giá trị rõ ràng vô lý</text>
    <text x="14" y="114">kiểu dữ liệu không khớp</text>
    <text x="354" y="74">xác suất luôn nằm giữa 0 và 1</text>
    <text x="354" y="94">danh sách luôn đủ số mục</text>
    <text x="354" y="114">chỉ số vẫn tính ra được</text>
  </g>
  <g font-size="10.5">
    <text x="14" y="140">có cơ chế phát tín hiệu sẵn</text>
    <text x="354" y="140">phải tự dựng bất biến để phát hiện</text>
  </g>
</svg>
<figcaption>Đầu ra của hệ học máy gần như luôn nằm trong miền hợp lệ, nên không có cơ chế tự nhiên nào báo hiệu khi có gì đó sai.</figcaption>
</figure>

Học máy khác phần mềm truyền thống ở một điểm căn bản. Trong phần mềm truyền thống, một hàm sai thường tạo ra hành vi sai quan sát được: chương trình dừng, hoặc trả về giá trị rõ ràng vô lý. Trong học máy, đầu ra gần như luôn nằm trong miền hợp lệ — một xác suất luôn nằm giữa 0 và 1, một danh sách gợi ý luôn có đủ số mục yêu cầu — nên không có cơ chế tự nhiên nào phát tín hiệu khi có gì đó không ổn.

Cách bù lại là dựng sẵn các **bất biến** — những điều kiện phải luôn đúng nếu hệ thống hoạt động bình thường — và kiểm tra chúng lúc khởi động thay vì lúc phân tích kết quả. Vài ví dụ áp dụng được ngay:

- Chỉ mục vector phải có số phần tử khớp với số mục đang phục vụ. Nếu chỉ mục chỉ phủ một phần nhỏ danh mục, dịch vụ nên từ chối khởi động thay vì phục vụ im lặng.
- Tỷ lệ mục có biểu diễn rỗng nên được theo dõi như một chỉ số vận hành, ngang hàng với độ trễ.
- Đầu ra của hệ gợi ý nên được đo độ đa dạng. Nếu phần lớn người dùng nhận cùng một danh sách, hệ thống đang không cá nhân hoá, bất kể chỉ số xếp hạng nói gì.
- Mô hình khi được nạp nên mang theo chỉ số của chính nó cùng một mốc so sánh; nếu chỉ số thấp hơn mốc thì việc nạp nên thất bại.

Điểm chung của các kiểm tra này: chúng biến một sự cố thầm lặng thành một sự cố ồn ào. Đó là toàn bộ mục đích, và cũng là lý do chúng đáng được viết trước khi cần đến.

Đây không phải quan sát mới. Một công trình được trích dẫn rộng rãi về **nợ kỹ thuật trong hệ thống học máy** mô tả đúng hiện tượng này ở quy mô công nghiệp: các hệ học máy tích luỹ một loại nợ đặc thù mà công cụ kỹ thuật phần mềm truyền thống không nhìn thấy — ranh giới giữa các thành phần bị xói mòn, các thành phần vướng vào nhau đến mức đổi một đặc trưng kéo theo mọi thứ đổi, những nơi tiêu thụ dữ liệu không được khai báo, những vòng phản hồi ẩn. Cái giá của các khoản nợ này đến muộn, và đến dưới dạng chi phí bảo trì chứ không phải dưới dạng lỗi.

## Nguyên tắc hai: hỏi "thông tin này có tồn tại lúc dự đoán không"

Rò rỉ dữ liệu là khi thông tin lẽ ra không được biết tại thời điểm dự đoán lại lọt vào quá trình huấn luyện. Dạng cơ bản thì ai cũng biết: chia tập ngẫu nhiên trên dữ liệu có thứ tự thời gian. Các dạng khác tinh vi hơn nhiều.

**Thông tin toàn cục lọt vào bước tiền xử lý.** Chuẩn hoá bằng trung bình và độ lệch chuẩn tính trên toàn bộ dữ liệu, bao gồm cả phần dành để kiểm tra, là ví dụ kinh điển. Chọn đặc trưng dựa trên tương quan với nhãn tính trên toàn bộ dữ liệu cũng vậy.

**Thuộc tính của đối tượng lọt vào dấu thời gian của sự kiện.** Nếu thời điểm một người tương tác với một nội dung được suy ra từ thuộc tính của chính nội dung đó thay vì từ hành vi thật, thì mọi chuỗi hành vi bị ép về cùng một hình dạng, và mô hình có trục thời gian sẽ học hình dạng ấy thay vì học sở thích.

**Đơn vị lặp lại giữa các tập.** Nhiều mẫu sinh ra từ cùng một nguồn — nhiều khung hình từ một video, nhiều đoạn từ một bài báo, nhiều lần đo từ một trạm — nếu rơi vào cả tập huấn luyện lẫn tập kiểm tra thì mô hình đã thấy trước câu trả lời dưới dạng hơi khác.

Đây không phải vấn đề của riêng dự án nhỏ. Một khảo sát trên các công trình khoa học ứng dụng học máy đã tìm thấy lỗi rò rỉ ở hàng trăm bài báo trải khắp nhiều lĩnh vực, và phân loại chúng thành nhiều kiểu khác nhau. Trong một trường hợp được phân tích kỹ, sau khi sửa rò rỉ thì các mô hình học máy phức tạp không còn vượt trội so với một mô hình hồi quy tuyến tính cổ điển — toàn bộ kết luận đã phải xem lại. Nhóm tác giả đề xuất kèm theo mỗi công bố một bản mô tả mô hình ghi rõ cách chia dữ liệu và các bước tiền xử lý, để lỗi loại này lộ ra trước khi công bố.

Phép phòng thủ tốt nhất là một câu hỏi duy nhất, hỏi cho từng đặc trưng: *thông tin này có thực sự tồn tại tại thời điểm cần dự đoán không?* Nếu câu trả lời không rõ ràng ngay, đó là chỗ đáng đào.

## Nguyên tắc ba: đặt hệ quy chiếu trước khi đo

Một con số tự nó không nói lên điều gì. Nó chỉ có nghĩa khi đặt cạnh một mốc.

Điều này nghe hiển nhiên, nhưng bước dựng baseline lại hay bị bỏ qua nhất, vì nó không thú vị và có cảm giác như đang làm thứ chắc chắn sẽ bị thay thế.

Hậu quả rất cụ thể. Một chỉ số nghe có vẻ thấp có thể thực ra là tốt nếu bài toán khó — trong tìm kiếm trên danh mục hàng trăm nghìn mục, một chỉ số nhỏ vẫn có thể gấp hàng trăm lần mức ngẫu nhiên. Ngược lại, một chỉ số nghe có vẻ cao có thể tệ hơn cả việc đoán theo lớp đông nhất. Không có mốc, cả hai trường hợp đều bị đọc sai, và quyết định tiếp theo — đầu tư thêm hay dừng lại — được đưa ra trên nền tảng sai.

Baseline hợp lý khác nhau theo lĩnh vực: gợi ý theo độ phổ biến cho hệ gợi ý; đoán lớp đông nhất cho phân loại; dự báo bằng giá trị gần nhất cho chuỗi thời gian. Điểm chung là tất cả đều mất vài phút để dựng.

Bộ hướng dẫn thực hành công nghiệp được biết đến rộng rãi nhất đặt điều này lên rất sớm trong danh sách quy tắc của nó: giữ mô hình đầu tiên thật đơn giản và tập trung làm đúng hạ tầng; kiểm thử hạ tầng tách rời khỏi phần học máy; chọn một chỉ số đơn giản, quan sát được và quy được trách nhiệm cho mục tiêu đầu tiên; phát hiện vấn đề trước khi xuất mô hình ra. Thứ tự này không ngẫu nhiên.

## Nguyên tắc bốn: chọn thước đo theo đặc tính dữ liệu

Mỗi lĩnh vực đều có ít nhất một chỉ số phổ biến nhưng gây hiểu lầm trong điều kiện thường gặp.

**Độ chính xác trên tập lệch lớp.** Khi một lớp chiếm đa số áp đảo, đoán luôn lớp đó đã cho độ chính xác cao. Đây là lý do các tiêu chuẩn về phát hiện tấn công trình bày tách riêng hai loại lỗi thay vì gộp, và là lý do các chỉ số trung bình theo lớp tồn tại bên cạnh chỉ số vi mô.

**Chỉ số gộp che lớp hiếm.** Trong phát hiện đối tượng, chỉ số trung bình trên mọi lớp có thể tăng trong khi lớp ít mẫu nhất đang tệ đi. Các bộ dữ liệu được thiết kế riêng để phơi bày điều này đều báo cáo tách theo nhóm tần suất lớp.

**Sai số phần trăm khi giá trị gần 0.** Với dữ liệu mà trạng thái bình thường là giá trị nhỏ, chia cho giá trị thật tạo ra những con số vô nghĩa. Các chỉ số chuẩn hoá theo baseline được đề xuất chính để giải quyết việc này.

**Chỉ số chỉ so được trong cùng điều kiện.** Độ bối rối của hai mô hình ngôn ngữ chỉ so được khi chúng dùng chung bộ từ vựng — điều kiện này được nêu rõ trong giáo trình chuẩn nhưng rất dễ bị bỏ qua khi thay đổi cách tách từ giữa các thí nghiệm.

Mẫu hình chung: **chỉ số nào cũng có điều kiện áp dụng, và điều kiện ấy thường không được viết cạnh con số.** Khi hai chỉ số cùng đo một mô hình mà cho kết luận trái ngược, sự chênh lệch đó là thông tin cần điều tra, không phải thứ để chọn bên nghe thuận tai hơn.

## Nguyên tắc năm: hiện vật phải mang theo cấu hình sinh ra nó

Trong hầu hết mã nghiên cứu đều có những tham số điều khiển quy mô chạy: dùng bao nhiêu phần trăm dữ liệu, chạy bao nhiêu vòng, giới hạn thời gian bao lâu. Chúng tồn tại vì lý do chính đáng — khi đang gỡ lỗi đường ống, chạy trên một phần nhỏ tiết kiệm rất nhiều thời gian.

Rủi ro nằm ở chỗ các tham số này thường có giá trị mặc định dành cho chạy thử, và khi chuyển sang chạy thật thì dễ quên đặt lại. Hệ thống vẫn chạy, vẫn ra số, vẫn lưu được mô hình — không có tín hiệu nào cho thấy có vấn đề.

Nguy hiểm hơn nữa: khi các tham số này khác nhau giữa các lần thí nghiệm, mọi so sánh giữa chúng đều mất giá trị. Nếu một lần chạy dùng ít dữ liệu hơn lần trước, kết quả kém hơn không nói gì về kiến trúc. Điều tương tự xảy ra khi việc huấn luyện dừng vì hết ngân sách thời gian chứ không phải vì hội tụ — con số thu được là "tốt nhất trong một ngân sách", không phải kết quả của phương pháp.

Cách phòng thủ đơn giản đến mức gần như tầm thường, nhưng hiệu quả: in ra cấu hình thực tế ở đầu mỗi lần chạy, và **ghi nó vào cùng chỗ với mô hình đã lưu**. Một tệp trọng số không kèm cấu hình sinh ra nó — số lớp, kích thước đầu vào, cách chuẩn hoá, lượng dữ liệu, số vòng — là một tệp nhị phân không diễn giải được sau vài tháng.

## Sợi chỉ xuyên suốt

Năm nguyên tắc trên nhìn thì rời rạc, nhưng chúng có chung một gốc: **trong học máy, khoảng cách giữa "chạy được" và "đúng" rộng hơn nhiều so với trong phần mềm thông thường, và không có cơ chế tự nhiên nào lấp khoảng cách ấy.**

Phần mềm thông thường có xu hướng tự phơi bày lỗi. Hệ học máy có xu hướng hấp thụ lỗi và tiếp tục sản xuất ra thứ trông giống kết quả. Vì vậy phần lớn công việc kỹ thuật thực sự không nằm ở chỗ chọn mô hình, mà ở chỗ dựng đủ điểm quan sát để biết mô hình đang thực sự làm gì.

Có một quan sát từ nghiên cứu thực địa đáng nhắc ở đây: khi phỏng vấn những người làm học máy trên các bài toán có rủi ro cao, phần lớn cho biết từng gặp chuỗi sự cố dồn tích bắt nguồn từ chất lượng dữ liệu. Kết luận của nghiên cứu ấy nằm ngay trong tiêu đề — ai cũng muốn làm phần mô hình, ít ai muốn làm phần dữ liệu.

Nếu chỉ giữ lại một thói quen từ tất cả những điều trên: trước khi huấn luyện bất cứ thứ gì, hãy dành một buổi chứng minh rằng tín hiệu cần học thực sự tồn tại trong dữ liệu — bằng thống kê đơn giản, bằng việc tự tay xem vài chục mẫu, bằng một baseline ngớ ngẩn. Buổi đó rẻ hơn rất nhiều so với những gì nó tránh được.
