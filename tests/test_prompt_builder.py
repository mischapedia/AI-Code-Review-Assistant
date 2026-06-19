from src.prompt_builder import build_review_prompt

def test_t06_t07_prompt_creation(mock_mr_metadata):
    diff_text = "--- Datei: test.py ---\n[Zeile 1] print('test')"
    
    # Funktion ohne Parameter aufrufen (wie in deinem Code)
    prompt_template = build_review_prompt()
    
    # Jetzt formatieren wir den Prompt, um den Inhalt zu testen
    messages = prompt_template.format_messages(
        title=mock_mr_metadata["title"],
        author=mock_mr_metadata["author"],
        diff_text=diff_text
    )
    
    system_prompt = messages[0].content
    user_prompt = messages[1].content
    
    kategorien = ["Bugs", "Edge Cases", "Performance", "Security", "Code Style", "Lesbarkeit"]
    for kat in kategorien:
        assert kat in system_prompt
        
    assert mock_mr_metadata["title"] in user_prompt
    assert mock_mr_metadata["author"] in user_prompt
    assert diff_text in user_prompt
    assert "Kontext der betroffenen Dateien" in user_prompt
