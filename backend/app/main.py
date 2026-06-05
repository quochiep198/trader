from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Đăng ký các models ORM vào Base Metadata

# Tự động tạo cấu trúc bảng (như bảng users) trên Database (Neon/SQLite) khi chạy app
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Cấu hình CORS Origins cho phép Vercel gọi API theo kiến trúc quy định
origins = [
    "http://localhost:5173", # Cho môi trường Dev Frontend
    "http://127.0.0.1:5173", # Hỗ trợ chạy thử bằng IP cục bộ
    "https://trademind-ai.vercel.app", # URL Frontend Production trên Vercel
    "https://*-trademind-ai.vercel.app", # Thêm các subdomains vercel cho test preview
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*-trademind-ai\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to TradeMind AI MVP API"}

# Đăng ký router chính (ở thời điểm hiện tại chỉ chứa auth router phục vụ Login)
app.include_router(api_router, prefix=settings.API_V1_STR)
