#!/bin/bash

./run_wine.sh 2.7.12 -m coverage run --include "senf\\*" setup.py test
sed -i -e 's/Z://g' .coverage
sed -i -e 's/\\\\/\//g' .coverage
mv .coverage .coverage.win.py2

./run_wine.sh 3.4.4 -m coverage run --include "senf\\*" setup.py test
sed -i -e 's/Z://g' .coverage
sed -i -e 's/\\\\/\//g' .coverage
mv .coverage .coverage.win.py3

python-coverage run --include "senf/*" setup.py test
mv .coverage .coverage.unix.py2

python3-coverage run --include "senf/*" setup.py test
mv .coverage .coverage.unix.py3

python-coverage combine
python-coverage html -d coverage
