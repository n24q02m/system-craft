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

### Hướng một: mạng tích chập kèm cơ chế chú ý

Backbone là một mạng tích chập đã huấn luyện sẵn trên tập ảnh lớn, dùng cả biến thể nặng cho trường hợp không giới hạn tài nguyên lẫn biến thể nhẹ hướng tới thiết bị di động.

Điểm bổ sung là khối chú ý CBAM chèn sau mỗi nhóm khối của backbone. CBAM gồm hai phần nối tiếp. Phần chú ý theo kênh gộp bản đồ đặc trưng theo trục không gian bằng cả trung bình lẫn cực đại, đưa hai vector thu được qua một MLP dùng chung, cộng lại rồi qua sigmoid để ra trọng số cho từng kênh. Phần chú ý theo không gian gộp theo trục kênh, đưa qua một lớp tích chập 7x7 rồi sigmoid để ra trọng số cho từng vị trí. Ý tưởng là để mạng tự học xem kênh nào và vùng ảnh nào đáng chú ý, thay vì đối xử đồng đều với toàn bộ bản đồ đặc trưng.

Đầu phân loại đặt sau backbone gồm: gộp trung bình toàn cục, dropout, một lớp tuyến tính trung gian, chuẩn hoá batch, ReLU, rồi một lớp tuyến tính cuối trả về một logit duy nhất.

### Hướng hai: Vision Transformer

Hướng này thay backbone tích chập bằng một Vision Transformer đã huấn luyện sẵn, có cả bản đầy đủ và bản rất nhẹ. Ảnh được chia thành các patch, và biểu diễn dùng cho phân loại lấy từ token CLS, gắn vào một đầu phân loại tương tự hướng một.

Hướng này có thêm một chế độ đóng băng toàn bộ backbone và chỉ huấn luyện phần đầu. Cách làm đó rẻ và hợp lý khi dữ liệu ít, nhưng đi kèm một đánh đổi được bàn ở phần kiến thức nền phía dưới.

### Hướng ba: GAN với nhánh phân loại phụ

Hướng này dùng một mạng đối sinh. Bộ sinh theo kiểu DCGAN: từ một vector ẩn đi qua chuỗi lớp upsample và tích chập để dựng ra ảnh. Bộ phân biệt có bốn khối tích chập stride 2, có chèn CBAM, rồi tách thành hai nhánh — một nhánh phán đoán ảnh thật hay do bộ sinh tạo ra, phục vụ phần đối kháng; một nhánh phụ phân loại live/spoof.

Chi tiết đáng chú ý là chính nhánh phụ mới là bộ phân loại dùng thật. Phần đối kháng ở đây đóng vai trò tín hiệu huấn luyện bổ trợ, buộc bộ phân biệt học biểu diễn giàu thông tin về ảnh khuôn mặt, chứ bản thân ảnh sinh ra không phải mục tiêu. Phần đối kháng được huấn luyện theo Wasserstein GAN có phạt gradient, một biến thể chọn vì ổn định hơn so với công thức đối kháng nguyên bản.

### Hướng bốn: tách phong cách khỏi nội dung

Ba hướng trên đều bắt đầu từ một kiến trúc có sẵn. Hướng thứ tư đi ngược lại: cài lại từ đầu một mạng được thiết kế riêng cho mục tiêu domain generalization, tức khả năng hoạt động trên nguồn dữ liệu chưa từng thấy.

Ý tưởng nền là tách trong ảnh hai thành phần: "nội dung" — thứ nói lên ảnh này là người thật hay bản sao chép; và "phong cách" — thứ phản ánh camera nào, ánh sáng nào, hậu kỳ nào. Mục tiêu là buộc biểu diễn nội dung độc lập với phong cách.

Cấu trúc gồm các phần sau:

- Một bộ trích đặc trưng nhiều tầng tự thiết kế, không dùng backbone pretrained.
- Một nhánh trích nội dung và một nhánh trích phong cách. Nhánh phong cách đi qua chuẩn hoá theo thực thể rồi vài lớp fully-connected để sinh ra hai tham số: hệ số tỷ lệ và hệ số dịch chuyển.
- Một bước ghép lại bằng AdaIN, tức chuẩn hoá thực thể thích ứng: chuẩn hoá đặc trưng nội dung về trung bình không và phương sai đơn vị, rồi áp hai tham số phong cách vào.

Cơ chế cốt lõi nằm ở cách sinh cặp dữ liệu để học. Trong mỗi batch, thứ tự mẫu được xáo trộn để ghép phong cách của ảnh này với nội dung của ảnh khác. Cặp lai đó mang nhãn dương nếu hai ảnh gốc cùng lớp live/spoof, và nhãn âm nếu khác lớp. Hàm mất mát tương phản trên các cặp này ép mạng đưa những ảnh cùng lớp lại gần nhau bất kể chúng đến từ thiết bị nào — đúng thứ cần có khi triển khai lên phần cứng lạ.

Hai chi tiết nữa. Đầu ra không phải một logit đơn mà là một bản đồ độ sâu dựng qua các lớp upsample: mặt người thật có cấu trúc ba chiều, còn ảnh in hay màn hình phát lại về bản chất là mặt phẳng, nên độ sâu là tín hiệu giám sát giàu thông tin hơn một nhãn nhị phân. Và có thêm một nhánh phân biệt miền nối qua lớp đảo gradient: nhánh này cố đoán mẫu đến từ nguồn dữ liệu nào, còn lớp đảo gradient khiến phần trích đặc trưng bị đẩy theo hướng ngược lại, tức học biểu diễn mà nhánh kia không đoán nổi nguồn.

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
