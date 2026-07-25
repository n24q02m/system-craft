---
title: "Quan trắc môi trường: hạ tầng dữ liệu và dự báo chuỗi thời gian"
description: "Lưu trữ dữ liệu vừa có chiều thời gian vừa có chiều không gian, dự báo từng thông số, và cách ngành đo sai số dự báo cho đúng."
lang: "vi"
order: 5
field: "TS"
topics: ["chuỗi thời gian", "dự báo", "dữ liệu không gian", "ARIMA", "MASE"]
---

Bài toán: từ dữ liệu quan trắc chất lượng không khí và chất lượng nước, thu tại nhiều trạm đo trong nhiều năm, đưa ra dự báo cho những ngày tới và cảnh báo khi có nguy cơ vượt ngưỡng an toàn.

Phần thú vị của bài toán này không nằm ở chỗ ai cũng nghĩ. Trước khi bàn tới mô hình dự báo, phải giải xong một bài toán hạ tầng — và đó là phần chiếm nhiều công sức nhất.

## Hệ thống đã dựng

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="Dữ liệu quan trắc hai chiều đi qua kho dữ liệu rồi tách hai nhánh dự báo">
  <defs><marker id="ts-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box" x="0" y="28" width="156" height="46"/>
  <rect class="box" x="0" y="96" width="156" height="46"/>
  <rect class="box-accent" x="212" y="62" width="180" height="46"/>
  <rect class="box" x="448" y="22" width="192" height="52"/>
  <rect class="box" x="448" y="100" width="192" height="52"/>
  <g class="flow" marker-end="url(#ts-a)">
    <path d="M156 51 H184 V80 H206"/>
    <path d="M156 119 H184 V90 H206"/>
    <path d="M392 78 H418 V44 H442"/>
    <path d="M392 92 H418 V122 H442"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="50">Chiều thời gian</text>
    <text x="10" y="118">Chiều không gian</text>
    <text x="222" y="82">Kho dữ liệu</text>
    <text x="458" y="42">Nhánh học sâu</text>
    <text x="458" y="120">Nhánh thống kê</text>
  </g>
  <g font-size="10" class="dim">
    <text x="10" y="66">đo không đều, có khoảng trống</text>
    <text x="10" y="134">toạ độ trạm, truy vấn bán kính</text>
    <text x="222" y="98">chuỗi thời gian và chỉ mục địa lý</text>
    <text x="458" y="58">một mô hình cho mỗi thông số</text>
    <text x="458" y="136">chọn bậc tự động, phân cụm mật độ</text>
  </g>
  <text x="0" y="180" font-size="10.5" class="dim">Trước cả hai nhánh: dự báo ngây thơ làm mốc so sánh.</text>
  <text x="0" y="196" font-size="10.5" class="dim">Không có mốc thì không tồn tại khái niệm tốt hay tệ.</text>
</svg>
<figcaption>Hai chiều dữ liệu quyết định cách lưu trữ; lượng dữ liệu trên mỗi chuỗi quyết định chọn nhánh nào.</figcaption>
</figure>

### Lưu trữ: dữ liệu hai chiều

Dữ liệu quan trắc có ba đặc tính khiến nó khó lưu và khó truy vấn hơn dữ liệu bảng thông thường.

**Nó vừa có chiều thời gian vừa có chiều không gian.** Mỗi phép đo gắn với một thời điểm và một toạ độ địa lý. Câu hỏi thường gặp không phải "giá trị tại trạm này hôm qua là bao nhiêu" mà là "trong bán kính vài chục kilômét quanh điểm này, mức trung bình tuần qua ra sao" — một truy vấn cần cả chỉ mục thời gian lẫn chỉ mục địa lý.

