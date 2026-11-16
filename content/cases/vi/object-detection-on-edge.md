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

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="Biểu đồ cột phân bố bốn lớp phương tiện, xe máy áp đảo và xe buýt thưa thớt">
  <text class="lbl dim" x="0" y="14" font-size="9.5">PHÂN BỐ SỐ LƯỢNG THEO LỚP</text>
  <path class="axis" d="M0 30 V170 H316"/>
  <rect class="bar-accent" x="14" y="46" width="56" height="124"/>
  <rect class="bar" x="92" y="114" width="56" height="56"/>
  <rect class="bar" x="170" y="151" width="56" height="19"/>
  <rect class="bar" x="248" y="162" width="56" height="8"/>
  <g font-size="10.5" text-anchor="middle">
    <text x="42" y="186">xe máy</text>
    <text x="120" y="186">ô tô</text>
    <text x="198" y="186">xe tải</text>
    <text x="276" y="186">xe buýt</text>
  </g>
  <rect class="box-soft" x="348" y="44" width="292" height="96"/>
  <text x="358" y="64" font-size="11.5">Chỉ số gộp bị lớp đông chi phối</text>
  <g font-size="10" class="dim">
    <text x="358" y="80">Trung bình cộng trên bốn lớp gần như</text>
    <text x="358" y="94">chỉ phản ánh lớp xe máy.</text>
    <text x="358" y="108">Muốn thấy lớp thưa nhất đang ở đâu thì</text>
    <text x="358" y="122">phải báo cáo theo từng lớp.</text>
  </g>
</svg>
<figcaption>Hình dạng đuôi dài này là lý do một con số tổng duy nhất không mô tả được kết quả.</figcaption>
</figure>

Có thêm một bước sinh ảnh nền không chứa đối tượng bằng kỹ thuật inpainting: lấy ảnh thật, xoá phương tiện đi và để thuật toán lấp lại phần bị xoá bằng nền hợp lý. Những ảnh này làm mẫu âm, dạy mô hình rằng một đoạn đường trống thì không có gì để báo.

### Augmentation hai tầng

Tăng cường dữ liệu được chia thành hai tầng, và ranh giới giữa chúng là một quyết định thiết kế có ý thức.

Tầng ngoại tuyến chạy trước khi huấn luyện, bằng một thư viện biến đổi ảnh chuyên dụng, và kết quả được lưu thành ảnh trên đĩa. Nhóm biến đổi gồm: lật ngang; dịch, xoay, co giãn; đổi màu sắc và độ sáng; làm mờ; thêm nhiễu. Nhóm quan trọng nhất là các phép mô phỏng thời tiết — mưa, sương mù, tuyết, bóng đổ, loá nắng. Nhóm này khớp trực tiếp với yêu cầu về điều kiện xấu, và cũng là nhóm tốn kém nhất về mặt tính toán.

Tầng trong lúc huấn luyện, tức phần augmentation tích hợp sẵn của framework, thì gần như tắt hết. Chỉ còn giữ mosaic — ghép bốn ảnh thành một để mô hình gặp nhiều ngữ cảnh và nhiều tỷ lệ trong một mẫu — cùng phép xoá ngẫu nhiên một vùng ảnh.

Sự phân chia này đến từ một đánh đổi cụ thể. Sinh biến thể trong lúc huấn luyện là mặc định của hầu hết framework vì mỗi epoch mô hình thấy một biến thể khác nhau, nên hiệu quả chống quá khớp cao hơn với cùng dung lượng lưu trữ. Nhưng các phép mô phỏng thời tiết đắt, và trả giá đó ở mỗi epoch là lãng phí; tính một lần rồi lưu lại thì rẻ hơn nhiều.

Rủi ro của việc bật cả hai tầng cùng lúc cũng cụ thể không kém: biến dạng cộng dồn. Một ảnh đã được nướng sẵn mưa và giảm sáng, nếu tiếp tục bị đổi màu và làm mờ lúc chạy, có thể trôi xa khỏi bất kỳ khung hình nào camera thật từng ghi được. Chọn một tầng làm chính và ghi lại lý do là cách tránh tình huống đó.

