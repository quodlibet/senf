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


def ansi_parse(code):
    """Returns command, (args)"""

    return code[-1:], tuple([int(v or "0") for v in code[2:-1].split(";")])


def ansi_split(text, _re=re.compile(u"(\x1b\[(\d*;?)*\S)")):
    """Yields (is_ansi, text)"""

    for part in _re.split(text):
        if part:
            yield (bool(_re.match(part)), part)


class AnsiCommand(object):
    TEXT = "m"


class TextAction(object):
    RESET_ALL = 0

    SET_BOLD = 1
    SET_DIM = 2
    SET_ITALIC = 3
    SET_UNDERLINE = 4
    SET_BLINK = 5
    SET_BLINK_FAST = 6
    SET_REVERSE = 7
    SET_HIDDEN = 8

    RESET_BOLD = 21
    RESET_DIM = 22
    RESET_ITALIC = 23
    RESET_UNDERLINE = 24
    RESET_BLINK = 25
    RESET_BLINK_FAST = 26
    RESET_REVERSE = 27
    RESET_HIDDEN = 28

    FG_BLACK = 30
    FG_RED = 31
    FG_GREEN = 32
    FG_YELLOW = 33
    FG_BLUE = 34
    FG_MAGENTA = 35
    FG_CYAN = 36
    FG_WHITE = 37

    FG_DEFAULT = 39

    FG_LIGHT_BLACK = 90
    FG_LIGHT_RED = 91
    FG_LIGHT_GREEN = 92
    FG_LIGHT_YELLOW = 93
    FG_LIGHT_BLUE = 94
    FG_LIGHT_MAGENTA = 95
    FG_LIGHT_CYAN = 96
    FG_LIGHT_WHITE = 97

    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47

    BG_DEFAULT = 49

    BG_LIGHT_BLACK = 100
    BG_LIGHT_RED = 101
    BG_LIGHT_GREEN = 102
    BG_LIGHT_YELLOW = 103
    BG_LIGHT_BLUE = 104
    BG_LIGHT_MAGENTA = 105
    BG_LIGHT_CYAN = 106
    BG_LIGHT_WHITE = 107


