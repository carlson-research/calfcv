import click
from bib_ami.launch import open_web_app
from bib_ami.client import BibAmiClient
from bib_ami._version import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """bib-ami: Thin client interface for citation verification."""
    pass


@main.command()
@click.option("--url", default=None, help="Custom URL for the web application.")
def launch(url: str | None):
    """Launch the interactive web interface in your default browser."""
    open_web_app(url)


@main.command()
@click.argument("identifier")
def lookup(identifier: str):
    """Look up a DOI, arXiv ID, or reference identifier via the API."""
    client = BibAmiClient()
    click.echo(f"Querying bib-ami API for '{identifier}'...")

    result = client.lookup_citation(identifier)

    if "error" in result:
        raise click.ClickException(result["error"])

    click.echo(result)


if __name__ == "__main__":
    main()
