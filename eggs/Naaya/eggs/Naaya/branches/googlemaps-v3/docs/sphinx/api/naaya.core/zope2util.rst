Zope 2 utilities
================

.. currentmodule:: naaya.core.zope2util

.. _restricted-toolkit:

Restricted Toolkit
------------------

RPython (RestrictedPython) is a subset of Python that can be used in scripts
and templates edited through-the-web, without compromising system security.
Most modules can't be imported, so you need to find workarounds to do various
simple things. The rationale of the :class:`RestrictedToolkit` is to provide
some helper functions that are available anywhere. Please take care when adding
functions since you are crossing a security layer.

Example usage, from a Python Script in ZODB::

    >>> str_date = "Wed, 24 Mar 2010 14:42:00 +0100"
    >>> rstk = context.rstk # pulled from NySite by acquisition
    >>> print repr(rstk.parse_string_to_datetime(str_date))
    >>> return printed

This should output::

    datetime.datetime(2010, 3, 24, 14, 42, tzinfo=tzoffset(None, 3600))


:mod:`naaya.core.zope2util` module
----------------------------------

.. automodule:: naaya.core.zope2util
    :members:
