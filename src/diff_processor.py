def process_diffs(raw_diffs: list, full_files: dict = None) -> str:
    """
    Formatiert die rohen GitLab-Diffs und optional die vollständigen Dateiinhalte in einen lesbaren Text für das LLM.
    """
    processed_text = []

    for diff in raw_diffs:
        file_path = diff.get('new_path')
        diff_content = diff.get('diff', '')

        # Überspringe gelöschte Dateien oder Dateien ohne Diff
        if diff.get('deleted_file') or not diff_content:
            continue
            
        processed_text.append(f"--- Datei: {file_path} ---")
        
        if full_files and file_path in full_files:
            processed_text.append("Vollständiger Dateiinhalt:")
            processed_text.append(full_files[file_path])
            processed_text.append("\nÄnderungen (Diff):")
            
        processed_text.append(diff_content)
        processed_text.append("-" * 40)
        
    return "\n".join(processed_text)
