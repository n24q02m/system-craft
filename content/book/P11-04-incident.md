# 11.4 — Chỉ huy Sự cố & Postmortem

> **Tầng:** Vận hành · **Quyển II** · **Trục đọc:** độ tin cậy · **Động từ liên quan:** Điều phối · Học
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 11.1 (error budget) · 10.7 (phản ứng sự cố an ninh).

**Sợi chỉ đỏ:** *Sự cố lúc 2h sáng — ai chỉ huy, ai nói với khách, học được gì?* — trả lời: sự cố 2h sáng — ai chỉ huy: incident commander giữ một tiếng nói và một la bàn; mitigate trước rồi mới hỏi vì sao; mức sev và đường escalation là bản đồ viết lúc trời quang; postmortem blameless hỏi cơ chế chứ không hỏi người; và on-call là điều kiện của mọi thứ trên. Câu hỏi để lại cho chương sau: *Hóa đơn cloud là SLO thứ hai — FinOps quản tiền theo đơn vị nào?*

**Thuật ngữ sẽ gặp:** *IC* — incident commander: chỉ huy, không code: một tiếng nói, một la bàn; *mitigate trước* — dừng cháy bằng rollback, shedding, tắt flag: nguyên nhân để sau, khách hàng trước; *sev matrix* — mức độ và ai gọi ai: viết lúc bình thường, không viết lúc đang cháy; *blameless postmortem* — hỏi "cơ chế nào cho phép lỗi này" chứ không "ai sai": văn hoá, không phải thủ tục; *near-miss* — gần-mất: chỉ khi báo cáo không bị phạt thì mới có dữ liệu thật; *on-call* — vòng trực có giá: đo page, đo burnout — điều kiện tồn tại của cả chương.

**Ví dụ mở đầu:** Sự cố 2h sáng đầu tiên của DM: mười hai người vào call, ai cũng nói, thời gian mitigate nhân đôi. Vụ sau có IC: một người giữ la bàn, một người nói với khách, việc chạy song song. Khác biệt không nằm ở kỹ năng — mà ở bản đồ viết sẵn từ lúc trời quang.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Vai trò khi sự cố: IC / Ops / Comms / Scribe | Ai giữ la bàn khi mọi người hoảng — và có được đào tạo trước không? |
| 2 | Mitigate trước hay điều tra trước | Dừng chảy máu trước, tìm hiểu sau — tổ chức tôi có tin câu này không? |
| 3 | Sev level & đường kích hoạt (ai được đánh thức) | Điều gì là Sev1 của tôi — viết trước bằng nghiệp vụ, không bằng cảm giác lúc cháy? |
| 4 | Postmortem: blameless, action item theo dõi thế nào | Sự cố xong 2 tuần — có gì đổi thật không (có chữ ký theo dõi không)? |

---

## 2. Cơ chế

### 2.1 Chỉ huy sự cố (IC) — one voice, one compass

Bộ vai chuẩn (đơn giản hoá từ ICS — firefighting thật):
- **IC (Incident Commander):** giữ bức tranh toàn cảnh, **không trực tiếp gõ lệnh** — phân công, quyết ưu tiên, theo dõi thời gian; thay phiên khi dài (> 4–6 h);
- **Ops lead:** gõ lệnh mitigate (nhóm kỹ thuật);
- **Comms:** viết cập nhật định kỳ cho stakeholder/lãnh đạo/khách (mỗi 30–60 phút — im lặng là tin xấu tự sinh);
- **Scribe:** ghi timeline (tín hiệu, quyết, ai — bằng chứng cho postmortem);
- **Chuyên gia chủ đề**: vào khi cần, ra khi xong (đừng 20 người trong một channel).

Vì sao phân vai sống còn: stress làm nhận hẹp lại (tunnel vision) — người vừa gõ lệnh vừa giữ bức tranh là người gõ lệnh vào sai cửa; IC rảnh đầu để nghĩ là **thiết kế, không phải may mắn**.

### 2.2 Mitigate trước — dừng cháy, rồi mới hỏi vì sao

Bốn lựa chọn mitigate theo thứ tự tốc độ: **rollback** (→9.7 — phút), **feature flag off** (→8.8 — giây–phút, có khi không cần rollback cả deploy), **scale/failover** (→9.2/8.7 — phút), **chặn lưu lượng** (shedding →8.5 — tức thì). Điều tra nguyên nhân gốc **sau** khi máu cầm — trừ khi mitigate xóa chứng cứ (khi đó: snapshot trước — →10.7 cùng luật). Anti-pattern số một của tổ chức non: 45 phút tranh luận "tại sao" trong lúc hệ vẫn chảy máu và khách vẫn thấy lỗi.

### 2.3 Sev & escalation — bản đồ viết lúc trời quang

