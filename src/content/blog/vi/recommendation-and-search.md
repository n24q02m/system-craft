---
title: "Hệ gợi ý và tìm kiếm ngữ nghĩa cho ứng dụng nội dung"
description: "Bốn tầng của một hệ gợi ý đa phương thức: từ phân tích nội dung thô, sinh biểu diễn vector, tới tìm kiếm lai và xếp hạng nhiều nguồn."
lang: "vi"
order: 1
field: "REC"
topics: ["hệ gợi ý", "tìm kiếm ngữ nghĩa", "embedding", "lọc cộng tác", "ANN"]
---

Một ứng dụng nghe nhạc cần trả lời hai câu hỏi liên tục: người này nên nghe gì tiếp theo, và khi họ gõ vào ô tìm kiếm thì trả về cái gì. Nghe như hai tính năng, nhưng chúng dùng chung phần lớn hạ tầng bên dưới — và chính phần hạ tầng ấy là nội dung chủ yếu của bài này.

## Hệ thống đã dựng

<figure class="diagram">
<svg viewBox="0 0 640 250" role="img" aria-label="Bốn tầng của hệ gợi ý, phụ thuộc một chiều từ nội dung thô tới xếp hạng">
  <defs><marker id="rec-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">NGUỒN VÀO</text>
    <text class="lbl" x="176" y="14" font-size="9.5">TẦNG 1 VÀ 2</text>
    <text class="lbl" x="404" y="14" font-size="9.5">TẦNG 3 VÀ 4</text>
  </g>
  <rect class="box" x="0" y="28" width="150" height="40"/>
  <rect class="box" x="0" y="88" width="150" height="40"/>
  <rect class="box" x="0" y="148" width="150" height="40"/>
  <rect class="box" x="176" y="28" width="196" height="40"/>
  <rect class="box-accent" x="176" y="88" width="196" height="54"/>
  <rect class="box" x="176" y="162" width="196" height="40"/>
  <rect class="box" x="404" y="54" width="182" height="46"/>
  <rect class="box" x="404" y="134" width="182" height="46"/>
  <g class="flow" marker-end="url(#rec-a)">
    <path d="M150 48 H172"/><path d="M150 108 H172"/><path d="M150 168 H172"/>
    <path d="M274 68 V84"/><path d="M274 142 V158"/>
    <path d="M372 108 H390 V80 H400"/><path d="M372 122 H390 V156 H400"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="46">Tệp âm thanh</text>
    <text x="10" y="60" font-size="10" class="dim">nội dung thô</text>
    <text x="10" y="106">Siêu dữ liệu và lời</text>
    <text x="10" y="120" font-size="10" class="dim">tiêu đề, nghệ sĩ, lời bài hát</text>
    <text x="10" y="166">Tương tác</text>
    <text x="10" y="180" font-size="10" class="dim">phát, thích, bỏ qua</text>
    <text x="186" y="46">1. Phân tích nội dung</text>
    <text x="186" y="60" font-size="10" class="dim">sinh năm nhóm nhãn mô tả</text>
    <text x="186" y="106">2. Sinh biểu diễn</text>
    <text x="186" y="120" font-size="10" class="dim">bốn không gian vector</text>
    <text x="186" y="134" font-size="10" class="dim">bốn chỉ mục lân cận gần đúng</text>
    <text x="186" y="180">Lọc cộng tác và mô hình chuỗi</text>
    <text x="186" y="194" font-size="10" class="dim">huấn luyện ngoại tuyến</text>
    <text x="414" y="74">3. Tìm kiếm lai</text>
    <text x="414" y="88" font-size="10" class="dim">nhánh vector cộng nhánh từ khoá</text>
    <text x="414" y="154">4. Gợi ý nhiều nguồn</text>
    <text x="414" y="168" font-size="10" class="dim">nội dung, cộng tác, trình tự</text>
  </g>
</svg>
<figcaption>Bốn tầng phụ thuộc một chiều. Tầng sinh biểu diễn là nút thắt: hai tầng cuối chỉ đọc các chỉ mục do nó tạo ra.</figcaption>
</figure>

Kiến trúc gồm bốn module xếp thành chuỗi phụ thuộc một chiều, chạy như một dịch vụ riêng bên cạnh backend nghiệp vụ.

### Tầng một: phân tích nội dung

Đầu vào là tệp âm thanh thô. Đầu ra là các nhãn mô tả, chia thành năm nhóm: thể loại, tâm trạng, nhạc cụ, đặc điểm giọng hát, và ngôn ngữ.

