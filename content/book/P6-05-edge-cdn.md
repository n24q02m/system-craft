# 6.5 — Edge Compute & Kiến trúc CDN

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** nền client · **Động từ liên quan:** Chọn · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 5.4 (cache phía server) · 4.2 (HTTP header là hợp đồng).

**Sợi chỉ đỏ:** *Ảnh menu nặng, khách ở xa — edge/CDN caching là hợp đồng gì với origin?* — trả lời: CDN là hợp đồng với origin viết bằng HTTP header — Cache-Control là dòng quan trọng nhất của cả web; bốn tầng lưu (browser, edge, shield, origin), hai trường phái vô hiệu hoá (purge hay TTL), chỗ đáng chạy code ở edge — và cache stampede cũng đổ bộ tới đây. Câu hỏi để lại cho chương sau: *Máy in bill, cảm biến tủ lạnh, kiosk — fleet thiết bị của quán vận hành thế nào?*

**Thuật ngữ sẽ gặp:** *Cache-Control* — max-age, s-maxage, stale-while-revalidate: hợp đồng origin cam kết với từng tầng; *bốn tầng lưu* — browser → edge CDN → origin shield → origin: mỗi tầng một vai: lỗi thường nằm ở tầng bị quên; *purge vs TTL* — chủ động xoá (nhanh, dễ quên chỗ) hay đợi hết hạn (an toàn, chậm): hai trường phái; *stale-while-revalidate* — trả bản cũ trong lúc lấy bản mới: khách không phải chờ; *edge compute* — chạy code tại điểm gần khách: cá nhân hoá nhẹ, WAF — không phải nghiệp vụ nặng; *multi-CDN + DNS* — nhiều nhà cung cấp sau một tên miền: DNS là công tắc chuyển.

**Ví dụ mở đầu:** Ảnh món ăn DM nặng và khách ở xa: origin một chỗ thì nửa bản đồ chờ. CDN chép ảnh ra điểm gần — nhưng Cache-Control quyết định khách thấy menu mới bao lâu sau khi quán đổi: đặt sai một max-age, khách đặt món đã hết. Chương này đọc kỹ từng dòng hợp đồng đó.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Cái gì cache ở đâu: browser / CDN / edge / origin | Nội dung của tôi thay đổi bao lâu một lần — thật sự? |
| 2 | Chiến lược vô hiệu hoá: TTL / surrogate key / purge API | Tôi có dám xóa cache toàn cục trong 1 phút không? |
| 3 | Edge compute: dùng cho việc gì (định tuyến, auth, biến đổi) — và KHÔNG dùng cho việc gì | Logic nào cần dữ liệu gốc ở cùng nơi với DB? |
| 4 | Ai là origin thật khi có nhiều tầng CDN | Lỗi "cache độc" — truy từ đâu để thấy sự thật? |

---

## 2. Cơ chế

### 2.1 Mô hình bốn tầng lưu

```
[browser cache] — private, theo user, TTL ngắn
      ↓ miss
[CDN PoP] — public, theo URL, số lượng lớn, gần người dùng (RTT ~ms)
      ↓ miss
[edge compute] — biến đổi/định tuyến tại PoP (worker)
      ↓
[origin] — nguồn sự thật (app + DB)
```

Mỗi tầng cache đều có hai câu hỏi: **khoá gì** (URL? header? cookie?) và **hết hạn khi nào** (TTL? purge? stale-while-revalidate?). 90% sự cố cache = trả lời sai một trong hai.

### 2.2 Cache-Control — hợp đồng quan trọng nhất của web

```
Cache-Control: public, max-age=300, stale-while-revalidate=60, s-maxage=3600
```

- `max-age` (browser) vs `s-maxage` (CDN/shared): tách riêng — thường CDN giữ lâu hơn browser;
- `private`: KHÔNG cho shared cache — dữ liệu theo user bắt buộc có;
- `stale-while-revalidate`: người dùng nhận bản cũ, CDN refresh nền — trải nghiệm "luôn nhanh, đôi khi cũ 1 chu kỳ";
- `Vary`: khoá cache theo header (Accept-Encoding, Accept-Language) — thiếu Vary = trả nhầm nội dung giữa user; thừa Vary (cookie) = cache hit rate sụp;
- **Surrogate key / cache-tag:** gắn nhiều khoá vào một response → xóa theo nhóm ("toàn bộ trang sản phẩm X") — Cloudflare cache-tag, Fastly surrogate-key; đây là vũ khí vô hiệu hoá chọn lọc.

