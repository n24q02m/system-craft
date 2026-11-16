# 9.7 — Build Systems & Progressive Delivery

> **Tầng:** Nền tảng · **Quyển II** · **Trục đọc:** điều phối · **Động từ liên quan:** Tự động hoá · Giải phóng
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.8 (flag, expand-contract) · 7.6 (test và đo).

**Sợi chỉ đỏ:** *Niềm tin vào từng bản build — CI/CD, artifact, DORA đo thế nào?* — trả lời: niềm tin vào từng bản build — build phải lặp được (cùng commit sinh cùng artifact có digest); trunk-based cộng feature flag cho luồng một hàng; progressive delivery thả dần có phanh theo metric; auto-rollback là điều kiện để dám thả nhanh; và DORA là bốn số của năng lực giao hàng. Câu hỏi để lại cho chương sau: *DM nổi tiếng rồi — và từ lúc đó có người muốn dữ liệu 4 triệu tài khoản: an ninh bắt đầu từ đâu?*

**Thuật ngữ sẽ gặp:** *build lặp được* — cùng commit cho cùng artifact, tham chiếu bằng digest: "chạy được trên máy em" không tính; *trunk-based* — nhánh ngắn cộng feature flag: hợp nhất nhỏ, tránh địa ngục merge; *progressive delivery* — canary 1% rồi 10% rồi 100% theo metric: thả dần có phanh; *auto-rollback* — metric xấu quá ngưỡng là lùi tự động: điều kiện của tốc độ, không phải mạo hiểm; *DORA* — tần suất deploy, lead time, tỉ lệ thay đổi hỏng, thời gian khôi phục: đo năng lực giao hàng, không đo cá nhân; *SBOM/digest* — dấu vết từ commit tới production: chuỗi cung ứng build.

**Ví dụ mở đầu:** "Build máy em chạy được" — artifact không đánh dấu, lúc sự cố không ai tái tạo đúng bản đó. Từ đó quy tắc của DM: mọi thứ lên prod phải là artifact có digest, deploy là tham chiếu digest. Chương này dựng chuỗi niềm tin từ commit tới production, đo bằng DORA thay vì cảm giác.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Cấu trúc repo & build: monorepo/polyrepo, remote cache, hermetic | "Từ sửa code tới biết hỏng" mất bao lâu — và lặp được không? |
| 2 | Chiến lược nhánh & gate: trunk-based + CI chặt | Cả tổ chức có một luồng thay đổi hay rừng nhánh? |
| 3 | Progressive delivery: canary % theo SLO, auto-rollback | Bản xấu tới bao nhiêu % người dùng trước khi tự rút? |
| 4 | Artifact & supply chain: một artifact dọn dẹp mọi môi trường | Cái tôi deploy lên prod có phải cái tôi test không? |

---

## 2. Cơ chế

### 2.1 Build — từ "chạy được" tới "lặp được"

Ba phẩm chất của build hiện đại: (1) **xác định (deterministic/hermetic)**: cùng input → cùng output, không phụ thuộc máy dev (tool pin version, dependency lock, không network lúc build); (2) **tăng dần (incremental) + cache xa**: chỉ build lại phần đổi — **remote cache** chia sẻ giữa máy dev và CI (Bazel/Buck2/Nx/Turbo/GHA cache): cảm giác "nhánh nào cũng build 30 giây" ở repo nghìn module; (3) **đo được**: thời gian build p50/p95 là metric được theo dõi như INP (→7.3) — build chậm là nợ dev kinh niên (nghiên cứu nội bộ lớn: chờ build đốt hàng nghìn giờ/năm — I).

Monorepo vs polyrepo: monorepo (một nguồn, atomic cross-service change, tool phải lo scale) vs polyrepo (ownership sạch, phiên bản rải — nhớ 8.8/4.8). Chọn theo **mô hình tổ chức** (như 8.6): Conway lại thắng.

### 2.2 Trunk-based + feature flag = luồng thay đổi một hàng

Trunk-based development: merge nhỏ hàng ngày vào nhánh chính; nhánh dài sống = nơi xung đột ủ mầm. Bộ ba đi kèm: (1) **CI gate nhanh** (test + lint + build < 10–15 phút — p95, không phải "khi may mắn"); (2) **feature flag** (chưa xong vẫn merge — tắt; →8.8 kỷ luật TTL); (3) **PR nhỏ** (review được trong phút). Cha/bác git-flow với hàng chục nhánh song song phù hợp một số org phát hành phiên bản đóng gói — web/SaaS sống khoẻ hơn với trunk + flag.

