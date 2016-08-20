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
import time

import senf


def main(argv):
    dir_ = argv[1]
    for entry in sorted(os.listdir(dir_)):
        path = os.path.join(dir_, entry)
        size = os.path.getsize(path)
        mtime = os.path.getmtime(path)
        mtime_format = time.strftime("%b %d %H:%M", time.localtime(mtime))

        reset = '\033[0m'
        if os.path.isdir(path):
            color = '\033[1;94m'
        elif os.access(path, os.X_OK):
            color = '\033[1;92m'
        else:
            color = ''

        senf.print_("%6d %13s %s%s%s" % (size, mtime_format, color, entry, reset))

if __name__ == "__main__":
    main(senf.argv)
