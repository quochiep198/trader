import json
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.OPENROUTER_MODEL

    async def analyze_emotion(self, reason: str, emotion_text: str, market_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if not self.api_key or self.api_key == "dummy_key":
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://trademind-ai.vercel.app",
            "X-Title": "TradeMind AI MVP"
        }

        prompt_system = (
            "Bạn là AI Trading Discipline Coach cho sản phẩm TradeMind AI.\n"
            "Nhiệm vụ của bạn:\n"
            "- Phân tích cảm xúc và rủi ro hành vi trong bối cảnh người dùng đang cân nhắc giao dịch chứng khoán.\n"
            "- Phối hợp thông tin tâm lý của người dùng với Bối cảnh thị trường (Market Context) nếu có để đưa ra những phân tích sâu sát (ví dụ: đang FOMO mà giá lại đang tăng mạnh liên tiếp nhiều phiên, hoặc đang hoảng loạn Panic mà giá đang rơi sâu).\n"
            "- Phát hiện các trạng thái cảm xúc chính (FOMO, Panic, Revenge trading, Overconfidence, Greed, Hesitation) và chấm điểm thang 0-10 cho mỗi trạng thái.\n"
            "- Trả về kết quả dưới định dạng JSON duy nhất, tuyệt đối không giải thích thêm, không bọc trong markdown code block (như ```json).\n"
            "\n"
            "Yêu cầu Schema JSON trả về:\n"
            "{\n"
            "  \"emotion_tags\": [\"FOMO\", \"Urgency\"],\n"
            "  \"fomo_score\": 8,\n"
            "  \"panic_score\": 1,\n"
            "  \"revenge_score\": 0,\n"
            "  \"overconfidence_score\": 4,\n"
            "  \"greed_score\": 3,\n"
            "  \"hesitation_score\": 1,\n"
            "  \"discipline_risk\": \"high\",\n"
            "  \"should_cooldown\": true,\n"
            "  \"reason\": \"Tóm tắt lý do cảm xúc của user bằng tiếng Việt\",\n"
            "  \"coach_message\": \"Lời khuyên kỷ luật bằng tiếng Việt kết hợp phân tích bối cảnh giá nếu có\",\n"
            "  \"reflection_question\": \"Câu hỏi tự phản tỉnh bằng tiếng Việt (bắt buộc nếu should_cooldown=true, ngược lại để null)\"\n"
            "}\n"
            "\n"
            "Giới hạn bắt buộc (Guardrails):\n"
            "- Không được khuyến nghị mua, bán hoặc nắm giữ bất kỳ mã chứng khoán nào.\n"
            "- Không được dự đoán chắc chắn giá tăng/giảm.\n"
            "- Không được cam kết lợi nhuận hoặc giảm lỗ.\n"
            "- Không được khuyến khích all-in, gỡ lỗ, hoặc giao dịch bằng mọi giá.\n"
            "- Không được dùng ngôn ngữ khiến người dùng hiểu rằng đây là tư vấn đầu tư."
        )

        prompt_user = (
            f"Lý do giao dịch: {reason}\n"
            f"Cảm xúc mô tả: {emotion_text}"
        )

        if market_context:
            prompt_user += (
                f"\n\nBối cảnh thị trường (Market Context):\n"
                f"- Giá hiện tại: {market_context.get('current_price')} VND\n"
                f"- Biến động giá 3 ngày qua: {market_context.get('price_change_3d', 0)}%\n"
                f"- Số phiên tăng liên tục: {market_context.get('consecutive_up_sessions', 0)} phiên\n"
                f"- Số phiên giảm liên tục: {market_context.get('consecutive_down_sessions', 0)} phiên\n"
                f"- Khối lượng giao dịch so với TB 20 ngày: {market_context.get('volume_vs_20d_avg', 1.0)}x\n"
                f"- Độ lệch giá hiện tại so với entry kế hoạch: {market_context.get('current_vs_entry_percent', 0)}%\n"
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": 1000
        }

        models_to_try = [self.model, "liquid/lfm-2.5-1.2b-instruct:free", "openrouter/free"]
        # Remove duplicates while preserving order
        models_to_try = list(dict.fromkeys(m for m in models_to_try if m))

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                for model_name in models_to_try:
                    payload["model"] = model_name
                    print(f"Trying OpenRouter with model: {model_name}...")
                    try:
                        response = await client.post(self.api_url, headers=headers, json=payload)
                        if response.status_code == 200:
                            data = response.json()
                            content = data["choices"][0]["message"]["content"].strip()
                            # Clean markdown code fences if returned
                            if content.startswith("```"):
                                lines = content.splitlines()
                                if lines[0].startswith("```"):
                                    lines = lines[1:]
                                if lines[-1].startswith("```"):
                                    lines = lines[:-1]
                                content = "\n".join(lines).strip()
                            parsed = json.loads(content)
                            print(f"Successfully retrieved AI response using model: {model_name}")
                            return parsed
                        else:
                            print(f"OpenRouter error for model {model_name} (Status {response.status_code}): {response.text}")
                    except Exception as model_err:
                        print(f"OpenRouter exception for model {model_name}: {str(model_err)}")
                
                # If all models failed
                return None
        except Exception as e:
            print(f"OpenRouter client exception: {str(e)}")
            return None
