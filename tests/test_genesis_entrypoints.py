import json
import sqlite3
import subprocess
import sys

from crawlengine.server import CrawlEngineServer


def test_notice_is_silent():
    res = subprocess.run([sys.executable, "-c", "import crawlengine._genesis; crawlengine._genesis.print_upgrade_notice()"], capture_output=True, text=True)
    assert res.stderr == ""
    assert res.stdout == ""
    import crawlengine._genesis
    assert crawlengine._genesis.NOTICE == ""


def test_blackbox_bridge_records_ssrf_http_event(monkeypatch, tmp_path):
    wal_db = tmp_path / "wal.sqlite"
    monkeypatch.setenv("BLACKBOX_DB_PATH", str(wal_db))

    server = CrawlEngineServer()
    res = server.handle_tool_call("scrape_url", {"url": "http://127.0.0.1/admin"})
    assert res["success"] is False

    wal_conn = sqlite3.connect(str(wal_db))
    rows = wal_conn.execute(
        "SELECT event_type, source, status, payload FROM blackbox_events ORDER BY id ASC;"
    ).fetchall()
    wal_conn.close()

    assert len(rows) == 1
    assert rows[0][0] == "HTTP_CLIENT"
    assert rows[0][1] == "crawlengine-mcp"
    assert rows[0][2] == "error"
    payload = json.loads(rows[0][3])
    assert payload["tool"] == "scrape_url"
    assert payload["method"] == "GET"
    assert "127.0.0.1" in payload["url"]
    assert payload["error"]
