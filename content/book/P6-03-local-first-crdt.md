# 6.3 — Lưu trữ Cục bộ, Local-First & Đồng bộ Offline (CRDT/Sync)

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** nền client · **Động từ liên quan:** Thiết kế · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.9 (đồng hồ lệch) · 4.8 (idempotency khi sync lại).

**Sợi chỉ đỏ:** *Đang đặt món thì mạng đứt — local-first giữ được gì, gỡ rối ra sao?* — trả lời: mạng đứt giữa lúc đặt món — giữ được gì tùy bậc của thang offline: từ "đọc được khi offline" tới "đặt được và tự gỡ rối khi mạng về"; ba họ giải xung đột — last-write-wins, CRDT, merge có ngữ nghĩa nghiệp vụ — mỗi họ một cái giá. Câu hỏi để lại cho chương sau: *Có tin mới phải báo — push tốn pin thế nào và thông báo nào xứng đáng đánh thức người?*

**Thuật ngữ sẽ gặp:** *bậc thang offline* — cache chỉ đọc → hàng đợi ghi → conflict-free: mỗi bậc lên một chi phí; *LWW* — last-write-wins: đơn giản, nhưng đồng hồ hai máy lệch nhau (nối 1.9) là âm thầm mất dữ liệu; *CRDT* — cấu trúc dữ liệu hội tụ: hai nhánh sửa cùng chỗ vẫn tự về một kết quả; *vector clock* — biết "ai sửa trước ai": merge có thông tin thay vì đoán; *độ tươi* — dữ liệu cũ bao nhiêu phút là quá cũ cho hành động này: quyết định nghiệp vụ; *sync engine* — tự viết hay mua: bài make-or-buy kinh điển của local-first.

**Ví dụ mở đầu:** Shipper xuống hầm vẫn phải bấm "đã giao". Mạng về: hai thế giới hoà lại — đơn vừa được bấm trên máy, vừa bị sửa ghi chú ở console. Không cơ chế thì "ai đè ai" được trả lời bằng may mắn. Chương này leo bậc thang offline tới đúng độ cao DM cần — mỗi bậc có giá thật.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|-----------|----------------|
| 1 | Mức offline: cache-chỉ-đọc / offline-đọc / offline-đọc-viết (local-first) | Người dùng của tôi cần **làm gì** khi mất mạng? |
| 2 | Giải quyết xung đột: LWW / field-merge / OT / CRDT | Hai thiết bị cùng sửa một bản ghi — ai thắng, mất gì? |
| 3 | Sync engine: tự viết hay dùng (ElectricSQL/RxDB/PowerSync/Yjs) | Tôi có dư 6 tháng để tự viết và bảo trì không? |
| 4 | Ngữ nghĩa hiển thị: stale-while-offline, badge "chưa sync" | Người dùng có biết dữ liệu đang cũ/chưa gửi không? |

---

## 2. Cơ chế

### 2.1 Bậc thang offline — mỗi bậc một chi phí

```
0. Không offline (hiện thông báo lỗi)          — mặc định đáng xấu hổ
1. Cache đọc (lần sau mở nhanh, cũ)            — rẻ: HTTP cache + storage
2. Offline-đọc (xem được mọi thứ đã từng load) — cần store cục bộ có cấu trúc
3. Offline-đọc + hàng đợi viết (outbox client) — idempotency + ordering
4. Local-first (client là nguồn thật, sync nền) — CRDT/merge — đắt nhất, mượt nhất
```

Bậc 3 đã đủ cho 80% use case (soạn thư, giỏ hàng, like); bậc 4 dành cho cộng tác nhiều người/nhiều thiết bị (note, bảng, chat). Nhảy thẳng bậc 4 vì "nghe hiện đại" là over-engineering có thật.

### 2.2 Ba họ giải quyết xung đột

