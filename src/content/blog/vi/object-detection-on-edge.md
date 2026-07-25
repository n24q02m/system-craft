---
title: "Phát hiện phương tiện giao thông và đường đi xuống thiết bị biên"
description: "Phát hiện phương tiện trong điều kiện thời tiết xấu trên phần cứng hạn chế: augmentation hai tầng, chưng cất tri thức, và đường xuống thiết bị."
lang: "vi"
order: 4
field: "DET"
topics: ["phát hiện đối tượng", "chưng cất tri thức", "mAP", "thiết bị biên", "augmentation"]
---

Một camera giao thông nhìn xuống mặt đường và sinh ra khung hình liên tục. Việc cần làm là từ mỗi khung hình xác định có những phương tiện nào, chúng thuộc loại gì, và nằm ở đâu trong ảnh. Đây là bài toán phát hiện đối tượng, một trong những bài toán được nghiên cứu nhiều nhất của thị giác máy tính, và với ảnh chụp ban ngày trời quang thì các mô hình sẵn có giải quyết khá tốt.

Độ khó đến từ hai ràng buộc đi kèm. Thứ nhất, hệ thống phải hoạt động trong đúng những điều kiện mà dữ liệu chuẩn hiếm khi có: trời mưa, ban đêm, đèn pha loá vào ống kính, sương mù. Thứ hai, mô hình phải chạy được trên thiết bị đặt ngoài hiện trường chứ không phải trên máy chủ có GPU — nghĩa là bị giới hạn về số tham số, về bộ nhớ, và chỉ có CPU.

Hai ràng buộc này kéo về hai hướng ngược nhau. Xử lý điều kiện xấu thường cần mô hình mạnh hơn và dữ liệu đa dạng hơn; chạy trên thiết bị biên lại đòi mô hình nhỏ hơn. Phần lớn công việc kỹ thuật nằm ở chỗ hoà giải chúng.

## Hệ thống đã dựng

### Dữ liệu và bốn lớp cần phân biệt

Dữ liệu là ảnh chụp từ camera giao thông thực tế. Ban đầu nhãn được tách theo điều kiện ngày và đêm, sau đó gộp lại thành bốn lớp chung: xe máy, ô tô, xe buýt, xe tải. Việc gộp có lý do thực dụng — một chiếc ô tô ban đêm vẫn là ô tô, và tách lớp theo thời điểm chụp chỉ làm loãng dữ liệu của mỗi lớp.

Phân bố lớp rất lệch. Xe máy áp đảo về số lượng, xe buýt thưa thớt, và chênh lệch giữa lớp đông nhất với lớp thưa nhất lớn tới mức mọi chỉ số gộp đều bị lớp đông chi phối. Đây không phải khiếm khuyết của việc thu thập mà là phản ánh đúng thực tế giao thông; nó cần được xử lý ở tầng phương pháp và tầng báo cáo, không phải bằng cách thu thêm dữ liệu.

Có thêm một bước sinh ảnh nền không chứa đối tượng bằng kỹ thuật inpainting: lấy ảnh thật, xoá phương tiện đi và để thuật toán lấp lại phần bị xoá bằng nền hợp lý. Những ảnh này làm mẫu âm, dạy mô hình rằng một đoạn đường trống thì không có gì để báo.

### Augmentation hai tầng

Tăng cường dữ liệu được chia thành hai tầng, và ranh giới giữa chúng là một quyết định thiết kế có ý thức.

Tầng ngoại tuyến chạy trước khi huấn luyện, bằng một thư viện biến đổi ảnh chuyên dụng, và kết quả được lưu thành ảnh trên đĩa. Nhóm biến đổi gồm: lật ngang; dịch, xoay, co giãn; đổi màu sắc và độ sáng; làm mờ; thêm nhiễu. Nhóm quan trọng nhất là các phép mô phỏng thời tiết — mưa, sương mù, tuyết, bóng đổ, loá nắng. Nhóm này khớp trực tiếp với yêu cầu về điều kiện xấu, và cũng là nhóm tốn kém nhất về mặt tính toán.

