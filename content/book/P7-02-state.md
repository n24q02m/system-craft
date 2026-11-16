# 7.2 — Phân loại Trạng thái & Kiến trúc Data Fetching

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** web frontend · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 7.1 · 4.8 (tư duy cache-control).

**Sợi chỉ đỏ:** *Trang đã mở — dữ liệu nó đang nắm là của ai, tới khi nào là cũ?* — trả lời: state frontend rối vì cố nhét những thứ khác bản chất vào một biến — chương này tách năm loại, mỗi loại một chủ một nhà; server state thật ra là cache với độ tươi và chính sách làm mới; và URL là state bậc nhất. Câu hỏi để lại cho chương sau: *JS mỗi tuần nặng thêm — bundle budget và INP giữ bằng cách nào?*

**Thuật ngữ sẽ gặp:** *năm loại state* — server, URL, form tạm, UI cục bộ, thứ tự sắp xếp: mỗi loại một chủ và một vòng đời; *server state = cache* — bản sao của dữ liệu bên kia mạng: có thể cũ, có thể mất, luôn cần độ tươi; *URL là state* — filter, tab, trang đưa lên URL: chia sẻ được, back đúng được; *ba trường phái fetching* — fetch rồi render, streaming, prefetch: đổi chỗ chờ; *stale-while-revalidate* — trả bản có sẵn trong lúc lấy bản mới (nối 6.5); *validation hai lớp* — client cho nhanh, server cho đúng: một lớp là sai.

**Ví dụ mở đầu:** Filter "giao trong 30 phút" của DM nằm trong biến JS: khách bấm back là mất, gửi link cho bạn là không mở lại được. Đưa lên URL — mọi thứ tự nhiên chia sẻ được. Phân state đúng nhà lấy đi nửa khối lượng bug kiểu "dữ liệu này cũ thế mà vẫn hiện".

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Phân loại state: server-cache / URL / UI / form / module | Trạng thái này sống sót qua refresh không? qua logout không? |
| 2 | Ai là nguồn chân lý cho từng loại | Nếu hai nơi cùng giữ — ai thắng khi lệch? |
| 3 | Chiến lược fetch: loader/route, query cache (TanStack/SWR), RSC fetch | Dữ liệu này gắn route hay gắn component? |
| 4 | Cache & làm mới: staleTime, invalidation, optimistic update | Sai số tôi chấp nhận bao lâu — và ai báo cho user? |

---

## 2. Cơ chế

### 2.1 Năm loại state — mỗi loại một chủ, một nhà

| Loại | Ví dụ | Chủ/sở hữu | Chết khi | Công cụ |
|---|---|---|---|---|
| **Server state** (cache) | danh sách sản phẩm | server (client chỉ cache) | invalidate/refetch | TanStack Query, SWR, RSC cache |
| **URL state** | filter, tab, trang | URL (shareable) | đổi route | router params/search |
| **UI state** | dropdown mở, modal | component | unmount | useState/store nhẹ |
| **Form state** | giá trị đang nhập, validation | form | submit/reset | react-hook-form, formik |
| **Client domain state** | giỏ hàng offline | client store | logout/clear | Zustand/Redux/valtio |

Bệnh phổ biến: **đổ mọi thứ vào một store toàn cục** (Redux cho tất cả) — mất phân biệt "ai là chủ": server data trong store toàn cục tự tay viết loading/error/invalidation = tự chế query cache tệ hơn thư viện; URL state trong store = mất deep link/share.

### 2.2 Server state là "cache" — nhớ điều đó mọi thứ sáng ra

Client giữ **bản sao tạm** của dữ liệu server: cần `staleTime` (bao lâu coi là tươi), `refetchOnFocus` (đúng khi dữ liệu đổi nhanh), **invalidation theo khoá** (sau mutation `X` → invalidate `['orders']`). Mọi tính năng "cập nhật sau khi lưu" là bài cache invalidation (→6.5 cùng toán, khác tầng). Optimistic update = ghi đè cache cục bộ trước, rollback nếu server từ chối — bắt buộc cho UX "nhanh", bắt buộc cả idempotency (→4.8).

### 2.3 URL là state bậc nhất

Filter/tab/search nằm trong URL: copy gửi được, back đúng, refresh đúng. Chuẩn: `?q=áo&tab=reviews&page=2` — mọi thao tác UI thay bộ lọc = `router.replace` với query mới (kèm `scroll: false` khi cần). Khi một trạng thái ảnh hưởng đến "cái người dùng đang nhìn" — mặc định để nó vào URL; UI state đúng nghĩa chỉ là thứ không ai muốn chia sẻ (hover, mở modal).

### 2.4 Data fetching — ba trường phái

1. **Route-level loader** (SvelteKit/Next server): fetch trước khi render — SEO + không waterfall; hợp dữ liệu "khung trang";
2. **Component-level query cache** (TanStack Query/SWR): khoá query, dedupe, retry, focus-refetch — hợp dữ liệu thành phần + tương tác;
3. **RSC fetch**: component server fetch trực tiếp (song song tự nhiên), client nhận kết quả — hợp khi dữ liệu không cần interactive.

Thực chiến trộn cả ba: khung bằng loader/RSC, chi tiết tương tác bằng query cache. Quy tắc chống waterfall: **mỗi cấp component không đợi cấp trước xong mới bắt đầu fetch** — bắt song song ở loader, hoặc defer phần dưới-fold (→7.1 streaming).

### 2.5 Form & validation: hai lớp

