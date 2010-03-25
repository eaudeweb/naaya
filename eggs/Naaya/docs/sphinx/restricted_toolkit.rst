RestrictedToolkit
=================

RPython (RestrictedPython) is a subset of Python that can be used in scripts
and templates edited through-the-web, without compromising system security.
Most modules can't be imported, so you need to find workarounds to do various
simple things. The rationale of RestrictedPython is to provide some helper
functions that are available anywhere. Please take care when adding functions
since you are crossing a security layer.

.. autoclass:: naaya.core.zope2util.RestrictedToolkit
   :members:
