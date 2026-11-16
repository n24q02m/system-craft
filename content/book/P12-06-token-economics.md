# 12.6 — AI FinOps, Model Routing & AI Gateway

> **Tầng:** AI · **Quyển III** · **Trục đọc:** nền AI · **Động từ liên quan:** Đo · Định giá
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 11.5 (unit economics) · 5.4 (tư duy cache).

**Sợi chỉ đỏ:** *Mỗi câu trả lời tốn tiền — token economics và routing tính sao cho lãi?* — trả lời: mỗi câu trả lời tốn tiền — sự cố I-067 giải phẫu hóa đơn nhân mười sau "upgrade model" mà không ai theo dõi token; các đòn: cascading (model nhỏ trước, to khi cần), semantic cache (cache ý thay chuỗi), AI Gateway (một cổng mọi model); và unit economics AI là bảng kế toán mới. Câu hỏi để lại cho chương sau: *Model từ đâu tới, ai ký, dữ liệu đi đâu — supply chain của chính AI?*

**Thuật ngữ sẽ gặp:** *token* — đơn vị tính tiền cả vào lẫn ra: hóa đơn bằng token nhân giá model; *cascading* — câu hỏi dễ cho model nhỏ, khó mới lên model to: phân loại trước, route sau; *semantic cache* — câu khác chữ nhưng cùng ý vẫn trúng cache (tư duy 5.10): nhớ đo tỉ lệ trúng; *AI Gateway* — một cổng: route, rate limit, log token theo team: API gateway của thế hệ AI (nối 4.9); *unit economics AI* — đồng mỗi câu trả lời hữu ích: doanh thu trên chi phí; *phí ẩn* — embedding, rerank, judge, tool call: hóa đơn không chỉ có model chính.

**Ví dụ mở đầu:** Đợt "nâng cấp model" của DM: chất lượng tăng nhẹ, hóa đơn nhân mười — vì model to trả lời cả những câu "mở cửa tới mấy giờ". Cascading cho câu rẻ theo đường nhỏ, câu khó mới lên đỉnh; semantic cache ăn phần câu lặp. Chương này là phòng kế toán của AI: biết mỗi câu trò chuyện lãi hay lỗ.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Model routing: cascading nhỏ→lớn, route theo gì (D-131) | Câu nào cần model to — và ai quyết (rule? model phân loại? người dùng)? |
| 2 | Semantic cache: cache gì, TTL theo nghiệp vụ | Câu hỏi lặp bao nhiêu % — trả lời cũ còn đúng không? |
| 3 | AI Gateway: một cổng cho model/provider — tự dựng hay mua | Đổi provider/model trong config hay trong code rải rác? |
| 4 | Quản trị ngân sách: theo tenant/feature/ngày — tắt khi vượt | AI đốt tiền — ai thấy số đang chảy, ai có nút vặn? |

---

## 2. Cơ chế

### 2.1 I-067 giải phẫu: hóa đơn ×10 sau "upgrade model"

Ba nguyên nhân cộng dồn: (1) **giá mỗi token khác bậc** giữa model to/nhỏ (chục lần không hiếm); (2) **reasoning/thinking token** — model mới sinh token suy nghĩ **tính tiền nhưng không hiển thị**; (3) **context dài hơn** (chat format mới, RAG nhét nhiều hơn). Chẩn: log token vào/ra theo model trước-sau (span — 12.5); phòng bệnh: **canary tài chính** — model mới bật 1% traffic, xem hóa đơn/1k request trước khi full. Bài học chung: model là **đơn giá**, thay đơn giá phải qua kỷ luật thay giá của 11.5 (ai duyệt, tác động lên unit economics).

### 2.2 Cascading — giải nhỏ trước, to khi cần

```
query → [router] → model nhỏ (đa số câu — rẻ, nhanh)
                     ↓ không đạt (schema fail / độ tin thấp / self-check)
                   model lớn (ít câu — đắt)
                     ↓ (hiếm)
                   người / từ chối
```
Router quyết định bằng: rule (độ dài, loại task, tier user), **model phân loại nhỏ** (rẻ), hoặc để model nhỏ **tự báo "tôi không chắc"** (self-report + verify — guardrail 12.5). Cascading là đòn lớn nhất của AI FinOps: đa số workload giảm chi phí mạnh trong khi chất lượng đầu-cuối giữ (vì câu khó vẫn lên to — D-131). Kèm luật: **mỗi tầng log** để biết câu rơi xuống đâu (metric chất lượng + tiền).

### 2.3 Semantic cache — cache "ý" thay "chuỗi"

