.. image:: images/header.svg
   :align: center
   :width: 400px

.. toctree::
    :hidden:
    :titlesonly:

    changelog
    tutorial
    api

.. title:: Overview

.. currentmodule:: senf


What?
-----

**Senf** makes filename handling easier by providing a set of filename
handling functions which work the same across all Python versions and
platforms. It also provides a print() function which can print filenames and
an input() function which can read filenames.

You can think of it as `six <https://pypi.org/project/six/>`__ for filename
handling.

It supports Python 2.6, 2.7, 3.3+, works with PyPy, works on Linux, Windows,
macOS, is MIT licensed, and only depends on the stdlib.

::

    pip install senf

The following example prints wrongly encoded filenames on Unix, Unicode
filenames on Windows and supports Unicode command line arguments on Windows +
Python 2.

::

    import os
    from senf import argv, print_, fsn2text, fsn2uri

    dir_ = os.path.abspath(argv[1])
    for entry in os.listdir(dir_):
        path = os.path.join(dir_, entry)
        print_(u"File: ", path)
        print_(u"Text: ", fsn2text(path))
        print_(u"URI: ", fsn2uri(path))

**Senf** does not monkey patch anything in the stdlib, it just provides
alternatives and wrappers.

See the :doc:`tutorial`, :doc:`api` and `GitHub repo
<https://github.com/lazka/senf>`__ for more details.


Who?
----

You might want to use Senf if you

* use Python 2 and want to improve your Windows support
* use Python 2 and want to move (gradually) to Python 3
* have a library which needs to support both Python 2 and Python 3
* want to print filenames


How?
----

It introduces a virtual type called `fsnative` which actually represents

- :obj:`python:unicode` under Python 2 + Windows
- :obj:`python:str` under Python 2 + Unix
- :obj:`python3:str` under Python 3 + Windows
- :obj:`python3:str` + ``surrogates`` (only containing code points which can
  be encoded with the locale encoding) under Python 3 + Unix [#]_

The type is used for filenames, environment variables and process arguments
and Senf provides functions so you can tread it as an opaque type and not have
to worry about its content or encoding.

The other nice thing about the `fsnative` type is that you can mix it with
ASCII `str` on all Python versions and platforms [#]_ which means minimal
change to your code:

::

    os.path.join(some_fsnative_path, "somefile")
    some_fsnative_path.endswith(".txt")
    some_fsnative_path == "foo.txt"
    "File: %s" % some_fsnative_path

For non-ASCII text you will need to use the `fsnative` helper:

::

    os.path.join(some_fsnative_path, fsnative(u"Gewürze"))

----

.. [#] Under Python 3, bytes is also a valid type for paths under Unix.
       Senf does not use/allow it as there are stdlib modules, like pathlib,
       which don't support bytes and mixing bytes with str + surrogates
       doesn't work.
.. [#] As long as you don't use "unicode_literals", which I strongly
       recommend you don't use.
