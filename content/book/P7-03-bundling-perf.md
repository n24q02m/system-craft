# 7.3 — Build Tooling, Bundling & Performance Budget (INP)

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** web frontend · **Động từ liên quan:** Đo · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 7.1 · 3.3 (chi phí TypeScript đã gặp).

**Sợi chỉ đỏ:** *JS mỗi tuần nặng thêm — bundle budget và INP giữ bằng cách nào?* — trả lời: JS mỗi tuần nặng thêm vì thêm phụ thuộc dễ mà bớt khó — performance budget là hợp đồng số mà CI giữ như giữ test; cây phụ thuộc npm là con dao hai lưỡi; và hai "mật danh" của độ trễ frontend: long task và layout shift. Câu hỏi để lại cho chương sau: *Màn hình mọc lên không kiểm soát — design system là hợp đồng gì giữa design và code?*

**Thuật ngữ sẽ gặp:** *performance budget* — số KB và mili giây tối đa cho từng trang: vượt là fail CI, không phải họp thảo luận; *cây phụ thuộc* — một thư viện kéo theo hàng trăm package: mỗi node một chỗ có thể nặng thêm; *code splitting* — chia bundle theo route và theo tương tác: tải cái cần trước; *long task* — task chính quá 50 ms chặn tương tác: thủ phạm của INP; *layout shift (CLS)* — nhảy layout giữa chừng: khách bấm nhầm nút vì nó chạy; *Vite* — toolchain mặc định 2026 (trạng thái verify trong chương).

**Ví dụ mở đầu:** Web DM sau 18 tháng: bundle chính gấp sáu lần ngày đầu — không ai cố ý, chỉ là mỗi tuần thêm "một thư viện nhỏ". Đặt ngân sách vào CI: pull request làm nặng thêm phải tự giải thích. Chương này là bản hợp đồng số và con dao gọt cây phụ thuộc.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Performance budget: JS/cơ cấu bundle + INP/LCP target | Tôi có con số treo tường — và build nào vi phạm thì bị chặn? |
| 2 | Bundler & toolchain: Vite/esbuild/Rspack/turbopack | Dev server nhanh + output deterministic — đội cần gì? |
| 3 | Chiến lược code-split & lazy theo route/tương tác | Gói nào tải lúc nào — ai quyết định, bằng số gì? |
| 4 | CI đo vitals & bundle-diff (nếu vượt ngân sách thì fail) | Tối ưu có "giữ được" không, hay tự mất sau 3 release? |

---

## 2. Cơ chế

### 2.1 Performance budget — hợp đồng số

Ngân sách điển hình cho web app 2026 (điều chỉnh theo sản phẩm): **JS ban đầu < 150–200 KB gzip**, LCP < 2,5 s (p75), **INP < 200 ms (p75)**. INP (Interaction to Next Paint) thay FID (3/2024) đo toàn bộ phản hồi tương tác — phản ánh "cảm giác mượt" thật hơn. Ngân sách không treo trong wiki — nó nằm trong CI: vượt → đỏ → phải giảm hoặc **ý thức** nâng ngân sách (ghi lý do). Không có cơ chế này, JS cứ phình 5–10%/release (nghiên cứu HTTP Archive nhiều năm liền — I).

### 2.2 Bundle: cây phụ thuộc và con dao

Ba đòn nền tảng:
- **Code-split theo route** (dynamic import) — chỉ tải code của trang đang mở;
- **Split theo tương tác** — module nặng (editor, chart, map) tải khi người dùng sắp dùng (hover/viewport);
- **Tree-shaking + ESM** — chết các export không dùng (caveat: thư viện commonjs/side-effect làm hỏng tree-shake — kiểm tra bundle analyzer, đừng tin).

Đo bằng **bundle analyzer** (visualizer): nhìn thấy thứ thật tải; "chữ A" (ad-hoc import lodash) chiếm 80 KB là phát hiện giá trị nhất tuần. Kỹ thuật nhóm: vendor chunk tách (cache lâu hơn giữa release — →6.5 hash), preload critical, `modulepreload` cho async chunk sắp tới.

### 2.3 Toolchain 2026: Vite là mặc định

Vite (esbuild dev + rollup build) là chuẩn de-facto: dev server ms-cold, HMR tức thì; Rspack/turbopack cạnh tranh ở quy mô lớn (monorepo nghìn module). Lựa chọn ít gây hư hại nhất: **đi theo meta-framework mặc định** (Next dùng turbopack, Nuxt/SvelteKit/Astro dùng Vite) — tự ghép toolchain chỉ khi có lý do đo được.

### 2.4 Mật danh của độ trễ FE: dài task & layout shift

- **Long task** (> 50 ms chặn main thread) — giết INP: tách bằng `scheduler.yield()`/`startTransition`, chuyển sang worker (→3.3);
- **CLS** (layout shift): ảnh/video **kích thước cố định**, font `font-display: swap` + preload, không chèn banner trên nội dung;
- **Hydration tốn kém** (→7.1): islands/resumability giảm;
- **Thư viện nặng:** `moment` → `temporal`/`date-fns`; `lodash` full → import từng hàm/native.

### 2.5 CI: giữ ngân sách như giữ test

```
build → bundle-size diff (so với main) → FAIL nếu > +10 KB không giải trình
      → Lighthouse CI (lab) — phát hiện sớm
      → RUM (→7.6) — số thật; CrUX field nếu site công khai
```

