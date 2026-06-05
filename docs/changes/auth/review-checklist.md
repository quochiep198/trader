# Danh sách kiểm tra review — auth (Authentication & User Profile)

> Ngày: 2026-06-05
> Nguồn AC: `docs/changes/auth/spec-pack.md`
> Nguồn plan: `docs/changes/auth/impl-plan.md`
> Template: `docs/standards/templates/review-checklist.template.md`
> Mức độ nghiêm trọng: **Blocker** = bắt buộc sửa trước khi merge | **Major** = phải sửa trong PR này | **Minor** = sửa hoặc ghi nhận là nợ kỹ thuật

---

## 1. Spec / AC
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-01 | Tất cả AC ở mục 5 (Tiêu chí chấp nhận) của spec-pack đã được triển khai và có bằng chứng | Blocker | [x] |
| RC-02 | Không thêm hành vi nào nằm ngoài phạm vi spec-pack mục 1 (Trong phạm vi MVP) | Blocker | [x] |
| RC-03 | Các Open Issue (nếu phát sinh trong tương lai) vẫn được liệt kê; không mục nào được triển khai khi chưa có quyết định | Blocker | [x] |
| RC-04 | Flow/model chính của phần Auth & Profile tuân thủ đúng định hướng spec; không tạo flow hoặc behavior thay thế ngoài spec | Blocker | [x] |
 
## 2. Thiết kế / Phụ thuộc
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-05 | State/model của User được đặt ở đúng layer/module; không mutate rải rác trong UI/component | Major | [x] |
| RC-06 | Logic lưu JWT token/session được gom ở repository/service riêng; frontend không phụ thuộc trực tiếp storage cụ thể | Major | [x] |
| RC-07 | Không phát sinh phụ thuộc vòng tròn giữa auth store, UI và profile services | Major | [x] |
| RC-08 | Contract API (POST `/api/auth/register`, `/api/auth/login`, PUT `/api/profile`,...) thay đổi khớp với phần đã chốt trong impl-plan và spec | Blocker | [x] |
| RC-09 | Lifecycle của session đăng nhập được tách rõ; không trộn logic giữa token và profile data | Major | [x] |
| RC-10 | Rendering theo trạng thái xác thực (Anonymous, Authenticated, ProfileIncomplete) được tách rõ và không hard-code lan rộng | Major | [ ] |
 
## 3. Bảo mật
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-11 | Mật khẩu và email đăng ký từ user được validate định dạng và password policy trước khi hash | Blocker | [x] |
| RC-12 | Phân quyền và tách biệt dữ liệu được enforce ở BE; user chỉ truy cập được profile của chính mình qua token/session | Blocker | [ ] |
| RC-13 | Không log password thô, secret, hoặc dữ liệu cá nhân nhạy cảm trong error logs hoặc audit logs | Blocker | [x] |
| RC-14 | Không có rủi ro XSS khi hiển thị tên người dùng (name) trên Dashboard; escape/sanitize khi render | Blocker | [ ] |
| RC-15 | Dữ liệu lưu trong localStorage/cookie không chứa password thô hay thông tin nhạy cảm khác | Major | [x] |
 
## 4. Hiệu năng
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-16 | Việc chuyển đổi giữa các trang không trigger query fetch profile liên tục ngoài ý muốn | Major | [x] |
| RC-17 | Các giới hạn số đầu vào (như độ dài name, giới hạn số dư account_size) được áp dụng sớm ở FE | Major | [x] |
| RC-18 | Không gây re-render toàn bộ shell/page khi chỉ đổi state loading/error cục bộ của form | Major | [x] |
| RC-19 | Xử lý băm mật khẩu (bcrypt) hoặc gọi gửi email verify chạy async đúng cách và không block thread chính | Major | [x] |
 
## 5. Tương thích
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-20 | Cấu trúc dữ liệu users cũ (nếu có) vẫn hoạt động hoặc có migration xử lý backward-compatible | Blocker | [x] |
| RC-21 | Migration tạo bảng `users` có rollback/down migration tương ứng | Major | [ ] |
| RC-22 | Các api endpoint khác (chưa viết) khi tích hợp auth middleware không bị thay đổi hành vi ngoài ý muốn | Blocker | [ ] |
| RC-23 | Trường hợp người dùng cũ chưa cập nhật profile (thiếu account_size) được chuyển trạng thái đúng sang `ProfileIncomplete` | Major | [ ] |
 
## 6. Logging / Audit
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-24 | Các thao tác register, login, logout, reset password, update profile được ghi nhận audit log đầy đủ | Major | [ ] |
| RC-25 | Log audit chỉ lưu metadata cần thiết (user_id, action, timestamp), không chứa password_hash, token thô | Blocker | [ ] |
| RC-26 | Thông báo lỗi đăng nhập sai (Wrong password/email) được chuẩn hóa chung để tránh rò rỉ thông tin sự tồn tại của tài khoản | Minor | [x] |
 
