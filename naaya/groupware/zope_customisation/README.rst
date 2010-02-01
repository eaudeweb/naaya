Custom scripts and templates
============================

This folder contains scripts and page templates that need to be created
by hand when deploying a new Groupware site. This is because they need
to live outside of any Groupware (Naaya) portal.

``get_gw_root.py``, ``groupedIGs.py``
    Create top-level objects of type `Script (Python)` named the same
    as the files (without the ``.py`` extension).

``gw_macro.zpt``, ``sitemapindex_xml.zpt``
    Create top-level `Page Template` objects named the same as the
    files (without the ``.zpt`` extension). The ``sitemapindex_xml``
    template should have its Content-Type set to ``text/xml``.

``index.html``
    Create a top-level `Page Template` named ``index.html``.

``cookie_crumbler``
    After creating a top-level `CookieCrumbler` instance, replace its
    `DTML` templates with the scripts and templates provided in this
    folder.
