---
title: "Mô hình ngôn ngữ tiếng Việt: dự đoán từ tiếp theo"
description: "Ba đường tách từ cho tiếng Việt, năm kiến trúc dựng từ đầu, và điều kiện để hai con số độ bối rối so sánh được với nhau."
lang: "vi"
order: 3
field: "LM"
topics: ["mô hình ngôn ngữ", "tokenizer", "perplexity", "LoRA", "tiếng Việt"]
---

Dự đoán từ tiếp theo là bài toán nền của mọi mô hình ngôn ngữ: cho một chuỗi từ đã có, đoán từ kế tiếp. Nó đơn giản đến mức có thể phát biểu bằng một câu, nhưng lại chứa gần như toàn bộ những vấn đề thú vị của xử lý ngôn ngữ — và với tiếng Việt thì có thêm một vấn đề riêng ngay từ bước đầu tiên.

## Tiếng Việt và câu hỏi "một từ là gì"

Trong tiếng Anh, khoảng trắng gần như trùng với ranh giới từ. Trong tiếng Việt thì không. "Học sinh" là một từ mang nghĩa riêng, nhưng được viết thành hai âm tiết cách nhau bằng khoảng trắng. Tách theo khoảng trắng sẽ cho ra hai đơn vị mà khi đứng riêng mang nghĩa khác hẳn.

<figure class="diagram">
<svg viewBox="0 0 640 160" role="img" aria-label="Tách theo khoảng trắng chẻ từ ghép tiếng Việt thành hai đơn vị mang nghĩa khác hẳn, còn với tiếng Anh thì không">
  <defs><marker id="lm-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">TIẾNG VIỆT</text>
    <text class="lbl" x="210" y="14" font-size="9.5">TÁCH THEO KHOẢNG TRẮNG</text>
    <text class="lbl" x="0" y="104" font-size="9.5">TIẾNG ANH</text>
  </g>
  <rect class="box-accent" x="0" y="24" width="170" height="48"/>
  <rect class="box" x="210" y="24" width="200" height="48"/>
  <rect class="box" x="430" y="24" width="210" height="48"/>
  <rect class="box-soft" x="0" y="112" width="170" height="36"/>
  <rect class="box-soft" x="210" y="112" width="200" height="36"/>
  <g class="flow" marker-end="url(#lm-a)">
    <path d="M170 48 H204"/>
    <path d="M170 130 H204"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="44">học sinh</text>
    <text x="220" y="44">học</text>
    <text x="440" y="44">sinh</text>
    <text x="10" y="132">pupil</text>
    <text x="220" y="132">pupil</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="58">nghĩa: người đi học</text>
    <text x="220" y="58">nghĩa: việc học</text>
    <text x="440" y="58">nghĩa: sinh ra</text>
  </g>
  <text x="430" y="134" font-size="10.5" class="dim">vẫn một đơn vị, nghĩa giữ nguyên</text>
</svg>
<figcaption>Cùng một phép tách, hai ngôn ngữ cho hai kết quả khác nhau về nghĩa — nên bước tách từ là quyết định kiến trúc chứ không phải thao tác tiền xử lý.</figcaption>
</figure>

Đây không phải chi tiết ngôn ngữ học thuần tuý. Nó quyết định đầu vào của mô hình, kích thước không gian đầu ra, và cả độ khó của bài toán — nên nó là quyết định kiến trúc đầu tiên phải đưa ra.

## Hệ thống đã dựng

