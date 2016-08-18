#!/bin/bash
# runs tests under all combinations and merges the coverage data

./run_wine.sh 2.7.12 python -m coverage run --branch --include "senf\\*" setup.py test -a "-s"
sed -i -e 's/Z://g' .coverage
sed -i -e 's/\\\\/\//g' .coverage
mv .coverage .coverage.win.py2

./run_wine.sh 3.4.4 python -m coverage run --branch --include "senf\\*" setup.py test -a "-s"
sed -i -e 's/Z://g' .coverage
sed -i -e 's/\\\\/\//g' .coverage
mv .coverage .coverage.win.py3

python-coverage run --branch --include "senf/*" setup.py test -a "-s"
mv .coverage .coverage.unix.py2

LANG=C python-coverage run --branch --include "senf/*" setup.py test -a "-s"
mv .coverage .coverage.unix.py2.c

python3-coverage run --branch --include "senf/*" setup.py test -a "-s"
mv .coverage .coverage.unix.py3

LANG=C python3-coverage run --branch --include "senf/*" setup.py test -a "-s"
mv .coverage .coverage.unix.py3.c

python-coverage combine
python-coverage html -d coverage
