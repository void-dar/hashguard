from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from . import anomaly, features
from .database import get_session
from .models import FileRecord
from .schemas import FileListItem, MatchedRecord, RegisterResponse, VerifyResponse

router = APIRouter()


# ── Register ─────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="Register a file — stores its SHA-256 hash and metadata",
)
async def register_file(
    file: UploadFile = File(...),
    tag: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
) -> RegisterResponse:
    data = await file.read()
    feats = features.extract_features(data, file.filename or "")

    result = await session.exec(
        select(FileRecord).where(FileRecord.sha256 == feats["sha256"])
    )
    existing = result.first()

    if existing:
        return RegisterResponse(
            status="already_registered",
            record_id=existing.id,
            filename=existing.filename,
            sha256=existing.sha256,
            file_size=existing.file_size,
            entropy=existing.entropy,
            mime_guess=existing.mime_guess,
            tag=existing.tag,
            message="This exact file is already in the registry.",
        )

    record = FileRecord(
        filename=file.filename or "unnamed",
        sha256=feats["sha256"],
        file_size=feats["file_size"],
        entropy=feats["entropy"],
        mime_guess=feats["mime_guess"],
        tag=tag,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)

    return RegisterResponse(
        status="registered",
        record_id=record.id,
        filename=record.filename,
        sha256=record.sha256,
        file_size=record.file_size,
        entropy=record.entropy,
        mime_guess=record.mime_guess,
        tag=record.tag,
        message="File registered successfully.",
    )


# ── Verify ───────────────────────────────────────────────────────────────────

@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verify a file against the registry — returns CLEAN / ALTERED / ANOMALY / UNKNOWN",
)
async def verify_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> VerifyResponse:
    data = await file.read()
    feats = features.extract_features(data, file.filename or "")

    # ── Step 1: exact hash match ──────────────────────────────────────────────
    match = await session.exec(
        select(FileRecord).where(FileRecord.sha256 == feats["sha256"])
    )
    match = match.first()

    if match:
        return VerifyResponse(
            verdict="CLEAN",
            message="File matches a registered record exactly. Integrity confirmed.",
            sha256=feats["sha256"],
            file_size=feats["file_size"],
            entropy=feats["entropy"],
            anomaly_score=None,
            matched_record=MatchedRecord(
                id=match.id,
                filename=match.filename,
                registered_at=match.registered_at,
                tag=match.tag,
            ),
        )

    # ── Step 2: no hash match → anomaly detection ────────────────────────────
    clf = await anomaly.train_model(session)

    if clf is None:
        return VerifyResponse(
            verdict="UNKNOWN",
            message=(
                f"Hash does not match any registered file. "
                f"AI model needs at least {anomaly.MIN_SAMPLES} registered files to activate "
                f"(register more files to enable anomaly detection)."
            ),
            sha256=feats["sha256"],
            file_size=feats["file_size"],
            entropy=feats["entropy"],
            anomaly_score=None,
            matched_record=None,
        )

    verdict, score = anomaly.predict(clf, feats["file_size"], feats["entropy"])

    messages = {
        "ALTERED": (
            "Hash does not match any registered file. "
            "The AI model considers this file statistically normal — "
            "it was likely modified or is simply unregistered."
        ),
        "ANOMALY": (
            "Hash does not match any registered file. "
            "The AI model flagged this file as statistically anomalous — "
            "unusual size or entropy relative to the registered corpus."
        ),
    }

    return VerifyResponse(
        verdict=verdict,
        message=messages[verdict],
        sha256=feats["sha256"],
        file_size=feats["file_size"],
        entropy=feats["entropy"],
        anomaly_score=score,
        matched_record=None,
    )


# ── List ──────────────────────────────────────────────────────────────────────

@router.get(
    "/files",
    response_model=list[FileListItem],
    summary="List all registered files",
)
async def list_files(session: AsyncSession = Depends(get_session)) -> list[FileListItem]:
    records = await session.exec(
        select(FileRecord).order_by(FileRecord.registered_at.desc())  # type: ignore[arg-type]
    )
    records = records.all()
    return [
        FileListItem(
            id=r.id,
            filename=r.filename,
            sha256_preview=r.sha256[:20] + "…",
            file_size=r.file_size,
            entropy=r.entropy,
            mime_guess=r.mime_guess,
            tag=r.tag,
            registered_at=r.registered_at,
        )
        for r in records
    ]


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete(
    "/files/{record_id}",
    summary="Remove a file record from the registry",
)
async def delete_file(record_id: int, session: AsyncSession = Depends(get_session)) -> dict:
    record = await session.get(FileRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    await session.delete(record)
    await session.commit()
    return {"status": "deleted", "record_id": record_id}
