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
import ctypes
import collections

from ._compat import text_type, PY2
if os.name == "nt":
    from ._winapi import SetEnvironmentVariableW, GetEnvironmentStringsW, \
        FreeEnvironmentStringsW, GetEnvironmentVariableW


def get_windows_env_var(key):
    """Get an env var.

    Raises:
        WindowsError
    """

    if not isinstance(key, text_type):
        raise TypeError("%r not of type %r" % (key, text_type))

    buf = ctypes.create_unicode_buffer(32767)

    stored = GetEnvironmentVariableW(key, buf, 32767)
    if stored == 0:
        raise ctypes.WinError()
    return buf[:stored]


def set_windows_env_var(key, value):
    """Set an env var.

    Raises:
        WindowsError
    """

    if not isinstance(key, text_type):
        raise TypeError("%r not of type %r" % (key, text_type))

    if not isinstance(value, text_type):
        raise TypeError("%r not of type %r" % (value, text_type))

    status = SetEnvironmentVariableW(key, value)
    if status == 0:
        raise ctypes.WinError()


def del_windows_env_var(key):
    """Delete an env var.

    Raises:
        WindowsError
    """

    if not isinstance(key, text_type):
        raise TypeError("%r not of type %r" % (key, text_type))

    status = SetEnvironmentVariableW(key, None)
    if status == 0:
        raise ctypes.WinError()


def read_windows_environ():
    """Returns a unicode dict of the Windows environment.

    Raises:
        WindowsEnvironError
    """

    res = GetEnvironmentStringsW()
    if not res:
        raise ctypes.WinError()

    res = ctypes.cast(res, ctypes.POINTER(ctypes.c_wchar))

    done = []
    current = u""
    i = 0
    while 1:
        c = res[i]
        i += 1
        if c == u"\x00":
            if not current:
                break
            done.append(current)
            current = u""
            continue
        current += c

    dict_ = {}
    for entry in done:
        try:
            key, value = entry.split(u"=", 1)
        except ValueError:
            continue
        dict_[key] = value

    status = FreeEnvironmentStringsW(res)
    if status == 0:
        raise ctypes.WinError()

    return dict_


class WindowsEnviron(collections.MutableMapping):
    """os.environ that supports unicode on Windows.

    Like os.environ it will only contain the environment content present at
    load time. Changes will be synced with the real environment.
    """

    def __init__(self):
        try:
            env = read_windows_environ()
        except WindowsError:
            env = {}
        self._env = env

    def __getitem__(self, key):
        key = text_type(key)
        return self._env[key]

    def __setitem__(self, key, value):
        key = text_type(key)
        value = text_type(value)
        try:
            set_windows_env_var(key, value)
        except WindowsError:
            pass
        self._env[key] = value

    def __delitem__(self, key):
        key = text_type(key)
        try:
            del_windows_env_var(key)
        except WindowsError:
            pass
        del self._env[key]

    def __iter__(self):
        return iter(self._env)

    def __len__(self):
        return len(self._env)

    def __repr__(self):
        return repr(self._env)


def create_environ():
    if os.name == "nt" and PY2:
        return WindowsEnviron()
    return os.environ


environ = create_environ()