<figure class="diagram">
<svg viewBox="0 0 640 226" role="img" aria-label="Ba cách tách từ tiếng Việt cho ra ba chuỗi đầu vào khác nhau">
  <g class="dim"><text class="lbl" x="0" y="14" font-size="9.5">CÙNG MỘT CÂU NGUỒN</text></g>
  <rect class="box" x="0" y="24" width="640" height="32"/>
  <text x="12" y="45" font-size="12.5">học sinh trường này rất giỏi</text>
  <g class="flow"><path d="M104 56 V80"/><path d="M320 56 V80"/><path d="M536 56 V80"/></g>
  <g class="dim"><text class="lbl" x="0" y="96" font-size="9.5">BA CÁCH TÁCH</text></g>
  <rect class="box" x="0" y="104" width="200" height="94"/>
  <rect class="box" x="220" y="104" width="200" height="94"/>
  <rect class="box-accent" x="440" y="104" width="200" height="94"/>
  <g font-size="11.5">
    <text x="12" y="126">Theo khoảng trắng</text>
    <text x="232" y="126">Tách từ tiếng Việt</text>
    <text x="452" y="126">Đơn vị con của từ</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="12" y="148">học | sinh | trường | …</text>
    <text x="12" y="167">từ vựng: lọc theo tần suất</text>
    <text x="12" y="186">nhiều đơn vị, mỗi đơn vị dễ đoán</text>
    <text x="232" y="148">học_sinh | trường | …</text>
    <text x="232" y="167">từ vựng: lớn hơn nhiều</text>
    <text x="232" y="186">ít đơn vị, mỗi đơn vị khó đoán</text>
    <text x="452" y="148">học | sinh | trườ | ng | …</text>
    <text x="452" y="167">từ vựng: cố định, biết trước</text>
    <text x="452" y="186">xử lý được từ chưa gặp</text>
  </g>
  <text x="0" y="219" font-size="10.5" class="dim">Vì độ bối rối chuẩn hoá theo số đơn vị, ba nhánh này không so trực tiếp với nhau được.</text>
</svg>
<figcaption>Ba cách tách cùng một câu cho ra số đơn vị khác nhau, nên mẫu số khi chuẩn hoá cũng khác nhau.</figcaption>
</figure>

### Ba đường tách từ, ba pipeline dữ liệu

Ngữ liệu là một tập lớn bài báo tiếng Việt, mỗi bài ghép tiêu đề, tóm tắt và nội dung thành một văn bản. Trên cùng ngữ liệu đó, ba pipeline khác nhau được dựng.

**Đường thứ nhất — tách theo khoảng trắng.** Đơn giản nhất, không phụ thuộc công cụ ngoài. Từ vựng được xây bằng cách đếm tần suất rồi **bỏ những từ xuất hiện dưới một ngưỡng**, gom chúng vào một ký hiệu chung cho "từ chưa biết". Chuỗi huấn luyện sinh bằng cửa sổ trượt trên toàn bộ token của bài báo, nên một bài dài sinh ra rất nhiều mẫu.

**Đường thứ hai — tách từ bằng công cụ chuyên cho tiếng Việt.** Dùng bộ tách từ có sẵn để lấy đơn vị là từ thật theo nghĩa ngôn ngữ học. Kích thước từ vựng tăng lên đáng kể so với đường thứ nhất, vì số tổ hợp âm tiết tạo thành từ lớn hơn nhiều so với số âm tiết đơn lẻ.

**Đường thứ ba — tách theo đơn vị con của từ.** Dùng bộ tách của một mô hình ngôn ngữ tiếng Việt đã huấn luyện sẵn, theo kiểu mã hoá cặp byte. Kích thước từ vựng cố định và biết trước; từ chưa gặp được xử lý bằng cách ghép các mảnh nhỏ hơn thay vì gom hết vào một ký hiệu chung.

Ba đường này không phải ba biến thể cấu hình của cùng một thứ. Chúng tạo ra ba chuỗi đầu vào khác nhau, ba kích thước không gian đầu ra khác nhau, và ba mức độ khó khác nhau cho cùng một tác vụ.

### Năm kiến trúc dựng từ đầu

Trên mỗi pipeline, năm kiến trúc được cài và huấn luyện với cùng bộ siêu tham số:

