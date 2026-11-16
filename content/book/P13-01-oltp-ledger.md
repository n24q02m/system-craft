# 13.1 — Playbook: OLTP, Thanh toán & Sổ cái

> **Tầng:** Nghiệp vụ · **Quyển III** · **Trục đọc:** playbook theo miền · **Động từ liên quan:** Áp dụng · Thiết kế
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.3 (saga, outbox) · 4.8 (idempotency — API).

**Sợi chỉ đỏ:** *DM giờ là platform thật — đầu tiên là tiền: sổ cái double-entry giữ đồng tiền thế nào?* — trả lời: tiền trước hết — sổ cái double-entry là bất biến số học của tiền: mỗi giao dịch hai vế, tổng hệ thống luôn cân; idempotency toàn trình (D-134) chặn trừ hai lần từ cổng thanh toán tới DB; payment provider có ba quyết định khó; và đối soát là việc không thể tự động hoá hết. Câu hỏi để lại cho chương sau: *Tiền đã vào sổ sạch — trạng thái đơn nhảy realtime cho hàng trăm nghìn người thế nào?*

**Thuật ngữ sẽ gặp:** *double-entry* — mỗi giao dịch ghi hai vế nợ-có: tổng luôn cân, lỗi cộng nổi ngay trong truy vấn; *ledger* — sổ chỉ thêm không sửa xoá: audit là truy vấn, không phải điều tra; *idempotency toàn trình* — khoá chống trùng xuyên suốt mọi tầng (D-134): thiếu một vòng thì trừ hai lần; *payment provider* — ai giữ tiền, ai xử khiếu nại, đường chuyển provider: ba quyết định khó nhất chương; *đối soát* — so ba nguồn số (internal, provider, ngân hàng): làm hằng ngày, tự động một phần; *playbook* — P13 là bảy playbook nền tảng: kiến trúc tham chiếu cộng quyết định đánh số.

**Ví dụ mở đầu:** Một đêm DM trừ tiền khách hai lần: retry từ wallet app đi qua callback provider — idempotency có ở app nhưng thiếu ở tầng giữa. Sổ double-entry làm lệch nổi ra ngay: hai vế không cân. Chương này mở P13 bằng playbook tiên: tiền sạch trước, mọi thứ khác sau.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Sổ cái: double-entry + đối soát thế nào (D-134) | Tiền của tôi **luôn cân** không — và cân bởi thiết kế hay bởi may mắn? |
| 2 | Idempotency toàn trình: từ nút bấm tới sổ | Cùng một giao dịch đi qua mạng lag/retry — bị trừ mấy lần? |
| 3 | Kiến trúc thanh toán: provider nào, lưu card ở đâu | Tôi có **chạm** số thẻ không (nếu không cần — đừng)? |
| 4 | Đối soát (reconciliation) hằng ngày với ai | Sai lệch provider-vs-sổ phát hiện trong ngày hay cuối quý? |

---

## 2. Cơ chế

### 2.1 Playbook là gì — cách đọc P13

P13 không dạy khái niệm mới — **xếp các chương I–II lại theo bài toán thật**. Mỗi playbook: kiến trúc tham chiếu + bảng quyết định + 5 sự cố điển hình + checklist. Đọc kèm chương nguồn (đánh dấu →).

### 2.2 Kiến trúc tham chiếu OLTP + thanh toán

```
[Client] → [Gateway/API: idempotency-key (→4.8)]
   → [Order service]  — saga orchestrator (→8.3)
        ├→ [Payment] ─ provider (Stripe/VNPay-style) qua adapter riêng
        ├→ [Ledger]   — double-entry, DB ACID (→5.1/5.2)
        ├→ [Inventory]— semantic lock (→8.3)
        └→ [Outbox]   → Kafka → notification/analytics (→5.15)
[Recon job] — đêm: đối chiếu sổ vs provider vs bank (→5.12)
```

### 2.3 Double-entry — bất biến số học của tiền

Mọi giao dịch tạo ≥2 dòng: **nợ một tài khoản, có một tài khoản khác, tổng đếm = 0** — bất biến kiểm tra được bằng một câu SQL đêm mỗi ngày (`SUM(amount) = 0` per journal). Tài khoản không phải "user" — là **ledger account** (tiền mặt, khoản phải thu, doanh thu, phí provider...). Lợi ích: lỗi trừ-thiếu/nhiều **không thể cân bằng giả** — đối soát phát hiện ngay tối đó. Không double-entry (chỉ cộng dồn số dư) = mọi bug ghi đè tự nhiên "cân" — phát hiện khi khách phàn nàn (muộn bậc độ lớn).

