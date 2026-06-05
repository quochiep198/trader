# Danh sách kế hoạch triển khai chi tiết các chức năng (TradeMind AI - MVP Implementation Plans)

Dưới đây là các kế hoạch triển khai chi tiết cho từng nhóm chức năng của dự án TradeMind AI MVP dựa trên bản đặc tả đã được thống nhất tại [spec-pack.md](file:///d:/Traider/spec-pack.md).

## Danh mục tài liệu kế hoạch:

1.  **[Authentication & User Profile](file:///d:/Traider/impl-plans/impl-auth-profile.md):** Quy trình đăng ký kích hoạt bằng Email Verification, Đăng nhập bảo mật, Quên mật khẩu và cấu hình Profile tài chính giao dịch (`account_size`, `max_risk_per_trade`).
2.  **[Personal Trading Rules](file:///d:/Traider/impl-plans/impl-personal-rules.md):** Quản lý bật/tắt (Toggle) và chỉnh sửa giá trị cho các quy tắc cá nhân mặc định (`require_stop_loss`, `max_fomo_score`, `max_consecutive_losses`, `prevent_oversized_trade`,...).
3.  **[Pre-trade Check & AI Analysis](file:///d:/Traider/impl-plans/impl-pretrade-check-ai.md):** Biểu mẫu phân tích trước khi vào lệnh, kết nối Gemini/OpenAI API phân tích cảm xúc (JSON Mode), thiết kế Prompt, xử lý AI Fallback và kiểm thử tự động bằng Golden Test Corpus 50 câu tiếng Việt.
4.  **[Risk Engine & Scoring](file:///d:/Traider/impl-plans/impl-risk-engine-score.md):** Các công thức tính toán toán học cho lệnh BUY/SELL, bộ máy kiểm thử luật (Rule Engine), quy tắc phát hiện lệnh quá cỡ (`prevent_oversized_trade`), công thức tính Discipline Score cố định tại Backend và cơ chế Soft Cooldown.
5.  **[Trade Journal & Weekly Report](file:///d:/Traider/impl-plans/impl-journal-weekly-report.md):** Nhật ký giao dịch (Trade Journal) và vòng đời của lệnh, Báo cáo tuần tổng hợp (Weekly Report) tự động theo múi giờ `Asia/Ho_Chi_Minh` (Thứ Hai - Chủ Nhật), chính sách Retention xóa AI thô sau 30 ngày và lưu Audit Logs.

---
*Lưu ý: Các kế hoạch trên được thiết kế để Dev và QA có thể tiến hành thiết kế hệ thống chi tiết và triển khai code độc lập hoặc song song.*
