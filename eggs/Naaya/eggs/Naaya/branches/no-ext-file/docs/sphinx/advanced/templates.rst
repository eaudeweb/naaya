Page templates
==============


The standard template
---------------------
Each portal layout has one or more `standard template` macros which render the
header, footer and portlets. They are included using the
:meth:`~Products.Naaya.NySite.NySite.standard_template_macro` function::

    <metal:block use-macro="python:here.standard_template_macro()">
        <metal:block fill-slot="body">
            <p>Body content goes here</p>
        </metal:block>
    </metal:block>


A number of slots are provided by all standard templates:

`head`
    Part of the ``<head>`` HTML tag. Use this to include custom meta
    tags or stylesheets.

`body`
    Slot for the main content of the page, surrounded by the header,
    footer, and portlets.


Internationalization
--------------------
Most messages included in templates should be translatable. For this, we use
the `i18n` tags from :term:`TAL`. For a detailed description see
`Internationalization For Developers`_ from the Plone documentation. In brief:

``i18n:translate``
    Translate the tag's inner text::

        <a href="/" i18n:translate="">Home</a>

``i18n:attributes``
    Translate the specified attributes of the tag. Names must be separated with
    a semicolon::

        <a href="/" alt="home" title="home" i18n:attributes="alt; title">Home</a>

``i18n:name``
    Within a parent tag with ``i18n:translate``, the current tag will be marked
    as a translation variable. The following markup::

        <p i18n:translate="">Click to go <a i18n:name="link-home" href="/">home</a>.</p>

    Results in the following translation string::

        Click to go ${link-home}.

    ``i18n:translate`` and ``i18n:name`` can be combined to generate two
    translation strings::

        <p i18n:translate="">
            Click to go
            <a i18n:name="link-home" href="/" i18n:translate="">home</a>.
        </p>

.. _`Internationalization For Developers`: http://plone.org/documentation/kb/i18n-for-developers

.. TODO say that translated messages go into the portal's translations catalogue


Verifying translated templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To check what messages are generated from the i18n markup, you can use a static
tool, `i18ndude`_::

    touch translations.pot
    i18ndude rebuild-pot --pot translations.pot --create default path/to/src/Naaya

.. _`i18ndude`: http://pypi.python.org/pypi/i18ndude

This will generate a ``translations.pot`` file with all translation strings
found in the ``Naaya`` package.
