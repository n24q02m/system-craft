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

<figure class="diagram">
<svg viewBox="0 0 640 256" role="img" aria-label="Vòng tròn cảm xúc Russell: mặt phẳng hai trục sắc thái và mức kích thích, tám tâm trạng ví dụ nằm quanh vòng tròn">
  <defs><marker id="rec-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <ellipse class="grid dashed" cx="320" cy="134" rx="190" ry="86"/>
  <g class="axis" marker-end="url(#rec-a2)">
    <path d="M320 134 V38"/><path d="M320 134 V230"/>
    <path d="M320 134 H90"/><path d="M320 134 H550"/>
  </g>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="320" y="26" text-anchor="middle">KÍCH THÍCH CAO</text>
    <text class="lbl" x="320" y="248" text-anchor="middle">KÍCH THÍCH THẤP</text>
    <text class="lbl" x="82" y="138" text-anchor="end">TIÊU CỰC</text>
    <text class="lbl" x="558" y="138">TÍCH CỰC</text>
  </g>
  <g class="node">
    <circle cx="496" cy="101" r="3"/><circle cx="393" cy="55" r="3"/>
    <circle cx="247" cy="55" r="3"/><circle cx="144" cy="101" r="3"/>
    <circle cx="144" cy="167" r="3"/><circle cx="247" cy="214" r="3"/>
    <circle cx="393" cy="214" r="3"/><circle cx="496" cy="167" r="3"/>
  </g>
  <circle class="node-open" cx="454" cy="73" r="3.5"/>
  <g font-size="11.5">
    <text x="504" y="105">hân hoan</text>
    <text x="401" y="59">phấn khích</text>
    <text x="239" y="59" text-anchor="end">giận dữ</text>
    <text x="136" y="105" text-anchor="end">lo âu</text>
    <text x="136" y="171" text-anchor="end">chán nản</text>
    <text x="239" y="218" text-anchor="end">buồn</text>
    <text x="401" y="218">êm dịu</text>
    <text x="504" y="171">thư thái</text>
    <text x="462" y="77" font-size="10" class="dim">nhãn mới</text>
  </g>
</svg>
<figcaption>Hai trục biến bộ nhãn tâm trạng thành một không gian có toạ độ, nên một nhãn mới có chỗ để rơi vào thay vì phải chèn thêm vào cuối một danh sách.</figcaption>
</figure>

Việc neo vào hệ phân loại có sẵn nghe như chi tiết nhỏ, nhưng nó quyết định khả năng mở rộng: khi cần thêm nhãn, có một cấu trúc để đặt nhãn mới vào đúng chỗ, thay vì một danh sách phẳng mà ai cũng có thể thêm bừa.

Về mô hình, tầng này dùng hai mạng chạy song song. Một mạng phân loại đa nhãn dựa trên kiến trúc transformer cho phổ âm thanh, với bốn đầu ra riêng cho bốn nhóm nhãn đầu. Một mạng riêng chuyên cho nhận dạng ngôn ngữ, dựa trên kiến trúc thường dùng trong xử lý tiếng nói. Tách hai việc thay vì gộp vào một mạng nhiều đầu là có chủ ý: nhận dạng ngôn ngữ dựa vào đặc trưng ngữ âm, còn phân loại thể loại dựa vào đặc trưng hoà âm và nhịp điệu — ép chúng dùng chung phần thân dễ khiến hai tác vụ cản nhau.

### Tầng hai: sinh biểu diễn và lập chỉ mục

Đây là nút thắt của toàn hệ thống. Mỗi bài hát được biến thành bốn vector nằm trong bốn không gian khác nhau:

- **Vector âm thanh**, lấy từ trạng thái ẩn của mạng phân tích phổ, tính trung bình theo trục thời gian.
- **Vector thẻ mô tả**, sinh bằng một mô hình nhúng văn bản đa ngữ. Điểm thú vị ở đây: thay vì mã hoá các nhãn thành vector nhị phân, hệ thống **ghép chúng thành một câu tiếng Việt tự nhiên** — đại ý "Tiêu đề X. Nghệ sĩ Y. Thể loại A. Tâm trạng B. Nhạc cụ C" — rồi mới đưa vào mô hình nhúng. Nhờ vậy một truy vấn kiểu "bài buồn có tiếng guitar" khớp được với nội dung mà không cần từ điển ánh xạ thủ công giữa từ khoá và nhãn.
- **Vector lời bài hát**, cũng từ mô hình nhúng văn bản, chạy trên phần lời.
- **Vector hành vi**, lấy từ ma trận thừa số của mô hình lọc cộng tác.

