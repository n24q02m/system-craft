# 7.1 — Kiến trúc Rendering & Routing (CSR/SSR/ISR/RSC)

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** web frontend · **Động từ liên quan:** Chọn · Thiết kế
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 6.5 (edge/CDN — tầng ngay dưới).

**Sợi chỉ đỏ:** *Mặt tiền web chính là sản phẩm — trang tải và vẽ thế nào cho người ở lại?* — trả lời: bốn chế độ render — CSR, SSR, SSG, islands — mỗi chế độ mạnh một kiểu theo "trang nào cần gì", nên chọn theo trang chứ không theo app; routing là hợp đồng cấu trúc; và TTFB, LCP, INP đọc khác nhau theo từng chế độ. Câu hỏi để lại cho chương sau: *Trang đã mở — dữ liệu nó đang nắm là của ai, tới khi nào là cũ?*

**Thuật ngữ sẽ gặp:** *CSR* — client render: chậm lần đầu, mượt về sau; *SSR* — server dựng HTML: thấy nhanh, tương tác đầu chậm hơn; *SSG* — dựng sẵn lúc build: nhanh nhất, đổi là build lại; *islands / partial hydration* — khung tĩnh, "đảo" tương tác hydrate đúng chỗ cần; *streaming* — gửi HTML từng phần: phần sẵn sàng ra trước, phần còn lại theo sau; *TTFB / LCP / INP* — ba mốc khách thấy và chạm được: chỉ có nghĩa khi đo theo chế độ.

**Ví dụ mở đầu:** Trang menu DM cần SEO (nội dung tĩnh), giỏ hàng cần tương tác tức thì, kết quả tìm kiếm cần mới nhất: ba trang — ba chế độ, trong cùng một app. Cuộc chiến "framework nào tốt hơn" đa số là tranh nhau một chế độ duy nhất. Chương này là bản đồ bốn chế độ và phép chọn theo từng trang.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Chiến lược render theo route: CSR/SSR/SSG/ISR/hybrid | Trang này cần gì: SEO? tươi ngay? cá nhân hoá? |
| 2 | Framework & meta-framework (Next/Nuxt/SvelteKit/Astro) | Đội tôi và hệ sinh thái nào — và ràng buộc deploy đi kèm? |
| 3 | Routing & data loading ownership (loader/file-based) | Route nào chịu trách nhiệm load dữ liệu của nó? |
| 4 | Cạnh render ở đâu: build / origin / edge (→6.5) | Nội dung thay đổi theo giây, giờ, hay tháng? |

---

## 2. Cơ chế

### 2.1 Bốn chế độ render — bản đồ sự thật

| Chế độ | Render khi nào | Ưu | Nhược | Khi nào |
|---|---|---|---|---|
| **SSG** (static) | build time | nhanh nhất, CDN trọn (→6.5) | dữ liệu cũ theo build | landing, docs, blog |
| **SSR** | mỗi request (server) | tươi + SEO + cá nhân hoá được | TTFB phụ thuộc origin; tốn compute | trang cá nhân hoá, checkout |
| **CSR** (SPA) | trong browser | tương tác giàu; sau lần đầu mượt | LCP chậm lần đầu; SEO phải làm thêm | app nội bộ sau đăng nhập |
| **ISR/hybrid** | build + revalidate nền | tươi gần SSR, giá gần SSG | cấu hình cache tinh tế; lỗi revalidate khó thấy | tin tức, catalog |

**Islands** (Astro): HTML tĩnh + các "đảo" JS tương tác — cho trang đa số tĩnh, vài widget sống. **RSC (React Server Components):** component chạy ở server, gửi kết quả serialize về client — không phải "SSR hơn" mà là **dịch ranh giới dữ liệu**: fetch ở server component (không waterfall client), client component chỉ cho tương tác.

### 2.2 Chọn theo trang, không theo app

Câu hỏi ba bước cho mỗi route: (1) **SEO/crawler có cần HTML ngay?** không → CSR được; (2) **dữ liệu thay đổi theo ai/người dùng?** theo người dùng → SSR/RSC hoặc CSR sau auth; mọi người giống nhau → SSG/ISR; (3) **tương tác dày?** dày → client component/island. Kết quả thực tế: hầu hết app lớn là **hybrid theo route** — một framework meta (Next/Nuxt/SvelteKit/Astro) cho phép trộn trong cùng project; "SPA hay MPA" là câu hỏi 2015.

### 2.3 Routing là hợp đồng cấu trúc

- **File-based routing** (`app/users/[id]/page.tsx`) — route + data loader + error boundary gắn nhau: cohesion theo tính năng, không theo loại file (không còn `reducers/` khổng lồ);
- **Nested layout** — layout cha giữ, con đổi: tránh re-render khối bất động (cảm giác "app thật");
- **Loading & error states là route property**: mỗi đoạn route phải khai `loading.tsx`/`error.tsx` (hoặc tương đương) — không có nó, chậm = trắng màn, lỗi = trắng màn;
- **Deep link & URL là state (→7.2):** mọi màn hình phải đến được bằng URL — back button đúng là yêu cầu tính năng, không phải phụ phẩm.

### 2.4 Đo render: TTFB, LCP, INP — theo chế độ

SSR đẩy công việc từ client sang server: LCP client đẹp hơn nhưng TTFB xấu đi nếu origin chậm — giải pháp chuẩn: **SSR ở edge** (render gần người dùng — →6.5) hoặc ISR để CDN giữ. Luật cân bằng: **"công việc render phải xảy ra đâu đó"** — chọn nơi rẻ nhất cho trải nghiệm đó; không có render miễn phí.

### 2.5 Streaming & partial hydration

