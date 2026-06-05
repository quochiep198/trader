# Kế hoạch triển khai: Personal Trading Rules (impl-personal-rules)

Kế hoạch này chi tiết hóa cách thiết lập hệ thống Luật giao dịch cá nhân (Personal Trading Rules) cho TradeMind AI MVP.

---

## 1. Mục tiêu chức năng

*   Cho phép người dùng xem danh sách bộ luật giao dịch cá nhân.
*   Người dùng có thể **Bật/Tắt (Toggle Active)** từng rule. Chỉ những rule đang active mới được Rule Engine sử dụng khi chạy Pre-trade Check.
*   Người dùng có thể **Chỉnh sửa giá trị (Edit Value)** của rule (ví dụ: đổi giới hạn rủi ro từ 2% sang 1.5%, đổi số trận thua liên tiếp tối đa cho phép từ 3 sang 2).
*   **Validation:** Ngăn chặn lưu các giá trị rule không hợp lệ (ví dụ: tỉ lệ rủi ro âm, số trận thua âm).
*   **AI Disclaimer & Guardrail:** Màn hình quản lý luật phải hiển thị rõ thông báo nhắc nhở: "Luật giao dịch chỉ phục vụ mục đích kiểm soát kỷ luật cá nhân, không cấu thành tín hiệu/khuyến nghị mua bán chứng khoán."

---

## 2. Thiết kế dữ liệu (Database Schema)

### Bảng `rules`
```sql
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Tên mã luật (rule_type) định danh cho Rule Engine
    rule_type VARCHAR(50) NOT NULL, 
    
    -- Giá trị của luật lưu dưới dạng String để linh hoạt (ví dụ: '2%', '3', '7')
    rule_value VARCHAR(100) NOT NULL,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Ràng buộc tránh tạo trùng lặp một rule cho cùng một user
    UNIQUE (user_id, rule_type)
);
```

### Danh mục Rule mặc định (Seeding Data)
Khi user đăng ký tài khoản thành công, hệ thống tự động khởi tạo (seed) bộ luật mặc định cho user:
1.  `require_stop_loss`: `true` | `Active` (Bắt buộc stop-loss khi đặt lệnh).
2.  `max_risk_per_trade`: `2%` (hoặc lấy từ Profile của user) | `Active` (Tỉ lệ rủi ro tối đa mỗi trade).
3.  `max_consecutive_losses`: `3` | `Active` (Số lệnh thua liên tiếp tối đa).
4.  `max_fomo_score`: `7` | `Active` (Điểm FOMO tối đa cho phép).
5.  `max_trades_per_day`: `5` | `Inactive` (Số lệnh tối đa mỗi ngày).
6.  `cooldown_after_loss`: `24` (giờ) | `Inactive` (Thời gian nghỉ sau mỗi trade thua).
7.  `prevent_oversized_trade`: `-15` (penalty score) | `Active` (Cảnh báo lệnh khối lượng bất thường).

---

## 3. Các API Endpoints cần xây dựng

| Phương thức | Path | Body / Payload | Mô tả |
|-------------|------|----------------|-------|
| `GET` | `/api/rules` | Không | Lấy danh sách toàn bộ luật của user hiện tại |
| `PUT` | `/api/rules/:id/toggle` | Không | Bật hoặc Tắt trạng thái hoạt động (`is_active`) của rule |
| `PUT` | `/api/rules/:id/value` | `{"rule_value": "..."}` | Cập nhật giá trị hoạt động của rule |

---

## 4. Quy tắc Validation nghiệp vụ (Business Rules Validation)

Khi người dùng chỉnh sửa `rule_value`, API phải thực hiện kiểm tra tính hợp lệ tùy theo `rule_type`:
*   `max_risk_per_trade`: Giá trị phải chuyển đổi được về dạng số thực dương và nằm trong khoảng `(0, 100)`.
*   `max_consecutive_losses`, `max_trades_per_day`, `cooldown_after_loss`: Phải là số nguyên dương lớn hơn 0.
*   `max_fomo_score`: Phải là số nguyên nằm trong thang điểm `[1, 10]`.

