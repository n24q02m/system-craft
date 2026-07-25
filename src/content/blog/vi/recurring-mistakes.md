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

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="Đường đi của một lỗi qua các tầng khi không có bất biến và khi có bất biến kiểm tra lúc khởi động">
  <defs><marker id="meta-a1" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="12" font-size="9.5">KHÔNG CÓ BẤT BIẾN</text>
  <rect class="box" x="0" y="22" width="100" height="50"/>
  <rect class="box" x="122" y="22" width="100" height="50"/>
  <rect class="box" x="244" y="22" width="100" height="50"/>
  <rect class="box-warn" x="366" y="22" width="274" height="50"/>
  <path class="flow" d="M101,47 L117,47" marker-end="url(#meta-a1)"/>
  <path class="flow" d="M223,47 L239,47" marker-end="url(#meta-a1)"/>
  <path class="flow" d="M345,47 L361,47" marker-end="url(#meta-a1)"/>
  <text class="lbl dim" x="0" y="106" font-size="9.5">CÓ BẤT BIẾN LÚC KHỞI ĐỘNG</text>
  <rect class="box" x="0" y="116" width="100" height="50"/>
  <rect class="box-ok" x="122" y="116" width="222" height="50"/>
  <rect class="box dim" x="366" y="116" width="274" height="50"/>
  <path class="flow" d="M101,141 L117,141" marker-end="url(#meta-a1)"/>
  <path class="flow dashed" d="M345,141 L363,141"/>
  <g font-size="11.5">
    <text x="12" y="42">dữ liệu</text>
    <text x="134" y="42">huấn luyện</text>
    <text x="256" y="42">phục vụ</text>
    <text x="378" y="42">chỉ lộ ra lúc phân tích kết quả</text>
    <text x="12" y="136">dữ liệu</text>
    <text x="134" y="136">bất biến chặn lỗi tại đây</text>
    <text class="dim" x="378" y="136">các tầng sau không chạy</text>
  </g>
  <g font-size="10" class="dim">
    <text x="12" y="58">lỗi phát sinh</text>
    <text x="134" y="58">im lặng</text>
    <text x="256" y="58">im lặng</text>
    <text x="12" y="152">lỗi phát sinh</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="378" y="58">hoặc không lộ ra lần nào</text>
    <text x="134" y="152">kiểm tra lúc khởi động</text>
    <text x="378" y="152">không có kết quả sai để đọc</text>
  </g>
  <text class="dim" x="0" y="188" font-size="10.5">Bất biến chạy lúc khởi động, không phải lúc phân tích kết quả.</text>
</svg>
<figcaption>Điều bất biến thay đổi là vị trí phát hiện trên trục thời gian: lỗi bị bắt ngay tại tầng sinh ra nó thay vì ở cuối đường ống.</figcaption>
</figure>

Đây không phải quan sát mới. Một công trình được trích dẫn rộng rãi về **nợ kỹ thuật trong hệ thống học máy** mô tả đúng hiện tượng này ở quy mô công nghiệp: các hệ học máy tích luỹ một loại nợ đặc thù mà công cụ kỹ thuật phần mềm truyền thống không nhìn thấy — ranh giới giữa các thành phần bị xói mòn, các thành phần vướng vào nhau đến mức đổi một đặc trưng kéo theo mọi thứ đổi, những nơi tiêu thụ dữ liệu không được khai báo, những vòng phản hồi ẩn. Cái giá của các khoản nợ này đến muộn, và đến dưới dạng chi phí bảo trì chứ không phải dưới dạng lỗi.

## Nguyên tắc hai: hỏi "thông tin này có tồn tại lúc dự đoán không"

Rò rỉ dữ liệu là khi thông tin lẽ ra không được biết tại thời điểm dự đoán lại lọt vào quá trình huấn luyện. Dạng cơ bản thì ai cũng biết: chia tập ngẫu nhiên trên dữ liệu có thứ tự thời gian. Các dạng khác tinh vi hơn nhiều.

**Thông tin toàn cục lọt vào bước tiền xử lý.** Chuẩn hoá bằng trung bình và độ lệch chuẩn tính trên toàn bộ dữ liệu, bao gồm cả phần dành để kiểm tra, là ví dụ kinh điển. Chọn đặc trưng dựa trên tương quan với nhãn tính trên toàn bộ dữ liệu cũng vậy.

