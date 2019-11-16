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
import sys
import contextlib
import ctypes
import shutil
import codecs
from typing import TYPE_CHECKING

import pytest

import senf
from senf import fsnative, sep, pathsep, curdir, pardir, \
    altsep, extsep, devnull, defpath, argv, getcwd, environ, getenv, \
    unsetenv, putenv, uri2fsn, fsn2uri, path2fsn, mkstemp, mkdtemp, \
    fsn2text, fsn2bytes, bytes2fsn, print_, input_, \
    expanduser, text2fsn, expandvars, supports_ansi_escape_codes, fsn2norm
from senf._compat import iteritems, PY3, PY2, BytesIO, StringIO, text_type, \
    TextIO
from senf._environ import set_windows_env_var, get_windows_env_var, \
    del_windows_env_var
from senf._winansi import ansi_parse, ansi_split
from senf._stdlib import _get_userdir
from senf._fsnative import _encoding, is_unix, _surrogatepass, _get_encoding
from senf._print import _encode_codepage, _decode_codepage
from senf import _winapi as winapi


is_wine = "WINEDEBUG" in os.environ

if PY3:
    linesepb = os.linesep.encode("ascii")
    linesepu = os.linesep
else:
    linesepb = os.linesep
    linesepu = os.linesep.decode("ascii")


def notfsnative(text=u""):
    fsn = fsnative(text)
    if isinstance(fsn, bytes):
        return fsn2text(fsn)
    else:
        return fsn2bytes(fsn, "utf-8")


assert not isinstance(notfsnative(), fsnative)


def isunicodeencoding():
    try:
        u"\u1234".encode(_encoding)
    except UnicodeEncodeError:
        return False
    return True


def iternotfsn():
    yield notfsnative(u"foo")

    if PY3 and is_unix and not isunicodeencoding():
        # in case we have a ascii encoding this is an invalid path
        yield u"\u1234"

    if PY2 and is_unix:
        yield b"\x00"
    else:
        yield u"\x00"


if TYPE_CHECKING:
    _base = os.PathLike
else:
    _base = object


class PathLike(_base):

    def __init__(self, path):
        self._path = path

    def __fspath__(self):
        return self._path


@contextlib.contextmanager
def preserve_environ(environ=environ):
    old = environ.copy()
    if environ is not os.environ:
        with preserve_environ(os.environ):
            yield
    else:
        yield
    # don't touch existing values as os.environ is broken for empty
    # keys on Windows: http://bugs.python.org/issue20658
    for key, value in list(environ.items()):
        if key not in old:
            del environ[key]
    for key, value in list(old.items()):
        if key not in environ or environ[key] != value:
            environ[key] = value


environ_case_sensitive = True
with preserve_environ():
    os.environ.pop("senf", None)
    os.environ["SENF"] = "foo"
    environ_case_sensitive = not ("senf" in os.environ)


@contextlib.contextmanager
def preserve_argv(argv=argv):
    old = argv[:]
    if argv is not sys.argv:
        with preserve_argv(sys.argv):
            yield
    else:
        yield
    argv[:] = old


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


def test__get_encoding():
    # type: () -> None

    orig = sys.getfilesystemencoding
    sys.getfilesystemencoding = lambda: None  # type: ignore
    try:
        codecs.lookup(_get_encoding())
    finally:
        sys.getfilesystemencoding = orig


def test_getuserdir():
    # type: () -> None

    userdir = _get_userdir()
    assert isinstance(userdir, fsnative)

    with pytest.raises(TypeError):
        _get_userdir(notfsnative(u"foo"))

    if sys.platform == "win32":
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
        if sys.platform != "win32":
            assert _get_userdir()
        else:
            environ["USERPROFILE"] = "uprof"
            assert _get_userdir() == "uprof"

    with preserve_environ():
        environ.pop("HOME", None)
        environ.pop("USERPROFILE", None)
        if sys.platform == "win32":
            environ["HOMEPATH"] = "hpath"
            environ["HOMEDRIVE"] = "C:\\"
            assert _get_userdir() == "C:\\hpath"
            assert _get_userdir(u"bla") == "C:\\bla"

    with preserve_environ():
        environ.pop("HOME", None)
        environ.pop("USERPROFILE", None)
        environ.pop("HOMEPATH", None)
        if sys.platform == "win32":
            assert _get_userdir() is None


