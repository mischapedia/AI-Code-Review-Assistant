from unittest.mock import MagicMock
from src.gitlab_client import GitLabClient

def test_t03_get_mr_metadata(mock_mr_metadata):
    client = GitLabClient("https://test.com", "token")
    mock_gl = MagicMock()
    
    mock_gl.projects.get.return_value.mergerequests.get.return_value = MagicMock(
        title=mock_mr_metadata["title"],
        description=mock_mr_metadata["description"],
        author={"username": mock_mr_metadata["author"]}
    )
    client.gl = mock_gl
    
    result = client.get_mr_metadata(7757, 7)
    # hier korrigiert:
    assert result["title"] == "Test MR für IPA"
    assert result["author"] == "Calvin.Pfrender"

def test_t04_get_mr_diffs(mock_raw_diff):
    client = GitLabClient("https://test.com", "token")
    mock_gl = MagicMock()
    
    mock_mr = MagicMock()
    mock_mr.changes.return_value = {"changes": mock_raw_diff}
    mock_gl.projects.get.return_value.mergerequests.get.return_value = mock_mr
    client.gl = mock_gl
    
    diffs = client.get_mr_diffs(7757, 7)
    assert len(diffs) == 1
    assert diffs[0]["new_path"] == "src/main.py"

def test_get_file_content():
    client = GitLabClient("https://test.com", "token")
    mock_gl = MagicMock()
    
    mock_file = MagicMock()
    mock_file.content = b"print('hello world')"
    mock_gl.projects.get.return_value.files.get.return_value = mock_file
    client.gl = mock_gl
    
    content = client.get_file_content(7757, "src/main.py", "main")
    assert content == "print('hello world')"

def test_t10_post_comment():
    client = GitLabClient("https://test.com", "token")
    mock_gl = MagicMock()
    
    mock_mr = MagicMock()
    mock_gl.projects.get.return_value.mergerequests.get.return_value = mock_mr
    client.gl = mock_gl
    
    client.post_comment(7757, 7, "Guter Code!")
    
    mock_mr.notes.create.assert_called_once()
    args, _ = mock_mr.notes.create.call_args
    assert "Guter Code!" in args[0]["body"]
