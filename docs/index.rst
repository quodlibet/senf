.. image:: images/header.svg
   :align: center
   :width: 400px

.. toctree::
    :hidden:
    :titlesonly:

    api


What?
-----

**senf** makes filename handing easier by papering over platform differences
in Python 2 and by making it easier to migrate to Python 3 or to have a mixed
Py2/Py3 code base. While at it, it improves the Unicode support for Python 2
under Windows to be on par with Python 3.

It supports Python 2.6, 2.7, 3.3+, works with PyPy, and only depends on the
stdlib.

::

    import os
    from senf import fsnative, print_

    # This supports unicode file names under Py2/3 on Linux/macOS/Window
    for entry in os.listdir(fsnative(u"my_dir")):
        print_(u"File: ", entry)


Who?
----

You might want to use senf if you

* use Python 2 and want to improve your Windows support
* use Python 2 and want to move to Python 3
* have a library which needs to support both Python 2 and Python 3
* want to print filenames under Python 3


How?
----

The core type it introduces is the ``fsnative`` type which actually is

- `unicode` under Py2 + Windows
- `str` under Py2 on other platforms
- `str` under Py3 + Windows
- `str` + ``surrogateescape`` under Py3 on other platforms [#]_

The type is used for file names, environment variables and process arguments
and senf provides functions so you can tread it as an opaque type and not have
to worry about its content or encoding.

The other nice thing about the ``fsnative`` type is that you can mix it with
ASCII `str` on all Python versions and platforms [#]_ which means minimal
change to your code:

::

    os.path.join(some_fsnative_path, "somefile")
    some_fsnative_path.endswith(".txt")
    some_fsnative_path == "foo.txt"

For non-ASCII text you will need to use the ``fsnative`` wrapper:

::

    os.path.join(some_fsnative_path, fsnative(u"Gewürze"))


The provided functions and constants can be split into three categories:

1) Helper functions to work with the fsnative type
2) Alternative implementations of stdlib functions for introducing Unicode
   support under Windows + Python 2 (os.environ for example)
3) Wrappers for constants and functions which don't return a fsnative path
   by default (os.sep, mkdtemp() with default arguments)

senf does not monkey patch stdlib functions, it just provides alternatives and
wrappers.

----

.. [#] Under Python 3, bytes is also a valid type for paths under Unix.
       We decide to not use/allow it as there are stdlib modules, like
       pathlib, which don't support bytes and mixing bytes with
       str + surrogateescape doesn't work.
.. [#] As long as you don't use "unicode_literals", which we strongly
       recommend.
