General-Purpose utility functions
=================================

The :class:`utils <Products.NaayaCore.managers.utils>` module contains
several general-purpose utility functions. Some are called by methods of the
utils class described below. Note that the deprecated functions regarding
generation of slugified unique ids in a given context (folder) are no longer
documented.

Generating a slugified unique id for object
-------------------------------------------

You can now generate a slugified text like this:

   >>> s = slugify(string)

And a unique available id in a "self" context:

   >>> id = uniqueId(string, lambda x: return self._getOb(x, None) is not None)`

where string is already slugified in the above example.

Also see the :func:`make_id` function which combines both functionalities,
but lacks the functionality of defining your own ``id existence test`` function.

The :class:`utils <Products.NaayaCore.managers.utils.utils>` class contains a
few more general-purpose utility functions. They are accessible in ``rstk`` via
acquisition, and will be migrated there eventually.


.. automodule:: Products.NaayaCore.managers.utils
   :members: slugify, uniqueId, make_id

.. autoclass:: Products.NaayaCore.managers.utils.utils
   :members: html2text, splitTextByWords, word_break, getObjectPaginator,
             parse_tags, utGetROOT, utGetObject