Cache exact match (cùng prompt + parameters) dễ; **semantic cache** hash embedding của câu hỏi — câu khác chữ, cùng ý → dùng lại câu trả lời (ngưỡng tương đồng). Ba câu kinh doanh: (1) **tỉ lệ lặp** bao nhiêu % (FAQ / agent chạy vòng — 12.4 prefix là anh em khái niệm); (2) **TTL theo nghiệp vụ** (câu về "giá vé hôm nay" TTL phút; "thủ tục visa" TTL tháng); (3) **ACL** (cache theo tenant/user — không để câu của tenant A nuôi câu trả lời cho B — lỗi chéo dữ liệu kiểu 6.5/12.3). Semantic cache là **cache-control của AI**: đúng chỗ giảm giá + trễ thấy được.

### 2.4 AI Gateway — một cổng cho mọi model

Đặc thù gateway AI (đứng trước provider / cluster tự chạy): **routing** (cascade §2.2 — policy theo feature/tenant/tier), **budget & quota** (per tenant/ngày — vượt: shed hoặc hạ model — 8.5 áp xuống), **failover provider** (provider chết → đường dự phòng — 8.5/8.7 tư duy), **cache** (§2.3), **log + cost attribution** (span chuẩn — 12.5), **guardrail đầu vào/ra** (12.5 — cài một chỗ, mọi route hưởng), **compliance routing** (dữ liệu EU chỉ đi provider có thoả thuận — 12.7/10.8). Gateway tự dựng (một service mỏng) hay mua — quyết định 11.7 (gateway hiếm khi là lợi thế cạnh tranh).

### 2.5 Unit economics AI — bảng kế toán mới

| Chỉ số | Ý nghĩa | Nguồn |
|---|---|---|
| đ/triệu token (vào/ra riêng) | giá nhiên liệu | span × bảng giá |
| đ/task hoàn tất | giá thật (gồm retry, phế phẩm) | 12.4 |
| đ/tính năng/ngày | phân bổ | span theo feature |
| Giá bán / giá vốn AI | biên — **định giá bán** | 11.5 |
| Cache hit % / cascade xuống nhỏ % | hai van tiết kiệm | §2.2–2.3 |

Luật: mọi tính năng AI ra mắt phải kèm **ước tính đ/task** và ngân sách tháng — như mọi tính năng kèm SLO (11.1). Không có giá vốn thì giá bán là phỏng đoán (11.7 đã phê bình tình trạng này cho VM; token còn trượt hơn).

### 2.6 Phí ẩn & đòn tiết kiệm khác

- **Embedding + rerank cũng tính tiền** (RAG pipeline — 12.3): đo đủ chuỗi, không chỉ phần chat;
- **Batch API** (rẻ hơn rõ cho việc không cần ngay — phân tích đêm — 11.5 giờ thấp điểm áp nguyên);
- **Prompt rút gọn** là tối ưu bị coi nhẹ: bớt 30% token context thừa = -30% hóa đơn ngay (12.3 context engineering);
- **Reasoning budget** (nếu model cấu hình được thinking): nhiệm vụ dễ không cần nghĩ lâu — tiết kiệm lớn;
- **Model cũ ổn định** cho task cũ (đừng nâng toàn bộ vì một tính năng mới cần model mới — route riêng tính năng đó).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Giá vào vs ra | ra đắt hơn rõ | V | bảng giá |
| Model to vs nhỏ | chênh bậc độ lớn | I | |
| Semantic cache tiết kiệm | cao với workload lặp | I | theo workload |
| Batch API giảm giá | đáng kể (đổi trễ) | V | provider |
| Canary tài chính | 1% traffic trước model mới | P | I-067 |

---

## 4. Suy luận kiến trúc

