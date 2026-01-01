from yt_dlp import YoutubeDL


def get_video_links(video_id: str):
    """
    Generates direct MP4 + MP3 download URLs using yt-dlp
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Options for video (MP4)
        video_opts = {
            "format": "best[ext=mp4]/best",
            "quiet": True,
            "skip_download": True
        }
        
        # Options for audio (MP3/M4A)
        audio_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "skip_download": True
        }
        
        # Get video URL
        with YoutubeDL(video_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)
            mp4 = video_info["url"]
        
        # Get audio URL
        with YoutubeDL(audio_opts) as ydl:
            audio_info = ydl.extract_info(url, download=False)
            mp3 = audio_info["url"]
        
        return mp4, mp3
    
    except Exception as e:
        print("Downloader Error:", e)
        return None, None


def get_audio_url(video_id: str):
    """
    Get only the audio URL (for background playback)
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "skip_download": True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info["url"]
    
    except Exception as e:
        print("Downloader Error:", e)
        return None


def get_video_url(video_id: str):
    """
    Get only the video URL
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "quiet": True,
            "skip_download": True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info["url"]
    
    except Exception as e:
        print("Downloader Error:", e)
        return None