- **RNN** — mạng hồi tiếp cơ bản, không có cổng.
- **GRU** — thêm cổng cập nhật và cổng đặt lại để kiểm soát dòng thông tin.
- **LSTM** — thêm ô nhớ cùng ba cổng vào, quên và ra.
- **LSTM kèm chú ý** — thêm một khối chú ý đa đầu chạy trên toàn bộ chuỗi đầu ra của LSTM trước khi lấy trạng thái cuối.
- **Transformer** — mã hoá vị trí bằng hàm sin và cosin, các khối gồm tự chú ý có mặt nạ nhân quả, mạng truyền thẳng, chuẩn hoá lớp và kết nối tắt.

<figure class="diagram">
<svg viewBox="0 0 640 222" role="img" aria-label="Ma trận mặt nạ nhân quả: mỗi hàng chỉ mở các cột ở quá khứ và chính nó, phần còn lại bị che">
  <g class="dim"><text class="lbl" x="0" y="14" font-size="9.5">MẶT NẠ NHÂN QUẢ</text></g>
  <text x="36" y="32" font-size="10" class="dim">vị trí được nhìn tới</text>
  <text transform="rotate(-90 10 132)" x="10" y="132" font-size="10" class="dim" text-anchor="middle">vị trí đang tính</text>
  <g class="cell-on">
    <rect x="36" y="56" width="20" height="20"/>
    <rect x="36" y="78" width="20" height="20"/><rect x="58" y="78" width="20" height="20"/>
    <rect x="36" y="100" width="20" height="20"/><rect x="58" y="100" width="20" height="20"/><rect x="80" y="100" width="20" height="20"/>
    <rect x="36" y="122" width="20" height="20"/><rect x="58" y="122" width="20" height="20"/><rect x="80" y="122" width="20" height="20"/><rect x="102" y="122" width="20" height="20"/>
    <rect x="36" y="144" width="20" height="20"/><rect x="58" y="144" width="20" height="20"/><rect x="80" y="144" width="20" height="20"/><rect x="102" y="144" width="20" height="20"/><rect x="124" y="144" width="20" height="20"/>
    <rect x="36" y="166" width="20" height="20"/><rect x="58" y="166" width="20" height="20"/><rect x="80" y="166" width="20" height="20"/><rect x="102" y="166" width="20" height="20"/><rect x="124" y="166" width="20" height="20"/><rect x="146" y="166" width="20" height="20"/>
    <rect x="36" y="188" width="20" height="20"/><rect x="58" y="188" width="20" height="20"/><rect x="80" y="188" width="20" height="20"/><rect x="102" y="188" width="20" height="20"/><rect x="124" y="188" width="20" height="20"/><rect x="146" y="188" width="20" height="20"/><rect x="168" y="188" width="20" height="20"/>
  </g>
  <g class="cell-off">
    <rect x="58" y="56" width="20" height="20"/><rect x="80" y="56" width="20" height="20"/><rect x="102" y="56" width="20" height="20"/><rect x="124" y="56" width="20" height="20"/><rect x="146" y="56" width="20" height="20"/><rect x="168" y="56" width="20" height="20"/>
    <rect x="80" y="78" width="20" height="20"/><rect x="102" y="78" width="20" height="20"/><rect x="124" y="78" width="20" height="20"/><rect x="146" y="78" width="20" height="20"/><rect x="168" y="78" width="20" height="20"/>
    <rect x="102" y="100" width="20" height="20"/><rect x="124" y="100" width="20" height="20"/><rect x="146" y="100" width="20" height="20"/><rect x="168" y="100" width="20" height="20"/>
    <rect x="124" y="122" width="20" height="20"/><rect x="146" y="122" width="20" height="20"/><rect x="168" y="122" width="20" height="20"/>
    <rect x="146" y="144" width="20" height="20"/><rect x="168" y="144" width="20" height="20"/>
    <rect x="168" y="166" width="20" height="20"/>
  </g>
  <g text-anchor="middle">
    <text class="num" x="46" y="48">1</text><text class="num" x="68" y="48">2</text><text class="num" x="90" y="48">3</text><text class="num" x="112" y="48">4</text><text class="num" x="134" y="48">5</text><text class="num" x="156" y="48">6</text><text class="num" x="178" y="48">7</text>
  </g>
  <g text-anchor="end">
    <text class="num" x="28" y="69">1</text><text class="num" x="28" y="91">2</text><text class="num" x="28" y="113">3</text><text class="num" x="28" y="135">4</text><text class="num" x="28" y="157">5</text><text class="num" x="28" y="179">6</text><text class="num" x="28" y="201">7</text>
  </g>
  <rect class="cell-on" x="220" y="56" width="16" height="16"/>
  <rect class="cell-off" x="220" y="82" width="16" height="16"/>
  <g font-size="10.5">
    <text x="244" y="68">được phép nhìn</text>
    <text x="244" y="94">bị che</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="220" y="128">Mỗi vị trí chỉ nhìn được về quá khứ</text>
    <text x="220" y="144">và chính nó: tam giác dưới của ma trận,</text>
    <text x="220" y="160">kể cả đường chéo. Nhờ vậy mà dự đoán</text>
    <text x="220" y="176">ở mọi vị trí đều là dự đoán hợp lệ.</text>
  </g>
