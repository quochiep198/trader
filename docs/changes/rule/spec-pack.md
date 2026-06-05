# Đặc tả chức năng: Personal Trading Rules (spec-personal-rules)

Tài liệu này đặc tả chi tiết yêu cầu nghiệp vụ, giao diện, dữ liệu và tiêu chí chấp nhận cho chức năng Thiết lập luật giao dịch cá nhân (Personal Trading Rules).

---

## 1. Phạm vi nghiệp vụ (Scope)

### Trong phạm vi MVP:
*   Xem danh sách các quy tắc giao dịch cá nhân (gồm rule hệ thống mặc định).
*   Bật/tắt trạng thái hoạt động (`is_active`) của từng quy tắc.
*   Chỉnh sửa giá trị ngưỡng hoạt động (`rule_value`) cho các quy tắc.
*   Validation giá trị rule hợp lệ trước khi lưu.
*   Hiển thị disclaimer: Rule chỉ dùng để cảnh báo kỷ luật, không phải tín hiệu mua/bán cổ phiếu.

### Ngoài phạm vi MVP:
*   Tự tạo rule tùy chỉnh mới (Custom rules).
*   Đề xuất rule tự động học từ lịch sử giao dịch cá nhân.

---

## 2. Quy tắc nghiệp vụ cứng (Business Rules)

| ID | Quy tắc nghiệp vụ | Mã AC tương ứng |
|---|---|---|
| **R-RULES-1** | Quy tắc cá nhân có thể xem, bật/tắt, chỉnh sửa giá trị; chỉ những quy tắc đang hoạt động (`is_active = true`) mới áp dụng khi check lệnh. | AC-RULES-1/v1, AC-RULES-2/v1, AC-RULES-3/v1 |
| **R-RULES-2** | Giá trị rule không hợp lệ (nhập số âm, vượt khung cho phép) phải bị hệ thống từ chối lưu. | AC-RULES-4/v1 |
| **R-RULES-3** | Bộ luật cá nhân và Rule Engine chỉ tạo cảnh báo kỷ luật, tuyệt đối không tạo tín hiệu khuyến nghị mua/bán. | AC-RULES-5/v1 |
| **R-RULES-4** | Quy tắc `prevent_oversized_trade` phát hiện giao dịch khối lượng bất thường dựa trên risk_percent, trade_value và lịch sử giao dịch. | AC-RULES-3/v1, AC-RISK-3/v1 |

---

## 3. Bản vẽ màn hình & Giao diện (Wireframes)

