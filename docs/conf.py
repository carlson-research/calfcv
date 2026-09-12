import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "calfcv"
copyright = "2026, Carlson Research"
author = "Carlson Research"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "numpydoc",
    "sphinx_gallery.gen_gallery",
]

autosummary_generate = True
numpydoc_show_class_members = False

html_theme = "pydata_sphinx_theme"
html_static_path = []

sphinx_gallery_conf = {
    "examples_dirs": "../examples",
    "gallery_dirs": "auto_examples",
    "filename_pattern": r"/plot_",
    "download_all_examples": False,
}