</svg>
<figcaption>Mặt nạ là thứ cho phép huấn luyện song song trên cả chuỗi mà không vị trí nào đọc trộm đáp án của chính nó.</figcaption>
</figure>

Cấu hình chung: lớp nhúng, hai tầng, dropout, độ dài chuỗi tối đa cố định. Tối ưu bằng Adam kèm bộ lập lịch giảm tốc độ học khi không cải thiện, cắt chuẩn gradient, dừng sớm, và huấn luyện độ chính xác hỗn hợp.

Một điểm về cách đặt bài toán đáng chú ý: các mạng này lấy **trạng thái ẩn tại vị trí cuối cùng** của chuỗi rồi chiếu sang không gian từ vựng — tức bài toán được đặt thành phân loại một từ, không phải sinh chuỗi. Mỗi mẫu huấn luyện vì thế cho đúng một tín hiệu học.

### Tinh chỉnh mô hình đã huấn luyện sẵn

Song song, một hướng khác: lấy các mô hình ngôn ngữ đa ngữ đã huấn luyện sẵn ở quy mô vài trăm triệu tham số và tinh chỉnh chúng cho cùng tác vụ.

Kỹ thuật dùng là **LoRA** — thích ứng hạng thấp. Thay vì cập nhật toàn bộ ma trận trọng số, LoRA giữ nguyên trọng số gốc và học thêm một cặp ma trận hạng thấp cộng vào. Số tham số cần cập nhật giảm xuống rất nhiều, nên tinh chỉnh được trên phần cứng khiêm tốn. Các ma trận đích chọn theo từng kiến trúc: với họ này là các phép chiếu truy vấn, khoá, giá trị và đầu ra; với họ kia là khối trọng số gộp ba phép chiếu cùng các lớp truyền thẳng.

<figure class="diagram">
<svg viewBox="0 0 640 178" role="img" aria-label="Ma trận trọng số gốc bị đóng băng, chỉ hai ma trận hẹp cộng thêm vào là được huấn luyện">
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">TRỌNG SỐ GỐC</text>
    <text class="lbl" x="152" y="14" font-size="9.5">HAI MA TRẬN HẸP</text>
  </g>
  <rect class="box-soft" x="0" y="26" width="120" height="120"/>
  <rect class="box-accent" x="152" y="26" width="16" height="120"/>
  <rect class="box-accent" x="196" y="78" width="120" height="16"/>
  <g font-size="13" text-anchor="middle">
    <text x="136" y="90">+</text>
    <text x="182" y="90">×</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="46">ma trận trọng số</text>
    <text x="10" y="60">đã huấn luyện sẵn</text>
    <text x="0" y="164">đóng băng, không cập nhật</text>
    <text x="152" y="164">chỉ hai khối này được huấn luyện</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="340" y="54">Số ô phải cập nhật là hai dải hẹp,</text>
    <text x="340" y="70">không phải cả tấm vuông. Đó là lý do</text>
    <text x="340" y="86">tinh chỉnh chạy được trên phần cứng</text>
    <text x="340" y="102">khiêm tốn.</text>
  </g>
