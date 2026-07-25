---
title: "Mô hình ngôn ngữ tiếng Việt: dự đoán từ tiếp theo"
description: "Ba đường tách từ cho tiếng Việt, năm kiến trúc dựng từ đầu, và điều kiện để hai con số độ bối rối so sánh được với nhau."
lang: "vi"
order: 3
field: "LM"
topics: ["mô hình ngôn ngữ", "tokenizer", "perplexity", "LoRA", "tiếng Việt"]
---

Dự đoán từ tiếp theo là bài toán nền của mọi mô hình ngôn ngữ: cho một chuỗi từ đã có, đoán từ kế
tiếp. Nó đơn giản đến mức có thể phát biểu bằng một câu, nhưng lại chứa gần như toàn bộ những vấn đề
thú vị của xử lý ngôn ngữ — và với tiếng Việt thì có thêm một vấn đề riêng ngay từ bước đầu tiên.

## Tiếng Việt và câu hỏi "một từ là gì"

Trong tiếng Anh, khoảng trắng gần như trùng với ranh giới từ. Trong tiếng Việt thì không. "Học sinh"
là một từ mang nghĩa riêng, nhưng được viết thành hai âm tiết cách nhau bằng khoảng trắng. Tách theo
khoảng trắng sẽ cho ra hai đơn vị mà khi đứng riêng mang nghĩa khác hẳn.

Đây không phải chi tiết ngôn ngữ học thuần tuý. Nó quyết định đầu vào của mô hình, kích thước không
gian đầu ra, và cả độ khó của bài toán — nên nó là quyết định kiến trúc đầu tiên phải đưa ra.

## Hệ thống đã dựng

### Ba đường tách từ, ba pipeline dữ liệu

Ngữ liệu là một tập lớn bài báo tiếng Việt, mỗi bài ghép tiêu đề, tóm tắt và nội dung thành một văn
bản. Trên cùng ngữ liệu đó, ba pipeline khác nhau được dựng.

**Đường thứ nhất — tách theo khoảng trắng.** Đơn giản nhất, không phụ thuộc công cụ ngoài. Từ vựng
được xây bằng cách đếm tần suất rồi **bỏ những từ xuất hiện dưới một ngưỡng**, gom chúng vào một ký
hiệu chung cho "từ chưa biết". Chuỗi huấn luyện sinh bằng cửa sổ trượt trên toàn bộ token của bài báo,
nên một bài dài sinh ra rất nhiều mẫu.

**Đường thứ hai — tách từ bằng công cụ chuyên cho tiếng Việt.** Dùng bộ tách từ có sẵn để lấy đơn vị
là từ thật theo nghĩa ngôn ngữ học. Kích thước từ vựng tăng lên đáng kể so với đường thứ nhất, vì số
tổ hợp âm tiết tạo thành từ lớn hơn nhiều so với số âm tiết đơn lẻ.

**Đường thứ ba — tách theo đơn vị con của từ.** Dùng bộ tách của một mô hình ngôn ngữ tiếng Việt đã
huấn luyện sẵn, theo kiểu mã hoá cặp byte. Kích thước từ vựng cố định và biết trước; từ chưa gặp được
xử lý bằng cách ghép các mảnh nhỏ hơn thay vì gom hết vào một ký hiệu chung.

Ba đường này không phải ba biến thể cấu hình của cùng một thứ. Chúng tạo ra ba chuỗi đầu vào khác nhau,
ba kích thước không gian đầu ra khác nhau, và ba mức độ khó khác nhau cho cùng một tác vụ.

### Năm kiến trúc dựng từ đầu

Trên mỗi pipeline, năm kiến trúc được cài và huấn luyện với cùng bộ siêu tham số:

- **RNN** — mạng hồi tiếp cơ bản, không có cổng.
- **GRU** — thêm cổng cập nhật và cổng đặt lại để kiểm soát dòng thông tin.
- **LSTM** — thêm ô nhớ cùng ba cổng vào, quên và ra.
- **LSTM kèm chú ý** — thêm một khối chú ý đa đầu chạy trên toàn bộ chuỗi đầu ra của LSTM trước khi
  lấy trạng thái cuối.
- **Transformer** — mã hoá vị trí bằng hàm sin và cosin, các khối gồm tự chú ý có mặt nạ nhân quả,
  mạng truyền thẳng, chuẩn hoá lớp và kết nối tắt.

Cấu hình chung: lớp nhúng, hai tầng, dropout, độ dài chuỗi tối đa cố định. Tối ưu bằng Adam kèm bộ
lập lịch giảm tốc độ học khi không cải thiện, cắt chuẩn gradient, dừng sớm, và huấn luyện độ chính xác
hỗn hợp.

