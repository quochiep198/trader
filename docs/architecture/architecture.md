# Kiến trúc hệ thống: TradeMind AI MVP (architecture.md)

Tài liệu này đặc tả kiến trúc phần mềm, cấu trúc thư mục dự án (Monorepo), thiết kế luồng dữ liệu, và phương án tích hợp kỹ thuật giữa FastAPI (Backend), React/Vite (Frontend), và OpenRouter (AI), kết hợp với kế hoạch triển khai hạ tầng đám mây (Deployment Setup).

---

## 1. Sơ đồ kiến trúc & Hạ tầng triển khai (System & Deployment Architecture)

MVP được triển khai trên môi trường đám mây phân tán để tối ưu chi phí (sử dụng các gói miễn phí/tiết kiệm) và tăng tính linh hoạt:

```mermaid
flowchart TD
    subgraph Client [Vercel Hosting]
        ReactApp[React + Vite Frontend]
    end

    subgraph Server [Hugging Face Spaces - Docker / Python]
        FastAPI[FastAPI Backend]
        RiskCalc[Risk Calculator]
        RuleEng[Rule Engine]
    end

    subgraph DataStore [Neon Serverless Database]
        PostgreSQL[(Neon PostgreSQL DB)]
    end

    subgraph ExternalService [AI Provider]
        OpenRouter[OpenRouter AI Free Tier]
    end

    ReactApp <=>|HTTPS API Requests + JWT Token| FastAPI
    FastAPI <=>|SQLAlchemy Conn String| PostgreSQL
    FastAPI -->|Logic nội bộ| RiskCalc
    FastAPI -->|Logic nội bộ| RuleEng
    FastAPI <=>|HTTPS API + API Key| OpenRouter
```

### Phương án triển khai hạ tầng (Deployment Setup):
1.  **Frontend (React + Vite):** Deploy lên **Vercel** (hỗ trợ CI/CD tự động từ GitHub, tối ưu hóa phân phối nội dung tĩnh).
2.  **Backend (FastAPI):** Deploy lên **Hugging Face Spaces** (chạy dưới dạng Docker Space hoặc Python Space). Cần cấu hình mở CORS để cho phép Frontend từ Vercel gọi API.
3.  **Database (Neon PostgreSQL):** Sử dụng cơ sở dữ liệu serverless **Neon** (nằm trong hệ sinh thái của Vercel), cung cấp URL kết nối Postgres dạng serverless tự động co giãn.

> [!IMPORTANT]
> **Cấu hình CORS (Cross-Origin Resource Sharing):**
> Do Frontend nằm trên tên miền của Vercel (`*.vercel.app`) và Backend nằm trên tên miền của Hugging Face (`*.hf.space`), Backend FastAPI bắt buộc phải cấu hình `CORSMiddleware` cho phép Origin của Frontend truy cập để tránh lỗi bảo mật trình duyệt.

---

## 2. Cấu trúc thư mục dự án (Monorepo Layout)

Dự án được tổ chức dưới dạng Monorepo để dễ dàng quản lý mã nguồn ở cả 2 đầu Backend và Frontend:

