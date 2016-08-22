Testing
-------

Python 2:

    ::

        py.test
        LANG=C py.test


Python 3:

    ::

        py.test-3
        LANG=C py.test-3


Windows + Python 2:

    ::

        ./run_wine.sh 2.7.12 cmd
        py.test


Windows + Python 3:

    ::

        ./run_wine.sh 3.4.4 cmd
        py.test


Coverage
--------

::

    ./coverage.sh
