# Danh sách tài liệu đặc tả chi tiết các chức năng (TradeMind AI - MVP Specs)

Thư mục này chứa toàn bộ các đặc tả chức năng chi tiết được phân tách từ tài liệu đặc tả tổng hợp [spec-pack.md](file:///d:/Traider/spec-pack.md).

## Danh mục tài liệu đặc tả theo chức năng:

1.  **[Authentication & User Profile Spec](file:///d:/Traider/specs/spec-auth-profile.md):** Yêu cầu nghiệp vụ, ma trận rule, giao diện, state transitions và tiêu chí chấp nhận cho đăng ký kích hoạt email, đăng nhập, quên mật khẩu và thiết lập profile tài chính.
2.  **[Personal Trading Rules Spec](file:///d:/Traider/specs/spec-personal-rules.md):** Chi tiết cấu hình luật cá nhân mặc định, quy tắc validation giá trị rule, toggle hoạt động và disclaimer nghiệp vụ.
3.  **[Pre-trade Check & AI Analysis Spec](file:///d:/Traider/specs/spec-pretrade-check-ai.md):** Đặc tả biểu mẫu phân tích trước lệnh, cấu trúc JSON thô của AI, logic xử lý Fallback khi AI lỗi, Prompt System, ranh giới AI Guardrails và bộ Golden Test Corpus.
4.  **[Risk Engine & Scoring Spec](file:///d:/Traider/specs/spec-risk-engine-score.md):** Công thức rủi ro BUY/SELL, Bộ máy Rule Engine, logic phát hiện lệnh quá cỡ (`prevent_oversized_trade`), công thức tính điểm Discipline Score và quy định Soft Cooldown.
5.  **[Trade Journal & Weekly Report Spec](file:///d:/Traider/specs/spec-journal-weekly-report.md):** Vòng đời bản ghi nhật ký, bộ lọc journal, thuật toán tổng hợp báo cáo tuần theo timezone Việt Nam, chính sách dữ liệu Retention và Audit Logs.

---
*Lưu ý: Các file đặc tả này đóng vai trò là "Nguồn tham chiếu duy nhất (Single Source of Truth)" cho từng module trong quá trình phát triển.*
