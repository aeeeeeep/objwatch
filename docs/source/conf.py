# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'ObjWatch'
copyright = '2025 aeeeeeep'
author = 'aeeeeeep'

try:
    from pathlib import Path

    this_dir = Path(__file__).parent.parent.parent
    version = (this_dir / 'version.txt').read_text()
except (ImportError, FileNotFoundError):
    version = '0.0.0'

release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',        # Google-style docstring support
    'sphinx.ext.intersphinx',     # Cross-referencing between projects
    'sphinx.ext.todo',            # TODO directive support
    'sphinx.ext.autosectionlabel', # Automatic section labels
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
    "special-members": "__init__, __call__",
    "member-order": "bysource"
}

templates_path = ['_templates']
exclude_patterns = []

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_preprocess_types = True

# Intersphinx mapping for cross-referencing
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# Enable TODO directives
todo_include_todos = True

# Auto section label prefixes
autosectionlabel_prefix_document = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"

# HTML theme options for better UX (furo specific)
html_theme_options = {
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/aeeeeeep/objwatch",
    "source_branch": "main",
    "source_directory": "docs/source/",
    "navigation_with_keys": True,
}

# Add syntax highlighting
pygments_style = "friendly"
pygments_dark_style = "monokai"

# Enable copy button for code blocks
html_copy_source = True
html_show_sourcelink = True

# Search functionality
html_use_index = True
html_domain_indices = True