| Mức | Định nghĩa nghiệp vụ | Kích hoạt |
|---|---|---|
| Sev1 | khách hàng chính không dùng được / dữ liệu sai / an ninh | đánh thức mọi vai (kể cả lãnh đạo biết) |
| Sev2 | tính năng chính hỏng, có cách vòng | on-call + IC trong giờ |
| Sev3 | phiền, chưa gấp | ticket, xử lý trong ngày |

Định nghĩa phải là **nghiệp vụ** ("khách không thanh toán được"), không phải kỹ thuật ("DB CPU 100%" — có khi khách vẫn vui). Đường kích hoạt (pager tree) + ai được quyền tuyên bố Sev1 (nhiều người — tuyên bố nhầm còn rẻ hơn tuyên bố muộn) + kênh liên lạc chuẩn (một channel sự cố + một bridge call — không họp trong comment).

### 2.4 Postmortem blameless — vì sao và làm sao

Blameless không phải "không ai sai" — là **tìm hệ thống sai**, không tìm người dại: "dev nào merge cái đó?" dẫn tới giấu lỗi lần sau; "tại sao quy trình cho phép cái đó tới prod mà không ai thấy?" dẫn tới hệ không tái diễn. Khung báo cáo chuẩn: **Tóm tắt** (ai bị ảnh hưởng, bao lâu) → **Timeline** (phát hiện → mitigate → phục hồi, giờ chính xác) → **Nguyên nhân gốc** (5-whys tới quy trình/thiết kế, dừng ở "con người" là chưa đủ sâu) → **Điều gì chạy tốt / hỏng** (cả phát hiện lẫn phản ứng) → **Action items** (mỗi cái có **chủ + hạn + issue số** — tracking như tính năng, không phải lời hứa).

### 2.5 Học từ gần-mất (near-miss) và từ người khác

- **Near-miss** (bắt được trước khi lan) cũng đáng postmortem-lite: tiềm năng cùng cơ chế, giá bằng 0 — bỏ qua là bỏ dữ liệu miễn phí;
- **Diễn tập từ sự cố của người khác** (báo cáo công khai của cloud lớn, các công ty công nghệ): đọc 15 phút, hỏi "hệ tôi dính cái này không?" — 80% sự cố lớn của ngành là dạng lặp lại (DNS, cert, config, dependency — đủ bài trên báo);
- **Error budget review** (→11.1): mỗi sự cố tiêu bao nhiêu budget, xu hướng quý — liên kết kỹ thuật với kinh doanh bằng con số.

### 2.6 On-call — điều kiện của mọi thứ trên

On-call lành mạnh: **số lần báo động/tháng có ngưỡng** (quá = tự động hoá trước khi thêm người), **tuần luân phiên có bồi dưỡng** (không phải danh dự), **handoff có bản ghi** (passdown — cảnh báo đang treo, việc đang nửa chừng), và **sau mỗi trực kỳ tồi** — sửa nguyên nhân alert (→11.1 precision) thay vì "chịu khó". On-call kiệt sức là nợ: lãi là người giỏi nghỉ việc (chi phí thật — 11.6).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Cập nhật comms | 30–60 phút/lần khi Sev | P | |
| Postmortemdeadline | 5 ngày làm việc sau sự cố | P | |
| Action item có chủ+hạn | 100% | P | không phải = tưởng niệm |
| MTTD/MTTR | metric trụ của 11.4 | P | |
| Alert/tuần on-call | < ~2–5 pages (khỏe) | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Sự cố là **thí nghiệm không xin phép** — chương 11.3 (chaos) là phiên bản có kiểm soát; tổ chức tốt biến sự cố thật thành dữ liệu quý (timeline + action) thay vì chỉ thành pain;
- **S2:** Tham số trụ: MTTD/MTTR theo Sev, số postmortem có action item đóng trong 30 ngày, số near-miss ghi nhận (trend văn hoá), alert/noise ratio cho on-call.
- **S3:** IC tách khỏi Ops đổi "mọi người lao đi" lấy "một người giữ bức tranh" — chi phí: một người không gõ lệnh khi đang thiếu người; giá trị: không mất 40 phút chạy vòng ở sai tầng (đã đo được ở mọi org từng cài IC).
- **S4:** Mọi chương của atlas là action item của một sự cố nào đó trong ngành — postmortem là **cơ chế quay vòng kinh nghiệm ngành vào tổ chức bạn**; không có postmortem thì mỗi thế hệ team tái học bằng chính tiền của mình.
- **S5:** AI vào phòng sự cố hai vai: (a) trợ lý tổng hợp timeline/log (LLM đọc telemetry — →11.2 — và nháp postmortem); (b) **nguyên nhân mới** (agent tự đổi config/upgrade phụ thuộc — sự cố "AI gây" cần playbook riêng: ai tắt agent? audit trail gì? — →12.7);
- **S6:** Khi sự cố lặp lại lần ba **cùng cơ chế**: đó không phải sự cố nữa — đó là **quyết định cấp tổ chức** chấp nhận rủi ro (hoặc từ chối action item đau); viết rõ điều đó lên lá thư lãnh đạo — im lặng lần ba là lựa chọn, hãy gọi tên nó.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Sự cố kéo dài vì 20 người "cùng cứu" | Không có IC | cài vai + đào tạo | §2.1 |
| Mitigate chậm vì tranh luận nguyên nhân | Văn hoá "tại sao trước" | mitigate-first + drill | §2.2 |
| Postmortem thành tổ họp đổ lỗi | Blame framing | template blameless + lãnh đạo mở đầu | §2.4 |
| Action item chết sau 2 tuần | Không tracking | issue + chủ + hạn + review | §2.4 |
| Khách biết trước nội bộ (Twitter) | Comms không kênh | cập nhật định kỳ + status page | §2.3 |
| On-call kiệt sức, người giỏi nghỉ | Alert ồn không sửa | precision alert (→11.1) + tự động hoá | §2.6 |

