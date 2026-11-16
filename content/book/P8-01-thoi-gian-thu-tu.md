# 8.1 — Thời gian, Thứ tự & Định lý Bất khả thi (FLP, CAP, PACELC)

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** lý thuyết vận hành hoá · **Động từ liên quan:** Hiểu · Chọn
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 1.9 (đồng hồ vật lý lệch) · 6.3 (LWW đã gặp).

**Sợi chỉ đỏ:** *Mặt tiền đẹp mà lưng chỉ có một máy chủ — DM nhân bản, và nhiều bản sao nghĩa là nhiều sự thật: ai đúng?* — trả lời: nhiều bản sao nghĩa là nhiều sự thật — chương này đặt nền: đồng hồ vật lý lệch là gốc của nửa sự cố phân tán; thứ tự thật nằm ở happens-before và đồng hồ logic; FLP chứng minh đồng thuận hoàn hảo không tồn tại; CAP, PACELC đọc đúng trước khi trích. Câu hỏi để lại cho chương sau: *Muốn một sự thật chung — đồng thuận kiểu Raft đánh đổi gì để có nó?*

**Thuật ngữ sẽ gặp:** *happens-before* — quan hệ "xảy ra trước": thứ tự nhân quả, không phải thứ tự đọc trên đồng hồ; *đồng hồ logic/vector clock* — Lamport đếm thứ tự, vector phân biệt "trước"/"song song" (nối 6.3); *FLP* — hệ bất đồng bộ thì đồng thuận hoàn hảo không đảm bảo: mọi hệ thật đều phải hy sinh gì đó; *CAP* — partition xảy ra thì chọn consistency hoặc availability: đừng trích sai như quảng cáo; *PACELC* — kể cả không partition vẫn đổi latency lấy consistency: phần hay bị quên; *NTP lệch* — vài miligiây tới hàng trăm (1.9).

**Ví dụ mở đầu:** Đơn được ghi ở app A lúc 10:00:00.012, kho ghi nhận "đã nhận lúc 10:00:00.009" theo hai đồng hồ khác nhau — "cái nào trước" không trả lời được bằng thời gian vật lý. Nửa sự cố phân tán của DM bắt nguồn từ câu hỏi tưởng ngây thơ đó. Đây là nền của cả quyển phía sau.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Dùng thời gian nào: vật lý (NTP/PTP) hay logic (Lamport/vector/HLC) | Tôi cần "khi nào" (đồng hồ tường) hay "trước/sau" (thứ tự nhân quả)? |
| 2 | Khi mất liên lạc (partition): chọn C hay A — theo nghiệp vụ nào | Tính năng này giữa partition: từ chối hay tiếp tục nhận sai? |
| 3 | Độ trễ sẵn sàng trả thường ngày (không partition) | PACELC: tôi trả latency để có consistency ở mức nào? |
| 4 | Ngưỡng coi "mất liên lạc" (timeout) đo thế nào | Timeout của tôi dựa trên gì — số đo hay cảm giác? |

---

## 2. Cơ chế

### 2.1 Thời gian vật lý lệch — gốc của nửa sự cố phân tán

Đồng hồ máy không đi cùng nhau: NTP giữ sai số ~ms trên LAN, chục–trăm ms trên WAN khi tệ (và có thể nhảy cả giây khi sync lại — I). Hệ quả: "last-write-wins theo timestamp" giữa hai máy là ngẫu nhiên (→6.3 đã gặp ở client). Giải pháp theo tầng: NTP cho log; **PTP/GPS + hardware timestamp** khi cần sub-ms (tài chính); và **không bao giờ** dùng giờ tường cho thứ tự — dùng phiên bản/logical clock.

### 2.2 Thứ tự: happens-before và ba loại đồng hồ logic

- **Lamport clock:** mỗi tiến trình đếm tăng khi có sự kiện; nhận tin thì nhảy lên max — cho **thứ tự toàn cục nhất quán với nhân quả**, nhưng không phát hiện "song song";
- **Vector clock:** mỗi node giữ mảng đếm của mọi node — so hai sự kiện biết được **nhân quả / song song (conflict)** — cơ sở của Dynamo-style conflict detection (→5.5);
- **Hybrid Logical Clock (HLC):** giờ vật lý + phần logic — vừa soạn log theo giờ người đọc được, vừa giữ nhân quả; được dùng trong CockroachDB/YugabyteDB-style DB phân tán.

