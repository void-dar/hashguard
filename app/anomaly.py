"""
Anomaly detection using scikit-learn's Isolation Forest.

The model is trained on-the-fly from every registered file in the DB.
Features used: [file_size, entropy]

Verdict logic:
  - Hash match found            → CLEAN      (no AI needed)
  - No hash match, AI inactive  → UNKNOWN    (< MIN_SAMPLES registered)
  - No hash match, pred = 1     → ALTERED    (looks normal, just not registered)
  - No hash match, pred = -1    → ANOMALY    (statistically unusual)
"""

from typing import Optional

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


from .models import FileRecord

MIN_SAMPLES = 5          # minimum records needed before AI activates
CONTAMINATION = 0.1      # expected fraction of outliers in training data


async def _load_training_matrix(session: AsyncSession) -> Optional[np.ndarray]:
    records = await session.exec(select(FileRecord))
    records = records.all()
    if len(records) < MIN_SAMPLES:
        return None
    return np.array([[r.file_size, r.entropy] for r in records], dtype=float)


async def train_model(session: AsyncSession) -> Optional[IsolationForest]:
    """Train and return an IsolationForest from current DB records, or None."""
    X = await _load_training_matrix(session)
    if X is None:
        return None
    clf = IsolationForest(contamination=CONTAMINATION, random_state=42)
    clf.fit(X)
    return clf


def predict(
    clf: IsolationForest,
    file_size: int,
    entropy: float,
) -> tuple[str, float]:
    """
    Return (verdict, anomaly_score) for a single sample.

    anomaly_score: higher (less negative) = more normal.
    Isolation Forest convention: pred=1 normal, pred=-1 anomaly.
    """
    X = np.array([[file_size, entropy]], dtype=float)
    pred = clf.predict(X)[0]
    score = float(clf.decision_function(X)[0])
    verdict = "ANOMALY" if pred == -1 else "ALTERED"
    return verdict, round(score, 6)