<figure class="diagram">
<svg viewBox="0 0 640 242" role="img" aria-label="Hai tầng augmentation, tầng ngoại tuyến chạy một lần và tầng trong lúc huấn luyện gần như tắt hết, kèm cảnh báo biến dạng cộng dồn">
  <text class="lbl dim" x="0" y="14" font-size="9.5">TẦNG NGOẠI TUYẾN</text>
  <text class="lbl dim" x="340" y="14" font-size="9.5">TẦNG TRONG LÚC HUẤN LUYỆN</text>
  <rect class="box" x="0" y="24" width="300" height="64"/>
  <rect class="box" x="340" y="24" width="300" height="64"/>
  <rect class="box-accent" x="0" y="96" width="300" height="52"/>
  <rect class="box-soft" x="340" y="96" width="300" height="52"/>
  <g font-size="11.5">
    <text x="10" y="44">Chạy một lần trước huấn luyện</text>
    <text x="350" y="44">Mỗi epoch một biến thể khác</text>
    <text x="10" y="116">Mô phỏng thời tiết</text>
    <text x="350" y="116">Chỉ còn hai phép</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="60">lật, dịch, xoay, đổi màu, làm mờ, thêm nhiễu</text>
    <text x="10" y="74">kết quả lưu thành ảnh trên đĩa</text>
    <text x="350" y="60">rẻ, chống quá khớp tốt hơn cùng dung lượng</text>
    <text x="350" y="74">nhưng ở đây gần như tắt hết</text>
    <text x="10" y="132">mưa, sương mù, tuyết, bóng đổ, loá nắng</text>
    <text x="350" y="132">mosaic và xoá một vùng ảnh ngẫu nhiên</text>
  </g>
  <text class="lbl dim" x="0" y="164" font-size="9.5">RỦI RO KHI BẬT CẢ HAI TẦNG</text>
  <rect class="box-warn" x="0" y="172" width="640" height="66"/>
  <text x="10" y="192" font-size="11.5">Bật cả hai tầng cùng lúc thì biến dạng cộng dồn</text>
  <g font-size="10" class="dim">
    <text x="10" y="208">Một ảnh đã nướng sẵn mưa và giảm sáng, nếu tiếp tục bị đổi màu và làm mờ lúc chạy, có thể trôi</text>
    <text x="10" y="222">xa khỏi bất kỳ khung hình nào camera thật từng ghi được.</text>
  </g>
</svg>
<figcaption>Ranh giới giữa hai tầng là một quyết định thiết kế, không phải mặc định của framework.</figcaption>
</figure>

### Kiến trúc student-teacher

Ràng buộc về kích thước mô hình được giải bằng chưng cất tri thức, với hai mô hình đóng hai vai.

**Thầy** là một mô hình phát hiện đối tượng cỡ lớn thuộc dòng YOLO, tinh chỉnh từ trọng số đã huấn luyện sẵn trên tập ảnh tổng quát. Vai trò của nó chỉ là nguồn tín hiệu giám sát; nó không bao giờ được triển khai.

**Trò** là một kiến trúc tự định nghĩa qua file cấu hình, với ba thay đổi so với thiết kế gốc:

- Toàn bộ tích chập chuẩn được thay bằng tích chập tách theo chiều sâu, hoặc biến thể Ghost. Đây là phần cắt giảm tham số chủ yếu.
- Thêm một đầu phát hiện ở mức phân giải cao hơn, thành bốn đầu thay vì ba. Phương tiện ở xa trong khung hình camera giao thông chiếm rất ít pixel, và một đầu ở phân giải cao hơn cho mô hình cơ hội bắt được chúng.
- Không dùng module attention nào. Đây là ràng buộc chủ động: các khối chú ý làm tăng độ trễ và thường được hỗ trợ kém trên runtime di động, nên chúng bị loại ngay từ khâu thiết kế.