Quy tắc chọn: **log & debug → HLC; phát hiện xung đột → vector; còn lại → Lamport đủ.**

### 2.3 FLP — vì sao "đồng thuận hoàn hảo" không tồn tại

Định lý Fischer–Lynch–Paterson (1985): trong hệ **bất đồng bộ** (không chặn trên độ trễ), không thuật toán đồng thuận nào chắc chắn chấm dứt nếu **một** node có thể chết. Thực tiễn sống nhờ: (a) **timeout + random** (Raft: bẻ tie bằng thời gian ngẫu nhiên); (b) giả định "độ trễ hữu hạn trong đa số thời gian" (partial synchrony — model thực tế của mọi hệ đang chạy); (c) chấp nhận p nhỏ phân vân. Bài học vận hành: **election timeout là tham số sinh tử** — quá ngắn: bầu leader liên tục khi mạng chậm (I-054 → §5); quá dài: thời gian không leader kéo dài.

### 2.4 CAP — đọc đúng trước khi dùng

Một partition (mất tin giữa hai nhóm node) ép chọn: **C** (từ chối ghi ở nhóm thiểu số) hay **A** (cả hai nhóm nhận, chấp nhận lệch). Ba điểm hay bị đọc sai:
1. C/A chỉ "bất lực" **trong lúc partition** — bình thường vẫn có cả hai (với giá latency);
2. Chọn **theo nghiệp vụ từng tính năng**: giỏ hàng/like → AP; chuyển tiền/số dư → CP; không chọn cho cả hệ thống một nhãn;
3. "Chọn A" nghĩa là phải có chiến lược hoà giải khi partition lành lại (→6.3 CRDT/LWW, →8.4 read repair) — không có hoà giải thì AP = hỏng dữ liệu chậm.

### 2.5 PACELC — phần bị quên của CAP

**P**artition → chọn A hay C; **E**lse (bình thường) → chọn **L**atency hay **C**onsistency. Đồng bộ chéo node trước khi trả lời = nhất quán mạnh **nhưng** thêm RTT vào mỗi thao tác. Đây là lý do "hệ phân tán nhanh" thường là eventual consistency: người dùng không trả RTT chéo vùng cho mỗi lần ghi. Bảng ví dụ: Dynamo/Cassandra-style (PA/EL), ZooKeeper/etcd-style (PC/EC), Mongo-style primaries (PC/EC cho ghi). Gán nhãn hệ của bạn theo hai trục này — và **theo từng đường dẫn nghiệp vụ**, không theo hệ.

### 2.6 Nơi các định lý gặp thực tế

- NTP lệch → log không sắp được, LWW sai (I-048, §5);
- Timeout nhầm "chết" → hệ khoẻ bị coi hỏng, tự gây sự cố (định luật: **phát hiện lỗi phân tán không đáng tin cậy**);
- Clock hardware khác nhau → metrics có "độ dốc" khi truy vết chéo máy (→11.1 — trace cần cùng trục thời gian).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| NTP sai số | ms LAN; chục ms+ WAN tệ | I | |
| PTP | sub-ms với HW support | V | |
| Lamport/vector overhead | vài byte–chục byte/sự kiện | I | |
| Election timeout (Raft khuyến nghị) | RTT chéo node × ~10 | I | giấy Raft |
| Partition "thật" | hiếm nhưng chắc chắn xảy ra | I | theo năm |

---

## 4. Suy luận kiến trúc

- **S1:** Thời gian trong hệ phân tán là **quan hệ (trước/sau)**, không phải con số — mọi thiết kế dựa "timestamp so sánh" phải chỉ ra nguồn đồng hồ hoặc chịu rủi ro ngẫu nhiên.
- **S2:** Tham số trụ: clock offset phân phối theo cặp máy, tần suất term đổi (Raft), số lần LWW "thắng sai" (so với kỳ vọng).
- **S3:** CAP/PACELC là **bảng giá chọn theo đường dẫn**, không huy hiệu sản phẩm — mỗi endpoint một hàng; tài liệu hóa hàng đó là việc của kiến trúc sư (không phải của DB).
- **S4:** FLP dạy khiêm tốn: mọi "đảm bảo" đồng thuận đều kèm giả định (bounded delay, crash-only fault); đọc giả định của thuật toán trước khi hứa với khách hàng.
- **S5:** Đồng hồ tốt hơn đang rẻ hoá (PTP trong cloud, HLC trong DB) — nhưng metric "sai số đồng hồ" vẫn phải nằm dashboard (→11.5): tệ nạn của sự cố 8.1 là im lặng cho tới khi dữ liệu sai.
- **S6:** Khi "dữ liệu mất/ghi đè nhau không rõ lý do": đo clock offset giữa các máy ghi trước mọi điều tra khác — rẻ nhất và đúng thường nhất.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Log hai máy không sắp theo thứ tự (I-048) | NTP skew giữa app servers | so sánh `date -u` + chrony tracking | §2.1 |
| Leader bầu liên tục (flap) | RTT > election timeout | đo RTT chéo node; tăng timeout | §2.3 |
| Update "mất" ngẫu nhiên | LWW trên clock lệch | audit nguồn timestamp | §2.1 |
| Ghi chậm chéo vùng | EC trả giá RTT mỗi ghi | PACELC: xem đường dẫn | §2.5 |
| Trace có "độ dốc" thời gian | máy lệch + export chậm | đồng bộ + HLC trong trace | §2.6 |

