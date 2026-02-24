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

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # SMTP
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Python Vue Boilerplate"

    # Reset Password
    reset_password_expire_minutes: int = 30

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # Facebook OAuth
    facebook_app_id: str = ""
    facebook_app_secret: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