def test_expanduser_simple():
    # type: () -> None

    home = _get_userdir()
    assert expanduser("~") == home
    assert isinstance(expanduser("~"), fsnative)
    assert expanduser(os.path.join("~", "a", "b")) == \
        os.path.join(home, "a", "b")
    assert expanduser(senf.sep + "~") == senf.sep + "~"
    if senf.altsep is not None:
        assert expanduser("~" + senf.altsep) == home + senf.altsep


def test_expanduser_user():
    # type: () -> None

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

    if sys.platform == "win32":
        assert expanduser(os.path.join("~nope", "foo")) == \
            os.path.join(os.path.dirname(home), "nope", "foo")


def test_ansi_matching():
    # type: () -> None

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
    # type: () -> None

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
    # type: () -> None

    with pytest.raises(TypeError):
        get_windows_env_var("")


@pytest.mark.skipif(os.name != "nt" or PY3, reason="win+py2 only")
def test_del_windows_env_var():
    # type: () -> None

    with pytest.raises(TypeError):
        del_windows_env_var("")

    if is_wine:
        with pytest.raises(WindowsError):
            del_windows_env_var(u"nopenopenopenope")


def test_print():
    # type: () -> None

    f = BytesIO()
    print_(u"foo", file=f)  # type: ignore
    out = f.getvalue()
    assert isinstance(out, bytes)
    assert out == b"foo" + linesepb

    f2 = StringIO()
    print_(u"foo", file=f2)
    out2 = f2.getvalue()
    assert isinstance(out2, str)
    assert out2 == "foo" + os.linesep

    print_(u"foo", file=f, flush=True)  # type: ignore

    f3 = TextIO()
    print_(u"foo", file=f3)
    out3 = f3.getvalue()
    assert isinstance(out3, text_type)
    assert out3 == u"foo" + linesepu

    f4 = TextIO()
    print_(u"", file=f4, end=b"\n")  # type: ignore
    out4 = f4.getvalue()
    assert isinstance(out4, text_type)
    assert out4 == linesepu

    f5 = BytesIO()
    print_("", file=f5, end=b"\n")  # type: ignore
    out5 = f5.getvalue()
    assert isinstance(out5, bytes)
    assert out5 == linesepb


@pytest.mark.skipif(os.name != "nt", reason="win only")
def test_print_windows():
    # type: () -> None

    f = BytesIO()
    print_(u"öäü\ud83d", file=f)  # type: ignore
    out = f.getvalue()
    assert isinstance(out, bytes)
    assert out == b"\xc3\xb6\xc3\xa4\xc3\xbc\xed\xa0\xbd" + linesepb

    f2 = TextIO()
    print_(u"öäü\ud83d", file=f2)
    out2 = f2.getvalue()
    assert isinstance(out2, text_type)
    assert out2 == u"öäü\ud83d" + linesepu


def test_print_defaults_none():
    # type: () -> None

    # python 3 print takes None as default, try to do the same
    with capture_output() as (out, err):
        print_("foo", "bar")
    first = out.getvalue()
    with capture_output() as (out, err):
        print_("foo", "bar", end=None, sep=None, file=None)  # type: ignore
    assert out.getvalue() == first


def test_print_ansi():
    # type: () -> None

    for i in range(1, 110):
        print_("\033[%dm" % i, end="")
    other = ["\033[A", "\033[B", "\033[C", "\033[D", "\033[s", "\033[u",
             "\033[H", "\033[f"]
    for c in other:
        print_(c, end="")


def test_print_anything():
    # type: () -> None

    with capture_output():
        print_(u"\u1234")

    with capture_output() as (out, err):
        print_(5, end="")
        assert out.getvalue() == b"5"

    with capture_output() as (out, err):
        print_([], end="")
        assert out.getvalue() == b"[]"


