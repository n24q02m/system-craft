# 7.4 — Component API & Design System như Hợp đồng

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** web frontend · **Động từ liên quan:** Thiết kế · Duy trì
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.8 (versioning là hợp đồng) · 7.1.

**Sợi chỉ đỏ:** *Màn hình mọc lên không kiểm soát — design system là hợp đồng gì giữa design và code?* — trả lời: design system là hợp đồng giữa design và code — token biến quyết định thiết kế thành số có tên, component API có bốn luật, breaking change UI cần versioning như API backend, và "thống nhất" là thứ đo được chứ không phải cảm giác. Câu hỏi để lại cho chương sau: *Sản phẩm cho mọi người — a11y và i18n là tính năng hay trang trí?*

**Thuật ngữ sẽ gặp:** *token* — màu, khoảng cách, cỡ chữ thành biến có tên: một quyết định, một chỗ sửa; *component API* — props là hợp đồng: bốn luật chương này điểm danh; *breaking change UI* — đổi hành vi component là nâng major version: hệ quả lan tới mọi app (nối 4.8); *dùng sẵn hay xây* — MUI, shadcn hay tự viết: bài make-or-buy có bảng; *đo thống nhất* — quét mã màu ngoài token, đếm component trùng mục đích: số hóa "màn hình mọc lên không kiểm soát"; *ba tầng* — tokens, component, pattern: mỗi tầng một chủ sở hữu.

**Ví dụ mở đầu:** Bốn mươi bảy mã xanh khác nhau trên các trang DM: không ai chọn sai — chỉ là mỗi người chọn một lần. Design system ép quyết định đó thành một biến: đổi một chỗ, đổi mọi nơi. Chương này viết hợp đồng và cả bộ đo để biết hợp đồng đang được giữ hay chỉ tồn tại trên giấy.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Xây design system riêng hay dùng (Radix/shadcn/MUI...) | Team tôi có thể trả "thuế bảo trì hệ thống thiết kế" dài hạn không? |
| 2 | Nguyên thủy hợp đồng: tokens → components → patterns | Giao diện của tôi nhất quán bằng cái gì — bằng mắt hay bằng cấu trúc? |
| 3 | Quy tắc breaking change & versioning cho UI | Đổi API component — nửa ứng dụng cũ nửa mới xử lý thế nào? |
| 4 | Ranh giới component: props in/props out, composition | Component này có thể dùng lại mà không đọc source không? |

---

## 2. Cơ chế

### 2.1 Ba tầng của một hệ thống thiết kế

```
[Tokens]     — màu, spacing, font, radius, z-index: biến số đặt tên (CSS vars)
[Components] — nút, input, modal: props là API công khai
[Patterns]   — form, table, empty-state: tổ hợp có quy tắc nghiệp vụ
```

Tokens là **hợp đồng thấp nhất và bền nhất** (đổi màu thương hiệu = đổi token, không đụng component); components là API thật; patterns là nơi nghiệp vụ nhập môn. Bệnh kinh điển: bỏ tokens, viết hex trực tiếp — 47 sắc xanh "gần giống" sau 2 năm, và dark mode bất khả thi.

### 2.2 Component API — bốn luật hợp đồng

1. **Props như tham số hàm:** ít (≤ 6–8), đặt tên rõ, không boolean flag chồng nhau (`isLoadingDisabledCompact` — tách thành prop object);
2. **Composition hơn configuration:** `<Modal><Modal.Header>…</Modal></Modal>` tốt hơn `<Modal title showClose hasFooter dense>` — slot con mở đường cho trường hợp ngách không lường trước;
3. **Controlled/uncontrolled rõ ràng:** value+onChange (điều khiển từ ngoài) HOẶC defaultValue — không nửa vời (hai chế độ đánh nhau là bug khó nhất của form);
4. **State nội bộ là chi tiết implementation:** component không rỉ state ra ngoài trừ khi props cho phép — rỉ ra = mọi consumer phụ thuộc chi tiết đó vĩnh viễn.

### 2.3 Versioning & breaking change UI

Component library là **thư viện nội bộ có người dùng** (các team sản phẩm). Không version = mọi đổi prop là breaking ngầm. Chuẩn: semver + changelog tự sinh + codemod cho rename (tự động sửa chỗ gọi) — giảm chi phí breaking từ "cả quý im lặng" xuống "một PR chạy máy". Quy tắc mềm: **deprecate 2 release trước khi remove**, cảnh báo runtime ở dev (console.warn với hướng dẫn).

### 2.4 Dùng sẵn hay xây

| Lựa chọn | Có ngay | Cái giá |
|---|---|---|
| **shadcn/ui** (Radix + Tailwind, copy vào repo) | code của bạn — sửa thoải mái | phải tự nâng từng bản vá; không có "version" — có diff |
| **MUI/Chakra/Ant** | hệ thống đầy đủ, docs | phong cách mang dấu ấn nhà cung cấp; nâng cấp theo lịch của họ |
| **Headless (Radix/Base UI)** | hành vi + a11y (→7.5) sẵn, tự vẽ giao diện | phải có team thiết kế vẽ |
| **Tự xây từ đầu** | đúng 100% ý mình | 3–5 năm bảo trì, a11y tự lo — chỉ khi design system LÀ sản phẩm |

2026: shadcn-style (copy component vào repo) phổ biến vì AI copilot đọc/sửa code có sẵn dễ hơn wrapper đen — đánh đổi "không tự update được" chấp nhận được khi component là của mình.

### 2.5 Đo "thống nhất"

