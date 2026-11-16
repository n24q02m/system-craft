# 11.6 — Kiến trúc Tổ chức: Conway, Team Topologies, ADR/RFC, Tech Debt

> **Tầng:** Vận hành · **Quyển II** · **Trục đọc:** tổ chức · **Động từ liên quan:** Quyết · Duy trì
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 9.6 (IaC, IDP — tổ chức đã gặp) · 8.6 (ranh giới, ownership).

**Sợi chỉ đỏ:** *Hệ thống là tổ chức — Conway, ADR, on-call nói gì về team của DM?* — trả lời: hệ thống là tổ chức — luật Conway: kiến trúc hệ thống chép lại kiến trúc giao tiếp, muốn kiến trúc khác thì phải đổi giao tiếp; Team Topologies cho bốn loại team và ba kiểu tương tác; ADR là hộ chiếu của quyết định; tech debt có sổ kế toán; sunset là việc của người trưởng thành. Câu hỏi để lại cho chương sau: *Kỳ họp với kế toán và pháp lý — nói ngôn ngữ gì cho hai bên cùng thấy rủi ro?*

**Thuật ngữ sẽ gặp:** *luật Conway* — hệ thống chép hình trục giao tiếp: người không tách thì code không tách; *bốn loại team* — stream-aligned, platform, enabling, complicated-subsystem: ba kiểu tương tác; *ADR* — bối cảnh, quyết định, hệ quả: hộ chiếu để ba năm sau khỏi đoán lại; *tech debt là kế toán* — ước lượng lãi suất từng món: nợ không ghi sổ là nợ ngầm; *sunset* — giết hệ thống cũ có kế hoạch: năng lực hiếm, dấu trưởng thành; *cognitive load* — tải nhận thức là giới hạn thật: chọn kiến trúc theo nó.

**Ví dụ mở đầu:** Muốn tách service thanh toán khỏi đơn hàng của DM? Nhìn sơ đồ tổ chức trước: hai team khác manager, khác OKR — code không tách nếu người chưa tách. ADR ghi "vì sao tách, đổi gì": người mới ba năm sau đọc hộ chiếu thay vì tìm hồ sơ trong đầu người cũ. Đây là atlas của tổ chức.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Team topology: stream-aligned / platform / enabling / complicated-subsystem | Team của tôi sinh ra để phục ai — và có đang làm đúng việc đó? |
| 2 | Quy trình quyết định kiến trúc: ADR/RFC nhẹ hay ủy ban | Quyết định lớn của tôi có vết viết và ngày hết hạn không? |
| 3 | Quản trị tech debt: danh sách, lãi, trả theo lịch | Tôi có bảng nợ (không phải cảm giác "nợ nhiều") không? |
| 4 | Sunset/khai tử hệ thống: tiêu chuẩn và can đảm | Hệ nào đang "sống dở" — và ai dám ký giấy tử? |

---

## 2. Cơ chế

### 2.1 Luật Conway — kiến trúc hệ = kiến trúc giao tiếp

Tổ chức thiết kế hệ thống sao chép **cấu trúc giao tiếp** của chính nó (Conway, 1967). Hệ quả thực dụng: muốn kiến trúc microservice theo nghiệp vụ (→8.6) thì tổ chức phải có team theo nghiệp vụ — vẽ lại sơ đồ org **trước** thì kiến trúc tự theo; ngược lại (team theo layer: FE/BE/DB) thì microservice sẽ ra theo layer (distributed monolith — 8.6 đã chẩn). "Inverse Conway maneuver" là công cụ quản trị thật, không phải meme.

### 2.2 Team Topologies — bốn loại team, ba kiểu tương tác

- **Stream-aligned** (theo luồng nghiệp vụ: "thanh toán", "vận đơn") — đa số, sở hữu end-to-end;
- **Platform** (nền tảng nội bộ — 9.6 IDP) — phục stream-aligned như khách hàng;
- **Enabling** (huấn luyện: deploy modern practice rồi rút đi) — tạm thời theo chủ đề;
- **Complicated-subsystem** (chuyên sâu: search engine, engine tính giá) — ít, khi thật sự cần.
Tương tác: **collaboration** (cùng làm — tốn, tạm), **X-as-a-Service** (platform cung tự phục vụ — mục tiêu), **facilitating** (enabling giúp team khác). Bệnh chẩn được: platform team làm "helpdesk" mãi không thành service (thiếu golden path — →9.6); stream-aligned thiếu quyền tự chủ (mọi thứ phải hỏi 3 team) — mỗi bệnh có toa ở 9.6/8.6.

### 2.3 ADR/RFC — quyết định có hộ chiếu

