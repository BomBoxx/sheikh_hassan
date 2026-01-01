from fastapi import APIRouter
from app.services.youtube_sync import sync_playlists_and_videos

router = APIRouter(
    prefix="/sync",
    tags=["Sync"]
)


@router.get("/")
async def run_sync():
    await sync_playlists_and_videos()
    return {"status": "Sync completed"}
