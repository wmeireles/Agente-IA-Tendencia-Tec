"""Testes unitários para o módulo src/summarizer.py (higienização de roteiro)."""
from src.summarizer import clean_script_for_tts


class TestCleanScriptForTts:
    def test_removes_markdown_headers(self):
        result = clean_script_for_tts("# Título Principal")
        assert "#" not in result
        assert "Título Principal" in result

    def test_removes_bold_and_italic(self):
        assert "**" not in clean_script_for_tts("**destaque**")
        assert "__" not in clean_script_for_tts("__sublinhado__")

    def test_removes_bullet_list_markers(self):
        result = clean_script_for_tts("- item um\n- item dois")
        assert "-" not in result

    def test_removes_stage_directions(self):
        result = clean_script_for_tts("Vinheta de abertura. [música de fundo]")
        assert "[música de fundo]" not in result

    def test_joins_paragraphs(self):
        result = clean_script_for_tts("Linha 1.\nLinha 2.")
        assert "\n\n" in result