<figure class="diagram">
<svg viewBox="0 0 640 248" role="img" aria-label="Bốn đầu phát hiện xếp theo phân giải, đầu thứ tư ở phân giải cao nhất là phần thêm vào so với thiết kế gốc ba đầu">
  <defs><marker id="det-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">BỐN ĐẦU PHÁT HIỆN, TỪ CAO XUỐNG THẤP</text>
  <rect class="box" x="0" y="24" width="36" height="36"/>
  <rect class="box" x="0" y="72" width="36" height="36"/>
  <rect class="box" x="0" y="120" width="36" height="36"/>
  <rect class="box" x="0" y="168" width="36" height="36"/>
  <path class="grid" d="M6 24 V60 M12 24 V60 M18 24 V60 M24 24 V60 M30 24 V60 M0 30 H36 M0 36 H36 M0 42 H36 M0 48 H36 M0 54 H36"/>
  <path class="grid" d="M9 72 V108 M18 72 V108 M27 72 V108 M0 81 H36 M0 90 H36 M0 99 H36"/>
  <path class="grid" d="M12 120 V156 M24 120 V156 M0 132 H36 M0 144 H36"/>
  <path class="grid" d="M18 168 V204 M0 186 H36"/>
  <g class="flow" marker-end="url(#det-a4)">
    <path d="M36 42 H72"/>
    <path d="M36 90 H72"/>
    <path d="M36 138 H72"/>
    <path d="M36 186 H72"/>
  </g>
  <rect class="box-accent" x="76" y="24" width="564" height="36"/>
  <rect class="box" x="76" y="72" width="564" height="36"/>
  <rect class="box" x="76" y="120" width="564" height="36"/>
  <rect class="box" x="76" y="168" width="564" height="36"/>
  <g font-size="11.5">
    <text x="86" y="47">Phân giải cao nhất, thêm vào</text>
    <text x="86" y="95">Phân giải cao</text>
    <text x="86" y="143">Phân giải trung bình</text>
    <text x="86" y="191">Phân giải thấp</text>
  </g>
  <g font-size="10" class="dim">
    <text x="290" y="47">đầu thứ tư, không có trong thiết kế gốc ba đầu</text>
    <text x="290" y="95">phương tiện ở xa, chiếm rất ít pixel</text>
    <text x="290" y="143">phương tiện ở khoảng giữa khung hình</text>
    <text x="290" y="191">phương tiện ở gần, chiếm nhiều pixel</text>
  </g>
  <text x="0" y="224" font-size="10.5" class="dim">Phân giải càng cao thì mỗi ô đặc trưng phủ càng ít pixel ảnh, nên vật nhỏ mới còn dấu vết để bắt.</text>
  <text x="0" y="240" font-size="10.5" class="dim">Ba đầu gốc phủ tốt vật vừa và lớn; phương tiện ở cuối khung hình rơi hết qua kẽ.</text>
</svg>
<figcaption>Cái giá của đầu thứ tư là thêm tính toán ở mức phân giải đắt nhất của mạng.</figcaption>
</figure>

Quá trình chưng cất giữ thầy ở trạng thái đóng băng. Hàm mất mát gồm hai phần: phần phát hiện thông thường tính trên nhãn thật, cộng phần chưng cất dựa trên phân kỳ KL giữa phân phối đầu ra của trò và của thầy. Phần thứ hai có hai tham số điều khiển — nhiệt độ, làm mềm phân phối để các lớp có xác suất thấp vẫn đóng góp tín hiệu; và hệ số pha trộn, quyết định trò nghe nhãn thật hay nghe thầy nhiều hơn.

### Suy luận và tiền xử lý

Hệ thống hỗ trợ hai chế độ suy luận. Chế độ thường đưa cả khung hình qua mô hình một lần. Chế độ theo lát cắt chia ảnh lớn thành các ô có chồng lấn, chạy mô hình trên từng ô rồi ghép kết quả lại — cách này tốn nhiều lần tính toán hơn nhưng làm vật nhỏ trở nên lớn tương đối so với đầu vào của mô hình, nên bắt được những phương tiện ở xa mà chế độ thường bỏ sót. Phần chồng lấn tồn tại để một phương tiện nằm vắt qua ranh giới hai ô không bị cắt đôi.