class AnsiState(object):

    def __init__(self):
        self.default_attrs = None

        self.bold = False
        self.bg_light = False
        self.fg_light = False

    def do_text_action(self, attrs, action):
        # In case the external state has changed, apply it it to ours.
        # Mostly the first time this is called.
        if attrs & winapi.FOREGROUND_INTENSITY and not self.fg_light \
                and not self.bold:
            self.fg_light = True
        if attrs & winapi.BACKGROUND_INTENSITY and not self.bg_light:
            self.bg_light = True

        dark_fg = {
            TextAction.FG_BLACK: 0,
            TextAction.FG_RED: winapi.FOREGROUND_RED,
            TextAction.FG_GREEN: winapi.FOREGROUND_GREEN,
            TextAction.FG_YELLOW: winapi.FOREGROUND_GREEN |
                winapi.FOREGROUND_RED,
            TextAction.FG_BLUE: winapi.FOREGROUND_BLUE,
            TextAction.FG_MAGENTA: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_RED,
            TextAction.FG_CYAN: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_GREEN,
            TextAction.FG_WHITE: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_GREEN | winapi.FOREGROUND_RED,
        }

        dark_bg = {
            TextAction.BG_BLACK: 0,
            TextAction.BG_RED: winapi.BACKGROUND_RED,
            TextAction.BG_GREEN: winapi.BACKGROUND_GREEN,
            TextAction.BG_YELLOW: winapi.BACKGROUND_GREEN |
                winapi.BACKGROUND_RED,
            TextAction.BG_BLUE: winapi.BACKGROUND_BLUE,
            TextAction.BG_MAGENTA: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_RED,
            TextAction.BG_CYAN: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_GREEN,
            TextAction.BG_WHITE: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_GREEN | winapi.BACKGROUND_RED,
        }

        light_fg = {
            TextAction.FG_LIGHT_BLACK: 0,
            TextAction.FG_LIGHT_RED: winapi.FOREGROUND_RED,
            TextAction.FG_LIGHT_GREEN: winapi.FOREGROUND_GREEN,
            TextAction.FG_LIGHT_YELLOW: winapi.FOREGROUND_GREEN |
                winapi.FOREGROUND_RED,
            TextAction.FG_LIGHT_BLUE: winapi.FOREGROUND_BLUE,
            TextAction.FG_LIGHT_MAGENTA: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_RED,
            TextAction.FG_LIGHT_CYAN: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_GREEN,
            TextAction.FG_LIGHT_WHITE: winapi.FOREGROUND_BLUE |
                winapi.FOREGROUND_GREEN | winapi.FOREGROUND_RED,
        }

        light_bg = {
            TextAction.BG_LIGHT_BLACK: 0,
            TextAction.BG_LIGHT_RED: winapi.BACKGROUND_RED,
            TextAction.BG_LIGHT_GREEN: winapi.BACKGROUND_GREEN,
            TextAction.BG_LIGHT_YELLOW: winapi.BACKGROUND_GREEN |
                                  winapi.BACKGROUND_RED,
            TextAction.BG_LIGHT_BLUE: winapi.BACKGROUND_BLUE,
            TextAction.BG_LIGHT_MAGENTA: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_RED,
            TextAction.BG_LIGHT_CYAN: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_GREEN,
            TextAction.BG_LIGHT_WHITE: winapi.BACKGROUND_BLUE |
                winapi.BACKGROUND_GREEN | winapi.BACKGROUND_RED,
        }

        if action == TextAction.RESET_ALL:
            attrs = self.default_attrs
            self.bold = self.fg_light = self.bg_light = False
        elif action == TextAction.SET_BOLD:
            self.bold = True
        elif action == TextAction.RESET_BOLD:
            self.bold = False
        elif action == TextAction.SET_DIM:
            self.bold = False
        elif action == TextAction.SET_REVERSE:
            attrs |= winapi.COMMON_LVB_REVERSE_VIDEO
        elif action == TextAction.RESET_REVERSE:
            attrs &= ~winapi.COMMON_LVB_REVERSE_VIDEO
        elif action == TextAction.SET_UNDERLINE:
            attrs |= winapi.COMMON_LVB_UNDERSCORE
        elif action == TextAction.RESET_UNDERLINE:
            attrs &= ~winapi.COMMON_LVB_UNDERSCORE
        elif action == TextAction.FG_DEFAULT:
            attrs = (attrs & ~0xF) | (self.default_attrs & 0xF)
            self.fg_light = False
        elif action == TextAction.BG_DEFAULT:
            attrs = (attrs & ~0xF0) | (self.default_attrs & 0xF0)
            self.bg_light = False
        elif action in dark_fg:
            attrs = (attrs & ~0xF) | dark_fg[action]
            self.fg_light = False
        elif action in dark_bg:
            attrs = (attrs & ~0xF0) | dark_bg[action]
            self.bg_light = False
        elif action in light_fg:
            attrs = (attrs & ~0xF) | light_fg[action]
            self.fg_light = True
        elif action in light_bg:
            attrs = (attrs & ~0xF0) | light_bg[action]
            self.bg_light = True

        if self.fg_light or self.bold:
            attrs |= winapi.FOREGROUND_INTENSITY
        else:
            attrs &= ~winapi.FOREGROUND_INTENSITY

        if self.bg_light:
            attrs |= winapi.BACKGROUND_INTENSITY
        else:
            attrs &= ~winapi.BACKGROUND_INTENSITY

        return attrs

    def apply(self, buffer_info, handle, code):
        attrs = buffer_info.wAttributes

        # We take the first attrs we see as default
        if self.default_attrs is None:
            self.default_attrs = attrs
            # Make sure that like with linux terminals the program doesn't
            # affect the prompt after it exits
            atexit.register(
                winapi.SetConsoleTextAttribute, handle, self.default_attrs)

        cmd, args = ansi_parse(code)
        if cmd == AnsiCommand.TEXT:
            for action in args:
                attrs = self.do_text_action(attrs, action)
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

    for is_ansi, part in ansi_split(text):
        if is_ansi:
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
