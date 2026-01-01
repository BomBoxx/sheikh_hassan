from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.youtube_sync import sync_playlists_and_videos
import asyncio

# Global scheduler instance
scheduler = None

def start_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        return
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(sync_playlists_and_videos, "interval", hours=2, id="youtube_sync")
    
    try:
        scheduler.start()
        print("✅ Scheduler started successfully")
    except Exception as e:
        print(f"⚠️ Scheduler error: {e}")

def stop_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("✅ Scheduler stopped")

