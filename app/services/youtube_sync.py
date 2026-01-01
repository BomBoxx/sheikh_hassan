from googleapiclient.discovery import build
from sqlalchemy import select
from app.db.models import Playlist, Video
from app.db.session import AsyncSessionLocal as async_session
from app.services.downloader import get_video_links
from app.config import settings
import isodate
import asyncio

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=settings.YT_API_KEY)


async def sync_playlists_and_videos():
    """
    Sync all playlists & videos from YouTube channel with pagination
    """
    print("🔄 Starting YouTube sync...")

    async with async_session() as db:
        playlists = []
        next_page_token = None

        # ============================
        # 1) FETCH ALL PLAYLISTS
        # ============================
        print("📋 Fetching playlists...")
        while True:
            request = youtube.playlists().list(
                part="snippet,contentDetails",
                channelId="UCx24U2X2rAIHEQylTCjSXgw",
                maxResults=50,
                pageToken=next_page_token
            )
            playlists_data = request.execute()

            for item in playlists_data.get("items", []):
                playlist_yid = item["id"]
                title = item["snippet"]["title"]
                thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

                # Check if playlist exists
                result = await db.execute(
                    select(Playlist).where(Playlist.playlist_id == playlist_yid)
                )
                existing = result.scalar_one_or_none()

                if not existing:
                    playlist_obj = Playlist(
                        playlist_id=playlist_yid,
                        name=title,
                        thumbnail=thumbnail
                    )
                    db.add(playlist_obj)
                    await db.commit()
                    await db.refresh(playlist_obj)
                    print(f"🆕 Added playlist: {title}")
                else:
                    playlist_obj = existing
                    print(f"✔ Playlist exists: {title}")

                playlists.append(playlist_obj)

            # Check if there is a next page
            next_page_token = playlists_data.get("nextPageToken")
            if not next_page_token:
                break

    # ============================
    # 2) FETCH VIDEOS WITH CONTROLLED CONCURRENCY
    # ============================
    print(f"\n⚡ Fetching videos from {len(playlists)} playlists with concurrency...")
    
    # Process 10 playlists at a time (each gets its own DB session)
    semaphore = asyncio.Semaphore(10)
    
    async def sync_with_limit(playlist):
        async with semaphore:
            try:
                await sync_videos_for_playlist(playlist)
            except Exception as e:
                print(f"❌ Error syncing playlist {playlist.name}: {e}")
    
    # Process all playlists concurrently with the semaphore limit
    await asyncio.gather(*[sync_with_limit(p) for p in playlists], return_exceptions=True)

    print("\n✅ Sync finished.")


# =====================================================
# Helper function to fetch videos inside playlist
# =====================================================
async def sync_videos_for_playlist(playlist_obj):
    """Fetch videos for a single playlist with its own database session"""
    # Each playlist gets its own session to avoid conflicts
    async with async_session() as db:
        print(f" ▶ Fetching videos for playlist: {playlist_obj.name}")

        next_page_token = None
        video_count = 0

        while True:
            try:
                request = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_obj.playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                videos_data = request.execute()

                # Collect all video IDs from this page
                video_ids_to_process = []
                
                for item in videos_data.get("items", []):
                    video_id = item["contentDetails"]["videoId"]
                    video_ids_to_process.append(video_id)

                # Batch check which videos already exist
                if video_ids_to_process:
                    result = await db.execute(
                        select(Video.video_id).where(Video.video_id.in_(video_ids_to_process))
                    )
                    existing_video_ids = {row[0] for row in result.fetchall()}
                    
                    # Filter out existing videos
                    new_video_ids = [vid for vid in video_ids_to_process if vid not in existing_video_ids]
                    
                    # Fetch details for all new videos in batch (YouTube allows up to 50 IDs)
                    if new_video_ids:
                        for i in range(0, len(new_video_ids), 50):
                            batch = new_video_ids[i:i+50]
                            
                            try:
                                video_req = youtube.videos().list(
                                    part="snippet,contentDetails",
                                    id=",".join(batch)
                                ).execute()

                                videos_to_add = []
                                for v in video_req.get("items", []):
                                    try:
                                        video_id = v["id"]
                                        title = v["snippet"]["title"]
                                        thumbnail = v["snippet"]["thumbnails"]["high"]["url"]
                                        duration_iso = v["contentDetails"]["duration"]
                                        duration_sec = parse_duration(duration_iso)

                                        # Generate download URLs
                                        mp4_link, mp3_link = get_video_links(video_id)

                                        new_video = Video(
                                            video_id=video_id,
                                            playlist_id=playlist_obj.id,
                                            title=title,
                                            thumbnail=thumbnail,
                                            duration=duration_sec,
                                            
                                        )

                                        videos_to_add.append(new_video)
                                        video_count += 1
                                    
                                    except Exception as e:
                                        print(f"   ⚠ Error processing video: {e}")
                                        continue
                                
                                # Bulk add videos
                                if videos_to_add:
                                    db.add_all(videos_to_add)
                                    await db.commit()
                                    print(f"   ✓ Added {len(videos_to_add)} videos")
                            
                            except Exception as e:
                                print(f"   ❌ Error fetching video batch: {e}")
                                await db.rollback()
                                continue

                # Pagination for videos
                next_page_token = videos_data.get("nextPageToken")
                if not next_page_token:
                    break
            
            except Exception as e:
                print(f"   ❌ Error fetching playlist items: {e}")
                break

        print(f"   ✅ Completed {playlist_obj.name}: {video_count} new videos")


# =====================================================
# Duration parser: Convert ISO 8601 → seconds
# Example: PT5M32S → 332 seconds
# =====================================================
def parse_duration(duration_str: str) -> int:
    try:
        duration = isodate.parse_duration(duration_str)
        return int(duration.total_seconds())
    except:
        return 0