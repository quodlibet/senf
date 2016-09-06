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
import ctypes
import shutil

import pytest

import senf
from senf import fsnative, sep, pathsep, curdir, pardir, \
    altsep, extsep, devnull, defpath, argv, getcwd, environ, getenv, \
    unsetenv, putenv, uri2fsn, fsn2uri, path2fsn, mkstemp, mkdtemp, \
    fsn2text, fsn2bytes, bytes2fsn, print_, input_, \
    expanduser, text2fsn, expandvars
from senf._compat import iteritems, PY3, PY2, BytesIO, StringIO, text_type
from senf._environ import set_windows_env_var, get_windows_env_var, \
    del_windows_env_var
from senf._winansi import ansi_parse, ansi_split
from senf._stdlib import _get_userdir
from senf._fsnative import _encoding, is_unix, _surrogatepass
from senf._print import _encode_codepage, _decode_codepage
from senf import _winapi as winapi


is_wine = "WINEDEBUG" in os.environ

linesepb = os.linesep
if PY3:
    linesepb = linesepb.encode("ascii")


def notfsnative(text=u""):
    fsn = fsnative(text)
    if isinstance(fsn, bytes):
        return fsn2text(fsn)
    else:
        return fsn2bytes(fsn, "utf-8")

assert not isinstance(notfsnative(), fsnative)


def iternotfsn():
    yield notfsnative(u"foo")

    if PY3 and is_unix:
        try:
            u"\u1234".encode(_encoding)
        except UnicodeEncodeError:
            # in case we have a ascii encoding this is an invalid path
            yield u"\u1234"


class PathLike(object):

    def __init__(self, path):
        self._path = path

    def __fspath__(self):
        return self._path


@contextlib.contextmanager
def preserve_environ():
    old = environ.copy()
    yield
    # don't touch existing values as os.environ is broken for empty
    # keys on Windows: http://bugs.python.org/issue20658
    for key, value in list(environ.items()):
        if key not in old:
            del environ[key]
    for key, value in list(old.items()):
        if key not in environ or environ[key] != value:
            environ[key] = value


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


def test_getuserdir():
    userdir = _get_userdir()
    assert isinstance(userdir, fsnative)

    with pytest.raises(TypeError):
        _get_userdir(notfsnative(u"foo"))

    if os.name == "nt":
        otherdir = _get_userdir(u"foo")
        assert otherdir == os.path.join(os.path.dirname(userdir), u"foo")
    else:
        user = os.path.basename(userdir)
        assert _get_userdir() == _get_userdir(user)

    with preserve_environ():
        environ["HOME"] = "bla"
        assert _get_userdir() == "bla"

    with preserve_environ():
        environ.pop("HOME", None)
        if os.name != "nt":
            assert _get_userdir()
        else:
            environ["USERPROFILE"] = "uprof"
            assert _get_userdir() == "uprof"

    with preserve_environ():
        environ.pop("HOME", None)
        environ.pop("USERPROFILE", None)
        if os.name == "nt":
            environ["HOMEPATH"] = "hpath"
            environ["HOMEDRIVE"] = "C:\\"
            assert _get_userdir() == "C:\\hpath"
            assert _get_userdir(u"bla") == "C:\\bla"

    with preserve_environ():
        environ.pop("HOME", None)
        environ.pop("USERPROFILE", None)
        environ.pop("HOMEPATH", None)
        if os.name == "nt":
            assert _get_userdir() is None


def test_expanduser_simple():
    home = _get_userdir()
    assert expanduser("~") == home
    assert isinstance(expanduser("~"), fsnative)
    assert expanduser(os.path.join("~", "a", "b")) == \
        os.path.join(home, "a", "b")
    assert expanduser(senf.sep + "~") == senf.sep + "~"
    if senf.altsep is not None:
        assert expanduser("~" + senf.altsep) == home + senf.altsep


def test_expanduser_user():
    home = _get_userdir()
    user = os.path.basename(home)

    assert expanduser("~" + user) == home
    assert expanduser(os.path.join("~" + user, "foo")) == \
        os.path.join(home, "foo")

    if senf.altsep is not None:
        assert expanduser("~" + senf.altsep + "foo") == \
            home + senf.altsep + "foo"

        assert expanduser("~" + user + senf.altsep + "a" + senf.sep) == \
            home + senf.altsep + "a" + senf.sep

    if os.name == "nt":
        assert expanduser(os.path.join("~nope", "foo")) == \
            os.path.join(os.path.dirname(home), "nope", "foo")


