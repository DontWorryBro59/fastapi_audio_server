from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_model import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    yandex_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=True
    )
    username: Mapped[str] = mapped_column(String, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)

    audio_files: Mapped[list["AudioFileORM"]] = relationship(
        "AudioFileORM", back_populates="owner"
    )


class AudioFileORM(Base):
    __tablename__ = "audio_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, index=True)
    file_path: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    owner: Mapped["UserORM"] = relationship("UserORM", back_populates="audio_files")
