import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from scripts import upload_btcusdt_history_to_supabase as uploader


class SupabaseUploaderReadbackTests(unittest.TestCase):
    def run_uploader(self, remote_bytes):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        payload = b"validated sample archive bytes"
        (root / "sample-2026-09.zip").write_bytes(payload)
        calls = []

        def fake_request(url, method, headers, data=None):
            calls.append((url, method, data))
            if method == "GET":
                return remote_bytes
            return b""

        env = {
            "SUPABASE_URL": "https://project.example.invalid",
            "SUPABASE_SERVICE_ROLE_KEY": "not-a-real-secret",
            "SUPABASE_BUCKET": "private-test-bucket",
        }
        with patch.dict(os.environ, env, clear=False), \
             patch("sys.argv", ["uploader", "--input-dir", str(root)]), \
             patch.object(uploader, "request", side_effect=fake_request), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = uploader.main()
        return code, calls, payload

    def test_catalog_write_only_after_matching_readback(self):
        code, calls, payload = self.run_uploader(payload := b"validated sample archive bytes")
        self.assertEqual(code, 0)
        methods = [method for _, method, _ in calls]
        self.assertEqual(methods, ["POST", "GET", "POST"])
        catalog_payload = calls[-1][2]
        record = json.loads(catalog_payload)
        self.assertEqual(record["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(record["size_bytes"], len(payload))

    def test_readback_mismatch_stops_before_catalog_write(self):
        code, calls, _ = self.run_uploader(b"corrupted remote bytes")
        self.assertEqual(code, 1)
        methods = [method for _, method, _ in calls]
        self.assertEqual(methods, ["POST", "GET"])


if __name__ == "__main__":
    unittest.main()
