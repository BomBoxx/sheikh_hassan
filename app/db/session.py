from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings  # loads DATABASE_URL
import ssl

DATABASE_URL = settings.DATABASE_URL

# Create SSL context that doesn't verify certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create the async engine with larger pool for concurrency
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production to reduce noise
    connect_args={
        "ssl": ssl_context,
        "server_settings": {"jit": "off"},
        "command_timeout": 60,  # Increased from 10 to 60 seconds
        "timeout": 60,  # Increased from 10 to 60 seconds
    },
    pool_size=20,  # Increased from default 5 to 20
    max_overflow=30,  # Allow up to 30 additional connections when pool is full
    pool_pre_ping=True,  # Verify connections are alive before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Wait up to 30 seconds for available connection
)

# Create async session factory using async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,  # Better control over when to flush
)

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session