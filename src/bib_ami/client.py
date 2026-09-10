import httpx
from bib_ami.config import API_URL, API_KEY


class BibAmiClient:
    """Lightweight HTTP client for interacting with the remote bib-ami API."""

    def __init__(self):
        headers = {"User-Agent": "bib-ami/1.0.0"}
        if API_KEY:
            headers["Authorization"] = f"Bearer {API_KEY}"

        self.http_client = httpx.Client(base_url=API_URL, headers=headers, timeout=10.0)

    def lookup_citation(self, identifier: str) -> dict:
        """Queries the bib-ami API for a citation or DOI lookup."""
        try:
            response = self.http_client.get(
                "/citations/lookup", params={"query": identifier}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as err:
            return {"error": f"API request failed: {err}"}