---

## 6. Cách đo

```bash
# Đo lệch đồng hồ toàn fleet (không cần agent mới):
for h in app1 app2 db1; do echo -n "$h: "; ssh $h date -u +%s.%N; done
#   — lệch > 50 ms giữa cặp ghi chung dữ liệu là vấn đề thật

# NTP chất lượng từng máy: chronyc tracking / ntpq -p   (đọc offset, jitter)
# Raft health: đếm term tăng theo giờ trên cluster (etcd: etcdctl endpoint status)
```

Nguyên tắc: **dashboard có "clock offset tối đa giữa cặp máy quan trọng"** — nếu con số này không tồn tại, tổ chức đang giả định đồng hồ hoàn hảo (giả định luôn sai).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay NTP:** PTP/GPS (đắt, chính xác — khi nghiệp vụ cần); **thay logical clock:** single-writer cho mỗi khoá (serialization key) — biến bài toán phân tán thành bài toán hàng đợi, đúng cho quy mô vừa; many systems sống khoẻ bằng cách **tránh** đồng thuận thay vì làm nó tốt (→8.2 câu hỏi đầu tiên).

Năm thấu kính:
- **Kinh tế:** Consistency mạnh tính bằng RTT (tiền hạ tầng chéo vùng) + thời gian dev; eventual tính bằng chi phí hoà giải & chăm sóc khách hàng phàn nàn — hai hoá đơn khác nhau, cộng trước khi chọn.
- **Vận hành:** Sự cố phân tán hay xảy ra lúc hạ tầng yếu nhất (deploy, mất AZ) — drill partition chủ động ( Chaos-style, →8.7) để biết hệ chọn gì TRƯỚC khi thật.
- **An ninh:** Giờ lệch phá xác thực (Kerberos/token có window) và phá audit (log không sắp được → điều tra đứt) — an ninh là khách hàng lớn nhất của đồng hồ tốt.
- **Lịch sử:** Lamport (1978, "Time, Clocks, and the Ordering of Events") → FLP (1985) → CAP (Brewer 2000, định lý hoá bởi Gilbert–Lynch 2002) → PACELC (Abadi 2012): mỗi bước thu hẹp khoảng cách "định lý đẹp" và "hệ thật"; đều là bài học "trade-off tồn tại, chọn có chủ ý".
- **Người dùng:** Người dùng không biết CAP — họ biết "lúc mạng nhà mạng lỗi, tôi vẫn thêm được hàng vào giỏ (A) nhưng không thanh toán được (C)". Hai cảm giác đó cùng tồn tại trong một app tốt — chương này là lý do.

---

## 8. Đọc tiếp & bài tập

- Đồng thuận & lease: **8.2** · Giao dịch phân tán: **8.3** · Sharding/quorum: **8.4** · CRDT ở client: **6.3** · Đồng hồ chi tiết: **1.9**
- **Bài tập 1:** Với 3 tính năng chính của hệ thống bạn, gán nhãn CAP/PACELC theo **đường dẫn** (không theo hệ). Hàng nào khó gán = nơi chưa ai quyết — chính là rủi ro.
- **Bài tập 2:** Đo clock offset giữa các máy ghi chung dữ liệu (lệnh §6). > 100 ms? Mọi timestamp LWW của bạn đang là xúc xắc.
- **Bài tập 3:** Đếm số lần đổi leader (term) của cluster đồng thuận bạn trong 7 ngày. > vài lần/tuần không kèm sự cố thật = election timeout sai, không phải "vận may xấu".