<figure class="diagram">
<svg viewBox="0 0 640 230" role="img" aria-label="Mặt phẳng nhiều trạm đo với một vòng bán kính quanh điểm truy vấn, đặt cạnh hai kiểu câu hỏi">
  <text class="lbl dim" x="0" y="20" font-size="9.5">MẶT PHẲNG TRẠM ĐO</text>
  <text class="lbl dim" x="330" y="20" font-size="9.5">HAI KIỂU CÂU HỎI</text>
  <rect class="box-soft" x="0" y="30" width="296" height="168"/>
  <circle class="node" cx="34" cy="58" r="3"/>
  <circle class="node" cx="70" cy="170" r="3"/>
  <circle class="node" cx="44" cy="112" r="3"/>
  <circle class="node" cx="94" cy="46" r="3"/>
  <circle class="node" cx="232" cy="58" r="3"/>
  <circle class="node" cx="268" cy="104" r="3"/>
  <circle class="node" cx="246" cy="160" r="3"/>
  <circle class="node" cx="206" cy="182" r="3"/>
  <circle class="node" cx="112" cy="182" r="3"/>
  <circle class="node" cx="126" cy="92" r="3"/>
  <circle class="node" cx="176" cy="96" r="3"/>
  <circle class="node" cx="146" cy="152" r="3"/>
  <circle class="node" cx="196" cy="128" r="3"/>
  <circle class="node" cx="118" cy="142" r="3"/>
  <circle class="edge dashed" cx="152" cy="114" r="56"/>
  <line class="edge" x1="96" y1="114" x2="152" y2="114"/>
  <circle class="node-accent" cx="152" cy="114" r="4.5"/>
  <text x="104" y="110" font-size="10" class="dim">bán kính</text>
  <rect class="box" x="330" y="30" width="306" height="48"/>
  <text x="340" y="50" font-size="11.5">Giá trị tại trạm này hôm qua?</text>
  <text x="340" y="66" font-size="10" class="dim">một chiều — chỉ cần chỉ mục thời gian</text>
  <rect class="box-accent" x="330" y="94" width="306" height="64"/>
  <text x="340" y="114" font-size="11.5">Trung bình tuần qua trong bán kính</text>
  <text x="340" y="130" font-size="10" class="dim">vài chục kilômét quanh điểm này</text>
  <text x="340" y="144" font-size="10" class="dim">cần chỉ mục thời gian và chỉ mục địa lý</text>
  <text x="0" y="220" font-size="10.5" class="dim">Cùng một phép đo phải tìm được theo trục thời gian lẫn theo vùng địa lý.</text>
</svg>
<figcaption>Vòng bán kính chỉ chọn ra vài trạm trong số rất nhiều trạm; phần lọc đó phải do chỉ mục địa lý làm chứ không phải quét toàn bộ.</figcaption>
</figure>

**Nó thưa và không đều.** Trạm này đo mỗi giờ, trạm kia mỗi ngày; có trạm ngừng hoạt động một thời gian rồi chạy lại. Giả định "mỗi bước thời gian có đúng một giá trị" — nền tảng của hầu hết mô hình chuỗi thời gian — không tự nhiên đúng, mà phải được tạo ra bằng bước tái lấy mẫu và điền khuyết.

