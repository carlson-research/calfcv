import webbrowser
from bib_ami.config import WEB_URL


def open_web_app(url: str | None = None) -> None:
    """Opens the bib-ami web interface in the user's default browser."""
    target_url = url or WEB_URL
    print(f"Opening bib-ami web app: {target_url}")
    webbrowser.open(target_url)