<figure class="diagram">
<svg viewBox="0 0 640 190" role="img" aria-label="Hai cách biến nhãn thành vector: ghép nhãn thành câu tự nhiên rồi nhúng, đối lại mã hoá nhị phân cho ra vector thưa">
  <defs><marker id="rec-a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="156" y="18">CÁCH ĐÃ CHỌN</text>
    <text class="lbl" x="156" y="116">CÁCH ĐÃ BỎ</text>
  </g>
  <rect class="box-soft" x="0" y="75" width="132" height="58"/>
  <rect class="box-ok" x="156" y="28" width="168" height="58"/>
  <rect class="box-ok" x="348" y="33" width="128" height="48"/>
  <rect class="box-ok" x="500" y="28" width="136" height="58"/>
  <rect class="box-warn" x="156" y="126" width="168" height="48"/>
  <rect class="box-warn" x="500" y="121" width="136" height="58"/>
  <g class="flow" marker-end="url(#rec-a3)">
    <path d="M132 96 H144 V57 H152"/><path d="M132 112 H144 V150 H152"/>
    <path d="M324 57 H344"/><path d="M476 57 H496"/><path d="M324 150 H496"/>
  </g>
  <g font-size="11.5">
    <text x="10" y="95">Nhãn rời</text>
    <text x="10" y="109" font-size="10" class="dim">thể loại, tâm trạng</text>
    <text x="10" y="123" font-size="10" class="dim">nhạc cụ, giọng hát</text>
    <text x="166" y="48">Câu tiếng Việt tự nhiên</text>
    <text x="166" y="62" font-size="10" class="dim">Tiêu đề X. Thể loại A.</text>
    <text x="166" y="76" font-size="10" class="dim">Tâm trạng B. Nhạc cụ C.</text>
    <text x="358" y="53">Mô hình nhúng</text>
    <text x="358" y="67" font-size="10" class="dim">văn bản đa ngữ</text>
    <text x="510" y="48">Vector dày</text>
    <text x="510" y="62" font-size="10" class="dim">khớp truy vấn</text>
    <text x="510" y="76" font-size="10" class="dim">ngôn ngữ tự nhiên</text>
    <text x="166" y="146">Mã hoá nhị phân</text>
    <text x="166" y="160" font-size="10" class="dim">mỗi nhãn một chiều 0/1</text>
    <text x="510" y="141">Vector thưa</text>
    <text x="510" y="155" font-size="10" class="dim">không khớp truy vấn</text>
    <text x="510" y="169" font-size="10" class="dim">ngôn ngữ tự nhiên</text>
    <text x="352" y="143" font-size="10" class="dim">không qua mô hình nào</text>
  </g>
</svg>
<figcaption>Câu tự nhiên là bước đệm đưa truy vấn của người dùng và mô tả nội dung về chung một không gian; mã hoá nhị phân không có bước đệm đó.</figcaption>
</figure>

Bốn vector này được lập chỉ mục riêng bằng một thư viện tìm kiếm lân cận gần đúng, dùng cấu trúc đồ thị phân tầng. Ý tưởng của cấu trúc này là xây đồ thị nhiều lớp, lớp trên thưa để nhảy xa, lớp dưới dày để tinh chỉnh — nhờ đó thời gian tìm kiếm tăng theo hàm lô-ga-rít thay vì tuyến tính với số lượng mục.

