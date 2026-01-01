from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(String, unique=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    thumbnail = Column(String)

    videos = relationship("Video", back_populates="playlist")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    title = Column(String)
    duration = Column(Integer)
    
    thumbnail = Column(String)

    playlist = relationship("Playlist", back_populates="videos")
