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

from hypothesis import given, strategies, settings

from senf import fsnative, text2fsn, fsn2text, bytes2fsn, fsn2bytes, print_, \
    path2fsn, fsn2uri, uri2fsn
from senf._fsnative import fsn2norm
from senf._compat import text_type, StringIO

from tests.hypothesis_fspaths import fspaths


is_wine = "WINEDEBUG" in os.environ


@given(fspaths().map(os.path.basename))
@settings(max_examples=1000)
def test_any_pathnames(path):
    fsn = path2fsn(path)
    abspath = os.path.abspath(fsn)
    if os.path.isabs(abspath):
        if is_wine:
            # FIXME: fails on native Windows
            assert uri2fsn(fsn2uri(abspath)) == abspath


@given(fspaths(allow_pathlike=False))
@settings(max_examples=1000)
def test_any_normalize(path):
    fsn = path2fsn(path)

    assert path2fsn(path) == fsn2norm(fsn)

    assert bytes2fsn(fsn2bytes(fsn, "utf-8"), "utf-8") == fsn2norm(fsn)

    if isinstance(path, text_type):
        assert text2fsn(path) == fsn2norm(text2fsn(path))


@given(fspaths())
@settings(max_examples=1000)
def test_any_filenames(path):
    if isinstance(path, fsnative):
        assert path2fsn(path) == fsn2norm(path)

    fsn = path2fsn(path)
    assert path2fsn(fsn) == fsn

    assert isinstance(fsn, fsnative)

    try:
        # never raises ValueError/TypError
        with open(fsn):
            pass
    except EnvironmentError:
        pass

    fsn2text(fsn).encode("utf-8")

    try:
        t = fsn2text(fsn, strict=True)
    except ValueError:
        pass
    else:
        assert fsn2norm(text2fsn(t)) == fsn2norm(fsn)

    data = fsn2bytes(fsn, "utf-8")
    assert fsn2bytes(bytes2fsn(data, "utf-8"), "utf-8") == data


@given(strategies.lists(strategies.text()), strategies.text(),
       strategies.text(), strategies.booleans())
def test_print(objects, sep, end, flush):
    h = StringIO()
    print_(*objects, sep=sep, end=end, flush=flush, file=h)
    h.getvalue()


@given(strategies.lists(strategies.binary()), strategies.binary(),
       strategies.binary(), strategies.booleans())
def test_print_bytes(objects, sep, end, flush):
    h = StringIO()
    print_(*objects, sep=sep, end=end, flush=flush, file=h)
    h.getvalue()


@given(strategies.text())
def test_fsnative(text):
    assert isinstance(fsnative(text), fsnative)


@given(strategies.text())
def test_text2fsn(text):
    assert isinstance(text2fsn(text), fsnative)


@given(strategies.text())
def test_text_fsn_roudntrip(text):
    if u"\x00" in text:
        return
    assert isinstance(fsn2text(text2fsn(text)), text_type)


@given(strategies.binary(),
       strategies.sampled_from(("utf-8", "utf-16-le",
                                "utf-32-le", "latin-1")))
def test_bytes(data, encoding):
    try:
        path = bytes2fsn(data, encoding)
    except ValueError:
        pass
    else:
        assert fsn2bytes(path, encoding) == data