<figure class="diagram">
<svg viewBox="0 0 640 248" role="img" aria-label="Đồ thị phân tầng: lớp trên ít điểm cạnh dài, các lớp dưới dày dần, đường tìm kiếm đi từ điểm vào ở lớp trên xuống tới đích ở lớp đáy">
  <defs><marker id="rec-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-soft" x="126" y="28" width="488" height="48"/>
  <rect class="box-soft" x="126" y="104" width="488" height="50"/>
  <rect class="box-soft" x="126" y="180" width="488" height="50"/>
  <g class="grid dashed">
    <path d="M140 62 V138"/><path d="M288 40 V142"/><path d="M510 58 V116"/>
    <path d="M140 138 V214"/><path d="M214 116 V218"/><path d="M288 142 V216"/>
    <path d="M362 118 V214"/><path d="M436 140 V218"/><path d="M510 116 V212"/>
    <path d="M584 140 V216"/>
  </g>
  <g class="edge">
    <path d="M140 62 L288 40"/><path d="M288 40 L510 58"/><path d="M140 62 L510 58"/>
    <path d="M140 138 L214 116"/><path d="M214 116 L288 142"/><path d="M288 142 L362 118"/>
    <path d="M362 118 L436 140"/><path d="M436 140 L510 116"/><path d="M510 116 L584 140"/>
    <path d="M140 138 L288 142"/><path d="M362 118 L510 116"/>
    <path d="M140 214 L177 192"/><path d="M177 192 L214 218"/><path d="M214 218 L251 194"/>
    <path d="M251 194 L288 216"/><path d="M288 216 L325 190"/><path d="M325 190 L362 214"/>
    <path d="M362 214 L399 196"/><path d="M399 196 L436 218"/><path d="M436 218 L473 192"/>
    <path d="M473 192 L510 212"/><path d="M510 212 L547 196"/><path d="M547 196 L584 216"/>
    <path d="M140 214 L214 218"/><path d="M288 216 L362 214"/><path d="M436 218 L510 212"/>
  </g>
  <g class="node">
    <circle cx="288" cy="40" r="3"/><circle cx="510" cy="58" r="3"/>
    <circle cx="140" cy="138" r="3"/><circle cx="214" cy="116" r="3"/>
    <circle cx="288" cy="142" r="3"/><circle cx="362" cy="118" r="3"/>
    <circle cx="436" cy="140" r="3"/><circle cx="510" cy="116" r="3"/>
    <circle cx="584" cy="140" r="3"/>
    <circle cx="140" cy="214" r="3"/><circle cx="177" cy="192" r="3"/>
    <circle cx="214" cy="218" r="3"/><circle cx="251" cy="194" r="3"/>
    <circle cx="288" cy="216" r="3"/><circle cx="325" cy="190" r="3"/>
    <circle cx="362" cy="214" r="3"/><circle cx="399" cy="196" r="3"/>
    <circle cx="473" cy="192" r="3"/><circle cx="510" cy="212" r="3"/>
    <circle cx="547" cy="196" r="3"/><circle cx="584" cy="216" r="3"/>
  </g>
  <circle class="node-open" cx="140" cy="62" r="4"/>
  <circle class="node-accent" cx="436" cy="218" r="4.5"/>
  <path class="flow" marker-end="url(#rec-a4)" d="M140 62 L288 40 L288 142 L362 118 L362 214 L399 196 L436 218"/>
  <g class="dim">
    <text class="lbl" x="0" y="34" font-size="9.5">LỚP TRÊN</text>
    <text x="0" y="48" font-size="10">ít điểm, cạnh dài</text>
    <text class="lbl" x="0" y="110" font-size="9.5">LỚP GIỮA</text>
    <text x="0" y="124" font-size="10">dày hơn, cạnh ngắn hơn</text>
    <text class="lbl" x="0" y="186" font-size="9.5">LỚP ĐÁY</text>
    <text x="0" y="200" font-size="10">đủ điểm, cạnh ngắn nhất</text>
    <text x="152" y="84" font-size="10">điểm vào</text>
    <text x="436" y="236" font-size="10" text-anchor="middle">đích</text>
  </g>
</svg>
<figcaption>Mỗi lần xuống một lớp, phạm vi còn phải xét lại thu nhỏ. Số lớp tăng theo lô-ga-rít của số điểm, nên số bước cũng vậy.</figcaption>
</figure>

### Tầng ba: tìm kiếm lai

Một truy vấn đi song song qua hai nhánh. Nhánh vector đưa truy vấn vào cùng không gian với nội dung rồi tìm lân cận. Nhánh từ khoá khớp chuỗi trên tiêu đề, tên nghệ sĩ và các nhãn. Hai nhánh cho ra hai danh sách, và một bước hợp điểm gộp lại cùng hai yếu tố phụ là độ phổ biến và độ mới.

Hệ thống hỗ trợ cả truy vấn bằng văn bản lẫn truy vấn bằng một đoạn âm thanh — trường hợp sau đi thẳng vào chỉ mục vector âm thanh.

### Tầng bốn: gợi ý nhiều nguồn

Ba nguồn ứng viên chạy độc lập rồi hợp lại.