Một điểm về cách đặt bài toán đáng chú ý: các mạng này lấy **trạng thái ẩn tại vị trí cuối cùng** của
chuỗi rồi chiếu sang không gian từ vựng — tức bài toán được đặt thành phân loại một từ, không phải
sinh chuỗi. Mỗi mẫu huấn luyện vì thế cho đúng một tín hiệu học.

### Tinh chỉnh mô hình đã huấn luyện sẵn

Song song, một hướng khác: lấy các mô hình ngôn ngữ đa ngữ đã huấn luyện sẵn ở quy mô vài trăm triệu
tham số và tinh chỉnh chúng cho cùng tác vụ.

Kỹ thuật dùng là **LoRA** — thích ứng hạng thấp. Thay vì cập nhật toàn bộ ma trận trọng số, LoRA giữ
nguyên trọng số gốc và học thêm một cặp ma trận hạng thấp cộng vào. Số tham số cần cập nhật giảm
xuống rất nhiều, nên tinh chỉnh được trên phần cứng khiêm tốn. Các ma trận đích chọn theo từng kiến
trúc: với họ này là các phép chiếu truy vấn, khoá, giá trị và đầu ra; với họ kia là khối trọng số gộp
ba phép chiếu cùng các lớp truyền thẳng.

Điểm khác biệt quan trọng về cách đặt bài toán: nhánh này huấn luyện theo kiểu **mô hình ngôn ngữ nhân
quả chuẩn** — dự đoán ở mọi vị trí trong chuỗi, với phần đệm bị che khỏi hàm mất mát. Mỗi mẫu cho hàng
trăm tín hiệu học thay vì một.

## Kiến thức nền

### Độ bối rối và điều kiện để so sánh nó

Chỉ số phổ biến nhất cho mô hình ngôn ngữ là **perplexity** — độ bối rối. Trực giác: nó đo mức độ
"ngạc nhiên" trung bình của mô hình khi gặp văn bản kiểm tra, và có thể hiểu như số lựa chọn hiệu dụng
mà mô hình còn phân vân giữa chúng ở mỗi bước. Độ bối rối bằng một trăm nghĩa là mô hình lúng túng như
thể đang chọn đều giữa một trăm khả năng.

Về mặt hình thức, nó là nghịch đảo xác suất mà mô hình gán cho tập kiểm tra, **chuẩn hoá theo số đơn
vị** trong chuỗi.

Chính chỗ chuẩn hoá ấy dẫn tới một điều kiện then chốt, được nêu thẳng trong giáo trình chuẩn của lĩnh
vực:

> Note that in computing perplexities, the language model must be constructed without any knowledge
> of the test set, or else the perplexity will be artificially low. **And the perplexity of two
> language models is only comparable if they use identical vocabularies.**

Lý do rất trực tiếp: nếu một mô hình chia câu thành hai mươi đơn vị còn mô hình khác chia cùng câu ấy
thành ba mươi lăm đơn vị, mẫu số đã khác nhau. Và độ khó của mỗi lần dự đoán cũng khác — đoán một mảnh
âm tiết dễ hơn hẳn đoán một từ trọn nghĩa.

Hệ quả thực hành: **một chuỗi thí nghiệm trong đó mỗi vòng đổi cách tách từ thì không phải là một chuỗi
cải tiến so sánh được với nhau.** Muốn biết cách tách nào tốt hơn, phải cố định mọi thứ còn lại và đo
bằng một chỉ số không phụ thuộc đơn vị chia — chẳng hạn độ chính xác trên một tác vụ hạ nguồn cụ thể.

### Kích thước từ vựng và cái đuôi dài

Từ vựng không chỉ là một con số cấu hình. Lớp đầu ra của mô hình phải trải xác suất trên toàn bộ từ
vựng, nên kích thước của nó quyết định phần lớn số tham số và chi phí tính toán.

Đây là lý do tồn tại của **ngưỡng lọc từ hiếm**. Bỏ những từ xuất hiện quá ít lần không phải để tiết
kiệm bộ nhớ, mà vì lý do sâu hơn: một từ chỉ xuất hiện vài lần trong toàn ngữ liệu thì mô hình không
có đủ tín hiệu để học biểu diễn cho nó. Giữ lại chỉ tạo thêm một hàng trong ma trận đầu ra mà gradient
hầu như không bao giờ chạm tới.

Có một dấu hiệu nhận biết khi từ vựng phình quá mức: cho mô hình dự đoán tiếp một câu mở đầu thông
thường, và những từ nó đề xuất là các mảnh vỡ kỳ lạ hoặc danh từ riêng hiếm thay vì các từ phổ biến.
Đó là dấu hiệu phân phối đầu ra đã bị cái đuôi dài chi phối.

### Vì sao mô hình huấn luyện sẵn có lợi thế lớn

