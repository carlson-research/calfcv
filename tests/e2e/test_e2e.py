from unittest.mock import patch

from click.testing import CliRunner

from bib_ami.__main__ import main


def test_cli_help_e2e():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Thin client interface for citation verification" in result.output


@patch("webbrowser.open")
def test_cli_launch_e2e(mock_browser):
    runner = CliRunner()
    result = runner.invoke(main, ["launch"])
    assert result.exit_code == 0
    assert "Opening bib-ami web app" in result.output
    mock_browser.assert_called_once_with("https://bib-ami.com")


def test_cli_lookup_e2e(httpx_mock):
    httpx_mock.add_response(
        url="http://127.0.0.1:8000/v1/citations/lookup?query=10.1038/nature12345",
        json={"status": "Verified", "title": "Sample Nature Paper"},
    )

    runner = CliRunner()
    result = runner.invoke(main, ["lookup", "10.1038/nature12345"])

    assert result.exit_code == 0
    assert "Querying bib-ami API for '10.1038/nature12345'..." in result.output
    assert "Verified" in result.output


def test_cli_lookup_e2e_error(httpx_mock):
    # Simulate a 404 Not Found from the API
    httpx_mock.add_response(
        url="http://127.0.0.1:8000/v1/citations/lookup?query=invalid",
        status_code=404,
        json={"error": "Citation not found"},
    )

    runner = CliRunner()
    result = runner.invoke(main, ["lookup", "invalid"])

    # Ensure the CLI fails gracefully with a non-zero exit code
    assert result.exit_code != 0
    assert "Citation not found" in result.output or "Error" in result.output
