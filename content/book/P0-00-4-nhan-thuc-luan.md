# 0.4 — Nhận thức luận: Provenance, 5 Mức Tin cậy & Chống phân rã

> **Tầng:** Propaedia · **Mở đầu** · **Trục đọc:** bản đồ · **Động từ liên quan:** Kiểm · Duy trì
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 0.2 (khái niệm tiên đề).

**Sợi chỉ đỏ:** *Review đủ lens rồi — con số '99% user hài lòng' trong slide lấy ở đâu, ai kiểm, và nếu nó đã chết thì sao?* — trả lời: mỗi con số được gán nhãn nguồn (P/I/V/E), ngày đo và điều kiện — con số không nhãn là con số mồ côi. Chương này cấp bộ đồ: 5 nhãn nguồn, 3 hạng phân rã của tài liệu cũ, và quy trình verify đã chạy thật cho facts/versions.csv của chính atlas. Câu hỏi để lại cho chương sau: *Đủ đồ tư duy, làm thật: DM khởi động bằng một máy chủ và một process — điều gì cần cảm bằng tay trước tiên?*

**Thuật ngữ sẽ gặp:** *provenance* — nguồn gốc của một con số: ai đo, khi nào, trong điều kiện nào; *nhãn nguồn P/I/V/E* — paper/đối chiếu độc lập/vendor/erect... chính xác hơn: P chuẩn hoá, I phân tích độc lập, V vendor, E kinh nghiệm nội bộ; *phân rã (decay)* — tài liệu chết dần khi thế giới đổi quanh nó; *errata* — danh mục sai đã biết, sửa công khai có kỷ luật; *verify* — đi kiểm một con số về nguồn sơ cấp, kèm ngày.

**Ví dụ mở đầu:** Slide kêu gọi vốn: "p99 của DM là 120 ms" — không nguồn, không ngày, không điều kiện. Sáu tháng sau ai cũng trích con số đó cho những điều kiện hoàn toàn khác (khác vùng, khác tải, khác phiên bản). Không ai cố ý nói dối; con số chỉ đơn giản là mồ côi — và chương này dạy cách cho nó giấy khai sinh.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Mọi con số mang nhãn nguồn P/I/V/E | Con số này từ đâu tới — và tôi có dám trích lại không? |
| 2 | Mọi mục "số & phiên bản" có ngày kiểm tra | Số này còn sống bao lâu (🔥/🌡/🧊)? |
| 3 | Ấn bản đóng băng hàng quý + errata công khai | Tôi đang đọc ấn bản nào — và sai sót đã sửa ở đâu? |
| 4 | Nguyên tắc "thà thiếu hơn sai" áp cho mọi mục chưa verify | Chưa kiểm chứng được — có nên viết? |

---

## 2. Cơ chế

### 2.1 Vì sao sách kỹ thuật cần nhận thức luận

Sách kỹ thuật hỏng bằng một con đường duy nhất: **số liệu cũ mà không ai biết cũ**. Người đọc trích lại, ra quyết định, và chuyển lỗi cho cuốn sách. Atlas đối xử với tri thức như hệ thống đối xử với dữ liệu: **có nguồn (provenance), có TTL, có version, có errata** — bốn thứ này là SLA của độ tin cậy.

### 2.2 Năm nhãn nguồn

| Nhãn | Nghĩa | Quy tắc dùng | Ví dụ |
|---|---|---|---|
| **P** (Primary) | nguồn sơ cấp: docs nhà sản xuất, RFC, tiêu chuẩn, paper gốc | ưu tiên tuyệt đối khi mâu thuẫn | FIPS 203 cho ML-KEM (10.2) |
| **I** (Independent) | đo lường/benchmark độc lập, nghiên cứu tái lập được | ghi nguồn + điều kiện đo | độ trễ bộ nhớ bậc ns (1.1) |
| **V** (Vendor) | tài liệu/hành vi nhà cung cấp (marketing có thể pha) | chỉ cho hành vi sản phẩm cụ thể | bảng giá egress (9.3) |
| **E** (Estimate) | ước tính của tác giả từ suy luận | **phải** ghi "ước tính" + cơ sở | 0,2–0,5 FTE/service (11.6) |
| **-** (Cắt) | không có nguồn đáng tin — đã cắt | danh sách cắt giữ trong errata | con số perf chưa công bố |

