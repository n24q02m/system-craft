# 11.7 — Vành Liên ngành: PM, Pháp lý, Tài chính, Mua sắm

> **Tầng:** Vận hành · **Quyển II** · **Trục đọc:** tổ chức · **Động từ liên quan:** Hợp tác · Quyết
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 10.8 (tuân thủ) · 11.1 (SLO — ngôn ngữ số).

**Sợi chỉ đỏ:** *Kỳ họp với kế toán và pháp lý — nói ngôn ngữ gì cho hai bên cùng thấy rủi ro?* — trả lời: nói ngôn ngữ gì cho kế toán và pháp lý cùng thấy rủi ro — build/buy/rent là ma trận quyết định; mời pháp lý sớm vì sửa hợp đồng trước khi code rẻ hơn nhiều; dịch capex/opex/unit cho tài chính; hợp đồng vendor là một loại kiến trúc; chương kết bằng bảng dịch thuật ba ngôn ngữ. Câu hỏi để lại cho chương sau: *Đi từ đây tới đâu — lộ trình lab và thói quen verify cho người vận hành?*

**Thuật ngữ sẽ gặp:** *build vs buy vs rent* — tự viết, mua, thuê SaaS: ma trận theo lợi thế cạnh tranh; *mời sớm* — pháp lý vào từ khâu thiết kế: giờ tư vấn rẻ hơn nhiều so tu sửa khi đã chạy; *capex/opex* — mua tài sản hay thuê chi phí: tài chính nhìn hai thứ khác hẳn; *unit cost* — ngôn ngữ chung tài chính và kỹ thuật: đồng mỗi đơn (nối 11.5); *hợp đồng là kiến trúc* — SLA vendor, di dỡ dữ liệu, exit clause: ràng buộc thiết kế như dependency;

**Ví dụ mở đầu:** Cuộc họp của DM với tài chính: kỹ thuật nói "multi-region DR", kế toán nghe "chi phí gấp đôi" — không ai sai, chỉ khác ngôn ngữ. Đặt unit cost làm phiên dịch — "mỗi chữ 9 thêm bao nhiêu đồng mỗi đơn" — quyết định rơi trong mười phút thay vì ba cuộc họp.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Làm–mua–thuê (build/buy/rent) theo ma trận nào | Cái gì là "cốt lõi tôi giỏi nhất thế giới" — còn lại mua? |
| 2 | Hợp tác PM-kỹ thuật: ai dịch yêu cầu thành SLI/journey | Tính năng mới — ai hỏi "đo thành công bằng gì" trước khi code? |
| 3 | Mua sắm/nhà cung cấp: ràng buộc thoát (exit) đặt ở đâu | Vendor này chết/tăng giá ×3 — tôi thoát trong bao lâu? |
| 4 | Bảng dịch thuật nghề: kỹ thuật ↔ tài chính ↔ pháp lý | CFO hỏi "capex hay opex?" — tôi trả lời bằng ngôn ngữ nào? |

---

## 2. Cơ chế

### 2.1 Build vs buy vs rent — ma trận quyết định

Hai trục: **lợi thế cạnh tranh** (cái này giúp tôi thắng không?) × **độ đặc thù** (thị trường có sẵn giải pháp không?).

| | Lợi thế cạnh tranh | Không phải lợi thế |
|---|---|---|
| **Đặc thù** (ít giải pháp sẵn) | **BUILD** (core IP) | BUILD-nhẹ hoặc chịu thủ công (ít khi nhiều) |
| **Phổ biến** (giải pháp đầy rẫy) | Tùy: buy + tuỳ biến | **BUY/RENT** (đừng viết lại auth, email, CRM) |

Câu hỏi vũ trụ: "5 năm nữa tôi có thắng vì mình tự viết cái này không?" — không thì tự viết là chuyển ngân sách khỏi thứ giúp thắng. Kèm 3 chi phí ẩn của buy: **thoát** (data export? format chuẩn?), **tích hợp** (API/SSO/SCIM — →10.3: vendor không có SCIM là nợ vận hành mỗi lần vào/ra nhân viên), **lock-in giá** (giá năm 3 không phải giá năm 1 — mặc cả bằng sẵn sàng rời đi).

### 2.2 PM & kỹ thuật — hợp tác ở đúng tầng

Sự cố giao tiếp kinh điển: PM mang "giải pháp" (làm nút X màu đỏ) thay vì "vấn đề" (khách bỏ ở bước Y). Chữa bằng hợp đồng làm việc: yêu cầu mang **mục tiêu + chỉ số** (SLI/journey — →11.1: "tăng tỉ lệ hoàn tất thanh toán"), kỹ thuật mang **phương án + đánh đổi** (ADR-lite — →11.6). Kỹ thuật có quyền nói "cách này rẻ hơn mà đạt cùng chỉ số"; PM có quyền nói "chỉ số đó không phải cái khách cần" — cả hai đúng theo nghề của mình. Ritual tối thiểu: mỗi quý xem SLO/error budget (→11.1) cùng nhau — ngôn ngữ chung là con số người dùng.

### 2.3 Pháp lý & tuân thủ — mời sớm, trả rẻ

