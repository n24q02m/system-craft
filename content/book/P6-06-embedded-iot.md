# 6.6 — Hệ thống Nhúng & IoT

> **Tầng:** Mép · **Quyển II** · **Trục đọc:** nền client · **Động từ liên quan:** Chọn · Vận hành
> **Bản:** SA-2026.13 · **Số liệu:** bậc độ lớn (xem §3, cách đọc số)
> **Nguồn migrate:** — (viết mới)

---

## 0. Nhập môn

**Đọc trước:** 6.1 (ràng buộc) · 5.7 (queue nhận dữ liệu).

**Sợi chỉ đỏ:** *Máy in bill, cảm biến tủ lạnh, kiosk — fleet thiết bị của quán vận hành thế nào?* — trả lời: fleet thiết bị quán — máy in bill, cảm biến tủ lạnh, kiosk — là "server không phòng máy": rải khắp thành phố, sống mười năm; giao thức chọn theo khoảng cách nhân pin nhân hệ sinh thái; mỗi máy cần danh tính, vòng đời và đường OTA an toàn. Câu hỏi để lại cho chương sau: *Mọi thứ chạy trên máy không tin được — bảo mật client là phòng tuyến nào?*

**Thuật ngữ sẽ gặp:** *hai thế giới nhúng* — thiết bị có Linux và vi điều khiển bare-metal: hai bài toán vận hành khác hẳn; *MQTT/CoAP* — giao thức nhắn tin nhẹ cho IoT: broker trung tâm, QoS chọn theo mức; *provisioning* — cấp danh tính và bí mật riêng cho từng máy từ xưởng: cấm password chung cả fleet; *OTA* — cập nhật qua sóng: nguyên vẹn, ký số, có rollback — hỏng là quán mất bill sáng sau; *fleet lifecycle* — ra đời, nâng cấp, thu hồi: thiết bị sống mười năm, không phải hai năm; *dữ liệu về backend* — telemetry chảy về queue và TSDB: nối 5.7 với 5.11.

**Ví dụ mở đầu:** Cảm biến nhiệt tủ lạnh báo mỗi 15 phút suốt mười năm: pin và băng thông là ngân sách tính bằng cent. Máy in bill tự cập nhật lúc nửa đêm khi quán đóng cửa. Chương này vận hành hạ tầng không ai đứng cạnh — mọi thao tác đều phải đi qua sóng.

## 1. Quyết định

| # | Quyết định | Câu hỏi tự vấn |
|---|---|---|
| 1 | Nền tảng nhúng: MCU (vi điều khiển) hay SBC/edge Linux | Độ trễ/điện/cần OS thật — cái nào ràng buộc? |
| 2 | Giao thức: MQTT / CoAP / HTTP / Matter / LoRaWAN | Khoảng cách, băng thông, pin, và hệ sinh thái ai dùng? |
| 3 | Fleet provisioning & danh tính thiết bị | Làm sao 10.000 thiết bị ra đời an toàn — và bị thu hồi an toàn? |
| 4 | OTA update: kênh nào, rollback thế nào | Bricking 10.000 máy là kịch bản được thiết kế chống lại chưa? |

---

## 2. Cơ chế

### 2.1 Hai thế giới nhúng

| | **MCU** (vi điều khiển) | **Edge Linux** (SBC/gateway) |
|---|---|---|
| Ví dụ | ESP32, STM32, nRF | Raspberry Pi, Jetson, gateway công nghiệp |
| RAM/Flash | KB–MB | MB–GB |
| OS | bare-metal/RTOS (FreeRTOS/Zephyr) | Linux đầy đủ |
| Mạng | wifi/BLE/LoRa/cellular NB-IoT | ethernet/wifi/cellular đủ |
| Điện | µA khi ngủ — chạy pin năm | W — cần nguồn thật |
| Cập nhật | OTA cẩn thận (A/B partition) | container/overlayfs (→2.7, 9.x) |
| Phù hợp | cảm biến, đèn, khóa, Wearable | camera, robot, edge AI, gateway tập hợp |

Sai lắng phổ biến: đưa Linux vào thiết bị pin vì "quen" — cần gateway/điện hoặc MCU thật sự, không có vùng giữa rẻ.

### 2.2 Giao thức — chọn theo "khoảng cách × pin × hệ sinh thái"

