---
title: "Chống giả mạo khuôn mặt: nhận ra người thật trước ống kính"
description: "Bốn hướng kiến trúc cho bài toán phát hiện tấn công giả mạo khuôn mặt, cơ chế tách phong cách khỏi nội dung, và cách ngành chuẩn hoá việc đo lường."
lang: "vi"
order: 2
field: "PAD"
topics: ["chống giả mạo", "domain generalization", "hiệu chỉnh ngưỡng", "ISO/IEC 30107-3", "biometrics"]
---

Một hệ thống nhận diện khuôn mặt trả lời câu hỏi "người này là ai". Nó không trả lời câu hỏi đứng trước đó: thứ đang ở trước ống kính có phải một con người thật hay không. Chỉ cần giơ một tấm ảnh in, một chiếc điện thoại đang phát video quay sẵn, hoặc một chiếc mặt nạ ra trước camera là phần nhận diện phía sau vẫn làm việc bình thường — nó vốn không được thiết kế để nghi ngờ. Lĩnh vực lấp chỗ trống đó có tên chuẩn trong tài liệu quốc tế: *presentation attack detection*, viết tắt là PAD.

Nhìn từ xa, đây là một bài phân loại nhị phân: đưa ảnh vào, trả lời live hay spoof. Nhưng nó khác mọi bài phân loại nhị phân thông thường ở một điểm quyết định: phía bên kia là người, và người đó chủ động tìm cách vượt qua. Không có gì buộc kẻ tấn công phải dùng đúng loại tấn công đã có trong tập huấn luyện, đúng chiếc máy in ấy, đúng chiếc màn hình ấy. Cũng không có gì bảo đảm camera nơi triển khai giống camera đã dùng để thu dữ liệu.

Bài này mô tả một hệ thống đã dựng cho bài toán đó: các hướng kiến trúc được thử song song, cơ chế được thiết kế riêng để mô hình không bám vào thiết bị cụ thể, và cách lĩnh vực này đã chuẩn hoá việc đo lường.

## Hệ thống đã dựng

Đầu vào chung cho mọi hướng là ảnh khuôn mặt đã được cắt ra bằng một face detector và chuẩn hoá về kích thước cố định. Đầu ra là một quyết định nhị phân: live hay spoof. Vì chưa rõ trước họ kiến trúc nào phù hợp với bài toán, hệ thống được dựng thành bốn hướng tiếp cận chạy song song, dùng chung pipeline dữ liệu và chung protocol đánh giá để kết quả giữa chúng so được với nhau.

<figure class="diagram">
<svg viewBox="0 0 640 258" role="img" aria-label="Bốn hướng kiến trúc chạy song song trên cùng một pipeline dữ liệu và cùng một protocol đánh giá">
  <defs><marker id="pad-a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">ĐẦU VÀO CHUNG CHO CẢ BỐN HƯỚNG</text>
  <rect class="box" x="145" y="22" width="350" height="44"/>
  <g text-anchor="middle">
    <text x="320" y="42" font-size="11.5">Ảnh khuôn mặt đã cắt và chuẩn hoá</text>
    <text x="320" y="58" font-size="10.5" class="dim">Một pipeline dữ liệu dùng chung</text>
  </g>
  <g class="flow"><path d="M320 66 V78"/><path d="M74 78 H566"/></g>
  <g class="flow" marker-end="url(#pad-a2)">
    <path d="M74 78 V94"/><path d="M238 78 V94"/><path d="M402 78 V94"/><path d="M566 78 V94"/>
  </g>
  <rect class="box" x="0" y="96" width="148" height="72"/>
  <rect class="box" x="164" y="96" width="148" height="72"/>
  <rect class="box" x="328" y="96" width="148" height="72"/>
  <rect class="box" x="492" y="96" width="148" height="72"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="74" y="118">Tích chập + chú ý</text>
    <text x="238" y="118">Vision Transformer</text>
    <text x="402" y="118">GAN + nhánh phụ</text>
    <text x="566" y="118">Tách phong cách</text>
  </g>
  <g text-anchor="middle" font-size="10" class="dim">
    <text x="74" y="136">CBAM chèn sau</text>
    <text x="74" y="150">mỗi nhóm khối</text>
    <text x="238" y="136">Đóng băng hoặc</text>
    <text x="238" y="150">tinh chỉnh backbone</text>
    <text x="402" y="136">Nhánh phụ mới là</text>
    <text x="402" y="150">bộ phân loại thật</text>
    <text x="566" y="136">Cài từ đầu, nhắm</text>
    <text x="566" y="150">tổng quát hoá miền</text>
  </g>
  <g class="flow"><path d="M74 168 V182"/><path d="M238 168 V182"/><path d="M402 168 V182"/><path d="M566 168 V182"/><path d="M74 182 H566"/></g>
  <g class="flow" marker-end="url(#pad-a2)"><path d="M320 182 V198"/></g>
  <rect class="box-accent" x="100" y="200" width="440" height="48"/>
  <g text-anchor="middle">
    <text x="320" y="220" font-size="11.5">Chung protocol đánh giá cho cả bốn hướng</text>
    <text x="320" y="236" font-size="10.5" class="dim">Nhờ đó bốn kết quả mới so được với nhau</text>
  </g>
