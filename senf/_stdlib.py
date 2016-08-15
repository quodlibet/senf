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
    """Like os.getcwd() but returns a fsnative path"""
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
