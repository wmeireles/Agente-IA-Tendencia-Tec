"""
Orquestrador Principal / CLI - Agente de Tendencias de Tecnologia e Audio Digest (Informativo + Educacional).
Suporta execucao avulsa ou modo continuo diário automatizado (--daily).
"""

import argparse
import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv

# Força codificação UTF-8 para evitar UnicodeEncodeError no terminal Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Adiciona o diretorio raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from src import __version__
from src.discord_utils import resolve_webhook_url, send_audio_to_webhook
from src.fetcher import get_daily_tech_trends
from src.summarizer import generate_podcast_script
from src.tts import text_to_speech

console = Console(force_terminal=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Agente de IA Educacional: Busca notícias de tecnologia, ensina um conceito do dia e gera um podcast em MP3."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Exibe a versão do agente e sai."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=6,
        help="Número de notícias/tópicos a serem coletados (padrão: 6)."
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=None,
        help="Voz do podcast (opções: francisca [recomendada], thalita, antonio, elevenlabs)."
    )
    parser.add_argument(
        "--rate",
        type=str,
        default="-3%",
        help="Cadência de fala estilo podcast (padrão: -3%%)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Diretório onde os arquivos gerados serão salvos (padrão: output)."
    )
    parser.add_argument(
        "--save-script",
        action="store_true",
        default=True,
        help="Salva uma cópia do roteiro gerado em formato .txt junto com o áudio."
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Executa o agente em modo contínuo (daemon) todos os dias no horário especificado."
    )
    parser.add_argument(
        "--schedule-time",
        type=str,
        default="08:00",
        help="Horário diário para execução no modo --daily no formato HH:MM (padrão: 08:00)."
    )
    parser.add_argument(
        "--send-discord",
        action="store_true",
        help="Envia o áudio gerado para o Discord via webhook ao final do pipeline."
    )
    parser.add_argument(
        "--discord-webhook",
        type=str,
        default=None,
        help="URL do webhook do Discord (sobrepõe DISCORD_WEBHOOK_URL do .env)."
    )
    return parser.parse_args()