<figure class="diagram">
<svg viewBox="0 0 640 260" role="img" aria-label="Ba trạm với nhịp đo lệch nhau, sau khi tái lấy mẫu thì nằm trên cùng một lưới thời gian đều">
  <defs><marker id="ts-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="16" font-size="9.5">TRƯỚC — NHỊP ĐO THẬT</text>
  <line class="axis" x1="60" y1="44" x2="632" y2="44"/>
  <line class="axis" x1="60" y1="68" x2="632" y2="68"/>
  <line class="axis" x1="60" y1="92" x2="632" y2="92"/>
  <line class="axis" x1="60" y1="190" x2="632" y2="190"/>
  <line class="axis" x1="60" y1="210" x2="632" y2="210"/>
  <line class="axis" x1="60" y1="230" x2="632" y2="230"/>
  <circle class="node" cx="80" cy="44" r="2.4"/>
  <circle class="node" cx="120" cy="44" r="2.4"/>
  <circle class="node" cx="160" cy="44" r="2.4"/>
  <circle class="node" cx="200" cy="44" r="2.4"/>
  <circle class="node" cx="240" cy="44" r="2.4"/>
  <circle class="node" cx="280" cy="44" r="2.4"/>
  <circle class="node" cx="320" cy="44" r="2.4"/>
  <circle class="node" cx="360" cy="44" r="2.4"/>
  <circle class="node" cx="400" cy="44" r="2.4"/>
  <circle class="node" cx="440" cy="44" r="2.4"/>
  <circle class="node" cx="480" cy="44" r="2.4"/>
  <circle class="node" cx="520" cy="44" r="2.4"/>
  <circle class="node" cx="560" cy="44" r="2.4"/>
  <circle class="node" cx="600" cy="44" r="2.4"/>
  <circle class="node" cx="96" cy="68" r="2.4"/>
  <circle class="node" cx="212" cy="68" r="2.4"/>
  <circle class="node" cx="328" cy="68" r="2.4"/>
  <circle class="node" cx="444" cy="68" r="2.4"/>
  <circle class="node" cx="560" cy="68" r="2.4"/>
  <circle class="node" cx="80" cy="92" r="2.4"/>
  <circle class="node" cx="124" cy="92" r="2.4"/>
  <circle class="node" cx="168" cy="92" r="2.4"/>
  <circle class="node" cx="212" cy="92" r="2.4"/>
  <circle class="node" cx="256" cy="92" r="2.4"/>
  <circle class="node" cx="428" cy="92" r="2.4"/>
  <circle class="node" cx="472" cy="92" r="2.4"/>
  <circle class="node" cx="516" cy="92" r="2.4"/>
  <circle class="node" cx="560" cy="92" r="2.4"/>
  <circle class="node" cx="604" cy="92" r="2.4"/>
  <line class="grid" x1="88" y1="182" x2="88" y2="240"/>
  <line class="grid" x1="152" y1="182" x2="152" y2="240"/>
  <line class="grid" x1="216" y1="182" x2="216" y2="240"/>
  <line class="grid" x1="280" y1="182" x2="280" y2="240"/>
  <line class="grid" x1="344" y1="182" x2="344" y2="240"/>
  <line class="grid" x1="408" y1="182" x2="408" y2="240"/>
  <line class="grid" x1="472" y1="182" x2="472" y2="240"/>
  <line class="grid" x1="536" y1="182" x2="536" y2="240"/>
  <line class="grid" x1="600" y1="182" x2="600" y2="240"/>
  <text x="0" y="48" font-size="10" class="dim">Trạm A</text>
  <text x="0" y="72" font-size="10" class="dim">Trạm B</text>
  <text x="0" y="96" font-size="10" class="dim">Trạm C</text>
  <text x="307" y="88" font-size="10" class="dim">ngừng hoạt động</text>
  <text x="60" y="116" font-size="10" class="dim">A đo dày, B đo thưa, C ngừng một đoạn rồi chạy lại</text>
  <path class="flow" marker-end="url(#ts-a2)" d="M380 130 V156"/>
  <text x="392" y="148" font-size="10.5" class="dim">tái lấy mẫu và điền khuyết</text>
  <text class="lbl dim" x="0" y="172" font-size="9.5">SAU — LƯỚI THỜI GIAN ĐỀU</text>
  <circle class="node" cx="88" cy="190" r="3"/>
  <circle class="node" cx="152" cy="190" r="3"/>
  <circle class="node" cx="216" cy="190" r="3"/>
  <circle class="node" cx="280" cy="190" r="3"/>
  <circle class="node" cx="344" cy="190" r="3"/>
  <circle class="node" cx="408" cy="190" r="3"/>
  <circle class="node" cx="472" cy="190" r="3"/>
  <circle class="node" cx="536" cy="190" r="3"/>
  <circle class="node" cx="600" cy="190" r="3"/>
  <circle class="node" cx="88" cy="210" r="3"/>
  <circle class="node" cx="216" cy="210" r="3"/>
  <circle class="node" cx="344" cy="210" r="3"/>
  <circle class="node" cx="472" cy="210" r="3"/>
  <circle class="node" cx="536" cy="210" r="3"/>
  <circle class="node-open" cx="152" cy="210" r="3"/>
  <circle class="node-open" cx="280" cy="210" r="3"/>
  <circle class="node-open" cx="408" cy="210" r="3"/>
  <circle class="node-open" cx="600" cy="210" r="3"/>
  <circle class="node" cx="88" cy="230" r="3"/>
  <circle class="node" cx="152" cy="230" r="3"/>
  <circle class="node" cx="216" cy="230" r="3"/>
  <circle class="node" cx="472" cy="230" r="3"/>
  <circle class="node" cx="536" cy="230" r="3"/>
  <circle class="node" cx="600" cy="230" r="3"/>
  <circle class="node-open" cx="280" cy="230" r="3"/>
  <circle class="node-open" cx="344" cy="230" r="3"/>
  <circle class="node-open" cx="408" cy="230" r="3"/>
  <text x="0" y="194" font-size="10" class="dim">Trạm A</text>
  <text x="0" y="214" font-size="10" class="dim">Trạm B</text>
  <text x="0" y="234" font-size="10" class="dim">Trạm C</text>
  <circle class="node" cx="64" cy="248" r="3"/>
  <text x="74" y="252" font-size="10" class="dim">số đo thật</text>
  <circle class="node-open" cx="170" cy="248" r="3"/>
  <text x="180" y="252" font-size="10" class="dim">giá trị điền vào</text>
  <text x="300" y="252" font-size="10" class="dim">điền khuyết là quyết định mô hình hoá, không phải dọn dẹp</text>
</svg>
<figcaption>Lưới đều là thứ được tạo ra ở bước xử lý chứ không có sẵn trong dữ liệu; các điểm rỗng là giá trị do ta chọn cách sinh ra.</figcaption>
</figure>

**Mỗi thông số là một chuỗi riêng.** Nồng độ ô-zôn và nồng độ một kim loại vết có biên độ khác nhau hàng nghìn lần, chu kỳ khác nhau, và cơ chế vật lý sinh ra chúng cũng khác nhau.

Giải pháp lưu trữ là một cơ sở dữ liệu tài liệu có hỗ trợ sẵn hai thứ cần thiết: **collection kiểu chuỗi thời gian** (tối ưu cho dữ liệu chỉ ghi thêm, có trục thời gian, nén tốt theo cụm thời gian) và **chỉ mục địa lý** (cho phép truy vấn theo bán kính, theo đa giác, theo khoảng cách). Hai thứ này giải quyết đúng hai chiều của bài toán mà không cần tự cài.

### Đường ống dữ liệu