---

## 6. Cách đo

```bash
# Sau mỗi sự cố, điền 6 con số (dán vào postmortem):
#   MTTD (vào → phát hiện), MTTA (phát hiện → người xem),
#   MTTM (xem → mitigate), MTTR (tổng), % khách ảnh hưởng, budget tiêu (→11.1)
# Trend 6 con số theo quý — chúng là "hệ hô hấp" của tổ chức vận hành

# Drill 15 phút mỗi quý: kịch bản giả, chạy đúng vai (IC/Ops/Comms),
#   đo riêng: bao lâu có cập nhật khách đầu tiên?
```

Nguyên tắc: **sự cố được đánh giá bằng đường cong phục hồi và bằng thứ để lại** (postmortem + thay đổi) — không bằng việc "có ai bị mắng không".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay IC mô hình đầy đủ:** cho đội < 10 người — một "người giữ điện thoại" + checklist (đủ, trung thực về quy mô); **thay postmortem đầy đủ cho sự cố nhỏ:** bản ghi 5 dòng (việc gì, vì sao, làm gì để không tái diễn) — 100% ghi còn hơn 20% nghi thức; **thay pager tree:** một kênh chung + tự phân công (vỡ ở quy mô — nhưng đúng lúc nhỏ).

Năm thấu kính:
- **Kinh tế:** MTTR là chỉ số tài chính (phút downtime × doanh thu/phút + chi phí uy tín); đầu tư vào vai/training/postmortem là bảo hiểm có ROI đo được ngay mùa sự cố đầu tiên;
- **Vận hành:** Postmortem chỉ mạnh khi **action item có chỗ sống** (backlog ưu tiên như bug — không phải file "lessons learned" không ai mở); review các item cũ mỗi tháng;
- **An ninh:** Sự cố an ninh (→10.7) dùng khung này thêm lớp nhạy cảm (thông tin hạn chế, pháp lý 72h — →10.8) — IC cho security cần thêm "ai được biết gì" trong bảng vai;
- **Lịch sử:** "War room" (1990s — phòng máy thật, pizza) → incident channel (2010s) — cùng một nguyên lý chỉ huy tồn tại từ đội cứu hoả thế kỷ 19 (ICS): **khủng hoảng cần cấu trúc định sẵn** vì não người trong stress không thiết kế được cấu trúc;
- **Người dùng:** Khách không nhớ hệ bạn chưa từng chết (không có hệ nào) — khách nhớ **cách bạn cư xử lúc chết**: có nói thật, có cập nhật, có sửa để không tái diễn. Chương này là kỹ thuật đứng sau ba câu trả lời đó.

---

## 8. Đọc tiếp & bài tập

- SLO/budget: **11.1** · Telemetry cho MTTD: **11.2** · Chaos drill: **11.3** · Security IR: **10.7** · Rollback/flag: **9.7, 8.8** · Văn hoá & tổ chức: **11.6**
- **Bài tập 1:** Viết bản đồ Sev cho sản phẩm (3 mức, định nghĩa nghiệp vụ, ai tuyên bố, ai bị đánh thức). Một trang — và gửi cho lãnh đạo ký; có chữ ký, 2h sáng không phải họp "cái này có phải Sev1 không".
- **Bài tập 2:** Chạy drill 15 phút (§6): kịch bản giả + đúng vai. Đo thời gian tới cập nhật khách đầu tiên. > 30 phút? Comms là vai thiếu của bạn — đó là phát hiện quý.
- **Bài tập 3:** Lấy sự cố gần nhất: viết lại theo template §2.4 (nếu chưa có). Kiểm 6 con số §6 — con số nào không có dữ liệu (thường MTTD)? Đó là gap telemetry (→11.2) lộ ra từ chính nỗi đau.
