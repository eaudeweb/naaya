Introduction
============

Display a map with a search interface that queries the AoA Virtual Library.


Translation
-----------

To update the message catalog::

  cd eea/aoamap
  i18ndude rebuild-pot --pot locales/eea-aoamap.pot --create eea-aoamap ./browser

To create a new translation::

  msgen locales/eea-aoamap.pot > locales/en/LC_MESSAGES/eea-aoamap.po

To compile a translation into an MO file::

  msgfmt -o locales/en/LC_MESSAGES/eea-aoamap.mo locales/en/LC_MESSAGES/eea-aoamap.po
