# -*- coding: utf-8 -*-

import os
import sys

dir_ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_)
sys.path.insert(0, os.path.abspath(os.path.join(dir_, "..")))
import senf

needs_sphinx = "1.3"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/2.7', None),
    'python3': ('https://docs.python.org/3.5', None),
}
source_suffix = '.rst'
master_doc = 'index'
project = 'senf'
copyright = u'2016, Christoph Reiter'
version = senf.version_string
release = senf.version_string
exclude_patterns = ['_build']

autodoc_member_order = "bysource"
default_role = "obj"

html_theme = "sphinx_rtd_theme"
html_favicon = "images/favicon.ico"
html_theme_options = {
    "display_version": False,
}