Nguồn là các bộ dữ liệu quan trắc công khai theo chuẩn của cơ quan môi trường: bảng đo chất lượng không khí với các trường mã bang, mã hạt, mã trạm, toạ độ, tên thông số, giá trị trung bình và chỉ số chất lượng không khí; bảng đo chất lượng nước với mã tổ chức, mã điểm quan trắc, tên đặc tính đo và giá trị.

Các bước xử lý: chuẩn hoá tên thông số, tái lấy mẫu về lưới thời gian đều, điền khuyết, chuẩn hoá đơn vị, rồi nạp vào cơ sở dữ liệu theo lược đồ đã thiết kế. Việc điền khuyết là một quyết định mô hình hoá chứ không phải thao tác dọn dẹp vô hại — cách điền ảnh hưởng trực tiếp tới thứ mô hình học được.

### Dự báo không khí: mạng hồi tiếp cho từng thông số

Thay vì một mô hình chung cho mọi thông số, hệ thống huấn luyện **một mô hình riêng cho mỗi thông số**. Lý do đã nêu ở trên: các thông số khác nhau về biên độ, chu kỳ và cơ chế, nên gộp chung thường tệ hơn.

Kiến trúc là mạng LSTM nhiều lớp kèm cơ chế chú ý, dropout và chuẩn hoá batch, dừng sớm theo tập kiểm định. Đầu ra là dự báo cho một cửa sổ vài ngày tới.

Kết quả từ các mô hình riêng lẻ được gộp thành một **chỉ số rủi ro sức khoẻ tổng hợp**: mỗi thông số được gán trọng số theo mức độ nguy hại, quy về thang chung rồi cộng lại, và ánh xạ sang các mức cảnh báo. Chỉ số này cũng được phân rã theo hệ cơ quan chịu ảnh hưởng — hô hấp, tim mạch, thần kinh — để cảnh báo có ý nghĩa với người đọc.

### Dự báo nước: thống kê cổ điển và phân cụm không gian

Nhánh chất lượng nước đi hướng khác hẳn: không dùng học sâu.

**Phân cụm không gian** bằng thuật toán gom cụm theo mật độ. Điểm hay của thuật toán này với dữ liệu địa lý là nó không cần biết trước số cụm, tự phát hiện được cụm hình dạng bất kỳ, và đánh dấu các điểm nằm ngoài mọi cụm là nhiễu — phù hợp với các trạm quan trắc rải rác không đều.

<figure class="diagram">
<svg viewBox="0 0 640 240" role="img" aria-label="Các trạm trên mặt phẳng gom thành ba vùng dày đặc hình dạng khác nhau, kèm vài điểm lẻ đánh dấu là nhiễu">
  <text class="lbl dim" x="0" y="20" font-size="9.5">TRẠM QUAN TRẮC TRÊN MẶT PHẲNG</text>
  <text class="lbl dim" x="364" y="20" font-size="9.5">BA TÍNH CHẤT</text>
  <rect class="box-soft" x="0" y="28" width="340" height="190"/>
  <circle class="node" cx="145" cy="114" r="3"/>
  <circle class="node" cx="136" cy="129" r="3"/>
  <circle class="node" cx="122" cy="141" r="3"/>
  <circle class="node" cx="105" cy="147" r="3"/>
  <circle class="node" cx="87" cy="147" r="3"/>
  <circle class="node" cx="70" cy="141" r="3"/>
  <circle class="node" cx="56" cy="129" r="3"/>
  <circle class="node" cx="47" cy="114" r="3"/>
  <circle class="node" cx="129" cy="119" r="3"/>
  <circle class="node" cx="113" cy="132" r="3"/>
  <circle class="node" cx="92" cy="136" r="3"/>
  <circle class="node" cx="73" cy="129" r="3"/>
  <circle class="node" cx="60" cy="113" r="3"/>
  <circle class="node" cx="176" cy="52" r="3"/>
  <circle class="node" cx="190" cy="60" r="3"/>
  <circle class="node" cx="204" cy="68" r="3"/>
  <circle class="node" cx="218" cy="76" r="3"/>
  <circle class="node" cx="232" cy="84" r="3"/>
  <circle class="node" cx="246" cy="92" r="3"/>
  <circle class="node" cx="170" cy="62" r="3"/>
  <circle class="node" cx="184" cy="70" r="3"/>
  <circle class="node" cx="198" cy="78" r="3"/>
  <circle class="node" cx="212" cy="86" r="3"/>
  <circle class="node" cx="226" cy="94" r="3"/>
  <circle class="node" cx="198" cy="148" r="3"/>
  <circle class="node" cx="212" cy="146" r="3"/>
  <circle class="node" cx="226" cy="149" r="3"/>
  <circle class="node" cx="240" cy="156" r="3"/>
  <circle class="node" cx="249" cy="168" r="3"/>
  <circle class="node" cx="250" cy="181" r="3"/>
  <circle class="node" cx="241" cy="191" r="3"/>
  <circle class="node" cx="227" cy="195" r="3"/>
  <circle class="node" cx="213" cy="190" r="3"/>
  <circle class="node" cx="222" cy="166" r="3"/>
  <circle class="node-open" cx="30" cy="58" r="3.2"/>
  <circle class="node-open" cx="156" cy="190" r="3.2"/>
  <circle class="node-open" cx="300" cy="120" r="3.2"/>
  <circle class="node-open" cx="292" cy="44" r="3.2"/>
  <circle class="node-open" cx="78" cy="202" r="3.2"/>
  <circle class="node-open" cx="306" cy="196" r="3.2"/>
  <text x="38" y="54" font-size="10" class="dim">nhiễu</text>
  <rect class="box" x="364" y="28" width="272" height="52"/>
  <text x="374" y="48" font-size="11.5">Không cần biết trước số cụm</text>
  <text x="374" y="64" font-size="10" class="dim">thuật toán tự xác định</text>
  <rect class="box" x="364" y="94" width="272" height="52"/>
  <text x="374" y="114" font-size="11.5">Cụm hình dạng bất kỳ</text>
  <text x="374" y="130" font-size="10" class="dim">không giả định cụm tròn</text>
  <rect class="box" x="364" y="160" width="272" height="52"/>
  <text x="374" y="180" font-size="11.5">Điểm ngoài cụm là nhiễu</text>
  <text x="374" y="196" font-size="10" class="dim">không bị ép vào cụm nào</text>
  <text x="0" y="234" font-size="10.5" class="dim">Cụm ở đây là vùng dày đặc trạm, không phải hình tròn quanh một tâm.</text>
