# 6.2 — Bốn Môi trường Thực thi Client

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** nền client · **Động từ liên quan:** Chọn · Đo
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 3.9 (ma trận runtime) · 4.3 (hợp đồng API).

**Sợi chỉ đỏ:** *Điện thoại, máy tính, kiosk quán, TV — bốn môi trường, logic chia theo đường nào?* — trả lời: bốn môi trường — điện thoại, máy tính, kiosk quán, TV — mỗi cái một bộ ràng buộc trị vì như một "hệ điều hành" riêng; logic chia theo kiến trúc lớp: lõi dùng chung, vỏ theo nền tảng; cross-platform có bốn trường phái kèm chi phí giấu trong mỗi lựa chọn. Câu hỏi để lại cho chương sau: *Đang đặt món thì mạng đứt — local-first giữ được gì, gỡ rối ra sao?*

**Thuật ngữ sẽ gặp:** *kiến trúc chia lớp* — lõi nghiệp vụ dùng chung, giao diện theo nền: đường phân chuẩn; *bốn trường phái cross-platform* — native từng nền, web, compile-to-native, tự vác runtime: chương có bảng sự thật; *chi phí giấu* — kích thước cài đặt, thời gian build, tính năng hụt: thứ không ghi trên landing page; *kiosk mode* — môi trường khoá một mục đích: ràng buộc nhẹ hơn nhưng trách nhiệm nặng hơn; *adaptive UI* — một logic, nhiều hình theo màn hình và cách tương tác; *trạng thái 2026* — bảng chọn đã verify để khỏi re-lai từ đầu.

**Ví dụ mở đầu:** DM cần app khách trên điện thoại, console quản trị trên máy tính, kiosk đặt món tại quán, màn bếp chỉ hiện đơn: một logic đơn hàng — bốn bộ ràng buộc trị vì. Copy bốn bản là mở bốn nhánh phân tán không bao giờ hoà. Chương này chỉ đường chia lớp: viết một lần chỗ nên viết một lần, tách đúng chỗ bắt buộc phải tách.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Nền tảng mục tiêu: web / iOS / Android / desktop / embedded | Người dùng tôi ở đâu thật — theo số, không theo thói quen? |
| 2 | Native hay cross-platform (React Native/Flutter/KMP/PWA) | Tôi đổi hiệu năng/UX lấy tốc độ xuất hàng thế nào? |
| 3 | Tầng dùng lại bao nhiêu (logic/UI) giữa các nền tảng | Core shared là gì — và biên giới vẽ ở đâu? |
| 4 | Version floor & chu kỳ nâng cấp toolchain | Xcode/Gradle/browser floor — ai theo dõi và nâng? |

---

## 2. Cơ chế

### 2.1 Bốn môi trường — bốn "hệ điều hành của ràng buộc"

| | **Web** | **iOS** | **Android** | **Desktop** |
|---|---|---|---|---|
| Runtime | engine trình duyệt | Swift/Obj-C (UIKit/SwiftUI) | Kotlin/Java (Compose) | Electron/Tauri/native |
| Phân phối | reload tức thì | App Store review (ngày) | Play Store (giờ–ngày) | auto-update riêng |
| Nâng cấp runtime | theo user (chrome nhanh; safari chậm) | theo OS (chậm) | WebView/Play Services rải | theo app |
| Giới hạn đặc trưng | sandbox tab, offline giới hạn | review policy, background hạn chế | fragmentation device, doze | quyền máy, khởi động |
| Sức mạnh ngôn ngữ | JS/Wasm (→3.8) | native full | native full + NDK | full |

Embedded/IoT là môi trường thứ năm — khác căn bản (RTOS, firmware) — chương 6.6 riêng.

### 2.2 Cross-platform: bốn trường phái, một bảng sự thật

