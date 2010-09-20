RestrictedToolkit
=================

RPython (RestrictedPython) is a subset of Python that can be used in scripts
and templates edited through-the-web, without compromising system security.
Most modules can't be imported, so you need to find workarounds to do various
simple things. The rationale of RestrictedPython is to provide some helper
functions that are available anywhere. Please take care when adding functions
since you are crossing a security layer.

Example usage, from a Python Script in ZODB::

    >>> str_date = "Wed, 24 Mar 2010 14:42:00 +0100"
    >>> rstk = context.rstk # pulled from NySite by acquisition
    >>> print repr(rstk.parse_string_to_datetime(str_date))
    >>> return printed

This should output::

    datetime.datetime(2010, 3, 24, 14, 42, tzinfo=tzoffset(None, 3600))


.. autoclass:: naaya.core.zope2util.RestrictedToolkit
   :members:

General-Purpose utility functions
=================================

The :class:`utils <Products.NaayaCore.managers.utils>` module contains
several general-purpose utility functions. Some are called by methods of the
utils class described below. Note that the depracted functions regarding
generation of slugified unique ids in a given context (folder) are no longer
documented.

Generating a slugified unique id for object
-------------------------------------------

You can now generate a slugified text like this:

   >>> s = slugify(string)

And a unique available id in a "self" context:

   >>> id = uniqueId(string, lambda x: return self._getOb(x, None) is not None)

where string is already slugified in the latter example.

Also see the make_id function which combines both functionalities but,
however, lacks the functionality of defining your own "id existence test"
function.

The :class:`utils <Products.NaayaCore.managers.utils.utils>` class contains a
few more general-purpose utility functions. They are accessible in ``rstk`` via
acquisition, and will be migrated there eventually.


.. automodule:: Products.NaayaCore.managers.utils
   :members: is_valid_email, slugify, uniqueId, make_id

.. autoclass:: Products.NaayaCore.managers.utils.utils
   :members: html2text, splitTextByWords, word_break, getObjectPaginator,
             parse_tags, utGetROOT, utGetObject