Tầng trong lúc huấn luyện, tức phần augmentation tích hợp sẵn của framework, thì gần như tắt hết. Chỉ còn giữ mosaic — ghép bốn ảnh thành một để mô hình gặp nhiều ngữ cảnh và nhiều tỷ lệ trong một mẫu — cùng phép xoá ngẫu nhiên một vùng ảnh.

Sự phân chia này đến từ một đánh đổi cụ thể. Sinh biến thể trong lúc huấn luyện là mặc định của hầu hết framework vì mỗi epoch mô hình thấy một biến thể khác nhau, nên hiệu quả chống quá khớp cao hơn với cùng dung lượng lưu trữ. Nhưng các phép mô phỏng thời tiết đắt, và trả giá đó ở mỗi epoch là lãng phí; tính một lần rồi lưu lại thì rẻ hơn nhiều.

Rủi ro của việc bật cả hai tầng cùng lúc cũng cụ thể không kém: biến dạng cộng dồn. Một ảnh đã được nướng sẵn mưa và giảm sáng, nếu tiếp tục bị đổi màu và làm mờ lúc chạy, có thể trôi xa khỏi bất kỳ khung hình nào camera thật từng ghi được. Chọn một tầng làm chính và ghi lại lý do là cách tránh tình huống đó.

### Kiến trúc student-teacher

Ràng buộc về kích thước mô hình được giải bằng chưng cất tri thức, với hai mô hình đóng hai vai.

**Thầy** là một mô hình phát hiện đối tượng cỡ lớn thuộc dòng YOLO, tinh chỉnh từ trọng số đã huấn luyện sẵn trên tập ảnh tổng quát. Vai trò của nó chỉ là nguồn tín hiệu giám sát; nó không bao giờ được triển khai.

**Trò** là một kiến trúc tự định nghĩa qua file cấu hình, với ba thay đổi so với thiết kế gốc:

- Toàn bộ tích chập chuẩn được thay bằng tích chập tách theo chiều sâu, hoặc biến thể Ghost. Đây là phần cắt giảm tham số chủ yếu.
- Thêm một đầu phát hiện ở mức phân giải cao hơn, thành bốn đầu thay vì ba. Phương tiện ở xa trong khung hình camera giao thông chiếm rất ít pixel, và một đầu ở phân giải cao hơn cho mô hình cơ hội bắt được chúng.
- Không dùng module attention nào. Đây là ràng buộc chủ động: các khối chú ý làm tăng độ trễ và thường được hỗ trợ kém trên runtime di động, nên chúng bị loại ngay từ khâu thiết kế.

Quá trình chưng cất giữ thầy ở trạng thái đóng băng. Hàm mất mát gồm hai phần: phần phát hiện thông thường tính trên nhãn thật, cộng phần chưng cất dựa trên phân kỳ KL giữa phân phối đầu ra của trò và của thầy. Phần thứ hai có hai tham số điều khiển — nhiệt độ, làm mềm phân phối để các lớp có xác suất thấp vẫn đóng góp tín hiệu; và hệ số pha trộn, quyết định trò nghe nhãn thật hay nghe thầy nhiều hơn.

### Suy luận và tiền xử lý

Hệ thống hỗ trợ hai chế độ suy luận. Chế độ thường đưa cả khung hình qua mô hình một lần. Chế độ theo lát cắt chia ảnh lớn thành các ô có chồng lấn, chạy mô hình trên từng ô rồi ghép kết quả lại — cách này tốn nhiều lần tính toán hơn nhưng làm vật nhỏ trở nên lớn tương đối so với đầu vào của mô hình, nên bắt được những phương tiện ở xa mà chế độ thường bỏ sót. Phần chồng lấn tồn tại để một phương tiện nằm vắt qua ranh giới hai ô không bị cắt đôi.

Ngoài ra có một bước tiền xử lý tuỳ chọn gồm cân bằng histogram thích ứng, khử nhiễu và làm nét, nhắm vào các khung hình thiếu sáng hoặc tương phản kém. Và có lượng tử hoá động sau huấn luyện áp cho các lớp tuyến tính, đổi một phần độ chính xác lấy kích thước và tốc độ.

### Đưa xuống thiết bị