def test_print_error():
    # type: () -> None

    with pytest.raises(TypeError):
        print_(end=4)  # type: ignore

    with pytest.raises(TypeError):
        print_(sep=4)  # type: ignore


@pytest.mark.skipif(os.name != "nt", reason="windows only")
def test_win_cp_encodings():
    # type: () -> None

    assert _encode_codepage(437, u"foo") == b"foo"
    assert _encode_codepage(437, u"\xe4") == b"\x84"
    assert _encode_codepage(437, u"") == b""
    assert _encode_codepage(437, u"\ud83d") == b"?"
    assert _decode_codepage(437, b"foo") == u"foo"
    assert _decode_codepage(437, b"\x84") == u"\xe4"
    assert _decode_codepage(437, b"") == u""


@pytest.mark.skipif(os.name == "nt" or PY2, reason="unix+py3 only")
def test_print_strict_strio():
    # type: () -> None

    f = StringIO()

    real_write = f.write

    def strict_write(data):
        if not isinstance(data, text_type):
            raise TypeError
        real_write(data.encode("utf-8").decode("utf-8"))

    f.write = strict_write  # type: ignore

    print_(b"\xff\xfe".decode(_encoding, "surrogateescape"), file=f)
    assert f.getvalue() == u"\ufffd\ufffd\n"


def test_print_real():
    # type: () -> None

    print_(u"foo")
    print_(u"foo", file=sys.stderr)
    print_(u"\033[94mfoo", u"\033[0m")
    print_(b"foo")
    print_(u"foo", flush=True)
    print_(u"\ud83d")


def test_print_capture():
    # type: () -> None

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
    # type: () -> None

    if os.name != "nt" and PY3:
        f = StringIO()
        print_(b"\xff\xfe", file=f)
        assert f.getvalue() == \
            b"\xff\xfe\n".decode(_encoding, "surrogateescape")


def test_input():
    # type: () -> None

    with capture_output(b"foo" + linesepb + b"bla"):
        out = input_()
        assert out == "foo"
        assert isinstance(out, fsnative)
        out = input_()
        assert out == "bla"
        assert isinstance(out, fsnative)


def test_input_prompt():
    # type: () -> None

    with capture_output(b"foo") as (out, err):
        in_ = input_(u"bla")
        assert in_ == "foo"
        assert isinstance(in_, fsnative)
        assert out.getvalue() == b"bla"
        assert err.getvalue() == b""


def test_version():
    # type: () -> None

    assert isinstance(senf.version, tuple)
    assert len(senf.version) == 3


def test_version_string():
    # type: () -> None

    assert isinstance(senf.version_string, str)


def test_fsnative():
    # type: () -> None

    assert isinstance(fsnative(u"foo"), fsnative)
    fsntype = type(fsnative(u""))
    assert issubclass(fsntype, fsnative)
    with pytest.raises(TypeError):
        fsnative(b"")  # type: ignore

    assert fsnative(u"\x00") == fsnative(u"\uFFFD")

    assert isinstance(fsnative(u"\x00"), fsnative)
    for inst in iternotfsn():
        assert not isinstance(inst, fsnative)

    if isinstance(fsnative(u"\uD800"), text_type) and \
            fsnative(u"\uD800") != u"\uD800":
        assert not isinstance(u"\uD800", fsnative)

    fsn = fsnative(u'\udcc2\udc80')
    assert fsn == fsn2norm(fsn)

    fsn = fsnative(u"\uD800\uDC01")
    assert fsn == fsn2norm(fsn)


def test_path2fsn():
    # type: () -> None

    assert isinstance(path2fsn(senf.__path__[0]), fsnative)  # type: ignore

    with pytest.raises(ValueError):
        path2fsn(b"\x00")
    with pytest.raises(ValueError):
        path2fsn(u"\x00")

    if sys.platform == "win32":
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
        path2fsn(object())  # type: ignore


