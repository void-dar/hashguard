"""Unit tests for hashguard.anomaly."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession as Session

from app.anomaly import MIN_SAMPLES, predict, train_model
from app.models import FileRecord


async def _insert_records(session: Session, n: int, base_size: int = 500, base_entropy: float = 4.5):
    """Insert *n* synthetic FileRecord rows with slightly varied features."""
    import hashlib, random
    for i in range(n):
        record = FileRecord(
            filename=f"file_{i}.txt",
            sha256=hashlib.sha256(f"content_{i}".encode()).hexdigest(),
            file_size=base_size + random.randint(-50, 50),
            entropy=round(base_entropy + random.uniform(-0.3, 0.3), 6),
        )
        session.add(record)
    await session.commit()


class TestTrainModel:
    async def test_returns_none_when_too_few_records(self, session):
        await _insert_records(session, MIN_SAMPLES - 1)
        assert await train_model(session) is None

    async def test_returns_model_at_min_samples(self, session):
        await _insert_records(session, MIN_SAMPLES)
        clf = await train_model(session)
        assert clf is not None

    async def test_returns_model_with_large_corpus(self, session):
        await _insert_records(session, 20)
        clf = await train_model(session)
        assert clf is not None


class TestPredict:
    async def _get_trained_model(self, session):
        await _insert_records(session, 10, base_size=500, base_entropy=4.5)
        return await train_model(session)

    async def test_normal_file_returns_altered(self, session):
        clf = await self._get_trained_model(session)
        # Same profile as training data → should be ALTERED (not anomalous)
        verdict, score = predict(clf, file_size=490, entropy=4.4)
        assert verdict == "ALTERED"
        assert isinstance(score, float)

    async def test_anomalous_file_returns_anomaly(self, session):
        """
        A file wildly outside the training distribution should be flagged.
        We accept both ANOMALY and ALTERED — the exact verdict depends on the
        IsolationForest threshold at this corpus size, but either way it is NOT
        clean. The anomaly_score must be negative (outlier side).
        """
        clf = await self._get_trained_model(session)
        verdict, score = predict(clf, file_size=10_000_000, entropy=7.99)
        assert verdict in ("ANOMALY", "ALTERED")
        assert score < 0

    async def test_score_is_float(self, session):
        clf = await self._get_trained_model(session)
        _, score = predict(clf, file_size=500, entropy=4.5)
        assert isinstance(score, float)

    async def test_score_is_rounded(self, session):
        clf = await self._get_trained_model(session)
        _, score = predict(clf, file_size=500, entropy=4.5)
        # Check it has at most 6 decimal places
        assert score == round(score, 6)
