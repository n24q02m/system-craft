# 8.6 — Kiến trúc Phần mềm: Monolith, Microservices, DDD, CQRS, Event Sourcing

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** kiến trúc ứng dụng · **Động từ liên quan:** Chọn · Duy trì
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.4 (service gọi service) · 8.3 (giao dịch chạm nhiều service).

**Sợi chỉ đỏ:** *Service đã đông — ranh giới nào mới đúng (bounded context, sở hữu dữ liệu)?* — trả lời: service đông là kết quả chứ không phải mục tiêu — ranh giới đúng vẽ bằng DDD: bounded context, mỗi context sở hữu dữ liệu của mình; monolith và microservices có bảng giá thật; CQRS, event sourcing là hai công cụ; và bốn câu kiểm "đáng phân tán không" trước khi trả giá. Câu hỏi để lại cho chương sau: *Cháy nguyên một vùng — multi-region/DR cam kết gì (RTO, RPO) và trả bao nhiêu?*

**Thuật ngữ sẽ gặp:** *bounded context* — ranh giới trong đó một mô hình có ngữ nghĩa nhất quán: "đơn" của bếp khác "đơn" của kế toán; *sở hữu dữ liệu* — đúng một chủ ghi cho mỗi dữ liệu: chủ khác đọc qua hợp đồng (nối 4.3); *bảng giá thật* — network hop, vận hành, debug phân tán: không thấy trong demo; *CQRS* — model đọc tách model viết: giải pháp cuối cho query nặng, không mặc định; *event sourcing* — trạng thái là hàm của sự kiện: audit miễn phí, tái dựng được (nối 5.15); *bốn câu kiểm* — "đáng phân tán không": bốn câu, trả lời trước khi trả tiền.

**Ví dụ mở đầu:** "Đơn" trong đầu bếp là món nào đang nấu; trong đầu kế toán là doanh thu chưa đối soát — ép chung một model là chiến trường đổi tên trường không hồi kết. Bounded context cho mỗi bên một model và một chủ. Chương này dạy vẽ ranh giới bằng DDD thay vì bằng sơ đồ tổ chức.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Monolith hay microservices — bây giờ và lộ trình | Team tôi mấy người và năng lực ops có nuôi nổi phân tán không? |
| 2 | Ranh giới service vẽ theo gì (DDD bounded context?) | Sắp đổi model ở đây — có kéo theo hệ khác không? |
| 3 | CQRS có đáng không, cho Context nào | Đọc và viết của tôi khác nhau cỡ nào (tỉ lệ, model, scale)? |
| 4 | Event Sourcing: thật sự cần event là nguồn chân lý? | Tôi có cần "diễn biến" hay chỉ cần "trạng thái"? |

---

## 2. Cơ chế

### 2.1 Monolith → microservices: bảng giá thật

| | Monolith (modular) | Microservices |
|---|---|---|
| Gọi nội bộ | hàm (ns–µs) | mạng + serialize (ms) (→4.4) |
| Giao dịch | 1 DB, ACID | saga/outbox (→8.3) |
| Deploy | cả app | từng service (đổi API phải additive — →4.8) |
| Debug | 1 stack trace | trace phân tán (→11.1) |
| Scaling | cả khối | theo service |
| Team | 1 codebase chung | ownership riêng (Conway) |
| Sự cố | sập chung | sập dây chuyền (→8.5) |

Microservices mua **autonomy tổ chức + scale chọn lọc** bằng **độ phức tác phân tán trả trước** (mọi chương 8.x là hoá đơn). Luật thực dụng: **microservices là giải pháp cho bài toán TỔ CHỨC (nhiều team đụng nhau) và SCALE khác biệt (compute khác nhau cỡ 10×+)** — không phải style đẹp hơn; đa số sản phẩm dưới ~20–50 dev hạnh phúc hơn với **modular monolith** (một deploy unit, module rạch ròi, ranh giới "hot" tách sau khi đúng).

### 2.2 DDD — kỹ thuật vẽ ranh giới

Bộ khái niệm dùng được: **Bounded Context** (mỗi ngữ cảnh có model riêng — "Order" ở bán hàng ≠ ở kho ≠ ở kế toán); **Ubiquitous language** (mỗi context một từ điển thống nhất giữa dev & nghiệp vụ); **Aggregate** (khối nhất quán trong 1 giao dịch — gốc quyết định "giao dịch đi đâu"); **Anti-corruption layer** (bọc hệ cũ khi tích hợp). Aggregate nhỏ + context rõ = service sau này tách rẻ; aggregate vô định (mọi thứ dính nhau) = microservices biến thành **distributed monolith** — tệ nhất của hai thế giới (latency mạng + coupling logic).

