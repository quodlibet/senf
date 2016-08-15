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
import locale

from ._compat import text_type, PY3, PY2


def _fsnative(text):
    if not isinstance(text, text_type):
        raise TypeError("%r needs to be a text type (%r)" % (text, text_type))

    if fsnative_type is text_type:
        return text
    else:
        # Theoretically we should fail here in case we have a non-unicode
        # encoding. But this would make everything complicated and there is
        # no good way to handle a failure from the user site.
        return text.encode(fsencoding(), "replace")


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
        """

        def __new__(cls, text=u""):
            return _fsnative(text)

    new_type = meta("fsnative", tuple(), dict(impl.__dict__))
    new_type.__module__ = "senf"
    return new_type

fsnative_type = text_type if os.name == "nt" or PY3 else bytes
fsnative = _create_fsnative(fsnative_type)


def fsencoding():
    """The encoding used for paths, argv, environ, stdout and stdin"""

    assert fsnative_type is bytes

    return locale.getpreferredencoding() or "utf-8"


def py2fsn(path):
    """Turns certain internal paths exposed by Python 2 to a fsnative path
    e.g. senf.__path__[0]

    Args:
        path (str): The path to convert
    Returns:
        fsnative_type: The converted path
    """

    if not isinstance(path, str):
        raise TypeError("path needs to be str")

    if os.name == "nt" and PY2:
        return path.decode("utf-8")
    return path


def path2fsn(path):
    """Returns a fsnative path for a bytes path under Py3+Unix.
    If the passed in path is a fsnative path simply returns it.

    This is useful for interfaces which need so support bytes paths under Py3.
    """
    pass


def fsn2text():
    """Converts a path to text. This process is not reversible and should
    only be used for display purposes.
    """
    pass


def fsn2bytes(path, encoding):
    """Turns a path to bytes. If the path is not associated with an encoding
    the passed encoding is used (under Windows for example)
    """
    pass


def bytes2fsn(data, encoding):
    """Turns bytes to a path. If the path is not associated with an encoding
    the passed encoding is used (under Windows for example)
    """
    pass


def uri2fsn():
    """Takes a file URI and returns a fsnative path"""
    pass


def fsn2uri():
    """Takes a fsnative path and returns a file URI"""
    pass
