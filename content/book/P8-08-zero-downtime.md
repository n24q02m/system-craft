# 8.8 — Tiến hoá Không gián đoạn (Expand-Contract, Strangler, Flags)

> **Tầng:** Lõi phân tán · **Quyển II** · **Trục đọc:** kiến trúc ứng dụng · **Động từ liên quan:** Migrate · Duy trì
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 4.8 (versioning hợp đồng) · 8.3 (outbox).

**Sợi chỉ đỏ:** *Ship liên tục không gián đoạn — migration, flag, canary đi đường nào?* — trả lời: ship liên tục không gián đoạn chỉ có một nguyên lý — mọi bước phải có đường lùi; từ đó sinh ra expand-contract đổi schema online, strangler fig dời hệ thống từng mảnh, parallel run chạy song song lấy bằng chứng, feature flag là gây tê tại chỗ. Câu hỏi để lại cho chương sau: *Tự vận hành chục máy thủ công đã chật — Kubernetes và control plane gánh việc gì?*

**Thuật ngữ sẽ gặp:** *expand-contract* — thêm cột mới, chép dữ liệu, đổi đường đọc, xoá cột cũ: ba bản deploy nhỏ thay một ALTER khoá bảng; *strangler fig* — route từng chức năng sang hệ mới cho tới khi hệ cũ tự biến mất: dây leo bao cây; *parallel run* — cũ và mới chạy song song, so kết quả: bằng chứng trước niềm tin; *feature flag* — bật tắt tính năng mà không deploy lại: gây tê tại chỗ — và là nợ phải dọn; *đổi hợp đồng đang chạy* — thêm trường dễ, bỏ trường phải chờ mọi client nâng cấp (nối 4.8); *đường lùi* — mỗi bước có kế hoạch rollback trước khi bấm: không có đường lùi là không được ship.

**Ví dụ mở đầu:** Đổi định danh khách hàng của DM từ số sang UUID khi hệ đang chạy: một ALTER duy nhất là hai chục phút khoá bảng. Expand-contract chia thành ba bản deploy, mỗi bản lùi được trong một phút. Chương này là kỹ thuật phẫu thuật cho hệ thống không được phép ngừng thở.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Migration schema: expand-contract (online) hay cửa sổ bảo trì | Bảng này to và quan trọng cỡ nào — downtime bao nhiêu phút được phép? |
| 2 | Di dời hệ thống: big-bang, song song chạy, hay strangler dần | Tôi tin cài đặt mới cỡ nào — có cách quay đầu ở mỗi bước không? |
| 3 | Feature flag: bộ nào, thời gian sống, ai dọn | Mỗi flag là nhánh code sống thêm bao lâu? |
| 4 | Rollback của chính cuộc di dời | Bước N hỏng — quay về bước N-1 thế nào, trong bao lâu? |

---

## 2. Cơ chế

### 2.1 Nguyên lý: mọi bước phải có đường lùi

Downtime thật của một migration lớn thường không đến từ thiết kế — mà từ **bước không có đường lùi** (sau khi `DROP COLUMN` thì không quay đầu). Kỹ thuật chương này là cùng một ý tưởng áp vào ba chất liệu: schema, hệ thống, luồng code.

### 2.2 Expand-Contract — di chuyển schema online

```
GIAI ĐOẠN 1 (expand):  thêm cột/bảng/index MỚI song song — không đụng đường cũ
                        (index online: CREATE INDEX CONCURRENTLY — PG-style)
GIAI ĐOẠN 2 (backfill): đổ dữ liệu cũ → mới theo lô nhỏ, throttle (→5.15)
GIAI ĐOẠN 3 (switch):   code ghi ĐÔI (cũ+mới) rồi đọc MỚI — theo flag từng % user
GIAI ĐOẠN 4 (contract): xóa đường cũ (cột, index) — chỉ sau khi không còn reader
```

Ba cái bẫy nắm rõ: **backfill dập DB** (khối lượng lớn — batch + ngủ giữa lô, đo replication lag); **đọc giữa giai đoạn** thấy dữ liệu nửa cũ nửa mới (đọc một nguồn trong một request); **quên contract** (cột chết nằm đó năm năm — "migration" chưa xong, chỉ mới xong phần vui). Rewrite truy vấn đường nóng trước khi thêm index — nhiều khi vấn đề không cần cột mới (→5.16).

### 2.3 Strangler Fig — di dời hệ thống bằng dây leo