@pytest.mark.skipif(not hasattr(os, "fspath"), reason="python3.6 only")
def test_path2fsn_pathlike():
    # type: () -> None

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
    # type: () -> None

    assert fsn2text(fsnative(u"foo")) == u"foo"
    with pytest.raises(TypeError):
        fsn2text(object())  # type: ignore
    with pytest.raises(TypeError):
        fsn2text(notfsnative(u"foo"))

    for path in iternotfsn():
        with pytest.raises(TypeError):
            fsn2text(path)

    if sys.platform == "win32":
        assert fsn2text(u"\uD800\uDC01") == u"\U00010001"


def test_fsn2text_strict():
    # type: () -> None

    if sys.platform != "win32":
        path = bytes2fsn(b"\xff", None)
    else:
        path = u"\ud83d"

    if text2fsn(fsn2text(path)) != path:
        with pytest.raises(ValueError):
            fsn2text(path, strict=True)


def test_text2fsn():
    # type: () -> None

    with pytest.raises(TypeError):
        text2fsn(b"foo")  # type: ignore
    assert text2fsn(u"foo") == fsnative(u"foo")


def test_fsn2bytes():
    # type: () -> None

    assert fsn2bytes(fsnative(u"foo"), "utf-8") == b"foo"
    with pytest.raises(TypeError):
        fsn2bytes(object(), "utf-8")  # type: ignore

    if PY3:
        with pytest.raises(TypeError):
            fsn2bytes(u"\x00", "utf-8")  # type: ignore
    else:
        with pytest.raises(TypeError):
            fsn2bytes(b"\x00", "utf-8")  # type: ignore

    if sys.platform != "win32":
        assert fsn2bytes(fsnative(u"foo"), None) == b"foo"
    else:
        with pytest.raises(ValueError):
            fsn2bytes(fsnative(u"foo"), "notanencoding")
        with pytest.raises(ValueError):
            fsn2bytes(fsnative(u"foo"), None)  # type: ignore
        with pytest.raises(TypeError):
            fsn2bytes(fsnative(u"foo"), object())  # type: ignore

    for path in iternotfsn():
        with pytest.raises(TypeError):
            fsn2bytes(path)

    assert fsn2bytes(fsnative(u"foo"), "utf-8") == fsn2bytes(fsnative(u"foo"))


@pytest.mark.skipif(os.name != "nt", reason="win only")
def test_fsn2bytes_surrogate_pairs():
    # type: () -> None

    assert fsn2bytes(u"\uD800\uDC01", "utf-8") == b"\xf0\x90\x80\x81"
    assert fsn2bytes(u"\uD800\uDC01", "utf-16-le") == b"\x00\xd8\x01\xdc"
    assert fsn2bytes(u"\uD800\uDC01", "utf-16-be") == b"\xd8\x00\xdc\x01"
    assert fsn2bytes(u"\uD800\uDC01", "utf-16") == b"\xff\xfe\x00\xd8\x01\xdc"
    assert fsn2bytes(u"\uD800\uDC01", "utf-32-le") == b"\x01\x00\x01\x00"
    assert fsn2bytes(u"\uD800\uDC01", "utf-32-be") == b"\x00\x01\x00\x01"

    for c in ["utf-8", "utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"]:
        assert fsn2bytes(
            bytes2fsn(fsn2bytes(u"\uD800", c), c) +
            bytes2fsn(fsn2bytes(u"\uDC01", c), c), c) == \
            fsn2bytes(u"\uD800\uDC01", c)


