Custom scripts and templates
============================

This folder contains scripts and page templates that need to be created
by hand when deploying a new Groupware site. This is because they need
to live outside of any Groupware (Naaya) portal.

``get_gw_root.py``, ``dropdowns.txt.py``, ``getBreadCrumbTrail.py``
    Create top-level objects of type `Script (Python)` named the same
    as the files (without the ``.py`` extension).
    ``getBreadCrumbTrail`` needs ``request`` parameter in parameter
    list.

``gw_macro.zpt``, ``sitemapindex_xml.zpt``, ``standard_template.pt.zpt``
    Create top-level `Page Template` objects named the same as the
    files (without the ``.zpt`` extension). The ``sitemapindex_xml``
    template should have its Content-Type set to ``text/xml``.

``cookie_crumbler``
    After creating a top-level `CookieCrumbler` instance, replace its
    `DTML` templates with the scripts and templates provided in this
    folder.

``applications``
    Create a `GW Applications` object with id ``applications``. The
    "mail from" field configures the address that emails will originate
    from, and the "admin mail" field configures who will be notified of
    application submissions.

Zope site customisations
========================
     * define a Zope root string property with the id 'root_site_title'
     * add ``naaya.groupware.interfaces.IGroupwareApplication``
       interface in Interfaces tab of Zope root
     * ``help`` is now an entire folder
     * don't forget of ``login`` object in Zope root


TODO
====

Register all templates from this folder as browser views. Python scripts as
views or utilities. And create a bootstrap script that adds GW Applications.
This would be more maintainable and can be used in test environments.
