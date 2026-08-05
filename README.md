<div align="center">

# 🎙️ Tech Trends Audio Digest

**Um podcast diário em áudio, gerado por IA, das melhores fontes de tecnologia do mundo — entregue direto no seu Discord.**

`Python` · `Groq/DeepSeek` · `Edge-TTS` · `GitHub Actions` · `Discord Webhook`

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-lint%20%2B%20test-green)](.github/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.1.0-ff69b4)](src/__init__.py)

</div>

---

## 📖 Visão Geral

O **Tech Trends Audio Digest** é um agente de IA residente que, todos os dias, monitora **50 das fontes mais relevantes de tecnologia do planeta**, transforma as principais novidades em uma **narrativa jornalística educacional** e a sintetiza em um **arquivo de áudio MP3** com voz humanizada — pronto para ser escutado no trajeto de manhã.

O diferencial vai além de *informar*: a cada episódio o agente **ensina um conceito técnico** usando analogias simples, conectando o que está acontecendo no mercado com o *porquê* de isso importar para engenheiros, arquitetos e gestores.

O resultado final pode ser enviado automaticamente para qualquer canal do **Discord** via webhook, totalmente **sem bot, sem servidor e sem custo de infraestrutura** — a rotina roda de graça na nuvem via **GitHub Actions**.

---

## ✨ Recursos

- 🌐 **50 fontes curadas de elite**, distribuídas em 5 categorias estratégicas (blogs de opinião, IA/LLMs, engenharia de big techs, portais de arquitetura e conteúdo em português).
- 🎓 **Pílula de conhecimento**: o roteiro explica o *conceito* por trás de cada notícia, não só o título.
- 🎙️ **Voz ultra-humanizada**: cadência e pausas de respiração estilo podcast (Edge-TTS), com fallback automático para gTTS.
- 📨 **Entrega no Discord**: envio do MP3 + resumo via webhook, reproduzível inline no canal.
- ⏰ **Rotina diária automática**: agendada via GitHub Actions, sem depender do seu computador.
- 🧪 **Qualidade de software**: testes unitários (pytest) e lint (ruff) com CI em múltiplas versões de Python.
- 🏷️ **Versionamento semântico** (SemVer) e Conventional Commits.

---

## ⚙️ Como Funciona

O agente é um pipeline de 3 etapas, cada uma implementada em um módulo independente:

```
┌─────────────┐      ┌──────────────────┐      ┌──────────────┐      ┌─────────────┐
│  1. Coleta   │ ──▶ │  2. Roteirização  │ ──▶ │  3. Síntese   │ ──▶ │  4. Entrega  │
│  src/fetcher │      │  src/summarizer  │      │    src/tts    │      │   Discord    │
└─────────────┘      └──────────────────┘      └──────────────┘      └─────────────┘
  Hacker News +     Narrativa narrativa       MP3 com voz            Webhook envia
  50 feeds RSS      educacional via LLM       humanizada             áudio + resumo
```

| Etapa | Módulo | Responsabilidade |
|---|---|---|
| **1. Coleta** | `fetcher.py` | Busca tendências no Hacker News e nos 50 feeds RSS curados, com deduplicação e balanço entre categorias. |
| **2. Roteirização** | `summarizer.py` | Chama a LLM (Groq/DeepSeek) para gerar um texto corrido, jornalístico e didático, sem tópicos ou marcadores. |
| **3. Síntese** | `tts.py` | Converte o roteiro em MP3 com pausas naturais; fallback em cascata: ElevenLabs → Edge-TTS → gTTS. |
| **4. Entrega** | `discord_utils.py` | Envia o MP3 e o resumo para o Discord via webhook. |

---

## 🧩 Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **Linguagem** | Python 3.10+ |
| **Sources** | Hacker News API + RSS via `feedparser` |
| **LLM** | Groq API (padrão `llama-3.3-70b-versatile`), compatível com DeepSeek |
| **TTS** | Microsoft Edge-TTS (SSML), fallback gTTS, opcional ElevenLabs |
| **Entrega** | Discord Webhook (`requests`) |
| **CI/CD** | GitHub Actions (cron diário + lint/test) |
| **Qualidade** | pytest · ruff |

---

## 📁 Estrutura do Projeto

```
.
├── src/
│   ├── __init__.py        # Versão do pacote (SemVer)
│   ├── sources.py         # Registrar das 50 fontes curadas
│   ├── fetcher.py         # Etapa 1: coleta de notícias
│   ├── summarizer.py      # Etapa 2: roteirização com LLM
│   ├── tts.py             # Etapa 3: síntese de voz
│   ├── discord_utils.py   # Etapa 4: entrega ao Discord
│   └── main.py            # CLI, orquestração, --daily e --send-discord
├── tests/                 # Testes unitários (pytest)
├── .github/workflows/     # CI (lint+test) e rotina diária
├── output/                # Áudios e roteiros gerados (ignorados pelo git)
├── .env.example           # Modelo de variáveis de ambiente
├── pyproject.toml         # Metadados, versão e dependências
├── requirements.txt       # Dependências de runtime
└── README.md
```