---

## 5. Các trạng thái giao diện UI cần thiết kế

Thiết kế giao diện tuân thủ chặt chẽ tài liệu hướng dẫn phong cách và phân bố không gian (Bento Grid):

1. **Bố cục chính (Layout Frame):**
   * **Thanh điều hướng bên trái (Sidebar):** Rộng 64px (cố định), màu nền `primary-container` (#0F172A), chứa liên kết dạng Tab. Tab "Trading Rules" được tô sáng bằng màu lục bảo (#4EDE03) và bo góc dạng tròn nhẹ.
   * **Thanh công cụ trên đầu (Header):** Cao 16px (h-16), chứa các liên kết nhanh (Market Data, Performance, Analytics), thanh tìm kiếm bo tròn và Avatar người dùng.

2. **Khối Kỷ luật (Discipline Card):**
   * Sử dụng card dạng bán trong suốt (Glassmorphism) với nền `#1E293B` độ mờ 70% kết hợp hiệu ứng `backdrop-filter: blur(12px)` và viền màu `#334155`.
   * Tích hợp một vòng tròn đo điểm Adherence Score (88 - Strong Consistency) bằng màu xanh lá chỉ thị thành công.

3. **Danh sách các quy tắc (Rules List):**
   * Hiển thị các Rule dưới dạng hàng/thẻ hoverable. Khi người dùng di chuột qua (hover), viền thẻ đổi từ màu xám mặc định sang màu xanh lục bảo mờ (`rgba(78, 222, 163, 0.3)`).
   * Mỗi rule có một icon Material Symbols tương ứng (ví dụ: `security` cho Stop-loss, `percent` cho Max Risk).
   * Giá trị cấu hình của rule được bọc trong một thẻ Badge màu tối `#2A2A2B` với text màu xanh lục bảo.

4. **Nút gạt Bật/Tắt (Switch Toggle):**
   * Nút gạt chuyển trạng thái hoạt động của từng quy tắc. Khi ở trạng thái hoạt động (active), màu nền của switch chuyển sang màu ngọc lục bảo (`#4EDE03`), ngược lại hiển thị màu xám tối `#353436`.

5. **Banner cảnh báo cố định (Caution Alert Banner):**
   * Đặt cố định ở đầu nội dung chính với nền vàng hổ phách mờ 10% (`status-caution/10`), viền vàng hổ phách 20%, hiển thị câu cảnh báo: `"Rules are for discipline coaching, not buy/sell signals."` để nhắc nhở người dùng tuân thủ nguyên tắc kỷ luật.

6. **Hộp thoại/Form sửa giá trị (Edit Form):**
   * Thiết kế input dạng chìm (inset depth) với nền tối hơn thẻ card. Khi được focus, input hiển thị viền tỏa sáng (focus ring) màu xanh lam rộng 2px.

7. **Trạng thái thông báo thành công (Success Toast):**
   * Khi lưu thiết lập, hiển thị một Toast trượt từ dưới lên ở góc phải màn hình (`translate-y-0 opacity-100`) với thông điệp `"Rules Synchronized - Your discipline framework is now active"`. Toast sẽ tự động ẩn đi sau 3 giây.

---

## 6. Kế hoạch kiểm thử (Verification Plan)

### 6.1 Unit Tests (Kiểm thử đơn vị)
*   `test_rule_seeding_on_registration`: Đăng ký user mới và kiểm tra xem database có tự tạo đủ các rule mặc định với trạng thái `is_active` chính xác không.
*   `test_rule_value_validation_limits`: Kiểm thử nhập giá trị sai (như `-2%`, `0` trận thua, FOMO score = `11`) đảm bảo API từ chối cập nhật và trả lỗi.

### 6.2 Integration Tests (Kiểm thử tích hợp)
*   `test_rule_toggle_behavior`: Bật/Tắt rule, kiểm tra trong DB trạng thái `is_active` thay đổi.
*   `test_rule_isolation`: User A tìm cách PUT/toggle rule của User B, hệ thống trả lỗi `403 Forbidden`.
