"""
Modulo de Processamento e Roteirizacao Profissional de Podcast (Groq / DeepSeek API).
Gera uma narrativa fluida, profunda e profissional em formato de monólogo narrativo (sem tópicos ou marcadores).
"""

import os
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um especialista em tecnologia, arquiteto de software e apresentador de um podcast técnico de alto nível.
Sua missão é transformar as principais notícias e artigos técnicos em um EPISÓDIO NARRATIVO PROFISSIONAL, FLUIDO E PROFUNDO.

DIRETRIZES FUNDAMENTAIS DE ESTILO E NARRATIVA:
1. NADA DE LISTAS OU TÓPICOS:
   - É ESTRITAMENTE PROIBIDO usar marcadores de tópicos como "Notícia 1", "Primeiro tópico", "Notícia 2", "Segunda novidade", etc.
   - O roteiro deve ser um texto corrido e jornalístico, onde um assunto se conecta organicamente ao próximo por afinidade (infraestrutura, IA, arquitetura, gestão).
2. EXPLIQUE O QUE AS COISAS REALMENTE SIGNIFICAM:
   - Não apenas leia os títulos ou resumos superficiais! Explique O QUE a tecnologia realmente é, COMO ela funciona na prática e QUAL É O IMPACTO REAL para engenheiros, empresas e arquitetura de sistemas.
   - Se uma notícia fala de "Autenticação Pós-Quântica" ou "Banco Colunar", explique o conceito técnico em linguagem clara, mostrando o motivo pelo qual isso é uma mudança importante na indústria.
3. TOM DE VOZ PROFISSIONAL E ENGAJANTE:
   - Tom de um Tech Lead ou CTO conversando com outros profissionais de tecnologia: maduro, perspicaz, analítico e sem sensacionalismo.
   - Use conectores narrativos elegantes: "No campo da infraestrutura de rede,", "Enquanto isso, quando olhamos para a arquitetura de dados,", "Essa mudança traz uma reflexão importante sobre...", "Do ponto de vista de engenharia,".
4. FORMATO E EXTENSÃO:
   - Duração falada: aproximadamente 3 a 4 minutos (500 a 650 palavras).
   - Idioma: Português do Brasil (pt-BR) impecável.
   - REGRAS PARA O SINTETIZADOR DE VOZ (TTS): NENHUM marcador markdown (sem **, #, *, listas), NENHUMA direção de palco ([música], [risos]), use pontuação natural para ditar as pausas de fala.
"""


def generate_podcast_script(
    articles: List[Dict[str, Any]],
    api_key: str = None,
    model_name: str = None
) -> str:
    """
    Recebe a lista de noticias/artigos e gera um roteiro narrativo profissional e aprofundado utilizando Groq / DeepSeek.
    """
    if not articles:
        raise ValueError("Nenhuma noticia foi fornecida para a geracao do roteiro.")

    key = api_key or os.environ.get("GROQ_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not key or key == "gsk_sua_chave_groq_aqui":
        raise ValueError(
            "GROQ_API_KEY nao foi configurada. "
            "Por favor, insira sua chave da API no arquivo .env"
        )

    selected_model = model_name or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Monta os dados brutos para o prompt
    formatted_articles = ""
    for idx, item in enumerate(articles, start=1):
        formatted_articles += (
            f"Fonte/Artigo {idx}:\n"
            f"• Título: {item['title']}\n"
            f"• Origem: {item['source']} (Categoria: {item.get('category', 'Geral')})\n"
            f"• Resumo/Conteúdo: {item['summary']}\n\n"
        )

    user_prompt = (
        "Com base nos artigos e análises abaixo, crie o roteiro completo do episódio de hoje em formato NARRATIVO PROFISSIONAL CONTINUO. "
        "Não use tópicos ou listas numeradas. Conecte os assuntos, explique o que as tecnologias significam e mostre seu impacto real no mercado:\n\n"
        f"{formatted_articles}"
    )

    try:
        client = Groq(api_key=key)

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            model=selected_model,
            temperature=0.7,
            max_completion_tokens=2000,
        )

        response_text = chat_completion.choices[0].message.content
        if not response_text:
            raise RuntimeError("O modelo retornou uma resposta vazia.")

        # Limpeza de blocos <think> do DeepSeek se houver
        if "<think>" in response_text and "</think>" in response_text:
            import re
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)

        script = clean_script_for_tts(response_text)

        return script

    except Exception as e:
        logger.error(f"Erro ao chamar API do Groq/DeepSeek: {e}")
        raise RuntimeError(f"Falha na geração do roteiro: {e}")


def clean_script_for_tts(text: str) -> str:
    """
    Higieniza o roteiro para leitura narrativa fluida no TTS.
    """
    import re
    # Remove titulos (#, ##, etc)
    text = re.sub(r'#+\s*', '', text)
    # Remove negrito e italico (**, *, __, _)
    text = re.sub(r'\*{1,2}|_{1,2}', '', text)
    # Remove marcadores de lista ou numeracoes no inicio de linhas
    text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*(?:Notícia|Tópico|Item|Número)?\s*\d+[:.]?\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
    # Remove colchetes ou parenteses com instrucoes de palco
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\((?:risos|musica|pausa|vinheta|vinheta de abertura|efeito sonora?)\)', '', text, flags=re.IGNORECASE)
    
    # Organiza em parágrafos bem espaçados para cadência de fala
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    return '\n\n'.join(paragraphs)


if __name__ == "__main__":
    test_articles = [
        {"title": "Post-quantum authentication to origins is now supported", "source": "Cloudflare Blog", "category": "Infra & Edge", "summary": "Cloudflare agora suporta autenticação pós-quântica em conexões de origem."},
        {"title": "Consenso demora. Decisão travada custa mais", "source": "Blog do Diego Eis", "category": "Gestão & Tech BR", "summary": "Buscar unanimidade em times de engenharia adia decisões importantes e gera gargalos."},
        {"title": "Handbook.md e a limitação de governança de agentes", "source": "Hacker News", "category": "IA & Agentes", "summary": "Documentos longos de política não são suficientes para controlar comportamento de agentes LLM."}
    ]
    try:
        script = generate_podcast_script(test_articles)
        print("Roteiro Narrativo Profissional Gerado:\n")
        print(script)
    except Exception as err:
        print(f"Erro: {err}")
