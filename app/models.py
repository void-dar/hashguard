from datetime import datetime
from typing import Optional
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, SQLModel
from sqlalchemy.sql import func


class FileRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True)
    sha256: str = Field(index=True, unique=True)
    file_size: int
    entropy: float
    mime_guess: Optional[str] = Field(default=None)
    tag: Optional[str] = Field(default=None)
    registered_at: datetime = Field(
    sa_column=Column(
        pg.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
)