ADR (Architecture Decision Record, ~1 trang): **bối cảnh** (ràng buộc, áp lực) → **quyết định** (chọn gì) → **hệ quả** (được/mất, ai chịu) → **ngày hết hạn điều kiện** ("tái xét khi X"). Giá trị: (1) người sau hiểu **vì sao** (không phải "vì thằng trước làm vậy"); (2) tranh luận có nơi chốt (PR của quyết định); (3) quyết định sai **được tìm ra nhanh** (đọc lại ADR, đối chiếu hệ quả thật). RFC cho cái lớn hơn (đa team): bản nháp → phản hồi bất đồng bộ (không họp 10 người) → quyết. Quy tắc vàng: **ADR ghi lựa chọn bị bỏ cũng đáng giá** ("đã cân nhắc Kafka, bỏ vì X" — sau này không ai đề lại từ đầu mỗi năm).

### 2.4 Tech debt — kế toán thật cho thứ vô hình

Metaphor của Ward Cunningham: đi tắt hôm nay, trả lãi mỗi lần đi qua. Quản trị: **danh sách có tên** (không phải "biết trong đầu"), mỗi mục: **lãi** (chi phí hằng ngày: chậm release, bug lặp, on-call đau) + **vốn** (công trả nợ) + **rủi ro nếu không trả**. Ưu tiên trả theo **lãi/vốn** cao (ROI), không theo tiếng kêu to. Ngân sách trả nợ là **% capacity cố định** (10–20%) — có thì nợ được trả đều, không có thì chỉ trả lúc gãy (đắt nhất). Nợ cũng có **lãi kép**: nợ trên nợ (workaround quanh workaround) — dấu hiệu: ai mới vào mất 3 tháng mới dám sửa code.

### 2.5 Sunset — giết hệ thống là việc của người trưởng thành

Mọi hệ thống có ngày hết usefulness: không còn khách dùng, chi phí duy trì > giá trị, rủi ro an ninh (→10.5 CVE không vá). Rào cản thật là **chính trị + sợ hãi** ("biết đâu còn ai dùng"). Quy trình sunset chuẩn: **đo dùng thật** (log/metric — không phỏng đoán) → công bố lịch (EOL như 6.6 đã dạy cho thiết bị) → đường thoát cho người còn dùng (export/migrate — →4.8 deprecation) → tắt từng bước (flag off trước, xoá sau — →8.8) — và **ăn mừng** (t tưởng niệm xóa code là lễ lớn nhất của team). Không sunset = nợ lãi kép vĩnh viễn + mặt bằng an ninh rệu rã.

### 2.6 Trưởng thành và quy mô — công cụ theo cỡ

| Cỡ tổ chức | Công cụ đủ dùng |
|---|---|
| 1–2 team | README "quyết định lớn" + repo đơn — đừng mua quy trình |
| 3–10 team | ADR trong repo + RFC nhẹ + một platform team mầm |
| 10+ team | Team Topologies chủ động + IDP (→9.6) + kiến trúc guild |
Mọi quy trình có chi phí riêng — mua theo cỡ (định luật Yagni lần cuối của Quyển II).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Conway | quan sát 1967 | V | "Organizations design systems..." |
| Team Topologies | sách 2020, phổ biến hoá khung | V | |
| ADR ~1 trang | template chuẩn mở | V | |
| Ngân sách trả nợ | 10–20% capacity | P | |
| Time-to-onboard (đo sức khoẻ code) | < 1 tuần–1 tháng | P | theo độ phức tạp |

---

## 4. Suy luận kiến trúc

- **S1:** Tổ chức và kiến trúc là **cùng một hệ** nhìn từ hai phía — mọi chương kỹ thuật của atlas có "bản org" tương ứng (8.6 ranh giới service = ranh giới team; 11.1 SLO = hợp đồng giữa team và khách...);
- **S2:** Tham số trụ: time-to-first-deploy (→9.6), time-to-onboard người mới, số quyết định lớn không ADR (đếm được qua "vì sao" không trả lời được), tuổi nợ trung bình, số hệ thống sống quá hạn sunset.
- **S3:** ADR đổi "trí nhớ lãnh đạo" lấy "trí nhớ tổ chức" — giá bằng 1 trang giấy; RFC bất đồng bộ đổi giờ họp của 10 người thành giờ đọc của 10 người (rẻ hơn và sâu hơn);
- **S4:** Nợ kỹ thuật là **tài sản quản trị được** khi có danh sách+lãi; không có thì là "tâm trạng" — và tâm trạng không vào được roadmap;
- **S5:** AI đổi cấu trúc công việc hơn công cụ: code sinh nhanh khiến **ranh giới sở hữu và review** là nút cổ chai mới (→9.7) — team size nhỏ hơn + sở hữu rõ hơn trở thành lợi thế (Conway quay lại một lần nữa);
- **S6:** Khi "team kỹ thuật kêu không làm được gì vì cản trở tổ chức": đó là dữ liệu kiến trúc (Conway báo bệnh) — vẽ lại org hoặc chấp nhận kiến trúc như hiện trạng có chủ ý; đứng giữa là đau nhất.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Microservice theo layer | Org theo layer (Conway) | inverse Conway | §2.1 |
| Platform thành helpdesk | Không X-as-a-Service | golden path (→9.6) | §2.2 |
| "Vì sao thế này?" không ai biết | Quyết định không ghi | ADR + review quá khứ | §2.3 |
| Nghĩa lại từ đầu quyết định cũ | Không ghi lựa chọn bị bỏ | ADR ghi cả option bỏ | §2.3 |
| Nợ chỉ được trả lúc gãy | Không ngân sách nợ | 10–20% cố định | §2.4 |
| Hệ chết sống dở 5 năm | Không quy trình sunset | đo dùng + EOL + lễ | §2.5 |

