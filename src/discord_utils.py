"""
Modulo de Envio para o Discord via Webhook.
Envia o audio MP3 do dia (e o roteiro em texto) para qualquer canal do Discord
usando um webhook, sem necessidade de bot ou permissoes especiais.
"""

import os
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

DISCORD_MAX_MESSAGE_LEN = 2000


def resolve_webhook_url(explicit: Optional[str] = None) -> Optional[str]:
    """
    Retorna a URL do webhook: prioriza o argumento explicito, senão a env
    DISCORD_WEBHOOK_URL. Retorna None se nenhum estiver configurado.
    """
    url = (explicit or os.environ.get("DISCORD_WEBHOOK_URL") or "").strip()
    return url or None


def truncate_for_discord(text: str, limit: int = DISCORD_MAX_MESSAGE_LEN) -> str:
    """Limita o tamanho da mensagem ao limite do Discord sem cortar no meio de uma palavra."""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def send_audio_to_webhook(
    webhook_url: str,
    file_path: str,
    message: str = "",
) -> int:
    """
    Envia um arquivo de audio (e uma mensagem opcional) para o webhook do Discord
    usando substituicao multipart/form-data. O Discord reproduz audio/* inline.

    Retorna o HTTP status code retornado pelo Discord.
    """
    if not webhook_url:
        raise ValueError("URL do webhook do Discord não está configurada.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    filename = os.path.basename(file_path)
    payload = {"content": truncate_for_discord(message)}

    with open(file_path, "rb") as f:
        files = {"file": (filename, f, "audio/mpeg")}
        response = requests.post(webhook_url, data=payload, files=files, timeout=90)

    response.raise_for_status()
    return response.status_code