Lab (Lighthouse) bắt sớm nhưng không phải người dùng thật; field (RUM/CrUX) là trọng tài cuối. Hai cái luôn chạy song song — chỉ tin một cái là sai.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| JS initial budget | 150–200 KB gzip | P | |
| INP "tốt" | < 200 ms (p75) | V | Core Web Vitals |
| LCP "tốt" | < 2,5 s (p75) | V | |
| Long task | > 50 ms chặn | V | INP driver |
| Vite 8 / esbuild | chuẩn toolchain | V | 30/10 versions.csv |
| Temporal (TC39) | giai đoạn 3→ triển khai dần | V | thay moment/luxon |

---

## 4. Suy luận kiến trúc

- **S1:** Hiệu năng là **ràng buộc phân bổ** (byte + mili giây ngân sách) — giống RAM và budget độ trễ của Quyển I; không đo thì không có.
- **S2:** Tham số trụ: INP/LCP p75 theo route, JS shipped theo route, tỉ lệ long task, số lần ngân sách bị vượt/quãng thời gian đỏ.
- **S3:** Code-split đổi công loading (spinner/rung lắc) lấy byte ban đầu — đặt ngưỡng theo hành vi thật (module > 50 KB và dùng < 30% session → split).
- **S4:** Bundle là **đồ thị phụ thuộc render ra bytes** — mỗi dependency mới là quyết định kiến trúc (→3.9 ma trận runtime cùng tư duy); npm install casually = architecture by accident.
- **S5:** AI copilot thêm dependency rất hào phóng (import cho tiện) — CI bundle-diff là phao chống lạm dụng tự nhiên của thời đại này; review người bỏ qua, số liệu thì không.
- **S6:** Khi "web chậm theo cảm giác nhưng vitals đẹp": đo INP chi tiết tương tác nào xấu (element-level) — thường 1–2 tương tác (search, bảng lọc) chiếm toàn bộ trải nghiệm xấu; sửa đúng điểm đó.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| JS phình mỗi release | Không CI budget | bundle-diff fail | §2.1 |
| INP xấu khi gõ tìm kiếm | Long task mỗi keystroke | debounce + worker + trace | §2.4 |
| Trang "nhảy" khi tải | Ảnh không size, font swap | width/height; preload | §2.4 |
| Vendor tải lại mỗi deploy | Chunk hash chung mọi thứ | tách vendor + contenthash | §2.2 |
| Dev chậm, HMR chết | Toolchain cũ (webpack thuần) | Vite/Rspack | §2.3 |
| Tối ưu xong 2 tuần lại xấu | Không ai giữ ngân sách | CI giữ (§2.5) | §2.5 |

---

## 6. Cách đo

```bash
# Bundle thật: build + analyzer
#   npx vite build --mode production && npx rollup-plugin-visualizer (hoặc tùy fw)
# CI diff: so sánh artifact size giữa PR và main — fail nếu vượt ngân sách

# Field: vitals RUM gắn route + element (→7.6); CrUX BigQuery nếu công khai
# Local repro INP: Performance panel — record tương tác, nhìn "long task" đỏ
```

Nguyên tắc: **mỗi byte tải xuống phải có người bảo lãnh** (route nào cần nó, khi nào) — không ai bảo lãnh là ứng viên xoá đầu tiên.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay CI budget:** review thủ công (vỡ khi bận deadline — mọi tổ chức đều bận); **thay bundle analyzer:** size gzip từng package trong lockfile (thô nhưng bắt được ~70% vấn đề trước khi install).

Năm thấu kính:
- **Kinh tế:** +100 KB JS trung bình = mất chuyển đổi có thể đo (nghiên cứu lớn của Google/Bing/Akamai cùng hướng (I)) — ngân sách hiệu năng là công cụ doanh thu, không phải thẩm mỹ.
- **Vận hành:** Hiệu năng là hệ thống **trôi xuống** (entropy) — giữ đà cần năng lượng (CI); "tối ưu một lần" là chi tiêu lãng phí lớn nhất của FE.
- **An ninh:** Bundle nhỏ = bề mặt audit nhỏ; dependency ít = CVE ít — SBOM (→7.7) gắn liền với danh sách byte bạn tải.
- **Lịch sử:** Grunt/gulp (2012) → webpack (2014) → Parcel/esbuild (2018–20) → Vite (2020+) → turbopack/Rspack (2023+): mỗi thế hệ chủ yếu thu ngắn **vòng lặp dev** (rebuild giây → ms) — vì thời gian dev là chi phí lớn nhất FE, không phải runtime.
- **Người dùng:** Người dùng trên máy Android tầm trung, mạng 4G lệch — không phải laptop của dev trên wifi văn phòng: ngân sách p75 là cách nói chuyện với người dùng thật bằng số.

---

## 8. Đọc tiếp & bài tập

- Render/streaming: **7.1** · State/fetch: **7.2** · RUM: **7.6** · CDN & hash cache: **6.5** · Runtime JIT/warmup (cùng tư duy budget): **1.1**
- **Bài tập 1:** Chạy bundle analyzer bản production hôm nay: chụp 5 package lớn nhất. Mỗi package viết "ai cần nó, bao nhiêu % session" — không trả lời được là mục xoá.
- **Bài tập 2:** Đặt CI guard: nếu PR làm JS initial +> 10 KB thì fail. Chạy 2 tuần — đếm số lần nó bắn: mỗi lần là một quyết định kiến trúc suýt trôi qua âm thầm.
- **Bài tập 3:** Đo INP p75 theo route (RUM hoặc CrUX): xếp hạng. Route tệ nhất — mở Performance panel và tìm đúng tương tác gây long task; đó là 90 phút đáng giá nhất của tuần.
