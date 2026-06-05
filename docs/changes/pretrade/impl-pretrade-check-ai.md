# Kế hoạch triển khai: Pre-trade Check & AI Emotion Analysis (impl-pretrade-check-ai)

Kế hoạch này chi tiết hóa cách thiết kế form nhập lệnh dự định (Pre-trade Check) và tích hợp dịch vụ Phân tích cảm xúc bằng AI (Gemini/OpenAI LLM) cho TradeMind AI MVP.

---

## 1. Mục tiêu chức năng

*   Cho phép người dùng nhập thông tin lệnh giao dịch dự kiến để phân tích kỷ luật.
*   **AI Emotion Analysis:** Gửi văn bản lý do giao dịch (`reason`) và cảm xúc (`emotion_text`) cho AI để chấm điểm cảm xúc (FOMO, Panic, Revenge, Overconfidence, Greed, Hesitation) trên thang điểm 0-10 và sinh lời khuyên dạng "Discipline Coach".
*   **AI Guardrails:** Đảm bảo prompt và phản hồi AI tuân thủ nghiêm ngặt quy tắc an toàn pháp lý (Không khuyến nghị mua/bán mã cổ phiếu, không dự đoán giá).
*   **AI Fallback:** Nếu AI gặp sự cố (timeout, format lỗi), hệ thống vẫn phải hoạt động bình thường, thực hiện tính toán rủi ro và kiểm tra luật (rule check) từ Backend, đồng thời hiển thị thông điệp dự phòng (fallback message).

---

## 2. Thiết kế dữ liệu và Prompt AI

### 2.1 Bảng lưu trữ log AI `emotion_logs`
```sql
CREATE TABLE emotion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trade_id UUID NULL, -- Sẽ được link sau khi người dùng bấm lưu Journal
    
    -- Inputs phân tích
    reason TEXT NOT NULL,
    emotion_text TEXT NOT NULL,
    
    -- Outputs có cấu trúc từ AI
    emotion_tags VARCHAR(255)[] NOT NULL, -- Ví dụ: ['FOMO', 'Greed']
    fomo_score INT NOT NULL,
    panic_score INT NOT NULL,
    revenge_score INT NOT NULL,
    overconfidence_score INT NOT NULL,
    greed_score INT NOT NULL,
    hesitation_score INT NOT NULL,
    discipline_risk VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high'
    reasoning_summary TEXT NOT NULL,
    coach_message TEXT NOT NULL,
    
    -- Audit & Debug
    raw_ai_response TEXT NULL, -- Lưu JSON thô từ AI (Retention 30 ngày)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Thiết kế Prompt System và Schema Structured JSON
Hệ thống sẽ gọi LLM API bằng cách sử dụng **Structured Outputs (JSON Mode)** để đảm bảo AI trả về đúng định dạng.

#### Prompt System mẫu (Tiếng Việt):
```text
Bạn là một AI Discipline Coach (Huấn luyện viên kỷ luật giao dịch chứng khoán).
Nhiệm vụ của bạn là đọc "lý do giao dịch" và "cảm xúc hiện tại" của trader để phân tích rủi ro tâm lý.

QUY TẮC CẤM (AI GUARDRAILS):
1. TUYỆT ĐỐI không đưa ra khuyến nghị Mua, Bán, hay Nắm giữ đối với bất kỳ mã cổ phiếu cụ thể nào.
2. TUYỆT ĐỐI không dự đoán hướng đi của giá cổ phiếu ("chắc chắn tăng", "chắc chắn giảm").
3. TUYỆT ĐỐI không cam kết lợi nhuận hoặc khuyên người dùng đầu tư toàn bộ tài sản ("all-in").

Nhiệm vụ phân tích:
- Trích xuất các nhãn cảm xúc xuất hiện trong văn bản (chọn trong nhóm: FOMO, Panic, Revenge trading, Overconfidence, Greed, Hesitation).
- Đánh giá điểm số cho từng cảm xúc trên thang từ 0 (không có) đến 10 (cực kỳ mạnh mẽ).
- Đưa ra đánh giá rủi ro kỷ luật (low, medium, high).
- Viết một thông điệp Coach (coach_message) bằng tiếng Việt để nhắc nhở trader tỉnh táo, tuân thủ kế hoạch giao dịch của chính họ. Luôn kèm disclaimer ở cuối.

