import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()

class Settings:
    YT_API_KEY: str = os.getenv("YT_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()

# Remove sslmode from DATABASE_URL for asyncpg compatibility
if settings.DATABASE_URL and '?' in settings.DATABASE_URL:
    settings.DATABASE_URL = settings.DATABASE_URL.split('?')[0]

print(f"DEBUG: DATABASE_URL = {settings.DATABASE_URL}")
print(f"DEBUG: YT_API_KEY = {settings.YT_API_KEY[:20] if settings.YT_API_KEY else 'NOT SET'}...")
