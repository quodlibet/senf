========
Tutorial
========

.. currentmodule:: senf

There are various ways to create fsnative instances:

.. code-block:: pycon

    # create from unicode text
    >>> senf.fsnative(u"foo")
    'foo'

    # create from some serialized format
    >>> senf.bytes2fsn(b"foo", "utf-8")
    'foo'

    # create from an URI
    >>> senf.uri2fsn("file:///foo")
    '/foo'

    # create from some Python path-like
    >>> senf.path2fsn(b"foo")
    'foo'

You can mix and match the fsnative type with ASCII str on all Python versions
and platforms:

.. code-block:: pycon

    >>> senf.fsnative(u"foo") + "bar"
    'foobar'
    >>> senf.fsnative(u"foo").endswith("foo")
    True
    >>> "File: %s" % senf.fsnative(u"foo")
    'File: foo'

Now that we have a `fsnative`, what can we do with it?

.. code-block:: pycon

    >>> path = senf.fsnative(u"/foo")

    # We can print it
    >>> senf.print_(path)
    /foo

    # We can convert it to text for our favorite GUI toolkit
    >>> senf.fsn2text(path)
    '/foo'

    # We can convert it to an ASCII only URI
    >>> senf.fsn2uri(path)
    'file:///foo'

    # We can serialize the path so we can save it somewhere
    >>> senf.fsn2bytes(path, "utf-8")
    b'/foo'

The functions in the stdlib usually return the same type as was passed in. If
we pass in a `fsnative` to `os.listdir`, we get one back as well.

::

    >>> files = os.listdir(senf.fsnative(u"."))
    >>> isinstance(files[0], senf.fsnative)
    True

In some cases the stdlib functions don't take arguments and always return the
same type. For those cases Senf provide alternative implementations.

::

    >>> isinstance(senf.getcwd(), senf.fsnative)
    True

A similar problem arises with stdlib collections. Senf provides alternatives
for `sys.argv` and `os.environ`.

::

    >>> isinstance(senf.argv[0], senf.fsnative)
    True
    >>> isinstance(senf.environ["PATH"], senf.fsnative)
    True

Also for `os.environ` related functions.

::

    >>> isinstance(senf.getenv("HOME"), fsnative)
    True
    >>> isinstance(senf.expanduser("~"), fsnative)
    True


If you work with files a lot your unit tests will probably need temporary
files. Senf provides wrappers for `tempfile` functions which always return a
`fsnative`.

::

    >>> senf.mkdtemp()
    '/tmp/tmp26Daqo'
    >>> isinstance(_, senf.fsnative)
    True
