# -*- coding: utf-8 -*-
# Copyright 2017 Christoph Reiter
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

import sys

import senf


def main(argv):
    assert len(argv) <= 2

    if len(argv) == 2:
        key = argv[-1]
        if key not in senf.environ:
            return 1
        senf.print_(senf.environ[key])
        return

    for key, value in sorted(senf.environ.items()):

        if not senf.supports_ansi_escape_codes(sys.stdout.fileno()):
            reset = color1 = color2 = ""
        else:
            reset = "\033[0m"
            color1 = "\033[1;91m"
            color2 = "\033[1;94m"

        senf.print_("%s%s%s=%s%s" % (color1, key, color2, reset, value))


if __name__ == "__main__":
    sys.exit(main(senf.argv))
