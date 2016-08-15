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

import ctypes
from ctypes import WinDLL, wintypes


user32 = WinDLL("user32")
shell32 = WinDLL("shell32")
kernel32 = WinDLL("kernel32")

GetCommandLineW = kernel32.GetCommandLineW
GetCommandLineW.argtypes = []
GetCommandLineW.restype = wintypes.LPCWSTR

CommandLineToArgvW = shell32.CommandLineToArgvW
CommandLineToArgvW.argtypes = [
    wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)

LocalFree = kernel32.LocalFree
LocalFree.argtypes = [wintypes.HLOCAL]
LocalFree.restype = wintypes.HLOCAL

LPCTSTR = ctypes.c_wchar_p
LPTSTR = wintypes.LPWSTR

SetEnvironmentVariableW = kernel32.SetEnvironmentVariableW
SetEnvironmentVariableW.argtypes = [LPCTSTR, LPCTSTR]
SetEnvironmentVariableW.restype = wintypes.BOOL

GetEnvironmentVariableW = kernel32.GetEnvironmentVariableW
GetEnvironmentVariableW.argtypes = [LPCTSTR, LPTSTR, wintypes.DWORD]
GetEnvironmentVariableW.restype = wintypes.DWORD

GetEnvironmentStringsW = kernel32.GetEnvironmentStringsW
GetEnvironmentStringsW.argtypes = []
GetEnvironmentStringsW.restype = ctypes.c_void_p

FreeEnvironmentStringsW = kernel32.FreeEnvironmentStringsW
FreeEnvironmentStringsW.argtypes = [ctypes.c_void_p]
FreeEnvironmentStringsW.restype = ctypes.c_bool