### 2.3 Progressive delivery — thả dần có kiểm soát

```
build artifact (một lần — "môi trường nào cũng cái này")
  → deploy staging → smoke test tự động
  → prod: canary 1% → 5% → 25% → 100%
        mỗi bậc: chờ + so sánh SLO (error rate, p95, business metric)
        lệch quá ngưỡng → TỰ động rollback về bản trước
  → post-deploy: synthetic + RUM theo dõi tiếp (→7.6/11.1)
```

Công cụ: Argo Rollouts/Flagger (K8s native — điều khiển trọng số Gateway — →9.4), canary-check có metric thật (Prometheus — →11.5). Vô địch hai điều: **điểm quyết định là SLO, không phải cảm giác**; và **rollback không cần người 2h sáng** — đây chính là "kill-switch" của 8.8 khi sản phẩm hoá.

### 2.4 Auto-rollback — điều kiện để "dám thả nhanh"

Rollback tự động cần: metric **mau** (cửa sổ 1–5 phút, không metric 30 phút), ngưỡng **quyết** (error +0,5%? p95 +200 ms? — số biết trước), và **đường lùi đã kiểm chứng** (migrations additive — 8.8: schema cũ vẫn đọc được). Không đủ ba điều kiện thì canary chỉ là trang trí phức tạp — tốt hơn big-bang một chút, và tệ hơn nhiều so với vẻ ngoài.

### 2.5 DORA — bốn số của năng lực giao hàng

- **Deployment frequency** (thay đổi tới prod — lần/tuần hay lần/ngày?);
- **Lead time for changes** (commit → prod — ngày hay giờ?);
- **Change failure rate** (% thay đổi gây sự cố — bao nhiêu lần rollback/hotfix);
- **MTTR** (phát hiện → phục hồi — giờ hay phút?).
Bốn số này là chỉ số **năng lực**, không phải KPI ép được (ép deployment frequency = merge rác nhiều hơn — Goodhart); dùng để đo hiệu quả đầu tư platform (IDP — 9.6) và hướng cải thiện kỹ thuật (test tốc, rollback tin cậy).

### 2.6 Supply chain build — dấu vết từ code tới prod

SBOM từ build (→7.7), **ký artifact** (provenance — "artifact này build từ commit đó bằng hệ đó": SLSA-style chuỗi tin), promote theo môi trường bằng **reference** (không build lại — "cái test là cái chạy"). Mỗi lần build lại cho môi trường khác là một cơ hội Dependency khác nhau sneak in — bài học của 7.7 lặp ở tầng build.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| CI gate p95 | < 10–15 phút | P | |
| Remote cache hit | > 80–90% (repo lớn) | P | |
| Canary bậc chuẩn | 1→5→25→100% | P | |
| Cửa sổ metric auto-rollback | 1–5 phút | P | |
| Elite DORA (mẫu tham chiếu khảo sát) | deploy theo ngày, lead time < 1 ngày | I | khảo sát DORA |

---

## 4. Suy luận kiến trúc

- **S1:** Delivery pipeline là **chuỗi mở rộng của Read–Eval–Print của tổ chức**: thời gian phản hồi ngắn (build, test, deploy, rollback) cho phép thử nhiều hơn và học nhanh hơn — mọi kỹ thuật chương này phục vụ rút ngắn vòng đó.
- **S2:** Tham số trụ: DORA bốn số theo quý, CI p95 + flake rate (→7.6), tỉ lệ deploy có auto-rollback can thiệp (ra mắt an toàn thật), tỉ lệ artifact promote-vs-rebuild.
- **S3:** Canary đổi "rủi ro cô đặc một lần" thành "rủi ro pha loãng có kiểm soát" — có giá khi có metric nhanh + rollback đáng tin; thiếu hai thứ đó, canary là nghi lễ.
- **S4:** Một artifact promote nhiều môi trường là **điều kiện** của canary có nghĩa (không thì "canary của cái khác") — supply chain và progressive delivery là một chương, không phải hai.
- **S5:** AI code gen làm bước "viết" nhanh hơn rõ — bottle neck dịch sang review + build + test: đầu tư CI/remote cache/test chất lượng giờ có ROI cao hơn từng có (vì thay đổi đổ về nhanh hơn).
- **S6:** Khi "deploy ai cũng sợ": tra ba thứ theo thứ tự — rollback đã kiểm chứng chưa? metric quyết là số biết trước không? ai từng bị quy trách nhiệm cho deploy xấu? (văn hoá đổi lỗi → học, không đổ — 11.4). Tâm lý sợ là triệu chứng của kỹ thuật thiếu, không phải tính nhút nhát.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| "Merge thứ Sáu" (người merge cuối đi về) | Không canary/rollback tự động | progressive §2.3 | §2.3 |
| CI 40 phút, ai cũng merge chờ | Không cache/không chia tầng | remote cache + test song song | §2.1 |
| Deploy hỏng tới 100% user | Big-bang không canary | bật canary bậc | §2.3 |
| Rollback sợ vì migration | Schema không additive | expand-contract (→8.8) | §2.4 |
| "Prod khác staging" | Build lại mỗi môi trường | promote một artifact | §2.6 |
| Flake làm red mù loà | Test không ổn định | flake rate + cách ly (→7.6) | §2.2 |