Luật xếp hạng mâu thuẫn: **P > I > V**; E không bao giờ thắng ai; không nhãn nào được ngầm — **không nhãn = chưa kiểm tra**.

### 2.3 Ba hạng phân rã (decay)

| Hạng | Tuổi thọ | Loại nội dung | Ví dụ |
|---|---|---|---|
| 🔥 | ~4 tuần | giá, phiên bản patch, trạng thái service | versions.csv (verify 30/10) |
| 🌡 | ~1 quý | chuẩn draft, roadmap, chính sách vendor | MCP revision (12.4) |
| 🧊 | ~1 năm+ | khái niệm, định lý, pattern, kinh nghiệm ngành | CAP/Raft (8.x) |

Mục "Bảng số & phiên bản" mỗi chương mang 🔥/🌡 đều **phải có ngày kiểm tra** (chương ghi rõ "đã verify 30/10/2026" theo nhịp 11.8 §2.4). Sách hứa: nội dung 🧊 ổn định nhiều năm — không dùng 🧊 làm cớ cho số 🔥 không cập nhật.

### 2.4 Errata — quyền được sai có kỷ luật

Sai sót ghi công khai: vị trí, cái sai, nguồn đúng, ngày sửa. Ba nguyên tắc: (1) **cứ đúng nguồn, không cãi tay đôi** — ai đưa được P/I cao hơn, mục được sửa và người chỉ ra được ghi nhận; (2) mỗi ấn bản đóng băng đi kèm **danh mục thay đổi** (như changelog của 9.7); (3) sai số liệu (🔥) ưu tiên sửa hơn sai khái niệm (🧊 hiếm sai — nhưng khi sai là nghiêm trọng, sửa toàn bộ chuỗi chương liên quan).

### 2.5 Quy trình verify một con số (đúng như đã làm cho versions.csv)

1. Tìm **P** trước (docs chính thức/API nhà cung cấp — endoflife.date là tổng hợp có nhãn nguồn tới P);
2. Không có P: tìm ≥2 nguồn **I** độc lập đồng hướng — chỉ ghi như "bậc độ lớn" (không ghi chính xác giả);
3. Chỉ có V: ghi kèm "theo docs <vendor>, ngày X";
4. Không đủ: **E hoặc cắt** — và ghi vào errata danh sách cắt (điều này từng xảy ra: số liệu perf không công bố bị loại khỏi 1.8/5.16 thay vì ghi bừa);
5. Ghi ngày kiểm tra cạnh con số — xong việc với nó cho tới chu kỳ tới.

### 2.6 Chống phân rã của chính cuốn sách

Cấu trúc chống cũ đi ba lớp: **nội dung 🧊 làm xương** (75%+ dung lượng), **số 🔥/🌡 cô lập** vào mục "Bảng số & phiên bản" (dễ cập nhật một chỗ — không rải trong văn), **versions.csv là kho trung tâm** (một nguồn — nhiều đầu ra, nguyên tắc của chính build pipeline). Khi con số chết: sửa một file, build lại — ấn bản mới ra trong cùng ngày.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị | Nhãn |
|---|---|---|
| Số nhãn nguồn | 5 (P/I/V/E/-) | V |
| Số hạng phân rã | 3 (🔥/🌡/🧊) | V |
| Chu kỳ đóng băng | hàng quý | P |
| versions.csv lần verify | 30/10/2026 (52 hàng) | P |

---

## 4. Suy luận kiến trúc

