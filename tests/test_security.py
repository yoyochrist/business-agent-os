"""Security regression tests for Business Agent OS. Run: python -m unittest discover -s tests"""
import http.client
import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import app


class SecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        app.DB = Path(cls.temp.name) / "tasks.db"
        app.init_db()
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp.cleanup()

    def request(self, method, route, token=None, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-Session-Token"] = token
        conn.request(method, route, body=body, headers=headers)
        res = conn.getresponse()
        code = res.status
        res.read()
        conn.close()
        return code

    def test_read_requires_token(self):
        self.assertEqual(self.request("GET", "/tasks/example"), 401)
        self.assertEqual(self.request("GET", "/tasks/example", "not-the-token"), 401)
        self.assertEqual(self.request("GET", "/tasks/example", app.SESSION_TOKEN), 404)

    def test_create_requires_token(self):
        body = json.dumps({"role":"pm","provider":"codex","prompt":"hello"})
        self.assertEqual(self.request("POST", "/tasks", body=body), 401)
        self.assertEqual(self.request("POST", "/tasks", token="bad", body=body), 401)


if __name__ == "__main__":
    unittest.main()