**Dựa trên nội dung.** Lấy trung bình vector của những bài người dùng đã thích để tạo hồ sơ sở thích, rồi tìm lân cận của hồ sơ đó. Với người dùng mới chưa thích bài nào, hồ sơ được dựng từ các bài phổ biến nhất — một cách xử lý khởi đầu nguội đơn giản và rẻ.

**Lọc cộng tác.** Dùng thuật toán bình phương tối thiểu luân phiên trên ma trận tương tác. Ý tưởng: phân rã ma trận người dùng nhân nội dung thành tích của hai ma trận thừa số nhỏ hơn, rồi luân phiên cố định một bên để giải bên còn lại — mỗi bước là một bài bình phương tối thiểu có nghiệm đóng, nên hội tụ nhanh và song song hoá được.

<figure class="diagram">
<svg viewBox="0 0 640 170" role="img" aria-label="Ma trận tương tác thưa xấp xỉ bằng tích hai ma trận thừa số hẹp, giải bằng cách luân phiên cố định một bên rồi giải bên kia">
  <defs><marker id="rec-a5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="20" y="32">TƯƠNG TÁC</text>
    <text class="lbl" x="170" y="32">NGƯỜI DÙNG</text>
    <text class="lbl" x="228" y="66">NỘI DUNG</text>
    <text class="lbl" x="440" y="32">BƯỚC LUÂN PHIÊN</text>
  </g>
  <rect class="box" x="20" y="42" width="130" height="91"/>
  <g class="grid">
    <path d="M33 42 V133"/><path d="M46 42 V133"/><path d="M59 42 V133"/><path d="M72 42 V133"/>
    <path d="M85 42 V133"/><path d="M98 42 V133"/><path d="M111 42 V133"/><path d="M124 42 V133"/>
    <path d="M137 42 V133"/>
    <path d="M20 55 H150"/><path d="M20 68 H150"/><path d="M20 81 H150"/>
    <path d="M20 94 H150"/><path d="M20 107 H150"/><path d="M20 120 H150"/>
  </g>
  <g class="cell-on">
    <rect x="20" y="42" width="13" height="13"/><rect x="59" y="42" width="13" height="13"/>
    <rect x="111" y="42" width="13" height="13"/><rect x="85" y="55" width="13" height="13"/>
    <rect x="46" y="68" width="13" height="13"/><rect x="124" y="68" width="13" height="13"/>
    <rect x="72" y="81" width="13" height="13"/><rect x="137" y="81" width="13" height="13"/>
    <rect x="98" y="94" width="13" height="13"/><rect x="33" y="107" width="13" height="13"/>
    <rect x="111" y="107" width="13" height="13"/><rect x="46" y="120" width="13" height="13"/>
    <rect x="85" y="120" width="13" height="13"/>
  </g>
  <rect class="box-accent" x="178" y="42" width="26" height="91"/>
  <rect class="box-accent" x="228" y="74" width="130" height="26"/>
  <g class="grid">
    <path d="M191 42 V133"/>
    <path d="M178 55 H204"/><path d="M178 68 H204"/><path d="M178 81 H204"/>
    <path d="M178 94 H204"/><path d="M178 107 H204"/><path d="M178 120 H204"/>
    <path d="M241 74 V100"/><path d="M254 74 V100"/><path d="M267 74 V100"/><path d="M280 74 V100"/>
    <path d="M293 74 V100"/><path d="M306 74 V100"/><path d="M319 74 V100"/><path d="M332 74 V100"/>
    <path d="M345 74 V100"/><path d="M228 87 H358"/>
  </g>
  <g font-size="13" text-anchor="middle">
    <text x="164" y="92">≈</text>
    <text x="216" y="92">×</text>
  </g>
  <path class="flow" marker-end="url(#rec-a5)" d="M374 92 H428"/>
  <rect class="box" x="440" y="44" width="196" height="44"/>
  <rect class="box" x="440" y="110" width="196" height="44"/>
  <g class="flow" marker-end="url(#rec-a5)">
    <path d="M490 88 V104"/><path d="M586 110 V94"/>
  </g>
  <g font-size="11.5">
    <text x="450" y="64">Cố định V, giải U</text>
    <text x="450" y="78" font-size="10" class="dim">mỗi bước có nghiệm đóng</text>
    <text x="450" y="130">Cố định U, giải V</text>
    <text x="450" y="144" font-size="10" class="dim">rồi đổi vai hai bên</text>
  </g>
  <g class="dim" font-size="10">
    <text x="20" y="150">phần lớn ô còn trống</text>
    <text x="378" y="84">giải bằng</text>
    <text x="520" y="105" text-anchor="middle">luân phiên</text>
  </g>
