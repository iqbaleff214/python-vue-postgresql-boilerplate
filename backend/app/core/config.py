from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Python Vue Boilerplate"
    frontend_url: str = "http://localhost:5173"
    environment: str = "development"
    database_url: str = "postgresql://username:password@localhost:5432/python_vue_boilerplate"
    secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
