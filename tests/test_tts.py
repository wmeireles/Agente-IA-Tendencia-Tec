"""Testes unitários para o módulo src/tts.py (funções puras de voz)."""
from src.tts import get_edge_voice_name, prepare_text_for_natural_pacing


class TestGetEdgeVoiceName:
    def test_alias_francisca(self):
        assert get_edge_voice_name("francisca") == "pt-BR-FranciscaNeural"

    def test_alias_thalita(self):
        assert get_edge_voice_name("thalita") == "pt-BR-ThalitaMultilingualNeural"

    def test_alias_antonio(self):
        assert get_edge_voice_name("antonio") == "pt-BR-AntonioNeural"

    def test_full_name_matches_by_substring(self):
        assert get_edge_voice_name("pt-BR-ThalitaMultilingualNeural") == "pt-BR-ThalitaMultilingualNeural"

    def test_unknown_falls_back_to_francisca(self):
        assert get_edge_voice_name("sem-voz") == "pt-BR-FranciscaNeural"

    def test_case_insensitive(self):
        assert get_edge_voice_name("ANTONIO") == "pt-BR-AntonioNeural"


class TestPrepareTextForNaturalPacing:
    def test_adds_period_when_missing(self):
        assert prepare_text_for_natural_pacing("Fala pessoal") == "Fala pessoal."

    def test_preserves_existing_punctuation(self):
        assert prepare_text_for_natural_pacing("Ola!") == "Ola!"

    def test_joins_paragraphs_with_blank_line(self):
        result = prepare_text_for_natural_pacing("Primeiro parágrafo\n\nSegundo parágrafo")
        assert result == "Primeiro parágrafo.\n\nSegundo parágrafo."
