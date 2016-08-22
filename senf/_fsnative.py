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
import ctypes

from . import _winapi as winapi
from ._compat import text_type, PY3, PY2, url2pathname, urlparse, quote


is_win = os.name == "nt"
is_unix = not is_win
is_darwin = sys.platform == "darwin"


def _fsnative(text):
    if not isinstance(text, text_type):
        raise TypeError("%r needs to be a text type (%r)" % (text, text_type))

    if is_unix:
        # First we go to bytes so we can be sure we have a valid source.
        # Theoretically we should fail here in case we have a non-unicode
        # encoding. But this would make everything complicated and there is
        # no good way to handle a failure from the user side. Instead
        # fall back to utf-8 which is the most likely the right choice in
        # a mis-configured environment
        encoding = _encoding()
        try:
            path = text.encode(encoding)
        except UnicodeEncodeError:
            path = text.encode("utf-8")
        if PY3:
            return os.fsdecode(path)
        return path
    else:
        return text


def _create_fsnative(type_):
    # a bit of magic to make fsnative(u"foo") and isinstance(path, fsnative)
    # work

    class meta(type):

        def __instancecheck__(self, instance):
            return isinstance(instance, type_)

        def __subclasscheck__(self, subclass):
            return issubclass(subclass, type_)

    class impl(object):
        """fsnative(text)

        Args:
            text (text): The text to convert to a path
        Returns:
            fsnative:
                The new path. Depending on the Python version and platform
                this is either `text` or `bytes`.
        Raises:
            TypeError: In case something other then `text` has been passed

        This type is a virtual base class for the real path type.
        Instantiating it returns an instance of the real path type
        and it overrides instance and subclass checks so that

        ::

            isinstance(fsnative(u"foo"), fsnative) == True
            issubclass(type(fsnative(u"foo")), fsnative) == True

        works as well.

        Can't fail.
        """

        def __new__(cls, text=u""):
            return _fsnative(text)

    new_type = meta("fsnative", (object,), dict(impl.__dict__))
    new_type.__module__ = "senf"
    return new_type


fsnative_type = text_type if is_win or PY3 else bytes
fsnative = _create_fsnative(fsnative_type)


def _encoding():
    """The encoding used for paths, argv, environ, stdout and stdin"""

    assert is_unix, "only call on unix code paths"

    encoding = sys.getfilesystemencoding()
    if encoding is None:
        encoding = "utf-8" if is_darwin else "ascii"
    return encoding


def path2fsn(path):
    """
    Args:
        path (pathlike): The path to convert
    Returns:
        fsnative
    Raises:
        TypeError: In case the type can't be converted to a `fsnative`
        ValueError: In case conversion fails

    Returns a fsnative path for a path-like.

    If the passed in path is a `fsnative` path it simply returns it.
    This will not fail for a valid path (Either retrieved from stdlib functions
    or `argv` or `environ` or through the `fsnative` helper)
    """

    # allow mbcs str on py2+win and bytes on py3
    if PY2:
        if is_win:
            if isinstance(path, str):
                path = path.decode("mbcs")
        else:
            if isinstance(path, unicode):
                path = path.encode(_encoding())
    else:
        # TODO: If it ever gets added to Python we should call os.fspath() here
        if isinstance(path, bytes):
            path = os.fsdecode(path)
        if is_unix:
            # make sure we can encode it and this is not just some random
            # unicode string
            os.fsencode(path)

    if not isinstance(path, fsnative_type):
        raise TypeError("path needs to be %s", fsnative_type.__name__)

    return path


def fsn2text(path):
    """
    Args:
        path (fsnative): The path to convert
    Returns:
        `text`
    Raises:
        TypeError: In case no `fsnative` has been passed

    Converts a path to text. This process is not reversible and should
    only be used for display purposes.

    On Python 3 the resulting `str` will not contain surrogates.

    This can't fail if a valid `fsnative` gets passed.
    """

    if not isinstance(path, fsnative_type):
        raise TypeError("path needs to be %s", fsnative_type.__name__)

    if fsnative_type is bytes:
        return path.decode(_encoding(), "replace")
    else:
        if PY2 or is_win:
            return path
        else:
            return os.fsencode(path).decode(_encoding(), "replace")


def text2fsn(text):
    """
    Args:
        text (text): The text to convert
    Returns:
        `fsnative`

    Takes `text` and converts it to a `fsnative`. This operation is not
    reversible and can't fail.

    This is the same as calling ``fsnative(text)`` and available for
    consistency.
    """

    return fsnative(text)


