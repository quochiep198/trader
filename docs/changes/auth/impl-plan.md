# Kế hoạch triển khai: Authentication & User Profile (impl-auth-profile)

Kế hoạch này chi tiết hóa cách thức xây dựng phân hệ Đăng nhập, Đăng ký, Quản lý tài khoản và thiết lập hồ sơ giao dịch (tính toán rủi ro) cho TradeMind AI MVP.

---

## 1. Mục tiêu chức năng

### 1.1 Authentication
*   **Đăng ký:** Cho phép người dùng tạo tài khoản mới bằng Email và Mật khẩu. Bắt buộc có cơ chế Email Verification gửi OTP/Link xác nhận để kích hoạt tài khoản.
*   **Đăng nhập/Đăng xuất:** Xác thực phiên bản email/password. Phiên đăng nhập cần được bảo mật và tách biệt dữ liệu hoàn toàn.
*   **Quên mật khẩu (Forgot Password):** Cho phép đặt lại mật khẩu thông qua email xác nhận.
*   **Password Policy:** Độ dài mật khẩu tối thiểu 8 ký tự, bao gồm ít nhất 1 chữ hoa, 1 chữ thường, 1 chữ số.

### 1.2 User Profile
*   Cung cấp các thông tin cần thiết phục vụ cho việc tính toán rủi ro tài chính của lệnh giao dịch:
    *   `account_size` (VND - Số dư tài khoản hiện tại): Số dương bắt buộc để tính `% risk/trade`.
    *   `default_max_risk_per_trade` (Mặc định: 2%): Giới hạn rủi ro thiết lập cho bộ lọc quy tắc.
    *   `trading_style` (Swing, Day Trade, Scalping, Position): Lưu phục vụ mục đích thống kê.
    *   `experience_level` (Beginner, Intermediate, Professional): Lưu phục vụ phân tích coach message.

---

## 2. Thiết kế dữ liệu (Database Schema)

### Bảng `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified_at TIMESTAMP NULL,
    verification_token VARCHAR(255) NULL,
    reset_password_token VARCHAR(255) NULL,
    reset_password_expires TIMESTAMP NULL,
    
    -- Risk Profile Fields
    account_size DECIMAL(18, 2) NOT NULL DEFAULT 0.00,
    default_max_risk_per_trade DECIMAL(5, 2) NOT NULL DEFAULT 2.00, -- Lưu tỉ lệ % (ví dụ: 2.00%)
    trading_style VARCHAR(50) NOT NULL DEFAULT 'Swing',
    experience_level VARCHAR(50) NOT NULL DEFAULT 'Beginner',
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Các API Endpoints cần xây dựng

| Phương thức | Path | Body / Payload | Mô tả |
|-------------|------|----------------|-------|
| `POST` | `/api/auth/register` | `{"email": "...", "password": "...", "name": "..."}` | Đăng ký tài khoản mới & gửi email xác thực |
| `POST` | `/api/auth/verify-email`| `{"token": "..."}` | Xác thực email kích hoạt tài khoản |
| `POST` | `/api/auth/login` | `{"email": "...", "password": "..."}` | Xác thực đăng nhập, trả về Session/JWT token |
| `POST` | `/api/auth/logout` | Không | Hủy phiên đăng nhập hiện tại |
| `POST` | `/api/auth/forgot-password`| `{"email": "..."}` | Gửi link reset mật khẩu |
| `POST` | `/api/auth/reset-password`| `{"token": "...", "new_password": "..."}` | Đặt lại mật khẩu mới |
| `GET` | `/api/profile` | Không | Lấy thông tin Profile của user hiện tại |
| `PUT` | `/api/profile` | `{"name": "...", "account_size": 100000000, "default_max_risk_per_trade": 2.0, "trading_style": "...", "experience_level": "..."}` | Cập nhật thông tin Profile/Risk Setup |

---

## 4. Các luồng xử lý chi tiết (Business Logic Flow)

### 4.1 Đăng ký tài khoản (Register)
1.  Frontend validate client-side (Email đúng định dạng, Password tuân thủ Password Policy).
2.  Backend kiểm tra email có tồn tại trong hệ thống chưa.
3.  Mật khẩu được băm bằng thuật toán bảo mật (ví dụ: **bcrypt** hoặc **argon2**). *Tuyệt đối không lưu plaintext*.
4.  Tạo tài khoản với `email_verified_at = NULL` và sinh ra `verification_token`.
5.  Gửi email kèm đường dẫn chứa token kích hoạt tài khoản.

### 4.2 Cập nhật Profile
1.  Bảo vệ endpoint bằng middleware xác thực (Authentication Middleware).
2.  Kiểm tra dữ liệu nhập vào:
    *   `account_size` bắt buộc phải là số dương lớn hơn 0.
    *   `default_max_risk_per_trade` phải thuộc khoảng `(0, 100]`.
3.  Cập nhật thông tin vào DB dựa trên `user_id` lấy từ session/token hiện tại (Tránh rủi ro IDOR).

---

## 5. Các trạng thái giao diện UI cần thiết kế

1.  **Màn hình Register/Login:** 
    *   Form nhập liệu rõ ràng.
    *   Hiển thị thông báo validation trực quan khi mật khẩu không đủ mạnh hoặc email bị trùng.
2.  **Màn hình Đăng ký thành công:** Yêu cầu người dùng kiểm tra hòm thư kích hoạt.
3.  **Trang Setup Profile / Risk Profile:**
    *   Hiển thị cảnh báo nếu `account_size` hoặc `default_max_risk_per_trade` chưa được nhập (vì nếu thiếu, các tính năng Pre-trade Check sau này sẽ bị hạn chế tính toán).

---

## 6. Kế hoạch kiểm thử (Verification Plan)

### 6.1 Unit Tests (Kiểm thử đơn vị)
*   `test_password_policy_validation`: Kiểm thử bộ lọc mật khẩu với các case mật khẩu yếu, mật khẩu mạnh.
*   `test_password_hashing`: Đảm bảo mật khẩu lưu trong DB đã được hash và không thể dịch ngược.
*   `test_profile_validation`: Kiểm thử API update profile với `account_size <= 0` hoặc tỉ lệ rủi ro không hợp lệ.

### 6.2 Integration Tests (Kiểm thử tích hợp)
*   `test_register_flow`: Đăng ký tài khoản -> Kiểm tra DB xem tài khoản có ở trạng thái chờ kích hoạt -> Xác thực email bằng token -> Tài khoản được kích hoạt thành công.
*   `test_user_data_isolation`: User A cố tình gọi API GET/PUT profile của User B bằng cách đổi payload ID, đảm bảo hệ thống trả lỗi `403 Forbidden` (Chống rủi ro rò rỉ dữ liệu).