---

## 🚀 Começando

### Pré-requisitos
- Python 3.10+
- Uma chave de API gratuita do [Groq Console](https://console.groq.com/keys)

### 1. Clone e instale
```bash
git clone <sua-url-do-repositorio>
cd tendencias_tecnologia
pip install -r requirements.txt
```

### 2. Configure o ambiente
```bash
cp .env.example .env
```
Edite o `.env` com sua chave:
```env
GROQ_API_KEY=gsk_SuaChaveGroqAqui
GROQ_MODEL=llama-3.3-70b-versatile
TTS_VOICE=francisca
TTS_RATE=-3%
```

> O arquivo `.env` nunca deve ser versionado — ele fica protegido pelo `.gitignore`.

### 3. Rode o agente
```bash
python src/main.py --version        # confirma a versão
python src/main.py                  # gera o digest de hoje
python src/main.py --send-discord   # gera e envia para o Discord
```

---

## 📨 Envio para o Discord

O envio usa um **webhook**, o jeito mais simples e seguro de entregar o áudio em um canal — sem bot, sem permissões, sem custo.

1. No Discord: abra o canal → **Configurações do Canal** → **Integrações** → **Webhooks** → **Novo Webhook**.
2. Copie a URL e adicione ao `.env`:
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxx/yyyyy
   ```
3. Gere e envie:
   ```bash
   python src/main.py --send-discord
   ```

Você também pode passar a URL diretamente no comando:
```bash
python src/main.py --send-discord --discord-webhook "https://..."
```

---

## 🤖 Automação Diária (GitHub Actions)

Sem depender do seu computador, o GitHub Actions gera e entrega o digest todos os dias.

| Workflow | Quando roda |
|---|---|
| **Rotina diária** — gera o áudio e envia ao Discord | Todos os dias `11:00 UTC` (≈ 08:00 em Brasília) + acionamento manual |
| **Qualidade** — roda `pytest` (3 versões de Python) e `ruff` | Em todo `push` e `pull request` |

### Configure os Secrets do repositório
Em **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Obrigatório | Exemplo |
|---|---|---|
| `GROQ_API_KEY` | ✅ | `gsk_...` |
| `DISCORD_WEBHOOK_URL` | ✅ | `https://discord.com/api/webhooks/...` |
| `GROQ_MODEL` | ❌ (tem padrão) | `llama-3.3-70b-versatile` |
| `TTS_VOICE` | ❌ (tem padrão) | `francisca` |
| `TTS_RATE` | ❌ (tem padrão) | `-3%` |

> 💡 Bom saber: o cron do `daily.yml` usa **UTC**. Para outro horário, edite a linha `cron` (ex: `0 22 * * *` = 22:00 UTC).

---

## 🏷️ Versionamento e Padrões

O projeto adota **SemVer** (`MAJOR.MINOR.PATCH`) e **Conventional Commits**.

- A versão vive em dois pontos sincronizados: `pyproject.toml` e `src/__init__.py`.
- Consulte via CLI: `python src/main.py --version`.

### Convenção de commits
```
feat: adicionar envio para Discord via webhook
fix: corrigir fallback do Edge-TTS
tests: cobrir higienização do roteiro
docs: documentar secrets do GitHub Actions
chore: atualizar dependências
```

### Publicando uma release
```bash
git tag v0.2.0 && git push origin v0.2.0
```

---

## 🧪 Qualidade de Software

Antes de qualquer mudança, rode a suíte localmente:
```bash
pip install -r requirements-dev.txt
python -m pytest        # testes unitários
ruff check src tests    # lint
```

O workflow de CI (`ci.yml`) executa essas checagens automaticamente a cada mudança.

---

## 🔒 Segurança

- O `.env` real é ignorado pelo git e **nunca deve ser commitado**.
- Use apenas o `.env.example` como modelo.
- No GitHub, credenciais são gerenciadas **exclusivamente como Secrets**.
- ⚠️ **Recomendação:** se as chaves (`GROQ_API_KEY`, `ELEVENLABS_API_KEY`) já apareceram em qualquer log, **rotacione-as** gerando novas no painel do provedor antes de publicar o repositório.

---

## 🗺️ Roadmap

- [x] Coleta de 50 fontes curadas
- [x] Narrativa educacional via LLM
- [x] Síntese de voz humanizada (Edge-TTS + fallbacks)
- [x] Entrega diária no Discord via webhook
- [x] CI/CD e versionamento semântico
- [ ] Envio também como resumo em texto no Discord
- [ ] Suporte a múltiplos horários por fuso
- [ ] Dashboard de history/tendências dos episódios

---

## 📄 Licença

Este projeto está licenciado sob a licença **MIT** — consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">
Feito com 💜 para quem gosta de começar o dia bem informado.
</div>