</svg>
<figcaption>Tích của hai dải hẹp có đúng hình dạng của tấm vuông, nên nó cộng thẳng vào trọng số gốc mà không cần đụng tới một ô nào của tấm ấy.</figcaption>
</figure>

Điểm khác biệt quan trọng về cách đặt bài toán: nhánh này huấn luyện theo kiểu **mô hình ngôn ngữ nhân quả chuẩn** — dự đoán ở mọi vị trí trong chuỗi, với phần đệm bị che khỏi hàm mất mát. Mỗi mẫu cho hàng trăm tín hiệu học thay vì một.

<figure class="diagram">
<svg viewBox="0 0 640 236" role="img" aria-label="Cùng một chuỗi token, cách đặt bài toán thứ nhất chỉ sinh tín hiệu học ở vị trí cuối, cách thứ hai sinh tín hiệu ở mọi vị trí">
  <defs><marker id="lm-b" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim"><text class="lbl" x="0" y="16" font-size="9.5">MỘT MẪU CHO MỘT TÍN HIỆU HỌC</text></g>
  <circle class="node" cx="337" cy="34" r="3.5"/>
  <g class="flow" marker-end="url(#lm-b)"><path d="M337 58 V44"/></g>
  <g class="cell">
    <rect x="0" y="58" width="54" height="28"/><rect x="62" y="58" width="54" height="28"/><rect x="124" y="58" width="54" height="28"/><rect x="186" y="58" width="54" height="28"/><rect x="248" y="58" width="54" height="28"/><rect x="310" y="58" width="54" height="28"/>
  </g>
  <g class="cell-off">
    <rect x="372" y="58" width="54" height="28"/><rect x="434" y="58" width="54" height="28"/>
  </g>
  <rect class="box-soft" x="508" y="58" width="132" height="28"/>
  <g font-size="10.5" text-anchor="middle">
    <text x="27" y="76">học</text><text x="89" y="76">sinh</text><text x="151" y="76">trường</text><text x="213" y="76">này</text><text x="275" y="76">rất</text><text x="337" y="76">giỏi</text>
    <text x="399" y="76" class="dim">đệm</text><text x="461" y="76" class="dim">đệm</text>
  </g>
  <text x="518" y="76" font-size="10.5">một tín hiệu học</text>
  <text x="0" y="104" font-size="10.5" class="dim">chỉ vị trí cuối sinh ra tín hiệu học</text>
  <g class="dim"><text class="lbl" x="0" y="136" font-size="9.5">MỘT MẪU CHO HÀNG TRĂM TÍN HIỆU</text></g>
  <g class="node">
    <circle cx="27" cy="154" r="3.5"/><circle cx="89" cy="154" r="3.5"/><circle cx="151" cy="154" r="3.5"/><circle cx="213" cy="154" r="3.5"/><circle cx="275" cy="154" r="3.5"/><circle cx="337" cy="154" r="3.5"/>
  </g>
  <g class="flow" marker-end="url(#lm-b)">
    <path d="M27 178 V164"/><path d="M89 178 V164"/><path d="M151 178 V164"/><path d="M213 178 V164"/><path d="M275 178 V164"/><path d="M337 178 V164"/>
  </g>
  <g class="cell">
    <rect x="0" y="178" width="54" height="28"/><rect x="62" y="178" width="54" height="28"/><rect x="124" y="178" width="54" height="28"/><rect x="186" y="178" width="54" height="28"/><rect x="248" y="178" width="54" height="28"/><rect x="310" y="178" width="54" height="28"/>
  </g>
  <g class="cell-off">
    <rect x="372" y="178" width="54" height="28"/><rect x="434" y="178" width="54" height="28"/>
  </g>
  <rect class="box-accent" x="508" y="178" width="132" height="28"/>
  <g font-size="10.5" text-anchor="middle">
    <text x="27" y="196">học</text><text x="89" y="196">sinh</text><text x="151" y="196">trường</text><text x="213" y="196">này</text><text x="275" y="196">rất</text><text x="337" y="196">giỏi</text>
    <text x="399" y="196" class="dim">đệm</text><text x="461" y="196" class="dim">đệm</text>
  </g>
  <text x="518" y="196" font-size="10.5">hàng trăm tín hiệu</text>
  <text x="0" y="224" font-size="10.5" class="dim">phần đệm bị che khỏi hàm mất mát</text>
