=================
API Documentation
=================

Package Related
---------------

.. autodata:: senf.version

.. autodata:: senf.version_string


Fsnative Related
----------------

.. autofunction:: senf.fsnative


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


.. class:: fsnative_type()

    Represents a file name which can be :obj:`python:str` or
    :obj:`python:unicode` under Python 2 and :obj:`python3:str` +
    ``surrogateescape`` under Python 3.
