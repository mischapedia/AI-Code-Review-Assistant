from src.diff_processor import process_diffs

def test_t05_diff_parsing(mock_raw_diff):
    result = process_diffs(mock_raw_diff)
    assert "--- Datei: src/main.py" in result

def test_diff_with_full_files(mock_raw_diff):
    full_files = {"src/main.py": "def hello():\n    print('hello')"}
    result = process_diffs(mock_raw_diff, full_files=full_files)
    assert "Vollständiger Dateiinhalt:" in result
    assert "def hello():" in result
    assert "Änderungen (Diff):" in result