```text
trademind-ai/
│
├── backend/                  # Cấu trúc mã nguồn FastAPI (Python)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # Điểm chạy ứng dụng FastAPI & Cấu hình CORS
│   │   │
│   │   ├── core/             # Cấu hình hệ thống, bảo mật, kết nối DB
│   │   │   ├── config.py     # Đọc biến môi trường (.env)
│   │   │   ├── database.py   # Kết nối Neon PostgreSQL via SQLAlchemy
│   │   │   ├── security.py   # Hashing password, JWT token helper
│   │   │   └── messages.py   # Quản lý tập trung các thông báo lỗi và thành công
│   │   │
│   │   ├── models/           # Khai báo cấu trúc bảng Database (ORM models)
│   │   │   ├── user.py
│   │   │   ├── rule.py
│   │   │   ├── trade.py
│   │   │   ├── emotion_log.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/          # Khai báo cấu trúc DTO / Validation (Pydantic)
│   │   │   ├── user_schema.py
│   │   │   ├── rule_schema.py
│   │   │   └── trade_schema.py
│   │   │
│   │   ├── api/              # Khai báo các API Endpoints (Router v1)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── profile.py
│   │   │   ├── rules.py
│   │   │   ├── trades.py
│   │   │   └── reports.py
│   │   │
│   │   ├── services/         # Thư mục chứa Logic nghiệp vụ cốt lõi
│   │   │   ├── ai_service.py      # Client gọi OpenRouter API
│   │   │   ├── risk_calculator.py # Tính rủi ro toán học
│   │   │   ├── rule_engine.py     # Check vi phạm rules
│   │   │   └── report_service.py  # Gom dữ liệu & tổng hợp báo cáo tuần
│   │   │
│   │   └── tasks/            # Cronjob và Worker chạy nền
│   │       └── retention_worker.py  # Xóa raw AI response định kỳ
│   │
│   ├── Dockerfile            # Cần thiết để chạy Docker Space trên Hugging Face
│   ├── requirements.txt      # Khai báo thư viện Backend
│   └── .env.example          # File cấu hình môi trường mẫu
│
├── frontend/                 # Cấu trúc mã nguồn React + Vite (TypeScript)
│   ├── public/               # Ảnh và assets tĩnh
│   ├── src/
│   │   ├── main.tsx          # Điểm khởi động ứng dụng React
│   │   ├── App.tsx           # Router chính & Layout wrapper
│   │   │
│   │   ├── components/       # Các UI Components dùng chung (reusable)
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Sidebar.tsx
│   │   │
│   │   ├── context/          # Quản lý Global State (React Context)
│   │   │   └── AuthContext.tsx    # Lưu trữ trạng thái đăng nhập, JWT token
│   │   │
│   │   ├── pages/            # Các trang màn hình chính
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Profile.tsx
│   │   │   ├── PersonalRules.tsx
│   │   │   ├── PreTradeCheck.tsx
│   │   │   ├── AnalysisResult.tsx
│   │   │   ├── TradeJournal.tsx
│   │   │   └── WeeklyReport.tsx
│   │   │
│   │   ├── services/         # Kết nối API
│   │   │   └── api.ts        # Axios client kết nối endpoint Hugging Face
│   │   │
│   │   └── styles/           # Styling hệ thống
│   │       └── css/          # Thư mục lưu trữ tập trung tất cả các tệp tin .css và .module.css
│   │           ├── variables.css # Mã màu, HSL colors, CSS variables
│   │           ├── global.css    # Typography, Reset CSS, UTs
│   │           ├── App.css       # Style chính của App
│   │           ├── index.css     # Điểm import các styles toàn cục
│   │           └── *.module.css  # Các file CSS Module cho các components & pages
│   │
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
```

---

## 3. Cấu hình CORS & Deploy trên Hugging Face Spaces

Để ứng dụng chạy mượt mà trên Hugging Face Spaces và kết nối được với Frontend Vercel, file `app/main.py` cần cấu hình CORS như sau:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import settings

app = FastAPI(title="TradeMind AI API")

