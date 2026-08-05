"""
Modulo de Conversao de Texto em Audio (Multi-Engine TTS para Podcast).
Suporta Edge-TTS com vozes altamente expressivas (Francisca, Thalita Multilingual),
suporte nativo a ElevenLabs (estudio hyper-realista) e fallback automatico para gTTS.
"""

import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Mapeamento de apelidos amigaveis de voz de podcast
PODCAST_VOICES = {
    "francisca": "pt-BR-FranciscaNeural",          # Voz feminina conversacional ultra-natural
    "thalita": "pt-BR-ThalitaMultilingualNeural",   # Voz multilingue expressiva
    "antonio": "pt-BR-AntonioNeural",               # Voz masculina jornalistica
}

DEFAULT_VOICE = os.environ.get("TTS_VOICE", "pt-BR-FranciscaNeural")
DEFAULT_RATE = os.environ.get("TTS_RATE", "-3%")  # Ritmo mais solto e cadenciado estilo podcast


def get_edge_voice_name(voice_alias: str) -> str:
    """Mapeia o nome ou apelido para uma voz valida do Edge-TTS."""
    alias_lower = voice_alias.lower().strip()
    if alias_lower in PODCAST_VOICES:
        return PODCAST_VOICES[alias_lower]
        
    for name in PODCAST_VOICES.values():
        if alias_lower in name.lower():
            return name
            
    return "pt-BR-FranciscaNeural"


def prepare_text_for_natural_pacing(text: str) -> str:
    """
    Formatacao de texto para garantir pausas de respiracao naturais de podcast.
    """
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    formatted_paragraphs = []
    
    for p in paragraphs:
        if not p.endswith(('.', '!', '?', '...')):
            p += '.'
        formatted_paragraphs.append(p)
        
    return '\n\n'.join(formatted_paragraphs)


async def generate_edge_tts(text: str, output_path: str, voice: str, rate: str = DEFAULT_RATE) -> None:
    """Sintetiza audio usando a biblioteca edge-tts com cadencia estilo podcast."""
    import edge_tts

    clean_text = prepare_text_for_natural_pacing(text)
    selected_voice = get_edge_voice_name(voice)
    
    communicate = edge_tts.Communicate(clean_text, selected_voice, rate=rate)
    await communicate.save(output_path)


def generate_elevenlabs_tts(text: str, output_path: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> None:
    """
    Sintetiza audio utilizando a API da ElevenLabs (Qualidade de Estudio Hyper-Realista).
    Requer ELEVENLABS_API_KEY no arquivo .env (Gratuito ate 10.000 caracteres/mes).
    """
    import requests
    
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY não foi configurada no arquivo .env.")

    # ID da voz padrão do ElevenLabs (ou usa a informada)
    voice = os.environ.get("ELEVENLABS_VOICE_ID", voice_id)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=data, headers=headers, timeout=60)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)


def generate_gtts(text: str, output_path: str, lang: str = "pt") -> None:
    """Fallback utilizando a biblioteca gTTS (Google Text-to-Speech)."""
    from gtts import gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_path)


async def text_to_speech_async(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE
) -> str:
    """
    Converte o texto em MP3. Tenta ElevenLabs se configurado, senao Edge-TTS (Francisca/Thalita), senao gTTS.
    """
    if not text.strip():
        raise ValueError("O texto fornecido para síntese de voz está vazio.")

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 1. Se o usuario configurou ElevenLabs no .env ou solicitou 'elevenlabs'
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    if voice.lower() == "elevenlabs" or (elevenlabs_key and voice.lower() != "edge"):
        try:
            logger.info("Gerando áudio com ElevenLabs (Qualidade Hyper-Realista de Estúdio)...")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, generate_elevenlabs_tts, text, output_path)
            logger.info(f"Áudio ElevenLabs gerado com sucesso: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"Falha no ElevenLabs ({e}). Alternando para Edge-TTS...")

    # 2. Sintese padrao Edge-TTS com vozes expressivas de podcast (Francisca / Thalita / Antonio)
    edge_voice = get_edge_voice_name(voice)
    try:
        logger.info(f"Gerando áudio com Edge-TTS (Voz de Podcast: {edge_voice}, cadência: {rate})...")
        await asyncio.wait_for(generate_edge_tts(text, output_path, edge_voice, rate), timeout=30.0)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info(f"Áudio gerado com sucesso via Edge-TTS ({edge_voice}): {output_path}")
            return output_path
        else:
            raise RuntimeError("O arquivo gerado ficou com 0 bytes.")
            
    except Exception as e:
        logger.warning(f"Edge-TTS indisponível ({e}). Ativando fallback gTTS...")
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, generate_gtts, text, output_path, "pt")
            logger.info(f"Áudio gerado com sucesso via gTTS (fallback): {output_path}")
            return output_path
        except Exception as gtts_err:
            logger.error(f"Erro ao gerar áudio com gTTS: {gtts_err}")
            raise RuntimeError(f"Falha na síntese de áudio: {gtts_err}")


def text_to_speech(
    text: str,
    output_path: str = None,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    output_dir: str = "output"
) -> str:
    """
    Wrapper sincrono para a conversao de texto em audio.
    """
    if not output_path:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"tech_trends_{date_str}.mp3"
        output_path = os.path.join(output_dir, output_filename)

    try:
        asyncio.run(text_to_speech_async(text, output_path, voice, rate))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(text_to_speech_async(text, output_path, voice, rate))

    return output_path


if __name__ == "__main__":
    test_text = (
        "Fala pessoal! Bem-vindos a mais uma edição do nosso podcast diário de tecnologia.\n\n"
        "Hoje temos análises profundas sobre arquitetura de software, inteligência artificial e novidades do mercado dev.\n\n"
        "Acompanhem a gente e até a próxima edição!"
    )
    path = text_to_speech(test_text, "output/test_podcast_voice.mp3", voice="francisca")
    print(f"Áudio de teste de podcast gerado em: {path}")