</svg>
<figcaption>Hai ma trận thừa số cộng lại nhỏ hơn hẳn ma trận gốc, và chúng dày đặc — đó là chỗ những ô còn trống được điền vào.</figcaption>
</figure>

**Theo trình tự.** Một mạng transformer nhận chuỗi nội dung người dùng vừa tiêu thụ và dự đoán mục tiếp theo, có mặt nạ nhân quả để mỗi vị trí chỉ nhìn được về quá khứ.

Điểm chung của cả ba: chúng trả về ứng viên kèm điểm số, và một hàm hợp điểm tuyến tính gộp lại thành bảng xếp hạng cuối, cộng thêm độ phổ biến và độ mới.

### Tín hiệu ngầm: biến hành vi thành con số

Có một chi tiết thiết kế đáng mang đi nơi khác. Dữ liệu tương tác thô chỉ có các sự kiện rời rạc — phát, thích, bỏ thích. Trước khi đưa vào mô hình, mỗi sự kiện được quy về một trọng số thực theo vài quy tắc:

- Bỏ qua sớm, tức nghe chưa được bao nhiêu đã chuyển bài, mang **giá trị âm** — nó là tín hiệu không thích, chứ không phải trung tính.
- Nghe gần trọn được nhân thêm hệ số: tín hiệu tích cực mạnh hơn nghe nửa chừng.
- Tương tác tự tìm đến được đánh giá cao hơn tương tác đến từ gợi ý, vì nó phản ánh ý định chủ động.
- Tương tác gần đây có trọng số cao hơn tương tác cũ, giảm dần theo thời gian.

<figure class="diagram">
<svg viewBox="0 0 640 256" role="img" aria-label="Thang trọng số liên tục có phần âm: bỏ qua sớm nằm bên âm, các mức nghe nằm bên dương, kèm đường suy giảm theo thời gian">
  <defs><marker id="rec-a6" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-warn" x="40" y="92" width="130" height="16"/>
  <rect class="box-ok" x="170" y="92" width="434" height="16"/>
  <path class="axis" d="M170 84 V116"/>
  <text class="num" x="170" y="128" text-anchor="middle">0</text>
  <g class="edge">
    <path d="M88 100 V70"/><path d="M224 100 V70"/><path d="M386 100 V70"/>
    <path d="M468 100 V134"/><path d="M560 100 V134"/>
  </g>
  <g class="node">
    <circle cx="88" cy="100" r="3.5"/><circle cx="224" cy="100" r="3.5"/>
    <circle cx="386" cy="100" r="3.5"/><circle cx="468" cy="100" r="3.5"/>
    <circle cx="560" cy="100" r="3.5"/>
  </g>
  <path class="flow" marker-end="url(#rec-a6)" d="M476 120 H552"/>
  <path class="axis" d="M40 190 V232 H248"/>
  <path class="curve" d="M42 194 C 92 216, 152 228, 244 230"/>
  <g class="dim" font-size="9.5">
    <text class="lbl" x="40" y="34">TRỌNG SỐ MỘT SỰ KIỆN</text>
    <text class="lbl" x="40" y="86">ÂM</text>
    <text class="lbl" x="600" y="86" text-anchor="end">DƯƠNG</text>
    <text class="lbl" x="40" y="180">SUY GIẢM THEO THỜI GIAN</text>
  </g>
  <g font-size="11.5" text-anchor="middle">
    <text x="88" y="64">bỏ qua sớm</text>
    <text x="224" y="64">nghe nửa chừng</text>
    <text x="386" y="64">nghe gần trọn</text>
    <text x="468" y="148">đến từ gợi ý</text>
    <text x="560" y="148">tự tìm đến</text>
  </g>
  <g class="dim" font-size="10">
    <text x="514" y="114" text-anchor="middle">cao hơn</text>
    <text x="40" y="246">gần đây</text>
    <text x="248" y="246" text-anchor="end">lâu rồi</text>
    <text x="264" y="216">cùng hành vi, càng cũ càng nhẹ</text>
  </g>
</svg>
<figcaption>Bảng đã thích hay chưa chỉ có hai giá trị. Thang này liên tục, có phần âm, và còn nhạt dần khi sự kiện lùi về quá khứ.</figcaption>
</figure>

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

