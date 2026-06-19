from langchain_core.prompts import ChatPromptTemplate

def build_review_prompt() -> ChatPromptTemplate:

    # Dieser Prompt wurde mit Unterstützung von ChatGPT präzisiert
    system_prompt = """Du bist ein erfahrener Software-Entwickler und führst ein Code-Review durch.
Analysiere die folgenden Code-Änderungen basierend auf diesen 6 Kategorien:
1. Bugs (Logikfehler, Null-Pointer)
2. Edge Cases (Grenzfälle, die nicht beachtet wurden)
3. Performance (Ressourcenverbrauch)
4. Security (Sicherheitslücken)
5. Code Style (Namensgebung, Konventionen)
6. Lesbarkeit (Komplexität)

Formatiere dein Feedback ZEILENBEZOGEN (z.B. 'Datei X, Zeile Y: ...').
Sei einfach und präzise! Wenn der Code gut ist, erwähne das kurz."""

    user_prompt = """Merge Request Titel: {title}
Autor: {author}

Hier ist der Kontext der betroffenen Dateien (Vollständiger Inhalt und Diffs):
{diff_text}

Bitte gib mir dein Review:"""

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    return prompt_template