### 2.4 Idempotency toàn trình (D-134) — chặn trừ 2 lần

Chuỗi lặp: user bấm 2 lần (double click) → client retry (→6.1/8.5) → provider webhook gọi lại (→4.6) → message replay (→5.7). Mỗi chặng tự có "key" khác nhau — thiết kế: **một id nghiệp vụ** (order id) xuyên suốt; mỗi chặng **kiểm trước khi thực hiện**:
- API: `Idempotency-Key` header → lưu kết quả theo key (→4.8);
- Ledger: unique constraint `(journal_id)` — insert trùng = từ chối (DB là lớp cuối);
- Provider: gửi `idempotency key` theo chuẩn của họ; webhook xử lý theo event id;
- Consumer Kafka: id + store đã-xử-lý (→8.3 at-least-once + idempotent).
Nguyên tắc: **lớp cuối (DB constraint) bắt buộc — các lớp trên là tối ưu trải nghiệm**; tin một lớp duy nhất là mời sự cố của lớp còn lại.

### 2.5 Payment provider — ba quyết định khó

1. **Lưu gì:** không bao giờ lưu số thẻ tự mình (PCI-DSS là đầm lầy giấy tờ) — dùng **token hoá provider** (vault bên họ; mình giữ customer id);
2. **Đồng bộ vs webhook:** kết quả thanh toán đến từ 2 con đường (redirect + webhook) — **webhook là nguồn sự thật** (redirect chỉ UX), xử lý theo event-id idempotent (→4.6);
3. **Đa provider:** main + backup (failover — 8.5) và/hoặc theo phương tiện (thẻ quốc tế + ví nội địa) — **adapter mỗi provider** (không if-else rải); lưu `provider_txn_id` để đối soát.

### 2.6 Đối soát — công việc không thể tự động hoá hết

Đêm: (1) **trong hệ**: journal cân (`SUM=0`), số dư = tổng dòng dẫn xuất; (2) **vs provider**: tổng tiền thành công hôm nay hai bên khớp (event-id mapping); (3) **vs ngân hàng** (settle thực). Lệch → **bảng treo** (pending) + phân loại (trễ provider? thiếu webhook? bug?) — bảng treo có SLA xử lý (ngày) và **dashboard**; đối soát là SLO nghiệp vụ thật (độ lệch > X = alert — 11.1 áp cho tiền). Ngày ngừng đối soát là ngày bug bắt đầu tích lũy âm thầm (sự cố tiền luôn âm thầm trước khi ồn ào).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Idempotency TTL | ≥ 24 h (theo retry window) | P | |
| Đối soát | đêm, hàng ngày | P | |
| Journal cân | SUM=0 bất biến | V | double-entry |
| Webhook latency | phút (best-effort — →6.4) | I | pull/kèo backup |
| PCI scope | tránh chạm PAN | V | token hoá |

---

## 4. Suy luận kiến trúc

- **S1:** Tiền là miền **nghiêm ngặt nhất** — mọi kỹ thuật "đổi mới chậm" chọn đây: DB quan hệ ACID (5.2) thay NoSQL; saga có audit (8.3) thay eventual mù; không eager microservice hóa (8.6);
- **S2:** Tham số trụ: journal cân (đúng/sai — không có trung gian), bảng treo đối soát theo ngày, thời gian phát hiện giao dịch trùng (drill), tỉ lệ webhook mất phải đối soát bù (chỉ số sức khoẻ hệ).
- **S3:** Idempotency là **hợp đồng nhiều lớp** (UI → API → saga → provider → DB) — mỗi lớp chịu trách nhiệm chặng mình, lớp DB là phao cuối;
- **S4:** Sổ cái là **event sourcing thuần khiết nhất** (append-only journal — 8.6): không update số dư — chỉ thêm dòng; đây là nơi ES đáng giá tuyệt đối (audit là luật, không phải lựa chọn);
- **S5:** AI trong thanh toán: chống gian lận (chấm điểm risk — model phân loại thường) và đối soát bất thường (anomaly) — **không** để LLM "quyết định" chuyển tiền trực tiếp (ngưỡng human-in-loop tuyệt đối — 12.4);
- **S6:** Khi "số không khớp": đối soát ba lớp §2.6 xác định tầng lệch (trong hệ? vs provider? vs bank?) — mỗi tầng có cách xử riêng; đừng bắt đầu bằng "dump DB ra Excel" (vẫn xảy ra hằng tuần ở đâu đó).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Trừ tiền 2 lần | Idempotency thiếu một chặng | audit chuỗi key (→4.8) | §2.4 |
| Số dư "không hiểu sao lệch" | Không double-entry | dựng journal + bất biến SUM=0 | §2.3 |
| Webhook mất, đơn treo | Tin 1 đường (redirect) | pull bù + đối soát | §2.5 |
| Đơn hàng có, sổ không có | Không outbox (→8.3) | outbox nguyên tử | §2.2 |
| Đối soát phát hiện cuối quý | Không job đêm | lịch + dashboard lệch | §2.6 |
| PCI audit kinh hoàng | Tự lưu số thẻ | token hoá provider | §2.5 |

