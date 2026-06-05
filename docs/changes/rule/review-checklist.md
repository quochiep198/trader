# Danh sách kiểm tra review — rule (Personal Trading Rules)

> Ngày: 2026-06-05
> Nguồn AC: `docs/changes/rule/spec-pack.md`
> Nguồn plan: `docs/changes/rule/impl-plan.md`
> Mức độ nghiêm trọng: **Blocker** = bắt buộc sửa trước khi merge | **Major** = phải sửa trong PR này | **Minor** = sửa hoặc ghi nhận là nợ kỹ thuật

---

## 1. Spec / AC

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-01 | Tất cả AC ở mục 5 (Tiêu chí chấp nhận) của spec-pack đã được triển khai và có bằng chứng | Blocker | [x] |
| RC-02 | Không thêm hành vi nào nằm ngoài phạm vi spec-pack mục 1 (Chỉ xem, bật/tắt, sửa giá trị rule mặc định; không cho phép tạo custom rule tự do trong MVP) | Blocker | [x] |
| RC-03 | Các Open Issue (nếu phát sinh trong tương lai) vẫn được liệt kê; không mục nào được triển khai khi chưa có quyết định | Blocker | [x] |
| RC-04 | Sơ đồ và luồng hoạt động chính tuân thủ đúng thiết kế spec; không tạo flow hoặc behavior thay thế ngoài spec | Blocker | [x] |

## 2. Thiết kế / Phụ thuộc

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-05 | State quản lý danh sách rules được tổ chức tập trung ở trang chính hoặc store; các sub-component không thay đổi trực tiếp | Major | [x] |
| RC-06 | API service gọi quy tắc được tách biệt; frontend không gọi trực tiếp URL thô trong component | Major | [x] |
| RC-07 | Không phát sinh phụ thuộc vòng tròn giữa module rules, profile, và rule engine kiểm tra lệnh | Major | [x] |
| RC-08 | Contract API (GET `/api/rules`, PUT `/api/rules/:id/toggle`, PUT `/api/rules/:id/value`) khớp chính xác cấu hình đã chốt | Blocker | [x] |
| RC-09 | Việc lưu trữ thông số rules không làm thay đổi hay ghi đè lên cấu hình thông số tài khoản (Profile) của user | Major | [x] |
| RC-10 | Phân tách rõ quy trình hiển thị rule đang active (`is_active = true`) và rule inactive (`is_active = false`) trên UI | Major | [x] |

## 3. Bảo mật

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-11 | Các tham số sửa đổi từ người dùng phải được validate nghiêm ngặt ở cả FE và BE để tránh SQL Injection hoặc lỗi kiểu dữ liệu | Blocker | [x] |
| RC-12 | Phân quyền và tách biệt dữ liệu được enforce ở BE; người dùng chỉ sửa đổi và xem được rule của chính mình thông qua JWT token | Blocker | [x] |
| RC-13 | Không ghi nhận hoặc lưu trữ các thông tin nhạy cảm của người dùng trong logs thay đổi cấu hình rule | Blocker | [x] |
| RC-14 | Ràng buộc tránh lỗi ghi đè chéo: API cập nhật chỉ nhận `rule_id` thuộc sở hữu của user gửi request | Blocker | [x] |
| RC-15 | Dữ liệu cấu hình của rule không được lưu tạm ở cache trình duyệt vượt quá vòng đời phiên làm việc của user | Major | [x] |

## 4. Hiệu năng

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-16 | Việc bật/tắt (toggle) trạng thái hoạt động của rule được cập nhật mượt mà, không gây hiện tượng tải lại toàn trang (re-fetch toàn bộ danh sách) | Major | [x] |
| RC-17 | Các giới hạn số đầu vào (ví dụ: điểm fomo từ 1-10) được áp dụng chặn ngay tại input component của FE | Major | [x] |
| RC-18 | Việc thay đổi giá trị một rule đơn lẻ không kích hoạt re-render toàn bộ khung Sidebar hay Header điều hướng | Major | [x] |
| RC-19 | Động cơ kiểm tra luật (Rule Engine) lấy cấu hình rule từ database tối ưu hóa bằng indexing hoặc cache đệm để tránh nghẽn luồng chính | Major | [x] |

## 5. Tương thích

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-20 | Các luật mặc định cũ (nếu có) không bị lỗi cấu trúc dữ liệu khi thay đổi schema của bảng `rules` | Blocker | [x] |
| RC-21 | Migration tạo bảng `rules` có đi kèm rollback/down migration tương ứng | Major | [ ] |
| RC-22 | Khi tắt trạng thái hoạt động của một rule, Rule Engine phải lập tức bỏ qua quy tắc đó trong lần check lệnh tiếp theo | Blocker | [x] |
| RC-23 | Dữ liệu khởi tạo (seeding data) các luật mặc định được thực hiện tự động ngay sau khi đăng ký tài khoản thành công | Major | [x] |