### 2.3 Vô hiệu hoá: hai trường phái

| Trường phái | Cách | Rủi ro |
|---|---|---|
| **TTL ngắn** | để tự hết hạn (30–300 s) | dữ liệu cũ trong cửa sổ TTL; origin chịu miss định kỳ |
| **Purge theo key** | xóa chủ động khi dữ liệu đổi | quên purge = cũ vô hạn; purge văng chùm = stampede origin |

Thực chiến: **TTL dài cho immutable (asset hash — →7.3) + purge-theo-key cho nội dung động** + stale-while-revalidate làm lớp lót. Quy tắc Phil Karlton vận dụng: "Có hai vấn đề khó trong CS: vô hiệu hoá cache, đặt tên, và off-by-one."

### 2.4 Edge compute — cái gì đáng xuống edge

Đáng: định tuyến theo geo/header, A/B, auth token verify (JWT verify + JWKS cache — không cần DB), biến đổi response (resize ảnh, personalise nhẹ), rate limit thô, bot filter. **Không đáng:** nghiệp vụ cần đọc/ghi DB nhiều — mỗi lần gọi DB từ edge là đi vòng Trái Đất tới region DB (mọi lợi ích RTT mất sạch). Edge có storage riêng (KV, Durable Objects — nhất quán yếu từng khoá) — đọc kỹ ngữ nghĩa nhất quán (→8.1) trước khi coi nó là "DB".

### 2.5 Đo & chống cache stampede

- **Hit ratio** theo tầng (CDN dashboard): 90%+ khả thi cho asset tĩnh; 50–70% cho nội dung động có cache;
- **Origin offload:** request/s chạm origin trước–sau;
- **Stampede:** một key hot hết hạn → hàng nghìn request dồn origin. Chống: stale-while-revalidate, soft TTL (serve stale + refresh một mình), lock/request-coalescing ở origin (→5.4 pattern).

### 2.6 Multi-CDN & DNS

Hệ thống lớn dùng nhiều CDN (theo khu vực giá/thiên tai): DNS/GeoDNS hoặc CNAME chain chuyển hướng — thêm một tầng state để vận hành; chỉ cần khi một CDN từng làm bạn sập thật (định luật Yagni — chỉ build khi có vết thương).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| RTT đến PoP CDN | ~1–30 ms (vs 100–300 ms origin xa) | I | |
| TTL asset hash | 1 năm, immutable | P | →7.3 |
| Hit ratio asset | > 90% | P | dưới = khoá/Vary sai |
| Purge lan truyền | s–phút (theo provider) | V | |
| Edge cold start (JS worker) | ~ms (V8 isolate) | I | khác container (→2.7) |

---

## 4. Suy luận kiến trúc

- **S1:** CDN là tầng phân tán **đọc** lớn nhất hệ thống của bạn — thiết kế cache-control cùng lúc thiết kế bảng schema, không phải việc "sau khi xong API".
- **S2:** Tham số trụ: hit ratio theo tầng, origin offload, p95 TTFB theo khu vực, tỉ lệ serve-stale.
- **S3:** Mỗi chiến lược hết hạn đổi "độ tươi tối đa" lấy áp lực origin — bảng giá §2.3; đặt TTL = độ tươi nghiệp vụ CHẤP NHẬN ĐƯỢC, không phải số đẹp.
- **S4:** Edge compute dùng V8 isolate (→3.9 cùng họ kỹ thuật với serverless) — hạn CPU/thời gian nhỏ, không socket tuỳ ý: đọc limits trước khi kiến trúc.
- **S5:** AI inference ở edge (model nhỏ, cache kết quả) đang là use case mới — nhưng kết quả AI cần cache theo input-hash + model-version, nếu không hit ratio ảo (→12.6).
- **S6:** Khi "nội dung không cập nhật": đừng đoán — truy vấn chain §2.1 từ ngoài vào (curl từng chặng với header no-cache) và xem miss nằm ở tầng nào; nhiều khi lỗi nằm ở origin trả nhầm cache-control.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| "Dữ liệu cũ" sau khi sửa | Thiếu purge / TTL dài | curl -sI từng chặng | §2.2 |
| User thấy nội dung của user khác | Thiếu private/Vary cookie | audit khoá cache | §2.2 |
| Origin bị dồn lúc hot key hết hạn | Stampede | stale-while-revalidate; lock | §2.5 |
| TTFB khu vực xa cao | Origin một region | CDN/edge cho route đó | §2.4 |
| Hit ratio thấp không rõ vì sao | Vary thừa / URL chứa query random | CDN log phân tích khoá | §2.2 |
| Deploy xong người dùng thấy cũ | Asset không hash / HTML cache | fingerprint bundle (→7.3) | §2.3 |

