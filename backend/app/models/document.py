"""
SQLAlchemy ORM model for stored document classifications
"""

from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from app.core.database import Base


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_hash: Mapped[str] = mapped_column(
        String(66), unique=True, nullable=False, index=True
    )
    classification: Mapped[str] = mapped_column(String(20), nullable=False)
    model_hash: Mapped[str] = mapped_column(String(66), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    blockchain_tx: Mapped[str | None] = mapped_column(String(66), nullable=True)
    on_chain: Mapped[bool] = mapped_column(Boolean, default=False)
    uploader_address: Mapped[str | None] = mapped_column(String(42), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
