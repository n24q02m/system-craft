---
title: "Mô hình ngôn ngữ tiếng Việt: khi thay tokenizer là thay cả bài toán"
description: "Ba thế hệ mô hình dự đoán từ tiếp theo, và bài học rằng perplexity của hai mô hình chỉ so được với nhau khi chúng dùng chung bộ từ vựng."
lang: "vi"
order: 3
field: "LM"
topics: ["mô hình ngôn ngữ", "tokenizer", "perplexity", "từ vựng", "so sánh có kiểm soát"]
---

Bài toán dự đoán từ tiếp theo là bài toán nền của mọi mô hình ngôn ngữ: cho một chuỗi từ đã có, đoán
từ kế tiếp. Với tiếng Việt, nó có một đặc thù ngay từ bước đầu tiên — và chính bước đầu tiên ấy quyết
định phần lớn kết quả.

## Tiếng Việt và câu hỏi "một từ là gì"

Trong tiếng Anh, khoảng trắng gần như trùng với ranh giới từ. Trong tiếng Việt thì không: "học sinh"
là một từ mang nghĩa riêng, nhưng viết thành hai âm tiết cách nhau bằng khoảng trắng. Tách theo khoảng
trắng sẽ cho ra hai đơn vị vô nghĩa khi đứng riêng.

Từ đó có ba hướng xử lý, và mỗi hướng tạo ra một bài toán khác nhau:

**Tách theo khoảng trắng.** Đơn giản nhất, không cần công cụ ngoài. Đổi lại, mô hình phải tự học rằng
hai âm tiết nào thường đi cùng nhau — tốn dung lượng mô hình cho việc lẽ ra có thể xử lý ở bước tiền
xử lý.

**Tách từ bằng công cụ chuyên cho tiếng Việt.** Có các bộ công cụ đã được xây dựng cho việc này, và
đơn vị thu được là từ thật theo nghĩa ngôn ngữ học. Đổi lại, số lượng từ khác nhau trong ngữ liệu tăng
lên đáng kể so với tách theo âm tiết.

**Tách theo đơn vị con của từ.** Dùng bộ tách của một mô hình đã huấn luyện sẵn cho tiếng Việt. Kích
thước từ vựng cố định và biết trước, xử lý được từ chưa gặp bằng cách ghép các mảnh.

Ba lựa chọn này không phải ba biến thể của cùng một cấu hình. Chúng tạo ra ba chuỗi đầu vào khác nhau,
ba kích thước từ vựng khác nhau, và ba không gian đầu ra khác nhau.

## Vì sao không thể so sánh trực tiếp ba thế hệ

Đây là chỗ bài học nằm ở, và nó có một phát biểu chuẩn trong giáo trình kinh điển về xử lý ngôn ngữ
của Jurafsky và Martin. Nguyên văn:

> Note that in computing perplexities, the language model must be constructed without any knowledge
> of the test set, or else the perplexity will be artificially low. **And the perplexity of two
> language models is only comparable if they use identical vocabularies.**

Perplexity — độ bối rối — đo mức độ "ngạc nhiên" trung bình của mô hình khi gặp văn bản kiểm tra.
Nó được chuẩn hoá theo số đơn vị trong chuỗi. Chính chỗ chuẩn hoá này khiến nó không so sánh được
giữa hai bộ từ vựng khác nhau: nếu một mô hình chia câu thành 20 đơn vị và mô hình khác chia cùng câu
ấy thành 35 đơn vị, mẫu số đã khác nhau, và độ khó của mỗi lần dự đoán cũng khác nhau. Đoán một mảnh
âm tiết dễ hơn nhiều so với đoán một từ trọn nghĩa.

Hệ quả thực tế: một chuỗi thí nghiệm trong đó mỗi thế hệ đổi tokenizer **không phải** là một chuỗi cải
tiến có thể so sánh. Nếu kết quả thế hệ sau khác thế hệ trước, ta không biết đó là do tokenizer, do
kích thước từ vựng, hay do quy mô dữ liệu — vì cả ba đã đổi cùng lúc.

Nguyên tắc thiết kế thí nghiệm ở đây rất cổ điển: **mỗi lần chỉ đổi một biến.** Muốn biết tokenizer
nào tốt hơn thì phải cố định lượng dữ liệu, cố định kiến trúc, cố định cách chia tập, và đo bằng một
chỉ số không phụ thuộc đơn vị chia — chẳng hạn độ chính xác trên một tác vụ hạ nguồn cụ thể, thay vì
perplexity.

## Từ vựng nở ra và cái đuôi dài

Có một hệ quả kỹ thuật đi kèm việc đổi tokenizer mà dễ bỏ qua: **ngưỡng lọc từ hiếm**.

Khi xây từ vựng từ ngữ liệu, thông lệ là bỏ những từ xuất hiện dưới một số lần nhất định và gộp chúng
vào một ký hiệu chung cho "từ chưa biết". Việc này không phải để tiết kiệm bộ nhớ, mà vì một lý do sâu
hơn: một từ chỉ xuất hiện vài lần trong toàn bộ ngữ liệu thì mô hình không có đủ tín hiệu để học biểu
diễn cho nó. Giữ nó lại chỉ tạo thêm một hàng trong ma trận đầu ra mà gradient hầu như không bao giờ
chạm tới.

Nếu bước lọc này bị bỏ khi đổi sang tokenizer mới, từ vựng có thể phình lên gấp nhiều lần. Lớp đầu ra
của mô hình — vốn phải trải xác suất trên toàn bộ từ vựng — trở nên khổng lồ, trong khi phần lớn các
lớp đầu ra ấy gần như không có dữ liệu huấn luyện. Kết quả là mô hình phân tán năng lực vào việc phân
biệt những thứ nó không thể học được.