def test_ansi_matching():
    to_match = [u"\033[39m", u"\033[3m", u"\033[m", u"\033[;m", u"\033[;2;m"]
    for t in to_match:
        assert list(ansi_split(t)) == [(True, t)]

    assert list(ansi_split("foo\033[;2;mbla")) == [
        (False, "foo"), (True, "\033[;2;m"), (False, "bla")]

    assert ansi_parse(u"\033[;2;m") == ("m", (0, 2, 0))
    assert ansi_parse(u"\033[;m") == ("m", (0, 0))
    assert ansi_parse(u"\033[k") == ("k", (0,))
    assert ansi_parse(u"\033[;;k") == ("k", (0, 0, 0))
    assert ansi_parse(u"\033[100k") == ("k", (100,))
    assert ansi_parse(u"\033[m") == ("m", (0,))


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

    if is_wine:
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

    print_(u"foo", file=f, flush=True)


def test_print_ansi():
    for i in range(1, 110):
        print_("\033[%dm" % i, end="")
    other = ["\033[A", "\033[B", "\033[C", "\033[D", "\033[s", "\033[u",
             "\033[H", "\033[f"]
    for c in other:
        print_(c, end="")


def test_print_anything():
    with capture_output():
        print_(u"\u1234")

    with capture_output() as (out, err):
        print_(5, end="")
        assert out.getvalue() == b"5"

    with capture_output() as (out, err):
        print_([], end="")
        assert out.getvalue() == b"[]"


def test_print_error():
    with pytest.raises(TypeError):
        print_(end=4)

    with pytest.raises(TypeError):
        print_(sep=4)


@pytest.mark.skipif(os.name != "nt", reason="windows only")
def test_win_cp_encodings():
    assert _encode_codepage(437, u"foo") == b"foo"
    assert _encode_codepage(437, u"\xe4") == b"\x84"
    assert _encode_codepage(437, u"") == b""
    assert _decode_codepage(437, b"foo") == u"foo"
    assert _decode_codepage(437, b"\x84") == u"\xe4"
    assert _decode_codepage(437, b"") == u""


@pytest.mark.skipif(os.name == "nt" or PY2, reason="unix+py3 only")
def test_print_strict_strio():
    f = StringIO()

    real_write = f.write

    def strict_write(data):
        if not isinstance(data, text_type):
            raise TypeError
        real_write(data.encode("utf-8").decode("utf-8"))

    f.write = strict_write

    print_(b"\xff\xfe".decode(_encoding, "surrogateescape"), file=f)
    assert f.getvalue() == u"\ufffd\ufffd\n"


def test_print_real():
    print_(u"foo")
    print_(u"foo", file=sys.stderr)
    print_(u"\033[94mfoo", u"\033[0m")
    print_(b"foo")
    print_(u"foo", flush=True)


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
        assert f.getvalue() == \
            b"\xff\xfe\n".decode(_encoding, "surrogateescape")


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

        try:
            path = u"\xf6".encode(_encoding)
        except UnicodeEncodeError:
            pass
        else:
            assert path2fsn(path) == u"\xf6"

    else:
        assert path2fsn(u"foo") == fsnative(u"foo")
        assert path2fsn(b"foo") == fsnative(u"foo")

        if PY3:
            # non unicode encoding, e.g. ascii
            if fsnative(u"\u1234") != u"\u1234":
                with pytest.raises(ValueError):
                    path2fsn(u"\u1234")
                assert fsnative(u"\u1234") == path2fsn(fsnative(u"\u1234"))

    with pytest.raises(TypeError):
        path2fsn(object())


@pytest.mark.skipif(not hasattr(os, "fspath"), reason="python3.6 only")
def test_path2fsn_pathlike():
    # basic tests for os.fspath
    with pytest.raises(TypeError):
        os.fspath(PathLike(None))
    assert os.fspath(PathLike(fsnative(u"foo"))) == fsnative(u"foo")
    assert os.fspath(PathLike(u"\u1234")) == u"\u1234"

    # now support in path2fsn
    pathlike = PathLike(fsnative(u"foo"))
    assert path2fsn(pathlike) == fsnative(u"foo")

    # pathlib should also work..
    from pathlib import Path
    assert path2fsn(Path(".")) == fsnative(u".")


def test_fsn2text():
    assert fsn2text(fsnative(u"foo")) == u"foo"
    with pytest.raises(TypeError):
        fsn2text(object())
    with pytest.raises(TypeError):
        fsn2text(notfsnative(u"foo"))

    for path in iternotfsn():
        with pytest.raises(TypeError):
            fsn2text(path)


def test_text2fsn():
    with pytest.raises(TypeError):
        text2fsn(b"foo")
    assert text2fsn(u"foo") == fsnative(u"foo")


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

    for path in iternotfsn():
        with pytest.raises(TypeError):
            fsn2bytes(path)