</svg>
<figcaption>Bốn hướng chỉ so được với nhau khi chúng chia sẻ đúng hai thứ: đường dữ liệu đi vào và cách đo ở đầu ra.</figcaption>
</figure>

### Hướng một: mạng tích chập kèm cơ chế chú ý

Backbone là một mạng tích chập đã huấn luyện sẵn trên tập ảnh lớn, dùng cả biến thể nặng cho trường hợp không giới hạn tài nguyên lẫn biến thể nhẹ hướng tới thiết bị di động.

Điểm bổ sung là khối chú ý CBAM chèn sau mỗi nhóm khối của backbone. CBAM gồm hai phần nối tiếp. Phần chú ý theo kênh gộp bản đồ đặc trưng theo trục không gian bằng cả trung bình lẫn cực đại, đưa hai vector thu được qua một MLP dùng chung, cộng lại rồi qua sigmoid để ra trọng số cho từng kênh. Phần chú ý theo không gian gộp theo trục kênh, đưa qua một lớp tích chập 7x7 rồi sigmoid để ra trọng số cho từng vị trí. Ý tưởng là để mạng tự học xem kênh nào và vùng ảnh nào đáng chú ý, thay vì đối xử đồng đều với toàn bộ bản đồ đặc trưng.

<figure class="diagram">
<svg viewBox="0 0 640 208" role="img" aria-label="CBAM gồm hai bước chú ý nối tiếp: chú ý theo kênh rồi chú ý theo không gian">
  <defs><marker id="pad-a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="lbl dim" font-size="9.5">
    <text x="104" y="30">BƯỚC 1 — CHÚ Ý THEO KÊNH</text>
    <text x="334" y="30">BƯỚC 2 — CHÚ Ý THEO KHÔNG GIAN</text>
  </g>
  <rect class="box-soft" x="0" y="76" width="88" height="62"/>
  <rect class="box" x="104" y="40" width="214" height="134"/>
  <rect class="box" x="334" y="40" width="214" height="134"/>
  <rect class="box-soft" x="564" y="76" width="76" height="62"/>
  <g text-anchor="middle" font-size="10.5">
    <text x="44" y="96">Bản đồ</text>
    <text x="44" y="110">đặc trưng</text>
    <text x="44" y="124">đầu vào</text>
    <text x="602" y="96">Đặc trưng</text>
    <text x="602" y="110">đã đánh</text>
    <text x="602" y="124">trọng số</text>
  </g>
  <rect class="box" x="116" y="50" width="190" height="24"/>
  <rect class="box" x="116" y="80" width="190" height="24"/>
  <rect class="box" x="116" y="110" width="190" height="24"/>
  <rect class="box-accent" x="116" y="140" width="190" height="24"/>
  <rect class="box" x="346" y="50" width="190" height="24"/>
  <rect class="box" x="346" y="80" width="190" height="24"/>
  <rect class="box" x="346" y="110" width="190" height="24"/>
  <rect class="box-accent" x="346" y="140" width="190" height="24"/>
  <g text-anchor="middle" font-size="10.5">
    <text x="211" y="66">Gộp theo trục không gian</text>
    <text x="211" y="96">bằng trung bình và cực đại</text>
    <text x="211" y="126">MLP dùng chung rồi cộng</text>
    <text x="211" y="156">Trọng số cho từng kênh</text>
    <text x="441" y="66">Gộp theo trục kênh</text>
    <text x="441" y="96">bằng trung bình và cực đại</text>
    <text x="441" y="126">Tích chập 7x7 rồi sigmoid</text>
    <text x="441" y="156">Trọng số cho từng vị trí</text>
  </g>
  <g class="flow" marker-end="url(#pad-a3)">
    <path d="M88 107 H104"/><path d="M318 107 H334"/><path d="M548 107 H564"/>
    <path d="M211 74 V80"/><path d="M211 104 V110"/><path d="M211 134 V140"/>
    <path d="M441 74 V80"/><path d="M441 104 V110"/><path d="M441 134 V140"/>
  </g>
  <text x="0" y="194" font-size="10.5" class="dim">Hai bước nối tiếp: chọn kênh nào đáng chú ý trước, rồi chọn vùng ảnh nào đáng chú ý.</text>
</svg>
<figcaption>Mỗi bước gộp bỏ đúng một trục để hỏi một câu: bước đầu bỏ trục không gian để hỏi về kênh, bước sau bỏ trục kênh để hỏi về vị trí.</figcaption>
</figure>

Đầu phân loại đặt sau backbone gồm: gộp trung bình toàn cục, dropout, một lớp tuyến tính trung gian, chuẩn hoá batch, ReLU, rồi một lớp tuyến tính cuối trả về một logit duy nhất.

### Hướng hai: Vision Transformer

Hướng này thay backbone tích chập bằng một Vision Transformer đã huấn luyện sẵn, có cả bản đầy đủ và bản rất nhẹ. Ảnh được chia thành các patch, và biểu diễn dùng cho phân loại lấy từ token CLS, gắn vào một đầu phân loại tương tự hướng một.

Hướng này có thêm một chế độ đóng băng toàn bộ backbone và chỉ huấn luyện phần đầu. Cách làm đó rẻ và hợp lý khi dữ liệu ít, nhưng đi kèm một đánh đổi được bàn ở phần kiến thức nền phía dưới.

### Hướng ba: GAN với nhánh phân loại phụ

