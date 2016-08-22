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

from ._fsnative import _encoding, path2fsn, is_win, is_unix
from ._compat import text_type, PY2, PY3
from ._winansi import AnsiState, ansi_split
from . import _winapi as winapi


def print_(*objects, **kwargs):
    """print_(*objects, sep=None, end=None, file=None, flush=False)

    Arguments:
        objects (object): zero or more objects to print
        sep (str): Object separator to use, defaults to ``" "``
        end (str): Trailing string to use, defaults to ``"\\n"``.
            If end is ``"\\n"`` then `os.linesep` is used.
        file (object): A file-like object, defaults to `sys.stdout`
        flush (bool): If the file stream should be flushed

    Like print(), but:

    * Supports printing filenames under Unix + Python 3 and Windows + Python 2
    * Emulates ANSI escape sequence support under Windows
    * Never fails due to encoding/decoding errors. Tries hard to get everything
      on screen as is, but will fall back to "?" if all fails.

    This does not conflict with ``colorama``, but will not use it on Windows.
    """

    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    file = kwargs.get("file", sys.stdout)
    flush = kwargs.get("flush", False)

    if end == "\n":
        end = os.linesep

    if is_win:
        _print_windows(objects, sep, end, file, flush)
    else:
        _print_default(objects, sep, end, file, flush)


def _print_default(objects, sep, end, file, flush):
    """A print_() implementation which writes bytes"""

    if is_win:
        encoding = "utf-8"
    else:
        encoding = _encoding()

    if isinstance(sep, text_type):
        sep = sep.encode(encoding, "replace")
    if not isinstance(sep, bytes):
        raise TypeError

    if isinstance(end, text_type):
        end = end.encode(encoding, "replace")
    if not isinstance(end, bytes):
        raise TypeError

    parts = []
    for obj in objects:
        if not isinstance(obj, text_type) and not isinstance(obj, bytes):
            obj = text_type(obj)
        if isinstance(obj, text_type):
            if PY2:
                obj = obj.encode(encoding, "replace")
            else:
                try:
                    obj = obj.encode(encoding, "surrogateescape")
                except UnicodeEncodeError:
                    obj = obj.encode(encoding, "replace")
        assert isinstance(obj, bytes)
        parts.append(obj)

    data = sep.join(parts) + end
    assert isinstance(data, bytes)

    file = getattr(file, "buffer", file)

    try:
        file.write(data)
    except TypeError:
        if is_unix and PY3:
            # For StringIO, first try with surrogates
            surr_data = os.fsdecode(data)
            try:
                file.write(surr_data)
            except (TypeError, ValueError):
                file.write(data.decode(encoding, "replace"))
        else:
            # for file like objects with don't support bytes
            file.write(data.decode(encoding, "replace"))

    if flush:
        file.flush()


ansi_state = AnsiState()


def _print_windows(objects, sep, end, file, flush):
    """The windows implementation of print_()"""

    h = winapi.INVALID_HANDLE_VALUE

    try:
        fileno = file.fileno()
    except (IOError, AttributeError):
        pass
    else:
        if fileno == 1:
            h = winapi.GetStdHandle(winapi.STD_OUTPUT_HANDLE)
        elif fileno == 2:
            h = winapi.GetStdHandle(winapi.STD_ERROR_HANDLE)

    if h == winapi.INVALID_HANDLE_VALUE:
        return _print_default(objects, sep, end, file, flush)

    # get the default value
    info = winapi.CONSOLE_SCREEN_BUFFER_INFO()
    if not winapi.GetConsoleScreenBufferInfo(h, ctypes.byref(info)):
        # not a console, fallback (e.g. redirect to file)
        return _print_default(objects, sep, end, file, flush)

    parts = []
    for obj in objects:
        if isinstance(obj, bytes):
            obj = obj.decode("mbcs", "replace")
        if not isinstance(obj, text_type):
            obj = text_type(obj)
        parts.append(obj)

    if isinstance(sep, bytes):
        sep = sep.decode("mbcs", "replace")
    if not isinstance(sep, text_type):
        raise TypeError

    if isinstance(end, bytes):
        end = end.decode("mbcs", "replace")
    if not isinstance(end, text_type):
        raise TypeError

    text = sep.join(parts) + end
    assert isinstance(text, text_type)

    # make sure we flush before we apply any console attributes
    file.flush()

    # try to force a utf-8 code page
    old_cp = winapi.GetConsoleOutputCP()
    encoding = "utf-8"
    if winapi.SetConsoleOutputCP(65001) == 0:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        old_cp = None

    for is_ansi, part in ansi_split(text):
        if is_ansi:
            ansi_state.apply(h, part)
        else:
            os.write(fileno, part.encode(encoding, 'replace'))

    # reset the code page to what we had before
    if old_cp is not None:
        winapi.SetConsoleOutputCP(old_cp)


def input_(prompt=None):
    """
    Args:
        prompt (object): Prints the passed object to stdout without
            adding a trailing newline
    Returns:
        `fsnative`

    Like :func:`python3:input` but returns a `fsnative` and allows printing
    filenames as prompt to stdout.

    Use :func:`fsn2text` on the result if you just want to deal with text.
    """

    if prompt is not None:
        print_(prompt, end="")

    data = getattr(sys.stdin, "buffer", sys.stdin).readline().rstrip(b"\r\n")
    return path2fsn(data)
