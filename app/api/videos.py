from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Video
from app.services.downloader import get_video_links
from pydantic import BaseModel

router = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)


# Response models
class VideoResponse(BaseModel):
    id: int
    video_id: str
    playlist_id: int
    title: str
    thumbnail: str
    duration: int
    
    class Config:
        from_attributes = True


class VideoWithLinksResponse(VideoResponse):
    mp4_url: str | None = None
    mp3_url: str | None = None


@router.get("/playlist/{playlist_id}", response_model=list[VideoResponse])
async def get_videos_by_playlist(playlist_id: int, db=Depends(get_db)):
    """
    Get all videos in a playlist (without download links)
    """
    query = await db.execute(
        select(Video).where(Video.playlist_id == playlist_id)
    )
    videos = query.scalars().all()
    return videos


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db=Depends(get_db)):
    """
    Get video metadata (without download links)
    """
    query = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = query.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video


@router.get("/{video_id}/play", response_model=VideoWithLinksResponse)
async def get_video_play_links(video_id: int, db=Depends(get_db)):
    """
    Get video with fresh playback URLs (mp4 and mp3)
    Generate URLs on-demand to avoid expiration issues
    """
    query = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = query.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Generate fresh download URLs
    mp4_url, mp3_url = get_video_links(video.video_id)
    
    if not mp4_url or not mp3_url:
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate playback URLs"
        )
    
    # Return video data with fresh URLs
    return VideoWithLinksResponse(
        id=video.id,
        video_id=video.video_id,
        playlist_id=video.playlist_id,
        title=video.title,
        thumbnail=video.thumbnail,
        duration=video.duration,
        mp4_url=mp4_url,
        mp3_url=mp3_url
    )


@router.get("/youtube/{youtube_video_id}/play")
async def get_video_play_links_by_youtube_id(
    youtube_video_id: str, 
    db=Depends(get_db)
):
    """
    Get video playback URLs using YouTube video ID (e.g., 'dQw4w9WgXcQ')
    Useful if you have the YouTube ID but not the database ID
    """
    query = await db.execute(
        select(Video).where(Video.video_id == youtube_video_id)
    )
    video = query.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Generate fresh download URLs
    mp4_url, mp3_url = get_video_links(video.video_id)
    
    if not mp4_url or not mp3_url:
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate playback URLs"
        )
    
    return {
        "id": video.id,
        "video_id": video.video_id,
        "title": video.title,
        "thumbnail": video.thumbnail,
        "duration": video.duration,
        "mp4_url": mp4_url,
        "mp3_url": mp3_url
    }