- **S1:** AI Gateway là **lớp 6.5/9.4 của AI** — cache + routing + guard + cost attribution một chỗ; không có gateway thì mọi chính sách (cascade, budget, compliance) cài rải rác trong code và sẽ mục;
- **S2:** Tham số trụ: đ/task theo tính năng, cache hit %, cascade rơi-đúng %, hóa đơn/ngày theo tenant, số lần budget-shed (và ai bị ảnh hưởng).
- **S3:** Cascading đổi chất lượng-per-đồng (không phải cắt chất lượng): thiết kế điểm rơi bằng **eval theo tầng** (12.5 — model nhỏ đạt bao nhiêu là đủ chuyển câu lên trên);
- **S4:** Token là **đơn vị tài nguyên như GB/IO** — FinOps (11.5) nguyên văn: showback theo feature, anomaly (I-067 là anomaly kinh điển), unit economics, exit-plan cho provider (11.7);
- **S5:** Chuẩn hoá đang kéo model thành **commodity thay thế được** (API tương thích + router) — đổi model sẽ là dòng config (như đổi LB); lợi thế chuyển sang **data + eval + routing** — đầu tư vào ba thứ đó;
- **S6:** Khi "hóa đơn AI tăng đột ngột": theo thứ tự — model mới (canary tài chính?), vòng lặp agent (cap — 12.4), cache miss (cấu trúc prompt đổi?), traffic thật (tăng user — mừng), leak (thứ gì gọi vòng trong hệ — trace lộ).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Bill ×10 sau upgrade (I-067) | Giá token + thinking + context dài | canary tài chính + log token | §2.1 |
| Câu dễ vẫn đắt | Không cascade | router + self-report | §2.2 |
| Câu lặp trả tiền lại | Không semantic cache | cache + TTL nghiệp vụ | §2.3 |
| Tenant A thấy câu của B | Cache không theo ACL | cache key + tenant | §2.3 |
| Đổi provider = sửa khắp code | Không gateway | gateway một cổng | §2.4 |
| Không ai biết AI tốn bao nhiêu | Cost không trong span | cost attribution | §2.5 |

---

## 6. Cách đo

```bash
# Canary tài chính (trước mỗi model mới):
#   bật 1% traffic → 24 h → so: đ/1k request, TTFT p95, eval điểm
#   ba cột quyết định full-roll (11.5 unit cost + 11.1 SLO + 12.5 chất lượng)

# Dashboard AI FinOps (từ span): đ/ngày × (feature × model × tenant)
#   — vẽ cùng đồ thị chất lượng: "điểm eval vs đ" là đường cong quyết định router
```

Nguyên tắc: **mỗi đồng AI chảy qua một cổng, mỗi cổng có số** — gateway + span là điều kiện của nguyên tắc này (không phải báo cáo cuối tháng bằng tay).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay gateway tự dựng:** dịch vụ managed (mua nhanh các tính năng §2.4 — lưu ý: gateway thấy toàn bộ prompt + câu trả lời: dữ liệu đi qua bên thứ ba — 12.7 pháp lý); **thay semantic cache:** exact-match + chuẩn hoá query (đơn giản, hit thấp hơn — khởi đầu trung thực); **thay router model:** "ai cũng dùng model to" (đơn giản, đắt, chậm — chấp nhận được lúc prototype).

Năm thấu kính:
- **Kinh tế:** Cascading + cache + prompt-gọn là ba đòn không đổi chất lượng đầu-cuối — đa số hệ giảm chi phí rõ rệt chỉ bằng kỷ luật; đơn giá model sẽ tiếp tục đổi — kỹ thuật vặn van là tài sản dài hạn;
- **Vận hành:** Budget-shed phải có rule rõ (ai bị hạ model khi hết ngân sách — tier khách?) — quyết định **sản phẩm**, không để kỹ thuật ngầm quyết (11.1 bài học phanh);
- **An ninh:** Gateway thấy mọi prompt — chính nó là **tài sản nhạy nhất** (vault của tương lai): hardening + audit như control plane (→10.2/10.6);
- **Lịch sử:** CDN (nội dung tĩnh) → API gateway (API) → AI gateway (ý nghĩa): mỗi thế hệ nội dung "sống" hơn, cache khó hơn, routing thông minh hơn — cùng ba chữ: **đặt đúng chỗ xử lý**;
- **Người dùng:** Người dùng thấy hai thứ: "nhanh không" và "đúng không". Router giỏi trả cả hai (câu dễ — model nhỏ nhanh; câu khó — model to đúng) — chương này là nghệ thuật **đắt chỗ cần, rẻ chỗ thừa**.

---

## 8. Đọc tiếp & bài tập

- Evals quyết router: **12.5** · Serving/prefix: **12.2** · Agent budget: **12.4** · FinOps gốc: **11.5** · Pháp lý provider: **12.7** · Playbook: **13.5**
- **Bài tập 1:** Tính đ/task cho 3 tính năng AI (từ span — nếu chưa có span, đó là bài tập 0). Viết giá vốn cạnh giá bán (nếu tính phí) — bảng này thay đổi cuộc họp định giá sắp tới;
- **Bài tập 2:** Đo tỉ lệ câu hỏi lặp (embedding tương đồng > 0,95 trong 7 ngày log). > 20%? Semantic cache cho nhóm đó là ticket có ROI rõ nhất quý này;
- **Bài tập 3:** Thiết kế cascade 2 tầng cho tính năng chính: model nhỏ + điều kiện leo lên (schema fail / self-check). Bật 10% traffic, đo chi phí -x% và chất lượng ±y% — bộ số (x, y) là bằng chứng thuyết phục toàn công ty.
