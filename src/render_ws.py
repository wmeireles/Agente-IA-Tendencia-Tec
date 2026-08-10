"""Entry point para o Render Web Service.

Mantem o processo vivo escutando em $PORT (exigencia do Render) e roda
a rotina diaria do digest EM UM SUBPROCESSO separado.

Executar o pipeline em um processo filho isola o servidor HTTP de crashes
nativos (ex.: segfault do onnxruntime/Kokoro) e libera a memoria do modelo
assim que a execucao termina, evitando estouro de RAM na instancia.
"""

import logging
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import schedule
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _pipeline_cmd() -> list[str]:
    cmd = [sys.executable, "-m", "src.main"]
    cmd += ["--count", os.environ.get("COUNT", "6")]
    voice = os.environ.get("TTS_VOICE")
    if voice:
        cmd += ["--voice", voice]
    cmd += ["--rate", os.environ.get("TTS_RATE", "-3%")]
    cmd += ["--output-dir", os.environ.get("OUTPUT_DIR", "output")]
    cmd.append("--send-discord")
    return cmd


def run_pipeline_subprocess() -> None:
    """Executa uma rodada do pipeline em um processo separado e tolera falhas."""
    cmd = _pipeline_cmd()
    timeout = int(os.environ.get("PIPELINE_TIMEOUT", "1800"))
    logger.info("Rodando pipeline em subprocesso: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_root(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.error(
                "Pipeline terminou com codigo %s.\nstdout (fim):\n%s\nstderr (fim):\n%s",
                result.returncode,
                result.stdout[-4000:],
                result.stderr[-4000:],
            )
        else:
            logger.info("Pipeline concluido com sucesso (codigo 0).")
    except subprocess.TimeoutExpired:
        logger.error("Pipeline excedeu o timeout de %ss e foi encerrado.", timeout)
    except Exception as e:  # noqa: BLE001 - nunca deixar o server cair por falha do pipeline
        logger.error("Falha ao executar o pipeline (o servidor segue no ar): %s", e)


def schedule_loop():
    load_dotenv()
    schedule_time = os.environ.get("SCHEDULE_TIME", "08:00")
    run_pipeline_subprocess()
    schedule.every().day.at(schedule_time).do(run_pipeline_subprocess)
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
