# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env in local dev

class Settings:
    def __init__(self) -> None:
        self.env = os.getenv("ENV", "development")
        self.database_url = os.getenv("DATABASE_URL")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.sentry_dsn = os.getenv("SENTRY_DSN")

        if not self.database_url:
            raise ValueError("DATABASE_URL is required")

settings = Settings()
