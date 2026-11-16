# 8.7 — Đa vùng, Cell-Based Architecture & DR

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** vũ trụ & thảm hoạ · **Động từ liên quan:** Chọn · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 8.2 (đồng thuận) · 8.4 (nhân bản, quorum).

**Sợi chỉ đỏ:** *Cháy nguyên một vùng — multi-region/DR cam kết gì (RTO, RPO) và trả bao nhiêu?* — trả lời: cháy nguyên một vùng là câu hỏi "cam kết gì" — RTO (mất tối đa bao lâu) và RPO (mất tối đa bao nhiêu dữ liệu) là hợp đồng thảm hoạ phải ghi bằng số; bốn cấp đa vùng từ backup xa tới active-active; xung đột đa vùng có ba con đường; DR thật bằng drill, không bằng tài liệu. Câu hỏi để lại cho chương sau: *Ship liên tục không gián đoạn — migration, flag, canary đi đường nào?*

**Thuật ngữ sẽ gặp:** *RTO/RPO* — thời gian khôi phục tối đa và lượng dữ liệu chấp nhận mất: hợp đồng ghi số, không ghi "nhanh nhất có thể"; *bốn cấp đa vùng* — backup xa, cold, warm, active-active: mỗi cấp gấp hoá đơn; *ba con đường xung đột* — tránh (route theo vùng), giải tự động (CRDT, LWW — 6.3), hoà ngược (người quyết); *cell-based* — chia hệ thành cell độc lập: cháy một cell không lan (blast radius); *drill* — tập sự cố định kỳ: chưa drill là DR tưởng tượng; *độ hạt thảm hoạ* — bảo vệ tới tủ, tới zone, tới vùng: chọn theo giá.

**Ví dụ mở đầu:** AZ cháy giữa giờ cao điểm của DM: bản active-active chạy tiếp và xử lý xung đột ghi theo ba con đường; bản warm standby mất hai chục phút chuyển đổi; bản "backup trong tủ" mất kể từ lần backup gần nhất. Ba mức — ba hoá đơn. Chương này giúp chọn mức xứng với từng loại dữ liệu.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Multi-region: active-passive / active-active / theo vùng người dùng | Vùng nào chết — tôi phục hồi trong bao lâu, mất bao nhiêu ghi (RTO/RPO)? |
| 2 | Conflict resolution khi active-active | Hai vùng cùng ghi một dữ liệu — ai thắng, khách thấy gì? |
| 3 | Kích thước & cấu trúc cell (blast radius) | Một lỗi lan tối đa bao nhiêu % người dùng? |
| 4 | DR: kịch bản nào được drill, tần suất | Tôi có bằng chứng (không phải niềm tin) là failover chạy được? |

---

## 2. Cơ chế

### 2.1 Bậc thang đa vùng — bốn cấp

```
1. Một vùng            — chết vùng = chết hệ thống (RTO = dựng lại)
2. Backup chéo vùng    — RPO = chu kỳ backup; RTO = giờ–ngày (khôi thủ công)
3. Active-Passive      — standby nóng: replicate liên tục (RPO ~s–phút),
                          DNS/route chuyển (RTO ~phút); không phục vụ traffic
4. Active-Active       — nhiều vùng phục vụ cùng lúc: RTO ≈ 0 nhưng phải giải
                          conflict + nhất quán chéo (mọi thứ 8.1–8.4 về đúng đây)
```

Càng lên cao càng đắt không phải vì máy — vì **mỗi cấp mở ra một lớp bài toán mới**: cấp 3 lo replication lag & split brain (→8.2/8.4); cấp 4 lo conflict + trải nghiệm latency chéo vùng (PACELC — →8.1). Quy tắc chọn vùng active theo **người dùng** (Latency — →1.6), không theo giá máy đơn thuần.

### 2.2 RTO/RPO — hợp đồng thảm hoạ

- **RPO** (mất tối đa bao nhiêu dữ liệu): quyết bởi **cách replicate/backup** (async = giây; backup giờ = giờ);
- **RTO** (downtime tối đa): quyết bởi **quy trình chuyển** (DNS TTL! — TTL 1h = failover chậm nhất 1h; đặt 60 s khi cần);
- **RHO** (mức phục hồi degraded) — thứ ba ít được hỏi: sau failover, hệ chạy **bao nhiêu % công suất**? (standby thường nhỏ hơn chính — nhỏ quá là "đúng giờ nhưng sập vì tải").

Ba con số này phải được **phê duyệt bởi nghiệp vụ** như SLO (→11.2) — kỹ thuật chỉ báo giá: mỗi bậc §2.1 tương ứng một bộ RTO/RPO/RHO và một hóa đơn.

### 2.3 Active-Active: ba con đường xử lý xung đột