Mời pháp lý vào **lúc thiết kế** (data flow, region, retention — →10.8) thì trả giá "review 1 buổi"; mời lúc phát hành thì trả "redesign 1 quý". Ba câu kỹ thuật phải tự trả được trước khi gặp luật: dữ liệu cá nhân gì/ở đâu/bao lâu (danh mục — →10.8 §2.3); nhà cung cấp nào xử lý thay (sub-processor); luồng xuyên biên giới nào. Mang sẵn ba câu trả lời, buổi gặp luật là **xác nhận** chứ không phải khám bệnh.

### 2.4 Tài chính — dịch capex/opex/unit

- **CAPEX** (mua trước, khấu hao): on-prem, license vĩnh viễn — đẹp báo cáo quý, cứng nhắc chiến lược;
- **OPEX** (trả theo dùng): cloud, SaaS — linh hoạt, đắt nếu không quản (→11.5);
- **Unit** (chi phí/đơn vị giá trị): cầu nối hai bên — CFO hiểu "giá/1 đơn vị" hơn "20 node Kubernetes".
Vai trò kỹ thuật trong cuộc họp tài chính: mang **unit cost + trend + kịch bản** (nếu khách ×2 thì chi phí thế nào — 11.3 Little + 11.5) — đó là đóng góp không thay thế được bởi bất kỳ phòng ban nào.

### 2.5 Mua sắm & quản lý vendor — hợp đồng là kiến trúc

Điều khoản kỹ thuật phải đòi (và luật soạn sẵn nếu kỹ thuật cung cấp ngôn ngữ): **SLA có teeth** (bồi thường = crédit thực sự đáng kể), **data portability** (export đầy đủ, format mở, thoát trong N ngày), **bảo mật** (SOC2/ISO-style audit, báo cáo sự cố trong X giờ — khớp 10.7/10.8 nghĩa vụ của **bạn** — chuỗi nhà cung cấp là trách nhiệm pháp lý của bạn với khách, không phải của họ), **roadmap cam kết** (tính năng bạn phụ thuộc). Vendor management thật: **danh sách vendor theo tầm quan trọng** (chết thì tôi thế nào — như 8.7 cho hạ tầng, áp cho hợp đồng) + review nửa năm + **kịch bản thoát rehearsed** cho 1–2 vendor quan trọng nhất (export thử — tin rằng exit được ≠ thoát được).

### 2.6 Bảng dịch thuật — giảm ma sát của ba ngôn ngữ

| Kỹ thuật nói | PM nghe | Tài chính nghe | Pháp lý nghe |
|---|---|---|---|
| p99 500 ms | "1 trong 100 người chờ > 0,5 s" | "đổi lấy 2 máy = X/tháng" | (không cần) |
| Error budget 30% còn | "còn quyền ship 1 lần lớn" | "rủi ro sự cố còn Y phút" | "đã có quy trình lỗi" |
| Data retention 30 ngày | "khách xoá dữ liệu sau 1 tháng" | "tiết kiệm lưu trữ Z" | "khớp NĐ 13/GDPR (→10.8)" |
| Multi-region | "khách Nhật nhanh hơn" | "+40% hóa đơn" | "dữ liệu nằm region nào" |

Bảng dạng này treo trong phòng họp — mỗi bên luyện nói **một câu** theo ngôn ngữ bên kia mỗi cuộc họp là văn hoá liên ngành bắt đầu.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| Ma trận build/buy | 2×2 lợi thế × đặc thù | P | |
| Exit drill | 1–2 vendor quan trọng/năm | P | |
| Review vendor | nửa năm | P | |
| Pháp lý vào sớm | giai đoạn thiết kế | P | rẻ hơn redesign một bậc |

---

## 4. Suy luận kiến trúc

- **S1:** Mọi quyết định kỹ thuật lớn là **quyết định kinh doanh mạo danh** (multi-region, tự dựng vs mua, retention) — chương này dạy kỹ thuật tham gia cuộc họp đó bằng **bảng giá + rủi ro định lượng**, không bằng "technical reasons";
- **S2:** Tham số trụ: % vendor quan trọng có exit plan được rehearsed, thời gian từ yêu cầu → thoả thuận mua (dẫn vòng mua), số lần "redesign vì pháp lý vào muộn"/năm (nên → 0).
- **S3:** Hợp đồng là **kiến trúc không thể refactor nhẹ** (đổi điều khoản khó hơn đổi code) — đầu tư đọc/viết điều khoản kỹ thuật ngang đầu tư review thiết kế;
- **S4:** Bảng dịch thuật là **API giữa các nghề** — cùng triết lý hợp đồng (→4.x): interface rõ, ngữ nghĩa thống nhất; "misunderstanding" giữa phòng ban là bug của interface này.
- **S5:** Mua AI (model/dịch vụ) là mặt trận mua sắm mới 2026: giá đổi theo phiên bản nhanh (→12.x), benchmark khó so (→12.4) — kỹ thuật cần mang **đơn vị giá trị (triệu token/task)** vào đàm phán như §2.4;
- **S6:** Khi dự án "kẹt vì các bên không hiểu nhau": vẽ lại theo bảng §2.6 — gần như luôn phát hiện một từ đang mang hai nghĩa (uổng: "sẵn sàng" với PM = tính năng đủ, với kỹ thuật = SLO đạt).

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Tự viết CRM/auth/email | Ma trận build/buy sai | 2×2 + câu 5 năm | §2.1 |
| Pháp lý đỏ toàn bộ thiết kế | Mời muộn | mời ở giai đoạn thiết kế | §2.3 |
| Vendor tăng giá ×3, không thoát được | Exit không rehearsed | exit drill + điều khoản | §2.5 |
| PM mang giải pháp không vấn đề | Hợp đồng làm việc thiếu | yêu cầu = mục tiêu + chỉ số | §2.2 |
| CFO phê chậm mọi đề xuất | Thiếu unit + kịch bản | unit cost + scenario | §2.4 |
| Ba phòng ba con số khác nhau | Không bảng dịch thuật | bảng §2.6 + thuật ngữ chung | §2.6 |