Hướng này dùng một mạng đối sinh. Bộ sinh theo kiểu DCGAN: từ một vector ẩn đi qua chuỗi lớp upsample và tích chập để dựng ra ảnh. Bộ phân biệt có bốn khối tích chập stride 2, có chèn CBAM, rồi tách thành hai nhánh — một nhánh phán đoán ảnh thật hay do bộ sinh tạo ra, phục vụ phần đối kháng; một nhánh phụ phân loại live/spoof.

<figure class="diagram">
<svg viewBox="0 0 640 236" role="img" aria-label="Bộ phân biệt tách thành nhánh đối kháng và nhánh phụ, trong đó nhánh phụ mới là bộ phân loại được dùng thật">
  <defs><marker id="pad-a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="26" font-size="9.5">ĐƯỜNG ĐI CỦA ẢNH VÀO BỘ PHÂN BIỆT</text>
  <rect class="box" x="0" y="36" width="112" height="36"/>
  <rect class="box" x="128" y="36" width="112" height="36"/>
  <rect class="box" x="256" y="36" width="148" height="36"/>
  <rect class="box-soft" x="256" y="94" width="148" height="36"/>
  <rect class="box" x="430" y="36" width="210" height="94"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="56" y="58">Vector ẩn</text>
    <text x="184" y="58">Bộ sinh</text>
    <text x="330" y="58">Ảnh do bộ sinh tạo</text>
    <text x="330" y="116">Ảnh thật</text>
  </g>
  <text x="442" y="58" font-size="11.5">Bộ phân biệt</text>
  <g font-size="10" class="dim">
    <text x="442" y="78">Bốn khối tích chập stride 2,</text>
    <text x="442" y="92">có chèn CBAM</text>
    <text x="442" y="106">rồi tách thành hai nhánh</text>
  </g>
  <g font-size="10.5" class="dim">
    <text x="0" y="104">Ảnh thật đi kèm nhãn</text>
    <text x="0" y="118">live hay spoof</text>
  </g>
  <g class="flow" marker-end="url(#pad-a4)">
    <path d="M112 54 H128"/><path d="M240 54 H256"/><path d="M404 54 H430"/><path d="M404 112 H430"/>
    <path d="M342 146 V160"/><path d="M544 146 V160"/>
  </g>
  <g class="flow"><path d="M535 130 V146"/><path d="M342 146 H544"/></g>
  <text class="lbl dim" x="0" y="152" font-size="9.5">HAI ĐẦU RA CỦA BỘ PHÂN BIỆT</text>
  <rect class="box" x="252" y="160" width="180" height="64"/>
  <rect class="box-accent" x="448" y="160" width="192" height="64"/>
  <g text-anchor="middle">
    <text x="342" y="180" font-size="11.5">Nhánh đối kháng</text>
    <text x="342" y="198" font-size="10" class="dim">Thật hay do bộ sinh tạo?</text>
    <text x="342" y="212" font-size="10" class="dim">Chỉ là tín hiệu bổ trợ</text>
    <text x="544" y="180" font-size="11.5">Nhánh phụ</text>
    <text x="544" y="198" font-size="10" class="dim">Live hay spoof?</text>
    <text x="544" y="212" font-size="10" class="dim">Bộ phân loại dùng thật</text>
  </g>
</svg>
<figcaption>Ảnh sinh ra không phải mục tiêu. Phần đối kháng chỉ tồn tại để ép bộ phân biệt học một biểu diễn giàu thông tin cho nhánh bên cạnh dùng.</figcaption>
</figure>

Chi tiết đáng chú ý là chính nhánh phụ mới là bộ phân loại dùng thật. Phần đối kháng ở đây đóng vai trò tín hiệu huấn luyện bổ trợ, buộc bộ phân biệt học biểu diễn giàu thông tin về ảnh khuôn mặt, chứ bản thân ảnh sinh ra không phải mục tiêu. Phần đối kháng được huấn luyện theo Wasserstein GAN có phạt gradient, một biến thể chọn vì ổn định hơn so với công thức đối kháng nguyên bản.

### Hướng bốn: tách phong cách khỏi nội dung

Ba hướng trên đều bắt đầu từ một kiến trúc có sẵn. Hướng thứ tư đi ngược lại: cài lại từ đầu một mạng được thiết kế riêng cho mục tiêu domain generalization, tức khả năng hoạt động trên nguồn dữ liệu chưa từng thấy.

Ý tưởng nền là tách trong ảnh hai thành phần: "nội dung" — thứ nói lên ảnh này là người thật hay bản sao chép; và "phong cách" — thứ phản ánh camera nào, ánh sáng nào, hậu kỳ nào. Mục tiêu là buộc biểu diễn nội dung độc lập với phong cách.

Cấu trúc gồm các phần sau:

- Một bộ trích đặc trưng nhiều tầng tự thiết kế, không dùng backbone pretrained.
- Một nhánh trích nội dung và một nhánh trích phong cách. Nhánh phong cách đi qua chuẩn hoá theo thực thể rồi vài lớp fully-connected để sinh ra hai tham số: hệ số tỷ lệ và hệ số dịch chuyển.
- Một bước ghép lại bằng AdaIN, tức chuẩn hoá thực thể thích ứng: chuẩn hoá đặc trưng nội dung về trung bình không và phương sai đơn vị, rồi áp hai tham số phong cách vào.

