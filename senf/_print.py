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
import re
import atexit

from ._fsnative import _encoding, path2fsn
from ._compat import text_type, PY2, PY3
from . import _winapi as winapi


def print_(*objects, **kwargs):
    """print_(*objects, sep=None, end=None, file=None, flush=False)

    Arguments:
        objects: none or more `bytes` or `text`
        sep (fsnative): Object separator to use, defaults to ``" "``
        end (fsnative): Trailing string to use, defaults to ``"\\n"``.
            If end is ``"\\n"`` then `os.linesep` is used.
        file (object): A file-like object, defaults to `sys.stdout`
        flush (bool): If the file stream should be flushed

    A print which supports printing bytes under Unix + Python 3 and Unicode
    under Windows + Python 2.

    In addition it interprets ANSI escape sequences on platforms which
    don't support them.
    """

    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    file = kwargs.get("file", sys.stdout)
    flush = kwargs.get("flush", False)

    if end == "\n":
        end = os.linesep

    if os.name == "nt" and file in (sys.__stdout__, sys.__stderr__):
        _print_windows(objects, sep, end, file, flush)
    else:
        _print_default(objects, sep, end, file, flush)


def _print_default(objects, sep, end, file, flush):
    """A print_() implementation which writes bytes"""

    if os.name == "nt":
        encoding = "utf-8"
    else:
        encoding = _encoding()

    if isinstance(sep, text_type):
        sep = sep.encode(encoding, "replace")

    if isinstance(end, text_type):
        end = end.encode(encoding, "replace")

    parts = []
    for obj in objects:
        if isinstance(obj, text_type):
            if PY2:
                obj = obj.encode(encoding, "replace")
            else:
                obj = obj.encode(encoding, "surrogateescape")
        parts.append(obj)

    data = sep.join(parts) + end

    file = getattr(file, "buffer", file)

    try:
        file.write(data)
    except TypeError:
        if os.name != "nt" and PY3:
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


