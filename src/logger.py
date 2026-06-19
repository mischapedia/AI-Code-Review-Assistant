import structlog
import logging
import os
from pathlib import Path

def setup_logger(log_file: str = "logs/review.log", log_level: str = "INFO"):
    # Erstelle das logs-Verzeichnis, falls es nicht existiert
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Konfiguriere structlog
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    
    # Konfiguriere logging (stdlib) mit File-Handler
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Auch in Konsole ausgeben
        ]
    )
    
    return structlog.get_logger()

# Wir entfernen den globalen Aufruf von setup_logger(), damit er in main.py/reviewer.py mit der Config initialisiert werden kann.