Cơ chế cốt lõi nằm ở cách sinh cặp dữ liệu để học. Trong mỗi batch, thứ tự mẫu được xáo trộn để ghép phong cách của ảnh này với nội dung của ảnh khác. Cặp lai đó mang nhãn dương nếu hai ảnh gốc cùng lớp live/spoof, và nhãn âm nếu khác lớp. Hàm mất mát tương phản trên các cặp này ép mạng đưa những ảnh cùng lớp lại gần nhau bất kể chúng đến từ thiết bị nào — đúng thứ cần có khi triển khai lên phần cứng lạ.

<figure class="diagram">
<svg viewBox="0 0 640 280" role="img" aria-label="Đặc trưng tách thành nội dung và phong cách, ghép lại bằng AdaIN, và cặp lai sinh ra từ việc xáo trộn thứ tự mẫu trong batch">
  <defs><marker id="pad-a5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">TÁCH NỘI DUNG KHỎI PHONG CÁCH</text>
  <rect class="box-soft" x="0" y="58" width="104" height="30"/>
  <rect class="box" x="120" y="49" width="132" height="48"/>
  <rect class="box" x="268" y="35" width="150" height="30"/>
  <rect class="box" x="268" y="81" width="150" height="30"/>
  <rect class="box" x="434" y="20" width="206" height="60"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="52" y="77">Ảnh đầu vào</text>
    <text x="186" y="69">Bộ trích</text>
    <text x="186" y="85">đặc trưng</text>
    <text x="343" y="54">Nhánh phong cách</text>
    <text x="343" y="100">Nhánh nội dung</text>
  </g>
  <text x="446" y="40" font-size="11.5">Chuẩn hoá thực thể</text>
  <g font-size="10" class="dim">
    <text x="446" y="56">rồi vài lớp fully-connected</text>
    <text x="446" y="70">sinh ra tỷ lệ và dịch chuyển</text>
  </g>
  <g class="flow"><path d="M252 73 H262"/><path d="M262 50 V96"/></g>
  <g class="flow" marker-end="url(#pad-a5)">
    <path d="M104 73 H120"/><path d="M262 50 H268"/><path d="M262 96 H268"/><path d="M418 50 H434"/>
    <path d="M343 111 V130"/><path d="M537 80 V130"/><path d="M370 192 V212"/>
  </g>
  <text class="lbl dim" x="0" y="126" font-size="9.5">GHÉP LẠI BẰNG AdaIN</text>
  <rect class="box" x="180" y="130" width="380" height="62"/>
  <text x="192" y="150" font-size="11.5">AdaIN: chuẩn hoá đặc trưng nội dung</text>
  <g font-size="10.5" class="dim">
    <text x="192" y="166">về trung bình không và phương sai đơn vị,</text>
    <text x="192" y="180">rồi áp tỷ lệ và dịch chuyển của phong cách vào</text>
  </g>
  <text class="lbl dim" x="0" y="206" font-size="9.5">XÁO TRỘN TRONG BATCH</text>
  <rect class="box-accent" x="0" y="212" width="640" height="60"/>
  <text x="12" y="232" font-size="11.5">Xáo trộn thứ tự mẫu trong batch: phong cách ảnh này ghép vào nội dung ảnh khác</text>
  <g font-size="10.5" class="dim">
    <text x="12" y="248">Cặp lai mang nhãn dương nếu hai ảnh gốc cùng lớp live/spoof, nhãn âm nếu khác lớp</text>
    <text x="12" y="262">Hàm mất mát tương phản trên các cặp này kéo ảnh cùng lớp lại gần nhau bất kể thiết bị nào</text>
  </g>
</svg>
<figcaption>Việc xáo trộn tạo ra những mẫu không tồn tại trong dữ liệu: cùng một nội dung mang phong cách của một thiết bị khác. Đó là cách nói với mạng rằng thiết bị không phải thứ cần học.</figcaption>
</figure>

Hai chi tiết nữa. Đầu ra không phải một logit đơn mà là một bản đồ độ sâu dựng qua các lớp upsample: mặt người thật có cấu trúc ba chiều, còn ảnh in hay màn hình phát lại về bản chất là mặt phẳng, nên độ sâu là tín hiệu giám sát giàu thông tin hơn một nhãn nhị phân. Và có thêm một nhánh phân biệt miền nối qua lớp đảo gradient: nhánh này cố đoán mẫu đến từ nguồn dữ liệu nào, còn lớp đảo gradient khiến phần trích đặc trưng bị đẩy theo hướng ngược lại, tức học biểu diễn mà nhánh kia không đoán nổi nguồn.

