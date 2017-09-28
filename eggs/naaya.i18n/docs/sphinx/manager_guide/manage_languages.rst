Managing available languages
============================

By default, a Naaya site is available only in English. You can view the
available languages in Zope Management Interface by accessing
*Languages* tab in the corresponding *portal_i18n* of your Naaya site item.

Adding a new language
---------------------

You can select a language from an existing ISO 386 list. This will only
prefill the *add a language*-form, you can still edit the code or the name
of the new language.

Selecting the default language
------------------------------
The *default language* is the language the portal is first displayed in,
when the user either has no localization preferences set or the default
language is within his preferred languages. This is also the default fallback
language.

This setting does not influence the default translation for new found strings.
Each new found message without translation is still considered in English,
since most of the Naaya and Zope products are edited so.

Languages display order
-----------------------
The default order is creation order, except for the default language which
is always first in list.
You can rearrange them anyhow you like using the arrows next to
them in the same page you used to add, remove or set default language.