</svg>
<figcaption>Hai băng dùng đúng một chuỗi đầu vào; thứ duy nhất thay đổi là số vị trí được tính vào hàm mất mát, và đó chính là hiệu suất sử dụng dữ liệu.</figcaption>
</figure>

## Kiến thức nền

### Độ bối rối và điều kiện để so sánh nó

Chỉ số phổ biến nhất cho mô hình ngôn ngữ là **perplexity** — độ bối rối. Trực giác: nó đo mức độ "ngạc nhiên" trung bình của mô hình khi gặp văn bản kiểm tra, và có thể hiểu như số lựa chọn hiệu dụng mà mô hình còn phân vân giữa chúng ở mỗi bước. Độ bối rối bằng một trăm nghĩa là mô hình lúng túng như thể đang chọn đều giữa một trăm khả năng.

Về mặt hình thức, nó là nghịch đảo xác suất mà mô hình gán cho tập kiểm tra, **chuẩn hoá theo số đơn vị** trong chuỗi.

Chính chỗ chuẩn hoá ấy dẫn tới một điều kiện then chốt, được nêu thẳng trong giáo trình chuẩn của lĩnh vực:

> Note that in computing perplexities, the language model must be constructed without any knowledge
> of the test set, or else the perplexity will be artificially low. **And the perplexity of two
> language models is only comparable if they use identical vocabularies.**

Lý do rất trực tiếp: nếu một mô hình chia câu thành hai mươi đơn vị còn mô hình khác chia cùng câu ấy thành ba mươi lăm đơn vị, mẫu số đã khác nhau. Và độ khó của mỗi lần dự đoán cũng khác — đoán một mảnh âm tiết dễ hơn hẳn đoán một từ trọn nghĩa.

Hệ quả thực hành: **một chuỗi thí nghiệm trong đó mỗi vòng đổi cách tách từ thì không phải là một chuỗi cải tiến so sánh được với nhau.** Muốn biết cách tách nào tốt hơn, phải cố định mọi thứ còn lại và đo bằng một chỉ số không phụ thuộc đơn vị chia — chẳng hạn độ chính xác trên một tác vụ hạ nguồn cụ thể.

### Kích thước từ vựng và cái đuôi dài

Từ vựng không chỉ là một con số cấu hình. Lớp đầu ra của mô hình phải trải xác suất trên toàn bộ từ vựng, nên kích thước của nó quyết định phần lớn số tham số và chi phí tính toán.

Đây là lý do tồn tại của **ngưỡng lọc từ hiếm**. Bỏ những từ xuất hiện quá ít lần không phải để tiết kiệm bộ nhớ, mà vì lý do sâu hơn: một từ chỉ xuất hiện vài lần trong toàn ngữ liệu thì mô hình không có đủ tín hiệu để học biểu diễn cho nó. Giữ lại chỉ tạo thêm một hàng trong ma trận đầu ra mà gradient hầu như không bao giờ chạm tới.