<figure class="diagram">
<svg viewBox="0 0 640 148" role="img" aria-label="Lớp đảo gradient để đặc trưng đi qua nguyên vẹn ở chiều thuận và đổi dấu gradient ở chiều ngược">
  <defs><marker id="pad-a6" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <text class="lbl dim" x="0" y="14" font-size="9.5">ĐI QUA THÌ NGUYÊN VẸN, QUAY LẠI THÌ ĐỔI DẤU</text>
  <rect class="box" x="0" y="30" width="150" height="56"/>
  <rect class="box-accent" x="245" y="30" width="150" height="56"/>
  <rect class="box" x="490" y="30" width="150" height="56"/>
  <g text-anchor="middle" font-size="11.5">
    <text x="75" y="50">Bộ trích</text>
    <text x="75" y="66">đặc trưng</text>
    <text x="320" y="50">Lớp đảo</text>
    <text x="320" y="66">gradient</text>
    <text x="565" y="50">Nhánh phân biệt</text>
    <text x="565" y="66">miền</text>
  </g>
  <g class="flow" marker-end="url(#pad-a6)">
    <path d="M150 46 H245"/><path d="M395 46 H490"/>
    <path d="M245 70 H150"/><path d="M490 70 H395"/>
  </g>
  <g text-anchor="middle" font-size="10" class="dim">
    <text x="197" y="40">chiều thuận</text>
    <text x="442" y="40">chiều thuận</text>
    <text x="197" y="84">chiều ngược</text>
    <text x="442" y="84">chiều ngược</text>
  </g>
  <text text-anchor="middle" x="320" y="108" font-size="10.5" class="dim">Ở lớp này, gradient chiều ngược bị nhân với một số âm.</text>
  <text x="0" y="130" font-size="10.5" class="dim">Bộ trích đặc trưng vì thế bị đẩy theo hướng làm nhánh phân biệt miền không đoán nổi mẫu đến từ nguồn nào.</text>
</svg>
<figcaption>Cả hai nhánh cùng tối ưu một hàm mất mát, nhưng dấu đảo khiến chúng kéo về hai phía ngược nhau — đó là toàn bộ mẹo của cơ chế này.</figcaption>
</figure>

Hàm mất mát tổng là tổng có trọng số của ba thành phần: phân loại, tương phản phong cách, và đối kháng miền.

### Dữ liệu và xử lý mất cân bằng

Hệ thống huấn luyện trên nhiều bộ dữ liệu khác nhau: một bộ tự thu thập, cùng các benchmark công khai gồm một bộ quy mô lớn có cả tấn công phát lại video, một bộ tập trung vào ảnh in, và một bộ dạng video đến từ một cuộc thi trong lĩnh vực. Có thêm một bộ bổ sung chỉ chứa ảnh người thật, dùng để bù lại việc mẫu tấn công thường nhiều hơn mẫu thật — tạo một mẫu tấn công rẻ hơn nhiều so với thu thập một khuôn mặt thật mới.

Phần mất cân bằng còn lại được xử lý trong hàm mất mát nhị phân bằng trọng số cho lớp dương, tính động từ tỷ lệ lớp thực tế của tập huấn luyện thay vì đặt cứng một con số.

### Protocol đánh giá

Hệ thống định nghĩa bốn kịch bản đánh giá, xếp theo mức độ khó tăng dần:

1. Huấn luyện và kiểm tra trong cùng một bộ dữ liệu.
2. Huấn luyện trên hỗn hợp nhiều bộ, kiểm tra trên phần giữ lại của hỗn hợp đó.
3. Huấn luyện trên vài bộ, kiểm tra trên một bộ hoàn toàn khác.
4. Kịch bản domain generalization: huấn luyện trên nhiều nguồn, kiểm tra trên nguồn chưa từng thấy.

Việc tách bốn kịch bản thay vì báo cáo một con số cho phép nhìn thấy khoảng cách giữa chúng, và chính khoảng cách đó mới là thông tin về khả năng dùng được ngoài thực tế.

<figure class="diagram">
<svg viewBox="0 0 640 262" role="img" aria-label="Bốn kịch bản đánh giá xếp thành bậc thang theo độ khó tăng dần, từ trong cùng một bộ dữ liệu đến nguồn chưa từng thấy">
  <defs><marker id="pad-a7" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="lbl dim" font-size="9.5">
    <text x="480" y="44">NẤC 4</text>
    <text x="320" y="80">NẤC 3</text>
    <text x="160" y="116">NẤC 2</text>
    <text x="0" y="152">NẤC 1</text>
  </g>
  <g font-size="10">
    <text x="480" y="60">Huấn luyện: nhiều nguồn</text>
    <text x="480" y="74">Kiểm tra: nguồn chưa thấy</text>
    <text x="320" y="96">Huấn luyện: vài bộ</text>
    <text x="320" y="110">Kiểm tra: một bộ khác hẳn</text>
    <text x="160" y="132">Huấn luyện: hỗn hợp bộ</text>
    <text x="160" y="146">Kiểm tra: phần giữ lại</text>
    <text x="0" y="168">Huấn luyện: một bộ</text>
    <text x="0" y="182">Kiểm tra: cùng bộ đó</text>
  </g>
  <rect class="box-accent" x="480" y="88" width="160" height="12"/>
  <rect class="box" x="320" y="124" width="160" height="12"/>
  <rect class="box" x="160" y="160" width="160" height="12"/>
  <rect class="box-soft" x="0" y="196" width="160" height="12"/>
  <g class="edge"><path d="M160 196 V172"/><path d="M320 160 V136"/><path d="M480 124 V100"/></g>
  <g class="flow" marker-end="url(#pad-a7)"><path d="M164 222 H630"/></g>
  <text class="lbl dim" x="0" y="226" font-size="9.5">ĐỘ KHÓ TĂNG DẦN</text>
  <text x="0" y="250" font-size="10.5" class="dim">Thông tin nằm ở khoảng cách giữa các nấc, không nằm ở kết quả của nấc dễ nhất.</text>
