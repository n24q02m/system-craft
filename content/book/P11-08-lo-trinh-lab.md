# 11.8 — Lộ trình Học & 24+ Lab

> **Tầng:** Vận hành · **Quyển II** · **Trục đọc:** tổ chức · **Động từ liên quan:** Học · Luyện
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** learn-v2.md + labs-legacy.md

---

## 0. Nhập môn

**Đọc trước:** Toàn bộ P0–P11 — chương này là lộ trình đọc lại theo vai.

**Sợi chỉ đỏ:** *Đi từ đây tới đâu — lộ trình lab và thói quen verify cho người vận hành?* — trả lời: từ đây tới đâu — cách đọc 145 chương theo vai thay vì tuần tự; 24 lab, mỗi lab dưới 30 phút, làm bằng chính hệ của bạn; runbook một trang là bài tập lớn nhất; nhịp kiểm tra phiên bản cho kiến thức tươi; và mốc "biết đủ để làm" để dừng đúng chỗ. Câu hỏi để lại cho chương sau: *Mọi tầng đã chạy — DM muốn trợ lý AI trả lời 'tối nay ăn gì': giả định nào của kỹ sư vỡ đầu tiên?*

**Thuật ngữ sẽ gặp:** *đọc theo vai* — dev, ops, SRE, kinh tế: mỗi vai một đường, chương có bản đồ; *lab* — 30 phút trên chính hệ của bạn: nguyên tắc thành kinh nghiệm khi tự verify; *runbook một trang* — tóm mỗi chương thành runbook: viết ra mới biết mình hiểu tới đâu; *nhịp verify phiên bản* — kiến thức có hạn dùng: kiểm tra phiên bản, EOL theo nhịp; *biết đủ để làm* — mốc dừng: đủ hành động an toàn, còn lại tra cứu.

**Ví dụ mở đầu:** Đây là chương cuối của tuyến học — không ai đọc 145 chương tuần tự như tiểu thuyết. Người vận hành đi đường khác người viết tính năng, người viết khác người kí hóa đơn. Chương này vẽ đường theo vai, gắn 24 trạm lab, và chỉ mốc dừng: đủ tự tin để hành động, đủ khiêm nhường để tra lại.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Lộ trình học của tôi/tổ chức: 6 tuần hay theo phần | Tôi đọc atlas này theo đường nào để **dùng được**, không chỉ đọc xong? |
| 2 | Lab: cái nào làm trước theo vai của tôi | 1 giờ thực hành đáng giá hơn chục giờ đọc — tôi đã làm lab nào? |
| 3 | Giữ kiến thức tươi: nhịp theo dõi phiên bản nào | Thông tin tôi tin có ngày kiểm tra không (EOL/versions)? |
| 4 | Runbook 1 trang cho hệ mình dùng | Tôi có thể viết tài liệu "sống sót" cho hệ mình không? |

---

## 2. Cơ chế

### 2.1 Cách đọc atlas theo vai (không đọc tuần tự 145 chương)

- **Backend/dev mới:** P0 → 3.x (runtime mình dùng) → 4.x → 8.3/8.5 → 11.1–11.2 → quay lại phần khó khi cần;
- **Ops/SRE:** P0 → 1.x → 2.x → 8.5/8.7 → 9.x → 11.x (toàn bộ) → 10.7;
- **Kiến trúc sư/lead:** P0 → đọc §1+§4 mọi phần (bảng quyết định + suy luận) → đào sâu nơi dự án chạm → 11.6–11.7;
- **Data:** 5.x trọn → 8.3–8.4 → 12.x (khi đến) → 11.3;
- **Frontend/mobile:** 6.x → 7.x → 4.x → 11.1–11.2 (RUM) → 10.3–10.4.
Quy tắc: **mỗi chương trả lời "quyết định gì"** (§1) — đọc bảng quyết định trước; chương nào không chứa quyết định của đời bạn thì để sau.

### 2.2 24 lab — mỗi lab ≤ 30 phút, làm bằng chính hệ của bạn

