#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 Christoph Reiter

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import senf


class pytest_command(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


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
        tests_require=['pytest'],
        cmdclass = {'test': pytest_command},
    )