</svg>
<figcaption>Mỗi nấc bỏ đi một điều kiện mà nấc dưới còn được hưởng. Nấc trên cùng không cho mô hình làm quen trước với bất cứ thứ gì.</figcaption>
</figure>

## Kiến thức nền

<figure class="diagram">
<svg viewBox="0 0 640 200" role="img" aria-label="Khoảng cách giữa phân phối lúc huấn luyện và lúc triển khai">
  <defs><marker id="pad-a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <g class="dim">
    <text class="lbl" x="0" y="14" font-size="9.5">MIỀN NGUỒN — LÚC HUẤN LUYỆN</text>
    <text class="lbl" x="368" y="14" font-size="9.5">MIỀN ĐÍCH — LÚC TRIỂN KHAI</text>
  </g>
  <rect class="box" x="0" y="26" width="266" height="132"/>
  <rect class="box-accent" x="368" y="26" width="272" height="132"/>
  <g font-size="11">
    <text x="12" y="50">Máy in và màn hình cụ thể</text>
    <text x="12" y="72">Ánh sáng phòng thí nghiệm</text>
    <text x="12" y="94">Camera đã biết</text>
    <text x="12" y="116">Kiểu tấn công đã thấy</text>
    <text x="380" y="50">Thiết bị chưa từng gặp</text>
    <text x="380" y="72">Ánh sáng bất kỳ</text>
    <text x="380" y="94">Camera khác hẳn</text>
    <text x="380" y="116">Kiểu tấn công mới</text>
  </g>
  <g class="flow" marker-end="url(#pad-a)"><path d="M266 92 H360"/></g>
  <text class="lbl dim" x="274" y="84" font-size="9">DỊCH CHUYỂN MIỀN</text>
  <g font-size="10.5" class="dim">
    <text x="12" y="146">Đo trong cùng miền: dễ lạc quan</text>
    <text x="380" y="146">Đo chéo miền: phép thử thật</text>
  </g>
  <text x="0" y="184" font-size="10.5" class="dim">Kẻ tấn công không bị ràng buộc phải dùng đúng loại tấn công có trong tập huấn luyện.</text>
</svg>
<figcaption>Bài toán này luôn có khoảng cách giữa hai miền. Con số đo trong cùng một bộ dữ liệu nói rất ít về khả năng dùng được ngoài thực tế.</figcaption>
</figure>

### Vì sao đây không phải bài phân loại nhị phân thường

Một bài phân loại thông thường dựa trên giả định tập huấn luyện và tập kiểm tra đến từ cùng một phân phối. Với chống giả mạo, giả định đó sai theo thiết kế. Camera nơi triển khai không phải camera đã quay dữ liệu, ánh sáng không phải ánh sáng phòng thu, và kiểu tấn công có thể hoàn toàn mới. Độ khó thật của bài toán nằm ở khoảng cách giữa hai phân phối ấy, chứ không nằm ở việc phân biệt thật với giả trên dữ liệu đã thấy.

Có một điểm bất đối xứng nữa. Lớp "live" tuy đa dạng về người và điều kiện chụp nhưng vẫn là một khái niệm đóng: đó luôn là một khuôn mặt người thật trước ống kính. Lớp "spoof" thì mở — nó gồm mọi cách làm giả đã biết và cả những cách chưa ai nghĩ ra. Huấn luyện một bộ phân loại nhị phân trên một tập hữu hạn kiểu tấn công về bản chất là dạy nó nhận ra vài điểm trong một không gian không có biên. Đó là lý do các chỉ số đo trên phần dữ liệu giữ lại của cùng một bộ gần như không nói gì về khả năng dùng được: mô hình rất có thể đã học đặc điểm của chiếc máy in cụ thể hoặc đặc trưng nén của chiếc màn hình cụ thể dùng để tạo dữ liệu.

### Domain shift và domain generalization

Hiện tượng phân phối lúc chạy khác phân phối lúc huấn luyện gọi là domain shift. Trong bài toán này, một "miền" thường tương ứng với một tổ hợp thiết bị thu, điều kiện ánh sáng và quy trình tạo mẫu tấn công — trên thực tế mỗi bộ dữ liệu công khai là một miền riêng, vì nó được thu bằng một dàn thiết bị và một kịch bản cố định.

Có hai hướng ứng phó, khác nhau ở giả định. Domain adaptation giả định ta có sẵn một ít dữ liệu từ miền đích, dù không nhãn, để tinh chỉnh trước khi triển khai. Domain generalization thì không giả định gì cả: mô hình phải chạy được trên miền chưa từng thấy và không có cơ hội làm quen trước. Cách đạt tới điều đó là huấn luyện trên nhiều miền nguồn cùng lúc, đồng thời ép biểu diễn không mang dấu vết của miền nào — nếu mạng không phân biệt nổi dữ liệu đến từ đâu, nó buộc phải dựa vào đặc trưng chung cho mọi miền. Hướng thứ tư ở phần trên là một hiện thực trực tiếp của tư tưởng này, với cơ chế xáo trộn phong cách và nhánh đảo gradient đóng đúng vai trò đó.

### Tín hiệu nằm ở kết cấu bề mặt tần số cao