<figure class="diagram">
<svg viewBox="0 0 640 260" role="img" aria-label="Phễu bốn mức thu hẹp dần: toàn bộ danh mục, sinh ứng viên, chấm điểm, sắp xếp lại, mỗi mức tối ưu cho một mục tiêu khác nhau">
  <defs><marker id="rec-a7" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-soft" x="20" y="30" width="320" height="30"/>
  <rect class="box" x="58" y="76" width="244" height="56"/>
  <rect class="box" x="94" y="148" width="172" height="42"/>
  <rect class="box-accent" x="118" y="206" width="124" height="42"/>
  <g class="flow" marker-end="url(#rec-a7)">
    <path d="M180 60 V72"/><path d="M180 132 V144"/><path d="M180 190 V202"/>
  </g>
  <g font-size="11.5">
    <text x="30" y="50">Toàn bộ danh mục</text>
    <text x="68" y="96">Sinh ứng viên</text>
    <text x="68" y="110" font-size="10" class="dim">nhiều bộ sinh chạy song song</text>
    <text x="68" y="124" font-size="10" class="dim">rẻ, thiên về độ phủ</text>
    <text x="104" y="168">Chấm điểm</text>
    <text x="104" y="182" font-size="10" class="dim">đắt, giàu đặc trưng</text>
    <text x="128" y="226">Sắp xếp lại</text>
    <text x="128" y="240" font-size="10" class="dim">quy tắc nghiệp vụ</text>
  </g>
  <g class="dim" font-size="10">
    <text x="192" y="143">còn một tập nhỏ</text>
    <text x="192" y="201">còn nhỏ hơn nữa</text>
    <text x="256" y="232">danh sách cuối</text>
  </g>
  <g class="dim">
    <text class="lbl" x="368" y="98" font-size="9.5">TỐI ƯU CHO ĐỘ PHỦ</text>
    <text x="368" y="112" font-size="10">thà thừa còn hơn bỏ sót</text>
    <text class="lbl" x="368" y="163" font-size="9.5">TỐI ƯU CHO ĐỘ CHÍNH XÁC</text>
    <text x="368" y="177" font-size="10">xếp đúng thứ tự</text>
    <text class="lbl" x="368" y="221" font-size="9.5">TỐI ƯU CHO TRẢI NGHIỆM</text>
    <text x="368" y="235" font-size="10">đa dạng, lọc đã xem, khám phá</text>
  </g>
</svg>
<figcaption>Mỗi tầng đổi độ phủ lấy độ chính xác. Chia tầng còn cho phép đo riêng từng khúc, nhờ đó biết khúc nào đang là nút thắt.</figcaption>
</figure>

Việc chia tầng không chỉ để nhanh. Nó còn cho phép cải thiện từng phần độc lập, và cho phép đo xem tầng nào đang là nút thắt.

**Hai họ mô hình cho hai tầng.** Phân rã ma trận nhanh và rẻ nhưng không dùng được đặc trưng ngoài định danh. Mạng hai tháp — một tháp mã hoá người dùng, một tháp mã hoá nội dung, cùng chiếu vào một không gian — nhận được đặc trưng phong phú và xử lý người dùng mới tốt hơn, đổi lại tốn kém hơn. Cách ghép thường thấy là dùng mô hình nhẹ ở tầng sinh ứng viên và mô hình nặng ở tầng chấm điểm.

**Chỉ số ngoại tuyến phải nối được với hành vi thật.** Các chỉ số xếp hạng như nDCG tính đến vị trí: một kết quả đúng ở hạng nhất giá trị hơn cùng kết quả đó ở hạng mười. Bên cạnh đó là các chỉ số trực tuyến — tỷ lệ nhấp, thời gian xem, tỷ lệ hoàn thành. Điều quan trọng là chọn chỉ số ngoại tuyến nào dự báo tốt cho chỉ số trực tuyến mà tổ chức thực sự quan tâm.

Một biến thể đáng chú ý là entropy chéo chuẩn hoá: nó chia hiệu năng mô hình cho hiệu năng của baseline luôn dự đoán tỷ lệ trung bình. Giá trị lớn hơn một nghĩa là mô hình tệ hơn baseline — chỉ số này tự phơi bày thất bại thay vì để người đọc phải suy ra.

