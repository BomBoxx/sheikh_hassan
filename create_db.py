import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Load .env file
load_dotenv()

# احصل على المتغير
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your .env file!")

engine = create_async_engine(DATABASE_URL, echo=True)