def fsn2bytes(path, encoding):
    """
    Args:
        path (fsnative): The path to convert
        encoding (`str` or `None`): `None` if you don't care about Windows
    Returns:
        `bytes`
    Raises:
        TypeError: If no `fsnative` path is passed
        ValueError: On Windows if no valid encoding is passed or encoding fails

    Turns a path to bytes. If the path is not associated with an encoding
    the passed encoding is used (under Windows for example).
    """

    if not isinstance(path, fsnative_type):
        raise TypeError("path needs to be %s", fsnative_type.__name__)

    if is_win:
        if encoding is None:
            raise ValueError("invalid encoding %r" % encoding)
        try:
            return path.encode(encoding)
        except LookupError:
            raise ValueError("invalid encoding %r" % encoding)
    elif PY2:
        return path
    else:
        return os.fsencode(path)


def bytes2fsn(data, encoding):
    """
    Args:
        data (bytes): The data to convert
        encoding (`str` or `None`): `None` if you don't care about Windows
    Returns:
        `fsnative`
    Raises:
        TypeError: If no `bytes` path is passed
        ValueError: On Windows if no valid encoding is passed or decoding fails

    Turns bytes to a path. If the path is not associated with an encoding
    the passed encoding is used (under Windows for example)
    """

    if not isinstance(data, bytes):
        raise TypeError("data needs to be bytes")

    if is_win:
        if encoding is None:
            raise ValueError("invalid encoding %r" % encoding)
        try:
            return data.decode(encoding)
        except LookupError:
            raise ValueError("invalid encoding %r" % encoding)
    elif PY2:
        return data
    else:
        return os.fsdecode(data)


def uri2fsn(uri):
    """
    Args:
        uri (`text` or :obj:`python:str`): A file URI
    Returns:
        `fsnative`
    Raises:
        TypeError: In case an invalid type is passed
        ValueError: In case the URI isn't a valid file URI

    Takes a file URI and returns a fsnative path
    """

    if PY2:
        if isinstance(uri, unicode):
            uri = uri.encode("utf-8")
        if not isinstance(uri, bytes):
            raise TypeError("uri needs to be ascii str or unicode")
    else:
        if not isinstance(uri, str):
            raise TypeError("uri needs to be str")

    parsed = urlparse(uri)
    scheme = parsed.scheme
    netloc = parsed.netloc
    path = parsed.path

    if scheme != "file":
        raise ValueError("Not a file URI")

    if is_win:
        path = url2pathname(netloc + path)
        if netloc:
            path = "\\\\" + path
        if PY2:
            path = path.decode("utf-8")
        return path
    else:
        if PY2:
            return url2pathname(path)
        else:
            return fsnative(url2pathname(path))


def fsn2uri(path):
    """
    Args:
        path (fsnative): The path to convert to an URI
    Returns:
        `fsnative`
    Raises:
        TypeError: If no `fsnative` was passed
        ValueError: If the path can't be converted

    Takes a fsnative path and returns a file URI.

    On Windows this returns a unicode URI. If you want an ASCII URI
    use :func:`fsn2uri_ascii` instead.
    """

    if not isinstance(path, fsnative_type):
        raise TypeError("path needs to be %s", fsnative_type.__name__)

    if is_win:
        buf = ctypes.create_unicode_buffer(winapi.INTERNET_MAX_URL_LENGTH)
        length = winapi.DWORD(winapi.INTERNET_MAX_URL_LENGTH)
        flags = 0
        try:
            winapi.UrlCreateFromPathW(path, buf, ctypes.byref(length), flags)
        except WindowsError as e:
            raise ValueError(e)
        return buf[:length.value]
    else:
        if PY2:
            return "file://" + quote(path)
        else:
            return "file://" + quote(os.fsencode(path))


def fsn2uri_ascii(path):
    """
    Args:
        path (fsnative): The path to convert to an URI
    Returns:
        `str`: An ASCII only `str`
    Raises:
        TypeError: If no `fsnative` was passed
        ValueError: If the path can't be converted

    Takes a fsnative path and returns a file URI.

    Like fsn2uri() but returns ASCII only. On Windows non-ASCII characters
    will be encoded using utf-8 and then percent encoded.
    """

    if is_win:
        uri = fsn2uri(path)

        def quoter(c):
            try:
                c.encode("ascii")
            except ValueError:
                return quote(c.encode("utf-8"))
            else:
                return c

        uri = map(quoter, uri)
        if PY2:
            return u"".join(uri).encode("ascii")
        else:
            return "".join(uri)
    else:
        return fsn2uri(path)
