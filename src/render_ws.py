"""Entry point para o Render Web Service.

Mantem o processo vivo escutando em $PORT (exigencia do Render) e roda
a rotina diaria do digest em uma thread em background.
"""

import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace

import schedule
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import run_pipeline


def build_args():
    return SimpleNamespace(
        output_dir=os.environ.get("OUTPUT_DIR", "output"),
        count=int(os.environ.get("COUNT", "6")),
        voice=os.environ.get("TTS_VOICE"),
        rate=os.environ.get("TTS_RATE", "-3%"),
        save_script=True,
        send_discord=True,
        discord_webhook=None,
    )


def schedule_loop():
    load_dotenv()
    schedule_time = os.environ.get("SCHEDULE_TIME", "08:00")
    args = build_args()
    run_pipeline(args)
    schedule.every().day.at(schedule_time).do(run_pipeline, build_args())
    while True:
        schedule.run_pending()
        time.sleep(30)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._send_ok(with_body=True)

    def do_HEAD(self):
        self._send_ok(with_body=False)

    def _send_ok(self, with_body):
        body = b"OK"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if with_body:
            self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    load_dotenv()
    port = int(os.environ.get("PORT", "8000"))

    scheduler = threading.Thread(target=schedule_loop, daemon=True)
    scheduler.start()

    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Serving health endpoint on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