</svg>
<figcaption>Ba vùng dày đặc có hình dạng khác hẳn nhau; sáu điểm lẻ không thuộc vùng nào và được để riêng thay vì gán bừa vào cụm gần nhất.</figcaption>
</figure>

**Dự báo bằng ARIMA với chọn bậc tự động.** ARIMA là mô hình thống kê kết hợp ba thành phần: tự hồi quy (giá trị hiện tại phụ thuộc tuyến tính vào các giá trị trước), sai phân (lấy hiệu để khử xu hướng, đưa chuỗi về dạng dừng), và trung bình trượt (phụ thuộc vào các sai số dự báo trước). Việc chọn ba bậc này thường làm thủ công bằng cách nhìn đồ thị tự tương quan; thư viện dùng ở đây tự dò trên một lưới tham số và chọn theo tiêu chí thông tin.

Ngoài dự báo, nhánh này còn tính **tỷ lệ vượt ngưỡng** cho từng đặc tính — bao nhiêu phần trăm số đo nằm ngoài khoảng an toàn — và cảnh báo khi dự báo cho thấy xu hướng vượt ngưỡng kéo dài.

## Kiến thức nền

### Vì sao chuỗi thời gian khác các bài toán học máy khác

Điểm khác biệt căn bản: **giá trị gần nhất đã là một dự báo rất tốt.** Nhiệt độ ngày mai gần với nhiệt độ hôm nay. Với dữ liệu có mùa vụ, giá trị cùng kỳ mùa trước còn tốt hơn nữa.

Hai phương pháp này — dự báo ngây thơ và dự báo ngây thơ theo mùa — không có tham số nào để học và chạy tức thì. Chúng là điểm khởi đầu bắt buộc, không phải vì chúng tốt, mà vì không có chúng thì không tồn tại khái niệm "tốt" hay "tệ" cho mọi con số về sau.

<figure class="diagram">
<svg viewBox="0 0 640 220" role="img" aria-label="Chuỗi có mùa vụ, và từ điểm kết thúc huấn luyện là hai đường dự báo ngây thơ">
  <path class="axis" d="M24 30 V170 H620"/>
  <line class="axis dashed" x1="414" y1="30" x2="414" y2="176"/>
  <text class="lbl dim" x="194" y="24" font-size="9.5">HUẤN LUYỆN</text>
  <text class="lbl dim" x="490" y="24" font-size="9.5">DỰ BÁO</text>
  <path class="curve" d="M30 134 C47.5 134 60.5 66 78 66 C95.5 66 108.5 134 126 134 C143.5 134 156.5 66 174 66 C191.5 66 204.5 134 222 134 C239.5 134 252.5 66 270 66 C287.5 66 300.5 134 318 134 C335.5 134 348.5 66 366 66 C383.5 66 396.5 134 414 134"/>
  <path class="curve-warn dashed" d="M414 134 H606"/>
  <path class="curve-accent dashed" d="M414 134 C431.5 134 444.5 66 462 66 C479.5 66 492.5 134 510 134 C527.5 134 540.5 66 558 66 C575.5 66 588.5 134 606 134"/>
  <line class="curve-warn dashed" x1="0" y1="192" x2="22" y2="192"/>
  <text x="28" y="196" font-size="10.5" class="dim">dự báo ngây thơ — giữ nguyên giá trị cuối</text>
  <line class="curve-accent dashed" x1="0" y1="208" x2="22" y2="208"/>
  <text x="28" y="212" font-size="10.5" class="dim">ngây thơ theo mùa — lặp lại cùng kỳ mùa trước</text>
  <text x="330" y="196" font-size="10.5" class="dim">Không có tham số nào để học, chạy tức thì.</text>
  <text x="330" y="212" font-size="10.5" class="dim">Bỏ mốc này thì không có gì để gọi là tốt.</text>
