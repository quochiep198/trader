class MessageProperties:
    EMAIL_ALREADY_REGISTERED = "Địa chỉ email này đã được đăng ký trong hệ thống"
    INVALID_CREDENTIALS = "Mật khẩu hoặc email không chính xác"
    REGISTER_SUCCESS = "Đăng ký tài khoản thành công! Vui lòng sử dụng thông tin này để đăng nhập."
    
    # Auth & API Credentials
    COULD_NOT_VALIDATE_CREDENTIALS = "Không thể xác thực thông tin đăng nhập"
    USER_NOT_FOUND = "Người dùng không tồn tại"

    # Rules Feature Messages
    RULE_NOT_FOUND = "Không tìm thấy quy tắc giao dịch hoặc không có quyền truy cập"
    RULE_VALUE_INVALID = "Giá trị quy tắc không hợp lệ cho loại luật này"
    RULE_UPDATE_SUCCESS = "Cập nhật giá trị quy tắc thành công"
    RULE_TOGGLE_SUCCESS = "Thay đổi trạng thái hoạt động quy tắc thành công"

    # Pre-trade Check Messages
    TRADE_CHECK_LOG_NOT_FOUND = "Không tìm thấy nhật ký phân tích hoặc không có quyền truy cập"
    TRADE_CHECK_ACKNOWLEDGE_SUCCESS = "Xác nhận kỷ luật thành công, bạn có thể tiếp tục giao dịch"
    TRADE_CHECK_ACKNOWLEDGE_MIN_LEN = "Câu trả lời phản tỉnh phải có độ dài tối thiểu 10 ký tự"
    TRADE_CHECK_INVALID_SL_TP = "Giá trị Stop-loss hoặc Take-profit không hợp lý"

