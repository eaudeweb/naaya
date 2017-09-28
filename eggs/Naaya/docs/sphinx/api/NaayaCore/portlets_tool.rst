.. _portlets-tool:

Portlets tool
=============

Portlet content is provided by `portlet objects`, and each of them has a unique
ID. These objects are either instantiated in ``portal_portlets`` (old-style
portlets), or obtained by adapting the current site to the ``INyPortlet``
interface, using the portlet id as name (adapter-based portlets).

Old-style portlets can be of two types:
    :class:`HTMLPortlet <Products.NaayaCore.PortletsTool.HTMLPortlet.HTMLPortlet>`
        A static piece of HTML, editable from the administration interface.
    :class:`Portlet <Products.NaayaCore.PortletsTool.Portlet.Portlet>`
        Also known as `Special portlet`. This is a subclass of
        ``PageTemplate``, and it's editable from the `ZMI`.

Adapter portlets are not stored inside the database; rather, they are
instantiated at runtime, as adapters of the `site` object to the
:class:`INyPortlet <Products.NaayaCore.PortletsTool.interfaces.INyPortlet>`
interface.  See :class:`naaya.core.portlets.MainSectionsPortlet` for an example
of writing adapter portlets.

Interfaces
----------

.. autointerface:: Products.NaayaCore.PortletsTool.interfaces.INyPortlet

Classes
-------

.. autoclass:: Products.NaayaCore.PortletsTool.PortletsTool.PortletsTool
   :members:
     getPortletById

.. autoclass:: Products.NaayaCore.PortletsTool.Portlet.Portlet

.. autoclass:: Products.NaayaCore.PortletsTool.HTMLPortlet.HTMLPortlet
