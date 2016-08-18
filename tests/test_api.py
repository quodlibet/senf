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
import contextlib

import pytest

import senf
from senf import fsnative, sep, pathsep, curdir, pardir, \
    altsep, extsep, devnull, defpath, argv, getcwd, environ, getenv, \
    unsetenv, putenv, uri2fsn, fsn2uri, path2fsn, mkstemp, mkdtemp, \
    fsn2uri_ascii, fsn2text, fsn2bytes, bytes2fsn, print_, input_
from senf._compat import iteritems, PY3, PY2, BytesIO, StringIO
from senf._environ import set_windows_env_var, get_windows_env_var, \
    del_windows_env_var


linesepb = os.linesep
if PY3:
    linesepb = linesepb.encode("ascii")


@contextlib.contextmanager
def capture_output(data=None):
    """
    with capture_output as (stdout, stderr):
        some_action()
    print stdout.getvalue(), stderr.getvalue()
    """

    in_ = BytesIO(data or b"")
    err = BytesIO()
    out = BytesIO()
    old_in = sys.stdin
    old_err = sys.stderr
    old_out = sys.stdout
    sys.stdin = in_
    sys.stderr = err
    sys.stdout = out

    try:
        yield (out, err)
    finally:
        sys.stdin = old_in
        sys.stderr = old_err
        sys.stdout = old_out


@pytest.mark.skipif(os.name != "nt" or PY3, reason="win+py2 only")
def test_set_windows_env_var():
    with pytest.raises(TypeError):
        set_windows_env_var("", u"")

    with pytest.raises(TypeError):
        set_windows_env_var(u"", "")

    with pytest.raises(WindowsError):
        set_windows_env_var(u"==", u"")

    set_windows_env_var(u"foo", u"bar")
    assert get_windows_env_var(u"foo") == u"bar"
    del_windows_env_var(u"foo")
    with pytest.raises(WindowsError):
        get_windows_env_var(u"foo")


@pytest.mark.skipif(os.name != "nt" or PY3, reason="win+py2 only")
def test_get_windows_env_var():
    with pytest.raises(TypeError):
        get_windows_env_var("")


@pytest.mark.skipif(os.name != "nt" or PY3, reason="win+py2 only")
def test_del_windows_env_var():
    with pytest.raises(TypeError):
        del_windows_env_var("")

    with pytest.raises(WindowsError):
        del_windows_env_var(u"nopenopenopenope")


def test_print():
    f = BytesIO()
    print_(u"foo", file=f)
    out = f.getvalue()
    assert isinstance(out, bytes)
    assert out == b"foo" + linesepb

    f = StringIO()
    print_(u"foo", file=f)
    out = f.getvalue()
    assert isinstance(out, str)
    assert out == "foo" + os.linesep


def test_print_capture():
    with capture_output() as (out, err):
        print_(u"bla")
        assert out.getvalue() == b"bla" + linesepb
        assert err.getvalue() == b""

    with capture_output() as (out, err):
        print_(u"bla", end="\n")
        assert out.getvalue() == b"bla" + linesepb

    with capture_output() as (out, err):
        print_()
        assert out.getvalue() == linesepb


def test_print_py3_stringio():
    if os.name != "nt" and PY3:
        f = StringIO()
        print_(b"\xff\xfe", file=f)
        assert f.getvalue() == os.fsdecode(b"\xff\xfe\n")


def test_input():
    with capture_output(b"foo" + linesepb + b"bla"):
        out = input_()
        assert out == "foo"
        assert isinstance(out, fsnative)
        out = input_()
        assert out == "bla"
        assert isinstance(out, fsnative)


def test_input_prompt():
    with capture_output(b"foo") as (out, err):
        in_ = input_(u"bla")
        assert in_ == "foo"
        assert isinstance(in_, fsnative)
        assert out.getvalue() == b"bla"
        assert err.getvalue() == b""


def test_version():
    assert isinstance(senf.version, tuple)
    assert len(senf.version) == 3


def test_version_string():
    assert isinstance(senf.version_string, str)


def test_fsnative():
    assert isinstance(fsnative(u"foo"), fsnative)
    fsntype = type(fsnative(u""))
    assert issubclass(fsntype, fsnative)
    with pytest.raises(TypeError):
        fsnative(b"")


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

    with pytest.raises(TypeError):
        path2fsn(object())


def test_fsn2text():
    assert fsn2text(fsnative(u"foo")) == u"foo"
    with pytest.raises(TypeError):
        fsn2text(object())


def test_fsn2bytes():
    assert fsn2bytes(fsnative(u"foo"), "utf-8") == b"foo"
    with pytest.raises(TypeError):
        fsn2bytes(object(), "utf-8")
    if os.name != "nt":
        assert fsn2bytes(fsnative(u"foo"), None) == b"foo"
    else:
        with pytest.raises(ValueError):
            fsn2bytes(fsnative(u"foo"), "notanencoding")
        with pytest.raises(ValueError):
            fsn2bytes(fsnative(u"foo"), None)
        with pytest.raises(TypeError):
            fsn2bytes(fsnative(u"foo"), object())


def test_bytes2fsn():
    assert bytes2fsn(b"foo", "utf-8") == fsnative(u"foo")
    assert (bytes2fsn(fsn2bytes(fsnative(u"\u1234"), "utf-8"), "utf-8") ==
            fsnative(u"\u1234"))

    with pytest.raises(TypeError):
        bytes2fsn(object(), "utf-8")

    with pytest.raises(TypeError):
        bytes2fsn(u"data", "utf-8")

    if os.name == "nt":
        with pytest.raises(ValueError):
            bytes2fsn(b"data", "notanencoding")
        with pytest.raises(ValueError):
            bytes2fsn(b"data", None)
        with pytest.raises(TypeError):
            bytes2fsn(b"data", object())


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
    with pytest.raises(KeyError):
        del environ["foo"]

    if os.name == "nt":
        with pytest.raises(ValueError):
            environ["=="] = "bla"
    else:
        environ["=="] = "bla"
        assert environ["=="] == "bla"

    assert len(environ) == len(environ.keys())
    repr(environ)


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


def test_putenv():
    if os.name == "nt":
        with pytest.raises(ValueError):
            putenv("==", "bla")
    else:
        putenv("==", "bla")


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

    with pytest.raises(TypeError):
        uri2fsn(object())

    with pytest.raises(ValueError):
        uri2fsn("http://www.foo.bar")

    if os.name == "nt":
        with pytest.raises(ValueError):
            uri2fsn(u"\u1234")

    if PY3:
        with pytest.raises(TypeError):
            uri2fsn(b"file:///foo")


def test_fsn2uri():

    with pytest.raises(TypeError):
        fsn2uri(object())

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
    with pytest.raises(TypeError):
        fsn2uri(object())

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
            path = fsnative(u"/foo-\u1234")
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
