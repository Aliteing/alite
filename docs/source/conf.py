# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
""" Configuration file for the Sphinx documentation builder.

Changelog
---------
.. versionadded::    23.06
    |br| first version of config (09)
    |br| added attempt to mock decorators (14)
    |br| supress warning for namedtuple (27)

|   **Open Source Notification:** This file is part of open source program **Alite**
|   **Copyright © 2023  Carlo Oliveira** <carlo@nce.ufrj.br>,
|   **SPDX-License-Identifier:** `GNU General Public License v3.0 or later <https://is.gd/3Udt>`_.
|   `Labase <http://labase.selfip.org/>`_ - `NCE <http://portal.nce.ufrj.br>`_ - `UFRJ <https://ufrj.br/>`_.

.. codeauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

"""
import sys
import pathlib
import unittest.mock as mock
path = pathlib.Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(path))
from dash import Configuration as Cfg
from functools import wraps
import collections


def remove_namedtuple_attrib_docstring(app, what, name, obj, skip, options):
    # noinspection PyProtectedMember
    if type(obj) is collections._tuplegetter:
        return True
    return skip


def setup(app):
    app.connect('autodoc-skip-member', remove_namedtuple_attrib_docstring)


def mock_decorator(*args, **kwargs):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args_, **kwargs_):
            return f(*args_, **kwargs_)
        return decorated_function
    return decorator


MOCK_MODULES = ['nameko', 'matplotlib', 'seaborn', 'nameko.rpc']
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = mock.Mock()
# mock.patch('nameko.rpc.rpc', mock_decorator).start()
mock_rpc = mock.Mock(name="mock_rpc_decorator")
mock_rpc.rpc.return_value.side_effect = mock_decorator
sys.modules['nameko.rpc'] = mock_rpc

project = 'Alite-Dash'
copyright = f'© 2023, Carlo E. T. Oliveira, version {Cfg.version}'
author = 'Carlo E. T. Oliveira'
release = Cfg.version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('../../tests/'))


# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx_rtd_theme',
              'sphinx_toolbox.more_autodoc.autonamedtuple']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'
exclude_patterns = []

language = 'pt_BR'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
