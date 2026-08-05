# 🎙️ Tech Trends Audio Digest Agent (Notícias + Ensino + 50 Fontes Curadas)

Um agente de Inteligência Artificial modular em Python que busca diariamente notícias e análises de **50 das melhores fontes técnicas do mundo**, gera um resumo roteirizado e educacional via **Groq / DeepSeek**, e sintetiza um arquivo de áudio MP3 de alta qualidade utilizando **Microsoft Edge TTS com SSML** (e fallback para **gTTS**).

---

## 🌟 Principais Destaques

- 🌐 **50 Fontes Curadas de Elite**: Coleta automática dividida em 5 categorias estratégicas:
  1. **Blogs Pessoais & Opinião Forte**: Fabio Akita (AkitaOnRails), Martin Fowler, Gergely Orosz (The Pragmatic Engineer), Julia Evans, Dan Abramov (Overreacted), Joel Spolsky, Gregor Hohpe, Chip Huyen, Lilian Weng, Alberto Romero.
  2. **Inteligência Artificial, LLMs & ML**: Hugging Face, Latent Space, OpenAI, Google DeepMind, LangChain, Towards Data Science, LlamaIndex, AI Snake Oil, Jay Alammar, MarkTechPost.
  3. **Engenharia de Big Techs**: Netflix TechBlog, GitHub Engineering, Cloudflare, Uber, Discord, Spotify, Stripe, AWS Architecture, Canva, DoorDash.
  4. **Portais & Arquitetura de Software**: InfoQ, Better Stack Community, Architecture Notes, The New Stack, DZone, HackerNoon, TLDR Tech, Dev.to, Hashnode, Red Hat.
  5. **Canais e Conteúdo em Português**: TabNews, Manual do Usuário (Rodrigo Ghedin), Filipe Deschamps, BrazilJS, Blog do Diego Eis, iMasters, Zup Innovation, Ezequiel Lanza, Pagar.me/Stone.
- 🎓 **Pílula de Conhecimento Tech (Ensino)**: Além de informar o giro de notícias, o agente seleciona um conceito importante e ensina ao ouvinte com uma analogia simples da vida real.
- 🎙️ **Voz Ultra-Humanizada**: Pausas de respiração e cadência ajustada no Edge-TTS.
- ⏰ **Execução Diária Automatizada**: Suporte a daemon interno (`--daily`) e agendamento nativo no Windows (`schedule_daily.ps1`).

---

## 📂 Estrutura do Projeto

```
tendencias_tecnologia/
├── src/
│   ├── __init__.py      # Versão do pacote (Ex: 0.1.0)
│   ├── sources.py       # Registro das 50 fontes curadas de tecnologia
│   ├── fetcher.py       # Coleta inteligente e balanceada pelas 5 categorias
│   ├── summarizer.py    # Geração de roteiro informativo + educacional (Groq/DeepSeek)
│   ├── tts.py           # Síntese SSML de voz ultra-humanizada (Edge-TTS / gTTS)
│   ├── discord_utils.py # Envio do áudio para o Discord via webhook
│   └── main.py          # Script principal (CLI, --daily e --send-discord)
├── tests/               # Testes unitários (pytest)
├── output/              # Arquivos finais (.mp3 e .txt) salvos por data
├── schedule_daily.ps1   # Agendador automático para Windows Task Scheduler
├── .github/workflows/   # CI/CD: ci.yml (lint+test) e daily.yml (rotina diária)
├── .env.example         # Modelo de variáveis de ambiente
├── .gitignore           # Protege .env e artefatos gerados
├── pyproject.toml       # Metadados, versão e dependências
├── requirements.txt     # Dependências Python
└── README.md            # Documentação completa
```

---