### 2.3 CQRS — tách model đọc khỏi model viết

Ghi theo nghiệp vụ chuẩn hoá (normalize), đọc theo màn hình (denormalize/view): tách hai đường + đồng bộ qua sự kiện → mỗi bên tối ưu riêng (viết chặt chẽ, đọc nhanh theo query). Chi phí: **độ trễ eventual giữa hai bên** (vừa lưu, view chưa cập nhật — phải thiết kế UI báo "đang xử lý") + hạ tầng projection phải nuôi. Dùng chọn lọc: module đọc nặng (search, báo cáo, feed) — không CQRS cả hệ thống (CRDT-tưởng-tượng bệnh của resume-driven design).

### 2.4 Event Sourcing — trạng thái là hàm của sự kiện

Lưu chuỗi sự kiện (`OrderPlaced`, `ItemAdded`...) thay vì bản ghi cuối; **trạng thái = replay** (như WAL của DB — →5.1 — nhưng nâng lên tầng nghiệp vụ, và như oplog/vết trước đó của 5.15). Được: audit hoàn hảo (ai làm gì khi nào), time travel, projection mới từ dữ liệu cũ, undo nghiệp vụ (event bù). Trả: **đọc cần projection** (replay mỗi lần đọc là chết), **schema evolution của event** (event sống năm năm — version hoá từ ngày đầu), **GDPR/right-to-be-forgotten** (không xoá dòng trong log bất biến — phải crypto-shred — →5.13), discipline tổ chức cao. Quy tắc chọn: cần "diễn biến" là yêu cầu nghiệp vụ (khai khoán, giao dịch tài chính, bidding) → dùng; chỉ cần trạng thái → **đừng** (dùng DB + outbox đủ — →8.3).

### 2.5 Kiểm tra "đáng phân tán không" — bốn câu

1. Hai phần đổi **vận tốc khác nhau** thật không (release hàng ngày vs hàng quý)?
2. Hai phần **scale khác nhau** thật không (10× trở lên)?
3. Hai phần **công nghệ khác nhau** đáng giá (library không dùng chung được)?
4. Ranh giới nghiệp vụ **ổn định** (đã 6 tháng không đổi model xuyên)?
4× "có" → tách; một câu "không" rõ ràng → giữ monolith module hoá. Câu 4 hay bị bỏ qua: tách theo ranh giới đang **dao động** là mua sự cố (mỗi refactor thành dự án dịch chuyển dữ liệu).

### 2.6 Trạng thái 2026 để ghi nhớ

- **Modular monolith** được "công nhận lại" như lựa chọn mặc định khôn ngoan (các nền tảng lớn công khai giữ monolith core + tách chọn lọc);
- **Service mesh/sidecar** giảm chi phí vận hành của phân tán (→9.4) — hạ giá vào bàn microservices nhưng không xoá hoá đơn độ phức tạp nghiệp vụ (8.3/8.5 vẫn phải trả);
- **Vertical slice + cell architecture (→8.7)** là hướng "phân tán có kiểm soát" của SaaS lớn: theo tenant, không theo layer kỹ thuật.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Gọi nội bộ: hàm vs mạng | ns–µs vs ms (nghìn×) | I | |
| Ngưỡng "đáng tách" scale | ~10× khác biệt | P | |
| Team/service hợp lý | 1 team sở hữu ≥ 2–5 service | P | ngược lại là phân mảnh |
| Event schema sống | năm (version hoá bắt buộc) | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Kiến trúc phục vụ **lịch trình thay đổi của tổ chức** (Conway) — quyết định số một là "ai sở hữu cái gì, đổi với vận tốc nào"; style kỹ thuật là hạ tầng cho quyết định đó.
- **S2:** Tham số trụ: tỉ lệ deploy xuyên service thành công, thời gian từ "đổi model" đến "ship" theo context, chi phí gọi chéo (số call/request), độ trễ projection p95 (nếu CQRS).
- **S3:** CQRS/ES đổi **độ phức tạp đọc/audit** lấy eventual consistency + hạ tầng projection — chỉ đáng ở module có sự chênh model đọc/viết thật (dùng bảng 4 câu §2.5 mở rộng).
- **S4:** Mọi công cụ 8.x (outbox 8.3, chịu lỗi 8.5, đồng thuận 8.2) là **điều kiện sống của microservices** — tổ chức thiếu những chương đó mà tách service là mượn tiền mua rủi ro.
- **S5:** AI copilot làm chi phí **viết** code giảm mạnh → giá trị kiến trúc dịch sang **ranh giới đúng** (module/service/context), vì ranh giới quyết thứ AI không tự sửa được: sở hữu dữ liệu và lịch trình thay đổi.
- **S6:** Khi "mọi thay đổi đều đụng 5 hệ": đó là triệu chứng **ranh giới sai** (aggregate chéo), không phải "thiếu công cụ orchestration" — vẽ lại ranh giới (2.2) trước khi thêm tầng phối hợp.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Distributed monolith | Tách theo layer, không theo nghiệp vụ | vẽ bounded context lại | §2.2 |
| Gọi chéo 10 hops/request | Ranh giới sai + chat gọi vòng | trace đếm hops (→11.1) | §2.1 |
| "Vừa lưu không thấy" | CQRS eventual, UI không báo | projection lag + UI state | §2.3 |
| Event cũ không replay được | Schema evolution thiếu version | audit event schema | §2.4 |
| Release phải đi cùng 3 team | Coupling deploy ngầm | hợp nhất hoặc hợp đồng API additive (→4.8) | §2.5 |
| Đội mỏi vì 20 service 6 dev | Phân mảnh ownership | gộp lại modular monolith | §2.6 |