def run_pipeline(args):
    """Executa uma rodada completa do pipeline de geração de áudio."""
    gemini_or_groq_key = os.environ.get("GROQ_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not gemini_or_groq_key or gemini_or_groq_key == "gsk_sua_chave_groq_aqui":
        console.print(
            "[bold red]❌ Erro:[/bold red] Chave [bold yellow]GROQ_API_KEY[/bold yellow] não configurada.\n"
            "Por favor, configure o arquivo [bold cyan].env[/bold cyan] com sua chave da Groq (https://console.groq.com/keys).\n"
        )
        return False

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    mp3_filename = f"tech_trends_{date_str}.mp3"
    mp3_filepath = os.path.join(output_dir, mp3_filename)
    script_filepath = os.path.join(output_dir, f"tech_trends_{date_str}.txt")

    articles = []
    script_text = ""
    final_audio_path = ""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        # Etapa 1: Coleta de noticias
        task1 = progress.add_task("[bold yellow]1. Coletando tendências do mercado de tecnologia...[/bold yellow]", total=1)
        try:
            articles = get_daily_tech_trends(target_count=args.count)
            progress.update(task1, completed=1, description="[bold green]1. Tendências coletadas com sucesso![/bold green]")
        except Exception as e:
            progress.update(task1, completed=1, description="[bold red]1. Erro ao buscar tendências![/bold red]")
            console.print(f"[red]Detalhes do erro na coleta:[/red] {e}")
            return False

        if not articles:
            console.print("[bold red]❌ Nenhuma notícia recente encontrada no momento.[/bold red]")
            return False

        # Etapa 2: Geracao do Roteiro Informativo + Educacional
        model_name = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        task2 = progress.add_task(f"[bold yellow]2. Criando narrativa profissional via Groq ({model_name})...[/bold yellow]", total=1)
        try:
            script_text = generate_podcast_script(articles)
            progress.update(task2, completed=1, description="[bold green]2. Roteiro narrativo profissional gerado![/bold green]")
        except Exception as e:
            progress.update(task2, completed=1, description="[bold red]2. Erro ao gerar roteiro![/bold red]")
            console.print(f"[red]Detalhes do erro na LLM:[/red] {e}")
            return False

        # Etapa 3: Sintese de Voz em Audio MP3 Ultra-Humanizada
        voice_name = args.voice or os.environ.get("TTS_VOICE", "francisca")
        task3 = progress.add_task(f"[bold yellow]3. Sintetizando voz de podcast ({voice_name})...[/bold yellow]", total=1)
        try:
            final_audio_path = text_to_speech(script_text, output_path=mp3_filepath, voice=voice_name, rate=args.rate)
            progress.update(task3, completed=1, description="[bold green]3. Áudio digest MP3 gerado com sucesso![/bold green]")
        except Exception as e:
            progress.update(task3, completed=1, description="[bold red]3. Erro na síntese de voz![/bold red]")
            console.print(f"[red]Detalhes do erro no TTS:[/red] {e}")
            return False

    # Salva o arquivo de roteiro
    if args.save_script and script_text:
        with open(script_filepath, "w", encoding="utf-8") as f:
            f.write(script_text)

    # Envia o áudio para o Discord via webhook, se solicitado
    if args.send_discord:
        webhook_url = resolve_webhook_url(args.discord_webhook)
        if not webhook_url:
            console.print("[bold red]❌ Erro:[/bold red] --send-discord foi usado, mas nenhum webhook do Discord está configurado.\n[cyan]Defina DISCORD_WEBHOOK_URL no .env ou passe --discord-webhook <url>.[/cyan]")
            return False
        try:
            console.print("[bold yellow]📤 Enviando áudio para o Discord...[/bold yellow]")
            digest_title = f"🎙️ Tech Trends Digest — {date_str}"
            sources_line = " | ".join(dict.fromkeys(item["source"] for item in articles))
            message = (
                f"{digest_title}\n"
                f"📌 {len(articles)} tendências de hoje:\n"
                f"🌐 Fontes: {sources_line}\n"
                f"▶️ Ouça o áudio abaixo."
            )
            status = send_audio_to_webhook(webhook_url, final_audio_path, message=message)
            console.print(f"[bold green]✅ Áudio enviado ao Discord (HTTP {status})![/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Falha ao enviar ao Discord:[/bold red] {e}")
            return False

    # Exibicao de Resultados
    console.print()
    console.print(f"[bold green]✨ Podcast Educacional do Dia ({date_str}) Gerado com Sucesso![/bold green]\n")

    # Tabela com as noticias utilizadas
    table = Table(title="📌 Principais Tendências Selecionadas", show_header=True, header_style="bold magenta")
    table.add_column("Fonte", style="cyan", width=15)
    table.add_column("Título / Tópico", style="white")

    for item in articles:
        table.add_row(item["source"], item["title"])

    console.print(table)
    console.print()

    # Painel do Resultado
    console.print(
        Panel(
            f"[bold yellow]🎧 Arquivo de Áudio MP3:[/bold yellow]\n[bold green]{os.path.abspath(final_audio_path)}[/bold green]\n\n"
            f"[bold yellow]📄 Roteiro de Texto:[/bold yellow]\n[cyan]{os.path.abspath(script_filepath)}[/cyan]",
            title="🎯 Áudio Digest (Voz de Podcast)",
            border_style="green"
        )
    )

    # Prévia do Roteiro Gerado
    console.print()
    console.print("[bold cyan]📜 Prévia da Narrativa Profissional:[/bold cyan]")
    preview_length = min(600, len(script_text))
    preview_text = script_text[:preview_length] + ("..." if len(script_text) > preview_length else "")
    console.print(Panel(preview_text, border_style="dim"))
    return True


def main():
    load_dotenv()
    args = parse_args()

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]🎓 Agente de IA: Tech Trends & Educational Podcast[/bold cyan]\n"
            "[dim]Narrativa Profissional ➔ Vozes Estilo Podcast (Francisca, Thalita, ElevenLabs) ➔ Áudio MP3[/dim]",
            border_style="cyan"
        )
    )
    console.print()

    if args.daily:
        import schedule
        console.print(f"[bold yellow]⏰ Modo Diário Ativado:[/bold yellow] O agente rodará todos os dias às [bold cyan]{args.schedule_time}[/bold cyan].")
        console.print("[dim]Executando a primeira rodada agora...[/dim]\n")

        # Executa imediatamente no arranque
        run_pipeline(args)

        # Agenda para rodar no horario especificado
        schedule.every().day.at(args.schedule_time).do(run_pipeline, args)

        console.print(f"\n[bold green]🔄 Agendador ativo.[/bold green] Aguardando próximo ciclo diário às {args.schedule_time} (Pressione Ctrl+C para encerrar)...")
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            console.print("\n[yellow]Agendador encerrado pelo usuário.[/yellow]")
            sys.exit(0)
    else:
        # Execucao avulsa única
        run_pipeline(args)


if __name__ == "__main__":
    main()