- **Độ phủ:** % màn hình dùng component chuẩn (audit visual/tool quét DOM) — 80%+ là mục tiêu khả thi;
- **Trùng lặp:** số component "button" khác nhau trong repo (grep class/variant) — > 3 là mùi;
- **Thời gian dựng màn chuẩn:** dựng lại 3 màn hình chuẩn (list+form+detail) — thời gian đó là "giá nhập môn" team mới.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Tokens điển hình | 50–150 biến | P | màu/spacing/typography |
| Radix/Base UI primitives | ~30–50 headless | I | |
| Codemod chi phí | giờ thay vì quý | P | |
| Độ phủ mục tiêu | ≥ 80% màn | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Design system là **hợp đồng API dành cho người thiết kế/lập trình viên FE** — mọi khái niệm Quyển I về versioning, additive-first (→4.8) áp nguyên văn; "chỉ là CSS" là cách nhìn thiển.
- **S2:** Tham số trụ: độ phủ, số bản sao trùng, thời gian nhập môn team mới, tỉ lệ PR đụng vào token/component chuẩn.
- **S3:** Headless + token đổi "đẹp sẵn có" lấy quyền sở hữu mã nguồn — phù hợp tổ chức có hệ thống thiết kế riêng, thương hiệu mạnh.
- **S4:** Component API tốt = **giảm khối lượng tri thức ngầm** (tribal knowledge): người mới dựng được màn đúng mà không hỏi ai — đó là metric thật của "hệ thống".
- **S5:** AI sinh UI theo prompt dựa trên design system (tokens + component trong ngữ cảnh) đang là use case AI FE số một 2026 — hệ thống sạch = AI ra code sạch; hệ thống bẩn = AI nhân bản sự bẩn với tốc độ mới (→12.7).
- **S6:** Khi "mọi màn hình mỗi kiểu một vẻ": đừng cải tạo từng màn — sửa **nguồn phát** (tokens + components + patterns); màn hình tự hội tụ khi công cụ dựng chuẩn hoá.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| 47 sắc màu xanh | Không tokens, hex rải | audit màu; CSS vars | §2.1 |
| Đổi 1 button sửa 30 chỗ | Component trùng lặp | gộp; đếm bản sao | §2.5 |
| Form "kỳ kỳ" | Controlled/uncontrolled trộn | rà value/onChange | §2.2 |
| Team khác nhau UI khác nhau | Không có patterns chung | pattern library + coverage | §2.1 |
| Nâng cấp library vỡ hết | Wrapping mỏng + flag chồng | codemod + composition | §2.2, §2.3 |
| Dark mode làm 3 tháng | Màu hard-code | token + màu scheme | §2.1 |

---

## 6. Cách đo

```bash
# Đếm màu/spacing "lạ" trong codebase:
grep -rhoE '#[0-9a-fA-F]{3,8}' src --include='*.tsx' | sort | uniq -c | sort -rn | head -30
#   — màu nào đứng đầu mà không nằm trong tokens = hardcoded

# Đếm "số loại button": grep -r 'className=.*btn' | phân loại variant
```

Nguyên tắc: **hợp đồng UI đo được bằng grep** — nếu không quét được "cái gì là chuẩn", chuẩn đó chỉ tồn tại trong đầu một người (và người đó sẽ nghỉ phép).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay design system:** quy chuẩn Figma + review bằng mắt (rẻ lúc đầu, lệch dần — chấp nhận được cho sản phẩm đời ngắn/prototype); **thay component library:** thầu agency dựng UI (nhanh, sở hữu kém — ràng buộc hợp đồng phải đòi source + tokens).

Năm thấu kính:
- **Kinh tế:** Design system là đầu tư cố định (fixed cost) — hoàn vốn theo số sản phẩm × số năm; 1 sản phẩm đời 6 tháng thì mua sẵn, 5 sản phẩm 5 năm thì xây.
- **Vận hành:** Mỗi breaking change lan theo độ phủ — đo "số chỗ gọi bị ảnh hưởng" trước khi đổi API (công cụ static analysis/CLI grep là đủ).
- **An ninh:** Component chuẩn hoá cách xử lý input nguy hiểm (escape, sanitize) — một chỗ đúng, mọi màn hưởng; ngược lại mỗi màn tự xử = mỗi màn một cơ hội XSS (→7.7).
- **Lịch sử:** BEM/OOCSS (2010s) → styled-components (2015) → Tailwind (2020) → tokens chuẩn W3C design tokens (DTCG): hướng đi là **dâng chân lý lên tầng trừu tượng cao hơn** (class → utility → biến ngữ nghĩa) — mỗi lần dâng, breaking giảm và reuse tăng.
- **Người dùng:** Người dùng không thấy design system — họ thấy "app này của một công ty biết mình đang làm gì". Nhất quán = tín dụng thương hiệu dạng thị giác; chương này là kỹ thuật đứng sau tín dụng đó.

---

## 8. Đọc tiếp & bài tập

- a11y trong component: **7.5** · API versioning (cùng luật): **4.8** · AI sinh UI: **12.7** · Test component: **7.6**
- **Bài tập 1:** Chạy lệnh grep màu ở §6 trên repo bạn. Sắc lặp nhiều nhất không nằm trong tokens? Đó là "nợ token" định lượng được.
- **Bài tập 2:** Chọn component dùng nhiều nhất (button/input): đếm số "biến thể" trong code. > 3 biến thể không có tài liệu — viết lại thành props hợp lệ theo §2.2.
- **Bài tập 3:** Cho người mới (hoặc AI copilot) dựng 1 màn chuẩn chỉ bằng docs của design system, không hỏi ai. Ghi thời gian + chỗ phải hỏi — mỗi chỗ hỏi là một lỗ hổng hợp đồng.