Thứ phân biệt một khuôn mặt thật với ảnh chụp lại nó thường không nằm ở hình dạng mà nằm ở kết cấu bề mặt: vệt moiré sinh ra khi camera chụp một màn hình pixel, hạt giấy của ảnh in, phản xạ ánh sáng không tự nhiên trên bề mặt phẳng. Đây đều là tín hiệu tần số cao.

Điều đó dẫn tới một cân nhắc thực tế. Các mô hình nền huấn luyện cho phân loại vật thể được tối ưu để nhận ra "con mèo" bất kể ảnh mờ hay nét, nên chúng có xu hướng loại bỏ chính lớp tín hiệu tần số cao đó như nhiễu. Đóng băng toàn bộ backbone như vậy đồng nghĩa với việc khoá mô hình vào một không gian đặc trưng đã bỏ mất thứ cần dùng. Đóng băng vẫn là lựa chọn hợp lý khi dữ liệu rất ít, nhưng nên là quyết định có cân nhắc chứ không phải mặc định.

### Hai loại lỗi có hậu quả khác nhau

Hệ thống có thể sai theo hai cách: cho một tấn công lọt qua, hoặc từ chối một người dùng thật. Loại lỗi thứ nhất là vấn đề bảo mật, loại thứ hai là vấn đề trải nghiệm. Chúng không quy đổi được về nhau, và tỷ lệ đánh đổi phù hợp phụ thuộc vào việc hệ thống bảo vệ cái gì: mở khoá một ứng dụng đọc báo và xác thực một giao dịch ngân hàng cần hai điểm vận hành rất khác nhau trên cùng một đường cong.

<figure class="diagram">
<svg viewBox="0 0 640 260" role="img" aria-label="Hai phân phối điểm số chồng lấn nhau với một vạch ngưỡng cắt qua, tạo ra vùng tấn công lọt và vùng người thật bị từ chối">
  <defs>
    <marker id="pad-b" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker>
    <marker id="pad-c" markerWidth="8" markerHeight="8" refX="1" refY="4" orient="auto">
      <path d="M8,0 L0,4 L8,8 z" fill="currentColor"/></marker>
  </defs>
  <path class="area-warn" d="M200 190 C 252.3 190 285.6 150.7 319.9 120.4 L319.9 190 Z"/>
  <path class="area" d="M320.1 115 C 354.4 147.6 387.7 190 440 190 L320.1 190 Z"/>
  <path class="curve-accent" d="M60 190 C 145 190 180 78 250 78 C 320 78 355 190 440 190"/>
  <path class="curve-warn" d="M200 190 C 285 190 320 86 390 86 C 460 86 495 190 580 190"/>
  <path class="axis" d="M40 190 H620"/>
  <path class="edge dashed" d="M320 76 V190"/>
  <path class="flow" d="M270 50 H370" marker-start="url(#pad-c)" marker-end="url(#pad-b)"/>
  <text text-anchor="middle" x="320" y="30" font-size="10.5" class="dim">ngưỡng quyết định</text>
  <text text-anchor="middle" x="320" y="68" font-size="10" class="dim">dịch ngưỡng là đánh đổi hai vùng này</text>
  <g text-anchor="middle" font-size="11">
    <text x="150" y="152">Mẫu thật</text>
    <text x="490" y="152">Mẫu tấn công</text>
  </g>
  <g font-size="10" class="dim">
    <text x="0" y="204">điểm số thấp — giống mẫu thật</text>
    <text text-anchor="end" x="636" y="204">điểm số cao — giống tấn công</text>
  </g>
  <rect class="box-warn" x="0" y="215" width="10" height="10"/>
  <rect class="cell-on" x="300" y="215" width="10" height="10"/>
  <g font-size="10.5" class="dim">
    <text x="16" y="224">Tấn công lọt qua ngưỡng — APCER</text>
    <text x="316" y="224">Người thật bị chặn — BPCER</text>
  </g>
  <text x="0" y="246" font-size="10.5" class="dim">Chất lượng mô hình là mức chồng lấn giữa hai phân phối; ngưỡng chỉ là tham số vận hành chọn sau.</text>
</svg>
<figcaption>Dịch vạch ngưỡng chỉ chuyển lỗi từ vùng này sang vùng kia. Muốn cả hai vùng cùng nhỏ đi thì phải kéo hai phân phối rời nhau ra, tức phải đổi mô hình.</figcaption>
</figure>

Điều này có hệ quả trực tiếp lên cách xây và cách công bố. Mô hình sinh ra một điểm số liên tục, còn quyết định cuối cùng đến từ việc so điểm số ấy với một ngưỡng. Chất lượng của mô hình nằm ở khả năng xếp hạng — mẫu thật có điểm cao hơn mẫu giả đến mức nào — còn ngưỡng chỉ là một tham số vận hành chọn sau. Trộn hai thứ đó vào một con số duy nhất làm mất thông tin: nó không cho biết kết quả kém là do mô hình phân biệt tồi hay do vạch cắt đặt sai chỗ. Vì vậy hai đại lượng nên được báo cáo tách nhau, và ngưỡng nên là thứ cấu hình được ở sản phẩm cuối chứ không phải hằng số nướng vào mã.

## Ngành công nghiệp làm việc này ra sao

