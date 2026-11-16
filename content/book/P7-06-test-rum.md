# 7.6 — Kiểm thử & Quan sát Frontend (RUM)

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** web frontend · **Động từ liên quan:** Đo · Bảo đảm
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 7.1–7.5 (mặt tiền vừa xây) · 6.1 (đo client khác đo server).

**Sợi chỉ đỏ:** *Làm sao biết mặt tiền thật sự hỏng chỗ nào (chứ không phải dev tưởng) — test và RUM?* — trả lời: dev tưởng và người dùng thật là hai thế giới — test xếp kim tự tháp, mỗi lớp trả lời một câu hỏi, flaky test phải truy tận diệt vì nó giết niềm tin; RUM mang vitals và lỗi từ máy thật; error tracking phải dẫn được về dòng code. Câu hỏi để lại cho chương sau: *Trình duyệt là chiến trường — XSS, CSP, token xử lý thế nào?*

**Thuật ngữ sẽ gặp:** *kim tự tháp FE* — unit, component, E2E: càng lên cao càng đắt và càng ít; *flaky test* — lúc qua lúc trượt: kẻ thù số một của niềm tin, tha thứ là mất cả bộ test; *web vitals* — LCP, INP, CLS đo trên máy thật của người dùng: RUM là thước cuối; *source map* — lỗi production sau minify quay về dòng code gốc; *hành trình* — tỉ lệ hoàn thành đặt hàng theo từng bước: con số đơn lẻ không nói lên điều gì; *lab vs RUM* — một bên giả lập có kiểm soát, một bên đời thực đầy nhiễu: dùng cả hai.

**Ví dụ mở đầu:** CI của DM xanh suốt tháng, nhưng tỉ lệ hoàn thành đặt món ở tỉnh xa rơi: test chạy trên máy nhanh, mạng đẹp; người dùng thật cầm máy bốn năm tuổi, 3G giờ cao điểm. Chương này nối lab với đời thực để câu hỏi "thật sự hỏng chỗ nào" có câu trả lời bằng dữ liệu.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Kim tự tháp test FE: unit/component/visual/E2E phân bổ ra sao | Mỗi lớp trả câu hỏi gì — và tôi trả bao nhiêu cho mỗi câu? |
| 2 | RUM: đo gì (vitals, error, hành trình) và lấy mẫu thế nào | Tôi có biết người dùng thật đang thấy gì lúc này không? |
| 3 | Error tracking + source map + release health | Lỗi JS trong production tôi thấy sau bao lâu — có tái lập được không? |
| 4 | Playwright/E2E chạy ở đâu, chặn release hay chỉ báo cáo | E2E đỏ — ai được quyền merge? |

---

## 2. Cơ chế

### 2.1 Kim tự tháp FE — mỗi lớp một câu hỏi

| Lớp | Câu hỏi | Chi phí/lượt chạy | Số lượng nên có |
|---|---|---|---|
| **Unit (logic/hooks)** | logic thuần đúng không? | ms | nhiều |
| **Component (Testing Library)** | component render đúng theo props/a11y? | ~chục ms | vừa |
| **Visual regression** | UI có đổi ngoài ý muốn? | s (screenshot diff) | chọn màn chính |
| **E2E (Playwright)** | luồng người dùng thật qua được không? | chục s | ít (luồng doanh thu) |

Bệnh hai đầu: E2E cho mọi thứ (chạy 40 phút, flaky, ai cũng ignore đỏ) hoặc chỉ unit (logic xanh mà màn trắng). Nguyên tắc viết test FE: **query theo role/label như người dùng** (Testing Library) — không theo class/thủ tục nội bộ; test gắn hành vi, không gắn chi tiết cài đặt (→7.4 hợp đồng props).

### 2.2 Flaky test — kẻ thù số một của niềm tin

E2E flaky làm cả pipeline mất ý nghĩa (đỏ = "chạy lại thử" = đỏ thật cũng "chạy lại thử"). Ba đòn: (1) **chờ điều kiện** (waitFor — không sleep cố định); (2) **data-cy selector ổn định** + seed dữ liệu deterministic; (3) **cách ly** (mỗi test state riêng — không phụ thuộc thứ tự). Đo flake rate theo test (số lần pass khi retry); flaky > 1%: sửa hoặc tách ra khỏi critical path ngay.

### 2.3 RUM — vitals & lỗi từ người dùng thật

```
[trình duyệt] --beacon (sendBeacon, không chặn)--> [collector]
   web-vitals: LCP, INP, CLS, TTFB  (→7.1, 7.3)
   JS errors + source-map nguồn gốc + release tag + route + device class
```

Bắt buộc gắn: **release version + route + kết nối (4G/wifi) + thiết bị** — không có bốn chiều này, số RUM là số chung chung không chẩn được gì. Lấy mẫu: vitals 100% (nhẹ, beacon); sự kiện đắt (session replay) lấy mẫu 1–5% + 100% cho session có lỗi.

### 2.4 Error tracking: từ lỗi đến dòng code

Source map upload theo release (không công khai — an toàn, →7.7); nhóm lỗi (fingerprint): lỗi giống nhau đếm chung — dashboard "top 10 lỗi ảnh hưởng nhiều user nhất" là họp hành tuần. **Release health:** crash-free session theo từng bản — sau mỗi release xem đường cong: tụt là rollback/canary thu hẹp (→11.7 tương tự server).

### 2.5 Quan sát hành trình, không chỉ con số