Phần triển khai là một ứng dụng Android riêng. Nó dùng một runtime suy luận nhẹ chuyên cho di động, kết hợp với một thư viện thị giác máy tính cho phần đọc ảnh và hậu xử lý, và giao tiếp giữa lớp Java với phần tính toán bằng C++ đi qua JNI. Toàn bộ chạy trên CPU, không phụ thuộc vào việc thiết bị có tăng tốc phần cứng hay không.

Mô hình được đóng gói theo định dạng riêng của runtime đó — một cặp tệp, một mô tả cấu trúc mạng và một chứa trọng số — đặt trong thư mục tài nguyên của ứng dụng. Bước chuyển từ định dạng của framework huấn luyện sang cặp tệp này là một mắt xích riêng, và như phần cuối bài sẽ nói, nó cần được kiểm tra như một mắt xích riêng.

## Kiến thức nền

<figure class="diagram">
<svg viewBox="0 0 640 196" role="img" aria-label="Luồng chưng cất tri thức từ mô hình thầy sang mô hình trò rồi xuống thiết bị">
  <defs><marker id="det-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">NGOẠI TUYẾN</text>
    <text class="lbl" x="452" y="14" font-size="9.5">TRÊN THIẾT BỊ</text>
  </g>
  <rect class="box" x="0" y="26" width="172" height="48"/>
  <rect class="box" x="0" y="104" width="172" height="48"/>
  <rect class="box-accent" x="234" y="64" width="178" height="52"/>
  <rect class="box" x="452" y="64" width="188" height="52"/>
  <g class="flow" marker-end="url(#det-a)">
    <path d="M172 50 H206 V84 H228"/>
    <path d="M172 128 H206 V98 H228"/>
    <path d="M412 90 H446"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="48">Mô hình thầy</text>
    <text x="10" y="126">Nhãn thật</text>
    <text x="244" y="84">Mô hình trò</text>
    <text x="462" y="84">Runtime di động</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="64">lớn, chính xác, không triển khai</text>
    <text x="10" y="142">từ dữ liệu đã gán nhãn</text>
    <text x="244" y="100">tích chập tách theo chiều sâu</text>
    <text x="244" y="112">bốn đầu phát hiện, không khối chú ý</text>
    <text x="462" y="100">chạy trên CPU</text>
    <text x="462" y="112">không cần tăng tốc phần cứng</text>
  </g>
  <text x="0" y="176" font-size="10.5" class="dim">Hàm mất mát của trò gồm phần phát hiện trên nhãn thật cộng phần chưng cất theo phân phối của thầy.</text>
  <text x="0" y="192" font-size="10.5" class="dim">Bước chuyển định dạng sang runtime là một mắt xích riêng, cần kiểm tra riêng.</text>
</svg>
<figcaption>Thầy chỉ đóng vai nguồn tín hiệu giám sát và không bao giờ được triển khai.</figcaption>
</figure>

### Đo phát hiện đối tượng: IoU và vì sao cần nhiều ngưỡng

Một dự đoán trong bài toán này gồm một hộp bao và một nhãn lớp. Để biết dự đoán đó đúng hay sai, cần so hộp dự đoán với hộp thật bằng tỷ lệ giao trên hợp — diện tích phần chung chia cho diện tích phần hợp của hai hộp, viết tắt là IoU. Giá trị bằng một nghĩa là trùng khít, bằng không nghĩa là rời nhau hoàn toàn.

Câu hỏi là lấy bao nhiêu làm ngưỡng chấp nhận. Ngưỡng thấp thì dễ dãi với độ chính xác vị trí: một hộp lệch đáng kể vẫn được tính đúng. Ngưỡng cao thì đòi hỏi định vị rất sát. Chọn một ngưỡng duy nhất nghĩa là ngầm quyết định thay cho mọi ứng dụng, trong khi một hệ thống đếm xe và một hệ thống đo khoảng cách có yêu cầu về độ chính xác vị trí khác hẳn nhau. Cách giải quyết của chuẩn hiện hành là lấy trung bình trên nhiều ngưỡng.

### Chưng cất tri thức và trực giác về tri thức tối

Chưng cất tri thức là kỹ thuật huấn luyện một mô hình nhỏ sao cho nó khớp không chỉ với nhãn thật mà còn với phân phối đầu ra của một mô hình lớn hơn đã huấn luyện xong.