<figure class="diagram">
<svg viewBox="0 0 640 222" role="img" aria-label="Đường tần suất theo hạng từ dốc rồi phẳng dài; một vạch cắt tách phần đuôi được gom vào một ký hiệu chung">
  <g class="dim"><text class="lbl" x="0" y="14" font-size="9.5">TẦN SUẤT THEO HẠNG TỪ</text></g>
  <path class="area" d="M44 44 C72 100 104 130 170 140 C226 148 262 150 300 151 L300 176 L44 176 Z"/>
  <path class="area-warn" d="M300 151 C380 153 470 154 600 155 L600 176 L300 176 Z"/>
  <path class="curve" d="M44 44 C72 100 104 130 170 140 C226 148 262 150 300 151 C380 153 470 154 600 155"/>
  <path class="axis" d="M40 32 V176 H620"/>
  <path class="axis dashed" d="M300 36 V176"/>
  <text x="44" y="30" font-size="10" class="dim">tần suất</text>
  <text x="306" y="48" font-size="10.5" class="dim">ngưỡng lọc tần suất</text>
  <g font-size="10.5" class="dim">
    <text x="44" y="192">giữ trong từ vựng</text>
    <text x="306" y="192">gom vào một ký hiệu chung</text>
  </g>
  <text x="620" y="192" font-size="10" class="dim" text-anchor="end">hạng từ (phổ biến → hiếm)</text>
  <text x="0" y="212" font-size="10.5" class="dim">Gradient hầu như không bao giờ chạm tới những hàng này trong ma trận đầu ra.</text>
</svg>
<figcaption>Vạch cắt không đặt ở chỗ tiết kiệm bộ nhớ, mà ở chỗ tần suất tụt xuống mức không còn đủ lần xuất hiện để học được một biểu diễn.</figcaption>
</figure>

Có một dấu hiệu nhận biết khi từ vựng phình quá mức: cho mô hình dự đoán tiếp một câu mở đầu thông thường, và những từ nó đề xuất là các mảnh vỡ kỳ lạ hoặc danh từ riêng hiếm thay vì các từ phổ biến. Đó là dấu hiệu phân phối đầu ra đã bị cái đuôi dài chi phối.

### Vì sao mô hình huấn luyện sẵn có lợi thế lớn

Một mô hình dựng từ đầu phải học đồng thời hai thứ: cấu trúc thống kê của ngôn ngữ, và tác vụ cụ thể đang huấn luyện. Một mô hình đã huấn luyện sẵn đã có thứ nhất, chỉ cần thích nghi với thứ hai.

<figure class="diagram">
<svg viewBox="0 0 640 164" role="img" aria-label="Dựng từ đầu phải học cả cấu trúc ngôn ngữ lẫn tác vụ, tinh chỉnh chỉ phải học tác vụ">
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">DỰNG TỪ ĐẦU</text>
    <text class="lbl" x="340" y="14" font-size="9.5">TINH CHỈNH MÔ HÌNH SẴN CÓ</text>
  </g>
  <rect class="box-accent" x="0" y="28" width="300" height="42"/>
  <rect class="box-accent" x="0" y="82" width="300" height="42"/>
  <rect class="box-soft" x="340" y="28" width="300" height="42"/>
  <rect class="box-accent" x="340" y="82" width="300" height="42"/>
  <g font-size="11.5">
    <text x="10" y="48">Cấu trúc thống kê của ngôn ngữ</text>
    <text x="10" y="102">Tác vụ cụ thể</text>
    <text x="350" y="48" class="dim">Cấu trúc thống kê của ngôn ngữ</text>
    <text x="350" y="102">Tác vụ cụ thể</text>
  </g>
  <text x="630" y="48" font-size="10" class="dim" text-anchor="end">đã có</text>
  <g font-size="10.5" class="dim">
    <text x="0" y="148">cả hai đều phải học từ cùng ngữ liệu</text>
    <text x="340" y="148">chỉ khối thứ hai cần học</text>
  </g>
</svg>
<figcaption>Cùng một lượng ngữ liệu, cột trái phải chia cho hai việc còn cột phải dồn hết cho một — đó là toàn bộ nội dung của cái gọi là lợi thế.</figcaption>
</figure>

Với ngữ liệu quy mô vừa phải, đây là chênh lệch rất lớn. Điều đó dẫn tới một cách phân biệt hữu ích: dựng kiến trúc từ đầu là bài tập hiểu nguyên lý; tinh chỉnh mô hình sẵn có là con đường tới hệ thống dùng được. Cả hai đều có giá trị, nhưng nhầm lẫn giữa chúng dẫn tới việc dồn thời gian huấn luyện một kiến trúc không có cơ hội thắng.