---

## 6. Cách đo

```bash
# DORA thô từ git + CI log (đo được ngay, không cần phần mềm đắt):
#   deployment frequency: đếm deploy prod/tuần (từ CD log)
#   lead time: now − commit_time của HEAD trước mỗi deploy
#   change failure rate: deploy cần rollback/hotfix / tổng deploy
#   MTTR: sự cố được ghi nhận giờ nào, phục hồi giờ nào (từ incident log 11.4)

# CI p95: đo từng job theo tuần — job > 15 phút là ứng viên:
#   chia tầng (unit nhanh trước), cache, hoặc song song hoá
```

Nguyên tắc: **bốn số DORA vẽ một biểu đồ, treo nơi cả team nhìn thấy** — không phải để ép, để **hỏi "cải thiện tuần này ở đâu"** (năng lực là đường cong, không phải mốc).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay canary tự động:** blue-green thủ công + runbook rollback (đơn giản, chậm hơn — vẫn hơn big-bang); **thay monorepo + Bazel:** polyrepo + Makefile kỷ luật (nhỏ, trung thực về quy mô); **thay remote cache:** build lại mọi thứ + máy CI mạnh (tiền hoá đơn đổi đơn giản — hợp lúc nhỏ).

Năm thấu kính:
- **Kinh tế:** Mỗi giờ CI tiết kiệm × số dev × lương = con số đặt cạnh giá cache server; DORA cải thiện tương quan doanh thu trong khảo sát lớn nhiều năm (I) — năng lực giao hàng là tài sản tài chính đo được.
- **Vận hành:** Progressive delivery là **kế hoạch mất điện của bản phát hành**: biết trước sẽ rút ở đâu, ai bấm, dựa metric nào — drill rollback định kỳ như drill DR (→8.7).
- **An ninh:** Chuỗi build (SLSA-style) là lớp chống "mã độc chèn vào giữa build" — kẻ tấn công thiên về đánh build server hơn repo (tạp chí sự kiện lớn 2024–2025 lặp lại đủ nhiều); ký + verify ở deploy là công nghệ có sẵn, thiếu là lựa chọn.
- **Lịch sử:** Nightly build + "build sheriff" (thập niên 90, CMU) → CI (2000s, "mỗi commit") → CD (2010s, "mọi merge có thể deploy") → progressive + auto-rollback (hiện tại): 30 năm rút ngắn "khoảng cách giữa thay đổi và hiểu rõ kết quả của nó" — chính là chủ đề chung của 8.8 (mọi bước có đường lùi).
- **Người dùng:** Người dùng không biết bạn deploy 5 lần/ngày — nhưng họ **nhận ra** hệ "hay có lỗi mới" hay "lỗi tự biến mất". Tần suất + an toàn thả dần chính là dịch "chúng tôi cẩn thận với trải nghiệm của bạn" thành kỹ thuật.

---

## 8. Đọc tiếp & bài tập

- Mở rộng thu hẹp (additive) cho migration: **8.8** · Flag TTL: **8.8, 7.2** · Gateway canary: **9.4** · DORA & văn hoá sự cố: **11.4** · Bundle budget CI (FE cùng tư duy): **7.3**
- **Bài tập 1:** Tính bốn số DORA thô của quý vừa rồi (lệnh §6). Chỉ một số — con số nào làm bạn giật mình nhất? Đó là dự án quý sau.
- **Bài tập 2:** Chạy "drill rollback": deploy bản trước của một service quan trọng (hành động thật, giờ làm việc). Nếu > 10 phút hoặc "phải hỏi ai đó" — đường lùi chưa sẵn sàng cho 2h sáng.
- **Bài tập 3:** Xem pipeline build: artifact promote từ staging sang prod, hay build lại? Nếu build lại: chuyển sang promote một artifact tuần này — đó là ticket nhỏ, giá trị an ninh + đúng đắn lớn.