**Nhóm A — Phần cứng & runtime (1.x–3.x):**
1. Đo bậc độ trễ bộ nhớ: script truy cập mảng 1 KB/1 MB/100 MB/1 GB (random) — thấy bậc L1→RAM (→1.1);
2. False sharing: 4 thread tăng biến cạnh nhau vs `alignas(64)` — tỉ lệ chênh, giải thích MESI (→1.3);
3. Trần GIL: 4 thread CPU-bound Python, đo hệ số — rồi thử `3.15t` free-threaded nếu có (→3.2);
4. Event loop bị chặn: FastAPI `/block` (sleep) vs `/offload` (`to_thread`) + đo `/health` đồng thời (→3.2/3.3);
5. Fork bẩn: thread nền + `os.fork()` quan sát treo — sửa bằng spawn/forkserver (→3.2);
6. Profiler 5 phút: flamegraph service mình (py-spy/perf/async-profiler — →3.x) — tìm đỉnh bất ngờ.

**Nhóm B — Mạng & API (1.6, 4.x):**
7. Curl chặng: TTFB/DNS/connect từng bước tới endpoint (→1.6/11.1);
8. Wireshark/tcpdump bắt 3-way handshake + TLS SNI (→4.1);
9. H2 vs H3: curl `--http3` so p50/p95 (→4.2);
10. Retry storm tái lập: 50 client không jitter đánh dependency — rồi thêm jitter xem khác biệt (→8.5);
11. Idempotency: gửi lại POST cùng id — đếm bản ghi sinh (→4.8);
12. gRPC vs REST đo cùng nghiệp vụ: payload + latency (→4.4).

**Nhóm C — Dữ liệu (5.x):**
13. EXPLAIN ANALYZE query chậm nhất của bạn — trước/sau index (→5.2);
14. Page cache & fsync: `dd` + `sync` — cảm nhận bậc tốc độ (→2.4/5.1);
15. OOM sinh ra: heap + không giới hạn — xem OOMKilled (→2.2/9.1);
16. Backup-restore thật: restore bảng to sang máy phụ — bấm giờ (→5.13);
17. isolation level: hai tab thay đổi cùng dòng — đo read skew (→5.1);
18. Outbox: sinh event trùng — consumer có chặn không (→8.3).

**Nhóm D — Phân tán & nền tảng (8.x–9.x):**
19. STOP–CONT lock: pause tiến trình giữ lock — fencing có chặn không (→8.2 — lab quan trọng nhất của Quyển II);
20. Raft election: 3 node etcd — tắt 1, tắt 2, quan sát (→8.2);
21. Drain node lúc giờ làm việc: service còn sống không (→9.1 PDB);
22. Synthetic xuyên deploy: curl 100 ms suốt release — đếm request rơi (→9.7);
23. Thêm 200 ms vào dependency (toxiproxy) — breaker có mở không (→8.5);
24. Chaos nhỏ: kill pod quan trọng nhất (→11.3).

**Nhóm E — Vận hành (10.x–11.x):**
25. Bảng SLO 3 journey + burn-rate alert (→11.1);
26. Traceparent xuyên 3 service — tìm chỗ đứt (→11.2);
27. Cardinality audit: top 10 metric chuỗi — sửa label vô hạn (→11.2);
28. SSRF check webhook: fetch `169.254.169.254` — chặn chưa (→10.4);
29. Syft+grype image: SBOM + CVE-KEV list (→10.5);
30. Load test k6 kịch bản thật — ghi điểm gãy kèm ngày (→11.3).
(Ba mươi lab — bộ "24+" luôn dư; mỗi lab ≤ 30 phút, dùng chính hệ mình làm chuột bạch.)

### 2.3 Runbook 1 trang — bài tập lớn nhất (migrate nguyên tắc learn-v2)

Cho **mỗi hệ thống mình trực**: đúng 1 trang gồm (1) phiên bản đang chạy **và ngày EOL**; (2) 3 con số sizing (worker/heap/limit); (3) 5 metric + ngưỡng đỏ; (4) 3 bẫy khả dĩ nhất + cách phát hiện; (5) lệnh chẩn copy-paste được; (6) kế hoạch nâng cấp tới + ai giữ. Trang này **biến kiến thức thành năng lực trực** — và là thứ người trực kế tiếp đọc khi bạn nghỉ phép.

