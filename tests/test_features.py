"""Unit tests for hashguard.features."""

import hashlib

from app.features import extract_features, guess_mime, sha256_of, shannon_entropy


class TestSha256:
    def test_known_value(self):
        digest = sha256_of(b"hello")
        assert digest == hashlib.sha256(b"hello").hexdigest()

    def test_avalanche_effect(self):
        """A single-byte difference should produce a completely different hash."""
        h1 = sha256_of(b"hello")
        h2 = sha256_of(b"hellO")
        assert h1 != h2
        # At least half the nibbles should differ (true avalanche)
        differing = sum(c1 != c2 for c1, c2 in zip(h1, h2))
        assert differing > len(h1) // 2

    def test_deterministic(self):
        assert sha256_of(b"abc") == sha256_of(b"abc")

    def test_empty_bytes(self):
        # SHA-256 of empty string is well-known
        assert sha256_of(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class TestEntropy:
    def test_zero_entropy(self):
        """All identical bytes → entropy = 0."""
        assert shannon_entropy(b"\x00" * 1000) == 0.0

    def test_max_entropy(self):
        """Uniformly distributed 256 byte values → entropy ≈ 8.0."""
        data = bytes(range(256)) * 100
        e = shannon_entropy(data)
        assert abs(e - 8.0) < 0.01

    def test_empty(self):
        assert shannon_entropy(b"") == 0.0

    def test_text_is_low_entropy(self):
        """Natural English text should be well below max entropy."""
        text = b"the quick brown fox jumps over the lazy dog " * 50
        assert shannon_entropy(text) < 5.0

    def test_range_bounds(self):
        import random
        data = bytes(random.randint(0, 255) for _ in range(10_000))
        e = shannon_entropy(data)
        assert 0.0 <= e <= 8.0


class TestGuessMime:
    def test_png(self):
        assert guess_mime(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100) == "image/png"

    def test_jpeg(self):
        assert guess_mime(b"\xff\xd8\xff\xe0" + b"\x00" * 100) == "image/jpeg"

    def test_pdf(self):
        assert guess_mime(b"%PDF-1.4 some content") == "application/pdf"

    def test_plain_text(self):
        assert guess_mime(b"Hello, this is plain text content.") == "text/plain"

    def test_binary_fallback(self):
        assert guess_mime(bytes(range(256))) == "application/octet-stream"


class TestExtractFeatures:
    def test_keys_present(self):
        feats = extract_features(b"test data", "test.txt")
        assert set(feats.keys()) == {"sha256", "file_size", "entropy", "mime_guess"}

    def test_file_size_correct(self):
        data = b"x" * 512
        feats = extract_features(data)
        assert feats["file_size"] == 512

    def test_sha256_correct(self):
        data = b"hello world"
        feats = extract_features(data)
        assert feats["sha256"] == hashlib.sha256(data).hexdigest()
