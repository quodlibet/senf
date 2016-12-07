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

from hypothesis import given, strategies

from senf import fsnative, text2fsn, fsn2text, bytes2fsn, fsn2bytes, print_
from senf._compat import text_type, StringIO


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
