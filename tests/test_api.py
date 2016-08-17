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
import sys

import pytest

import senf
from senf import fsnative, sep, pathsep, curdir, pardir, \
    altsep, extsep, devnull, defpath, argv, getcwd, environ, getenv, \
    unsetenv, putenv, uri2fsn, fsn2uri, path2fsn, mkstemp, mkdtemp, \
    fsn2uri_ascii
from senf._compat import iteritems, PY3, PY2


def test_version():
    assert isinstance(senf.version, tuple)
    assert len(senf.version) == 3


def test_version_string():
    assert isinstance(senf.version_string, str)


def test_fsnative():
    assert isinstance(fsnative(u"foo"), fsnative)
    fsntype = type(fsnative(u""))
    assert issubclass(fsntype, fsnative)


def test_path2fsn():
    assert isinstance(path2fsn(senf.__path__[0]), fsnative)

    if os.name == "nt":
        assert path2fsn(u"\u1234") == u"\u1234"
        assert path2fsn("abc") == u"abc"
        assert isinstance(path2fsn("abc"), fsnative)
        assert path2fsn(b"abc") == u"abc"
    else:
        assert path2fsn(u"foo") == fsnative(u"foo")
        assert path2fsn(b"foo") == fsnative(u"foo")


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


def test_environ():
    for key, value in iteritems(environ):
        assert isinstance(key, fsnative)
        assert isinstance(value, fsnative)

    environ[fsnative(u"foo")] = fsnative(u"bar")
    assert getenv(fsnative(u"foo")) == "bar"
    assert isinstance(getenv("foo"), fsnative)

    assert environ["foo"] == "bar"
    assert isinstance(environ["foo"], fsnative)

    del environ["foo"]
    assert getenv("foo") is None


def test_getenv():
    environ["foo"] = "bar"

    assert getenv("foo") == "bar"
    del environ["foo"]
    assert getenv("foo", "quux") == "quux"
    assert getenv("foo") is None


def test_unsetenv():
    putenv("foo", "bar")
    # for some reason getenv goes to the cache, which makes it hard to test
    # things
    assert getenv("foo") is None
    unsetenv("foo")
    unsetenv("foo")
    assert getenv("foo") is None


def test_uri2fsn():
    if os.name != "nt":
        assert uri2fsn("file:///foo") == fsnative(u"/foo")
        assert uri2fsn(u"file:///foo") == fsnative(u"/foo")
        assert isinstance(uri2fsn("file:///foo"), fsnative)
        assert isinstance(uri2fsn(u"file:///foo"), fsnative)
        assert \
            uri2fsn("file:///foo-%E1%88%B4") == path2fsn(b"/foo-\xe1\x88\xb4")
    else:
        assert uri2fsn("file:///C:/foo") == fsnative(u"C:\\foo")
        assert uri2fsn(u"file:///C:/foo") == fsnative(u"C:\\foo")
        assert isinstance(uri2fsn("file:///C:/foo"), fsnative)
        assert isinstance(uri2fsn(u"file:///C:/foo"), fsnative)
        assert uri2fsn(u"file:///C:/foo-\u1234") == fsnative(u"C:\\foo-\u1234")
        assert \
            uri2fsn("file:///C:/foo-%E1%88%B4") == fsnative(u"C:\\foo-\u1234")
        assert uri2fsn(u"file://UNC/foo/bar") == u"\\\\UNC\\foo\\bar"
        assert uri2fsn(u"file://\u1234/\u4321") == u"\\\\\u1234\\\u4321"

    with pytest.raises(ValueError):
        uri2fsn("http://www.foo.bar")

    if os.name == "nt":
        with pytest.raises(ValueError):
            uri2fsn(u"\u1234")

    if PY3:
        with pytest.raises(TypeError):
            uri2fsn(b"file:///foo")


def test_fsn2uri():
    if os.name != "nt":
        assert fsn2uri(fsnative(u"/foo")) == "file:///foo"
        assert isinstance(fsn2uri(fsnative(u"/foo")), fsnative)
    else:
        assert fsn2uri(fsnative(u"C:\\foo")) == "file:///C:/foo"
        assert isinstance(fsn2uri(fsnative(u"C:\\foo")), fsnative)
        assert \
            fsn2uri(fsnative(u"\\\\UNC\\foo\\bar")) == u"file://UNC/foo/bar"
        assert fsn2uri(fsnative(u"C:\\foo\u1234")) == u"file:///C:/foo\u1234"

        # winapi can't handle too large paths. make sure we raise properly
        with pytest.raises(ValueError):
            fsn2uri(u"C:\\" + 4000 * u"a")


def test_fsn2uri_ascii():
    if os.name == "nt":
        assert (fsn2uri_ascii(u"C:\\foo-\u1234") ==
                "file:///C:/foo-%E1%88%B4")
        assert isinstance(fsn2uri_ascii(u"C:\\foo-\u1234"), str)
        assert fsn2uri_ascii(u"\\\serv\\share\\") == "file://serv/share/"
        assert fsn2uri_ascii(u"\\\serv\\\u1234\\") == "file://serv/%E1%88%B4/"
    else:
        if PY2:
            path = "/foo-\xe1\x88\xb4"
        else:
            path = u"/foo-\u1234"
        assert fsn2uri_ascii(path) == "file:///foo-%E1%88%B4"
        assert isinstance(fsn2uri_ascii(path), str)


def test_uri_roundtrip():
    if os.name == "nt":
        for path in [u"C:\\foo-\u1234", u"C:\\bla\\quux ha",
                     u"\\\\\u1234\\foo\\\u1423"]:
            path = fsnative(path)
            assert uri2fsn(fsn2uri(path)) == path
            assert isinstance(uri2fsn(fsn2uri(path)), fsnative)
            assert uri2fsn(fsn2uri_ascii(path)) == path
            assert isinstance(uri2fsn(fsn2uri_ascii(path)), fsnative)
    else:
        path = path2fsn(b"/foo-\xe1\x88\xb4")

        assert uri2fsn(fsn2uri(fsnative(u"/foo"))) == "/foo"
        assert uri2fsn(fsn2uri(path)) == path
        assert isinstance(uri2fsn(fsn2uri(path)), fsnative)

        assert uri2fsn(fsn2uri_ascii(fsnative(u"/foo"))) == "/foo"
        assert uri2fsn(fsn2uri_ascii(path)) == path
        assert isinstance(uri2fsn(fsn2uri_ascii(path)), fsnative)


def test_mkdtemp():
    fsn = mkdtemp()
    assert isinstance(fsn, fsnative)
    os.rmdir(fsn)

    fsn = mkdtemp(suffix="foo")
    fsn.endswith("foo")
    assert isinstance(fsn, fsnative)
    os.rmdir(fsn)


def test_test_mkstemp():
    fd, fsn = mkstemp()
    os.close(fd)
    assert isinstance(fsn, fsnative)
    os.remove(fsn)

    fd, fsn = mkstemp(suffix="foo")
    os.close(fd)
    fsn.endswith("foo")
    assert isinstance(fsn, fsnative)
    os.remove(fsn)