@pytest.mark.skipif(os.name != "nt", reason="win only")
def test_fsn2bytes_wtf8():
    # type: () -> None

    test_data = {
        u"aé ": b"a\xC3\xA9 ",
        u"aé 💩": b"a\xC3\xA9 \xF0\x9F\x92\xA9",
        u"\uD83D\x20\uDCA9": b"\xED\xA0\xBD \xED\xB2\xA9",
        u"\uD800\uDBFF": b"\xED\xA0\x80\xED\xAF\xBF",
        u"\uD800\uE000": b"\xED\xA0\x80\xEE\x80\x80",
        u"\uD7FF\uDC00": b"\xED\x9F\xBF\xED\xB0\x80",
        u"\x61\uDC00": b"\x61\xED\xB0\x80",
        u"\uDC00": b"\xED\xB0\x80",
    }

    for uni, data in test_data.items():
        assert fsn2bytes(uni, "utf-8") == data

    def cat(*args):
        return fsn2bytes(
            "".join([bytes2fsn(a, "utf-8") for a in args]), "utf-8")

    assert cat(b"\xED\xA0\xBD", b"\xED\xB2\xA9") == b"\xF0\x9F\x92\xA9"
    assert cat(b"\xED\xA0\xBD", b" ", b"\xED\xB2\xA9") == \
        b"\xED\xA0\xBD \xED\xB2\xA9"
    assert cat(b"\xED\xA0\x80", b"\xED\xAF\xBF") == \
        b"\xED\xA0\x80\xED\xAF\xBF"
    assert cat(b"\xED\xA0\x80", b"\xEE\x80\x80") == \
        b"\xED\xA0\x80\xEE\x80\x80"
    assert cat(b"\xED\x9F\xBF", b"\xED\xB0\x80") == b"\xED\x9F\xBF\xED\xB0\x80"
    assert cat(b"a", b"\xED\xB0\x80") == b"\x61\xED\xB0\x80"
    assert cat(b"\xED\xB0\x80") == b"\xED\xB0\x80"


@pytest.mark.skipif(os.name != "nt", reason="win only")
def test_fsn2bytes_ill_formed_utf16():
    # type: () -> None

    p = bytes2fsn(b"a\x00\xe9\x00 \x00=\xd8=\xd8\xa9\xdc", "utf-16-le")
    assert fsn2bytes(p, "utf-8") == b"a\xC3\xA9 \xED\xA0\xBD\xF0\x9F\x92\xA9"
    assert fsn2bytes(u"aé " + u"\uD83D" + u"💩", "utf-16-le") == \
        b'a\x00\xe9\x00 \x00=\xd8=\xd8\xa9\xdc'


def test_surrogates():
    # type: () -> None

    if sys.platform == "win32":
        assert fsn2bytes(u"\ud83d", "utf-16-le") == b"=\xd8"
        assert bytes2fsn(b"\xd8=", "utf-16-be") == u"\ud83d"

        with pytest.raises(ValueError):
            bytes2fsn(b"\xd8=a", "utf-16-be")

        with pytest.raises(ValueError):
            bytes2fsn(b"=\xd8a", "utf-16-le")

        # for utf-16-le we have a workaround
        assert bytes2fsn(b"=\xd8", "utf-16-le") == u"\ud83d"
        assert bytes2fsn(b"=\xd8=\xd8", "utf-16-le") == u"\ud83d\ud83d"

        with pytest.raises(ValueError):
            bytes2fsn(b"=\xd8\x00\x00", "utf-16-le")

        # 4 byte code point
        assert fsn2bytes(u"\U0001f600", "utf-16-le") == b"=\xd8\x00\xde"
        assert bytes2fsn(b"=\xd8\x00\xde", "utf-16-le") == u"\U0001f600"

        # 4 byte codepoint + lone surrogate
        assert bytes2fsn(b"=\xd8\x00\xde=\xd8", "utf-16-le") == \
            u"\U0001f600\ud83d"

        with pytest.raises(UnicodeDecodeError):
            bytes2fsn(b"a", "utf-16-le")

        assert fsn2bytes(u"\ud83d", "utf-8") == b"\xed\xa0\xbd"
        assert bytes2fsn(b"\xed\xa0\xbd", "utf-8") == u"\ud83d"

        assert fsnative(u"\ud83d") == u"\ud83d"
        assert fsn2text(u"\ud83d") == u"\ufffd"

        # at least don't fail...
        assert fsn2uri(u"C:\\\ud83d") == u"file:///C:/%ED%A0%BD"
    else:
        # this shouldn't fail and produce the same result on py2/3 at least.
        assert fsn2bytes(fsnative(u"\ud83d"), None) == b"\xed\xa0\xbd"
        text2fsn(fsn2text(fsnative(u"\ud83d")))

        if PY2 and isunicodeencoding():
            # under Python 2 we get surrogates, but we can't do anything about
            # it since most codecs don't treat that as an error
            assert fsn2text(fsnative(u"\ud83d")) == u"\ud83d"
        else:
            # under Python 3 the decoder don't allow surrogates
            assert fsn2text(fsnative(u"\ud83d")) == u"\ufffd\ufffd\ufffd"


