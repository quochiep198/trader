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

### Màn hình Personal Trading Rules:
```text
+----------------------------------------------------------------+
| PERSONAL TRADING RULES                                         |
|----------------------------------------------------------------|
| Rule                            | Value | Active | Action      |
| Require stop-loss               | Yes   | ON     | [Toggle]    |
| Max risk per trade              | 2%    | ON     | [Edit]      |
| Max consecutive losses          | 3     | ON     | [Edit]      |
| Max FOMO score                  | 7     | ON     | [Edit]      |
| Max trades per day              | 5     | OFF    | [Edit]      |
| Cooldown after loss             | TBD   | OFF    | [Edit]      |
| Prevent oversized trade         | -15   | ON     | [Edit]      |
|----------------------------------------------------------------|
| Message: Rule chỉ cảnh báo kỷ luật, không phải tín hiệu mua/bán.|
+----------------------------------------------------------------+
```

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