SSR hiện đại **stream** HTML (chunks theo readiness) + hydrate từng phần (progressive/resumability — Qwik): màn hình có nội dung trước khi dữ liệu đầy đủ. Kết quả đo được: LCP giảm rõ khi fetch chậm; nhưng thứ tự HTML quyết định cảm giác — đẩy khối trên-fold trước, để skeleton cho phần sau. Đây là kỹ thuật của mọi meta-framework 2026, không còn optional.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| TTFB SSG (CDN) | ~10–50 ms | I | →6.5 |
| TTFB SSR origin chậm | 100–500 ms+ | I | đẩy lên edge nếu có |
| LCP "tốt" | < 2,5 s (p75) | V | Core Web Vitals |
| Hydration cost | tỉ lệ bundle JS | I | islands/resumability giảm |
| Next 16 / React 19 | RSC stable, streaming mặc định | V | 30/10 |

---

## 4. Suy luận kiến trúc

- **S1:** Render là **phân bổ công việc** (build/origin/edge/browser) — mỗi chế độ là một điểm trên phổ đó; quyết định theo route theo dữ liệu của chính route đó.
- **S2:** Tham số trụ: LCP/INP theo route (RUM — →7.6), TTFB theo cạnh render, tỉ lệ hydration (JS shipped trên HTML).
- **S3:** SSR đổi compute server lấy UX lần đầu; SSG đổi độ tươi lấy tốc độ; RSC đổi mô hình tinh thần (server-first) lấy ít waterfall — mỗi lựa chọn cần cả đội hiểu, không phải một người.
- **S4:** RSC làm ranh giới client/server **trong component tree** — bảo mật: dữ liệu nhạy không vô tình xuống client bundle (nhưng có thể vô tình serialize — →7.7; biên Tin/Oxy phải chủ động).
- **S5:** AI sinh giao diện theo request (màn hình động theo người dùng — →12.7) sẽ phá vỡ giả định "route = HTML cố định" — cache theo cấu trúc, không theo URL thuần; ISR mindset sẽ còn dùng lâu.
- **S6:** Khi "web chậm": xác định chế độ render của route đó trước khi tối ưu code — CSR nặng và SSR origin xa là hai bệnh khác nhau, thuốc khác nhau.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| LCP xấu (trắng lâu) | CSR bundle lớn / SSR waterfall | vitals theo route; waterfall trace | §2.1 |
| SEO kém trang tương tác | CSR thuần không prerender | SSG/ISR cho route công khai | §2.2 |
| TTFB SSR cao | origin xa / render nặng | SSR edge; cache partial | §2.4 |
| Nhấp nháy (flash) khi tải | Hydration mismatch | fix markup đồng nhất server/client | §2.5 |
| Back/refresh mất state | URL không mang state | URL-as-state (→7.2) | §2.3 |
| Nội dung cũ sau deploy | ISR không revalidate đúng | revalidate path/tag kiểm thử | §2.1 |

---

## 6. Cách đo

```bash
# Phân biệt TTFB vs render: curl -w '{ttfb:%{time_starttransfer} total:%{time_total}}' #   -o /dev/null -s https://site/page     (chạy từ 3 vùng địa lý)

# RUM theo route: vitals (LCP/INP) gắn route name — bảng xếp hạng route
#   tệ nhất là backlog tối ưu của bạn (không "cảm giác")
```

Nguyên tắc: **đo theo route, không theo site trung bình** — trung bình giấu đúng những trang người dùng đang rời bỏ.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay meta-framework:** Vite SPA + router thuần (đơn giản, tự chủ) khi không cần SEO và nội bộ — hợp lệ và rẻ hơn; **thay ISR:** cron rebuild SSG (mộc mạc, hiệu quả với site vừa) — chấp nhận "cập nhật theo lịch".

Năm thấu kính:
- **Kinh tế:** SSR compute là hóa đơn server thực; SSG chuyển hóa đơn sang CDN (rẻ hơn nhiều lần) — di chuyển về SSG/ISR khi có thể là tối ưu chi phí thật, không chỉ kỹ thuật.
- **Vận hành:** Mỗi chế độ render cần runbook riêng khi deploy lùi (rollback cả HTML tĩnh lẫn SSR code — hai artifact khác nhau).
- **An ninh:** SSR/RSC mở mặt phẳng mới — secrets và dữ liệu nhạy trên server render; serialize đúng chỗ sai (props xuống client) là lỗi công khai dữ liệu (→7.7).
- **Lịch sử:** CGI/PHP (server render mọi thứ) → AJAX/SPA (client) → SSR lại → islands/RSC (hỗn hợp có chủ ý): vòng lặp pendulum 20 năm, mỗi lần mang theo bài học "không cực đoan"; 2026 là thời điểm hybrid trưởng thành.
- **Người dùng:** "Trang có gì cho tôi nhìn ngay, và tôi bấm thì nó phản hồi" — SSG trả lời nửa đầu, hydration/islands trả lời nửa sau; mọi thuật ngữ chương này chỉ là kế toán cho hai câu đó.

---

## 8. Đọc tiếp & bài tập

- State & fetching: **7.2** · Bundle & INP: **7.3** · CDN/edge render: **6.5** · FE security/RSC leak: **7.7**
- **Bài tập 1:** Liệt kê 10 route chính của bạn; với mỗi route ghi chế độ render hiện tại + chế độ nên có theo §2.2. Mỗi dòng lệch là một ticket.
- **Bài tập 2:** Đo TTFB của một trang SSR từ 3 khu vực (curl ở §6). Chênh nhau > 5×? Ứng viên số một cho edge render.
- **Bài tập 3:** Tắt JS (trình duyệt) rồi mở 5 trang công khai của bạn. Còn đọc được nội dung nào? Danh sách mất mát = đo lường mức "SSR thật" của bạn (khác "SSR trên giấy").