---

## 6. Cách đo

```sql
-- Kiểm bất biến sổ cái (chạy đêm — alert nếu lệch):
-- SELECT journal_id, SUM(amount) FROM ledger_entries
--   GROUP BY journal_id HAVING SUM(amount) <> 0;   -- phải rỗng

-- Drill trừ-2-lần (staging): gửi cùng Idempotency-Key 3 lần
--   + replay webhook 2 lần — đếm dòng ledger sinh ra: phải đúng 1
```

Nguyên tắc: **mọi bất biến tiền được viết thành truy vấn chạy tự động mỗi đêm** — con người chỉ đọc alert; "tin rằng cân" không phải cơ chế.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự dựng ledger:** dịch vụ ledger managed (mở của vài fintech lớn) hoặc DB nền tảng có hỗ trợ — hợp khi fintech không phải lợi thế cạnh tranh (11.7); **thay double-entry:** single-entry + đối soát tay (rẻ lúc 5 giao dịch/ngày — chết ở 5.000); **thay provider adapter:** một provider duy nhất (đơn giản, rủi ro tập trung — 8.7 bảng thảm hoạ áp cho vendor).

Năm thấu kính:
- **Kinh tế:** Mỗi bug tiền = hoàn + xin lỗi + nguy cơ pháp lý; chi phí "làm đúng từ đầu" (double-entry + idempotency) thấp hơn một sự cố nhỏ — đây là miền ROI của kỷ luật cao nhất;
- **Vận hành:** Bảng treo đối soát phải có **chủ mỗi ngày** (người trực nhìn dashboard — 11.4 vai trò); "để mai tính" là nợ lãi kép;
- **An ninh:** Thanh toán là mục tiêu tấn công số một (card testing, refund abuse — 10.3/11.3 rate limit theo phương tiện); log giao dịch là chứng cứ pháp lý — retention dài, immutable (append-only);
- **Lịch sử:** Sổ cái double-entry tồn tại từ thời trung cổ Ý (1494, Luca Pacioli hệ thống hoá) — 500 năm trước máy tính; kỷ luật của chương này là **cũ hơn mọi công nghệ trong atlas** và sẽ sống qua hết — tài sản dài hạn của người làm hệ thống tiền;
- **Người dùng:** Người dùng tha thứ nhiều thứ, **trừ sai tiền** — mỗi lần trừ nhầm là một người kể lại 10 người nghe. Playbook này tồn tại để câu chuyện đó không bao giờ có dịp bắt đầu.

---

## 8. Đọc tiếp & bài tập

- Saga/outbox: **8.3** · Idempotency hợp đồng: **4.8** · Webhook/SSE: **4.6** · DB ACID: **5.1, 5.2** · CDC: **5.15** · Sự cố & on-call: **11.4**
- **Bài tập 1:** Nếu có hệ tiền: chạy kiểm SUM=0 (§6) đêm nay — kết quả ra gì? Nếu chưa có journal double-entry — đó là dự án quý tới, ghi ADR;
- **Bài tập 2:** Drill trừ-2-lần (§6) ở staging: gửi 3 lần + replay webhook. Đếm dòng ledger — >1 là lỗ idempotency ở đúng chặng đó (sửa theo bảng §2.4);
- **Bài tập 3:** Vẽ chuỗi id của một giao dịch thật (từ nút bấm tới dòng sổ) — đánh dấu key idempotency mỗi chặng. Một mũi tên không key = cửa vào của bug ×2.
