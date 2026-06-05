from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Đăng ký các models ORM vào Base Metadata

# Tự động tạo cấu trúc bảng (như bảng users) trên Database (Neon/SQLite) khi chạy app
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"Database initialization warning: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Cấu hình CORS Origins cho phép Vercel và môi trường cục bộ gọi API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://trademind-ai.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.hf\.space|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to TradeMind AI MVP API"}

# Đăng ký router chính (ở thời điểm hiện tại chỉ chứa auth router phục vụ Login)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Khởi chạy background worker dọn dẹp log định kỳ (24h một lần)
import threading
import time
from app.tasks.retention_worker import cleanup_old_logs
from app.core.database import SessionLocal

def run_retention_worker():
    # Chờ 10 giây sau khi app khởi động để tránh xung đột DB
    time.sleep(10)
    while True:
        try:
            print("Running scheduled data retention cleanup task...")
            with SessionLocal() as db:
                cleanup_old_logs(db)
            print("Data retention cleanup completed successfully.")
        except Exception as e:
            print(f"Error in data retention worker: {e}")
        # Sleep 24 hours
        time.sleep(86400)

# Khởi tạo luồng chạy nền daemon
threading.Thread(target=run_retention_worker, daemon=True).start()