def test_surrogates():
    if os.name == "nt":
        assert fsn2bytes(u"\ud83d", "utf-16-le") == b"=\xd8"
        if sys.version_info[:2] >= (3, 4):
            # decoding lone surrogates is broken on PY < 3.4 with utf-16
            # https://bugs.python.org/issue27971
            assert bytes2fsn(b"=\xd8", "utf-16-le") == u"\ud83d"

        assert fsn2bytes(u"\ud83d", "utf-8") == b"\xed\xa0\xbd"
        assert bytes2fsn(b"\xed\xa0\xbd", "utf-8") == u"\ud83d"

        assert fsnative(u"\ud83d") == u"\ud83d"
        assert fsn2text(u"\ud83d") == u"\ufffd"

        # at least don't fail...
        assert fsn2uri(u"C:\\\ud83d") == u"file:///C:/%ED%A0%BD"
    else:
        # this shouldn't fail and produce the same result on py2/3 at least.
        assert fsn2bytes(fsnative(u"\ud83d"), None) == b"\xed\xa0\xbd"


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

    if os.name == "nt":
        assert fsn2uri(fsnative(u"C:\\foo")) == "file:///C:/foo"
        assert fsn2uri(u"C:\\ö ä%") == "file:///C:/%C3%B6%20%C3%A4%25"
        assert (fsn2uri(u"C:\\foo-\u1234") ==
                "file:///C:/foo-%E1%88%B4")
        assert isinstance(fsn2uri(u"C:\\foo-\u1234"), str)
        assert fsn2uri(u"\\\serv\\share\\") == "file://serv/share/"
        assert fsn2uri(u"\\\serv\\\u1234\\") == "file://serv/%E1%88%B4/"
        assert \
            fsn2uri(fsnative(u"\\\\UNC\\foo\\bar")) == u"file://UNC/foo/bar"

        # winapi can't handle too large paths. make sure we raise properly
        with pytest.raises(ValueError):
            fsn2uri(u"C:\\" + 4000 * u"a")
    else:
        if PY2:
            path = "/foo-\xe1\x88\xb4"
        else:
            path = fsnative(u"/foo-\u1234")
        assert fsn2uri(path) == "file:///foo-%E1%88%B4"
        assert isinstance(fsn2uri(path), str)


def test_uri_roundtrip():
    if os.name == "nt":
        for path in [u"C:\\foo-\u1234", u"C:\\bla\\quux ha",
                     u"\\\\\u1234\\foo\\\u1423", u"\\\\foo;\\f"]:
            path = fsnative(path)
            assert uri2fsn(fsn2uri(path)) == path
            assert isinstance(uri2fsn(fsn2uri(path)), fsnative)
    else:
        path = path2fsn(b"/foo-\xe1\x88\xb4")

        assert uri2fsn(fsn2uri(fsnative(u"/foo"))) == "/foo"
        assert uri2fsn(fsn2uri(path)) == path
        assert isinstance(uri2fsn(fsn2uri(path)), fsnative)


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


def test_expandvars():
    with preserve_environ():
        environ["foo"] = "bar"
        environ["nope b"] = "xxx"
        environ["f/oo"] = "bar"
        environ.pop("nope", "")

        assert expandvars("$foo") == "bar"
        assert expandvars("$nope b") == "$nope b"
        assert expandvars("/$foo/") == "/bar/"
        assert expandvars("$f/oo") == "$f/oo"
        assert expandvars("$nope") == "$nope"
        assert expandvars("$foo_") == "$foo_"

        assert expandvars("${f/oo}") == "bar"
        assert expandvars("${nope b}") == "xxx"
        assert expandvars("${nope}") == "${nope}"
        assert isinstance(expandvars("$foo"), fsnative)

    with preserve_environ():
        if os.name == "nt":
            environ[u"ö"] = u"ä"
            environ.pop(u"ä", "")
            assert isinstance(expandvars("$ö"), fsnative)
            assert expandvars(u"$ö") == u"ä"
            assert expandvars(u"${ö}") == u"ä"
            assert expandvars(u"${ä}") == u"${ä}"
            assert expandvars(u"$ä") == u"$ä"

            assert expandvars(u"%ö") == u"%ö"
            assert expandvars(u"ö%") == u"ö%"
            assert expandvars(u"%ö%") == u"ä"
            assert expandvars(u"%ä%") == u"%ä%"


def test_python_handling_broken_utf16():
    # Create a file with an invalid utf-16 name.
    # Mainly to see how Python handles it

    tmp = mkdtemp()
    try:
        path = os.path.join(tmp, "foo")
        with open(path, "wb") as h:
            h.write(b"content")
        assert "foo" in os.listdir(tmp)

        if os.name == "nt":
            faulty = (path.encode("utf-16-le") + b"=\xd8\x01\xde" +
                      b"=\xd8-\x00\x01\xde")
            buf = ctypes.create_string_buffer(faulty + b"\x00\x00")

            if winapi.MoveFileW(path, ctypes.cast(buf, ctypes.c_wchar_p)) == 0:
                raise ctypes.WinError()
            assert "foo" not in os.listdir(tmp)

            newpath = os.path.join(tmp, os.listdir(tmp)[0])
            if not is_wine:  # this is broken on wine..
                assert newpath.encode("utf-16-le", _surrogatepass) == faulty

            with open(newpath, "rb") as h:
                assert h.read() == b"content"
    finally:
        shutil.rmtree(tmp)
