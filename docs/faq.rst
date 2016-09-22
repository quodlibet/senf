Frequently Asked Questions
==========================

.. currentmodule:: senf

Are there any existing users of Senf?
    It is currently used in `Quod Libet <https://quodlibet.readthedocs.io>`__
    and `mutagen <https://mutagen.readthedocs.io>`__.

Why not use bytes for paths on Python 3 + Unix?
    Downsides of using str: str can not be pickled as it depends on the locale
    encoding. You have to use something like `fsn2bytes` first, or you have to
    make sure that the encoding doesn't change across program invocations.

    Upsides of using str: str has more support in the stdlib (pathlib for
    example) and it can be used in combination with the string literal
    ``"foo"``. The later makes ``some_fsnative + "foo"`` work for all Python
    versions and platforms as long as it contains ASCII only.

Why the weird "foo2bar" function naming?
    As the real types depend on the platform anything like "decode"/"encode"
    is confusing. So you end up with "a_to_b" or "a_from_b". And imo having
    things always go one direction, being fast to parse visually and not being
    too long makes this a good choice. But ymmv.

How can it be that `fsnative()` can't fail, even with an ASCII encoding?
    It falls back to utf-8 if encoding fails. Raising there would make
    everything complicated and there is no good way to handle that error case
    anyway.

Why not replace ``sys.stdout`` instead of providing a new :func:`print`?
    No monkey patching. Allows us to do our own error handling so print will
    never fail. Printing some question marks is better than a stack trace
    if the target is a user.