def test_bytes2fsn():
    # type: () -> None

    assert bytes2fsn(b"foo", "utf-8") == fsnative(u"foo")
    assert (bytes2fsn(fsn2bytes(fsnative(u"\u1234"), "utf-8"), "utf-8") ==
            fsnative(u"\u1234"))

    with pytest.raises(ValueError):
        bytes2fsn(b"\x00", "utf-8")

    with pytest.raises(ValueError):
        bytes2fsn(b"\x00\x00", "utf-16-le")

    with pytest.raises(TypeError):
        bytes2fsn(object(), "utf-8")  # type: ignore

    with pytest.raises(TypeError):
        bytes2fsn(u"data", "utf-8")  # type: ignore

    if sys.platform == "win32":
        with pytest.raises(ValueError):
            bytes2fsn(b"data", "notanencoding")
        with pytest.raises(ValueError):
            bytes2fsn(b"data", None)  # type: ignore
        with pytest.raises(TypeError):
            bytes2fsn(b"data", object())  # type: ignore

    assert bytes2fsn(b"foo", "utf-8") == bytes2fsn(b"foo")


def test_constants():
    # type: () -> None

    assert isinstance(sep, fsnative)
    assert isinstance(pathsep, fsnative)
    assert isinstance(curdir, fsnative)
    assert isinstance(pardir, fsnative)
    assert altsep is None or isinstance(altsep, fsnative)
    assert isinstance(extsep, fsnative)
    assert isinstance(devnull, fsnative)
    assert isinstance(defpath, fsnative)


def test_argv():
    # type: () -> None

    assert len(sys.argv) == len(argv)
    assert all(isinstance(v, fsnative) for v in argv)
    assert all(isinstance(v, fsnative) for v in argv[:])


def test_argv_change():
    # type: () -> None

    with preserve_argv():
        argv.append(fsnative(u"\u1234"))
        assert argv[-1] == fsnative(u"\u1234")
        assert len(sys.argv) == len(argv)
        assert sys.argv[-1] in (fsnative(u"\u1234"), "?")
        argv[-1] = fsnative(u"X")
        assert path2fsn(sys.argv[-1]) == argv[-1]
        del argv[-1]
        assert len(sys.argv) == len(argv)

    with preserve_argv():
        sys.argv[0] = sys.argv[0] + sys.argv[0]
        if path2fsn(sys.argv[0]) != argv[0]:
            del sys.argv[:]
            argv[0] = fsnative(u"")
            del argv[0]

    with preserve_argv():
        argv[:] = [fsnative(u"foo")]
        assert repr(argv).replace("u'", "'") == repr(sys.argv)
        assert argv[:] == argv

    with preserve_argv():
        del argv[:]
        assert not argv
        assert argv == []
        assert argv == argv
        assert not argv != argv
        argv.append("")
        assert len(argv) == 1
        assert isinstance(argv[-1], fsnative)
        argv.insert(0, "")
        assert isinstance(argv[0], fsnative)
        assert len(argv) == 2
        assert not (argv > argv)


def test_getcwd():
    # type: () -> None

    assert isinstance(getcwd(), fsnative)


def test_environ():
    # type: () -> None

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

    try:
        environ["=="] = "bla"
    except ValueError:
        # fails on Windows and on Linux with some Python versions
        pass

    assert len(environ) == len(environ.keys())
    repr(environ)