1. **Phân vùng ghi theo khu vực** (user VN ghi vùng VN — regional write; conflict chỉ khi chuyển vùng giữa chừng): đơn giản nhất, phổ biến nhất;
2. **CRDT/merge tự động** (→6.3): cho dữ liệu hội tụ được (counters, set, text) — không cho dữ liệu "một giá trị đúng";
3. **Quorum chéo vùng** ( ghi đa số vùng): nhất quán mạnh + latency mỗi ghi = RTT chéo vùng xa nhất — thường chỉ cho metadata/tài khoản, không cho mọi thao tác.

Thực chiến: trộn cả ba theo loại dữ liệu (bảng per-entity — như bài học CAP của 8.1: quyết theo đường dẫn, không theo hệ).

### 2.4 Cell-based architecture — chia để khống chế blast radius

**Cell** = một bản triển khai độc lập đủ phục vụ một phần người dùng (traffic + data + config riêng; có thể là "shard" theo tenant — →8.4/5.14). Người dùng gắn cell (định tuyến ở tầng gateway/metadata); lỗi trong một cell chỉ ảnh hưởng cell đó. Điều khiển: **control plane** (không nằm trong cell) quản DANH SÁCH cell + định tuyến — chính nó phải siêu dự phòng (→8.2 đồng thuận). Lợi ích lớn nhất không phải uptime — mà là **triển khai an toàn**: deploy 1 cell → theo dõi → đẩy tiếp (canary có ranh giới cứng), và **cách ly tin đồn xấu**: cell xấu route ra, người dùng "đổi cell" (shuffle sharding — mỗi user thấy tổ hợp node riêng, giảm chồng lấn nạn nhân giữa các user).

### 2.5 DR thật = drill

Tài liệu DR không đọc từ 2h sáng được; hệ standby không được drill thì **không tồn tại** (tin đồn có backup cũng vậy — test restore — →5.13). Chương trình DR chuẩn: **game day định kỳ** (tắt vùng chủ động ở staging hoặc production có kiểm soát), đo RTO/RPO thật, viết sai khác giữa tài liệu và thực tế, sửa, lặp. Vấn đề thường lộ ra: DNS TTL dài hơn kế hoạch, connection pool treo (không timeout — →8.5), sequence/ID trùng (hai vùng sinh ID đụng nhau — chuẩn bị: range phân vùng hoặc ID có phần vùng), và "standby thiếu dữ liệu tham chiếu mới".

### 2.6 Chọn độ hạt của thảm hoạ được bảo vệ

| Thảm hoạ | Bảo vệ | Chương |
|---|---|---|
| Một process chết | restart/k8s | 9.1 |
| Một máy chết | multi-node + replica | 8.4 |
| Một AZ chết | placement chéo AZ | 8.4, 9.1 |
| Một vùng chết | multi-region | 8.7 |
| Một service chết | bulkhead/isolation | 8.5 |
| Một cell "điên" | cell boundary + shuffle | 8.7 |
| Lỗi logic triển khai | canary + rollback nhanh | 9.7 |
| Sai sót dữ liệu người | backup point-in-time + audit | 5.13 |

Đừng trả tiền bảo vệ thứ không thể xảy ra và đừng giả định thứ xảy ra hàng năm (AZ chết) là "không thể" — bảng này là checklist đối thoại với lãnh đạo về **tiền**.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| DNS TTL cho failover | 30–60 s khi cần nhanh | P | |
| Replication chéo vùng latency | 50–200 ms một chiều (theo cặp vùng) | I | |
| RPO async chéo vùng | ~giây–chục giây | I | theo khoảng cách |
| Drill DR tần suất | quý–nửa năm | P | |
| Blast radius mục tiêu | 1–10% người dùng/cell | P | theo nghiệp vụ |

---

## 4. Suy luận kiến trúc

- **S1:** Đa vùng là **bậc thang chi phí phi tuyến** — mỗi cấp giải bài toán cấp trước và mở ra hai bài mới; đi đúng cấp nghiệp vụ cần (bảng RTO/RPO ký duyệt), không đi theo khẩu hiệu khoe khoang.
- **S2:** Tham số trụ: RTO/RPO **đo được từ drill** (không phải từ tài liệu), blast radius % user của một deploy/cell, tỉ lệ traffic từng vùng, chi phí vùng dự phòng đang "ngủ".
- **S3:** Cell đổi chi phí vận hành (nhiều "cluster" nuôi + định tuyến) lấy cách ly lỗi + triển khai an toàn — đáng khi số người dùng đủ lớn để 1% cell vẫn là đơn vị kinh doanh có nghĩa.
- **S4:** Control plane (định tuyến, danh sách cell, config) là **điểm singleton logic** — dùng kỹ thuật 8.2 và nuôi nó như sản phẩm riêng; control plane chết = chết kiểu "không thể route", tệ hơn chết cell.
- **S5:** Định tuyến người dùng theo vùng/nearness (latency-based) + cell-aware client (→6.4/WebPush-style token route) đang hợp nhất: client biết "home cell" của mình, giúp failover nhanh hơn DNS.
- **S6:** Khi thảm hoạ thật xảy ra: thứ giết bạn thường không phải thiết kế — mà là **tham số mòn** (TTL dài, pool không timeout, standby thiếu bảng mới) — drill là cách duy nhất phát hiện sự mòn này trước khách hàng.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Failover kéo dài quá RTO | DNS TTL/pool treo | đo từng chặng failover | §2.2, §2.5 |
| Standby lên rồi sập tiếp | RHO không đủ (quá nhỏ) | tải thử standby | §2.2 |
| Sau split vùng, dữ liệu đụng nhau | ID/sequence trùng vùng | range ID mỗi vùng | §2.5 |
| Lỗi lan cả hệ (I-056) | Không chia cell (blast radius) | vạch ranh giới cell | §2.4 |
| Active-active "lộp bộp" dữ liệu | Conflict không thiết kế | bảng per-entity §2.3 | §2.3 |
| DR kế hoạch nằm bụi | Không drill | lịch game day | §2.5 |

