"""The public portfolio cannot invoke the preserved experimental AI pipeline."""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

from frameworks_and_drivers.public_portfolio_app import app


def request(method: str, path: str):
    async def run():
        output = []
        body_sent = False

        async def receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": b'{"message":"hello"}', "more_body": False}
            return {"type": "http.disconnect"}

        async def send(message):
            output.append(message)

        await app({"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method,
                   "scheme": "http", "path": path, "raw_path": path.encode(), "query_string": b"",
                   "root_path": "", "headers": [], "server": ("test", 80), "client": ("test", 123)}, receive, send)
        status = next(item["status"] for item in output if item["type"] == "http.response.start")
        body = b"".join(item.get("body", b"") for item in output if item["type"] == "http.response.body")
        return status, json.loads(body)
    return asyncio.run(run())


def test_public_health_remains_available():
    assert request("GET", "/health") == (200, {"status": "ok"})


def test_chat_and_admin_routes_are_unavailable():
    for method, path in [("POST", "/v1/chat"), ("GET", "/v1/admin/chat-sessions"),
                         ("GET", "/v1/admin/chat-observations"), ("GET", "/openapi.json")]:
        assert request(method, path)[0] == 404


def test_public_entry_does_not_import_the_ai_pipeline():
    result = subprocess.run([sys.executable, "-c",
        "import sys; import frameworks_and_drivers.public_portfolio_app; "
        "assert 'application.chat_controller' not in sys.modules; "
        "assert 'frameworks_and_drivers.cloudflare_worker_controller' not in sys.modules"],
        cwd=Path(__file__).resolve().parents[1] / 'src',
        capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
