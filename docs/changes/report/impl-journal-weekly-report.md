# Kế hoạch triển khai: Trade Journal & Weekly Report (impl-journal-weekly-report)

Kế hoạch này chi tiết hóa cách thức xây dựng Nhật ký giao dịch (Trade Journal), cơ chế tổng hợp Báo cáo tuần (Weekly Report) tự động và thiết lập chính sách lưu trữ (Retention) cùng Nhật ký kiểm toán (Audit Logs) cho TradeMind AI MVP.

---

## 1. Mục tiêu chức năng

### 1.1 Trade Journal
*   Lưu trữ thông tin lệnh giao dịch kèm theo điểm số kỷ luật, điểm cảm xúc, danh sách vi phạm từ Pre-trade Check.
*   **Vòng đời của lệnh (Lifecycle):** Người dùng có thể đánh dấu lệnh là đã vào thực tế (`opened`), cập nhật kết quả lời/lỗ khi đóng lệnh (`closed`), hoặc hủy bản ghi (`cancelled`).
*   **Lọc dữ liệu:** Hỗ trợ lọc danh sách nhật ký theo Symbol, Cảm xúc chính, Kết quả (lời/lỗ), Luật vi phạm và Khoảng ngày.
*   **Nhập thủ công:** Chỉ hỗ trợ nhập tay thông tin lệnh hoặc lưu trực tiếp sau check. Không hỗ trợ import file CSV.

### 1.2 Weekly Report
*   Tổng hợp định kỳ kết quả giao dịch và mức độ kỷ luật của người dùng theo tuần calendar.
*   Thời gian tuần: **Thứ Hai 00:00:00 đến Chủ Nhật 23:59:59** (Múi giờ `Asia/Ho_Chi_Minh`).
*   Gom dữ liệu theo trường `created_at` của trade.
*   **Chỉ số thống kê:**
    *   Tổng số giao dịch được tạo trong tuần (gồm tất cả các trạng thái).
    *   Tỉ lệ thắng/thua (Win/Loss Ratio) - *chỉ tính trên các trade có trạng thái `closed`*.
    *   Điểm kỷ luật trung bình (Discipline Score Average).
    *   Cảm xúc xuất hiện nhiều nhất (Most common emotion) và Luật vi phạm nhiều nhất (Most common violation).
    *   Đếm số lượng trade có dấu hiệu cảm xúc cao: `fomo_trades_count`, `revenge_trades_count`, `panic_trades_count` (điểm tương ứng >= 8).

### 1.3 Data Retention & Audit Logs
*   Thực hiện xóa/anonymize phản hồi thô của AI (`raw_ai_response`) sau 30 ngày.
*   Ghi audit log các thao tác quan trọng để debug và phục vụ rủi ro pháp lý.

---

## 2. Thiết kế dữ liệu (Database Schema)

### 2.1 Bảng `trades` (Trade Journal)
```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Chi tiết lệnh
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL, -- 'BUY' hoặc 'SELL' (SELL_TO_CLOSE)
    entry_price DECIMAL(18, 2) NOT NULL,
    exit_price DECIMAL(18, 2) NULL,
    quantity INT NOT NULL,
    stop_loss DECIMAL(18, 2) NULL,
    take_profit DECIMAL(18, 2) NULL,
    reason TEXT NOT NULL,
    emotion_text TEXT NOT NULL,
    
    -- Trạng thái vòng đời
    status VARCHAR(20) NOT NULL DEFAULT 'planned', -- 'planned', 'opened', 'closed', 'cancelled'
    
    -- Kết quả đóng lệnh
    profit_loss_amount DECIMAL(18, 2) NULL,
    profit_loss_percent DECIMAL(5, 2) NULL,
    
    -- Kết quả phân tích (kết nối với logs)
    discipline_score INT NOT NULL,
    had_cooldown BOOLEAN NOT NULL DEFAULT FALSE,
    
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL
);
```

### 2.2 Bảng `audit_logs` (Nhật ký kiểm toán)
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL, -- 'LOGIN', 'CREATE_RULE', 'UPDATE_RULE', 'CREATE_TRADE', 'CLOSE_TRADE', 'GENERATE_REPORT', 'DELETE_ACCOUNT'
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    metadata JSONB NULL, -- Lưu trữ thông tin kỹ thuật không nhạy cảm (ví dụ: {"rule_id": "...", "trade_id": "..."})
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Các API Endpoints cần xây dựng

| Phương thức | Path | Body / Payload | Mô tả |
|-------------|------|----------------|-------|
| `POST` | `/api/trades` | `{ "symbol": "...", ..., "discipline_score": 85 }` | Tạo mới một bản ghi journal (thường gọi sau khi check lệnh thành công và user bấm Save) |
| `GET` | `/api/trades` | Query params: `symbol`, `emotion`, `status`, `start_date`, `end_date` | Lấy danh sách journal có phân trang và bộ lọc |
| `GET` | `/api/trades/:id` | Không | Lấy thông tin chi tiết một bản ghi nhật ký |
| `PUT` | `/api/trades/:id/outcome` | `{ "exit_price": 29500, "status": "closed", "profit_loss_amount": 1000000, "profit_loss_percent": 3.5, "notes": "..." }` | Cập nhật kết quả khi đóng lệnh |
| `PUT` | `/api/trades/:id/cancel` | Không | Đổi trạng thái lệnh sang `cancelled` |
| `GET` | `/api/weekly-report` | Query params: `date` | Lấy dữ liệu báo cáo tuần chứa ngày được chọn |