def test_environ_case():
    # type: () -> None

    if not environ_case_sensitive:
        with preserve_environ():
            environ.pop("foo", None)
            environ["FoO"] = "bla"
            assert environ["foo"] == "bla"
            for key in ["foo", "FoO"]:
                assert os.environ[key] == environ[key]
    else:
        with preserve_environ():
            environ["foo"] = "1"
            environ["FOO"] = "2"
            assert environ["foo"] != environ["FOO"]
            for key in ["foo", "FOO"]:
                assert os.environ[key] == environ[key]


@pytest.mark.skipif(os.name != "nt", reason="win only")
def test_environ_mirror():
    # type: () -> None

    with preserve_environ():
        os.environ.pop("BLA", None)
        environ["BLA"] = u"\ud83d"
        assert "BLA" in os.environ
        assert os.environ["BLA"] in (u"\ud83d", "?")
        assert get_windows_env_var(u"BLA") == u"\ud83d"
        del environ["BLA"]
        assert "BLA" not in os.environ
        assert getenv("BLA") is None


def test_getenv():
    # type: () -> None

    environ["foo"] = "bar"

    assert getenv("foo") == "bar"
    del environ["foo"]
    assert getenv("foo", "quux") == "quux"
    assert getenv("foo") is None


def test_unsetenv():
    # type: () -> None

    putenv("foo", "bar")
    # for some reason getenv goes to the cache, which makes it hard to test
    # things
    assert getenv("foo") is None
    unsetenv("foo")
    unsetenv("foo")
    assert getenv("foo") is None


def test_putenv():
    # type: () -> None

    try:
        putenv("==", "bla")
    except ValueError:
        pass


def test_uri2fsn():
    # type: () -> None

    if sys.platform != "win32":
        with pytest.raises(ValueError):
            assert uri2fsn(u"file:///%00")
        with pytest.raises(ValueError):
            assert uri2fsn("file:///%00")
        assert uri2fsn("file:///foo") == fsnative(u"/foo")
        assert uri2fsn(u"file:///foo") == fsnative(u"/foo")
        assert isinstance(uri2fsn("file:///foo"), fsnative)
        assert isinstance(uri2fsn(u"file:///foo"), fsnative)
        assert \
            uri2fsn("file:///foo-%E1%88%B4") == path2fsn(b"/foo-\xe1\x88\xb4")
        assert uri2fsn("file:NOPE") == fsnative(u"/NOPE")
        assert uri2fsn("file:/NOPE") == fsnative(u"/NOPE")
        with pytest.raises(ValueError):
            assert uri2fsn("file://NOPE")
        assert uri2fsn("file:///bla:foo@NOPE.com") == \
            fsnative(u"/bla:foo@NOPE.com")
        assert uri2fsn("file:///bla?x#b") == fsnative(u"/bla?x#b")
    else:
        assert uri2fsn("file:///C:/%ED%A0%80") == fsnative(u"C:\\\ud800")
        assert uri2fsn("file:///C:/%20") == "C:\\ "
        assert uri2fsn("file:NOPE") == "\\NOPE"
        assert uri2fsn("file:/NOPE") == "\\NOPE"
        with pytest.raises(ValueError):
            assert uri2fsn(u"file:///C:/%00")
        with pytest.raises(ValueError):
            assert uri2fsn("file:///C:/%00")
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
        uri2fsn(object())  # type: ignore

    with pytest.raises(ValueError):
        uri2fsn("http://www.foo.bar")

    if os.name == "nt":
        with pytest.raises(ValueError):
            uri2fsn(u"\u1234")

    if PY3:
        with pytest.raises(TypeError):
            uri2fsn(b"file:///foo")  # type: ignore