**Tìm kiếm xuyên phương thức cần không gian chung.** Muốn truy vấn bằng văn bản chạm tới nội dung âm thanh, hai bên phải nằm trong cùng một không gian vector, và điều đó chỉ có được khi mô hình được huấn luyện tương phản trên các cặp văn bản–âm thanh. Đặt cạnh nhau hai bộ mã hoá riêng biệt rồi cộng điểm không tạo ra khả năng đó — nó chỉ cho phép so văn bản với phần văn bản mô tả nội dung, đúng như cách hệ thống ở trên hoạt động.

## Vài điều rút ra

**Bước biến sự kiện thành tín hiệu quan trọng hơn vẻ ngoài của nó.** Công thức quy đổi tương tác thành trọng số — phân biệt bỏ qua với nghe trọn, tự tìm với được gợi ý, gần đây với đã lâu — là phần mang lại nhiều giá trị nhất trên mỗi dòng mã trong toàn hệ thống.

**Ghép nhiều nguồn điểm cần chuẩn hoá trước khi cộng.** Điểm từ ba nguồn thường có thang đo hoàn toàn khác nhau: một bên là tương đồng nằm trong khoảng đơn vị, một bên là tích vô hướng không chặn, một bên là xác suất trên hàng nghìn lớp nên luôn rất nhỏ. Cộng thẳng có trọng số sẽ khiến nguồn có thang nhỏ gần như không đóng góp gì, dù trọng số danh nghĩa không nhỏ. Chuẩn hoá về cùng thang, hoặc hợp nhất theo thứ hạng, là bước bắt buộc.

<figure class="diagram">
<svg viewBox="0 0 640 212" role="img" aria-label="Ba nguồn điểm trên cùng một trục: cột xác suất gần như biến mất khi cộng thẳng, và cân bằng lại sau khi chuẩn hoá">
  <defs><marker id="rec-a8" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect class="box-warn" x="2" y="24" width="302" height="176"/>
  <rect class="box-ok" x="336" y="24" width="302" height="176"/>
  <g class="axis">
    <path d="M12 170 H294"/><path d="M346 170 H628"/>
  </g>
  <g class="bar">
    <rect x="44" y="159" width="40" height="11"/>
    <rect x="124" y="52" width="40" height="118"/>
    <rect x="378" y="76" width="40" height="94"/>
    <rect x="458" y="58" width="40" height="112"/>
  </g>
  <g class="bar-accent">
    <rect x="204" y="168" width="40" height="2"/>
    <rect x="538" y="90" width="40" height="80"/>
  </g>
  <path class="flow" marker-end="url(#rec-a8)" d="M308 112 H332"/>
  <g class="dim">
    <text class="lbl" x="12" y="42" font-size="9.5">CỘNG THẲNG</text>
    <text x="12" y="56" font-size="10">ba thang khác hẳn nhau</text>
    <text class="lbl" x="346" y="42" font-size="9.5">CHUẨN HOÁ TRƯỚC</text>
    <text x="346" y="56" font-size="10">hoặc hợp nhất theo hạng</text>
    <text x="224" y="158" font-size="10" text-anchor="middle">gần như biến mất</text>
  </g>
  <g font-size="10" text-anchor="middle">
    <text x="64" y="186">tương đồng cosin</text>
    <text x="144" y="186">tích vô hướng</text>
    <text x="224" y="186">xác suất</text>
    <text x="398" y="186">tương đồng cosin</text>
    <text x="478" y="186">tích vô hướng</text>
    <text x="558" y="186">xác suất</text>
  </g>
</svg>
<figcaption>Trọng số danh nghĩa không quyết định đóng góp thật; thang đo mới quyết định. Chuẩn hoá là bước trả quyền đó lại cho trọng số.</figcaption>
</figure>

**Thước đo khoảng cách phải khớp với cách vector được tạo ra.** Chỉ mục lân cận mặc định thường dùng khoảng cách Euclid, trong khi phần lớn biểu diễn ngữ nghĩa được thiết kế để so bằng cosin. Nếu không chuẩn hoá độ dài vector trước khi lập chỉ mục, thứ hạng sẽ bị chi phối bởi độ dài chứ không chỉ bởi hướng.

**Sinh biểu diễn nên đi trước mọi thứ khác.** Trong chuỗi bốn tầng, ba tầng sau đều đọc chỉ mục do tầng hai tạo ra. Khi dựng lại một hệ thống tương tự, đây là thứ tự bắt buộc — và cũng là chỗ đáng đầu tư nhất, vì chất lượng biểu diễn đặt trần cho mọi thứ phía sau.
