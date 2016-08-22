.. image:: images/header.svg
   :align: center
   :width: 400px

.. toctree::
    :hidden:
    :titlesonly:

    changelog
    tutorial
    api

.. currentmodule:: senf


What?
-----

**senf** makes filename handling easier by providing a set of filename
handling functions which work the same across all Python versions and
supported platforms. It also provides a print() function which can print all
filenames.

You can think of it as `six <https://pypi.org/project/six/>`__ for filename
handling.

It supports Python 2.6, 2.7, 3.3+, works with PyPy, works on Linux, Windows,
macOS and only depends on the stdlib.

::

    import os
    from senf import argv, print_

    for entry in os.listdir(argv[1]):
        print_(u"File: ", entry)

The above example prints wrongly encoded filenames on Unix and unicode
filenames on Windows.

**senf** does not monkey patch stdlib functions, it just provides alternatives
and wrappers.

See the :doc:`tutorial` or :doc:`api` for more details.


Who?
----

You might want to use senf if you

* use Python 2 and want to improve your Windows support
* use Python 2 and want to move (gradually) to Python 3
* have a library which needs to support both Python 2 and Python 3
* want to print filenames


How?
----

It introduces a virtual type called `fsnative` which actually represents

- :obj:`python:unicode`  under Py2 + Windows
- :obj:`python:str` under Py2 on other platforms
- :obj:`python3:str` under Py3 + Windows
- :obj:`python3:str` + ``surrogates`` under Py3 on other platforms [#]_

The type is used for filenames, environment variables and process arguments
and senf provides functions so you can tread it as an opaque type and not have
to worry about its content or encoding.

The other nice thing about the `fsnative` type is that you can mix it with
ASCII `str` on all Python versions and platforms [#]_ which means minimal
change to your code:

::

    os.path.join(some_fsnative_path, "somefile")
    some_fsnative_path.endswith(".txt")
    some_fsnative_path == "foo.txt"

For non-ASCII text you will need to use the `fsnative` helper:

::

    os.path.join(some_fsnative_path, fsnative(u"Gewürze"))

----

.. [#] Under Python 3, bytes is also a valid type for paths under Unix.
       We decide to not use/allow it as there are stdlib modules, like
       pathlib, which don't support bytes and mixing bytes with
       str + surrogateescape doesn't work.
.. [#] As long as you don't use "unicode_literals", which we strongly
       recommend you don't use.