## 7. Xử lý lỗi
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-27 | Khi thiếu account_size hoặc max risk, UI hiển thị cảnh báo rõ ràng và không tính toán sai tỉ lệ rủi ro | Major | [ ] |
| RC-28 | Thao tác đổi mật khẩu/reset mật khẩu yêu cầu xác nhận chính xác; nút Cancel giữ nguyên mật khẩu cũ | Blocker | [ ] |
| RC-29 | Thao tác xóa tài khoản (nếu triển khai sau này) có confirm dialog trước khi thực hiện | Major | [ ] |
| RC-30 | Trùng email khi đăng ký được trả lỗi rõ ràng ở đầu API; không ghi đè lên tài khoản cũ | Blocker | [x] |
| RC-31 | Update profile thất bại do lỗi mạng/server không làm mất thông tin cũ hiển thị trên màn hình | Blocker | [ ] |
| RC-32 | Client không nhận stack trace từ backend; lỗi đăng nhập hoặc update profile dùng wording dễ hiểu | Major | [x] |
 
## 8. Kiểm thử
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-33 | Unit test bao phủ chính sách mật khẩu (Password Policy) cho đăng ký | Major | [ ] |
| RC-34 | Unit test bao phủ middleware xác thực token (Auth Middleware) và phân tách dữ liệu user | Major | [ ] |
| RC-35 | Unit test bao phủ validation đầu vào của Profile (`account_size > 0`, `default_max_risk_per_trade` trong khoảng 0-100) | Major | [ ] |
| RC-36 | Unit test bao phủ kiểm tra trùng lặp email khi đăng ký | Major | [ ] |
| RC-37 | Manual/E2E test bao phủ toàn bộ luồng: Đăng ký -> Xác thực Email -> Đăng nhập -> Cập nhật Profile | Major | [ ] |
| RC-38 | Manual/E2E test bao phủ kịch bản đăng xuất và xác minh token bị vô hiệu hóa | Major | [ ] |
| RC-39 | Kiểm tra trực quan (Visual check) các trạng thái: Form trống, Form lỗi validation, Trạng thái Loading khi gọi API | Major | [x] |
 
## 9. Vận hành
 
| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-40 | Quy trình rollback DB schema cho bảng `users` được chuẩn bị | Major | [x] |
| RC-41 | Cách thức xóa dữ liệu nhạy cảm hoặc debug session của user được hướng dẫn | Minor | [x] |
| RC-42 | Các cấu hình JWT Secret key, SMTP credentials cho email được đặt ở biến môi trường bảo mật | Minor | [x] |
| RC-43 | Không thêm feature flag cho cơ chế đăng nhập lõi của MVP | Minor | [x] |
| RC-44 | Bản tin miễn trừ trách nhiệm đầu tư bắt buộc (Mandatory Investment Disclaimer / Risk Disclosure) xuất hiện đầy đủ trên Login, Register và Forgot Password | Blocker | [x] |
| RC-45 | Nút bấm ẩn/hiện mật khẩu (Password visibility toggle) chuyển đổi trạng thái input (password <-> text) và icon chính xác | Major | [x] |
| RC-46 | Giao diện Quên mật khẩu có lớp phủ thành công (Success Overlay) hiển thị tại chỗ với nút Resend Email khi gửi thành công | Major | [ ] |
| RC-47 | Tương tác trạng thái (Micro-interactions) của nút submit hiển thị chuyển trạng thái Loading và Success chính xác | Major | [x] |

---

## Bảng ánh xạ AC → Checklist items

| #   | AC | Các hạng mục checklist xác nhận |
| --- | -- | ------------------------------- |
| 1   | AC-AUTH-1/v1 (Đăng ký tài khoản) | RC-01, RC-08, RC-11, RC-19, RC-30, RC-33, RC-36, RC-37, RC-44, RC-47 |
| 2   | AC-AUTH-2/v1 (Đăng nhập hệ thống) | RC-01, RC-05, RC-08, RC-10, RC-12, RC-15, RC-34, RC-37, RC-44, RC-45, RC-47 |
| 3   | AC-AUTH-3/v1 (Đăng xuất khỏi hệ thống) | RC-01, RC-06, RC-08, RC-09, RC-37, RC-38 |
| 4   | AC-PROFILE-1/v1 (Lưu profile rủi ro) | RC-01, RC-05, RC-08, RC-11, RC-17, RC-31, RC-35, RC-37 |
| 5   | AC-PROFILE-2/v1 (Cảnh báo thiếu thông tin) | RC-01, RC-10, RC-23, RC-27 |
| 6   | AC-PROFILE-3/v1 (Sử dụng đúng profile) | RC-01, RC-12, RC-34 |
| 7   | AC-AUTH-FORGOT (Quên mật khẩu - Mở rộng) | RC-44, RC-46 |
