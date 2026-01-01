from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import playlists, videos, sync
from app.scheduler import start_scheduler
from app.db.models import Base
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database on startup: {e}")
        print("ℹ️  Check your Supabase connection and network connectivity")
    
    try:
        start_scheduler()
        print("✅ Scheduler started")
    except Exception as e:
        print(f"⚠️  Warning: Could not start scheduler: {e}")
    
    yield
    # Optional: shutdown code here if you need to stop the scheduler


from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(lifespan=lifespan,debug=True)


# Allow your frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"] if you serve HTML locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Routers
app.include_router(playlists.router)
app.include_router(videos.router)
app.include_router(sync.router)
