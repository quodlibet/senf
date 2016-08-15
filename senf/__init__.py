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

from ._fsnative import fsnative, py2fsn
from ._print import print_
from ._stdlib import sep, pathsep, curdir, pardir, altsep, extsep, devnull, \
    defpath, getcwd, getenv, unsetenv, putenv
from ._argv import argv
from ._environ import environ


fsnative, print_, py2fsn, getcwd, getenv, unsetenv, putenv


version = (0, 0, 0)
"""Tuple[`int`, `int`, `int`]: The version tuple (major, minor, micro)"""


version_string = ".".join(map(str, version))
"""`str`: A version string"""


environ = environ
"""Dict[`fsnative`, `fsnative`]: Like `os.environ` but contains unicode keys
and values under Windows + Python 2
"""


argv = argv
"""List[`fsnative`]: Like `sys.argv` but contains unicode under
Windows + Python 2
"""


sep = sep
"""`fsnative`: Like os.sep or os.path.sep but a fsnative path"""


pathsep = pathsep
"""`fsnative`: Like os.pathsep but a fsnative path"""


curdir = curdir
"""`fsnative`: Like os.curdir but a fsnative path"""


pardir = pardir
"""`fsnative`: Like os.pardir but a fsnative path"""


altsep = altsep
"""`fsnative` or `None`: Like os.altsep but a fsnative path"""


extsep = extsep
"""`fsnative`: Like os.extsep but a fsnative path"""


devnull = devnull
"""`fsnative`: Like os.devnull but a fsnative path"""


defpath = defpath
"""`fsnative`: Like os.defpath but a fsnative path"""