---

## 6. Cách đo

```bash
# Đi từng chặng — xem ai trả gì:
curl -sI https://app.example.com/page        # xem cache-control, age, x-cache
curl -sI -H 'Cache-Control: no-cache' ...    # xuyên qua browser/CDN
curl -sI https://origin.internal/page        # origin thật trả gì?

# Trên CDN: hit ratio theo khoá phổ biến nhất (top URL) —
#   20% URL đầu thường chiếm 80% miss; sửa 20% đó trước
```

Nguyên tắc: **mỗi response mang hộ chiếu** (age, x-cache, cache-control) — đọc hộ chiếu trước khi tranh luận; không có header debug thì thêm (đèn đường) (→11.1).

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay CDN:** origin đa region + GeoDNS (kiểm soát đầy đủ, vận hành nặng hơn — khi dữ liệu không cache được nhiều, CDN chỉ là lớp chuyển tiếp thêm giá); **thay edge compute:** đưa logic về origin đơn giản hơn — chỉ xuống edge khi RTT người dùng cảm nhận được hoặc chi phí origin rõ ràng.

Năm thấu kính:
- **Kinh tế:** CDN tính theo băng thông; origin + region tính theo compute — di chuyển tính toán sang CDN thường là di chuyển hóa đơn; đo giá/GB hai bên trước khi "tối ưu".
- **Vận hành:** Multi-CDN = hai bảng điều khiển, hai bộ hành vi purge khác nhau — chạy drill chuyển CDN định kỳ nếu đã đầu tư.
- **An ninh:** CDN cũng là tường chặn DDoS L7 (rate limit, WAF) — nhưng lỗi cấu hình cache response nhạy cảm là lỗ hổng kinh điển (→7.7); coi header an toàn là một phần schema.
- **Lịch sử:** Akamai (1998) → CloudFront → Cloudflare Workers (2017) — từ "copy file ra nhiều nơi" tới "chạy code nhiều nơi"; mỗi bước đều là lời tuyên bố "RTT là số một người dùng cảm nhận".
- **Người dùng:** Người dùng không biết CDN là gì — họ biết "trang này mở nhanh ở nhà mình". Chương này tồn tại vì Trái Đất tròn và ánh sáng chậm (→1.6): mọi phần còn lại là kế toán.

---

## 8. Đọc tiếp & bài tập

- Asset hash & deploy: **7.3** · HTTP semantics sâu: **4.2** · Nhất quán yếu ở KV edge: **8.1** · Rate limit: **11.3**
- **Bài tập 1:** `curl -sI` trang chủ bạn và 3 API công khai: ghi lại cache-control từng cái. Nếu không giải thích được từng trường — hợp đồng cache của bạn đang là ngầm định.
- **Bài tập 2:** Với một sự kiện đổi dữ liệu (sửa giá sản phẩm): vẽ đường purge — khoá nào phải xóa, ở tầng nào, mất bao lâu lan. Không vẽ được = người dùng sẽ vẽ bằng phàn nàn.
- **Bài tập 3:** Tính: nếu TTL giảm từ 10 phút xuống 1 phút, origin QPS thêm bao nhiêu? Con số đó nên nằm ngay trong ticket quyết định — không có nó, tranh luận TTL là khẩu hiệu.