### 2.4 Giữ kiến thức tươi — nhịp kiểm tra phiên bản

| Nguồn | Nhịp | Phủ |
|---|---|---|
| `endoflife.date` (tự query API — đã làm cho versions.csv) | mỗi quý | EOL toàn bộ stack |
| Release notes runtime chính mình (whatsnew Python, Go blog, Node release) | mỗi tháng | breaking changes |
| K8s release notes + deprecation | mỗi ~4 tháng | platform |
| Security advisory (NVD/KEV feed) | mỗi tuần | →10.5 |
| Chính sách cloud (giá/limit đổi) | mỗi nửa năm | →11.5 |

Quy tắc vàng từ kinh nghiệm atlas: **mọi con số phiên bản có ngày kiểm tra** — kiến thức không có ngày là đồ hết hạn không nhãn (versions.csv của dự án này là hiện thân: 52 hàng, ngày verify 30/10, hàng loạt sẽ cũ trong 6 tháng).

### 2.5 Học kiểu tổ chức — chia lại cho team

Format "hội thảo 15 phút" (migrate từ learn-v2): mỗi tuần một người lấy **một chương + một lab đã làm** — trình bày 15 phút (vấn đề gì, lab ra sao, thứ mình đổi thật). Luật: phải có lab — trình bày lý thuyết suông bị từ chối đặt lịch. Sau 30 tuần, team có 30 lab + 30 runbook sống; đó là "platform knowledge" không ai mang đi khi nghỉ việc. Ghi lại vào repo nội bộ (ADR + runbook — →11.6 cấu trúc hoá).

### 2.6 Khi nào "biết đủ để làm"?

Bốn câu tự kiểm (per phần): (1) tôi vẽ được sơ đồ phần này **từ trí nhớ**? (2) tôi gọi được tên 3 quyết định + đánh đổi? (3) tôi đã làm ≥ 1 lab và thay đổi thứ gì đó thật? (4) tôi biết con số nào của hệ mình tương ứng với chương này? Bốn × "có" = đủ để **hành động** — mức đọc hiểu sâu hơn chờ lúc cần (atlas là sách tra, không phải novel đọc một mạch).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Lab mỗi cái | ≤ 30 phút | P | |
| Runbook | 1 trang, 6 mục | P | |
| Hội thảo tuần | 15 phút, có lab | P | |
| Verify EOL | mỗi quý | P | |
| Trình bày tổng kết | 15 phút/team | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Kiến thức vận hành chỉ tồn tại khi **được dùng thường xuyên hoặc ghi lại đúng chỗ** — não là cache không đáng tin cho thông tin phiên bản; artifact (runbook/versions.csv/ADR) là nguồn chân lý;
- **S2:** Tham số trụ: số lab đã làm (cá nhân/team), số runbook sống, thời gian từ "người mới" → "trực được" (mục tiêu giảm), tuổi trung bình của "con số tin được" (≤ 1 quý).
- **S3:** Lab đổi thời gian lấy **niềm tin có bằng chứng** — như chaos (11.3) đổi niềm tin bằng thí nghiệm; đọc không làm được điều đó;
- **S4:** Lộ trình theo vai (§2.1) tôn trọng quy luật: **học để giải quyết vấn đề của mình trước** — atlas tổ chức theo quyết định chính là để phục vụ lối học này (không phải để đọc tuần tự làm nhiệm vụ);
- **S5:** AI làm "tài liệu sống" khả thi hơn: sinh nháp runbook từ telemetry/ADR thật (người duyệt + cập nhật) — kiến thức tươi bằng tự động hoá thay vì kỷ luật con người (vẫn cần người duyệt — →12.7);
- **S6:** Khi "đọc nhiều mà vẫn không dám quyết": thiếu lab — chọn 1 chương liên quan nhất, làm 1 lab hôm nay; 30 phút đó thường mở khóa nhanh hơn 3 giờ đọc lại.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Đọc xong quên sạch | Không lab/runbook | 1 lab/tuần + runbook | §2.2–2.3 |
| Tin số cũ (phiên bản đã đổi) | Không nhịp verify | lịch quý EOL | §2.4 |
| On-call mới luống cuống | Không runbook 1 trang | viết theo template §2.3 | §2.3 |
| Team không chia kiến thức | Không cấu trúc sinh hoạt | 15 phút có lab | §2.5 |
| "Biết tên không làm được" | Thiếu tự kiểm 4 câu | §2.6 | §2.6 |
| Mất người = mất tri thức | Tri thức trong đầu, không repo | ADR + runbook + wiki sống | §2.5 |