## 🛠️ Instalação e Execução

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar `.env`
Adicione sua chave de API gratuita do [Groq Console](https://console.groq.com/keys) no `.env`:

```env
GROQ_API_KEY=gsk_SuaChaveGroqAqui
GROQ_MODEL=llama-3.3-70b-versatile
TTS_VOICE=pt-BR-AntonioNeural
TTS_RATE=-1%
```

### 3. Rodar o Agente
```bash
python src/main.py
```

### 4. Rodar em Modo Diário Automatizado
```bash
python src/main.py --daily --schedule-time 08:00
```
Ou no Windows:
```powershell
.\schedule_daily.ps1
```

---

## 📨 Envio Diário para o Discord (Webhook)

O agente pode enviar o MP3 gerado diretamente para qualquer canal do Discord usando um **webhook** (sem precisar de bot ou permissões especiais). O áudio aparece inline e pode ser reproduzido na hora.

### 1. Criar um webhook no Discord
1. Abra o canal desejado → **Configurações do Canal** (ícone de engrenagem).
2. Vá em **Integrações → Webhooks → Novo Webhook**.
3. Dê um nome (ex: "Tech Trends") e **Copiar URL do Webhook**.

### 2. Configurar
Adicione a URL no `.env`:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxx/yyyyy
```

### 3. Enviar o áudio
```bash
python src/main.py --send-discord
# ou informe a URL diretamente:
python src/main.py --send-discord --discord-webhook "https://..."
```

No GitHub Actions, a URL vai como um **Secret** (veja abaixo), não no `.env`.

---

## 🤖 Execução Diária Automática via GitHub Actions

A rotina diária roda na nuvem (não depende do seu PC ficar ligado) e envia o áudio ao Discord:

| Workflow | Arquivo | Quando roda |
|---|---|---|
| Rótina diária `generate-and-send` | `.github/workflows/daily.yml` | Todos os dias às `11:00 UTC` (≈ 08:00 em Brasília) + **acionamento manual** na aba *Actions* |
| Qualidade `test` + `lint` | `.github/workflows/ci.yml` | Em todo `push` e `pull request` |

### Configurar os Secrets do repositório
No GitHub: **Settings → Secrets and variables → Actions → New repository secret**. Valor vazio em `.env` no CI não é um problema — as variáveis vêm daqui:

| Secret | Obligatório | Exemplo |
|---|---|---|
| `GROQ_API_KEY` | ✅ | `gsk_...` |
| `GROQ_MODEL` | ❌ (tem padrão) | `llama-3.3-70b-versatile` |
| `DISCORD_WEBHOOK_URL` | ✅ (para o envio) | `https://discord.com/api/webhooks/...` |
| `TTS_VOICE` | ❌ (tem padrão) | `francisca` |
| `TTS_RATE` | ❌ (tem padrão) | `-3%` |

> **Ajuste de horário:** o cron do `daily.yml` usa **UTC**. Para mudar o horário, edite a linha `cron` (ex: `0 8 * * *` = 08:00 UTC).

---

## 🏷️ Versionamento e Boas Práticas

O projeto segue **SemVer** (`MAJOR.MINOR.PATCH`) e **Conventional Commits**.

- A versão atual está em **dois lugares sincronizados**:
  - `pyproject.toml` → `[project] version = "0.1.0"`
  - `src/__init__.py` → `__version__ = "0.1.0"`
- Consulte a versão via CLI: `python src/main.py --version`.

### Convenção de commits
```
feat: adicionar envio para Discord via webhook
fix: corrigir fallback do Edge-TTS
chore: atualizar dependências
tests: cobrir função de higienização do roteiro
docs: documentar secrets do GitHub Actions
```

### Bump de versão
1. Aumente `version` em `pyproject.toml` e `__version__` em `src/__init__.py`.
2. Crie uma **tag** semântica para releases: `git tag v0.1.0 && git push origin v0.1.0`.
3. (Opcional) gitignore já protege `.env`, `output/` e artefatos — rode testes antes de commitar:
   ```bash
   pip install -r requirements-dev.txt
   python -m pytest        # testes
   ruff check src tests    # lint
   ```

---

## 🧪 Qualidade de Software (CI)

O workflow `ci.yml` roda, em toda mudança, **testes em 3 versões de Python** (`pytest`) e **lint** (`ruff`). Para rodar localmente:
```bash
pip install -r requirements-dev.txt
python -m pytest
ruff check src tests
```

---

## ⚠️ Segurança

- O arquivo `.env` real está no `.gitignore` e **não deve ser commitado**.
- Use apenas o `.env.example` como referência.
- No GitHub, credenciais vão **sempre** como **Secrets**, nunca no código.
- ⚠️ **Recomendação:** por já terem sido exibidos em logs, rotacione (gere novas) as chaves `GROQ_API_KEY` e `ELEVENLABS_API_KEY` no painel de cada provedor antes de publicar o repositório.