---

## 6. Cách đo

```bash
# "Thử Conway": vẽ sơ đồ org thật (ai báo cáo ai) đè lên sơ đồ service —
#   mỗi cạnh service-to-service chéo 2 team trở lên là "thuế giao tiếp" — đếm.

# Health org bằng 4 câu (khảo sát nặc danh mỗi quý, thang 1-5):
#   1) Tôi deploy được không cần hỏi team khác?
#   2) Quyết định lớn có chỗ ghi và tìm được?
#   3) Tôi có thời gian trả nợ kỹ thuật?
#   4) Tôi biết hệ nào đang chết dần và kế hoạch của nó?
```

Nguyên tắc: **tổ chức đo bằng khả năng hành động của người ở rìa** (deploy mà không xin, quyết mà tìm được hồ sơ) — không bằng sơ đồ đẹp trên slide.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay ADR/RFC:** wiki "quyết định lớn" (được — miễn có ngày và chủ); **thay Team Topologies chính thức:** common sense + inverse Conway khi đau (đa số tổ chức đến đây qua vết thương, không qua sách — sách chỉ rút ngắn); **thay quy trình sunset:** "kéo dài vô hạn" (rẻ hôm nay, đắt mỗi ngày — chọn chủ ý nếu tính rồi thấy vậy ổn).

Năm thấu kính:
- **Kinh tế:** Nợ kỹ thuật là **khoản vay có lãi thật** (chậm release × giá sprint); danh sách nợ + lãi là bảng cân đối kế toán của kỹ thuật — không có thì CFO chỉ thấy "kỹ thuật đòi đầu tư" mà không thấy cấu trúc;
- **Vận hành:** Mỗi ADR có ngày tái xét (thế giới đổi — →12 AI đang đổi nhanh nhất); ADR vĩnh viễn là bia mộ có chữ;
- **An ninh:** Hệ thống sống dở là **mặt tối an ninh** (không chủ sở hữu = không vá — →10.5; không ai review = chỗ nấp của kẻ xấu — →10.1 trust boundary vô chủ);
- **Lịch sử:** Conway (1967, bị từ chối xuất bản Harvard Business Review) → Manual of Mythical Man-Month (1975, "thêm người vào dự án muộn làm muộn hơn") → DevOps (2009) → Team Topologies (2020): 50 năm cùng một phát hiện lặp lại — **vấn đề kỹ thuật lớn nhất là tổ chức** — và mọi thế hệ đặt tên lại cho nó;
- **Người dùng:** "Người dùng" của chương này là nhân viên — và trải nghiệm của họ (deploy không xin, quyết định có hồ sơ, nợ được trả) **rò ra ngoài** thành chất lượng sản phẩm và tốc độ đổi mới; tổ chức không vui thì khách không yên — câu này không thi vị, là dữ liệu (engagement ↔ chất lượng tương quan ở mọi khảo sát lớn).

---

## 8. Đọc tiếp & bài tập

- Platform/IDP: **9.6** · Ranh giới service: **8.6** · Sunset & deprecation API: **4.8, 8.8** · DORA (đo tổ chức giao hàng): **9.7** · Vành liên ngành: **11.7**
- **Bài tập 1:** Chạy "thử Conway" (§6): đếm cạnh service chéo team. Top 3 cạnh tốn nhất — mỗi cạnh một đề xuất (gộp team / tách service / thêm hợp đồng API — 8.6);
- **Bài tập 2:** Viết 3 ADR cho 3 quyết định lớn nhất 6 tháng qua (nếu không có sẵn). Gọi ý: frame "bối cảnh–quyết–hệ quả–hạn" — phần "hạn" sẽ làm bạn nhận ra quyết định nào đã quá hạn tái xét;
- **Bài tập 3:** Lập bảng tech debt: 5 mục, mỗi mục lãi (chậm gì, đau gì — đo/th phỏng) + vốn + rủi ro. Xếp theo lãi/vốn và đề xuất trả mục đầu trong ngân sách quý sau. Bảng này chuyển "nợ nhiều lắm" thành phê duyệt ngân sách.