class ANSI(object):

    SET_BOLD = '\033[1m'
    SET_DIM = '\033[2m'
    SET_ITALIC = '\033[3m'
    SET_UNDERLINE = '\033[4m'
    SET_BLINK = '\033[5m'
    SET_BLINK_FAST = '\033[6m'
    SET_REVERSE = '\033[7m'
    SET_HIDDEN = '\033[8m'

    RESET_ALL = '\033[0m'

    RESET_BOLD = '\033[21m'
    RESET_DIM = '\033[22m'
    RESET_ITALIC = '\033[23m'
    RESET_UNDERLINE = '\033[24m'
    RESET_BLINK = '\033[25m'
    RESET_BLINK_FAST = '\033[26m'
    RESET_REVERSE = '\033[27m'
    RESET_HIDDEN = '\033[28m'

    FG_BLACK= '\033[30m'
    FG_RED = '\033[31m'
    FG_GREEN = '\033[32m'
    FG_YELLOW = '\033[33m'
    FG_BLUE = '\033[34m'
    FG_MAGENTA = '\033[35m'
    FG_CYAN = '\033[36m'
    FG_WHITE = '\033[37m'

    FG_DEFAULT = '\033[39m'

    FG_LIGHT_BLACK= '\033[90m'
    FG_LIGHT_RED = '\033[91m'
    FG_LIGHT_GREEN = '\033[92m'
    FG_LIGHT_YELLOW = '\033[93m'
    FG_LIGHT_BLUE = '\033[94m'
    FG_LIGHT_MAGENTA = '\033[95m'
    FG_LIGHT_CYAN = '\033[96m'
    FG_LIGHT_WHITE = '\033[97m'

    BG_BLACK= '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    BG_DEFAULT = '\033[49m'

    BG_LIGHT_BLACK= '\033[100m'
    BG_LIGHT_RED = '\033[101m'
    BG_LIGHT_GREEN = '\033[102m'
    BG_LIGHT_YELLOW = '\033[103m'
    BG_LIGHT_BLUE = '\033[104m'
    BG_LIGHT_MAGENTA = '\033[105m'
    BG_LIGHT_CYAN = '\033[106m'
    BG_LIGHT_WHITE = '\033[107m'

_ANSI_ESC_RE = re.compile(u"(\x1b\[\d{1,3}m)")


class AnsiState(object):

    def __init__(self):
        self.default = None
        self.bold = False
        self.bg_light = False
        self.fg_light = False

    def apply(self, buffer_info, handle, code):
        attrs = buffer_info.wAttributes

        # We take the first attrs we see as default
        if self.default is None:
            self.default = attrs
            # Make sure that like with linux terminals the program doesn't
            # affect the prompt after it exits
            atexit.register(winapi.SetConsoleTextAttribute, handle, attrs)

        # In case the external state has changed, apply it it to ours.
        # Mostly the first time this is called.
        if attrs & winapi.FOREGROUND_INTENSITY and not self.fg_light \
                and not self.bold:
            self.fg_light = True
        if attrs & winapi.BACKGROUND_INTENSITY and not self.bg_light:
            self.bg_light = True

        fg_mask = attrs & (~0xF)
        bg_mask = attrs & (~0xF0)

        dark_fg = {
            ANSI.FG_BLACK: 0,
            ANSI.FG_RED: winapi.FOREGROUND_RED,
            ANSI.FG_GREEN: winapi.FOREGROUND_GREEN,
            ANSI.FG_YELLOW: winapi.FOREGROUND_GREEN | winapi.FOREGROUND_RED,
            ANSI.FG_BLUE: winapi.FOREGROUND_BLUE,
            ANSI.FG_MAGENTA: winapi.FOREGROUND_BLUE | winapi.FOREGROUND_RED,
            ANSI.FG_CYAN: winapi.FOREGROUND_BLUE | winapi.FOREGROUND_GREEN,
            ANSI.FG_WHITE: winapi.FOREGROUND_BLUE | winapi.FOREGROUND_GREEN |
                winapi.FOREGROUND_RED,
        }

        dark_bg = {
            ANSI.BG_BLACK: 0,
            ANSI.BG_RED: winapi.BACKGROUND_RED,
            ANSI.BG_GREEN: winapi.BACKGROUND_GREEN,
            ANSI.BG_YELLOW: winapi.BACKGROUND_GREEN | winapi.BACKGROUND_RED,
            ANSI.BG_BLUE: winapi.BACKGROUND_BLUE,
            ANSI.BG_MAGENTA: winapi.BACKGROUND_BLUE | winapi.BACKGROUND_RED,
            ANSI.BG_CYAN: winapi.BACKGROUND_BLUE | winapi.BACKGROUND_GREEN,
            ANSI.BG_WHITE: winapi.BACKGROUND_BLUE | winapi.BACKGROUND_GREEN |
                winapi.BACKGROUND_RED,
        }

        light_fg = {
            ANSI.FG_LIGHT_BLACK: 0,
            ANSI.FG_LIGHT_RED: winapi.FOREGROUND_RED,
            ANSI.FG_LIGHT_GREEN: winapi.FOREGROUND_GREEN,
            ANSI.FG_LIGHT_YELLOW: winapi.FOREGROUND_GREEN |
                winapi.FOREGROUND_RED,
            ANSI.FG_LIGHT_BLUE: winapi.FOREGROUND_BLUE,
            ANSI.FG_LIGHT_MAGENTA: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_RED,
            ANSI.FG_LIGHT_CYAN: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_GREEN,
            ANSI.FG_LIGHT_WHITE: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_GREEN | winapi.FOREGROUND_RED,
        }

        light_bg = {
            ANSI.BG_LIGHT_BLACK: 0,
            ANSI.BG_LIGHT_RED: winapi.BACKGROUND_RED,
            ANSI.BG_LIGHT_GREEN: winapi.BACKGROUND_GREEN,
            ANSI.BG_LIGHT_YELLOW: winapi.BACKGROUND_GREEN |
                                  winapi.BACKGROUND_RED,
            ANSI.BG_LIGHT_BLUE: winapi.BACKGROUND_BLUE,
            ANSI.BG_LIGHT_MAGENTA: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_RED,
            ANSI.BG_LIGHT_CYAN: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_GREEN,
            ANSI.BG_LIGHT_WHITE: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_GREEN | winapi.BACKGROUND_RED,
        }

        if code == ANSI.RESET_ALL:
            attrs = self.default
            self.bold = self.fg_light = self.bg_light = False
        elif code == ANSI.SET_BOLD:
            self.bold = True
        elif code == ANSI.RESET_BOLD:
            self.bold = False
        elif code == ANSI.SET_DIM:
            self.bold = False
        elif code == ANSI.SET_REVERSE:
            attrs |= winapi.COMMON_LVB_REVERSE_VIDEO
        elif code == ANSI.RESET_REVERSE:
            attrs &= ~winapi.COMMON_LVB_REVERSE_VIDEO
        elif code == ANSI.SET_UNDERLINE:
            attrs |= winapi.COMMON_LVB_UNDERSCORE
        elif code == ANSI.RESET_UNDERLINE:
            attrs &= ~winapi.COMMON_LVB_UNDERSCORE
        elif code == ANSI.FG_DEFAULT:
            attrs = (attrs & ~0xF) | (self.default & 0xF)
            self.fg_light = False
        elif code == ANSI.BG_DEFAULT:
            attrs = (attrs & ~0xF0) | (self.default & 0xF0)
            self.bg_light = False
        elif code in dark_fg:
            attrs = (attrs & ~0xF) | dark_fg[code]
            self.fg_light = False
        elif code in dark_bg:
            attrs = (attrs & ~0xF0) | dark_bg[code]
            self.bg_light = False
        elif code in light_fg:
            attrs = (attrs & ~0xF) | light_fg[code]
            self.fg_light = True
        elif code in light_bg:
            attrs = (attrs & ~0xF0) | light_bg[code]
            self.bg_light = True

        if self.fg_light or self.bold:
            attrs |= winapi.FOREGROUND_INTENSITY
        else:
            attrs &= ~winapi.FOREGROUND_INTENSITY

        if self.bg_light:
            attrs |= winapi.BACKGROUND_INTENSITY
        else:
            attrs &= ~winapi.BACKGROUND_INTENSITY

        winapi.SetConsoleTextAttribute(handle, attrs)


ansi_state = AnsiState()


def _print_windows(objects, sep, end, file, flush):
    """The windows implementation of print_()"""

    if file is sys.__stdout__:
        h = winapi.GetStdHandle(winapi.STD_OUTPUT_HANDLE)
    elif file is sys.__stderr__:
        h = winapi.GetStdHandle(winapi.STD_ERROR_HANDLE)
    else:
        assert 0

    if h == winapi.INVALID_HANDLE_VALUE:
        return _print_default(objects, sep, end, file, flush)

    # get the default value
    info = winapi.PCONSOLE_SCREEN_BUFFER_INFO()
    if not winapi.GetConsoleScreenBufferInfo(h, ctypes.byref(info)):
        # not a console, fallback (e.g. redirect to file)
        return _print_default(objects, sep, end, file, flush)

    parts = []
    for obj in objects:
        if isinstance(obj, bytes):
            obj = obj.decode("ascii", "replace")
        if not isinstance(obj, text_type):
            obj = text_type(obj)
        parts.append(obj)

    sep = path2fsn(sep)
    end = path2fsn(end)

    text = sep.join(parts) + end
    assert isinstance(text, text_type)

    # make sure we flush before we apply any console attributes
    file.flush()

    fileno = file.fileno()

    # try to force a utf-8 code page
    old_cp = winapi.GetConsoleOutputCP()
    encoding = "utf-8"
    if winapi.SetConsoleOutputCP(65001) == 0:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        old_cp = None

    for part in _ANSI_ESC_RE.split(text):
        if _ANSI_ESC_RE.match(part):
            ansi_state.apply(info, h, part)
        else:
            os.write(fileno, part.encode(encoding, 'replace'))

    # reset the code page to what we had before
    if old_cp is not None:
        winapi.SetConsoleOutputCP(old_cp)


def input_(prompt=None):
    """
    Args:
        prompt (`bytes` or `text`): Prints the passed text to stdout without
            a trailing newline
    Returns:
        `fsnative`

    Like :func:`python3:input` but returns a `fsnative` and allows printing
    `fsnative` as prompt to stdout.

    Use :func:`fsn2text` on the output if you just want to process text.
    """

    if prompt is not None:
        print_(prompt, end="")

    data = getattr(sys.stdin, "buffer", sys.stdin).readline().rstrip(b"\r\n")
    return path2fsn(data)
