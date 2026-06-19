from src.config_loader import get_config
from src.gitlab_client import GitLabClient
from src.diff_processor import process_diffs
from src.prompt_builder import build_review_prompt
from src.llm_adapter import get_llm
import time
import structlog

def run_review(project_id: int, mr_id: int, dry_run: bool = False):
    logger = structlog.get_logger()
    start_time = time.time()
    config = get_config()

    log_context = {
        "mr_id": mr_id,
        "project_id": project_id,
        "llm": f"{config.llm_provider}/{config.llm_model}"
    }

    logger.info("Starte MR-Review", **log_context)

    try:
        # ---- 1 Daten holen
        client = GitLabClient(config.gitlab_url, config.gitlab_token)
        metadata = client.get_mr_metadata(project_id, mr_id)
        raw_diffs = client.get_mr_diffs(project_id, mr_id)

        # Hole vollständige Dateiinhalte für alle geänderten Dateien
        full_files = {}
        # Wir brauchen die Referenz (Branch/Commit), um die Dateien zu holen. 
        # In einem MR ist das normalerweise der Source Branch.
        # GitLab API: MR hat ein 'source_branch' Attribut.
        
        # Da get_mr_metadata nur title, description, author liefert, 
        # müssen wir den MR erneut abfragen oder metadata erweitern.
        # Für den Moment nutzen wir den MR-Objekt-Zugriff über den Client.
        project = client.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_id)
        # Use the commit hash of the MR head for fetching files to ensure we get the correct version
        ref = mr.sha

        for diff in raw_diffs:
            file_path = diff.get('new_path')
            if file_path and not diff.get('deleted_file'):
                try:
                    content = client.get_file_content(project_id, file_path, ref)
                    # Store content with its size for sorting
                    full_files[file_path] = content
                except Exception as e:
                    logger.warning(f"Konnte Dateiinhalt für {file_path} nicht laden: {e}", **log_context)

        # ---- 2 Diffs verarbeiten
        # Sort files by size (smallest first) to maximize number of files we can include
        # or by "importance" (e.g. files with more changes)
        sorted_files = dict(sorted(full_files.items(), key=lambda item: len(item[1])))
        
        # Dynamically fit into a reasonable budget
        budget = config.context_budget
        current_size = 0
        files_to_include = {}
        
        for path, content in sorted_files.items():
            if current_size + len(content) <= budget:
                files_to_include[path] = content
                current_size += len(content)
            else:
                logger.debug(f"Datei {path} übersprungen, um Context Window zu schonen", **log_context)

        diff_text = process_diffs(raw_diffs, files_to_include)
        if not diff_text.strip():
            logger.info("Keine änderungen im MR gefunden. Abbruch.", **log_context)
            return

    
        # ---- 3 Prompt bauen
        prompt = build_review_prompt()
        llm = get_llm(config)
        chain = prompt | llm

        # Vorbereite die Eingaben für den Prompt
        prompt_inputs = {
            "title": metadata.get('title', 'Unbekannt'),
            "author": metadata.get('author', 'Unbekannt'),
            "diff_text": diff_text
        }
        
        # Trace Logging: Logge den finalen Prompt (wenn DEBUG aktiviert ist)
        # Da prompt ist ein Template, rendern wir es manuell für das Log
        full_prompt_text = prompt.format(
            title=prompt_inputs["title"],
            author=prompt_inputs["author"],
            diff_text=prompt_inputs["diff_text"]
        )
        logger.debug("LLM Prompt:", prompt=full_prompt_text, **log_context)

        logger.info("Sende Daten an LLM...", **log_context)

        response = chain.invoke(prompt_inputs)
        
        # Trace Logging: Logge die Antwort des LLM
        logger.debug("LLM Response:", response=response.content, **log_context)

        review_result = response.content
        # -- Prefix für AI generiert
        tagged_result = f"**[AI-Review by {config.llm_provider}/{config.llm_model} with temperature {config.llm_temperature}]**\n\n{review_result}"

    
        # ---- 4 Kommentar posten oder in die Konsole ausgeben

        if dry_run:
            print("\n" + "="*50)
            print("DRY-RUN ERGEBNIS (Wird nicht gepostet):")
            print("="*50)
            print(tagged_result)
        else:
            client.post_comment(project_id, mr_id, tagged_result)
            logger.info("Review-Kommentar erfolgreich gepostet.", **log_context)

        # Erfolgs Logging

        duration = round(time.time() - start_time, 2)
        logger.info("Review abgeschlossen", status="erfolgreich", dauer_sekunden=duration, **log_context)

    except Exception as e:
        # expeption, Prozess nicht blockieren, aber loggen.
        duration = round(time.time() - start_time, 2)
        logger.error("Fehler während des Reviews", error=str(e), status="fehler", dauer_sekunden=duration, **log_context)
        if dry_run:
            print(f"Ein Fehler ist aufgetreten: {e}")
