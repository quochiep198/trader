from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration to allow local Vite frontend calls
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginPayload(BaseModel):
    email: str
    password: str

@app.get("/")
def read_root():
    return {"message": "Welcome to TradeMind AI MVP API"}

@app.post(f"{settings.API_V1_STR}/auth/login")
def login(payload: LoginPayload):
    # Mock authentication matching spec requirements
    if payload.email == "demo@trademind.ai" and payload.password == "Password123":
        return {
            "access_token": "mock_jwt_token_for_demo",
            "token_type": "bearer",
            "user": {
                "name": "Demo Trader",
                "email": payload.email,
                "account_size": 100000000.0,
                "default_max_risk_per_trade": 2.0,
                "trading_style": "Swing",
                "experience_level": "Beginner"
            }
        }
    raise HTTPException(
        status_code=400, 
        detail="Mật khẩu hoặc email không chính xác"
    )