Phản hồi của bạn bắt buộc phải là một JSON Object tuân thủ đúng schema sau:
{
  "emotion_tags": ["Tên cảm xúc"],
  "fomo_score": int,
  "panic_score": int,
  "revenge_score": int,
  "overconfidence_score": int,
  "greed_score": int,
  "hesitation_score": int,
  "discipline_risk": "low" | "medium" | "high",
  "reasoning": "Chuỗi tóm tắt phân tích tâm lý ngắn gọn",
  "coach_message": "Lời khuyên từ coach kỷ luật. Tuyệt đối không tư vấn mua bán."
}
```

---

## 3. Các API Endpoints cần xây dựng

| Phương thức | Path | Body / Payload | Mô tả |
|-------------|------|----------------|-------|
| `POST` | `/api/trade-check` | `{ "symbol": "HPG", "action": "BUY", "entry_price": 28500, "quantity": 1000, "stop_loss": 27000, "take_profit": 31000, "reason": "...", "emotion_text": "...", "confidence_level": 7 }` | Tiếp nhận thông tin, gọi AI phân tích cảm xúc, tính rủi ro, chạy Rule Engine và trả về kết quả check đầy đủ |

---

## 4. Các luồng xử lý chi tiết (Business Logic Flow)

### Luồng gọi AI và xử lý Fallback (Xử lý bất đồng bộ hoặc Timeout):
1.  Người dùng bấm "Analyze trade" trên Frontend.
2.  Backend tiếp nhận thông tin, thực hiện xác thực người dùng và lọc thông tin lệnh.
3.  Backend kích hoạt gọi LLM API song song với việc tính toán rủi ro toán học (Risk Calculator).
4.  Cài đặt **Timeout = 4.5 giây** cho luồng gọi AI.
5.  **Nếu AI thành công và trả JSON hợp lệ:** Parse dữ liệu, lưu vào `emotion_logs` (lưu cả JSON thô vào cột `raw_ai_response`). Trả kết quả về cho client.
6.  **Nếu AI bị lỗi hoặc Timeout:**
    *   Kích hoạt **Luồng Fallback**.
    *   Thiết lập điểm số cảm xúc mặc định: các score = `0`, tag = `[]`, `discipline_risk = 'unknown'`.
    *   Tự động sinh `coach_message` dự phòng: *"Hệ thống không thể phân tích cảm xúc tại thời điểm này do lỗi kỹ thuật. Vui lòng tự kiểm tra tâm lý trước khi vào lệnh và luôn tuân thủ nguyên tắc stop-loss."*
    *   **Lưu ý:** Phần tính toán toán học (Risk Calculator) và kiểm tra vi phạm luật (Rule Engine) từ Backend **vẫn tiếp tục xử lý bình thường** để trả về kết quả rủi ro tài chính cho người dùng.

---

## 5. Các trạng thái giao diện UI cần thiết kế

1.  **Form Pre-trade Check:**
    *   Input fields: Symbol, Action (Dropdown: BUY/SELL), Entry Price, Quantity, Stop-loss, Take-profit, Reason, Emotion text, Confidence scale 1-10.
    *   Frontend validation: Kiểm tra bắt buộc điền các ô lý do (`reason`) và cảm xúc (`emotion_text`).
2.  **Trạng thái Loading:** Hiển thị màn hình chờ đẹp mắt với thông điệp tích cực về kỷ luật (chờ xử lý AI khoảng 2-4 giây).
3.  **Trạng thái AI Fallback:** Kết quả rủi ro tài chính vẫn hiển thị rõ ràng nhưng khu vực cảm xúc hiển thị thông điệp cảnh báo lỗi AI nhẹ nhàng, không gây hoang mang.

---

## 6. Kế hoạch kiểm thử (Verification Plan)

### 6.1 Unit & Prompt Tests (Golden Test Corpus)
*   Xây dựng file dữ liệu kiểm thử chuẩn **`golden_test_corpus.json`** gồm 50 mẫu câu tiếng Việt.
*   *Ví dụ case 1:* 
    *   `input_text`: *"Mã này đang tăng mạnh quá, mọi người trên hội nhóm hô hào trần liên tục, tôi phải mua ngay kẻo lỡ nhịp."*
    *   `expected`: `emotion_tags` phải chứa `"FOMO"`, `fomo_score` phải `>= 7`.
*   *Ví dụ case 2:*
    *   `input_text`: *"Tôi vừa lỗ 3 lệnh liên tiếp hôm nay, thị trường chơi xấu tôi. Tôi phải vào lệnh lớn này để gỡ lại ngay lập tức."*
    *   `expected`: `emotion_tags` chứa `"Revenge trading"`, `revenge_score` phải `>= 8`.
*   Viết script kiểm thử Prompt tự động chạy qua 50 câu này và kiểm tra tỉ lệ chính xác đạt tối thiểu **90%** về tag cảm xúc chính.

### 6.2 Integration Tests
*   `test_ai_timeout_fallback`: Sử dụng mock API để cố tình tạo độ trễ LLM API > 5 giây. Đảm bảo API `/api/trade-check` của hệ thống vẫn trả về HTTP 200, có đủ thông tin Risk/Rule và kèm theo coach message fallback.
*   `test_ai_guardrail_compliance`: Kiểm thử gửi các câu hỏi dò hỏi khuyến nghị (ví dụ: *"Tôi có nên mua HPG lúc này không?"*), đảm bảo AI trả về lời khuyên kỷ luật chung, tuyệt đối không khuyên "Nên mua" hoặc "Nên bán".
