=================
API Documentation
=================

.. currentmodule:: senf

Package Related
---------------

.. autodata:: version

.. autodata:: version_string


Fsnative Related
----------------

Helper functions to work with the fsnative type

.. autoclass:: fsnative

.. autofunction:: path2fsn

.. autofunction:: fsn2text

.. autofunction:: text2fsn

.. autofunction:: fsn2bytes

.. autofunction:: bytes2fsn

.. autofunction:: uri2fsn

.. autofunction:: fsn2uri

.. autofunction:: fsn2uri_ascii


Stdlib Replacements
-------------------

Alternative implementations or wrappers of stdlib functions and constants. In
some cases their default is changed to return an fsnative path (mkdtemp() with
default arguments) or Unicode support for Windows is added (sys.argv)

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


Documentation Types
-------------------

These types only exist for documentation purposes and represent different
types depending on the Python version and platform used.

.. currentmodule:: senf

.. class:: text()

    Represents :obj:`unicode` under Python 2 and :obj:`str` under Python 3.


.. class:: bytes()

    Represents :obj:`python:str` under Python 2 and :obj:`python3:bytes` under
    Python 3.


.. class:: pathlike()

    Anything the Python stdlib allows as a path. In addition to `fsnative`
    this allows MBCS :obj:`python:str` under Python 2 + Windows and
    :obj:`python3:bytes` under Python 3 + Unix.