<figure class="diagram">
<svg viewBox="0 0 640 240" role="img" aria-label="Chế độ theo lát cắt chia khung hình thành các ô có phần chồng lấn, so với việc đưa cả khung hình vào cùng một kích thước đầu vào">
  <text class="lbl dim" x="0" y="14" font-size="9.5">CHẾ ĐỘ THEO LÁT CẮT</text>
  <text class="lbl dim" x="380" y="14" font-size="9.5">CÙNG MỘT ĐẦU VÀO MÔ HÌNH</text>
  <path class="grid" d="M360 6 V218"/>
  <rect class="area" x="100" y="24" width="30" height="140"/>
  <rect class="area" x="200" y="24" width="30" height="140"/>
  <rect class="area" x="0" y="80" width="330" height="28"/>
  <rect class="box" x="0" y="24" width="130" height="84"/>
  <rect class="box" x="100" y="24" width="130" height="84"/>
  <rect class="box" x="200" y="24" width="130" height="84"/>
  <rect class="box" x="0" y="80" width="130" height="84"/>
  <rect class="box" x="100" y="80" width="130" height="84"/>
  <rect class="box" x="200" y="80" width="130" height="84"/>
  <path class="edge dashed" d="M115 24 V164"/>
  <rect class="box-accent" x="102" y="118" width="26" height="14"/>
  <rect class="box" x="380" y="38" width="120" height="62"/>
  <rect class="box-accent" x="430" y="74" width="24" height="11"/>
  <rect class="box" x="380" y="124" width="120" height="62"/>
  <rect class="box-accent" x="436" y="160" width="9" height="6"/>
  <g font-size="10" class="dim">
    <text x="516" y="66">một ô lát cắt</text>
    <text x="516" y="152">cả khung hình</text>
    <text x="0" y="182">phần tô đậm là vùng chồng lấn giữa các ô</text>
    <text x="0" y="196">nét đứt là chỗ cắt nếu không có chồng lấn</text>
    <text x="0" y="210">phương tiện vắt qua ranh giới vẫn nguyên trong một ô</text>
    <text x="380" y="204">vật ở xa lớn hơn hẳn khi chỉ một ô đi vào</text>
  </g>
  <text x="0" y="232" font-size="10.5" class="dim">Đánh đổi: chế độ theo lát cắt tốn nhiều lần tính toán hơn cho mỗi khung hình.</text>
</svg>
<figcaption>Phần chồng lấn là lý do một phương tiện nằm vắt qua ranh giới hai ô không bị cắt đôi.</figcaption>
</figure>

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

<figure class="diagram">
<svg viewBox="0 0 640 258" role="img" aria-label="Giao trên hợp của hai hộp bao, và ba mức chồng lấn đặt trên thang IoU với hai vạch ngưỡng">
  <text class="lbl dim" x="0" y="14" font-size="9.5">GIAO TRÊN HỢP</text>
  <text class="lbl dim" x="330" y="14" font-size="9.5">MỘT NGƯỠNG LÀ KHÔNG ĐỦ</text>
  <path class="grid" d="M314 6 V218"/>
  <rect class="area" x="86" y="76" width="56" height="58"/>
  <rect class="box" x="24" y="48" width="118" height="86"/>
  <rect class="box" x="86" y="76" width="118" height="86"/>
  <path class="edge dashed" d="M19 43 H147 V71 H209 V167 H81 V139 H19 Z"/>
  <g font-size="10" class="dim">
    <text x="24" y="36">hộp thật</text>
    <text x="216" y="62">vùng hợp</text>
    <text x="216" y="76">viền nét đứt</text>
    <text x="86" y="180">hộp dự đoán</text>
  </g>
  <text x="114" y="109" font-size="10" text-anchor="middle">giao</text>
  <text x="0" y="200" font-size="10.5" class="dim">diện tích phần chung chia diện tích phần hợp</text>
  <text x="0" y="214" font-size="10.5" class="dim">bằng một là trùng khít, bằng không là rời nhau</text>
  <g font-size="10" class="dim">
    <text x="330" y="38">chồng ít</text>
    <text x="436" y="38">chồng vừa</text>
    <text x="542" y="38">chồng nhiều</text>
  </g>
  <rect class="area" x="368" y="50" width="14" height="34"/>
  <rect class="area" x="460" y="50" width="28" height="34"/>
  <rect class="area" x="552" y="50" width="42" height="34"/>
  <rect class="box" x="330" y="44" width="52" height="40"/>
  <rect class="box" x="368" y="50" width="52" height="40"/>
  <rect class="box" x="436" y="44" width="52" height="40"/>
  <rect class="box" x="460" y="50" width="52" height="40"/>
  <rect class="box" x="542" y="44" width="52" height="40"/>
  <rect class="box" x="552" y="50" width="52" height="40"/>
  <g class="edge">
    <path d="M375 96 V104 H435 V120"/>
    <path d="M474 96 V104 H510 V120"/>
    <path d="M573 96 V104 H570 V120"/>
  </g>
  <path class="axis" d="M330 124 H630 M330 124 V130 M480 124 V130 M555 124 V130 M630 124 V130"/>
  <path class="grid dashed" d="M480 106 V124 M555 106 V124"/>
  <circle class="node-open" cx="435" cy="124" r="3.2"/>
  <circle class="node" cx="510" cy="124" r="3.2"/>
  <circle class="node-accent" cx="570" cy="124" r="3.2"/>
  <g class="dim" text-anchor="middle">
    <text class="num" x="330" y="140">0</text>
    <text class="num" x="480" y="140">0.5</text>
    <text class="num" x="555" y="140">0.75</text>
    <text class="num" x="630" y="140">1</text>
  </g>
  <text x="330" y="160" font-size="10" class="dim">IoU của cặp hộp, từ rời nhau đến trùng khít</text>
  <text x="330" y="176" font-size="10" class="dim">Cặp giữa: đúng ở ngưỡng 0.5, sai ở ngưỡng 0.75.</text>
  <text x="0" y="234" font-size="10.5" class="dim">Chọn một ngưỡng duy nhất là ngầm quyết định thay cho mọi ứng dụng dùng kết quả này.</text>
  <text x="0" y="250" font-size="10.5" class="dim">Chuẩn hiện hành lấy trung bình trên mười ngưỡng từ 0.5 đến 0.95 để tránh đúng chuyện đó.</text>
