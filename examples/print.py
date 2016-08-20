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
from senf._print import ANSI

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
