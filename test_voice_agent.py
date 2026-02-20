import pytest
from unittest.mock import patch, MagicMock
import sys
import voice_agent


@patch("subprocess.run")
def test_copy_to_clipboard_wayland(mock_run, capsys):
    voice_agent.copy_to_clipboard("test text")
    mock_run.assert_called_with(["wl-copy"], input=b"test text", check=True)
    captured = capsys.readouterr()
    assert "Copied to clipboard!" in captured.err


@patch("subprocess.run")
def test_copy_to_clipboard_xclip(mock_run, capsys):
    mock_run.side_effect = [FileNotFoundError, MagicMock()]
    voice_agent.copy_to_clipboard("test text")
    mock_run.assert_called_with(
        ["xclip", "-selection", "clipboard"], input=b"test text", check=True
    )
    captured = capsys.readouterr()
    assert "Copied to clipboard!" in captured.err


@patch("voice_agent.google.auth.default", return_value=(MagicMock(), None))
def test_transcribe_audio_no_project_id(mock_auth_default):
    with patch("sys.exit", side_effect=SystemExit(1)):
        with patch("builtins.print") as mock_print:
            with pytest.raises(SystemExit):
                voice_agent.transcribe_audio()
            mock_print.assert_called_with(
                "Error: Could not determine project ID from Application Default Credentials. Set GOOGLE_CLOUD_PROJECT.",
                file=sys.stderr,
            )


@patch("voice_agent.google.auth.default", return_value=(MagicMock(), "test-project"))
@patch("voice_agent.SpeechClient", create=True)
def test_transcribe_audio_exception(mock_speech_client, mock_auth_default):
    mock_client_instance = mock_speech_client.return_value
    mock_client_instance.recognize.side_effect = Exception("API error")

    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = b"test audio"
    with patch("builtins.open", return_value=mock_file):
        with patch("builtins.print") as mock_print:
            res = voice_agent.transcribe_audio()
            mock_print.assert_called_with(
                "Transcription failed: API error", file=sys.stderr
            )
            assert res == ""