Client validate để **phản hồi nhanh** (UX); server validate để **đúng** (an toàn — →6.7). Hai lớp dùng chung schema (zod/valibot) — một định nghĩa, hai nơi chạy (kỹ thuật "một nguồn" của chương này). Không bao giờ chỉ client: payload tự viết bỏ qua validate client là bài học đầu tiên của mọi kẻ lạm dụng API.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| staleTime hợp lý | theo nghiệp vụ (s–phút) | P | |
| dedupe window | ~vài s (query cache) | V | mặc định thư viện |
| Zustand vs Redux bundle | ~1 KB vs ~10+ KB | I | |
| zod schema dùng 2 nơi | client + server | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Mỗi loại state một chủ sở hữu duy nhất — quyết định sở hữu là quyết định kiến trúc; hai chủ = lệch nhau sớm hay muộn.
- **S2:** Tham số trụ: tỉ lệ refetch lãng phí (đếm request trùng khoá), stale-đã-báo (mutation xong UI không cập nhật), deep-link pass rate (mở URL đồng nghiệp — giống màn hình không?).
- **S3:** Optimistic update đổi UX lấy rủi ro rollback hiếm; URL-state đổi "đẹp code" lấy router kỷ luật — cả hai đáng tiền nếu đo được.
- **S4:** Server-state-as-cache khiến frontend hội tụ với backend: cùng khái niệm cache/invalidation (→6.5), cùng idempotency (→4.8) — từ vựng chung giảm nửa cuộc họp.
- **S5:** AI copilot sinh code state rất nhanh nhưng trộn loại (UI state lên store toàn cục) — review theo bảng §2.1 là checklist nhanh nhất; schema dùng chung giúp agent hiểu biên.
- **S6:** Khi "dữ liệu hai chỗ khác nhau": tìm chủ sở hữu của state đó — gần như luôn phát hiện hai chủ (store + query cache); hợp nhất theo bảng, không vá từng điểm.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Lưu xong UI không đổi | Thiếu invalidate khoá | audit mutation→invalidation | §2.2 |
| Refresh mất filter | State không nằm trong URL | chuyển sang search params | §2.3 |
| Request dồn trùng | Thiếu dedupe/staleTime | query cache keys + stale | §2.2 |
| Load "nước xoáy" | Waterfall cấp component | song song hóa loader | §2.4 |
| Validate lệch client/server | Hai bộ rule | schema dùng chung | §2.5 |
| Hai tab lệch nhau | Không refetchOnFocus | stale policy | §2.2 |

---

## 6. Cách đo

```ts
// Query cache devtools: đếm request theo khoá trong 60 giây dùng app thật
//   — khoá nào refetch > 3 lần không đổi dữ liệu = staleTime sai

// Deep-link test: 5 URL (filter/tab/chi tiết) mở incognito —
//   khôi phục đúng màn hình? Mỗi URL hỏng là một bug state ownership
```

Nguyên tắc: **đo state bằng "thí nghiệm làm rối"** — refresh, back, mở tab mới, hai tab song song: mọi lỗi lộ ra là lỗi sở hữu, không phải lỗi code lẻ.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay query cache:** tự fetch + useState (đúng cho app nhỏ — mọi loading/error/loading tay là tín hiệu đã đến lúc thư viện); **thay store toàn cục:** context + useState cho scope nhỏ, chỉ lên store khi thật cần chia sẻ rộng — mặc định là "không cần".

Năm thấu kính:
- **Kinh tế:** Query cache tiết kiệm request (tiền hạ tầng) + giờ dev (loading/error viết sẵn); chi phí là học khái niệm khoá/invalidation — hoàn vốn từ sprint thứ hai.
- **Vận hành:** State bugs là dạng khó tái lập nhất của FE — phân loại rõ (§2.1) biến bug "ma" thành bug có nhãn, đỡ nửa thời gian triage (→7.6).
- **An ninh:** Client store giữ dữ liệu sau logout là lỗi rò rỉ thật — logout phải xoá theo loại (server cache, store, storage) — checklist release bắt buộc (→7.7).
- **Lịch sử:** Flux/Redux (2015) dạy "một store toàn cục" cho một thời SPA non trẻ; hooks + query cache (2019+) phân mảnh lại theo "chủ sở hữu" — bài học lặp: kiến trúc đi theo quyền sở hữu, không theo sự đồng đều.
- **Người dùng:** Người dùng không biết state là gì — họ biết "lưu xong thấy ngay, bấm back không mất, gửi link cho bạn mở ra giống hệt". Ba câu đó là toàn bộ §2.2–2.3.

---

## 8. Đọc tiếp & bài tập

- Render & loader: **7.1** · Bundle: **7.3** · Cache CDN (cùng toán): **6.5** · Idempotency: **4.8** · Logout/data leak: **7.7**
- **Bài tập 1:** Với app bạn, liệt kê 10 biến state quan trọng nhất; gán nhãn theo bảng §2.1. Mỗi biến không gán được nhãn = tranh chấp sở hữu ngầm.
- **Bài tập 2:** Mở app ở 2 tab, thao tác bên trái, nhìn bên phải. Không cập nhật sau 30 giây? staleTime/refetchOnFocus đang mặc định sai cho nghiệp vụ của bạn.
- **Bài tập 3:** Chọn một form chính: kiểm tra validate có dùng chung schema với server không. Hai nơi viết riêng? Thống nhất — đó là giảm 50% bug validate tương lai.
