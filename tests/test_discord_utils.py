"""Testes unitários para o módulo src/discord_utils."""

from src.discord_utils import resolve_webhook_url, truncate_for_discord


class TestTruncateForDiscord:
    def test_short_text_unchanged(self):
        assert truncate_for_discord("ola") == "ola"

    def test_empty_text(self):
        assert truncate_for_discord("") == ""

    def test_truncates_with_ellipsis_without_cutting_words(self):
        text = "a" * 3000
        result = truncate_for_discord(text)
        assert len(result) <= 2000
        assert result.endswith("...")

    def test_strips_whitespace(self):
        assert truncate_for_discord("  ola  ") == "ola"


class TestResolveWebhookUrl:
    def test_explicit_beats_env(self, monkeypatch):
        monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://env.example")
        assert resolve_webhook_url("https://explicit.example") == "https://explicit.example"

    def test_falls_back_to_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://env.example")
        assert resolve_webhook_url(None) == "https://env.example"

    def test_none_when_unset(self, monkeypatch):
        monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
        assert resolve_webhook_url(None) is None
