.. image:: images/header.svg
   :align: center
   :width: 400px

.. toctree::
    :hidden:
    :titlesonly:

    api

.. currentmodule:: senf


What?
-----

**senf** makes filename handing easier by papering over platform differences
in Python 2 and by making it easier to migrate to Python 3 or to have a mixed
Py2/Py3 code base. While at it, it improves the Unicode support for Python 2
under Windows to be on par with Python 3.

You can think of it as `six <https://pypi.org/project/six/>`__ for file path
handling.

It supports Python 2.6, 2.7, 3.3+, works with PyPy, and only depends on the
stdlib.

::

    import os
    from senf import fsnative, print_

    # This supports unicode file names under Py2/3 on Linux/macOS/Windows
    for entry in os.listdir(fsnative(u"my_dir")):
        print_(u"File: ", entry)

**senf** does not monkey patch stdlib functions, it just provides alternatives
and wrappers.


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

The type is used for file names, environment variables and process arguments
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


See the :doc:`api` for more details.


----

.. [#] Under Python 3, bytes is also a valid type for paths under Unix.
       We decide to not use/allow it as there are stdlib modules, like
       pathlib, which don't support bytes and mixing bytes with
       str + surrogateescape doesn't work.
.. [#] As long as you don't use "unicode_literals", which we strongly
       recommend you don't use.