---

## 6. Cách đo

```bash
# Điểm "cá nhân" một quý (tự chấm, 10 phút):
#   - số lab mới làm (mục tiêu ≥ 3)
#   - runbook mình sở hữu còn đúng? (kiểm 3 con số trong đó)
#   - phiên bản quan trọng mình dùng: biết EOL không ngày kiểm?
#   - một thứ mình đã dạy lại cho ai (hội thảo/ghi chú)

# Điểm "tổ chức": đếm runbook sống / số hệ thống trực; đếm lab làm chung
#   quý này; tuổi trung bình của bảng versions nội bộ (nếu có — nên có)
```

Nguyên tắc: **học đo bằng thứ để lại** (lab đã đổi gì, runbook ai đọc, người mình dạy) — không bằng số trang đã đọc.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay lab tự làm:** khóa học thực hành có môi trường dựng sẵn (nhanh hơn — không dính vào hệ mình — đánh đổi: ít "đau thật" nên nhớ kém hơn); **thay runbook template:** wiki tự do (tốt hơn không gì, xấu hơn template về tính đầy đủ); **thay nhịp verify EOL:** alarm tự động (đáng làm — scripted check EOL API gửi alert — một buổi, dùng nhiều năm).

Năm thấu kính:
- **Kinh tế:** 30 phút lab × 30 = 15 giờ đổi lấy việc tránh một sự cố (vài chục giờ) và ra quyết định đúng (tiền máy — 11.5) — ROI cao nhất của mọi giờ học;
- **Vận hành:** Runbook là **bảo hiểm nghỉ phép** (và bảo hiểm nghỉ việc — 11.6: tri thức trong đầu rời đi cùng người);
- **An ninh:** Nửa bộ lab (SSRF, syft, token) chính là checklist sống của 10.x — học và an ninh cùng một động tác;
- **Lịch sử:** Từ "certification hết-life" (thập niên 90, học một lần dùng mười năm) → nhịp release 6 tuần hiện tại: **tài năng kỹ thuật là kỹ năng học lại**, và cơ sở hạ tầng tri thức (runbook/ADR/verify date) là cách con người theo kịp máy móc;
- **Người dùng:** "Người dùng" cuối cùng của chương này là **chính bạn sau sáu tháng** — quay lại đọc ghi chú của mình mà hiểu trong 5 phút là thiết kế tri thức thành công; lúng túng là dấu hiệu chưa xong.

---

## 8. Đọc tiếp & bài tập

- Mọi chương là "đọc tiếp" — và quyển III (P12 AI, P13 enterprise) mở tiếp; **P14** là vi kiến trúc cho ai muốn xuống silicon;
- **Bài tập 1 (làm ngay hôm nay):** chọn 1 lab nhóm D-E liên quan hệ mình (gợi ý: #19 STOP–CONT nếu có lock; #22 synthetic xuyên deploy nếu đang ship) — làm, ghi 3 dòng kết luận;
- **Bài tập 2 (tuần này):** viết runbook 1 trang cho hệ mình trực (template §2.3) — rồi nhờ đồng nghiệp đọc 10 phút và hỏi "trực được chưa?";
- **Bài tập 3 (tháng này):** dựng lịch verify EOL (endoflife.date API — chính nguồn atlas dùng) cho 5 stack chính của bạn; đặt alarm quý. Con số cũ tự chết — quyết định dựa trên số chết là quyết định bơi trong tối.
