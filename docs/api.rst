=================
API Documentation
=================

.. currentmodule:: senf

Fsnative Related
----------------

Helper functions for working with the `fsnative` type

======================= =================================
:func:`fsnative`        Virtual path type and constructor
:func:`path2fsn`        Convert `pathlike` to `fsnative`
:func:`fsn2text`        Convert `fsnative` to `text`
:func:`text2fsn`        Convert `text` to `fsnative`
:func:`fsn2bytes`       Convert `fsnative` to `bytes`
:func:`bytes2fsn`       Convert `bytes` to `fsnative`
:func:`uri2fsn`         Convert URI to `fsnative`
:func:`fsn2uri`         Convert `fsnative` to ASCII URI
:func:`fsn2norm`        Normalize `fsnative`
======================= =================================


Stdlib Replacements
-------------------

Alternative implementations or wrappers of stdlib functions and constants. In
some cases their default is changed to return an fsnative path (mkdtemp() with
default arguments) or Unicode support for Windows is added (sys.argv)

======================= =======================================================
:data:`environ`         `os.environ` replacement
:data:`argv`            `sys.argv` replacement
:data:`sep`             `os.sep` replacement
:data:`pathsep`         `os.pathsep` replacement
:data:`curdir`          `os.curdir` replacement
:data:`pardir`          `os.pardir` replacement
:data:`altsep`          `os.altsep` replacement
:data:`extsep`          `os.extsep` replacement
:data:`devnull`         `os.devnull` replacement
:data:`defpath`         `os.defpath` replacement
:func:`getcwd`          `os.getcwd` replacement
:func:`getenv`          `os.getenv` replacement
:func:`putenv`          `os.putenv` replacement
:func:`unsetenv`        `os.unsetenv` replacement
:func:`print_`          :func:`print` replacement
:func:`input_`          :func:`input` replacement
:func:`expanduser`      :func:`os.path.expanduser` replacement
:func:`expandvars`      :func:`os.path.expandvars` replacement
:func:`gettempdir`      :func:`tempfile.gettempdir` replacement
:func:`gettempprefix`   :func:`tempfile.gettempprefix` replacement
:func:`mkstemp`         :func:`tempfile.mkstemp` replacement
:func:`mkdtemp`         :func:`tempfile.mkdtemp` replacement
======================= =======================================================

Misc Functions
--------------

================================== ============================================
:func:`supports_ansi_escape_codes` if the output file supports ANSI codes
================================== ============================================


Package Related
---------------

===================== ===============
`senf.version`        Version tuple
`senf.version_string` Version string
===================== ===============


----

.. autodata:: version

.. autodata:: version_string

.. autoclass:: fsnative

.. autofunction:: path2fsn

.. autofunction:: fsn2text

.. autofunction:: text2fsn

.. autofunction:: fsn2bytes

.. autofunction:: bytes2fsn

.. autofunction:: uri2fsn

.. autofunction:: fsn2uri

.. autofunction:: fsn2norm

.. autodata:: environ
    :annotation: = {}

.. autodata:: argv
    :annotation: = []

.. autodata:: sep

.. autodata:: pathsep

.. autodata:: curdir

.. autodata:: pardir

.. autodata:: altsep

.. autodata:: extsep

.. autodata:: devnull

.. autodata:: defpath

.. autofunction:: getcwd

.. autofunction:: getenv

.. autofunction:: putenv

.. autofunction:: unsetenv

.. autofunction:: print_

.. autofunction:: input_

.. autofunction:: expanduser

.. autofunction:: expandvars

.. autofunction:: gettempdir

.. autofunction:: gettempprefix

.. autofunction:: mkstemp

.. autofunction:: mkdtemp

.. autofunction:: supports_ansi_escape_codes


Documentation Types
-------------------

These types only exist for documentation purposes and represent different
types depending on the Python version and platform used.

.. currentmodule:: senf

.. class:: text()

    Represents :obj:`unicode` under Python 2 and :obj:`str` under Python 3.
    Does not include `surrogates
    <https://www.python.org/dev/peps/pep-0383/>`__.


.. class:: bytes()

    Represents :obj:`python:str` under Python 2 and :obj:`python3:bytes` under
    Python 3.


.. class:: pathlike()

    Anything the Python stdlib allows as a path. In addition to `fsnative`
    this allows

    * :obj:`bytes` encoded with the default file system encoding
      (usually ``mbcs``) on Windows.
    * :obj:`bytes` under Python 3 + Unix.
    * :obj:`unicode` under Python 2 + Unix if it can be encoded with the
      default file system encoding.
    * (Python 3.6+) Instances where its type implements the ``__fspath__``
      protocol. See `PEP 519 <http://legacy.python.org/dev/peps/pep-0519/>`__
      for details.