</svg>
<figcaption>Đường ngang là toàn bộ nội dung của dự báo ngây thơ; một mô hình phức tạp phải vượt được nó trước khi đáng bàn.</figcaption>
</figure>

### Tính dừng

Phần lớn mô hình thống kê cho chuỗi thời gian giả định chuỗi **dừng**: các tính chất thống kê như trung bình và phương sai không đổi theo thời gian. Dữ liệu thật hiếm khi dừng — nó có xu hướng tăng giảm dài hạn và có chu kỳ mùa. Bước sai phân trong ARIMA chính là để khử xu hướng, và các biến thể có thành phần mùa vụ để khử chu kỳ.

<figure class="diagram">
<svg viewBox="0 0 640 268" role="img" aria-label="Chuỗi gốc có trung bình trôi lên, và chuỗi sau sai phân dao động quanh một mức không đổi">
  <defs><marker id="ts-a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="16" font-size="9.5">CHUỖI GỐC — XU HƯỚNG VÀ MÙA VỤ</text>
  <path class="axis" d="M24 26 V112 H620"/>
  <path class="curve" d="M30 108 C47.5 108 60.5 80.3 78 80.3 C95.5 80.3 108.5 100.7 126 100.7 C143.5 100.7 156.5 73 174 73 C191.5 73 204.5 93.3 222 93.3 C239.5 93.3 252.5 65.7 270 65.7 C287.5 65.7 300.5 86 318 86 C335.5 86 348.5 58.3 366 58.3 C383.5 58.3 396.5 78.7 414 78.7 C431.5 78.7 444.5 51 462 51 C479.5 51 492.5 71.3 510 71.3 C527.5 71.3 540.5 43.7 558 43.7 C575.5 43.7 588.5 64 606 64"/>
  <line class="curve-accent dashed" x1="30" y1="96" x2="606" y2="52"/>
  <line class="curve-accent dashed" x1="0" y1="128" x2="22" y2="128"/>
  <text x="28" y="132" font-size="10" class="dim">trung bình trượt trôi theo thời gian — chuỗi không dừng</text>
  <path class="flow" marker-end="url(#ts-a3)" d="M600 122 V152"/>
  <text x="470" y="141" font-size="10.5" class="dim">một bước sai phân</text>
  <text class="lbl dim" x="0" y="166" font-size="9.5">SAU MỘT BƯỚC SAI PHÂN</text>
  <path class="axis" d="M24 174 V242 H620"/>
  <path class="curve" d="M30 226 C47.5 226 60.5 190 78 190 C95.5 190 108.5 228 126 228 C143.5 228 156.5 188 174 188 C191.5 188 204.5 224 222 224 C239.5 224 252.5 192 270 192 C287.5 192 300.5 227 318 227 C335.5 227 348.5 189 366 189 C383.5 189 396.5 225 414 225 C431.5 225 444.5 191 462 191 C479.5 191 492.5 226 510 226 C527.5 226 540.5 190 558 190 C575.5 190 588.5 224 606 224"/>
  <line class="curve-accent dashed" x1="30" y1="208" x2="606" y2="208"/>
  <line class="curve-accent dashed" x1="0" y1="256" x2="22" y2="256"/>
  <text x="28" y="260" font-size="10" class="dim">trung bình trượt nằm ngang — chuỗi đã dừng</text>
</svg>
<figcaption>Sai phân không làm dữ liệu tốt hơn; nó đưa dữ liệu về đúng dạng mà mô hình thống kê giả định là có sẵn.</figcaption>
</figure>

Với mạng nơ-ron thì giả định này không bắt buộc, nhưng đổi lại chúng cần nhiều dữ liệu hơn nhiều để tự học được cấu trúc mà mô hình thống kê được cho biết trước.

### Khi nào học sâu có lợi thế, khi nào không

Mô hình học sâu cần **nhiều điểm quan sát trên mỗi chuỗi** để vượt các phương pháp thống kê. Khi mỗi chuỗi chỉ có vài trăm điểm, số tham số của mạng vượt xa lượng thông tin trong dữ liệu, và thứ nó học được chủ yếu là nhiễu.