**Thuộc tính của đối tượng lọt vào dấu thời gian của sự kiện.** Nếu thời điểm một người tương tác với một nội dung được suy ra từ thuộc tính của chính nội dung đó thay vì từ hành vi thật, thì mọi chuỗi hành vi bị ép về cùng một hình dạng, và mô hình có trục thời gian sẽ học hình dạng ấy thay vì học sở thích.

**Đơn vị lặp lại giữa các tập.** Nhiều mẫu sinh ra từ cùng một nguồn — nhiều khung hình từ một video, nhiều đoạn từ một bài báo, nhiều lần đo từ một trạm — nếu rơi vào cả tập huấn luyện lẫn tập kiểm tra thì mô hình đã thấy trước câu trả lời dưới dạng hơi khác.

<figure class="diagram">
<svg viewBox="0 0 640 286" role="img" aria-label="Ba dạng rò rỉ dữ liệu: thông tin toàn cục vào tiền xử lý, thuộc tính đối tượng vào dấu thời gian, và đơn vị lặp qua các tập chia">
  <defs><marker id="meta-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="12" font-size="9.5">THÔNG TIN TOÀN CỤC RÒ VÀO TIỀN XỬ LÝ</text>
  <rect class="box-warn" x="0" y="22" width="196" height="44"/>
  <rect class="box" x="8" y="30" width="88" height="28"/>
  <rect class="box" x="100" y="30" width="88" height="28"/>
  <path class="flow" d="M197,44 L214,44" marker-end="url(#meta-a2)"/>
  <rect class="box" x="216" y="30" width="84" height="28"/>
  <rect class="box" x="340" y="30" width="88" height="28"/>
  <path class="flow" d="M429,44 L446,44" marker-end="url(#meta-a2)"/>
  <rect class="box-ok" x="448" y="30" width="88" height="28"/>
  <path class="flow" d="M537,44 L554,44" marker-end="url(#meta-a2)"/>
  <rect class="box" x="556" y="30" width="84" height="28"/>
  <g font-size="10.5">
    <text x="16" y="48">huấn luyện</text>
    <text x="108" y="48">giữ lại</text>
    <text x="224" y="48">chuẩn hoá</text>
    <text x="348" y="48">huấn luyện</text>
    <text x="456" y="48">chuẩn hoá</text>
    <text x="564" y="48">giữ lại</text>
  </g>
  <g font-size="10" class="dim">
    <text x="0" y="82">trung bình và độ lệch chuẩn tính trên toàn bộ</text>
    <text x="340" y="82">chỉ tính trên phần huấn luyện, rồi áp sang</text>
  </g>
  <text class="lbl dim" x="0" y="106" font-size="9.5">THUỘC TÍNH ĐỐI TƯỢNG RÒ VÀO DẤU THỜI GIAN</text>
  <rect class="box" x="0" y="116" width="150" height="44"/>
  <path class="flow" d="M151,138 L168,138" marker-end="url(#meta-a2)"/>
  <rect class="box-warn" x="170" y="116" width="170" height="44"/>
  <path class="flow" d="M341,138 L358,138" marker-end="url(#meta-a2)"/>
  <g class="edge">
    <line x1="376" y1="124" x2="466" y2="124"/>
    <line x1="376" y1="138" x2="466" y2="138"/>
    <line x1="376" y1="152" x2="466" y2="152"/>
  </g>
  <g class="node">
    <circle cx="376" cy="124" r="3"/>
    <circle cx="406" cy="124" r="3"/>
    <circle cx="436" cy="124" r="3"/>
    <circle cx="466" cy="124" r="3"/>
    <circle cx="376" cy="138" r="3"/>
    <circle cx="406" cy="138" r="3"/>
    <circle cx="436" cy="138" r="3"/>
    <circle cx="466" cy="138" r="3"/>
    <circle cx="376" cy="152" r="3"/>
    <circle cx="406" cy="152" r="3"/>
    <circle cx="436" cy="152" r="3"/>
    <circle cx="466" cy="152" r="3"/>
  </g>
  <g font-size="10.5">
    <text x="12" y="134">thuộc tính</text>
    <text x="12" y="148">của đối tượng</text>
    <text x="182" y="134">dấu thời gian</text>
    <text x="182" y="148">của sự kiện</text>
  </g>
  <text class="dim" x="484" y="142" font-size="10">cùng một hình dạng</text>
  <text class="dim" x="0" y="176" font-size="10">dấu thời gian suy ra từ thuộc tính chứ không từ hành vi thật, nên mọi chuỗi mang cùng một hình dạng</text>
  <text class="lbl dim" x="0" y="200" font-size="9.5">ĐƠN VỊ LẶP QUA CÁC TẬP CHIA</text>
  <rect class="box-warn" x="0" y="210" width="300" height="48"/>
  <rect class="box-ok" x="340" y="210" width="300" height="48"/>
  <line class="edge dashed" x1="150" y1="216" x2="150" y2="252"/>
  <line class="edge dashed" x1="490" y1="216" x2="490" y2="252"/>
  <g class="node-accent">
    <circle cx="30" cy="228" r="4"/>
    <circle cx="60" cy="228" r="4"/>
    <circle cx="90" cy="228" r="4"/>
    <circle cx="120" cy="228" r="4"/>
    <circle cx="180" cy="228" r="4"/>
    <circle cx="210" cy="228" r="4"/>
    <circle cx="370" cy="228" r="4"/>
    <circle cx="400" cy="228" r="4"/>
    <circle cx="430" cy="228" r="4"/>
  </g>
  <g class="node-open">
    <circle cx="520" cy="228" r="4"/>
    <circle cx="550" cy="228" r="4"/>
    <circle cx="580" cy="228" r="4"/>
  </g>
  <g font-size="10" class="dim">
    <text x="30" y="248">huấn luyện</text>
    <text x="175" y="248">kiểm tra</text>
    <text x="370" y="248">huấn luyện</text>
    <text x="515" y="248">kiểm tra</text>
    <text x="0" y="274">nhiều mẫu của cùng một nguồn rơi vào cả hai tập</text>
    <text x="340" y="274">chia theo nguồn: mỗi nguồn chỉ nằm ở một tập</text>
  </g>
