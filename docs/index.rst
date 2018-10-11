.. image:: images/header.svg
   :align: center
   :width: 400px

.. toctree::
    :hidden:
    :titlesonly:

    changelog
    tutorial
    api
    examples
    faq

.. title:: Overview

.. currentmodule:: senf

|

**Senf** introduces a new platform native string type called `fsnative`. It
adds functions to convert text, bytes and paths to and from that new type and
helper functions to integrate it nicely with the Python stdlib.

**Senf** supports Python 2.7, 3.3+, works with PyPy, works on Linux, Windows,
macOS, is MIT licensed, and only depends on the stdlib. It does not monkey
patch anything in the stdlib.

::

    pip install senf

.. |github-logo| raw:: html

    <i class="fa fa-github"></i>

|github-logo| https://github.com/quodlibet/senf

Why?
----

OS strings are used in many different places across the Python stdlib. They
are used for filesystem paths, for environment variables (`os.environ`), for
program arguments (`sys.argv` and `subprocess`), for printing to the console
(`sys.stdout`, `sys.stderr`) and more.

The problem with them is that they come in many shapes and forms and handling
them has changed significantly between Python 2 and Python 3.

A valid platform native string is either `bytes`, `unicode`, `str` +
surrogates (either through the ``surrogatepass`` or the ``surrogateescape``
error handler) or anything implementing the ``__fspath__`` protocol. The
values of those types depend on the Python version, the platform and the
enviroment the program was started in. Ideally we don't want to care about any
of those details.

----

For example, assume you want to check the extension of a file name:

::

    import os
    from senf import path2fsn

    def has_extension(filename, ext):
        root, filename_ext = os.path.splitext(path2fsn(filemame))
        return filename_ext == path2fsn(ext)

This will just work everywhere. :func:`path2fsn` will convert anything which
is considered a valid path by Python to a `fsnative` and then we can just
compare by value. Note that Python stdlib functions will always returns the
same type which was passed in, so :func:`os.path.splitext` will return two
`fsnative` values.

----

Or you want to send a filename over some binary interface:

::

    from senf import fsnative, fsn2bytes, bytes2fsn

    def send(filename):
        assert isinstance(filename, fsnative)
        data = fsn2bytes(filename, "utf-8")
        return data

    def receive(data):
        filename = bytes2fsn(data, "utf-8")
        return filename

:func:`fsn2bytes` converts the path to binary ("utf-8" is used on Windows, or
"wtf-8" to be exact) and the receiving end re-creates the filename with
:func:`bytes2fsn`.

----

Another example is printing filenames and text to a console:

::

    import os
    from senf import print_, argv

    for filename in os.listdir(argv[1]):
        print_(u"File: ", filename)

**Senf** provids its own print function which can output platform strings as
is and mix them with text. No more encoding/decoding errors.

In addition, **Senf** emulates ANSI escape sequence handling when using the
Windows console and extends Python 2 under Windows with Unicode support for
`sys.argv` and `os.environ`.


Who?
----

**Senf** is used by the following software:

* `Quod Libet <https://quodlibet.readthedocs.io/>`__ - A multi platform music
  player
* `mutagen <https://mutagen.readthedocs.io>`__ - A Python multimedia tagging
  library