<figure class="diagram">
<svg viewBox="0 0 640 226" role="img" aria-label="Hai đường chất lượng dự báo cắt nhau khi số điểm quan sát trên mỗi chuỗi tăng dần">
  <text class="lbl dim" x="0" y="18" font-size="9.5">CHẤT LƯỢNG DỰ BÁO</text>
  <text class="lbl dim" x="120" y="18" font-size="9.5">BÀI TOÁN NÀY — VÀI TRĂM ĐIỂM MỖI CHUỖI</text>
  <rect class="area" x="120" y="26" width="120" height="154"/>
  <path class="axis" d="M40 26 V180 H610"/>
  <line class="axis dashed" x1="305" y1="26" x2="305" y2="186"/>
  <path class="curve" d="M60 140 L90 128 L120 118.4 L150 110.6 L185 103.4 L220 97.8 L260 92.9 L305 88.8 L350 85.8 L400 83.5 L450 81.8 L500 80.7 L550 79.9 L600 79.3"/>
  <path class="curve-accent" d="M60 170 L90 153.6 L120 139.7 L150 127.7 L185 116 L220 106.2 L260 97.1 L305 88.8 L350 82.3 L400 76.7 L450 72.4 L500 69.1 L550 66.5 L600 64.5"/>
  <circle class="node-accent" cx="305" cy="88.8" r="4"/>
  <text x="312" y="44" font-size="10.5" class="dim">điểm cắt</text>
  <text x="124" y="166" font-size="10" class="dim">thống kê thắng ở vùng này</text>
  <text class="num" x="44" y="194">ít</text>
  <text class="num" x="586" y="194">nhiều</text>
  <text class="lbl dim" x="240" y="194" font-size="9.5">SỐ ĐIỂM TRÊN MỖI CHUỖI</text>
  <line class="curve" x1="0" y1="210" x2="22" y2="210"/>
  <text x="28" y="214" font-size="10.5" class="dim">thống kê cổ điển</text>
  <line class="curve-accent" x1="180" y1="210" x2="202" y2="210"/>
  <text x="208" y="214" font-size="10.5" class="dim">học sâu</text>
  <text x="320" y="214" font-size="10.5" class="dim">Điểm cắt phụ thuộc lượng dữ liệu trên mỗi chuỗi.</text>
</svg>
<figcaption>Điểm cắt, chứ không phải bản thân kiến trúc, là thứ quyết định nên chọn nhánh nào cho một tập dữ liệu cụ thể.</figcaption>
</figure>

Lợi thế của học sâu xuất hiện khi có nhiều chuỗi liên quan để học chung một biểu diễn, khi có biến ngoại sinh phức tạp, hoặc khi quan hệ phi tuyến rõ rệt. Với một tập trạm quan trắc quy mô vừa, đó không hiển nhiên là trường hợp tốt cho học sâu.

## Ngành công nghiệp làm việc này ra sao

### Chọn thước đo sai số

Phản xạ tự nhiên khi báo cáo sai số dự báo là dùng sai số phần trăm tuyệt đối trung bình. Nó trực quan và ai cũng hiểu. Nhưng nó có một chỗ hỏng nghiêm trọng với đúng loại dữ liệu này: **nó chia cho giá trị thật**, mà nhiều thông số môi trường có giá trị rất gần 0 trong phần lớn thời gian — đó chính là trạng thái bình thường, không phải dữ liệu lỗi. Khi mẫu số gần 0, tỷ số nổ tung.

<figure class="diagram">
<svg viewBox="0 0 640 236" role="img" aria-label="Đường sai số phần trăm vọt lên vô cực khi giá trị thật tiến về 0, trong khi đường chỉ số chuẩn hoá theo baseline nằm ngang">
  <defs><marker id="ts-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="area-warn" x="60" y="28" width="64" height="172"/>
  <path class="axis" d="M60 24 V200 H436"/>
  <line class="axis dashed" x1="60" y1="140" x2="430" y2="140"/>
  <text class="num" x="48" y="144">1</text>
  <text class="lbl dim" x="0" y="18" font-size="9.5">GIÁ TRỊ CỦA CHỈ SỐ</text>
  <path class="curve-warn" d="M68 28 L70 52.9 L72 69.6 L75 86.2 L78 97.3 L82 107.4 L86 114.3 L92 121.5 L100 127.8 L110 132.8 L124 137.1 L140 140.2 L160 142.7 L185 144.7 L215 146.3 L250 147.5 L290 148.4 L340 149.1 L430 150"/>
  <path class="curve-accent" d="M62 160 H430"/>
  <path class="flow" marker-end="url(#ts-a4)" d="M146 48 H110"/>
  <text x="150" y="52" font-size="11.5">Giá trị thật gần 0 là trạng thái bình thường</text>
  <text x="150" y="68" font-size="10" class="dim">của dữ liệu môi trường, không phải dữ liệu lỗi</text>
  <text x="200" y="134" font-size="10" class="dim">trên một: tệ hơn dự báo ngây thơ</text>
  <text x="200" y="176" font-size="10" class="dim">dưới một: tốt hơn dự báo ngây thơ</text>
  <line class="edge" x1="432" y1="150" x2="440" y2="144"/>
  <line class="edge" x1="432" y1="160" x2="440" y2="176"/>
  <text x="444" y="140" font-size="11.5">MAPE</text>
  <text x="444" y="154" font-size="10" class="dim">chia cho giá trị thật</text>
  <text x="444" y="178" font-size="11.5">MASE</text>
  <text x="444" y="192" font-size="10" class="dim">chia cho sai số ngây thơ</text>
  <text class="lbl dim" x="360" y="218" font-size="9.5">GIÁ TRỊ THẬT</text>
  <text x="0" y="232" font-size="10.5" class="dim">Ở vùng nguy hiểm chỉ số vẫn cho ra một con số — nó không báo lỗi, chỉ vô nghĩa.</text>
