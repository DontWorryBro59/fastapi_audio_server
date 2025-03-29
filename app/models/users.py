from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


from app.models.base_model import Base


class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    audio_files = relationship("AudioFile", back_populates="owner")


class AudioFileORM(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="audio_files")
