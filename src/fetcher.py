"""
Modulo de Coleta de Tendencias e Noticias de Tecnologia.
Busca noticias recentes a partir de 50 fontes selecionadas (Hacker News API e Feeds RSS Curados).
"""

import logging
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

import feedparser
import requests

# Adiciona o diretorio raiz ao sys.path para garantir importacoes corretas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.sources import CURATED_SOURCES

logger = logging.getLogger(__name__)

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


def fetch_hacker_news(limit: int = 3, max_hours: int = 48) -> list[dict[str, Any]]:
    """
    Busca os principais topicos recentes do Hacker News via Firebase API.
    """
    articles = []
    try:
        response = requests.get(HN_TOP_STORIES_URL, timeout=8)
        response.raise_for_status()
        story_ids = response.json()[: limit * 3]

        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=max_hours)

        for story_id in story_ids:
            if len(articles) >= limit:
                break
            try:
                item_resp = requests.get(HN_ITEM_URL.format(id=story_id), timeout=4)
                if item_resp.status_code == 200:
                    item = item_resp.json()
                    if not item or item.get("type") != "story":
                        continue

                    time_sec = item.get("time")
                    if time_sec:
                        pub_date = datetime.fromtimestamp(time_sec, tz=timezone.utc)
                        if pub_date < cutoff_time:
                            continue
                    else:
                        pub_date = now

                    articles.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "summary": f"Pontuacao Hacker News: {item.get('score', 0)} pontos, {item.get('descendants', 0)} comentarios.",
                        "source": "Hacker News",
                        "category": "Opiniao & Mercado",
                        "published": pub_date.strftime("%Y-%m-%d %H:%M:%S")
                    })
            except requests.RequestException:
                continue

    except Exception as e:
        logger.warning(f"Aviso ao consultar Hacker News: {e}")

    return articles


def fetch_curated_rss_feeds(target_count: int = 6, max_hours: int = 72) -> list[dict[str, Any]]:
    """
    Coleta noticias recentes das 50 fontes curadas de tecnologia (Big Techs, Blogs de Arquitetura, IA e Conteudo BR).
    Embaralha as fontes dentro de cada categoria para garantir diversidade de conteudo a cada execucao.
    """
    articles = []
    now = datetime.now(timezone.utc)

    categories = {}
    for source in CURATED_SOURCES:
        cat = source["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(source)

    selected_feeds = []
    for cat_name, feed_list in categories.items():
        shuffled = list(feed_list)
        random.shuffle(shuffled)
        selected_feeds.extend(shuffled[:3])

    random.shuffle(selected_feeds)

    for feed_info in selected_feeds:
        if len(articles) >= target_count:
            break
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:2]:
                pub_date = now
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except Exception:
                        pub_date = now

                title = entry.get("title", "").strip()
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", "")).strip()

                if "<" in summary and ">" in summary:
                    import re
                    summary = re.sub(r"<[^>]+>", "", summary)[:300] + "..."
                else:
                    summary = summary[:300] + "..." if len(summary) > 300 else summary

                if title and not any(a["title"].lower() == title.lower() for a in articles):
                    articles.append({
                        "title": title,
                        "url": link,
                        "summary": summary,
                        "source": feed_info["name"],
                        "category": feed_info["category"],
                        "published": pub_date.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    break
        except Exception as e:
            logger.debug(f"Falha ao ler feed {feed_info['name']}: {e}")
            continue

    return articles


def get_daily_tech_trends(target_count: int = 6, max_hours: int = 72) -> list[dict[str, Any]]:
    """
    Orquestra a coleta de tendencias combinando Hacker News e as 50 fontes curadas de tecnologia.
    """
    hn_articles = fetch_hacker_news(limit=2, max_hours=max_hours)
    rss_articles = fetch_curated_rss_feeds(target_count=target_count, max_hours=max_hours)

    combined = []
    hn_idx, rss_idx = 0, 0
    while len(combined) < target_count and (hn_idx < len(hn_articles) or rss_idx < len(rss_articles)):
        if rss_idx < len(rss_articles):
            combined.append(rss_articles[rss_idx])
            rss_idx += 1
        if len(combined) < target_count and hn_idx < len(hn_articles):
            combined.append(hn_articles[hn_idx])
            hn_idx += 1

    remaining = rss_articles[rss_idx:] + hn_articles[hn_idx:]
    for item in remaining:
        if len(combined) >= target_count:
            break
        combined.append(item)

    return combined


if __name__ == "__main__":
    import json
    trends = get_daily_tech_trends(target_count=6)
    print(f"Coletadas {len(trends)} tendencias a partir das 50 fontes curadas:")
    print(json.dumps(trends, indent=2, ensure_ascii=False))