</svg>
<figcaption>Cả ba dạng đều trả lời sai cùng một câu hỏi: thông tin này có tồn tại tại thời điểm cần dự đoán không.</figcaption>
</figure>

Đây không phải vấn đề của riêng dự án nhỏ. Một khảo sát trên các công trình khoa học ứng dụng học máy đã tìm thấy lỗi rò rỉ ở hàng trăm bài báo trải khắp nhiều lĩnh vực, và phân loại chúng thành nhiều kiểu khác nhau. Trong một trường hợp được phân tích kỹ, sau khi sửa rò rỉ thì các mô hình học máy phức tạp không còn vượt trội so với một mô hình hồi quy tuyến tính cổ điển — toàn bộ kết luận đã phải xem lại. Nhóm tác giả đề xuất kèm theo mỗi công bố một bản mô tả mô hình ghi rõ cách chia dữ liệu và các bước tiền xử lý, để lỗi loại này lộ ra trước khi công bố.

Phép phòng thủ tốt nhất là một câu hỏi duy nhất, hỏi cho từng đặc trưng: *thông tin này có thực sự tồn tại tại thời điểm cần dự đoán không?* Nếu câu trả lời không rõ ràng ngay, đó là chỗ đáng đào.

## Nguyên tắc ba: đặt hệ quy chiếu trước khi đo

Một con số tự nó không nói lên điều gì. Nó chỉ có nghĩa khi đặt cạnh một mốc.

Điều này nghe hiển nhiên, nhưng bước dựng baseline lại hay bị bỏ qua nhất, vì nó không thú vị và có cảm giác như đang làm thứ chắc chắn sẽ bị thay thế.

Hậu quả rất cụ thể. Một chỉ số nghe có vẻ thấp có thể thực ra là tốt nếu bài toán khó — trong tìm kiếm trên danh mục hàng trăm nghìn mục, một chỉ số nhỏ vẫn có thể gấp hàng trăm lần mức ngẫu nhiên. Ngược lại, một chỉ số nghe có vẻ cao có thể tệ hơn cả việc đoán theo lớp đông nhất. Không có mốc, cả hai trường hợp đều bị đọc sai, và quyết định tiếp theo — đầu tư thêm hay dừng lại — được đưa ra trên nền tảng sai.

