1.0.8 (unreleased)
------------------
* strips and collapses whitespaces in message translations [simiamih]

1.0.7 (2011-11-08)
------------------
* bufix: setting default lang or del. languages when custom order is
  specified #739 [simiamih]

1.0.6 (2011-11-03)
------------------
* feature: fallback for translation utility - identity translation when
  not in INySite portal context [simiamih]

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
