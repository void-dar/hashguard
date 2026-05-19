import hashlib
import math
from collections import Counter


def sha256_of(data: bytes) -> str:
    """Return the hex-encoded SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def shannon_entropy(data: bytes) -> float:
    """
    Compute Shannon entropy (bits per byte, 0–8) for *data*.

    High entropy (> 7.0) usually means the file is compressed or encrypted.
    Low entropy (< 3.0) means highly repetitive / mostly text.
    """
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    return -sum(
        (c / total) * math.log2(c / total)
        for c in counts.values()
        if c
    )


# Minimal magic-byte table — good enough for a demo without python-magic deps
_MAGIC: list[tuple[bytes, str]] = [
    (b"\x89PNG",         "image/png"),
    (b"\xff\xd8\xff",    "image/jpeg"),
    (b"GIF8",            "image/gif"),
    (b"%PDF",            "application/pdf"),
    (b"PK\x03\x04",      "application/zip"),
    (b"\x1f\x8b",        "application/gzip"),
    (b"BZh",             "application/bzip2"),
    (b"\x7fELF",         "application/elf"),
    (b"MZ",              "application/exe"),
    (b"\xd0\xcf\x11\xe0","application/msoffice"),
    (b"<!DOCTYPE",       "text/html"),
    (b"<html",           "text/html"),
    (b"<?xml",           "application/xml"),
]


def guess_mime(data: bytes) -> str:
    """Guess MIME type from magic bytes. Falls back to text/plain or application/octet-stream."""
    head = data[:16].lower()
    for magic, mime in _MAGIC:
        if head.startswith(magic.lower()):
            return mime
    # Simple text heuristic: check if printable ASCII dominates
    try:
        data[:512].decode("utf-8")
        return "text/plain"
    except UnicodeDecodeError:
        return "application/octet-stream"


def extract_features(data: bytes, filename: str = "") -> dict:
    """Return all computed features for a file payload."""
    return {
        "sha256":     sha256_of(data),
        "file_size":  len(data),
        "entropy":    round(shannon_entropy(data), 6),
        "mime_guess": guess_mime(data),
    }