Điểm đáng nói ở tầng này là **bộ nhãn không được bịa ra**. Mỗi nhóm neo vào một hệ phân loại có sẵn: tâm trạng theo mô hình vòng tròn cảm xúc của Russell, chia mặt phẳng thành bốn góc phần tư theo hai trục mức độ kích thích và sắc thái tích cực hay tiêu cực; nhạc cụ theo hệ Hornbostel–Sachs, phân theo cơ chế phát âm thành dây, hơi, màng rung, tự thân vang và điện tử; ngôn ngữ lấy tập con của một bộ nhận dạng ngôn ngữ có sẵn để khớp với mô hình dùng ở bước sau.

Việc neo vào hệ phân loại có sẵn nghe như chi tiết nhỏ, nhưng nó quyết định khả năng mở rộng: khi cần thêm nhãn, có một cấu trúc để đặt nhãn mới vào đúng chỗ, thay vì một danh sách phẳng mà ai cũng có thể thêm bừa.

Về mô hình, tầng này dùng hai mạng chạy song song. Một mạng phân loại đa nhãn dựa trên kiến trúc transformer cho phổ âm thanh, với bốn đầu ra riêng cho bốn nhóm nhãn đầu. Một mạng riêng chuyên cho nhận dạng ngôn ngữ, dựa trên kiến trúc thường dùng trong xử lý tiếng nói. Tách hai việc thay vì gộp vào một mạng nhiều đầu là có chủ ý: nhận dạng ngôn ngữ dựa vào đặc trưng ngữ âm, còn phân loại thể loại dựa vào đặc trưng hoà âm và nhịp điệu — ép chúng dùng chung phần thân dễ khiến hai tác vụ cản nhau.

### Tầng hai: sinh biểu diễn và lập chỉ mục

Đây là nút thắt của toàn hệ thống. Mỗi bài hát được biến thành bốn vector nằm trong bốn không gian khác nhau:

- **Vector âm thanh**, lấy từ trạng thái ẩn của mạng phân tích phổ, tính trung bình theo trục thời gian.
- **Vector thẻ mô tả**, sinh bằng một mô hình nhúng văn bản đa ngữ. Điểm thú vị ở đây: thay vì mã hoá các nhãn thành vector nhị phân, hệ thống **ghép chúng thành một câu tiếng Việt tự nhiên** — đại ý "Tiêu đề X. Nghệ sĩ Y. Thể loại A. Tâm trạng B. Nhạc cụ C" — rồi mới đưa vào mô hình nhúng. Nhờ vậy một truy vấn kiểu "bài buồn có tiếng guitar" khớp được với nội dung mà không cần từ điển ánh xạ thủ công giữa từ khoá và nhãn.
- **Vector lời bài hát**, cũng từ mô hình nhúng văn bản, chạy trên phần lời.
- **Vector hành vi**, lấy từ ma trận thừa số của mô hình lọc cộng tác.

Bốn vector này được lập chỉ mục riêng bằng một thư viện tìm kiếm lân cận gần đúng, dùng cấu trúc đồ thị phân tầng. Ý tưởng của cấu trúc này là xây đồ thị nhiều lớp, lớp trên thưa để nhảy xa, lớp dưới dày để tinh chỉnh — nhờ đó thời gian tìm kiếm tăng theo hàm lô-ga-rít thay vì tuyến tính với số lượng mục.

### Tầng ba: tìm kiếm lai

Một truy vấn đi song song qua hai nhánh. Nhánh vector đưa truy vấn vào cùng không gian với nội dung rồi tìm lân cận. Nhánh từ khoá khớp chuỗi trên tiêu đề, tên nghệ sĩ và các nhãn. Hai nhánh cho ra hai danh sách, và một bước hợp điểm gộp lại cùng hai yếu tố phụ là độ phổ biến và độ mới.

Hệ thống hỗ trợ cả truy vấn bằng văn bản lẫn truy vấn bằng một đoạn âm thanh — trường hợp sau đi thẳng vào chỉ mục vector âm thanh.

### Tầng bốn: gợi ý nhiều nguồn

Ba nguồn ứng viên chạy độc lập rồi hợp lại.

**Dựa trên nội dung.** Lấy trung bình vector của những bài người dùng đã thích để tạo hồ sơ sở thích, rồi tìm lân cận của hồ sơ đó. Với người dùng mới chưa thích bài nào, hồ sơ được dựng từ các bài phổ biến nhất — một cách xử lý khởi đầu nguội đơn giản và rẻ.

**Lọc cộng tác.** Dùng thuật toán bình phương tối thiểu luân phiên trên ma trận tương tác. Ý tưởng: phân rã ma trận người dùng nhân nội dung thành tích của hai ma trận thừa số nhỏ hơn, rồi luân phiên cố định một bên để giải bên còn lại — mỗi bước là một bài bình phương tối thiểu có nghiệm đóng, nên hội tụ nhanh và song song hoá được.

