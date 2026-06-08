from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TradeMind AI API"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    OPENROUTER_API_KEY: str = "dummy_key"
    OPENROUTER_MODEL: str = "google/gemma-4-31b-it:free"

    @property
    def sqlalchemy_database_url(self) -> str:
        # Resolve Vercel/Neon postgres:// to postgresql:// format for SQLAlchemy compatibility
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
