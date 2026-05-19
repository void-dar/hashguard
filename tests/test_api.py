"""Integration tests for /register and /verify endpoints."""

import pytest
from tests.conftest import make_file


ORIGINAL = b"This is the original file content. Do not modify."
TAMPERED = b"This is the original file content. I have been modified!"
RANDOM_BINARY = bytes(range(256)) * 40   # high entropy, looks anomalous


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/register", files=[make_file(ORIGINAL, "doc.txt")])
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "registered"
        assert body["filename"] == "doc.txt"
        assert len(body["sha256"]) == 64
        assert body["file_size"] == len(ORIGINAL)
        assert 0.0 <= body["entropy"] <= 8.0
        assert body["record_id"] is not None

    def test_register_with_tag(self, client):
        resp = client.post(
            "/register?tag=v1",
            files=[make_file(ORIGINAL, "doc.txt")],
        )
        assert resp.status_code == 200
        assert resp.json()["tag"] == "v1"

    def test_register_duplicate_returns_already_registered(self, client):
        client.post("/register", files=[make_file(ORIGINAL, "doc.txt")])
        resp = client.post("/register", files=[make_file(ORIGINAL, "doc.txt")])
        assert resp.status_code == 200
        assert resp.json()["status"] == "already_registered"

    def test_register_different_files_both_succeed(self, client):
        r1 = client.post("/register", files=[make_file(ORIGINAL, "a.txt")])
        r2 = client.post("/register", files=[make_file(TAMPERED, "b.txt")])
        assert r1.json()["status"] == "registered"
        assert r2.json()["status"] == "registered"
        assert r1.json()["record_id"] != r2.json()["record_id"]


class TestVerify:
    def test_verify_clean(self, client):
        """Exact same file → CLEAN."""
        client.post("/register", files=[make_file(ORIGINAL, "doc.txt")])
        resp = client.post("/verify", files=[make_file(ORIGINAL, "doc.txt")])
        assert resp.status_code == 200
        body = resp.json()
        assert body["verdict"] == "CLEAN"
        assert body["matched_record"] is not None
        assert body["matched_record"]["filename"] == "doc.txt"

    def test_verify_unknown_when_corpus_too_small(self, client):
        """With < 5 registered files, unregistered file → UNKNOWN."""
        client.post("/register", files=[make_file(ORIGINAL, "doc.txt")])
        resp = client.post("/verify", files=[make_file(TAMPERED, "modified.txt")])
        body = resp.json()
        assert body["verdict"] == "UNKNOWN"
        assert body["matched_record"] is None
        assert body["anomaly_score"] is None

    def test_verify_altered_or_anomaly_with_large_corpus(self, client):
        """With ≥ 5 registered files, unregistered file → ALTERED or ANOMALY."""
        # Register 5 similar text files to build the model corpus
        for i in range(5):
            content = f"Normal document number {i}. It has typical text content.".encode()
            client.post("/register", files=[make_file(content, f"file{i}.txt")])

        resp = client.post("/verify", files=[make_file(TAMPERED, "unknown.txt")])
        body = resp.json()
        assert body["verdict"] in ("ALTERED", "ANOMALY")
        assert body["anomaly_score"] is not None
        assert body["matched_record"] is None

    def test_verify_clean_after_multiple_registers(self, client):
        """CLEAN verdict should still work correctly even with a large corpus."""
        for i in range(6):
            content = f"Filler document {i}.".encode()
            client.post("/register", files=[make_file(content, f"filler{i}.txt")])

        client.post("/register", files=[make_file(ORIGINAL, "target.txt")])
        resp = client.post("/verify", files=[make_file(ORIGINAL, "target.txt")])
        assert resp.json()["verdict"] == "CLEAN"

    def test_verify_response_shape(self, client):
        """Verify response always includes required fields."""
        resp = client.post("/verify", files=[make_file(ORIGINAL, "x.txt")])
        body = resp.json()
        for field in ("verdict", "message", "sha256", "file_size", "entropy"):
            assert field in body


class TestFilesList:
    def test_list_empty(self, client):
        resp = client.get("/files")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_after_register(self, client):
        client.post("/register", files=[make_file(ORIGINAL, "a.txt")])
        client.post("/register", files=[make_file(TAMPERED, "b.txt")])
        resp = client.get("/files")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 2
        filenames = {i["filename"] for i in items}
        assert filenames == {"a.txt", "b.txt"}

    def test_list_item_shape(self, client):
        client.post("/register?tag=v1", files=[make_file(ORIGINAL, "doc.txt")])
        item = client.get("/files").json()[0]
        for field in ("id", "filename", "sha256_preview", "file_size", "entropy", "registered_at"):
            assert field in item
        assert item["tag"] == "v1"
        assert item["sha256_preview"].endswith("…")


class TestDelete:
    def test_delete_existing(self, client):
        reg = client.post("/register", files=[make_file(ORIGINAL, "doc.txt")]).json()
        rid = reg["record_id"]

        resp = client.delete(f"/files/{rid}")
        assert resp.status_code == 200
        assert resp.json()["record_id"] == rid

        # Should no longer appear in list
        assert client.get("/files").json() == []

    def test_delete_nonexistent(self, client):
        resp = client.delete("/files/99999")
        assert resp.status_code == 404

    def test_delete_then_re_register(self, client):
        """After deletion, the same file can be registered again."""
        reg = client.post("/register", files=[make_file(ORIGINAL, "doc.txt")]).json()
        client.delete(f"/files/{reg['record_id']}")
        reg2 = client.post("/register", files=[make_file(ORIGINAL, "doc.txt")]).json()
        assert reg2["status"] == "registered"
