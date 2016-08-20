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

from senf import print_


class ANSI(object):

    SET_BOLD = '\033[1m'
    SET_DIM = '\033[2m'
    SET_ITALIC = '\033[3m'
    SET_UNDERLINE = '\033[4m'
    SET_BLINK = '\033[5m'
    SET_BLINK_FAST = '\033[6m'
    SET_REVERSE = '\033[7m'
    SET_HIDDEN = '\033[8m'

    RESET_ALL = '\033[0m'

    RESET_BOLD = '\033[21m'
    RESET_DIM = '\033[22m'
    RESET_ITALIC = '\033[23m'
    RESET_UNDERLINE = '\033[24m'
    RESET_BLINK = '\033[25m'
    RESET_BLINK_FAST = '\033[26m'
    RESET_REVERSE = '\033[27m'
    RESET_HIDDEN = '\033[28m'

    FG_BLACK = '\033[30m'
    FG_RED = '\033[31m'
    FG_GREEN = '\033[32m'
    FG_YELLOW = '\033[33m'
    FG_BLUE = '\033[34m'
    FG_MAGENTA = '\033[35m'
    FG_CYAN = '\033[36m'
    FG_WHITE = '\033[37m'

    FG_DEFAULT = '\033[39m'

    FG_LIGHT_BLACK = '\033[90m'
    FG_LIGHT_RED = '\033[91m'
    FG_LIGHT_GREEN = '\033[92m'
    FG_LIGHT_YELLOW = '\033[93m'
    FG_LIGHT_BLUE = '\033[94m'
    FG_LIGHT_MAGENTA = '\033[95m'
    FG_LIGHT_CYAN = '\033[96m'
    FG_LIGHT_WHITE = '\033[97m'

    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    BG_DEFAULT = '\033[49m'

    BG_LIGHT_BLACK = '\033[100m'
    BG_LIGHT_RED = '\033[101m'
    BG_LIGHT_GREEN = '\033[102m'
    BG_LIGHT_YELLOW = '\033[103m'
    BG_LIGHT_BLUE = '\033[104m'
    BG_LIGHT_MAGENTA = '\033[105m'
    BG_LIGHT_CYAN = '\033[106m'
    BG_LIGHT_WHITE = '\033[107m'


try:
    unichr_ = unichr
except NameError:
    unichr_ = chr


def main():
    N = ["black", "blue", "magenta", "red", "yellow", "green", "cyan", "white"]
    FG = [ANSI.FG_DEFAULT]
    for n in N:
        FG.append(getattr(ANSI, "FG_" + n.upper()))
        FG.append(getattr(ANSI, "FG_LIGHT_" + n.upper()))

    BG = [ANSI.BG_DEFAULT]
    for n in N:
        BG.append(getattr(ANSI, "BG_" + n.upper()))
        BG.append(getattr(ANSI, "BG_LIGHT_" + n.upper()))

    i = 0x180
    for background in BG:
        print_(background, end="")
        for foreground in FG:
            print_(foreground, end="")
            print_(ANSI.SET_UNDERLINE + unichr_(i) +
                   ANSI.RESET_UNDERLINE + " ", end="")
            print_(ANSI.SET_BOLD + unichr_(i) + ANSI.RESET_BOLD + " ", end="")
            i += 1
        print_()
    print_()


if __name__ == "__main__":
    main()
