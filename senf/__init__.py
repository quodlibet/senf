# -*- coding: utf-8 -*-
# Copyright 2016 Christoph Reiter
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""
senf makes filename handing easier by papering over platform differences
in Python 2 and by making it easier to migrate to Python 3 or to have a mixed
Py2/Py3 code base. While at it, it improves the Unicode support for Python 2
under Windows.

It supports Python 2.6, 2.7, 3.3+, works with PyPy, and only depends on the
stdlib.

The core type it introduces is the "fsnative" type which actually is

* unicode under Py2 + Windows
* str under Py2 on other platforms
* str under Py3 + Windows
* str+surrogateescape under Py3 on other platforms [0]

The type is used for file names, environment variables and process arguments
and senf provides functions so you can tread it as an opaque type and not have
to worry about its content or encoding.

The other nice thing about the fsnative type is that you can mix it with ASCII
str on all Python versions and platforms [1] which means minimal change to you
code:

::

    os.path.join(some_fsnative_path, "somefile")
    some_fsnative_path.endswith(".txt")
    some_fsnative_path == "foo.txt"

For unicode text you will need to use the `fsnative` wrapper:

::

    os.path.join(some_fsnative_path, fsnative(u"Gewürze"))


The provided functions and constants can be split into three categories:

1) Helper functions to work with the fsnative type
2) Alternative implementations of stdlib functions for introducing Unicode
   support under Windows + Python 2 (os.environ for example)
3) Wrappers for constants and functions which don't return a fsnative path
   by default (os.sep, mkdtemp() with default arguments)

senf does not monkey patch stdlib functions, it just provides alternatives and
wrappers.

----

[0] Under Python 3, bytes is also a valid type for paths under Unix.
    We decide to not use/allow it as there are stdlib modules, like pathlib,
    which don't support bytes and mixing bytes with str+surrogateescape
    doesn't work.
[1] As long as you don't use "unicode_literals", which we strongly recommend.
"""


version = (0, 0, 0)
"""The version tuple (major, minor, micro)"""


version_string = u".".join(map(str, version))
"""A version string"""


environ = None
"""Like os.environ but supports unicode under Win+Py2"""


argv = None
"""Like os.environ but supports unicode under Win+Py2"""


def expanduser():
    """Like os.path.expanduser but supports unicode user names under Win+Py2"""
    pass


def expandvars():
    """Like os.path.expanduser but supports unicode variables under Win+Py2"""
    pass


def fsnative(text):
    """Takes text and returns a fsnative path object."""
    pass


def path2fsn(path):
    """Returns a fsnative path for a bytes path under Py3+Unix.
    If the passed in path is a fsnative path simply returns it.

    This is useful for interfaces which need so support bytes paths under Py3.
    """
    pass


def is_fsnative(path):
    """Returns whether the passed path is a fsnative object"""
    pass


def fsn2text():
    """Converts a path to text. This process is not reversible and should
    only be used for display purposes.
    """
    pass


def fsn2bytes(path, encoding):
    """Turns a path to bytes. If the path is not associated with an encoding
    the passed encoding is used (under Windows for example)
    """
    pass


def bytes2fsn(data, encoding):
    """Turns bytes to a path. If the path is not associated with an encoding
    the passed encoding is used (under Windows for example)
    """
    pass


def py2fsn():
    """Turns certain internal paths exposed by Python 2 to a fsnative path
    e.g. senf.__path__[0]
    """
    pass


def getcwd():
    """Like os.getcwd() but returns a fsnative path"""
    pass


sep = None
"""Like os.sep but a fsnative path"""


pathsep = None
"""Like os.pathsep but a fsnative path"""


curdir = None
"""Like os.curdir but a fsnative path"""


pardir = None
"""Like os.pardir but a fsnative path"""


altsep = None
"""Like os.altsep but a fsnative path"""


extsep = None
"""Like os.extsep but a fsnative path"""


devnull = None
"""Like os.devnull but a fsnative path"""


defpath = None
"""Like os.defpath but a fsnative path"""


def print_():
    """Like print but handles fsnative paths, e.g. unix byte paths can be
    printed as is. Also supports unicode output under Windows.
    """
    pass


def uri2fsn():
    """Takes a file URI and returns a fsnative path"""
    pass


def fsn2uri():
    """Takes a fsnative path and returns a file URI"""
    pass


def getenv():
    """Like os.getenv() but supports unicode under Win+Py2"""
    pass


def unsetenv():
    """Like os.unsetenc() but supports unicode under Win+Py2"""
    pass


def putenv():
    """Like os.putenv() but supports unicode under Win+Py2"""
    pass


def mkdtemp():
    """Like tempfile.mkdtemp(), but always returns a fsnative path"""
    pass


def mkstemp():
    """Like tempfile.mkstemp(), but always returns a fsnative path"""
    pass


def format_exc():
    """"""
    pass


def format_exception():
    """"""
    pass


def extract_tb():
    """"""
    pass