Có một dấu hiệu nhận biết rất rõ: khi cho mô hình dự đoán tiếp một câu mở đầu thông thường, những từ
nó đề xuất là các mảnh vỡ kỳ lạ hoặc các danh từ riêng hiếm, thay vì các từ phổ biến. Đó là dấu hiệu
phân phối đầu ra đã bị cái đuôi dài chi phối.

## Học thuộc không phải học được

Một hiện tượng khác đáng ghi lại: mô hình đạt độ chính xác rất cao trên tập huấn luyện trong khi trên
tập kiểm tra thì không nhúc nhích, thậm chí độ bối rối trên tập kiểm tra còn tăng lên theo thời gian
huấn luyện.

Đây là quá khớp ở dạng kinh điển, nhưng trong bối cảnh mô hình ngôn ngữ nó có một sắc thái riêng: với
từ vựng rất lớn và dữ liệu tương đối nhỏ, việc ghi nhớ trở nên *dễ hơn* việc khái quát hoá. Mô hình
có đủ tham số để nhớ chuỗi cụ thể, và đó là con đường giảm hàm mất mát nhanh nhất.

Điều đáng nói là khi hiện tượng này xảy ra, **các chỉ số bắt đầu mâu thuẫn nhau**. Độ chính xác có thể
vẫn ổn định vì nó chỉ đếm xem đáp án đúng có nằm trong nhóm dự đoán hàng đầu hay không. Nhưng độ bối
rối thì nhạy hơn nhiều: nó lấy trung bình của một hàm mũ, nên chỉ vài mẫu bị mô hình gán xác suất
gần bằng không cũng đủ kéo giá trị lên rất cao. Với một tập đánh giá nhỏ và cố định, vài trường hợp
như vậy có thể chi phối toàn bộ con số.

Bài học vận hành: nếu hai chỉ số cùng đo một mô hình mà kể hai câu chuyện khác nhau, đừng chọn cái
nghe hợp ý hơn. Sự chênh lệch ấy chính là thông tin — thường là thông tin về việc tập đánh giá quá
nhỏ, hoặc về việc mô hình đang ghi nhớ thay vì khái quát.

## Vì sao mô hình huấn luyện sẵn thắng dễ dàng

Trong cùng một chuỗi thí nghiệm, các mô hình được tinh chỉnh từ một mô hình ngôn ngữ đã huấn luyện sẵn
vượt xa các mô hình xây từ đầu — dù chúng được cho ít dữ liệu hơn hẳn.

Điều này không có gì bất ngờ, nhưng đáng nói rõ vì sao: mô hình xây từ đầu phải học đồng thời hai thứ —
cấu trúc thống kê của ngôn ngữ, và tác vụ cụ thể đang huấn luyện. Mô hình đã huấn luyện sẵn đã có thứ
nhất, chỉ cần thích nghi với thứ hai. Với ngữ liệu quy mô vừa phải, cuộc so sánh không cân sức ngay
từ đầu.

Điều này dẫn tới một khuyến nghị thực tế: **xây từ đầu là bài tập hiểu nguyên lý, không phải con đường
tới hệ thống dùng được.** Cả hai đều có giá trị, nhưng nhầm lẫn giữa chúng dẫn tới việc bỏ nhiều tuần
huấn luyện một kiến trúc không bao giờ thắng nổi một mô hình sẵn có được tinh chỉnh trong vài giờ.

Với tiếng Việt, hệ sinh thái này đã tương đối đầy đủ: có mô hình ngôn ngữ đơn ngữ quy mô lớn được công
bố công khai, có bộ công cụ xử lý cơ bản, và gần đây có cả bộ benchmark đánh giá hiểu ngôn ngữ. Bắt
đầu từ đó hợp lý hơn nhiều so với bắt đầu từ một lớp nhúng khởi tạo ngẫu nhiên.

## Cách đánh giá cần rộng hơn một con số

Điểm cuối cùng, và là điểm mà ngành đã đi xa hơn hẳn thực hành thông thường: đánh giá mô hình ngôn ngữ
bằng một chỉ số duy nhất là không đủ.

Các khung đánh giá hiện đại đo đồng thời nhiều chiều — không chỉ độ chính xác mà cả độ hiệu chuẩn của
xác suất, độ bền trước nhiễu đầu vào, tính công bằng, thiên lệch, độc hại, và chi phí tính toán — trên
một tập tình huống rộng và với điều kiện chuẩn hoá như nhau cho mọi mô hình. Lý do là một mô hình có
thể tốt ở chiều này và tệ ở chiều khác, và một con số gộp sẽ che mất điều đó.

Với một dự án nhỏ, không cần chạy đủ mọi chiều. Nhưng nguyên tắc thì vẫn áp dụng được: chọn ít nhất
một chỉ số đo **năng lực nội tại** và một chỉ số đo **tác vụ thật**, rồi báo cáo cả hai. Khi chúng
đồng thuận, ta có tự tin. Khi chúng lệch nhau, ta có việc cần điều tra.

## Điều còn đọng lại

Bài học lớn nhất từ chuỗi thí nghiệm này không nằm ở kiến trúc nào tốt hơn, mà nằm ở thiết kế thí
nghiệm: **một so sánh chỉ có ý nghĩa khi các yếu tố còn lại được giữ nguyên.** Đổi tokenizer là đổi
đơn vị đo; đổi lượng dữ liệu là đổi độ khó; đổi cả hai cùng lúc thì kết quả không diễn giải được, dù
mỗi lần chạy đều thành công và đều cho ra số.

Và trước khi so hai con số perplexity, hãy hỏi một câu rất đơn giản: hai mô hình này có dùng chung bộ
từ vựng không? Nếu không, hai con số ấy không so được với nhau — bất kể chúng trông có vẻ so sánh
được đến đâu.