</svg>
<figcaption>Vùng tô là nơi phần lớn dữ liệu môi trường thực sự nằm — cũng chính là nơi chỉ số phần trăm mất hết ý nghĩa.</figcaption>
</figure>

Công trình chuẩn về vấn đề này, đăng trên tạp chí chuyên ngành về dự báo, chỉ ra rằng ngay cả biến thể "đối xứng" của chỉ số ấy cũng không cứu được: nó vẫn chia cho một đại lượng có thể rất nhỏ, và bất chấp cái tên có chữ "tuyệt đối", nó vẫn có thể nhận giá trị âm. Bài báo minh hoạ bằng các chuỗi thật có chứa giá trị bằng 0 hoặc âm, ở đó chỉ số này cho ra vô cực hoặc không xác định.

Giải pháp được đề xuất là **MASE** — sai số tuyệt đối chuẩn hoá theo thang. Thay vì chia cho giá trị thật, chia sai số cho sai số trung bình của phương pháp ngây thơ tính trên tập huấn luyện. Ba tính chất làm nó phù hợp: không phụ thuộc thang đo nên so được giữa các thông số khác nhau; không bao giờ vô định trừ khi chuỗi là hằng số; và có mốc diễn giải tự nhiên — dưới một nghĩa là tốt hơn phép dự báo ngây thơ, trên một nghĩa là tệ hơn.

### Benchmark của lĩnh vực

Các cuộc thi dự báo quy mô lớn của ngành đặt ra chuẩn thực hành. Một cuộc thi dùng hàng trăm nghìn chuỗi thuộc nhiều lĩnh vực khác nhau và hàng chục phương pháp dự thi, đánh giá bằng các chỉ số chuẩn hoá theo baseline và yêu cầu cả khoảng dự báo chứ không chỉ giá trị điểm. Một cuộc thi khác dùng dữ liệu doanh số bán lẻ có cấu trúc phân cấp, với hàng chục nghìn chuỗi, và báo cáo mức cải thiện so với benchmark tốt nhất thay vì sai số trần trụi.

Giáo trình chuẩn của lĩnh vực, do chính đồng tác giả của MASE viết và công bố miễn phí, nhấn mạnh thêm hai điều: phải so với phương pháp ngây thơ trước khi kết luận một mô hình phức tạp có giá trị; và phải đánh giá bằng dự báo thật trên tập kiểm tra, vì một mô hình khớp dữ liệu huấn luyện rất tốt không đảm bảo sẽ dự báo tốt.

## Vài điều rút ra

**Baseline là hệ quy chiếu, không phải nghi thức.** Với chuỗi thời gian, baseline mạnh một cách bất ngờ, nên bỏ qua bước này dễ dẫn tới việc ăn mừng một kết quả thực ra tệ hơn không làm gì.

**Chọn chỉ số phải khớp với đặc tính dữ liệu.** Một chỉ số không phù hợp vẫn tính ra số, và đó chính là chỗ nguy hiểm: nó không báo lỗi, chỉ đưa ra con số vô nghĩa để người đọc tin.

**Thêm dữ liệu tổng hợp không mặc nhiên có lợi.** Nếu quá trình sinh không phản ánh đúng cơ chế tạo ra dữ liệu thật, mô hình sẽ học phân phối của bộ sinh. Cách kiểm tra rẻ: luôn giữ một nhánh chỉ dùng dữ liệu thật và so hai nhánh trên cùng một tập kiểm tra thật.

**Chỉ số tổng hợp cần ghi rõ giả định.** Trọng số của từng thông số và các ngưỡng cảnh báo là phán đoán chuyên môn, không phải lựa chọn kỹ thuật. Ghi chúng thành tài liệu kèm nguồn là điều kiện để người khác kiểm chứng được.

**Hạ tầng dữ liệu là phần đầu tư có tuổi thọ dài nhất.** Mô hình sẽ được thay; lược đồ lưu trữ, chỉ mục và đường ống làm sạch thì ở lại lâu hơn nhiều.