Hệ mới "quấn" dần hệ cũ: **facade/router** đứng trước (chỉ định tuyến, không logic), từng nhóm endpoint chuyển sang hệ mới (theo route, rồi theo % traffic); hệ cũ co lại tới xoá. Bài học vận hành: (1) định tuyến phải **đo được hai bên** (so sánh kết quả cũ/mới — shadow/dark launch); (2) dữ liệu: hoặc chia sẻ (DB chung — tách sau) hoặc CDC đồng bộ (→5.15); (3) cập nhật **liên tục đánh giá phần còn lại** — strangler dở dang mãi là nợ, đặt mốc "tắt hệ cũ ngày X" công khai.

### 2.4 Song song chạy (parallel run) — bằng chứng trước niềm tin

Gửi cùng request cho hai hệ (một phục vụ thật, một "gác"), so sánh kết quả; sai khác = bug tìm thấy **trước** khi khách thấy. Chi phí: gấp đôi compute cho phần di dời + hạ tầng diff — trả cho những migration không được sai (tính tiền, tính lãi, định tuyến). Kết hợp §2.3: shadow tăng dần 1% → 100% sạch → switch thật.

### 2.5 Feature flag — phẫu thuật có gây tê

Flag tách **deploy** khỏi **release** (code lên production nhưng tắt; bật theo % user/cohort). Bộ tối thiểu: kill-switch (tắt ngay), percent rollout (canary — →8.7/9.7), cohort (nhân viên trước, khách sau). Hai kỷ luật sống còn: **flag có chủ + TTL** (mỗi flag ghi ngày xóa dự kiến — quá 2 sprint không xóa là "nợ flag", mỗi nhánh if là mặt lỗi mới (test matrix nhân đôi)); **trạng thái flag vào context sự cố** (sự cố 2h sáng: flag nào đang bật cho ai? — flag không hiện trong observability = tín hiệu gỡ rối mù — →11.1).

### 2.6 Đổi "hợp đồng" khi mọi bên đang chạy