| Họ | Cách | Chết ở đâu |
|---|---|---|
| **LWW** (last-write-wins) | timestamp mới nhất thắng | đồng hồ lệch → mất update im lặng (→1.9); xóa field lẫn value |
| **Field merge / OT** | gộp theo trường / vận hành biến đổi (text) | OT: chỉ cho văn bản, phức tạp server trung tâm; field merge: mâu thuẫn chéo trường |
| **CRDT** (Yjs/Automerge) | cấu trúc hội tụ toán học — mọi bản sao cuối cùng giống nhau | metadata phình; semantic conflict vẫn cần người (hai người đổi title khác nhau — hội tụ được nhưng chọn ai?) |

Sự thật cần thuộc: **CRDT loại bỏ conflict ở tầng dữ liệu, không phải tầng ý nghĩa.** "Hai người cùng đổi tên dự án" vẫn là quyết định sản phẩm (thường: LWW cho scalar + hiển thị "đã có thay đổi").

### 2.3 Kiến trúc local-first chuẩn

```
[UI] ⇄ [local DB (SQLite/IndexedDB) = nguồn hiển thị duy nhất]
              │ 1. ghi local ngay (UI mượt, không chờ mạng)
              │ 2. outbox/changeset queue (idempotent — →4.8)
              ▼        ▲ 4. push/pull merge
        [sync engine] ⇄ [server: changeset log / CRDT doc / row-level patch]
```

Ba nguyên tắc bất biến: (a) **UI chỉ đọc từ local store** (không bao giờ "đợi API" trên đường vẽ — mọi fetch là background); (b) **mọi ghi có id client** (UUID) để merge/xóa trùng; (c) **push-pull tách rời** (không giao dịch chờ hai chiều).

### 2.4 Sync engine — tự viết hay mua

Tự viết = journal + push + pull + resolve + tombstone + backoff + migrate schema local — 6 tháng để tới "tạm được", sau đó là bảo trì vĩnh viễn. Mua/dùng: **Yjs/Automerge** (CRDT doc — hợp tác văn bản), **ElectricSQL/PowerSync/RxDB** (sync DB quan hệ sang SQLite client), **Firebase/Supabase Realtime** (managed, khóa nhẹ theo provider). Quy tắc: **sync là "cơ sở dữ liệu phân tán cực khó" (→8.x), không phải tính năng tuần nào xong** — trừ khi đó là sản phẩm cốt lõi của bạn, đừng tự viết.

### 2.5 Đo độ tươi & xung đột

- **Sync lag:** `now - last_pulled_at` theo thiết bị — phân phối, không trung bình;
- **Conflict rate:** số bản ghi phải resolve/1000 sync — metric chất lượng schema (nhiều conflict = chia trường sai);
- **Queue depth offline:** hàng đợi viết chưa gửi — tăng dần = mạng/policy lỗi, không phải "user offline lâu".

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| UI local read | < 10 ms | I | SQLite/IndexedDB |
| CRDT metadata overhead | ~1,5–3× payload (tệ nhất) | I | theo loại doc |
| Conflict hợp lý | < 0,1–1% bản ghi | P | cao hơn = schema sai |
| Sync interval nền | phút (mobile), tức thì khi active | P | pin (→6.4) |

---

## 4. Suy luận kiến trúc