---

## 6. Cách đo

```bash
# "Exit drill" cho vendor quan trọng nhất (nửa ngày):
#   1. Export dữ liệu thật (đúng hướng dẫn docs của vendor)
#   2. Đếm % dữ liệu lấy được + format (mở/chủ quyền?)
#   3. Liệt kê tích hợp phải chuyển (SSO/SCIM/webhook — →10.3/4.6)
#   4. Ước tính thời gian + chi phí chuyển toàn bộ
#   → kết quả là "điểm thoát được" của vendor — mang vào vòng mua sắm tới

# Bảng dịch thuật: mỗi cuộc họp liên ngành ghi 1 thuật ngữ gây hiểu lầm —
#   tổng hợp quý: từ nào đắt nhất (theo giờ họp + quyết sai)
```

Nguyên tắc: **sức khỏe liên ngành đo bằng thời gian ra quyết định đúng** (yêu cầu → phê duyệt → ship) — không bằng cảm giác "hợp tác tốt".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay ma trận build/buy:** "làm hết" (thói quen của đội mạnh kỹ thuật — đắt dần theo năm) hoặc "mua hết" (thói quen của tổ chức sợ rủi ro — mất lợi thế cạnh tranh + phụ thuộc); **thay exit drill:** tin lời cam kết sales (rẻ — tới ngày cần thì biết); **thay bảng dịch thuật:** hiring "bridge people" (PM hiểu kỹ thuật — tốt nhưng hiếm và không scale).

Năm thấu kính:
- **Kinh tế:** Lỗi build/buy là **lỗi đầu tư lớn nhất** của phòng kỹ thuật (năm người-năm vào thứ không phải lợi thế = cơ hội mất của thứ có thể là lợi thế); ma trận 2×2 là due diligence rẻ nhất;
- **Vận hành:** Mỗi vendor = một dependency vận hành (on-call gián tiếp, upgrade theo lịch người ta, sự cố của họ là sự cố của bạn — →8.7 bảng thảm hoạ mở rộng cho vendor);
- **An ninh:** Chuỗi cung ứng pháp lý = chuỗi cung ứng an ninh (→10.5/10.8): NIS2/DORA đặt trách nhiệm **người mua** về nhà cung cấp — vendor management là compliance, không phải thủ tục;
- **Lịch sử:** IT là "phòng giá rẻ" (1990s) → đối tác chiến lược (2000s) → "công ty công nghệ" mọi ngân hàng tự xưng (2010s) → kỹ thuật là **người giữ unit economics** (2020s): mỗi thập kỷ kéo kỹ thuật vào phòng họp kinh doanh sâu hơn một tầng;
- **Người dùng:** Người dùng cuối không thấy ranh giới phòng ban — họ chỉ thấy "sản phẩm chậm ra và vụng về" khi các nghề không hạ cánh được cùng một con số; chương này là lớp keo của toàn bộ trải nghiệm đó.

---

## 8. Đọc tiếp & bài tập

- ADR: **11.6** · SLO chung với PM: **11.1** · Vendor trong bảng thảm hoạ: **8.7** · Pháp lý dữ liệu: **10.8** · Unit economics: **11.5** · Lộ trình học liên nghề: **11.8**
- **Bài tập 1:** Áp ma trận 2×2 cho 3 hệ thống bạn tự viết đang duy trì. Cái nào rơi vào ô "buy/rent" — viết bản đề xuất thay thế (kèm chi phí 3 năm so sánh — 11.5 giúp);
- **Bài tập 2:** Chọn vendor quan trọng nhất, chạy exit drill nửa ngày (§6). Điểm thoát < 70% dữ liệu hoặc > 1 quý chuyển? Đó là rủi ro đích danh cần lên agenda với lãnh đạo;
- **Bài tập 3:** Trong họp liên ngành tới, thử nói một nhận định kỹ thuật bằng ngôn ngữ của bên kế toán (đơn vị tiền + rủi ro). Ghi lại phản ứng — nếu phòng kia ngạc nhiên thì bạn vừa mở một kênh mới tổ chức chưa từng có.

