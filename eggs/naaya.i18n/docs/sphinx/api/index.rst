API Documentation
=================

Portal i18n
-----------

**Portal i18n** is the main object used for internationalization operations, used
for querying the other submodules or getting their address. Most
of the public API available for restricted access resides here.

.. toctree::
    :maxdepth: 2
    :glob:

    portal_tool


Message Catalog
---------------

The **Message Catalog** is the main storage for translations. Its API is defined
by *interfaces.INyCatalog* interface.

.. toctree::
    :maxdepth: 2
    :glob:

    message_catalog/*


Negotiator
---------------

The **Negotiator** is responsible for selecting a display language for the
browser. It has some configuration settings which can be tweaked by programmers.

.. toctree::
    :maxdepth: 2
    :glob:

    negotiator/*


Property Manager
----------------

The **Property Manager** takes care of properly setting and returning localized
values for objects in database.

.. toctree::
    :maxdepth: 2
    :glob:

    property_manager/*


Import Export Tool
------------------

The **Import Export Tool** provides input-output action
for **Message Catalog** data.

.. toctree::
    :maxdepth: 2
    :glob:

    import_export/*