Phiên bản cũ client vẫn gọi trong tháng (→6.1 ràng buộc #4), version cũ data vẫn nằm trong log (→8.3 event version hoá): quy tắc **additive-first, deprecate-có-lịch** (→4.8): thêm trường mới OK; đổi nghĩa trường cũ KHÔNG (thêm trường mới); xoá sau khi metric nói "không còn ai dùng" (không phải "ai đó nói chắc không"). Bảng theo dõi usage-by-version là điều kiện xoá (đã gặp ở 4.8 — nguyên lý lặp lại vì đây là nơi nó giết người).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Backfill batch | 1–10k rows, ngủ giữa lô | P | theo DB |
| Index online | CONCURRENTLY-style, không khoá ghi | V | PG/MySQL modern |
| Flag TTL | ≤ 1–2 sprint | P | |
| Strangler mốc | "tắt cũ" có ngày công khai | P | |
| So sánh shadow | sai khác ~0 trước switch | P | |

---

## 4. Suy luận kiến trúc

- **S1:** Khả năng tiến hoá là **thuộc tính thiết kế**, không phải nỗ lực anh hùng: hệ "dễ đổi" = mỗi bước có đường lùi (flag, expand, song song); hệ "khó đổi" = một bước không quay đầu.
- **S2:** Tham số trụ: số bước migration trong 6 tháng + tỉ lệ phải rollback, tuổi trung bình flag, thời gian từ "xong code" đến "bật 100%", dung lượng schema chết (cột không reader).
- **S3:** Parallel-run đổi compute lấy độ tin cậy — tính bằng "thiệt hại một lần sai"; strangler đổi thời gian dài lấy rủi ro thấp — cả hai đều **lệ thuộc observability** (đo được hai bên mới dám so).
- **S4:** Migration là bài toán **dữ liệu + phiên bản + tốc độ**, không chỉ code: kế hoạch không trả lời "dữ liệu đi đâu, phiên bản cũ sống bao lâu" là kế hoạch nửa vời (→5.15/4.8).
- **S5:** AI accelerate viết migration script — nhưng backfill/switch/rollback vẫn là **kế hoạch vận hành** (người quyết % user từng bước); tốc độ code mới làm nổi bật vai trò của kỷ luật bước.
- **S6:** Khi "migration kẹt giữa": đừng cố đẩy bậc tiếp — quay về bước trước (flag về 0, đọc đường cũ) rồi chẩn đoán; kẹt giữa mà đẩy tiếp là chuyển sự cố từ server sang khách hàng.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| DB lag/timeout trong migration | Backfill không throttle | batch + đo lag | §2.2 |
| Đọc thấy dữ liệu "nửa nạc nửa mỡ" | Đọc hai nguồn trong 1 request | mỗi request một nguồn | §2.2 |
| Hệ mới khác kết quả hệ cũ | Logic lệch (bug di dời) | parallel-run diff | §2.4 |
| Cột/bảng chết chất đống | Quên contract | audit schema định kỳ | §2.2 |
| Code rối như tổ quạ vì flag chồng chất | Flag không dọn | TTL + chủ + sweep | §2.5 |
| Không dám xoá API cũ | Không biết còn ai dùng | usage-by-version (→4.8) | §2.6 |

---

## 6. Cách đo

```sql
-- Tuổi flag & nợ flag: liệt kê từ config + repo:
--   tên flag | ngày tạo | chủ | % user đang bật | ngày xóa dự kiến
--   — flag > 30 ngày tuổi và không có chủ: xóa (hoặc tìm chủ) tuần này

-- Dữ liệu "chết": cột không được đọc (audit truy vấn — pg_stat_statements tìm
--   cột không xuất hiện trong SELECT/UPDATE còn sống)
```

Nguyên tắc: **đếm "bước không quay đầu"** trong kế hoạch migration — mỗi bước như vậy cần người ký duyệt bằng tên (rủi ro hiện rõ mới được quản).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay expand-contract:** cửa sổ bảo trì 30 phút (rẻ, thô — hợp lệ khi ít user khuya và bảng nhỏ); **thay strangler:** big-bang khi hệ thống nhỏ + có thể rollback artifact (deploy cũ) — nhanh xong, rủi ro cô đặc; **thay flag tự dựng:** dịch vụ flag managed (LaunchDarkly/tự host OpenFeature) — mua ngay những gì §2.5 đòi hỏi.

Năm thấu kính:
- **Kinh tế:** Migration online đắt (làm đôi) nhưng không dừng doanh thu; big-bang rẻ khi thành công và rất đắt khi thất bại — kỳ vọng chi phí = xác suất × thiệt hại, đừng chỉ nhìn nhánh tốt.
- **Vận hành:** Mỗi migration có runbook 1 trang: đang ở bước nào, lệnh quay đầu, ai giữ chìa — có giấy này thì 2h sáng vẫn chạy được.
- **An ninh:** Đường dữ liệu song song = thêm đường rò (hệ cũ thiếu patch, thiếu RLS — →5.14); hệ cũ "sắp chết" 2 năm vẫn cần đối xử như production đến ngày tắt thật.
- **Lịch sử:** "Backup trước khi sửa" thập niên 70 → version control/branch (1990s–2000s) → blue-green & canary (2010s) → flag/progressive (hiện tại): cùng một tâm lý học — **con người cần lối thoát mới dám tiến**; công cụ chỉ chuyên biệt hoá lối thoát theo chất liệu.
- **Người dùng:** Người dùng không biết migration đang chạy — và đó là mục tiêu: "hôm qua và hôm nay hệ giống nhau, chỉ tốt hơn". Chương này tồn tại để giữ lời hứa im lặng đó trong lúc thay động cơ giữa chuyến bay.

---

## 8. Đọc tiếp & bài tập

- Backfill/CDC: **5.15** · API versioning: **4.8** · Canary platform: **9.7** · Flag trong observability: **11.1** · Cell canary: **8.7**
- **Bài tập 1:** Với migration gần nhất của bạn: vẽ các bước và đánh dấu bước "không quay đầu". Không có bước nào? Bạn may mắn (hoặc chưa nhìn kỹ). Có? Lần sau thêm expand-contract quanh nó.
- **Bài tập 2:** Liệt kê mọi flag đang sống (lệnh §6): tuổi, chủ, % bật. Đặt deadline dọn 5 flag già nhất — mỗi flag dọn là một nhánh test được xoá (những gì không đo được thì không dám refactor).
- **Bài tập 3:** Chọn một endpoint quan trọng: chạy shadow so sánh giữa hai cách tính (cũ và cách định refactor) trong 1 giờ — liệt kê sai khác. Không khác? Refactor an toàn. Khác? Bạn vừa tránh một sự cố trong production.
