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

import senf
from senf import fsnative, py2fsn, sep, pathsep, curdir, pardir, \
    altsep, extsep, devnull, defpath, argv, getcwd


def test_version():
    assert isinstance(senf.version, tuple)
    assert len(senf.version) == 3


def test_version_string():
    assert isinstance(senf.version_string, str)


def test_fsnative():
    assert isinstance(fsnative(u"foo"), fsnative)
    fsntype = type(fsnative(u""))
    assert issubclass(fsntype, fsnative)


def test_py2fsn():
    assert isinstance(py2fsn(senf.__path__[0]), fsnative)


def test_constants():
    assert isinstance(sep, fsnative)
    assert isinstance(pathsep, fsnative)
    assert isinstance(curdir, fsnative)
    assert isinstance(pardir, fsnative)
    assert altsep is None or isinstance(altsep, fsnative)
    assert isinstance(extsep, fsnative)
    assert isinstance(devnull, fsnative)
    assert isinstance(defpath, fsnative)


def test_argv():
    assert isinstance(argv, list)
    assert len(sys.argv) == len(argv)
    assert all(isinstance(v, fsnative) for v in argv)


def test_getcwd():
    assert isinstance(getcwd(), fsnative)