**Theo trình tự.** Một mạng transformer nhận chuỗi nội dung người dùng vừa tiêu thụ và dự đoán mục tiếp theo, có mặt nạ nhân quả để mỗi vị trí chỉ nhìn được về quá khứ.

Điểm chung của cả ba: chúng trả về ứng viên kèm điểm số, và một hàm hợp điểm tuyến tính gộp lại thành bảng xếp hạng cuối, cộng thêm độ phổ biến và độ mới.

### Tín hiệu ngầm: biến hành vi thành con số

Có một chi tiết thiết kế đáng mang đi nơi khác. Dữ liệu tương tác thô chỉ có các sự kiện rời rạc — phát, thích, bỏ thích. Trước khi đưa vào mô hình, mỗi sự kiện được quy về một trọng số thực theo vài quy tắc:

- Bỏ qua sớm, tức nghe chưa được bao nhiêu đã chuyển bài, mang **giá trị âm** — nó là tín hiệu không thích, chứ không phải trung tính.
- Nghe gần trọn được nhân thêm hệ số: tín hiệu tích cực mạnh hơn nghe nửa chừng.
- Tương tác tự tìm đến được đánh giá cao hơn tương tác đến từ gợi ý, vì nó phản ánh ý định chủ động.
- Tương tác gần đây có trọng số cao hơn tương tác cũ, giảm dần theo thời gian.

Bốn quy tắc này mã hoá được những thứ mà một bảng "đã thích hay chưa" không có. Đây là phần chuyển từ dữ liệu sự kiện sang tín hiệu học được, và nó thường quyết định chất lượng nhiều hơn việc chọn mô hình.

### Hạ tầng

Dịch vụ AI viết bằng Python với FastAPI, phơi ra bốn điểm cuối tương ứng bốn module. Backend nghiệp vụ viết bằng Java gọi sang. Dữ liệu nằm trên một cơ sở dữ liệu tài liệu, kèm một lớp bộ nhớ đệm cho kết quả gợi ý và tìm kiếm. Trọng số mô hình được tải sẵn vào ảnh máy ảo lúc dựng thay vì tải lúc chạy.

Một chi tiết vận hành đáng ghi: tác vụ nặng được tách ra chạy như tiến trình con riêng thay vì chạy trong tiến trình web. Lý do là mô hình chiếm nhiều bộ nhớ, và nếu chạy chung thì một yêu cầu nặng có thể làm chết worker đang phục vụ mọi người dùng khác.

## Kiến thức nền: vì sao bài toán này khó

### Không gian tìm kiếm quá lớn để chấm điểm trực tiếp

Với danh mục cỡ vài nghìn mục, có thể chấm điểm mọi mục cho mọi người dùng. Với vài triệu thì không. Đây là ràng buộc định hình toàn bộ kiến trúc của các hệ thống lớn, và là lý do tồn tại của tìm kiếm lân cận gần đúng: chấp nhận bỏ sót một phần nhỏ kết quả đúng để đổi lấy tốc độ tăng theo bậc.

### Ba họ phương pháp, ba điểm mạnh khác nhau

**Dựa trên nội dung** hoạt động ngay cả với mục hoàn toàn mới, vì nó chỉ cần đặc trưng của chính mục đó. Nhược điểm là nó có xu hướng gợi ý quanh quẩn những thứ giống cái đã biết, khó đưa người dùng tới sở thích mới.

**Lọc cộng tác** phát hiện được những liên hệ mà không đặc trưng nội dung nào giải thích nổi — hai bài hát chẳng liên quan gì về âm nhạc nhưng cùng được một nhóm người yêu thích. Đổi lại, nó cần lịch sử tương tác, nên thất bại với mục mới và người dùng mới.

**Theo trình tự** nắm bắt ý định trong phiên hiện tại, thứ mà hai họ trên bỏ qua: người vừa nghe ba bài ru con có ngữ cảnh khác hẳn người vừa nghe ba bài tập gym, dù hồ sơ dài hạn giống nhau.

Không họ nào thay thế được họ nào, và đó là lý do các hệ thống thực tế đều lai.

### Khởi đầu nguội là bài toán riêng

Một mục mới chưa ai nghe thì lọc cộng tác không có gì để nói về nó. Một người dùng mới cũng vậy. Các hướng xử lý phổ biến: dựa vào đặc trưng nội dung cho mục mới, dựa vào nhân khẩu học cho người dùng mới, hoặc chủ động đưa mục mới vào một phần nhỏ lưu lượng để thu thập tín hiệu ban đầu.

## Ngành công nghiệp làm việc này ra sao

Đối chiếu với các tài liệu thiết kế hệ thống quy mô lớn, có bốn điểm đáng học.

