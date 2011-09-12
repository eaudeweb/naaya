Introduction
============

Display a map with a search interface that queries the AoA Virtual Library.


Translation
-----------

To update the message catalog::

  cd eea/aoamap
  i18ndude rebuild-pot --pot locales/eea-aoamap.pot --create eea-aoamap ./browser

To create a new translation::

  msgen locales/eea-aoamap.pot > locales/ru/LC_MESSAGES/eea-aoamap.po

To update an existing translation::

  msgmerge locales/ru/LC_MESSAGES/eea-aoamap.po locales/eea-aoamap.pot > locales/ru/LC_MESSAGES/eea-aoamap.po.new
  mv locales/ru/LC_MESSAGES/eea-aoamap.po.new locales/ru/LC_MESSAGES/eea-aoamap.po

To compile a translation into an MO file::

  msgfmt -o locales/ru/LC_MESSAGES/eea-aoamap.mo locales/ru/LC_MESSAGES/eea-aoamap.po

Deployment
----------

A few things to remember when deploying the AoA map to production:

* Plone site - configure the map tile source
* Plone site - configure prefix of AoA portal
* AoA portal - configure and test cache invalidation URL(s)