---

## 6. Cách đo

```bash
# Đo RTO thật (game day, mỗi quý):
#   T0: tắt vùng chính (hoặc withdraw route có kiểm soát)
#   T1: hệ phục vụ lại yêu cầu thành công từ vùng phụ (từ bên ngoài đo — synthetic check)
#   RTO = T1 - T0; RPO = so mốc dữ liệu cuối giữa hai vùng
#   — chạy trong giờ làm việc, có người mổ xẻ, ghi lại mọi chỗ "không như tài liệu"

# Blast radius: với mỗi deploy tuần này: tối đa bao nhiêu % user nhận bản mới đầu?
#   (canary 1% → 10% → all = 10% max; big-bang = 100% max)
```

Nguyên tắc: **RTO/RPO không có số đo từ drill thì chưa phải con số — là ước tính marketing**; mọi chương trình DR nghiêm túc có một bảng "lần drill gần nhất, kết quả, chênh lệch kế hoạch".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay active-active:** active-passive + chấp nhận vài phút downtime (phần lớn nghiệp vụ chấp nhận được và rẻ hơn một bậc độ lớn); **thay cell tự dựng:** đặt nhiều "deployment" trong một region/AZ khác nhau + định tuyến tenant (bán cell mềm); **thay multi-region:** multi-AZ (giải 90% thảm hoạ thật với 10% chi phí).

Năm thấu kính:
- **Kinh tế:** Vùng dự phòng không chạy traffic là **tiền ngủ** — cân nhắc chạy workload phi quan trọng (batch, staging) trên đó để ít tốn hơn, hoặc bán "thiệt hại downtime" cho lãnh đạo để quyết định đúng cấp đầu tư.
- **Vận hành:** Mỗi vùng/cell thêm một bộ runbook + dashboard — đảm bảo tooling mô tả được "đang nhìn vùng nào" (lỗi số một của sự cố đa vùng: mọi người nhìn màn hình của vùng chết và tưởng hệ thống mất).
- **An ninh:** DR mở mặt diện an ninh (region phụ: ai có quyền? secret replicated đúng cách — →11.6? key management chéo vùng phải được drill cùng); tội phạm cũng biết vùng phụ là đường vào ít được giám sát.
- **Lịch sử:** Hot site/cold site (thập niên 80 — phòng máy vật lý) → cloud multi-AZ (2010s, rẻ hoá) → active-active global + cell (AWS/Netflix/Google công bố 2010s–2020s): mỗi thế hệ hạ thấp giá của cấp trước — và nâng kỳ vọng của khách hàng tương ứng.
- **Người dùng:** Người dùng chỉ trải qua một câu: "tối qua hệ giật 3 phút" hay "tối qua tôi không biết hệ vừa chuyển vùng". Khác biệt giữa hai câu là toàn bộ chương này.

---

## 8. Đọc tiếp & bài tập

- Canary/progressive: **9.7** · Sharding/tenant: **8.4, 5.14** · Đồng thuận control plane: **8.2** · SLO: **11.2** · Backup/restore: **5.13**
- **Bài tập 1:** Viết RTO/RPO/RHO của hệ thống bạn — rồi hỏi nghiệp vụ ký. Nếu không ai dám ký con số nào → hiện không có cam kết thảm hoạ nào cả (đây là phát hiện giá trị).
- **Bài tập 2:** Tính blast radius của deploy gần nhất: % user nhận bản mới trong giờ đầu. 100%? Đề xuất canary 10% tuần sau — đo sự khác biệt.
- **Bài tập 3:** Chạy game day 30 phút: tắt một bản sao dịch vụ chính ở staging, đo tới khi khôi phục. Ghi 3 chỗ thực tế khác tài liệu — đó là 3 ticket thật.

