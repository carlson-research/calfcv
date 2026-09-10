# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add the src directory to sys.path so autodoc can discover bib_ami
sys.path.insert(0, os.path.abspath("../src"))

from bib_ami import __version__  # noqa: E402

project = "bib-ami"
copyright = "2025–2026, Carlson Research"
author = "Rolf Carlson"
version = ".".join(__version__.split(".")[:2])
release = __version__

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

autodoc_typehints = "description"
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