### 3.1 Bố cục giao diện Personal Trading Rules (Bento Grid Layout)
Giao diện tuân thủ phong cách **Corporate / Modern** với tông màu nền xanh đen sâu đậm (#0F172A) kết hợp các thẻ Acrylic bóng mờ (#1E293B) có viền 1px tinh tế (#334155). 

```text
+-----------------------------------------------------------------------------------------+
|  TradeMind AI   |  [Header] Trading Rules     [Search parameters...]   [Notif] [Avatar] |
|  Discipline     +-----------------------------------------------------------------------+
|  Coach          |  [!] Rules are for discipline coaching, not buy/sell signals.         |
|  ---------------+-----------------------------------------------------------------------+
|  [ ] Dashboard  |  +--------------------------------+  +------------------------------+ |
|  [ ] Pre-trade  |  | Discipline Framework           |  | [Icon] Require Stop-loss     | |
|  [ ] Journal    |  |                                |  | Mandates exit price... [Toggle] |
|  [*] Rules      |  | These rules act as your        |  +------------------------------+ |
|  [ ] Settings   |  | behavioral guardrails...       |  | [Icon] Max Risk per Trade    | |
|                 |  |                                |  | strictly limits... 2%  [Toggle] |
|  +------------+ |  | Adherence Score: ( 88 )        |  +------------------------------+ |
|  | Log Trade  | |  | Strong Consistency             |  | [Icon] Max Consecutive Loss  | |
|  +------------+ |  |                                |  | Triggers cooldown... 3 [Toggle] |
|                 |  +--------------------------------+  +------------------------------+ |
|  [ ] Support    |                                      | [Icon] Max FOMO Score        | |
|  [ ] Sign Out   |                                      | AI calculated... 7   [Toggle] |
|                 |                                      +------------------------------+ |
|                 |                                      | [Icon] Max Trades per Day    | |
|                 |                                      | Limits over-trading.. [Toggle] |
|                 |                                      +------------------------------+ |
|                 |                                                                       |
|                 |                                          [Discard] [Save Settings]    |
+-----------------------------------------------------------------------------------------+
```

### 3.2 Đặc tả các khối thành phần (Component Specifications)

1. **Thanh điều hướng bên trái (Sidebar Navigation):**
   * **Logo & Brand:** `TradeMind AI` (Màu primary `#BEC6E0` nổi bật) đi kèm nhãn phụ `Discipline Coach` viết hoa dạng nhỏ.
   * **Menu liên kết:** Dashboard, Pre-trade Check, Trade Journal, Trading Rules (đang được kích hoạt active), Settings.
   * **Nút Action:** "Log New Trade" màu ngọc lục bảo (Emerald `#4EDE03`) có micro-interaction chuyển đổi tỷ lệ co giãn khi click.
   * **Liên kết phụ:** Support và Sign Out.

2. **Thanh công cụ phía trên (Header):**
   * **Tiêu đề phân hệ:** `Trading Rules` chữ đậm, kích thước lớn.
   * **Sub-nav liên kết:** Market Data, Performance, Analytics.
   * **Tìm kiếm:** Input tròn tích hợp icon tìm kiếm và placeholder `"Search parameters..."`.
   * **Khu vực User:** Nút bật tắt thông báo chuông và ảnh đại diện Avatar hình tròn.

3. **Banner Cảnh báo (Warning Alert Banner):**
   * Hiển thị cảnh báo quan trọng có hiệu ứng nhấp nháy nhẹ (pulse): `"Rules are for discipline coaching, not buy/sell signals."` (Rule chỉ phục vụ mục đích kiểm soát kỷ luật, không cấu thành khuyến nghị mua bán) đi kèm icon cảnh báo màu hổ phách (`status-caution` `#F59E0B`).

4. **Khối Chỉ số kỷ luật (Discipline Header Card):**
   * Chiếm 4 cột trên lưới Desktop. Chứa tiêu đề phụ `"Discipline Framework"`, phần giải thích hành vi và một **Vòng đo Adherence Score** dạng bán nguyệt/tròn hiển thị điểm kỷ luật tuần trước (ví dụ: `88` - Strong Consistency) dùng tông màu xanh lá thành công (`status-good` `#10B981`).

5. **Danh sách các quy tắc (Rules List):**
   * Chiếm 8 cột trên lưới Desktop. Hiển thị dạng thẻ danh sách các quy tắc. Mỗi thẻ gồm:
     * **Icon minh họa:** Tách biệt theo loại quy tắc (`security`, `percent`, `history`, `psychology`, `timer`).
     * **Tiêu đề luật & Giá trị hiện tại:** Có các nhãn Badge dạng con số đơn sắc hiển thị ngưỡng đang cấu hình (ví dụ: `2%`, `3`, `7`).
     * **Nội dung giải thích:** Đoạn mô tả chi tiết chức năng ngăn chặn hành vi xấu.
     * **Nút bấm Edit:** Icon bút chì chỉnh sửa giá trị quy tắc (chỉ hiện rõ khi hover chuột vào thẻ - group-hover).
     * **Nút gạt Bật/Tắt (Switch Toggle):** Cho phép kích hoạt hoặc tắt luật nhanh. Switch chuyển màu xanh lá (Emerald) khi ON và xám tối khi OFF.

6. **Chân trang Hành động (Action Footer):**
   * Nút hủy bỏ thay đổi (`Discard Changes`).
   * Nút lưu thiết lập kỷ luật (`Save Disciplinary Settings`) nổi bật với hiệu ứng shadow tỏa rộng, khi click sẽ kích hoạt **Success Toast** thông báo đồng bộ hóa thành công: *"Rules Synchronized - Your discipline framework is now active."* ở góc phải màn hình.

---


## 4. Dữ liệu & Quy tắc Validation

### 4.1 Bảng dữ liệu Rules (Trích xuất)
*   `rules`: `id` (UUID), `user_id` (FK), `rule_type`, `rule_value`, `is_active`, `created_at`, `updated_at`.

### 4.2 Ngưỡng Validation
*   `max_risk_per_trade`: Thuộc khoảng `(0, 100)` dưới dạng tỉ lệ %.
*   `max_consecutive_losses`, `max_trades_per_day`: Số nguyên dương lớn hơn 0.
*   `max_fomo_score`: Số nguyên trong khoảng `[1, 10]`.

---

## 5. Tiêu chí chấp nhận (Acceptance Criteria - AC-RULES)

*   **AC-RULES-1/v1:** Người dùng xem được danh sách rule cá nhân, gồm rule mặc định và trạng thái bật/tắt.
*   **AC-RULES-2/v1:** Người dùng bật/tắt một rule và lần kiểm tra lệnh tiếp theo chỉ áp dụng rule đang bật.
*   **AC-RULES-3/v1:** Người dùng chỉnh được giá trị rule hợp lệ và hệ thống dùng giá trị mới khi kiểm tra lệnh.
*   **AC-RULES-4/v1:** Nếu người dùng nhập giá trị rule không hợp lệ, hệ thống từ chối lưu và hiển thị lỗi dễ hiểu.
*   **AC-RULES-5/v1:** Rule mặc định không được tự động biến thành khuyến nghị mua/bán; rule chỉ dùng để cảnh báo kỷ luật.

---

## 6. Bảng truy vết kiểm thử (Traceability Matrix)

| AC | Screen/API | DB | Logs | Permissions | Test type |
|---|---|---|---|---|---|
| **AC-RULES-1/v1** | Personal Rules / GET /rules | rules | rule_validation | Owner user | IT · E2E · BB |
| **AC-RULES-2/v1** | Personal Rules / PUT /rules/:id/toggle | rules | rule_change | Owner user | UT · IT · E2E · BB |
| **AC-RULES-3/v1** | Personal Rules / PUT /rules/:id/value | rules | rule_change | Owner user | UT · IT · E2E · BB |
| **AC-RULES-4/v1** | Personal Rules / PUT /rules/:id/value | rules | rule_validation | Owner user | UT · IT · E2E · BB |
| **AC-RULES-5/v1** | Rule Engine validation | rules | rule_validation | Owner user | UT · IT · E2E · BB |
