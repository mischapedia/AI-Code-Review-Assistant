import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """
    Konfigurationsklasse für GitLab-Zugriff.
    """
    gitlab_url: str
    gitlab_token: str
    llm_provider: str
    llm_model: str
    llm_temperature: float
    openrouter_api_key: str
    use_litellm: bool
    log_level: str
    max_file_size: int
    context_budget: int

def get_config() -> Config:
    """
    Liest die benötigten Umgebungsvariablen aus
    und gibt eine Config-Instanz zurück.
    """
    gitlab_url = os.getenv("GITLAB_URL")
    gitlab_token = os.getenv("GITLAB_TOKEN")

    # Prüft ob beide Variablen vorhanden sind
    if not gitlab_url or not gitlab_token:
        raise ValueError("GITLAB_URL und GITLAB_TOKEN fehlen")
    
    return Config(
        gitlab_url=gitlab_url,
        gitlab_token=gitlab_token,
        llm_provider=os.getenv("LLM_PROVIDER", "ollama").lower(),
        llm_model=os.getenv("LLM_MODEL", "codellama"),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        use_litellm = os.getenv("USE_LITELLM", "false").lower() in ("true", "1", "yes"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        max_file_size=int(os.getenv("MAX_FILE_SIZE", "10000")),
        context_budget=int(os.getenv("CONTEXT_BUDGET", "200000")),
    )
