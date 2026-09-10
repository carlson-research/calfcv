from unittest.mock import patch
from bib_ami.launch import open_web_app


@patch("webbrowser.open")
def test_open_web_app_default(mock_browser_open):
    open_web_app()
    mock_browser_open.assert_called_once_with("https://bib-ami.com")


@patch("webbrowser.open")
def test_open_web_app_custom_url(mock_browser_open):
    open_web_app("https://custom.bib-ami.com")
    mock_browser_open.assert_called_once_with("https://custom.bib-ami.com")