Trực giác nằm ở lượng thông tin trong hai loại tín hiệu. Nhãn cứng chỉ nói "đây là xe máy" — một bit thông tin về lớp đúng, không gì hơn. Phân phối đầu ra của thầy nói "đây là xe máy, có phần giống xe đạp, và gần như chắc chắn không phải xe buýt". Cấu trúc quan hệ giữa các lớp đó, đôi khi gọi là tri thức tối, là thứ nhãn cứng không mang theo, và là lý do trò học từ thầy nhanh hơn học từ nhãn thuần tuý.

### Vì sao chưng cất cho detection khác chưng cất cho phân loại

Kỹ thuật này ra đời cho bài phân loại ảnh và không chuyển thẳng sang phát hiện đối tượng được, vì ba khác biệt.

Thứ nhất, phần lớn diện tích một khung hình là nền. Nếu ép trò bắt chước thầy trên toàn bộ bản đồ đặc trưng, gần như toàn bộ tín hiệu học được sẽ nói về nền — thứ không ai quan tâm.

Thứ hai, phát hiện đối tượng có thành phần hồi quy toạ độ chứ không chỉ phân loại. Ép trò khớp hoàn toàn với thầy ở phần toạ độ có thể phản tác dụng khi chính thầy dự đoán lệch.

Thứ ba, mất cân bằng giữa nền và đối tượng nghiêm trọng hơn nhiều so với mất cân bằng lớp trong bài phân loại thông thường, nên hàm mất mát cần có cơ chế bù.

### Đánh đổi giữa độ chính xác và kích thước

Có hai đòn bẩy chính để thu nhỏ mô hình. Tích chập tách theo chiều sâu chia một phép tích chập chuẩn thành hai bước — một phép lọc theo từng kênh riêng, rồi một phép trộn kênh bằng tích chập 1x1 — giảm số phép nhân và số tham số xuống nhiều lần, đổi lại mỗi lớp biểu đạt kém hơn một chút. Lượng tử hoá biểu diễn trọng số bằng số nguyên độ rộng thấp thay vì số thực, giảm dung lượng và tăng tốc trên phần cứng hỗ trợ phép nguyên, đổi lại mất một phần độ phân giải số học.

Cả hai đều là đánh đổi có kiểm soát, và điều quan trọng là chúng phải nằm trong thiết kế ban đầu chứ không phải được áp vào một mô hình đã hoàn thiện.

## Ngành công nghiệp làm việc này ra sao

**Chuẩn đánh giá COCO.** Bộ dữ liệu Microsoft COCO (Lin và cộng sự, ECCV 2014) đi kèm một công cụ đánh giá chính thức, và công cụ đó định hình cách cả lĩnh vực báo cáo kết quả. Nó lấy trung bình AP trên mười ngưỡng IoU từ 0.5 đến 0.95 — đó chính là ý nghĩa của ký hiệu mAP@0.5:0.95 mà mọi paper đều trích dẫn. Nó cũng báo cáo riêng AP tại IoU 0.5 và tại 0.75, và tách AP theo kích thước đối tượng nhỏ, vừa, lớn, vì phát hiện vật nhỏ khó hơn hẳn và một con số gộp sẽ che mất điều đó.

Có một chi tiết trong công cụ này thường bị bỏ qua: **AP của từng lớp là kết quả gốc, còn mAP chỉ là trung bình cộng của chúng ở bước cuối cùng**. Nói cách khác, per-class AP không phải một phép tính phụ thêm mà là thứ có trước; con số tổng là thứ được dẫn xuất ra sau.

**LVIS.** Bộ dữ liệu này (Gupta, Dollár, Girshick, CVPR 2019) gồm hơn một nghìn lớp với phân bố đuôi dài tự nhiên, và được thiết kế chính để phơi bày vấn đề lớp hiếm. Paper nêu thẳng rằng các phương pháp học sâu hiện đại hoạt động kém ở vùng ít mẫu, và vì vậy LVIS báo cáo AP tách theo nhóm lớp hiếm, thường và phổ biến thay vì một con số tổng duy nhất. Đây là lập luận mạnh nhất cho việc phải báo cáo per-class AP khi dữ liệu lệch lớp — nó không phải sở thích cá nhân mà là chuẩn của một benchmark lớn.