---

## 6. Cách đo

```bash
# Sức khoẻ ranh giới (mỗi quý, 1 giờ):
#   1. Đếm call chéo service cho 5 endpoint chính (từ trace) — xu hướng tăng = ranh giới mòn
#   2. Đếm PR đụng >2 repo cho 1 tính năng — tăng = coupling tổ chức
#   3. Đo "time-to-ship" một đổi model nhỏ trong 1 context — tăng = dính nhau
```

Nguyên tắc: **ranh giới tốt đo bằng chi phí thay đổi** (PR nhỏ, 1 repo, 1 team) — không đo bằng số service trên slide.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay microservices:** modular monolith + module theo bounded context (giữ lựa chọn tách sau); **thay event sourcing:** DB + audit log + outbox (đủ cho đa số "muốn audit"); **thay CQRS:** replica đọc + index (5.2) — nhiều khi "đọc chậm" chỉ là thiếu index đúng.

Năm thấu kính:
- **Kinh tế:** Mỗi service = một pipeline CI/CD + dashboard + on-call + bảo mật riêng: ước 0,2–0,5 FTE/service/năm vận hành (P) — nhân 40 service rồi so với lợi ích autonomy.
- **Vận hành:** Ranh giới sai không "sửa dần" được — nó là nợ lãi kép (mỗi tính năng trả thuế); cho phép quyết định "gộp lại" định kỳ là dấu hiệu tổ chức trưởng thành.
- **An ninh:** Service ranh giới là ranh giới dữ liệu (token scope hẹp per service — →10.1) — monolith một token toàn quyền là mặt diện lớn hơn; ngược lại nhiều service = nhiều bề mặt tấn công mạng nội bộ (mesh mTLS — →9.4).
- **Lịch sử:** SOA (2000s, chuẩn nặng) → microservices (2010s, nhẹ) → "monolith is fine" phản ứng (2020s) → cell/vertical (hiện tại): mỗi thế kỷ lặp lại cuộc tranh luận "gần hay xa" — đáp án luôn là "theo ranh giới thay đổi", chỉ công cụ thay đổi.
- **Người dùng:** Người dùng không biết kiến trúc — họ biết "tính năng ra đều, không vỡ". Mỗi lựa chọn chương này là chọn **ai được phép làm chậm ai**; người dùng chỉ cảm nhận được qua điều đó.

---

## 8. Đọc tiếp & bài tập

- Giao dịch chéo service: **8.3** · Chịu lỗi chuỗi: **8.5** · Ranh giới & ownership API: **4.8** · Cell/multi-region: **8.7** · Domain/data silo-bridge-pool: **5.14**
- **Bài tập 1:** Vẽ bounded context của sản phẩm bạn (bảng + mũi tên dịch thuật giữa context). Nếu một danh từ có 3 nghĩa khác nhau ở 3 phòng — bạn vừa tìm thấy 3 context thật (và khả năng cao: 1 service đang gánh 3 nghĩa).
- **Bài tập 2:** Chọn 1 tính năng mới gần nhất: đếm số repo/service/PR phải mở. > 3? Ghi lại đường đi — đó là bản đồ "thuế ranh giới" hiện tại của bạn.
- **Bài tập 3:** Với mỗi service đang có: trả lời 4 câu §2.5. Service nào 4×"không" — ứng viên gộp; danh sách đó là đề cương kiến trúc quý sau.
