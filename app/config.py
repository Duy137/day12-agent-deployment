from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Production-ready Agent"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    port: int = 8000
    host: str = "0.0.0.0"
    allowed_origins: list[str] = ["*"]
    
    redis_url: str = "redis://localhost:6379/0"
    agent_api_key: str = "my-super-secret-key-123"
    log_level: str = "INFO"
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    
    class Config:
        env_file = ".env"
        # Đảm bảo có thể lấy ENV từ file hệ thống, pydantic override case-insensitive
        env_file_encoding = "utf-8"

settings = Settings()