| Trường phái | Đại diện | Dùng lại | Cái giá |
|---|---|---|---|
| **Web-wrap** | PWA/Capacitor | 1 codebase, cập nhật tức thời | hiệu năng/UX "gần native" thôi; quyền thiết bị giới hạn |
| **JS-bridge** | React Native | JS logic + native render | bridge churn; hiệu năng trung bình; đội vẫn cần native để vá |
| **Self-render** | Flutter | UI + logic (Dart) | vẽ lại mọi thứ — không theo platform look; binary to; Dart là "đảo ngôn ngữ" (→3.9) |
| **Shared-logic** | Kotlin Multiplatform / .NET MAUI | logic/domain, UI native từng nền | UI viết 2 lần — đổi công lớn cho UX "đúng chuẩn" |

Quy tắc chọn: **team ≤ 5 người, app CRUD/media → 1 codebase (RN/Flutter); team có native dev + app "sản phẩm cảm giác" (camera, animation mượt) → native hoặc KMP; nội bộ tool → PWA/desktop nhẹ.** Không có lựa chọn đúng cho mọi tổ chức — có lựa chọn đúng cho đội hình hiện có (đây là quyết định nhân sự đội lốt kỹ thuật).

### 2.3 Chi phí "giấu" của mỗi nền tảng

- **iOS:** thời gian review (expedited review có nhưng không thường xuyên được); device test giới hạn; SwiftUI bugs theo OS version;
- **Android:** fragmentation (screen/OS/API level) — phải test ma trận; Play policy + targetSdk deadline hằng năm (bắt buộc nâng);
- **Web:** engine không đồng nhất (Safari là IE của thời đại — latency API khác, bug riêng); third-party cookie/permission tightening;
- **Desktop (Electron):** mỗi app = một bản Chromium (~150–200 MB RAM baseline (I)) — Tauri (system webview, binary nhỏ ~10×) là câu trả lời mỏng hơn.

### 2.4 Kiến trúc chia lớp phổ quát

```
[UI layer]      — nền tảng riêng (SwiftUI/Compose/React/…)  ┐
[Domain layer]  — pure logic (KMP/Rust/TS) — test được    ├ dùng lại tối đa
[Sync/API layer]— protobuf/OpenAPI sinh client (→4.3/4.4)  ┘
[Platform glue] — keychain, notification, file — adapter từng nền
```

Domain + hợp đồng API là phần đáng dùng lại; UI là phần đáng viết riêng nếu sản phẩm cạnh tranh bằng cảm giác. Logic dùng lại qua **Rust core** (đóng gói cho iOS/Android/desktop qua FFI/Wasm) đang lên — đúng mô hình "một lõi, nhiều mặt" (→3.5/3.8).

### 2.5 Trạng thái 2026 để ghi nhớ

- **PWA:** đủ tốt cho rất nhiều app nội bộ; push trên iOS (16.4+) đã bớt khoảng cách; vẫn thua native ở background;
- **React Native:** New Architecture (Fabric/TurboModules) đã mặc định — hiệu năng bridge cũ đã được sửa căn bản; 
- **Flutter:** ổn định, phổ biến ở startup/ĐNÁ; rendering riêng = chi phí "không giống hệ điều hành";
- **KMP:** JetBrains đưa stable (2023–2024); dùng nhiều ở app lớn muốn chia logic;
- **Compose Multiplatform / Expo EAS** — tooling trưởng thành tiếp.

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| App Store review | giờ–ngày | I | expedited hiếm |
| Play targetSdk deadline | hằng năm | V | buộc nâng |
| Electron RAM baseline | ~150–200 MB | I | mỗi app một Chromium |
| Tauri binary vs Electron | ~10× nhỏ hơn | I | system webview |
| Đoạn máy Android cần test | ~5–10 máy đại diện | P | theo thị trường mục tiêu |

---

## 4. Suy luận kiến trúc

