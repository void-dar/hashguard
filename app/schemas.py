from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


# ── Register ─────────────────────────────────────────────────────────────────

class RegisterResponse(BaseModel):
    status: Literal["registered", "already_registered"]
    record_id: int
    filename: str
    sha256: str
    file_size: int
    entropy: float
    mime_guess: Optional[str]
    tag: Optional[str]
    message: str


# ── Verify ───────────────────────────────────────────────────────────────────

class MatchedRecord(BaseModel):
    id: int
    filename: str
    registered_at: datetime
    tag: Optional[str]


class VerifyResponse(BaseModel):
    verdict: Literal["CLEAN", "ALTERED", "ANOMALY", "UNKNOWN"]
    message: str
    sha256: str
    file_size: int
    entropy: float
    anomaly_score: Optional[float]
    matched_record: Optional[MatchedRecord]


# ── File list ────────────────────────────────────────────────────────────────

class FileListItem(BaseModel):
    id: int
    filename: str
    sha256_preview: str      # first 20 chars + "…"
    file_size: int
    entropy: float
    mime_guess: Optional[str]
    tag: Optional[str]
    registered_at: datetime