</svg>
<figcaption>Vì thế một kết quả trích ở ngưỡng này và một kết quả trích ở ngưỡng khác không so trực tiếp được.</figcaption>
</figure>

### Chưng cất tri thức và trực giác về tri thức tối

Chưng cất tri thức là kỹ thuật huấn luyện một mô hình nhỏ sao cho nó khớp không chỉ với nhãn thật mà còn với phân phối đầu ra của một mô hình lớn hơn đã huấn luyện xong.

Trực giác nằm ở lượng thông tin trong hai loại tín hiệu. Nhãn cứng chỉ nói "đây là xe máy" — một bit thông tin về lớp đúng, không gì hơn. Phân phối đầu ra của thầy nói "đây là xe máy, có phần giống xe đạp, và gần như chắc chắn không phải xe buýt". Cấu trúc quan hệ giữa các lớp đó, đôi khi gọi là tri thức tối, là thứ nhãn cứng không mang theo, và là lý do trò học từ thầy nhanh hơn học từ nhãn thuần tuý.

<figure class="diagram">
<svg viewBox="0 0 640 222" role="img" aria-label="Hai biểu đồ cột, nhãn cứng dồn hết vào một lớp còn phân phối của thầy trải giá trị sang các lớp gần giống">
  <text class="lbl dim" x="0" y="14" font-size="9.5">NHÃN CỨNG</text>
  <text class="lbl dim" x="346" y="14" font-size="9.5">PHÂN PHỐI CỦA THẦY</text>
  <path class="grid" d="M320 6 V178"/>
  <path class="axis" d="M0 40 V152 H280"/>
  <path class="axis" d="M346 40 V152 H626"/>
  <rect class="bar-accent" x="16" y="48" width="46" height="104"/>
  <rect class="bar-accent" x="362" y="52" width="46" height="100"/>
  <rect class="bar" x="430" y="114" width="46" height="38"/>
  <rect class="bar" x="498" y="139" width="46" height="13"/>
  <rect class="bar" x="566" y="147" width="46" height="5"/>
  <g font-size="10" text-anchor="middle">
    <text x="39" y="168">xe máy</text>
    <text x="107" y="168">xe đạp</text>
    <text x="175" y="168">ô tô</text>
    <text x="243" y="168">xe buýt</text>
    <text x="385" y="168">xe máy</text>
    <text x="453" y="168">xe đạp</text>
    <text x="521" y="168">ô tô</text>
    <text x="589" y="168">xe buýt</text>
  </g>
  <text x="0" y="192" font-size="10.5" class="dim">Một lớp đúng, ba lớp còn lại bằng không.</text>
  <text x="346" y="192" font-size="10.5" class="dim">Lớp gần giống vẫn có giá trị đáng kể.</text>
  <text x="0" y="214" font-size="10.5" class="dim">Cấu trúc quan hệ giữa các lớp là thứ nhãn cứng không mang theo, và là thứ trò học được từ thầy.</text>
