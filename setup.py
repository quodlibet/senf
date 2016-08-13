#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 Christoph Reiter

from distutils.core import setup

import senf


if __name__ == "__main__":
    setup(
        name="senf",
        version=senf.version_string,
        url="https://github.com/lazka/senf",
        description="like six but for paths and other environment data",
        author="Christoph Reiter",
        author_email="reiter.christoph@gmail.com",
        long_description="""\
senf makes it easy to handle file paths in a mixed py2/3 code base and while
at it backports some Python 3 improvements like unicode environ/argv to Python
2.""",
        packages=[
            "senf",
        ],
        classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'License :: OSI Approved :: MIT License',
        ],
    )