Funnel + rage-click + dead-click (bấm không phản hồi — chỉ báo INP xấu hoặc nút chết — →7.3): đây là "observability nghiệp vụ" của FE. Session replay chọn lọc cho page có vấn đề — coi là "hộp đen máy bay": 5% ngẫu nhiên + 100% lỗi — và chú ý quyền riêng tư (mask input nhạy cảm) — đây là ranh giới pháp lý (GDPR/tương đương) không phải tùy chọn kỹ thuật.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Thời gian E2E hợp lý | < 10–15 phút toàn bộ | P | |
| Beacon vitals | ~1 KB/lần gửi | I | |
| Lấy mẫu replay | 1–5% thường, 100% lỗi | P | |
| Crash-free session mục tiêu | > 99,5% | P | |
| Playwright | chuẩn E2E 2026 | V | |

---

## 4. Suy luận kiến trúc

- **S1:** Test FE bảo vệ **hợp đồng hiển thị** (props/URL → DOM/aria/side-effect); RUM bảo vệ **trải nghiệm thật** — hai hệ miễn dịch khác nhau, cần cả hai; chỉ lab thì mù, chỉ RUM thì muộn.
- **S2:** Tham số trụ: vitals p75 theo route, crash-free session theo release, flake rate, thời gian từ lỗi xuất hiện đến người đầu tiên thấy dashboard.
- **S3:** Visual regression đổi chi phí snapshot (cập nhật mỗi thay đổi thiết kế có chủ ý) cho phát hiện "đổi ngoài ý muốn" — đáng cho design system (→7.4), ít đáng cho màn một lần.
- **S4:** RUM là **điều kiện tiên quyết của mọi tối ưu hiệu năng** (→7.3): không có baseline theo route thì mọi tối ưu là phỏng đoán; mục tiêu không ai đo là mục tiêu trang trí.
- **S5:** AI viết test case nhanh — giá trị con người dịch sang **chọn cái gì đáng test** (luồng doanh thu, biên state — →7.2) và đọc flake; pipeline test là nơi AI copilot cho năng suất thấy rõ nhất 2026.
- **S6:** Khi "không tái lập được" ở FE: mở dữ liệu §2.3 (release + route + device + replay) — 80% "không tái lập" hóa ra tái lập được khi có đủ bốn chiều.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| CI đỏ bị ignore | Flaky cao | flake rate per test; cách ly | §2.2 |
| E2E 40 phút | Dùng sai tầng kim tự tháp | dồn xuống unit/component | §2.1 |
| Người dùng thấy trắng, dashboard yên | Không có error tracking | Sentry + sourcemap + release tag | §2.4 |
| Vitals đẹp nhưng khách phàn nàn | Đo trung bình site, không theo route | RUM cut theo route | §2.3 |
| Replay lộ dữ liệu cá nhân | Không mask input | privacy masking bật | §2.5 |
| Test xanh nhưng UI sai a11y | Test không query theo role | Testing Library role queries (→7.5) | §2.1 |

---

## 6. Cách đo

```bash
# Flake: chạy 20 lần một test hay đỏ
npx playwright test tests/critical/checkout.spec.ts --repeat-each=20

# RUM sanity: gắn release + route, mở dashboard, tự hỏi:
#   "bản mới nhất, route tệ nhất, thiết bị tệ nhất là gì?" —
#   trả lời trong 10 giây hay không trả lời được?
```

Nguyên tắc: **dashboard FE phải trả được "ai đang khổ, ở route nào, từ bản nào"** trong một cái nhìn — nếu cần export CSV và viết query mới, đó chưa phải dashboard mà là kho dữ liệu.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay RUM:** chỉ CrUX (miễn phí, công khai — nhưng chỉ p75 tổng và chậm 28 ngày) — hợp kiểm đối thủ, không đủ vận hành; **thay E2E tự viết:** dịch vụ cloud test (BrowserStack/Sauce) + AI-heal selector — giảm bảo trì hạ tầng, tăng chi phí định kỳ.

Năm thấu kính:
- **Kinh tế:** 1 giờ đo RUM thay 40 giờ "tối ưu theo cảm giác"; chi phí Sentry/replay là lẻ so với một tuần dev đoán lỗi production.
- **Vận hành:** Niềm tin vào pipeline là tài sản cộng dồn — mỗi lần đỏ giả được ignore, tài sản đó mất một phần; flake budget cần được vận hành như SLO (→11.2).
- **An ninh:** Source map công khai = lộ source (thường chấp nhận, đôi khi không); replay là dữ liệu cá nhân — hai quyết định này là chính sách, không phải mặc định kỹ thuật (→7.7).
- **Lịch sử:** Karma/Jasmine (2012) → Jest (2014) → Testing Library (2018, đổi triết lý sang "test như người dùng") → Playwright (2020, đa trình duyệt) → AI-assisted (2025+): mỗi bước dịch test gần hơn người dùng thật một tầng.
- **Người dùng:** Người dùng không báo lỗi — họ im lặng rời đi (chỉ ~1/20 người gặp lỗi báo (I)); RUM là tiếng nói của 19 người còn lại; chương này tồn tại để bạn nghe được họ.

---

## 8. Đọc tiếp & bài tập

- Vitals/budget: **7.3** · State để test biên: **7.2** · Component hợp đồng: **7.4** · SLO/alert cho FE: **11.2** · Release health & rollback: **11.7**
- **Bài tập 1:** Chạy `--repeat-each=20` với 3 test E2E quan trọng nhất. Flake rate bao nhiêu? Mỗi % flake là % niềm tin team vào CI.
- **Bài tập 2:** Mở dashboard FE và trả lời trong 10 giây: route nào INP tệ nhất ở bản mới nhất? Nếu không trả lời được — thiếu chiều release/route (§2.3).
- **Bài tập 3:** Đếm lỗi JS ảnh hưởng ≥ 100 user trong 30 ngày (top 10). Chọn 1 lỗi đầu — sửa + viết test chặn hồi quy. Lặp lại hàng tuần: đó là ROI cao nhất của FE.
