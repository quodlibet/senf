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

import os

from ._fsnative import py2fsn
from ._compat import PY2, text_type
from ._environ import del_windows_env_var, set_windows_env_var, environ


sep = py2fsn(os.sep)
pathsep = py2fsn(os.pathsep)
curdir = py2fsn(os.curdir)
pardir = py2fsn(os.pardir)
altsep = py2fsn(os.altsep) if os.altsep is not None else None
extsep = py2fsn(os.extsep)
devnull = py2fsn(os.devnull)
defpath = py2fsn(os.defpath)


def expanduser():
    """Like os.path.expanduser but supports unicode user names under Win+Py2"""
    pass


def expandvars():
    """Like os.path.expanduser but supports unicode variables under Win+Py2"""
    pass


def getcwd():
    """Like `os.getcwd` but returns a fsnative path

    Returns:
        `fsnative`
    """

    if os.name == "nt" and PY2:
        return os.getcwdu()
    return os.getcwd()


def getenv(key, value=None):
    """Like `os.getenv` but returns unicode under Windows + Python 2

    Args:
        key (fsnative): The env var to get
        value (object): The value to return if the env var does not exist
    Returns:
        `fsnative` or `object`:
            The env var or the passed value if it doesn't exist
    """

    if os.name == "nt" and PY2:
        key = text_type(key)
        return environ.get(key, value)
    return os.getenv(key, value)


def unsetenv(key):
    """Like `os.unsetenv` but takes unicode under Windows + Python 2

    Args:
        key (fsnative): The env var to unset
    """

    if os.name == "nt":
        # python 3 has no unsetenv under Windows -> use our ctypes one as well
        key = text_type(key)
        try:
            del_windows_env_var(key)
        except WindowsError:
            pass
    else:
        os.unsetenv(key)


def putenv(key, value):
    """Like `os.putenv` but takes unicode under Windows + Python 2

    Args:
        key (fsnative): The env var to get
        value (object): The value to return if the env var does not exist
    """

    if os.name == "nt" and PY2:
        key = text_type(key)
        value = text_type(value)
        try:
            set_windows_env_var(key, value)
        except WindowsError:
            pass
    else:
        os.putenv(key, value)


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