Lĩnh vực này có tiêu chuẩn quốc tế riêng cho việc đo lường: **ISO/IEC 30107-3**, tên đầy đủ *Information technology — Biometric presentation attack detection — Part 3: Testing and reporting*, do ISO/IEC JTC 1/SC 37 phụ trách, bản hiện hành ban hành năm 2023 thay cho bản 2017. Tiêu chuẩn quy định cách đánh giá và cách báo cáo, không quy định phải dùng thuật toán nào.

Bộ chỉ số nó chuẩn hoá gồm ba đại lượng. **APCER** là tỷ lệ tấn công bị phân loại nhầm thành hợp lệ. **BPCER** là tỷ lệ người dùng thật bị từ chối nhầm — lưu ý bản 2017 gọi đại lượng này là NPCER, nên khi đọc tài liệu cũ cần đối chiếu. **ACER** là trung bình cộng của hai đại lượng trên. Việc tiêu chuẩn tách bạch hai loại lỗi thay vì gộp thành một con số độ chính xác chính là sự thừa nhận rằng chúng có hậu quả khác nhau.

Về protocol, bộ dữ liệu **OULU-NPU** đưa ra một thiết kế đáng học. Đây là bộ video quay bằng camera trước của nhiều dòng smartphone, trong nhiều môi trường, với tấn công in ảnh và phát lại video. Nó định nghĩa bốn protocol, và điểm mấu chốt là mỗi protocol cố tình đặt vào tập kiểm tra ít nhất một điều kiện chưa xuất hiện khi huấn luyện: thiết bị mới, môi trường mới, hoặc loại tấn công mới. Cấu trúc đó ép mô hình phải khái quát hoá thay vì học thuộc.

Các benchmark khác đi cùng tinh thần. **SiW** (Liu, Jourabloo, Liu, CVPR 2018) đưa ra hướng giám sát bổ trợ: thay vì chỉ dùng nhãn nhị phân, mô hình học thêm bản đồ độ sâu và tín hiệu rPPG — dấu vết mạch đập nhìn thấy được qua thay đổi màu da rất nhỏ, thứ mà ảnh in không có; paper báo cáo cả kết quả trong cùng bộ dữ liệu lẫn kết quả chéo bộ. **CASIA-SURF** (CVPR 2019) là benchmark đa phương thức quy mô lớn với ba modality RGB, Depth và IR, kèm protocol chuẩn đi cùng.

Về cách trình bày kết quả, **đường cong DET** (Martin và cộng sự, Eurospeech 1997, *The DET curve in assessment of detection task performance*) được đề xuất đúng cho lớp bài toán có đánh đổi hai loại lỗi. Nó vẽ trên trục log, nhờ đó vùng quanh điểm cân bằng — vùng thực sự quan trọng khi chọn ngưỡng vận hành — được giãn ra và dễ so sánh hơn so với ROC thông thường.

Các cuộc thi PAD quốc tế lấy ACER làm tiêu chí xếp hạng, và xác định ngưỡng quyết định bằng EER trên tập validation thay vì chọn một con số tuỳ ý. Chi tiết nhỏ này có ý nghĩa lớn: nó biến việc chọn ngưỡng thành một quy trình lặp lại được, thay vì một lựa chọn có thể vô tình hoặc cố ý làm đẹp kết quả.

Từ đó rút ra hai nguyên tắc báo cáo. Thứ nhất, một con số tại một ngưỡng cố định chỉ là một điểm trên đường cong, nên cần công bố cả đường cong ROC hoặc DET cùng EER để người đọc thấy toàn cảnh. Thứ hai, khi tập kiểm tra lệch lớp — mà trong lĩnh vực này thì gần như luôn lệch, vì mẫu tấn công dễ tạo hơn mẫu thật — một con số độ chính xác gộp chung sẽ phản ánh tỷ lệ lớp nhiều hơn phản ánh chất lượng mô hình.

## Vài điều rút ra

**Ưu tiên chỉ số không phụ thuộc ngưỡng khi đánh giá mô hình.** Diện tích dưới đường cong ROC hay EER nói về khả năng xếp hạng của mô hình; độ chính xác tại một ngưỡng nói về chất lượng của một quyết định vận hành. Hai thứ đó tách rời nhau, và nhầm lẫn giữa chúng dẫn tới kết luận sai về cả hai.

**Thiết kế protocol đánh giá để nó có thể thất bại.** Cách OULU-NPU đặt điều kiện chưa từng thấy vào tập kiểm tra là một mẫu đáng sao chép cho mọi bài toán có domain shift. Một protocol không bao giờ báo lỗi thì không cung cấp thông tin.

**Đưa bất biến vào kiến trúc thay vì trông chờ dữ liệu dạy nó.** Cơ chế xáo trộn phong cách trong batch và nhánh đảo gradient là hai cách nói với mạng rằng thiết bị và ánh sáng không phải thứ cần học. Khi biết trước chiều biến thiên nào là nhiễu, mã hoá nó vào hàm mất mát hiệu quả hơn thu thêm dữ liệu.

**Chọn điểm vận hành theo hậu quả của từng loại lỗi.** Vì hai loại lỗi có giá khác nhau tuỳ ứng dụng, sản phẩm cuối nên phơi ra một ngưỡng cấu hình được kèm đường cong đánh đổi, để bên triển khai chọn điểm phù hợp với ngữ cảnh của họ thay vì nhận một con số cố định.