def test_fsn2uri():
    # type: () -> None

    with pytest.raises(TypeError):
        fsn2uri(object())  # type: ignore

    if sys.platform == "win32":
        with pytest.raises(TypeError):
            fsn2uri(u"\x00")
        assert fsn2uri(fsnative(u"C:\\\ud800")) == "file:///C:/%ED%A0%80"
        if is_wine:
            # FIXME: fails on native Windows
            assert fsn2uri(fsnative(u"C:\\ ")) == "file:///C:/%20"
        assert fsn2uri(fsnative(u"C:\\foo")) == "file:///C:/foo"
        assert fsn2uri(u"C:\\ö ä%") == "file:///C:/%C3%B6%20%C3%A4%25"
        assert (fsn2uri(u"C:\\foo-\u1234") ==
                "file:///C:/foo-%E1%88%B4")
        assert isinstance(fsn2uri(u"C:\\foo-\u1234"), text_type)
        assert fsn2uri(u"\\\\serv\\share\\") == "file://serv/share/"
        assert fsn2uri(u"\\\\serv\\\u1234\\") == "file://serv/%E1%88%B4/"
        assert \
            fsn2uri(fsnative(u"\\\\UNC\\foo\\bar")) == u"file://UNC/foo/bar"

        # winapi can't handle too large paths. make sure we raise properly
        with pytest.raises(ValueError):
            fsn2uri(u"C:\\" + 4000 * u"a")

        assert fsn2uri(u"C:\\\uD800\uDC01") == u"file:///C:/%F0%90%80%81"
    else:
        with pytest.raises(TypeError):
            fsn2uri(b"\x00")  # type: ignore
        if PY2:
            path = "/foo-\xe1\x88\xb4"
        else:
            path = fsnative(u"/foo-\u1234")
        assert fsn2uri(path) == "file:///foo-%E1%88%B4"
        assert isinstance(fsn2uri(path), text_type)


def test_uri_roundtrip():
    # type: () -> None

    if sys.platform == "win32":
        for path in [u"C:\\foo-\u1234", u"C:\\bla\\quux ha",
                     u"\\\\\u1234\\foo\\\u1423", u"\\\\foo;\\f"]:
            path = fsnative(path)
            assert uri2fsn(fsn2uri(path)) == path
            assert isinstance(uri2fsn(fsn2uri(path)), fsnative)
    else:
        path = path2fsn(b"/foo-\xe1\x88\xb4")

        assert uri2fsn(fsn2uri(path2fsn(b"/\x80"))) == path2fsn(b"/\x80")
        assert uri2fsn(fsn2uri(fsnative(u"/foo"))) == "/foo"
        assert uri2fsn(fsn2uri(path)) == path
        assert isinstance(uri2fsn(fsn2uri(path)), fsnative)


def test_mkdtemp():
    # type: () -> None

    fsn = mkdtemp()
    assert isinstance(fsn, fsnative)
    os.rmdir(fsn)

    fsn = mkdtemp(suffix="foo")
    fsn.endswith("foo")
    assert isinstance(fsn, fsnative)
    os.rmdir(fsn)


def test_test_mkstemp():
    # type: () -> None

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
    # type: () -> None

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


def test_expandvars_case():
    # type: () -> None

    if not environ_case_sensitive:
        with preserve_environ():
            environ.pop("foo", None)
            environ["FOO"] = "bar"
            assert expandvars("$foo") == "bar"
            environ["FOo"] = "baz"
            assert expandvars("$fOO") == "baz"
    else:
        with preserve_environ():
            environ.pop("foo", None)
            environ["FOO"] = "bar"
            assert expandvars("$foo") == "$foo"


def test_python_handling_broken_utf16():
    # type: () -> None

    # Create a file with an invalid utf-16 name.
    # Mainly to see how Python handles it

    tmp = mkdtemp()
    try:
        path = os.path.join(tmp, "foo")
        with open(path, "wb") as h:
            h.write(b"content")
        assert "foo" in os.listdir(tmp)

        if sys.platform == "win32":
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


def test_fsn2norm():
    # type: () -> None
    if sys.platform == "win32":
        assert fsn2norm(u"\uD800\uDC01") == fsn2norm(u"\U00010001")

    if PY3 and is_unix and isunicodeencoding():
        assert fsn2norm(u'\udcc2\udc80') == fsn2norm(u'\x80')

    for path in iternotfsn():
        with pytest.raises(TypeError):
            fsn2norm(path)


def test_supports_ansi_escape_codes():
    # type: () -> None
    supports_ansi_escape_codes(sys.stdout.fileno())
