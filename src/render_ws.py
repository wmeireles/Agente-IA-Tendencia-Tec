"""Entry point para o Render Web Service.

Mantem o processo vivo escutando em $PORT (exigencia do Render) e roda
a rotina diaria do digest EM UM SUBPROCESSO separado.

Executar o pipeline em um processo filho isola o servidor HTTP de crashes
nativos (ex.: segfault do onnxruntime/Kokoro) e libera a memoria do modelo
assim que a execucao termina, evitando estouro de RAM na instancia.
"""

import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import schedule
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

_state_lock = threading.Lock()
_state = {
    "pipeline": "idle", "scheduler": "starting", "started_at": None,
    "finished_at": None, "returncode": None, "next_run": None,
}


def _update_status(**changes):
    with _state_lock:
        _state.update(changes)


def get_status():
    """Public operational state; never expose logs, credentials or command arguments."""
    with _state_lock:
        return dict(_state)


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _pipeline_cmd() -> list[str]:
    cmd = [sys.executable, "-u", "-m", "src.main"]
    cmd += ["--count", os.environ.get("COUNT", "6")]
    voice = os.environ.get("TTS_VOICE")
    if voice:
        cmd += ["--voice", voice]
    cmd += ["--rate=" + (os.environ.get("TTS_RATE") or "-3%")]
    cmd += ["--output-dir", os.environ.get("OUTPUT_DIR", "output")]
    cmd.append("--send-discord")
    return cmd


def run_pipeline_subprocess() -> None:
    """Executa uma rodada do pipeline em um processo separado e tolera falhas."""
    _update_status(pipeline="running", started_at=_utc_now(), finished_at=None, returncode=None)
    try:
        timeout = int(os.environ.get("PIPELINE_TIMEOUT", "1800"))
        if timeout <= 0:
            raise ValueError("PIPELINE_TIMEOUT deve ser um inteiro positivo")
        logger.info("Iniciando pipeline; limite de %ss. Logs do filho em tempo real.", timeout)
        started = time.monotonic()
        # Inherit stdout/stderr: no pipe buffer, no reader thread, no lost success logs.
        with subprocess.Popen(_pipeline_cmd(), cwd=repo_root()) as process:
            try:
                while True:
                    remaining = timeout - (time.monotonic() - started)
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(process.args, timeout)
                    try:
                        code = process.wait(timeout=min(30, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        logger.info("Pipeline em execucao ha %.0fs (limite: %ss).", time.monotonic() - started, timeout)
            except BaseException:
                process.kill()
                process.wait()
                raise
        _update_status(pipeline="succeeded" if code == 0 else "failed", returncode=code)
        if code != 0:
            logger.error("Pipeline terminou com codigo %s. Consulte os logs acima.", code)
        else:
            logger.info("Pipeline concluido com sucesso (codigo 0).")
    except subprocess.TimeoutExpired:
        _update_status(pipeline="timed_out")
        logger.error("Pipeline excedeu o timeout de %ss e foi encerrado.", timeout)
    except Exception:  # Never take down HTTP when the pipeline fails.
        _update_status(pipeline="failed")
        logger.exception("Falha ao executar o pipeline (o servidor segue no ar).")
    finally:
        _update_status(finished_at=_utc_now())


def schedule_loop():
    try:
        load_dotenv()
        schedule_time = os.environ.get("SCHEDULE_TIME", "08:00")
        scheduler = schedule.Scheduler()
        # Validate before expensive work; invalid settings must remain visible via HTTP.
        job = scheduler.every().day.at(schedule_time).do(run_pipeline_subprocess)
        logger.info("Agendamento diario: %s, fuso local %s.", schedule_time, time.tzname)
        _update_status(scheduler="running", next_run=job.next_run.astimezone(timezone.utc).isoformat())
        if os.environ.get("RUN_ON_STARTUP", "true").lower() == "true":
            # Job.run also advances next_run if startup crosses the scheduled time.
            job.run()
        while True:
            scheduler.run_pending()
            _update_status(next_run=job.next_run.astimezone(timezone.utc).isoformat())
            time.sleep(30)
    except Exception:
        _update_status(scheduler="failed", next_run=None)
        logger.exception("Agendador parou. Corrija a configuracao e reinicie o servico.")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._send_response(with_body=True)

    def do_HEAD(self):
        self._send_response(with_body=False)

    def _send_response(self, with_body):
        path = urlsplit(self.path).path
        code = 200
        content_type = "application/json; charset=utf-8"
        if path == "/healthz":
            body = b"OK"
            content_type = "text/plain; charset=utf-8"
        elif path in ("/", "/status"):
            body = json.dumps(get_status(), indent=2).encode("utf-8")
        else:
            code, body = 404, b'{"error": "not_found"}'
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if with_body:
            self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    load_dotenv()
    port = int(os.environ.get("PORT", "8000"))

    with ThreadingHTTPServer(("0.0.0.0", port), HealthHandler) as server:
        scheduler = threading.Thread(target=schedule_loop, daemon=True)
        scheduler.start()
        logger.info("HTTP na porta %s: /status e /healthz", port)
        server.serve_forever()


if __name__ == "__main__":
    main()