</svg>
<figcaption>Nhiệt độ trong hàm mất mát chưng cất chính là tham số điều khiển độ mềm của phân phối bên phải.</figcaption>
</figure>

### Vì sao chưng cất cho detection khác chưng cất cho phân loại

Kỹ thuật này ra đời cho bài phân loại ảnh và không chuyển thẳng sang phát hiện đối tượng được, vì ba khác biệt.

Thứ nhất, phần lớn diện tích một khung hình là nền. Nếu ép trò bắt chước thầy trên toàn bộ bản đồ đặc trưng, gần như toàn bộ tín hiệu học được sẽ nói về nền — thứ không ai quan tâm.

Thứ hai, phát hiện đối tượng có thành phần hồi quy toạ độ chứ không chỉ phân loại. Ép trò khớp hoàn toàn với thầy ở phần toạ độ có thể phản tác dụng khi chính thầy dự đoán lệch.

Thứ ba, mất cân bằng giữa nền và đối tượng nghiêm trọng hơn nhiều so với mất cân bằng lớp trong bài phân loại thông thường, nên hàm mất mát cần có cơ chế bù.

### Đánh đổi giữa độ chính xác và kích thước

Có hai đòn bẩy chính để thu nhỏ mô hình. Tích chập tách theo chiều sâu chia một phép tích chập chuẩn thành hai bước — một phép lọc theo từng kênh riêng, rồi một phép trộn kênh bằng tích chập 1x1 — giảm số phép nhân và số tham số xuống nhiều lần, đổi lại mỗi lớp biểu đạt kém hơn một chút. Lượng tử hoá biểu diễn trọng số bằng số nguyên độ rộng thấp thay vì số thực, giảm dung lượng và tăng tốc trên phần cứng hỗ trợ phép nguyên, đổi lại mất một phần độ phân giải số học.

<figure class="diagram">
<svg viewBox="0 0 640 240" role="img" aria-label="Tích chập chuẩn làm một phép duy nhất, còn tích chập tách chia thành lọc từng kênh rồi trộn kênh bằng tích chập một nhân một">
  <defs><marker id="det-a8" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">TÍCH CHẬP CHUẨN</text>
  <text class="lbl dim" x="340" y="14" font-size="9.5">TÍCH CHẬP TÁCH</text>
  <rect class="box" x="0" y="24" width="300" height="80"/>
  <rect class="box" x="340" y="24" width="300" height="32"/>
  <rect class="box" x="340" y="72" width="300" height="32"/>
  <path class="flow" marker-end="url(#det-a8)" d="M490 58 V70"/>
  <text x="10" y="44" font-size="11.5">Một phép duy nhất</text>
  <g font-size="10" class="dim">
    <text x="10" y="60">lọc không gian và trộn kênh cùng lúc</text>
    <text x="10" y="74">mỗi bộ lọc chạm vào mọi kênh đầu vào</text>
    <text x="10" y="88">không tách thành bước riêng</text>
  </g>
  <g font-size="11.5">
    <text x="350" y="44">Bước một: lọc từng kênh riêng</text>
    <text x="350" y="92">Bước hai: trộn kênh bằng tích chập 1x1</text>
  </g>
  <text class="lbl dim" x="0" y="126" font-size="9.5">SỐ PHÉP NHÂN, THEO DIỆN TÍCH KHỐI</text>
  <rect class="box-soft" x="0" y="132" width="280" height="48"/>
  <rect class="box-accent" x="340" y="132" width="14" height="48"/>
  <rect class="box-accent" x="372" y="132" width="52" height="48"/>
  <g font-size="10" class="dim">
    <text x="0" y="194">lọc và trộn cùng lúc</text>
    <text x="340" y="194">lọc</text>
    <text x="372" y="194">trộn kênh</text>
  </g>
  <text x="0" y="216" font-size="10.5" class="dim">Tách thành hai bước làm số phép nhân và số tham số giảm xuống nhiều lần.</text>
  <text x="0" y="232" font-size="10.5" class="dim">Đổi lại mỗi lớp biểu đạt kém hơn một chút, nên đây là đánh đổi có kiểm soát.</text>
</svg>
<figcaption>Đòn bẩy này phải nằm trong thiết kế ban đầu, vì nó đổi cả hình dạng của mạng chứ không riêng kích thước.</figcaption>
</figure>

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
