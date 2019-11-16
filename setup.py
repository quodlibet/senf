#!/usr/bin/env python
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
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# type: ignore

import os
import sys

from setuptools import setup, Command

import senf


class coverage_command(Command):
    description = "generate test coverage data"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            from coverage import coverage
        except ImportError:
            raise SystemExit(
                "Missing 'coverage' module. See "
                "https://pypi.python.org/pypi/coverage or try "
                "`apt-get install python-coverage python3-coverage`")

        for key in list(sys.modules.keys()):
            if key.startswith('senf'):
                del(sys.modules[key])

        cov = coverage()
        cov.start()

        cmd = self.reinitialize_command("test")
        cmd.ensure_finalized()
        cmd.run()

        dest = os.path.join(os.getcwd(), "coverage")

        cov.stop()
        cov.html_report(
            directory=dest,
            ignore_errors=True,
            include=["senf/*"])

        print("Coverage summary: file://%s/index.html" % dest)


class pytest_command(Command):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        self.pytest_args = []

    def finalize_options(self):
        pass

    def run(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        if errno != 0:
            sys.exit(errno)


if __name__ == "__main__":

    with open('README.rst') as h:
        long_description = h.read()

    setup(
        name="senf",
        version=senf.version_string,
        url="https://github.com/quodlibet/senf",
        description=("Consistent filename handling for all Python versions "
                     "and platforms"),
        long_description=long_description,
        author="Christoph Reiter",
        author_email="reiter.christoph@gmail.com",
        packages=[
            "senf",
        ],
        package_data={
            "senf": [
                "__init__.pyi",
                "py.typed",
            ],
        },
        classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'License :: OSI Approved :: MIT License',
        ],
        tests_require=['pytest', 'typing', 'hypothesis'],
        python_requires=(
            '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4'),
        cmdclass={
            'test': pytest_command,
            'coverage': coverage_command,
        },
    )