- **S1:** Nhận thức luận của sách = **data governance của tri thức** (5.13/5.14 áp cho chính atlas): nguồn, tuổi, quyền sửa, danh sách cắt;
- **S2:** "Thà thiếu hơn sai" là nguyên tắc phân bổ niềm tin: một con số sai phá hoại **toàn bộ** uy tín của các con số đúng xung quanh — giá trị biên của sự trung thực rất cao;
- **S3:** Đóng băng theo quý đổi tính tươi lấy **khả năng trích dẫn** — wiki không trích được ("bản nào?"); ấn bản trích được — và trích dẫn là cách sách tham gia hệ sinh thái tri thức;
- **S4:** Chuỗi nhãn P/I/V áp cho **người đọc** khi đọc bất kỳ tài liệu nào: docs vendor là V (dù uy tín — 9.7 từng ghi: docs cũng là artifact có bias); đào sâu nguồn là kỹ năng thuộc 11.8;
- **S5:** AI làm provenance **khẩn cấp hơn**: nội dung sinh ra không nhãn nguồn (12.1 xác suất); mọi tổ chức dùng AI viết tài liệu cần cài lại đúng bộ máy này (nhãn + ngày + errata) — nếu không, nội bộ sẽ đầy "sự thật không nguồn" trong một quý;
- **S6:** Khi trích atlas ra ngoài (report/học): kèm nhãn + ngày — quy tắc một dòng, giữ cho người trích không trở thành kẻ vô tình phát tán số đã chết.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân | Lệnh chẩn |
|---|---|---|
| Trích số cũ vào báo cáo | Không xem ngày kiểm tra | nhãn 🔥 + ngày |
| Hai nguồn mâu thuẫn, bế tắc | Chưa xếp P/I/V | bảng §2.2 |
| "Con số này chắc đâu có sẵn" | Không có P/I — đang bịa | quy tắc E hoặc cắt |
| Wiki nội bộ không ai tin | Không version/errata | đóng băng + changelog |
| Sửa một số phải rà cả sách | Số rải trong văn | cô lập vào mục bảng số |

---

## 6. Cách đo

```bash
# Chất lượng nguồn của chính tài liệu bạn viết (đo 10 phút):
#   chọn 10 con số gần nhất bạn ghi — mỗi con: nhãn nào? ngày nào? nguồn đâu?
#   < 5/10 trả lời được = tài liệu đang phát tán rủi ro (và ai đó sẽ trích)

# Đặt lịch verify: 🔥 hằng tháng, 🌡 hằng quý, 🧊 hằng năm —
#   giống 11.8 §2.4; một buổi, giữ cả kho tài liệu sống
```

Nguyên tắc: **con số không có ngày sinh thì không có ngày chết — và không đáng tin lúc nào**.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay nhãn 5 mức:** chỉ P vs non-P (đơn giản, mất khả năng nói "đo độc lập"); **thay đóng băng:** liên tục với git tag mỗi quý — hợp lệ nếu có quy ước trích "tag SA-2026.Q4" (chính là phiên bản kỹ thuật của ấn bản).

Năm thấu kính:
- **Kinh tế:** Verify tốn giờ — nhưng một con số sai trong hợp đồng/RFP tốn nhiều hơn bậc độ lớn; kho số có nhãn là **bảo hiểm uy tín**;
- **Vận hành:** Danh sách cắt + errata là **backlog của tri thức** — có owner, có nhịp, không khác bug queue;
- **An ninh:** Nhãn nguồn chính là **trust boundary của tri thức** (10.1): tin nhầm nguồn V như tin request không xác thực;
- **Lịch sử:** Từ trích chú cuối sách (in một lần, sai mãi mãi) → errata trên web → nhãn TTL + verify định kỳ: khoa học và kỹ thuật cùng đi về hướng **kiến thức có hạn sử dụng ghi rõ**;
- **Người dùng:** Người đọc xứng đáng biết mình đang đứng trên đá nào — chương này là lời hứa cuối (và quan trọng không kém lời hứa đầu ở 0.2) của atlas với người đọc.

---

## 8. Đọc tiếp & bài tập

- Tiên đề: **0.2** · Nhịp verify/EOL: **11.8** · Data governance: **5.13, 5.14** · Trust boundary: **10.1** · Một nguồn nhiều đầu ra: **9.6** · versions.csv hiện vật: `facts/versions.csv`
- **Bài tập 1:** Đo 10 con số bạn viết gần nhất theo §6 — tỉ lệ có nhãn+ngày là "điểm provenance" cá nhân của bạn;
- **Bài tập 2:** Lập errata cho chính tài liệu team (danh mục: sai đã biết, số đã chết, mục đã cắt) — công khai nội bộ; lần đầu sẽ khó chịu, sau đó nó trở thành tài sản;
- **Bài tập 3:** Chuyển 5 con số nóng nhất (giá, phiên bản, giới hạn) vào một file "versions nội bộ" + lịch verify — copy nguyên mô hình versions.csv của atlas.
