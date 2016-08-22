#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 Christoph Reiter

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
    setup(
        name="senf",
        version=senf.version_string,
        url="https://github.com/lazka/senf",
        description=("Consistent filename handling for all Python versions "
                     "and platforms"),
        author="Christoph Reiter",
        author_email="reiter.christoph@gmail.com",
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
        cmdclass = {
            'test': pytest_command,
            'coverage': coverage_command,
        },
    )
