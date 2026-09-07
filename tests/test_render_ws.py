"""Regression coverage for the Render process supervisor (no external APIs)."""

import json
import sys
import threading
from http.client import HTTPConnection
from http.server import HTTPServer

from src import render_ws


def test_render_command_accepts_negative_speech_rate(monkeypatch):
    from src.main import parse_args

    monkeypatch.setenv("TTS_RATE", "-3%")
    command = render_ws._pipeline_cmd()
    monkeypatch.setattr(sys, "argv", command[command.index("src.main"):])
    args = parse_args()
    assert args.rate == "-3%"
    assert args.send_discord is True


def test_successful_child_output_is_visible(monkeypatch, capfd):
    monkeypatch.setattr(render_ws, "_pipeline_cmd", lambda: [sys.executable, "-u", "-c", "print('pipeline-stage')"])
    render_ws.run_pipeline_subprocess()
    assert "pipeline-stage" in capfd.readouterr().out


def test_failed_child_is_visible_in_http_status(monkeypatch):
    monkeypatch.setattr(render_ws, "_pipeline_cmd", lambda: [sys.executable, "-c", "raise SystemExit(7)"])
    render_ws.run_pipeline_subprocess()
    server = HTTPServer(("127.0.0.1", 0), render_ws.HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = HTTPConnection(*server.server_address, timeout=3)
    try:
        connection.request("GET", "/status")
        response = connection.getresponse()
        assert response.status == 200
        status = json.loads(response.read())
        assert status["pipeline"] == "failed"
        assert status["returncode"] == 7
        connection.request("GET", "/healthz")
        assert connection.getresponse().status == 200
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_timeout_is_reported_and_child_stops(monkeypatch):
    monkeypatch.setenv("PIPELINE_TIMEOUT", "1")
    monkeypatch.setattr(render_ws, "_pipeline_cmd", lambda: [sys.executable, "-c", "import time; time.sleep(60)"])
    render_ws.run_pipeline_subprocess()
    assert render_ws.get_status()["pipeline"] == "timed_out"


def test_invalid_schedule_fails_before_pipeline(monkeypatch):
    monkeypatch.setenv("SCHEDULE_TIME", "invalid")
    calls = []
    monkeypatch.setattr(render_ws, "run_pipeline_subprocess", lambda: calls.append(True))
    render_ws.schedule_loop()
    assert calls == []
    assert render_ws.get_status()["scheduler"] == "failed"