- **S1:** Local-first đảo hợp đồng dữ liệu: **client là nguồn sự kiện, server là merge point** — mọi ràng buộc 8.1 (nhất quán) áp lên sync engine như một hệ phân tán thật.
- **S2:** Tham số trụ: sync lag p95, conflict rate, queue depth, tỉ lệ mất-update báo cáo từ user (so với metric — tìm khoảng mù).
- **S3:** Mỗi bậc offline đổi chi phí phức tạp lấy UX; CRDT đổi metadata + "hội tụ nhưng không đúng nghĩa" lấy tự động hoá.
- **S4:** Yjs/Automerge + Wasm (→3.8) làm CRDT chạy đồng nhất web/app/server — một thuật toán, ba nơi; tự viết ba nơi là lỗi thời.
- **S5:** AI offline (transcribe/dịch trên thiết bị) + local-first = "sản phẩm tôn trọng mạng & privacy" — hướng đi thương mại thật 2026 (→12.3).
- **S6:** Khi user báo "dữ liệu mất/đè nhau": tra conflict path của đúng field đó — gần như luôn là LWW lệch giờ (→1.9) hoặc thiếu tombstone.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| "Bản ghi cũ đè mới" | LWW + clock skew (→1.9) | so timestamp 2 máy | §2.2 |
| Xoá rồi "sống lại" | Thiếu tombstone (sync lại từ bản cũ) | audit delete path | §2.3 |
| Metadata CRDT phình | Doc lâu năm không compact | Automerge compact; snapshot | §2.4 |
| Sync "chạy mà không tươi" | Pull chỉ khi mở app | background fetch policy (→6.4) | §2.5 |
| Hai thiết bị lệch vĩnh viễn | Merge bug / thiếu một chiều | repro 2 máy + log changeset | §2.3 |

---

## 6. Cách đo

```sql
-- Local store: tuổi dữ liệu & hàng đợi
-- SELECT max(updated_at), count(*) FROM outbox WHERE sent=0;   (SQLite client)

-- Server: changeset lag theo device
--   last_seen vs now — phân phối theo thiết bị (p50/p95), vẽ theo giờ trong ngày
```

Nguyên tắc: **"độ tươi" là metric người dùng** ("tôi vừa sửa trên máy tính, điện thoại thấy sau bao lâu?") — đo đúng câu đó, công bố số bên trong app khi debug.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay local-first:** optimistic UI + server authoritative (đơn giản hơn nhiều, hỏng mạng thì rollback với thông báo) — đủ cho form CRUD; **thay CRDT:** field-level LWW + hiển thị xung đột cho người chọn — đôi khi sản phẩm muốn con người quyết. **thay sync engine tự viết:** mua managed — mỗi tháng phí nhỏ vẫn rẻ hơn 1 FTE giữ engine.

Năm thấu kính:
- **Kinh tế:** Local-first mua "retention qua mạng xấu" — ở thị trường mạng yếu (đường dài, tàu điện), đó là thị phần thật, không phải luxury.
- **Vận hành:** Schema local phải migrate (có user 6 tháng không mở app rồi update thẳng 3 version) — migration plan cho local store là bắt buộc, không phải edge case.
- **An ninh:** Local store = dữ liệu người dùng nằm ngoài kiểm soát bạn — mã hoá at-rest client (→6.7) + chính sách wipe từ xa cho thiết bị mất.
- **Lịch sử:** Lotus Notes từng là local-first thập niên 90 (replication là tính năng số một); Dropbox/GDocs dạy thế giới "sync là sản phẩm"; 2020s CRDT phổ quát hoá nó — ý tưởng cũ, toán mới.
- **Người dùng:** "Tôi viết dở ở trên máy bay, về nhà mở điện thoại thấy đủ" — câu đó là toàn bộ chương này; mỗi kiến trúc khác nhau chỉ là cách trả giá khác nhau cho câu đó.

---

## 8. Đọc tiếp & bài tập

- Xung đột & nhất quán: **8.1** · Idempotency: **4.8** · Đồng hồ: **1.9** · Push/energy: **6.4** · Wasm đồng nhất: **3.8**
- **Bài tập 1:** Mở app của bạn ở airplane mode, tạo 3 thao tác (viết/sửa/xoá), đóng app, mở lại khi có mạng. Mấy thao tác sống sót? Mỗi cái mất là một câu hỏi kiến trúc.
- **Bài tập 2:** Nếu app có sync: đo sync lag p95 hôm nay. > 30 giây khi active? Người dùng đang "nhìn thấy quá khứ" mà không ai báo.
- **Bài tập 3:** Chọn 1 entity: viết ra 3 kịch bản xung đột (2 máy, 2 field, xoá+sửa). Ai thắng hôm nay? Nếu không trả lời được trong 10 phút — quyết định đã để mặc định LWW ngầm quyết.