- **S1:** Chọn nền tảng = chọn **ràng buộc phân phối** (review, fragmentation, upgrade floor) — phần code chỉ là phần nổi;
- **S2:** Tham số trụ: crash-free & vitals theo nền tảng, thời gian release (commit→store), ma trận device test pass.
- **S3:** Cross-platform đổi tốc độ ra mắt lấy chiều sâu native; chia lớp (§2.4) đổi kỷ luật kiến trúc lấy khả năng đổi hướng sau này.
- **S4:** Toolchain client đổi nhanh (browser API, store policy, OS version mỗi năm) — "chi phí bảo trì nền tảng" là khoản ngân sách thật, không phải bất ngờ.
- **S5:** AI assistant lập trình làm chi phí viết UI 2 lần (KMP-style) giảm — cân bằng cross/native đang lệch lại về phía "UI native từng nền".
- **S6:** Khi app "khó nâng cấp/chờ review": vấn đề là §2.3 (phân phối), không phải code — thay kiến trúc phát hành (staged rollout, config server-driven) trước.

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Bug chỉ trên Safari | Engine khác nhau | test matrix web | §2.3 |
| Từ chối App Store luân phiên | Policy vi phạm (background, IAP) | rejection log; policy checklist | §2.3 |
| App nặng RAM desktop | Electron × nhiều app | đổi Tauri/system webview | §2.3 |
| Play bắt nâng cấp hằng năm | targetSdk deadline | lịch nâng cấp | §2.3 |
| Cross-platform "kẹt" hiệu năng | Vượt giới hạn bridge/render | profile native layer | §2.2 |

---

## 6. Cách đo

```bash
# Ma trận sự thật: crash-free + vitals theo (platform × app-version × device-tier)
#   — từ Crashlytics/Sentry dashboard; dưới 99,5% crash-free session là đỏ

# Thời gian phát hành: commit → production (web so app) — đo theo tuần
#   — khác biệt này là chi phí phân phối, không phải tốc độ code

# Kích thước & hiệu năng bundle/binary theo từng bản release (budget — →7.3)
```

Nguyên tắc: **so sánh nền tảng bằng số của chính nó** (crash-free Android vs Android tuần trước) — so chéo iOS/Android dễ dẫn kết luận sai vì device base khác nhau.

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay viết app mobile:** PWA (nếu quyền thiết bị không cần sâu); responsive web + push (iOS 16.4+); SMS/USSD cho thị trường feature-phone (vẫn thật ở một số thị trường). **Thay cross-platform:** thuê đội native + dùng lại domain qua KMP/Rust — tăng chi phí nhân sự, giảm rủi ro UX.

Năm thấu kính:
- **Kinh tế:** Một codebase cho 3 nền tảng tiết kiệm 30–50% chi phí phát triển ban đầu (I) nhưng cộng dồn "thuế bridge" mỗi lần cần sâu — bài toán NPV, không phải khẩu hiệu.
- **Vận hành:** Mỗi nền tảng một runbook phát hành (review, signing, rollback) — rollback app store không tồn tại (chỉ stop-rollout + nâng cấp nhanh) — thiết kế theo hướng đó.
- **An ninh:** Cửa hàng app (store) là lớp soát thủ công có thật; web không có — policy an ninh web phải tự lo toàn bộ (→7.7).
- **Lịch sử:** PhoneGap (2011) → RN (2015) → Flutter (2018) → KMP stable (2023): mỗi thế hệ cross-platform dịch cái "dùng lại" từ UI xuống logic — hội tụ về kiến trúc chia lớp §2.4.
- **Người dùng:** Người dùng không biết app viết bằng gì — họ biết "cảm giác app này là app thật" hay "web đội lốt". Chọn công nghệ theo ngưỡng cảm giác đó của thị trường mục tiêu.

---

## 8. Đọc tiếp & bài tập

- Ràng buộc nền: **6.1** · Chia sẻ logic bằng Rust/Wasm: **3.5, 3.8** · Web sâu: **7.x** · IoT riêng: **6.6**
- **Bài tập 1:** Với sản phẩm của bạn: liệt kê % người dùng theo nền tảng (số thật). Nếu 90% là một nền tảng — cross-platform đang trả phí cho 10%.
- **Bài tập 2:** Đo thời gian commit→người dùng (mọi nền tảng). Con số này quyết định chiến lược phát hành (canary? staged?) nhiều hơn mọi quyết định kiến trúc khác của chương này.
- **Bài tập 3:** Viết 1 tính toán domain (ví dụ tính phí) ở tầng shared (KMP/TS module), test nó chạy đồng nhất trên 2 nền tảng — bài kiểm chứng biên chia lớp §2.4 của chính bạn.
