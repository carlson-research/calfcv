import httpx

from bib_ami.client import BibAmiClient


def test_lookup_citation_success(httpx_mock):
    # Intercept API request and mock a successful response
    httpx_mock.add_response(
        url="http://127.0.0.1:8000/v1/citations/lookup?query=10.1038/nature12345",
        json={
            "status": "Verified",
            "doi": "10.1038/nature12345",
            "title": "Sample Nature Paper",
        },
    )

    client = BibAmiClient()
    result = client.lookup_citation("10.1038/nature12345")

    assert result["status"] == "Verified"
    assert result["title"] == "Sample Nature Paper"


def test_lookup_citation_http_error(httpx_mock):
    # Intercept API request and simulate a 500 server error
    httpx_mock.add_response(
        url="http://127.0.0.1:8000/v1/citations/lookup?query=invalid", status_code=500
    )

    client = BibAmiClient()
    result = client.lookup_citation("invalid")

    assert "error" in result
    assert "API request failed" in result["error"]


def test_client_with_api_key(monkeypatch, httpx_mock):
    monkeypatch.setattr("bib_ami.client.API_KEY", "test-secret-key")
    httpx_mock.add_response(
        url="http://127.0.0.1:8000/v1/citations/lookup?query=test",
        json={"status": "ok"},
    )

    client = BibAmiClient()
    result = client.lookup_citation("test")

    assert client.http_client.headers["Authorization"] == "Bearer test-secret-key"
    assert result == {"status": "ok"}


def test_lookup_citation_timeout(httpx_mock):
    # Simulate a network timeout before the server responds
    httpx_mock.add_exception(httpx.ReadTimeout("Connection timed out"))

    client = BibAmiClient()
    result = client.lookup_citation("10.1038/nature12345")

    assert "error" in result
    assert "timeout" in result["error"].lower() or "failed" in result["error"].lower()