**Chưng cất cho detection.** Hai công trình định hình hướng này. Chen, Choi, Yu, Han và Chandraker (NeurIPS 2017), *Learning Efficient Object Detection Models with Knowledge Distillation*, xử lý ba thách thức riêng của detection bằng ba cơ chế tương ứng: weighted cross-entropy cho mất cân bằng lớp, teacher-bounded regression loss cho phần toạ độ — chỉ phạt trò khi nó tệ hơn thầy, tức dùng thầy làm cận trên chứ không làm đích tuyệt đối — và lớp thích ứng cho việc khớp đặc trưng trung gian. Wang, Yuan, Zhang và Feng (CVPR 2019), *Distilling Object Detectors with Fine-grained Feature Imitation*, giải quyết vấn đề nền chiếm ưu thế bằng cách chỉ bắt chước đặc trưng tại những vùng gần đối tượng thay vì trên toàn bộ bản đồ đặc trưng.

**MLPerf Inference.** Việc đo tốc độ suy luận đã được chuẩn hoá bởi MLCommons. Benchmark này định nghĩa bốn kịch bản tải chuẩn, phản ánh các cách hệ thống thực nhận yêu cầu, và chia kết quả thành hai hạng mục: Closed bắt buộc mọi bên dùng cùng một model để so sánh phần cứng cho công bằng, Open cho phép đổi model nên đo được cả cải tiến thuật toán. Kết quả nộp lên được công khai kèm cấu hình chi tiết, nghĩa là người khác lặp lại được.

**MLPerf Tiny.** Đây là nhánh dành cho vi điều khiển và thiết bị siêu nhỏ, gồm các benchmark như phân loại ảnh, phát hiện người, nhận dạng từ khoá và phát hiện bất thường. Nó chạy ở chế độ single-stream, đo đồng thời độ trễ và chất lượng model — vì một mô hình nhanh mà sai thì vô nghĩa — và có tuỳ chọn đo cả năng lượng tiêu thụ, đại lượng quyết định với thiết bị chạy pin.

## Vài điều rút ra

**Báo cáo per-class khi dữ liệu lệch lớp.** Con số tổng trên dữ liệu đuôi dài chủ yếu phản ánh lớp đông nhất. Cả công cụ đánh giá COCO lẫn thiết kế của LVIS đều cho thấy AP theo lớp là thông tin gốc, nên hiển thị nó là việc trả lại thứ vốn đã có.

**Đặt ràng buộc triển khai vào giai đoạn thiết kế.** Việc bỏ attention, chọn tích chập tách theo chiều sâu và thêm đầu phát hiện phân giải cao đều là quyết định kiến trúc xuất phát từ đích đến là CPU của một thiết bị ngoài hiện trường. Ràng buộc này gắn vào đầu dự án rẻ hơn nhiều so với gắn vào cuối.

**Kiểm tra bước chuyển đổi định dạng như một mắt xích độc lập.** Đường từ framework huấn luyện tới runtime thiết bị đi qua vài lần chuyển đổi, mỗi lần đều có thể làm lệch kết quả vì toán tử không được hỗ trợ, vì khác biệt làm tròn, hoặc vì thứ tự kênh màu. Phép kiểm tra đúng là chạy cùng một đầu vào qua cả hai phiên bản và so đầu ra.

**Để hiện vật mô hình mang theo cấu hình sinh ra nó.** Một tệp trọng số không tự nói nó có bao nhiêu lớp, tên các lớp theo thứ tự nào, kích thước đầu vào bao nhiêu, chuẩn hoá ra sao. Đóng gói những thông tin đó cùng trọng số là điều kiện để sau này còn diễn giải được kết quả.

**Đo tốc độ theo cách người khác lặp lại được.** Nếu độ trễ là một yêu cầu, nó cần được đo với kịch bản tải rõ ràng và cấu hình được ghi lại, theo tinh thần của các benchmark công nghiệp — chứ không phải bằng cảm nhận rằng ứng dụng chạy mượt.
