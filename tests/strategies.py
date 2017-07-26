# -*- coding: utf-8 -*-
# Copyright 2017 Christoph Reiter
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys

from hypothesis.strategies import composite, sampled_from, characters, lists, \
    integers, binary


@composite
def filenames(draw):
    s = []

    if os.name == "nt":
        if sys.version_info[0] == 3:
            unichr_ = chr
        else:
            unichr_ = unichr
        surrogate = integers(
            min_value=0xD800, max_value=0xDFFF).map(lambda i: unichr_(i))
        one_char = sampled_from(draw(characters(blacklist_characters=u"\x00")))
        any_char = sampled_from([draw(one_char), draw(surrogate)])
        any_text = lists(any_char).map(lambda l: u"".join(l))

        windows_path_text = any_text
        s.append(windows_path_text)

        def text_to_bytes(path):
            fs_enc = sys.getfilesystemencoding()
            try:
                return path.encode(fs_enc, "surrogatepass")
            except UnicodeEncodeError:
                return path.encode(fs_enc, "replace")

        windows_path_bytes = windows_path_text.map(text_to_bytes)
        s.append(windows_path_bytes)
    else:
        unix_path_bytes = binary().map(lambda b: b.replace(b"\x00", b" "))
        s.append(unix_path_bytes)

        if sys.version_info[0] == 3:
            unix_path_text = unix_path_bytes.map(
                lambda b: b.decode(
                    sys.getfilesystemencoding(), "surrogateescape"))
            s.append(unix_path_text)

    return draw(sampled_from(list(map(draw, s))))


class _PathLike(object):

    def __init__(self, value):
        self._value = value

    def __fspath__(self):
        return self._value


@composite
def pathlikes(draw):
    filename = draw(filenames())

    if hasattr(os, "fspath"):
        return draw(sampled_from([filename, _PathLike(filename)]))
    else:
        return filename