## Ngành công nghiệp làm việc này ra sao

**Đánh giá cần rộng hơn một con số.** Các khung đánh giá hiện đại đo đồng thời nhiều chiều — không chỉ độ chính xác mà cả độ hiệu chuẩn của xác suất, độ bền trước nhiễu đầu vào, tính công bằng, thiên lệch, độc hại, và chi phí tính toán — trên một tập tình huống rộng, với điều kiện chuẩn hoá như nhau cho mọi mô hình. Lý do là một mô hình có thể tốt ở chiều này và tệ ở chiều khác, và một con số gộp sẽ che mất điều đó. Trước khi các khung này ra đời, các mô hình thường chỉ được đo trên một phần nhỏ số tình huống đáng quan tâm.

**Benchmark đa nhiệm.** Truyền thống đánh giá hiểu ngôn ngữ dựa trên các bộ gồm nhiều tác vụ khác nhau — suy luận, tương đồng câu, phân loại — thay vì một tác vụ đơn lẻ, kèm bộ chẩn đoán để phân tích mô hình mạnh yếu ở hiện tượng ngôn ngữ nào. Khi các mô hình đã vượt qua bộ đầu tiên, một bộ khó hơn được xây tiếp.

**Hệ sinh thái cho tiếng Việt đã tương đối đầy đủ.** Có mô hình ngôn ngữ đơn ngữ quy mô lớn được công bố công khai, vượt các mô hình đa ngữ trên các tác vụ tiếng Việt như gán nhãn từ loại, phân tích cú pháp phụ thuộc, nhận dạng thực thể và suy luận. Có bộ công cụ xử lý cơ bản bao gồm tách từ, gán nhãn từ loại và nhận dạng thực thể. Và gần đây có cả bộ benchmark hiểu ngôn ngữ dành riêng cho tiếng Việt, gồm hơn chục tác vụ được xây bằng cách dịch benchmark có sẵn, sinh ngữ liệu mới, và thu thập các bộ dữ liệu rời rạc.

Điều này đáng nói vì nó thay đổi điểm khởi đầu hợp lý: bắt đầu từ một mô hình sẵn có cho tiếng Việt tiết kiệm hơn nhiều so với bắt đầu từ một lớp nhúng khởi tạo ngẫu nhiên.

## Vài điều rút ra

**Một so sánh chỉ có ý nghĩa khi các yếu tố còn lại được giữ nguyên.** Đổi cách tách từ là đổi đơn vị đo; đổi lượng dữ liệu là đổi độ khó. Đổi cả hai cùng lúc thì kết quả không diễn giải được, dù mỗi lần chạy đều thành công.

**Trước khi so hai con số độ bối rối, hãy kiểm tra hai mô hình có chung bộ từ vựng không.** Nếu không, hai con số ấy không so được với nhau, bất kể chúng trông có vẻ so sánh được đến đâu.

**Khi hai chỉ số cùng đo một mô hình mà kể hai câu chuyện khác nhau, sự chênh lệch đó là thông tin.** Độ chính xác chỉ đếm xem đáp án đúng có nằm trong nhóm dự đoán hàng đầu hay không, nên khá thô. Độ bối rối lấy trung bình của một hàm mũ, nên vài mẫu bị gán xác suất rất thấp cũng đủ kéo giá trị lên cao. Hai chỉ số lệch nhau thường có nghĩa là tập đánh giá quá nhỏ, hoặc mô hình đang ghi nhớ thay vì khái quát hoá.

**Cách đặt bài toán quyết định hiệu quả sử dụng dữ liệu.** Cùng một ngữ liệu, cách đặt thành "dự đoán một từ ở cuối chuỗi" cho ít tín hiệu học hơn nhiều so với cách đặt thành "dự đoán ở mọi vị trí". Đây là lựa chọn nên cân nhắc sớm, vì nó ảnh hưởng tới toàn bộ ngân sách huấn luyện về sau.