- **MQTT:** pub/sub qua broker, header nhỏ, QoS 0/1/2, retained message, LWT (last will — báo "thiết bị chết"). Chủ đạo trong công nghiệp & backend nhận dữ liệu (→ Kafka bridge). Chú ý: QoS-2 đắt — hầu hết dùng QoS-1 + idempotency phía consume.
- **CoAP:** UDP + mô hình REST thu nhỏ, cho mạng cực hạn băng thông; cần UDP xuyên được NAT (keepalive).
- **HTTP(S):** khi thiết bị đủ mạnh và infra web có sẵn — đơn giản, tốn pin/băng thông hơn.
- **Matter/Thread:** chuẩn smarthome (CSA) — interop giữa Apple/Google/Amazon/Samsung; Thread (IPv6 mesh) + Matter (application layer). Chọn khi sản phẩm cho nhà tiêu dùng cần "chạy với mọi hệ sinh thái".
- **LoRaWAN:** km, pin năm, băng thông byte — cảm biến nông nghiệp/thành phố; cần gateway + network server.
- **BLE/Zigbee/Z-Wave:** mesh ngắn cho nhà; qua hub.

### 2.3 Fleet: provisioning, danh tính, lifecycle

Thiết bị là **client không có màn hình và không ai SSH được** (→6.1 ràng buộc #8 nhân bản toàn vẹn). Ba quyết định gốc:

1. **Danh tính:** mỗi thiết bị một cặp khoá/x509 sinh lúc sản xuất (root of trust trong chip — secure element) — không password dùng chung (lỗi kinh điển khiến 10.000 camera botnet);
2. **Onboarding:** claim flow (QR code trên máy → người dùng/quản trị gán fleet) — tự động hoá: zero-touch (manufacturer certificate → cloud tự nhận);
3. **Thu hồi:** CRL/short-lived credential — thiết bị mất/mạng bị xâm nhập phải bị đuổi khỏi fleet trong phút, không phải năm.

### 2.4 OTA — tính năng sống còn

```
A/B partition: [slot A đang chạy][slot B nhận bản mới]
  → verify chữ ký + hash → đánh dấu thử → reboot sang B
  → watchdog/watchpost: không "báo sống" trong N phút → tự rollback A
```

Không có rollback tự động = bạn chưa có OTA, bạn có "sổ xổ bị brick". Kèm: update theo nhóm (canary fleet — 1% → 10% → all), giới hạn băng thông (fleet nghìn máy không dồn mạng nhà máy), và trạng thái version của toàn fleet trên một dashboard (→11.5 metrics + inventory).

### 2.5 Dữ liệu IoT về backend

```
[thiết bị] → MQTT/HTTP → [broker/gateway] → [Kafka (→5.7)] → [stream process (→5.12)] → [TSDB (→5.11)]
```

MQTT broker KHÔNG phải kho dài hạn — là cửa: giữ nó stateless càng nhiều càng tốt, mọi dữ liệu vào pipeline chuẩn (Quyển I – 5.x) trong vài trăm ms. Command ngược (cloud → thiết bị): qua topic command + ack + TTL (đừng đòi thiết bị offline 3 ngày còn nhận lệnh tức thời — store-and-forward ở gateway nếu cần).

---

## 3. Bảng số & phiên bản

| Thông số | Giá trị bậc | Nhãn | Ghi chú |
|---|---|---|---|
| MCU ngủ sâu | µA–mA | I | pin năm khả thi |
| MQTT header | ~2 byte fixed + nhỏ | I | vs HTTP ~vài trăm byte |
| LoRaWAN payload | ~chục byte/tin | I | |
| Thread mesh hop | chục mét/hop | I | |
| OTA partition | 2× flash app | P | chi phí phần cứng thật |

---

## 4. Suy luận kiến trúc

- **S1:** IoT = **hệ phân tán có hàng nghìn node không ai nhìn trực tiếp** — mọi thứ Quyển II/III (provisioning = identity, OTA = deploy, fleet dashboard = observability) áp xuống từng thiết bị như áp xuống một cluster.
- **S2:** Tham số trụ: fleet size, % online theo giờ, OTA success rate, thời gian mean từ release đến phủ fleet, dữ liệu loss rate.
- **S3:** Mỗi giao thức đổi khoảng cách/pin/complexity — bảng §2.2; chuẩn mở (MQTT/Matter) mua interop, hàng đóng (vendor hub) mua tiện ban đầu, trả thuế vĩnh viễn.
- **S4:** Edge Linux kế thừa mọi kỹ thuật Quyển I (Linux, container, observability) — MCU thì không (không filesystem, không ssh): tooling hai thế giới khác nhau, đừng ép một quy trình.
- **S5:** Edge AI (camera phát hiện, predictive maintenance) đẩy model về Jetson/NPU MCU — nhưng model phải OTA như firmware (version + rollback), nếu không "AI về đêm biến thành bug không ai cập nhật được" (→12.3).
- **S6:** Khi "thiết bị lạ lùng": ba câu hỏi theo thứ tự — firmware nào? provisioning khi nào? lần cuối online khi nào? — sau khi đủ ba câu trả lời thì mới tới "có phải phần cứng hỏng".

---

## 5. Hỏng thế nào & chẩn đoán

| Triệu chứng | Nguyên nhân hàng đầu | Lệnh chẩn | Mục |
|---|---|---|---|
| Fleet "ngơ" sau deploy OTA | Watchdog thiếu / brick | A/B rollback; canary fleet | §2.4 |
| Thiết bị rớt rồi lên liên tục | Wifi power-save/NAT timeout | keepalive tune; LWT | §2.2 |
| Broker quá tải | QoS-2 + retained lạm dụng | QoS-1; sharding topic | §2.2 |
| Bị botnet quét | Password dùng chung | per-device key (→6.7) | §2.3 |
| Lệnh cloud không tới | Thiết bị ngủ sâu không poll | store-and-forward gateway | §2.5 |
| Dữ liệu loang loạt mất | UDP/CoAP mất không ack | QoS/ack phù hợp | §2.2 |

---

## 6. Cách đo

```bash
# Fleet inventory: version firmware × trạng thái × lần online cuối
#   — dashboard này là "kubectl get nodes" của IoT (→9.1); không có nó = mù

# MQTT broker: số connection, message/s, rớt nối theo giờ
#   mosquitto_sub -t 'fleet/+/status' -v   # nghe một lát
# OTA funnel: gửi → nhận → verify → boot → report (mất ở chặng nào?)
```

Nguyên tắc: **mỗi thiết bị phải tự báo version + health định kỳ** (heartbeat) — im lặng là trạng thái nghiêm trọng nhất của fleet, không phải "không có gì để báo".

---

## 7. Lựa chọn thay thế & năm thấu kính

**Thay tự xây fleet platform:** AWS IoT Core / Azure IoT Hub / GCP IoT (đã ngừng — lưu ý rủi ro cloud) — mua nhanh, khóa vendor, giá theo tin nhắn phình theo fleet; tự xây trên MQTT broker + Kafka đang phổ biến ở fleet lớn. **Thay OTA tự viết:** MCUboot / platform vendor — ít quyền kiểm soát, ít trách nhiệm brick.

Năm thấu kính:
- **Kinh tế:** Chi phí thiết bị × số lượng vs chi phí vận hành fleet × năm — firmware khó update là chi phí lũy tiến; thiết bị đắt hơn 1$ nhưng OTA tốt đôi khi rẻ hơn tổng cuộc đời.
- **Vận hành:** Thiết bị "sống" ngoài kia 5–10 năm — legacy đường dài nhất của mọi phần mềm bạn từng viết (browser floor 2 năm là con của nó — →6.2); chính sách EOL sản phẩm phải công bố.
- **An ninh:** Mirai (2016) dạy bài học password chung → botnet triệu máy; điểm yếu của bạn là thiết bị cũ không update — chạy chương trình "fleet refresh" định kỳ như patch server (→6.7).
- **Lịch sử:** Từ SCADA/Modbus (1979) → MQTT (1999, dầu khí) → smartphone smarthome → Matter (2022): mỗi thế hệ chuẩn hoá thêm một tầng; Matter là cố gắng "HTTP moment" của nhà thông minh — đang nửa vời.
- **Người dùng:** Người dùng IoT là cả chủ nhà lẫn kỹ sư nhà máy — nhưng cùng một câu: "nó tự chạy, tôi không phải nghĩ". Mọi giao thức trên chỉ là cách khác nhau để đạt câu đó.

---

## 8. Đọc tiếp & bài tập

- Bảo mật thiết bị: **6.7** · MQTT→Kafka pipeline: **5.7** · TSDB lưu: **5.11** · Fleet như cluster: **9.1** · Edge AI: **12.3**
- **Bài tập 1:** Vẽ danh tính một thiết bị trong hệ thống bạn: khoá sinh ở đâu, lưu đâu, ai có thể thu hồi, bao lâu? Một trong bốn câu không trả lời được = lỗ hổng fleet.
- **Bài tập 2:** Mô phỏng brick: flash bản firmware lỗi cho 1 thiết bị, đo thời gian từ "biết lỗi" đến "thiết bị tự hồi phục". Nếu thời gian đó phụ thuộc con người can thiệp — chưa có OTA đúng nghĩa.
- **Bài tập 3:** Tính băng thông fleet: N thiết bị × message/s × byte — rồi nhân hệ số QoS-ack. Con số đó quyết định broker sizing và hoá đơn cloud trước khi viết dòng code đầu tiên.
