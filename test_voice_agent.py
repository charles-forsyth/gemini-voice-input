import pytest
from unittest.mock import patch, MagicMock
import voice_agent

@patch("subprocess.run")
def test_copy_to_clipboard_wayland(mock_run, capsys):
    voice_agent.copy_to_clipboard("test text")
    mock_run.assert_called_with(['wl-copy'], input=b"test text", check=True)
    captured = capsys.readouterr()
    assert "Copied to clipboard!" in captured.err

@patch("subprocess.run")
def test_copy_to_clipboard_xclip(mock_run, capsys):
    # Simulate wl-copy failing
    mock_run.side_effect = [FileNotFoundError, MagicMock()]
    voice_agent.copy_to_clipboard("test text")
    mock_run.assert_called_with(['xclip', '-selection', 'clipboard'], input=b"test text", check=True)
    captured = capsys.readouterr()
    assert "Copied to clipboard!" in captured.err