## 6. Logging / Audit

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-24 | Mọi thao tác thay đổi giá trị hoặc bật/tắt hoạt động của rule được ghi nhận log nghiệp vụ (audit log) rõ ràng | Major | [ ] |
| RC-25 | Log audit chỉ lưu các thông tin cần thiết (rule_id, user_id, old_value, new_value, action), không lưu data không liên quan | Blocker | [ ] |
| RC-26 | Thay đổi cấu hình rule thành công hoặc thất bại do vi phạm ràng buộc phải được báo về log hệ thống để giám sát lỗi | Minor | [ ] |

## 7. Xử lý lỗi

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-27 | Khi người dùng nhập giá trị không hợp lệ (ví dụ: nhập số âm cho số trận thua tối đa), hệ thống từ chối lưu và hiển thị thông báo lỗi chi tiết | Major | [x] |
| RC-28 | Lỗi mất kết nối mạng hoặc lỗi server khi nhấn Save không làm mất đi các giá trị tạm thời đang hiển thị trên form | Blocker | [x] |
| RC-29 | Trường hợp DB trả lỗi trùng lặp ràng buộc UNIQUE `(user_id, rule_type)` được API xử lý êm dịu, không gây sập ứng dụng | Major | [x] |
| RC-30 | Người dùng nhận được thông báo lỗi Việt hóa dễ hiểu qua tệp `message.ts`, không nhận stack trace lỗi kỹ thuật từ backend | Major | [x] |

## 8. Kiểm thử

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-31 | Unit test bao phủ tính năng tự động tạo (seeding) bộ luật mặc định cho người dùng mới đăng ký | Major | [x] |
| RC-32 | Unit test bao phủ các biên giá trị hợp lệ/không hợp lệ của `max_risk_per_trade` (0 đến 100), `max_fomo_score` (1 đến 10), v.v. | Major | [x] |
| RC-33 | Unit test bao phủ cơ chế xác thực quyền sở hữu rule (ngăn chặn User A chỉnh sửa rule của User B) | Major | [x] |
| RC-34 | Integration/E2E test luồng hoạt động: Bật rule -> Chỉnh sửa giá trị -> Chạy Pre-trade check để xác nhận cảnh báo kích hoạt đúng tham số mới | Major | [x] |
| RC-35 | Kiểm tra trực quan (Visual check) hiệu ứng hover thay đổi viền thẻ rule, hoạt động chính xác của nút gạt Switch, và việc xuất hiện thông báo Success Toast khi lưu thành công | Major | [x] |

## 9. Vận hành

| #     | Hạng mục | Mức độ | Trạng thái |
| ----- | -------- | ------ | ---------- |
| RC-36 | Quy trình thiết lập lại (Reset) bộ luật về trạng thái mặc định của hệ thống được chuẩn bị | Minor | [ ] |
| RC-37 | Các cảnh báo/thông điệp Disclaimer tuyên bố miễn trừ trách nhiệm xuất hiện đầy đủ ở banner đầu trang Trading Rules | Blocker | [x] |
| RC-38 | Nút "Discard Changes" hoạt động chính xác, hoàn trả lại cấu hình cũ trên UI nếu người dùng chưa nhấn Save | Major | [x] |
| RC-39 | Tương tác trạng thái (Micro-interactions) của nút lưu hiển thị trạng thái đang xử lý và hiển thị Toast thông báo thành công đồng bộ hóa | Major | [x] |

---

## Bảng ánh xạ AC → Checklist items

| #   | AC | Các hạng mục checklist xác nhận |
| --- | -- | ------------------------------- |
| 1   | AC-RULES-1/v1 (Xem danh sách rule cá nhân) | RC-01, RC-05, RC-08, RC-10, RC-37 |
| 2   | AC-RULES-2/v1 (Bật/tắt trạng thái hoạt động) | RC-01, RC-04, RC-08, RC-16, RC-22, RC-34, RC-35, RC-38, RC-39 |
| 3   | AC-RULES-3/v1 (Chỉnh sửa giá trị rule hợp lệ) | RC-01, RC-04, RC-08, RC-09, RC-11, RC-17, RC-18, RC-32, RC-34, RC-35, RC-38, RC-39 |
| 4   | AC-RULES-4/v1 (Từ chối giá trị không hợp lệ) | RC-01, RC-11, RC-17, RC-27, RC-28, RC-30, RC-32 |
| 5   | AC-RULES-5/v1 (Quy tắc không là tín hiệu khuyên mua/bán) | RC-01, RC-02, RC-37 |