<figure class="diagram">
<svg viewBox="0 0 640 196" role="img" aria-label="Một giá trị đo duy nhất được đọc thành hai kết luận trái ngược tuỳ theo mốc so sánh đặt cạnh nó">
  <text class="lbl dim" x="0" y="12" font-size="9.5">MỘT GIÁ TRỊ ĐO, HAI MỐC SO SÁNH</text>
  <line class="axis" x1="30" y1="104" x2="620" y2="104"/>
  <line class="edge dashed" x1="120" y1="66" x2="120" y2="104"/>
  <line class="edge dashed" x1="520" y1="66" x2="520" y2="104"/>
  <line class="edge" x1="380" y1="66" x2="380" y2="104"/>
  <circle class="node-open" cx="120" cy="104" r="4"/>
  <circle class="node-open" cx="520" cy="104" r="4"/>
  <circle class="node-accent" cx="380" cy="104" r="5.5"/>
  <path class="flow" d="M120,120 L120,128 M120,124 L380,124 M380,120 L380,128"/>
  <path class="flow" d="M380,120 L380,128 M380,124 L520,124 M520,120 L520,128"/>
  <text x="380" y="50" font-size="11.5" text-anchor="middle">cùng một giá trị đo</text>
  <g font-size="10.5" class="dim" text-anchor="middle">
    <text x="120" y="44">mốc ngẫu nhiên</text>
    <text x="120" y="58">trên danh mục lớn</text>
    <text x="520" y="44">mốc đoán lớp</text>
    <text x="520" y="58">đông nhất</text>
  </g>
  <g font-size="10.5" text-anchor="middle">
    <text x="250" y="144">cao hơn mốc nhiều lần</text>
    <text x="450" y="144">thấp hơn mốc</text>
  </g>
  <g font-size="10.5" class="dim" text-anchor="middle">
    <text x="250" y="158">đọc thành: đáng đi tiếp</text>
    <text x="450" y="158">đọc thành: nên dừng lại</text>
  </g>
  <text class="dim" x="30" y="118" font-size="10">thấp</text>
  <text class="dim" x="620" y="118" font-size="10" text-anchor="end">cao</text>
  <text class="dim" x="0" y="182" font-size="10.5">Con số không đổi. Chỉ mốc đổi, mà kết luận lật ngược.</text>
</svg>
<figcaption>Bước dựng mốc là bước hay bị bỏ nhất, và cũng là bước quyết định con số được đọc theo hướng nào.</figcaption>
</figure>

Baseline hợp lý khác nhau theo lĩnh vực: gợi ý theo độ phổ biến cho hệ gợi ý; đoán lớp đông nhất cho phân loại; dự báo bằng giá trị gần nhất cho chuỗi thời gian. Điểm chung là tất cả đều mất vài phút để dựng.

Bộ hướng dẫn thực hành công nghiệp được biết đến rộng rãi nhất đặt điều này lên rất sớm trong danh sách quy tắc của nó: giữ mô hình đầu tiên thật đơn giản và tập trung làm đúng hạ tầng; kiểm thử hạ tầng tách rời khỏi phần học máy; chọn một chỉ số đơn giản, quan sát được và quy được trách nhiệm cho mục tiêu đầu tiên; phát hiện vấn đề trước khi xuất mô hình ra. Thứ tự này không ngẫu nhiên.

## Nguyên tắc bốn: chọn thước đo theo đặc tính dữ liệu

Mỗi lĩnh vực đều có ít nhất một chỉ số phổ biến nhưng gây hiểu lầm trong điều kiện thường gặp.

**Độ chính xác trên tập lệch lớp.** Khi một lớp chiếm đa số áp đảo, đoán luôn lớp đó đã cho độ chính xác cao. Đây là lý do các tiêu chuẩn về phát hiện tấn công trình bày tách riêng hai loại lỗi thay vì gộp, và là lý do các chỉ số trung bình theo lớp tồn tại bên cạnh chỉ số vi mô.

**Chỉ số gộp che lớp hiếm.** Trong phát hiện đối tượng, chỉ số trung bình trên mọi lớp có thể tăng trong khi lớp ít mẫu nhất đang tệ đi. Các bộ dữ liệu được thiết kế riêng để phơi bày điều này đều báo cáo tách theo nhóm tần suất lớp.

**Sai số phần trăm khi giá trị gần 0.** Với dữ liệu mà trạng thái bình thường là giá trị nhỏ, chia cho giá trị thật tạo ra những con số vô nghĩa. Các chỉ số chuẩn hoá theo baseline được đề xuất chính để giải quyết việc này.

