1.0.6 (unreleased)
------------------

1.0.5 (2011-10-20)
------------------
* bugfix: fallback lang on localprops when lang is specified
  in params [simiamih]

1.0.4 (2011-10-19)
------------------
* feature: return en translation when default lang in site is not en,
  but object has translation only for en [simiamih]

1.0.3 (2011-10-13)
------------------
* feature: languages display order is customizable [simiamih]

1.0.2 (2011-10-10)
------------------
* update script for cleaning empty translations on local
  props

1.0.1 (2011-10-07)
------------------
* _p_changed = 1 for deleting contenttype property on site

1.0 (2011-10-06)
----------------
* Fully functional version - now translating templates, messages, local
  properties and linked with Naaya administration
* includes migration script from :mod:`Products.Localizer`

0.1.2 (2011-06-14)
-------------------
* Renamed get_catalog to get_message_catalog

0.1 (2011-06-10)
-------------------
* First numbered version
* TODO: test local properties, importing language files (po, tmx, xliff)
* TODO: several fixes and update script from old localizer