**Kiến trúc nhiều tầng lọc dần.** Chuẩn phổ biến là hai đến ba tầng. Tầng sinh ứng viên rẻ và thiên về độ phủ, thường chạy nhiều bộ sinh song song với tiêu chí khác nhau — độ liên quan, độ phổ biến, độ mới — rồi gộp lại, thu từ hàng triệu mục xuống vài trăm. Tầng chấm điểm đắt hơn và giàu đặc trưng hơn, thu tiếp xuống vài chục. Tầng sắp xếp lại áp các quy tắc nghiệp vụ: đa dạng nguồn, lọc nội dung đã xem, chèn yếu tố khám phá, cân bằng lợi ích các bên trong một thị trường hai chiều.

Việc chia tầng không chỉ để nhanh. Nó còn cho phép cải thiện từng phần độc lập, và cho phép đo xem tầng nào đang là nút thắt.

**Hai họ mô hình cho hai tầng.** Phân rã ma trận nhanh và rẻ nhưng không dùng được đặc trưng ngoài định danh. Mạng hai tháp — một tháp mã hoá người dùng, một tháp mã hoá nội dung, cùng chiếu vào một không gian — nhận được đặc trưng phong phú và xử lý người dùng mới tốt hơn, đổi lại tốn kém hơn. Cách ghép thường thấy là dùng mô hình nhẹ ở tầng sinh ứng viên và mô hình nặng ở tầng chấm điểm.

**Chỉ số ngoại tuyến phải nối được với hành vi thật.** Các chỉ số xếp hạng như nDCG tính đến vị trí: một kết quả đúng ở hạng nhất giá trị hơn cùng kết quả đó ở hạng mười. Bên cạnh đó là các chỉ số trực tuyến — tỷ lệ nhấp, thời gian xem, tỷ lệ hoàn thành. Điều quan trọng là chọn chỉ số ngoại tuyến nào dự báo tốt cho chỉ số trực tuyến mà tổ chức thực sự quan tâm.

Một biến thể đáng chú ý là entropy chéo chuẩn hoá: nó chia hiệu năng mô hình cho hiệu năng của baseline luôn dự đoán tỷ lệ trung bình. Giá trị lớn hơn một nghĩa là mô hình tệ hơn baseline — chỉ số này tự phơi bày thất bại thay vì để người đọc phải suy ra.

**Tìm kiếm xuyên phương thức cần không gian chung.** Muốn truy vấn bằng văn bản chạm tới nội dung âm thanh, hai bên phải nằm trong cùng một không gian vector, và điều đó chỉ có được khi mô hình được huấn luyện tương phản trên các cặp văn bản–âm thanh. Đặt cạnh nhau hai bộ mã hoá riêng biệt rồi cộng điểm không tạo ra khả năng đó — nó chỉ cho phép so văn bản với phần văn bản mô tả nội dung, đúng như cách hệ thống ở trên hoạt động.

## Vài điều rút ra

**Bước biến sự kiện thành tín hiệu quan trọng hơn vẻ ngoài của nó.** Công thức quy đổi tương tác thành trọng số — phân biệt bỏ qua với nghe trọn, tự tìm với được gợi ý, gần đây với đã lâu — là phần mang lại nhiều giá trị nhất trên mỗi dòng mã trong toàn hệ thống.

**Ghép nhiều nguồn điểm cần chuẩn hoá trước khi cộng.** Điểm từ ba nguồn thường có thang đo hoàn toàn khác nhau: một bên là tương đồng nằm trong khoảng đơn vị, một bên là tích vô hướng không chặn, một bên là xác suất trên hàng nghìn lớp nên luôn rất nhỏ. Cộng thẳng có trọng số sẽ khiến nguồn có thang nhỏ gần như không đóng góp gì, dù trọng số danh nghĩa không nhỏ. Chuẩn hoá về cùng thang, hoặc hợp nhất theo thứ hạng, là bước bắt buộc.

**Thước đo khoảng cách phải khớp với cách vector được tạo ra.** Chỉ mục lân cận mặc định thường dùng khoảng cách Euclid, trong khi phần lớn biểu diễn ngữ nghĩa được thiết kế để so bằng cosin. Nếu không chuẩn hoá độ dài vector trước khi lập chỉ mục, thứ hạng sẽ bị chi phối bởi độ dài chứ không chỉ bởi hướng.

**Sinh biểu diễn nên đi trước mọi thứ khác.** Trong chuỗi bốn tầng, ba tầng sau đều đọc chỉ mục do tầng hai tạo ra. Khi dựng lại một hệ thống tương tự, đây là thứ tự bắt buộc — và cũng là chỗ đáng đầu tư nhất, vì chất lượng biểu diễn đặt trần cho mọi thứ phía sau.