**Chỉ số chỉ so được trong cùng điều kiện.** Độ bối rối của hai mô hình ngôn ngữ chỉ so được khi chúng dùng chung bộ từ vựng — điều kiện này được nêu rõ trong giáo trình chuẩn nhưng rất dễ bị bỏ qua khi thay đổi cách tách từ giữa các thí nghiệm.

<figure class="diagram">
<svg viewBox="0 0 640 222" role="img" aria-label="Bốn thước đo phổ biến, mỗi thước đo đi kèm điều kiện làm nó mất ý nghĩa">
  <text class="lbl dim" x="0" y="12" font-size="9.5">THƯỚC ĐO — ĐIỀU KIỆN LÀM NÓ VÔ NGHĨA</text>
  <rect class="box" x="0" y="22" width="308" height="76"/>
  <rect class="box" x="332" y="22" width="308" height="76"/>
  <rect class="box" x="0" y="114" width="308" height="76"/>
  <rect class="box" x="332" y="114" width="308" height="76"/>
  <rect class="box-warn" x="12" y="56" width="284" height="30"/>
  <rect class="box-warn" x="344" y="56" width="284" height="30"/>
  <rect class="box-warn" x="12" y="148" width="284" height="30"/>
  <rect class="box-warn" x="344" y="148" width="284" height="30"/>
  <g font-size="11.5">
    <text x="12" y="46">độ chính xác</text>
    <text x="344" y="46">chỉ số gộp trung bình</text>
    <text x="12" y="138">sai số phần trăm</text>
    <text x="344" y="138">độ bối rối</text>
  </g>
  <g font-size="10.5">
    <text x="22" y="75">hỏng khi một lớp áp đảo</text>
    <text x="354" y="75">hỏng khi có lớp hiếm bị che</text>
    <text x="22" y="167">hỏng khi giá trị thật gần 0</text>
    <text x="354" y="167">hỏng khi hai mô hình khác bộ từ vựng</text>
  </g>
  <text class="dim" x="0" y="212" font-size="10.5">Điều kiện áp dụng thường không được ghi cạnh con số.</text>
</svg>
<figcaption>Bốn thước đo này đều đúng trong điều kiện của chúng; vấn đề là điều kiện ấy không đi kèm con số khi con số được báo cáo.</figcaption>
</figure>

Mẫu hình chung: **chỉ số nào cũng có điều kiện áp dụng, và điều kiện ấy thường không được viết cạnh con số.** Khi hai chỉ số cùng đo một mô hình mà cho kết luận trái ngược, sự chênh lệch đó là thông tin cần điều tra, không phải thứ để chọn bên nghe thuận tai hơn.

## Nguyên tắc năm: hiện vật phải mang theo cấu hình sinh ra nó

Trong hầu hết mã nghiên cứu đều có những tham số điều khiển quy mô chạy: dùng bao nhiêu phần trăm dữ liệu, chạy bao nhiêu vòng, giới hạn thời gian bao lâu. Chúng tồn tại vì lý do chính đáng — khi đang gỡ lỗi đường ống, chạy trên một phần nhỏ tiết kiệm rất nhiều thời gian.

Rủi ro nằm ở chỗ các tham số này thường có giá trị mặc định dành cho chạy thử, và khi chuyển sang chạy thật thì dễ quên đặt lại. Hệ thống vẫn chạy, vẫn ra số, vẫn lưu được mô hình — không có tín hiệu nào cho thấy có vấn đề.

Nguy hiểm hơn nữa: khi các tham số này khác nhau giữa các lần thí nghiệm, mọi so sánh giữa chúng đều mất giá trị. Nếu một lần chạy dùng ít dữ liệu hơn lần trước, kết quả kém hơn không nói gì về kiến trúc. Điều tương tự xảy ra khi việc huấn luyện dừng vì hết ngân sách thời gian chứ không phải vì hội tụ — con số thu được là "tốt nhất trong một ngân sách", không phải kết quả của phương pháp.

Cách phòng thủ đơn giản đến mức gần như tầm thường, nhưng hiệu quả: in ra cấu hình thực tế ở đầu mỗi lần chạy, và **ghi nó vào cùng chỗ với mô hình đã lưu**. Một tệp trọng số không kèm cấu hình sinh ra nó — số lớp, kích thước đầu vào, cách chuẩn hoá, lượng dữ liệu, số vòng — là một tệp nhị phân không diễn giải được sau vài tháng.

