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

import sys
import os
import ctypes

from ._fsnative import _fsencoding
from ._compat import text_type, PY3


def print_(*objects, **kwargs):
    """A print which supports bytes and str+surrogates under python3.

    Needed so we can print anything passed to us through argv and environ.
    Under Windows only text_type is allowed.

    Arguments:
        objects: one or more bytes/text
        linesep (bool): whether a line separator should be appended
        sep (bool): whether objects should be printed separated by spaces
    """

    linesep = kwargs.pop("linesep", True)
    sep = kwargs.pop("sep", True)
    file_ = kwargs.pop("file", None)
    if file_ is None:
        file_ = sys.stdout

    old_cp = None
    if os.name == "nt":
        # Try to force the output to cp65001 aka utf-8.
        # If that fails use the current one (most likely cp850, so
        # most of unicode will be replaced with '?')
        encoding = "utf-8"
        old_cp = ctypes.windll.kernel32.GetConsoleOutputCP()
        if ctypes.windll.kernel32.SetConsoleOutputCP(65001) == 0:
            encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            old_cp = None
    else:
        encoding = _fsencoding()

    try:
        if linesep:
            objects = list(objects) + [os.linesep]

        parts = []
        for text in objects:
            if isinstance(text, text_type):
                if PY3:
                    try:
                        text = text.encode(encoding, 'surrogateescape')
                    except UnicodeEncodeError:
                        text = text.encode(encoding, 'replace')
                else:
                    text = text.encode(encoding, 'replace')
            parts.append(text)

        data = (b" " if sep else b"").join(parts)
        try:
            fileno = file_.fileno()
        except (AttributeError, OSError, ValueError):
            # for tests when stdout is replaced
            try:
                file_.write(data)
            except TypeError:
                file_.write(data.decode(encoding, "replace"))
        else:
            file_.flush()
            os.write(fileno, data)
    finally:
        # reset the code page to what we had before
        if old_cp is not None:
            ctypes.windll.kernel32.SetConsoleOutputCP(old_cp)
