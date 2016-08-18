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

from ._fsnative import path2fsn
from ._compat import PY2


sep = path2fsn(os.sep)
pathsep = path2fsn(os.pathsep)
curdir = path2fsn(os.curdir)
pardir = path2fsn(os.pardir)
altsep = path2fsn(os.altsep) if os.altsep is not None else None
extsep = path2fsn(os.extsep)
devnull = path2fsn(os.devnull)
defpath = path2fsn(os.defpath)


def getcwd():
    """Like `os.getcwd` but returns a `fsnative` path

    Returns:
        `fsnative`
    """

    if os.name == "nt" and PY2:
        return os.getcwdu()
    return os.getcwd()
