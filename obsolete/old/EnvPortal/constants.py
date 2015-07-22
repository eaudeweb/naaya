# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
# Adriana Baciu, Finsiel Romania

#Python imports
from os.path import join

#Zope imports

#Product imports
import Globals

ENVPORTAL_PRODUCT_NAME = 'EnvPortal'
ENVPORTAL_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADD_ENVPORTAL = 'EnvPortal - Add Environmental Portal objects'

METATYPE_ENVPORTAL = 'EnvPortal'

ID_LINKCHECKER = 'LinkChecker'
TITLE_LINKCHECKER = 'URL checker'

ID_HELPDESKAGENT = 'HelpDesk'
TITLE_HELPDESKAGENT = 'Helpdesk'

ID_PHOTOARCHIVE = 'PhotoArchive'
TITLE_PHOTOARCHIVE = 'Photo archive'

ID_GLOSSARY_KEYWORDS = 'glossary_keywords'
TITLE_GLOSSARY_KEYWORDS = 'Keywords glossary'
ID_GLOSSARY_COVERAGE = 'glossary_coverage'
TITLE_GLOSSARY_COVERAGE = 'Coverage glossary'