<figure class="diagram">
<svg viewBox="0 0 640 232" role="img" aria-label="Tệp trọng số trần trụi so với tệp trọng số đóng gói kèm cấu hình sinh ra nó, và hệ quả khi tham số quy mô khác nhau giữa hai lần chạy">
  <text class="lbl dim" x="0" y="12" font-size="9.5">CHỈ CÓ TRỌNG SỐ</text>
  <text class="lbl dim" x="340" y="12" font-size="9.5">TRỌNG SỐ KÈM CẤU HÌNH</text>
  <rect class="box-warn" x="0" y="22" width="300" height="118"/>
  <rect class="box-ok" x="340" y="22" width="300" height="118"/>
  <g font-size="11.5">
    <text x="12" y="44">tệp trọng số</text>
    <text x="352" y="44">tệp trọng số kèm cấu hình</text>
  </g>
  <g font-size="10" class="dim">
    <text x="12" y="66">bao nhiêu lớp?</text>
    <text x="12" y="80">tên lớp theo thứ tự nào?</text>
    <text x="12" y="94">kích thước đầu vào?</text>
    <text x="12" y="108">chuẩn hoá thế nào?</text>
    <text x="12" y="122">dùng bao nhiêu dữ liệu, bao nhiêu vòng?</text>
    <text x="352" y="66">số lớp và tên lớp theo thứ tự</text>
    <text x="352" y="80">kích thước đầu vào</text>
    <text x="352" y="94">cách chuẩn hoá</text>
    <text x="352" y="108">lượng dữ liệu và số vòng</text>
    <text x="352" y="122">in ra lúc chạy, lưu cạnh mô hình</text>
  </g>
  <rect class="box-soft" x="0" y="164" width="640" height="56"/>
  <rect class="box" x="12" y="174" width="130" height="36"/>
  <rect class="box" x="172" y="174" width="130" height="36"/>
  <path class="flow" d="M151,186 L163,198 M163,186 L151,198"/>
  <g font-size="10.5">
    <text x="22" y="196">lần chạy A</text>
    <text x="182" y="196">lần chạy B</text>
  </g>
  <text x="318" y="190" font-size="11.5">tham số quy mô khác nhau</text>
  <text class="dim" x="318" y="206" font-size="10">mọi so sánh giữa hai lần đều vô hiệu</text>
</svg>
<figcaption>Cấu hình đi cùng hiện vật là điều kiện để hai lần chạy còn so sánh được với nhau.</figcaption>
</figure>

## Sợi chỉ xuyên suốt

Năm nguyên tắc trên nhìn thì rời rạc, nhưng chúng có chung một gốc: **trong học máy, khoảng cách giữa "chạy được" và "đúng" rộng hơn nhiều so với trong phần mềm thông thường, và không có cơ chế tự nhiên nào lấp khoảng cách ấy.**

Phần mềm thông thường có xu hướng tự phơi bày lỗi. Hệ học máy có xu hướng hấp thụ lỗi và tiếp tục sản xuất ra thứ trông giống kết quả. Vì vậy phần lớn công việc kỹ thuật thực sự không nằm ở chỗ chọn mô hình, mà ở chỗ dựng đủ điểm quan sát để biết mô hình đang thực sự làm gì.

Có một quan sát từ nghiên cứu thực địa đáng nhắc ở đây: khi phỏng vấn những người làm học máy trên các bài toán có rủi ro cao, phần lớn cho biết từng gặp chuỗi sự cố dồn tích bắt nguồn từ chất lượng dữ liệu. Kết luận của nghiên cứu ấy nằm ngay trong tiêu đề — ai cũng muốn làm phần mô hình, ít ai muốn làm phần dữ liệu.

Nếu chỉ giữ lại một thói quen từ tất cả những điều trên: trước khi huấn luyện bất cứ thứ gì, hãy dành một buổi chứng minh rằng tín hiệu cần học thực sự tồn tại trong dữ liệu — bằng thống kê đơn giản, bằng việc tự tay xem vài chục mẫu, bằng một baseline ngớ ngẩn. Buổi đó rẻ hơn rất nhiều so với những gì nó tránh được.
