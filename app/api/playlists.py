from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Playlist

router = APIRouter(
    prefix="/playlists",
    tags=["Playlists"]
)


@router.get("/")
async def get_playlists(db=Depends(get_db)):
    query = await db.execute(select(Playlist))
    playlists = query.scalars().all()
    return playlists


@router.get("/{playlist_id}")
async def get_playlist(playlist_id: int, db=Depends(get_db)):
    query = await db.execute(
        select(Playlist).where(Playlist.id == playlist_id)
    )
    playlist = query.scalar_one_or_none()
    return playlist