Một mô hình dựng từ đầu phải học đồng thời hai thứ: cấu trúc thống kê của ngôn ngữ, và tác vụ cụ thể
đang huấn luyện. Một mô hình đã huấn luyện sẵn đã có thứ nhất, chỉ cần thích nghi với thứ hai.

Với ngữ liệu quy mô vừa phải, đây là chênh lệch rất lớn. Điều đó dẫn tới một cách phân biệt hữu ích:
dựng kiến trúc từ đầu là bài tập hiểu nguyên lý; tinh chỉnh mô hình sẵn có là con đường tới hệ thống
dùng được. Cả hai đều có giá trị, nhưng nhầm lẫn giữa chúng dẫn tới việc dồn thời gian huấn luyện một
kiến trúc không có cơ hội thắng.

## Ngành công nghiệp làm việc này ra sao

**Đánh giá cần rộng hơn một con số.** Các khung đánh giá hiện đại đo đồng thời nhiều chiều — không chỉ
độ chính xác mà cả độ hiệu chuẩn của xác suất, độ bền trước nhiễu đầu vào, tính công bằng, thiên lệch,
độc hại, và chi phí tính toán — trên một tập tình huống rộng, với điều kiện chuẩn hoá như nhau cho mọi
mô hình. Lý do là một mô hình có thể tốt ở chiều này và tệ ở chiều khác, và một con số gộp sẽ che mất
điều đó. Trước khi các khung này ra đời, các mô hình thường chỉ được đo trên một phần nhỏ số tình
huống đáng quan tâm.

**Benchmark đa nhiệm.** Truyền thống đánh giá hiểu ngôn ngữ dựa trên các bộ gồm nhiều tác vụ khác nhau
— suy luận, tương đồng câu, phân loại — thay vì một tác vụ đơn lẻ, kèm bộ chẩn đoán để phân tích mô
hình mạnh yếu ở hiện tượng ngôn ngữ nào. Khi các mô hình đã vượt qua bộ đầu tiên, một bộ khó hơn được
xây tiếp.

**Hệ sinh thái cho tiếng Việt đã tương đối đầy đủ.** Có mô hình ngôn ngữ đơn ngữ quy mô lớn được công
bố công khai, vượt các mô hình đa ngữ trên các tác vụ tiếng Việt như gán nhãn từ loại, phân tích cú
pháp phụ thuộc, nhận dạng thực thể và suy luận. Có bộ công cụ xử lý cơ bản bao gồm tách từ, gán nhãn
từ loại và nhận dạng thực thể. Và gần đây có cả bộ benchmark hiểu ngôn ngữ dành riêng cho tiếng Việt,
gồm hơn chục tác vụ được xây bằng cách dịch benchmark có sẵn, sinh ngữ liệu mới, và thu thập các bộ
dữ liệu rời rạc.

Điều này đáng nói vì nó thay đổi điểm khởi đầu hợp lý: bắt đầu từ một mô hình sẵn có cho tiếng Việt
tiết kiệm hơn nhiều so với bắt đầu từ một lớp nhúng khởi tạo ngẫu nhiên.

## Vài điều rút ra

**Một so sánh chỉ có ý nghĩa khi các yếu tố còn lại được giữ nguyên.** Đổi cách tách từ là đổi đơn vị
đo; đổi lượng dữ liệu là đổi độ khó. Đổi cả hai cùng lúc thì kết quả không diễn giải được, dù mỗi lần
chạy đều thành công.

**Trước khi so hai con số độ bối rối, hãy kiểm tra hai mô hình có chung bộ từ vựng không.** Nếu không,
hai con số ấy không so được với nhau, bất kể chúng trông có vẻ so sánh được đến đâu.

**Khi hai chỉ số cùng đo một mô hình mà kể hai câu chuyện khác nhau, sự chênh lệch đó là thông tin.**
Độ chính xác chỉ đếm xem đáp án đúng có nằm trong nhóm dự đoán hàng đầu hay không, nên khá thô. Độ bối
rối lấy trung bình của một hàm mũ, nên vài mẫu bị gán xác suất rất thấp cũng đủ kéo giá trị lên cao.
Hai chỉ số lệch nhau thường có nghĩa là tập đánh giá quá nhỏ, hoặc mô hình đang ghi nhớ thay vì khái
quát hoá.

**Cách đặt bài toán quyết định hiệu quả sử dụng dữ liệu.** Cùng một ngữ liệu, cách đặt thành "dự đoán
một từ ở cuối chuỗi" cho ít tín hiệu học hơn nhiều so với cách đặt thành "dự đoán ở mọi vị trí". Đây
là lựa chọn nên cân nhắc sớm, vì nó ảnh hưởng tới toàn bộ ngân sách huấn luyện về sau.