---

## 4. Các luồng xử lý chi tiết (Business Logic Flow)

### 4.1 Tính toán Báo cáo tuần (Weekly Report Engine)
Khi người dùng truy cập trang Weekly Report:
1.  Backend xác định khoảng thời gian tuần (Thứ Hai 00:00:00 đến Chủ Nhật 23:59:59) chứa ngày được yêu cầu. Múi giờ mặc định sử dụng là `Asia/Ho_Chi_Minh`.
2.  Query danh sách các trade thuộc `user_id` hiện tại có `created_at` nằm trong khoảng thời gian trên.
3.  **Nếu danh sách rỗng:** Trả về trạng thái **Empty State** lập tức, không bịa số liệu hay tính toán.
4.  **Nếu có dữ liệu:**
    *   `total_trades` = Count tất cả bản ghi tìm thấy.
    *   Lọc các bản ghi có `status = 'closed'`: tính tổng số trade win (P/L > 0) và trade loss (P/L < 0) để tính tỉ lệ.
    *   Tính trung bình cộng cột `discipline_score`.
    *   Gom nhóm các `emotion_tags` và `rule_violations` liên kết để tìm ra cảm xúc xuất hiện nhiều nhất và luật bị vi phạm nhiều nhất.
    *   Đếm số lượng trade có điểm cảm xúc FOMO, Revenge, Panic tương ứng `>= 8` từ bảng liên kết `emotion_logs`.
5.  Gọi LLM (hoặc template rule-based) sinh ra lời khuyên kỷ luật cá nhân (Insights/Recommendations) dựa trên các số liệu thống kê ở trên. Đảm bảo prompt AI cho report tuân thủ nghiêm ngặt disclaimer và guardrail (Không khuyến nghị cổ phiếu).

### 4.2 Xử lý định kỳ xóa dữ liệu AI (Data Retention Worker)
*   Thiết lập một cron job chạy hàng ngày vào lúc 02:00 sáng.
*   Thực hiện câu lệnh SQL xóa nội dung trường `raw_ai_response` của các bản ghi trong bảng `emotion_logs` có `created_at` < `CURRENT_DATE - INTERVAL '30 days'`.

---

## 5. Các trạng thái giao diện UI cần thiết kế

1.  **Trang danh sách Trade Journal:**
    *   Thanh bộ lọc phía trên (Symbols, Emtoion tag dropdown, Status, Date Picker).
    *   Bảng hiển thị danh sách nhật ký rõ ràng. Cột điểm kỷ luật hiển thị màu sắc sinh động (Xanh, Vàng, Đỏ).
    *   Nút "Cập nhật kết quả" hiển thị inline đối với các trade có status `opened`. Khi click mở ra Form cập nhật giá đóng lệnh và ghi chú kết quả.
2.  **Trang Weekly Report:**
    *   Hiển thị thông số tổng hợp dạng thẻ (KPI Cards).
    *   Hiển thị biểu đồ tròn tỉ lệ thắng thua (chỉ vẽ từ trade `closed`).
    *   Khu vực Insights & Coach khuyên bảo được trình bày trang trọng, định dạng rõ ràng, kèm disclaimer bắt buộc ở cuối trang.
3.  **Trạng thái Empty State của Báo cáo:** Hình ảnh minh họa nhẹ nhàng kèm dòng chữ *"Tuần này chưa có giao dịch nào được lưu. Hãy kiểm tra lệnh mới để tích lũy dữ liệu."*

---

## 6. Kế hoạch kiểm thử (Verification Plan)

### 6.1 Unit Tests (Kiểm thử đơn vị)
*   `test_weekly_report_empty_state`: Đảm bảo nếu tuần đó user không tạo trade nào, API trả về JSON chứa empty flag và không tính toán số liệu giả.
*   `test_weekly_report_win_loss_calculation`: Đảm bảo tỉ lệ win/loss chỉ tính trên các trade có trạng thái `closed`. Trade ở trạng thái `planned` hoặc `cancelled` không được đưa vào tử số và mẫu số của tỷ lệ này.

### 6.2 Integration Tests
*   `test_timezone_boundary_weekly_report`: Tạo 1 trade lúc 23:59:50 Chủ Nhật và 1 trade lúc 00:00:10 Thứ Hai (theo múi giờ Việt Nam). Đảm bảo hệ thống phân tách chính xác 2 trade này vào 2 tuần báo cáo khác nhau.
*   `test_retention_policy_execution`: Chạy trigger cron worker xóa dữ liệu và kiểm tra DB xem các trường `raw_ai_response` của các log > 30 ngày đã thực sự chuyển thành `NULL` hoặc được anonymize chưa.
