import uuid

from sqlalchemy import Integer, String, ForeignKey, UUID, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_model import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    yandex_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    username: Mapped[str] = mapped_column(String, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    audio_files: Mapped[list["AudioFileORM"]] = relationship(
        "AudioFileORM", back_populates="owner"
    )


class AudioFileORM(Base):
    __tablename__ = "audio_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(String, index=True)
    file_path: Mapped[str] = mapped_column(String)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    owner: Mapped["UserORM"] = relationship("UserORM", back_populates="audio_files")