# Cấu hình CORS Origins cho phép Vercel gọi API
origins = [
    "http://localhost:5173", # Cho môi trường Dev Frontend
    "https://trademind-ai.vercel.app", # URL Frontend Production trên Vercel
    # Thêm các subdomains vercel nếu cần để phục vụ test preview
    "https://*-trademind-ai.vercel.app", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*-trademind-ai\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
```

---

## 4. Kết nối Database Neon (PostgreSQL)

Neon PostgreSQL cung cấp connection string tựa như:
`postgresql://[user]:[password]@[neon-host]/[dbname]?sslmode=require`

File `app/core/database.py` sẽ cấu hình SQLAlchemy Session Engine kết nối trực tiếp đến Neon:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Bắt buộc bật sslmode=require khi kết nối Neon DB để bảo mật đường truyền
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL, 
    pool_size=5, 
    max_overflow=10,
    pool_pre_ping=True # Giúp tự phục hồi kết nối nếu Neon DB chuyển sang chế độ ngủ (Idle)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 5. Tích hợp AI OpenRouter (OpenRouter Integration)

### 5.1 Các Model AI Free khuyên dùng cho Tiếng Việt:
1.  `google/gemma-2-9b-it:free` (Model Gemma 2 cực mạnh về xử lý tiếng Việt, tư duy logic).
2.  `meta-llama/llama-3-8b-instruct:free` (Llama 3 tốc độ phản hồi nhanh, hoạt động ổn định).

### 5.2 Mã nguồn mẫu Backend gọi OpenRouter (`app/services/ai_service.py`):

Sử dụng thư viện `httpx` (hoặc thư viện `openai` SDK cấu hình custom `base_url`) để gọi OpenRouter:

```python
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

class AIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.OPENROUTER_MODEL  # Ví dụ: "google/gemma-2-9b-it:free"

    async def analyze_emotion(self, reason: str, emotion_text: str) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://trademind-ai.vercel.app", # URL Frontend của bạn
            "X-Title": "TradeMind AI MVP"
        }

        # Prompt thiết kế trả về JSON có cấu trúc (Structured Output)
        prompt_system = (
            "Bạn là AI Coach kỷ luật giao dịch chứng khoán bằng tiếng Việt. "
            "Phân tích lý do và cảm xúc của trader để tìm FOMO, Panic, Revenge, Greed, Hesitation, Overconfidence (thang điểm 0-10). "
            "Trả về kết quả dưới định dạng JSON duy nhất, tuyệt đối không giải thích thêm ngoài JSON."
        )

        prompt_user = (
            f"Lý do giao dịch: {reason}\n"
            f"Cảm xúc mô tả: {emotion_text}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }

        try:
            async with httpx.AsyncClient(timeout=4.5) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    json_str = data["choices"][0]["message"]["content"]
                    import json
                    return json.loads(json_str)
                else:
                    print(f"OpenRouter Error Status: {response.status_code}, Body: {response.text}")
                    return None
        except Exception as e:
            print(f"OpenRouter Connection Exception: {str(e)}")
            return None
```

---

## 6. Quy chuẩn viết code Backend & Frontend (Coding Conventions)

### 6.1 Quản lý tập trung thông điệp Backend (Centralized Message Management)
- **Quy tắc cứng:** Tất cả các câu thông báo văn bản trả về cho Client (bao gồm thông báo lỗi `detail` của `HTTPException` hoặc thông báo thành công `message` của JSON response) **tuyệt đối không được viết chuỗi tĩnh (hardcode string)** trực tiếp trong file router hay các tầng nghiệp vụ logic khác.
- **Giải pháp:** Tất cả các thông điệp phải được tập trung khai báo dưới dạng hằng số lớp (class constants) trong tệp [messages.py](file:///d:/Traider/backend/app/core/messages.py) thuộc lớp `MessageProperties`. Các Router/Logic sẽ import lớp này để sử dụng nhằm dễ dàng chỉnh sửa, dịch thuật hoặc bảo trì.
- **Ví dụ mẫu sử dụng:**
```python
# Trong file app/core/messages.py
class MessageProperties:
    INVALID_CREDENTIALS = "Mật khẩu hoặc email không chính xác"

# Trong file app/api/auth.py
from app.core.messages import MessageProperties

raise HTTPException(
    status_code=400,
    detail=MessageProperties.INVALID_CREDENTIALS
)
```

### 6.2 Quản lý bảo mật Token JWT Frontend
- **Quy tắc:** Mã token xác thực phiên JWT (`access_token`) bắt buộc phải được lưu trữ trong **Cookie** thay vì `localStorage` để tăng tính bảo mật (hạn chế nguy cơ tấn công XSS đánh cắp token).
- **Giải pháp:** Toàn bộ logic lưu trữ, đọc và xóa Cookie/localStorage được đóng gói tập trung trong [AuthContext.tsx](file:///d:/Traider/frontend/src/context/AuthContext.tsx) và được gọi thông qua hook `useAuth()`. Frontend Client không được can thiệp trực tiếp đến `document.cookie` bên ngoài context này.

### 6.3 Quản lý tập trung nội dung hiển thị ở Frontend (Centralized Frontend Localization)
- **Quy tắc cứng:** Tất cả các chuỗi văn bản hiển thị trên giao diện người dùng có tiếng Việt (bao gồm nhãn label, placeholder, nút bấm, thông báo, cảnh báo lỗi, mô tả và điều khoản từ chối trách nhiệm pháp lý...) **tuyệt đối không được viết chuỗi tĩnh (hardcode string)** trực tiếp trong mã nguồn các component hay trang giao diện.
- **Giải pháp:** Toàn bộ các chuỗi nội dung hiển thị này phải được tập trung khai báo làm thuộc tính của đối tượng `MessageProperties` trong tệp [message.ts](file:///d:/Traider/frontend/src/services/message.ts). Các component sẽ import và sử dụng chúng thay cho chuỗi text tĩnh để thuận tiện cho việc chỉnh sửa và mở rộng quốc tế hóa (i18n).
- **Ví dụ mẫu sử dụng:**
```typescript
// Trong file frontend/src/services/message.ts
export const MessageProperties = {
  LOGIN_EMAIL_LABEL: "Địa chỉ Email",
};

// Trong file frontend/src/pages/Login.tsx
import { MessageProperties } from '../services/message';

// Sử dụng trong JSX:
<label htmlFor="email">{MessageProperties.LOGIN_EMAIL_LABEL}</label>
```

### 6.4 Quy chuẩn quản lý tệp tin CSS và CSS Modules (CSS File Management)
- **Quy tắc cứng:** Tất cả các tệp tin có phần mở rộng `.css` (bao gồm tệp cấu hình biến CSS toàn cục, CSS Reset, và tất cả các tệp CSS Modules có đuôi `.module.css` phục vụ riêng cho các component hoặc trang giao diện) **tuyệt đối không được đặt rải rác** bên cạnh tệp `.tsx` trong thư mục `src/components` hay `src/pages`.
- **Giải pháp:** Tất cả các tệp tin `.css` và `.module.css` bắt buộc phải được tập trung lưu trữ thống nhất bên trong thư mục [src/styles/css/](file:///d:/Traider/frontend/src/styles/css/). Các file component và page sẽ thực hiện import tương quan (relative import) từ thư mục này để đảm bảo kiến trúc sạch sẽ và dễ quản lý.
- **Ví dụ mẫu sử dụng:**
```typescript
// Trong tệp tin frontend/src/components/Button.tsx
import styles from '../styles/css/Button.module.css';
```



