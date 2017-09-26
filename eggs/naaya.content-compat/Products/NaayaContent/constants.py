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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Dragos Chirila

#Python imports

#Zope imports
import Globals
from naaya.content.base.constants import (
    NAAYACONTENT_PRODUCT_NAME,
    DEFAULT_SORTORDER,
    MUST_BE_NONEMPTY,
    MUST_BE_DATETIME,
    MUST_BE_DATETIME_STRICT,
    MUST_BE_POSITIV_INT,
    MUST_BE_POSITIV_FLOAT,
    MUST_BE_CAPTCHA,
)

import warnings
from naaya.content.base import constants as newlocation
warnings.warn(
    '%s is deprecated. Use %s instead'  % (__name__, newlocation.__name__),
    DeprecationWarning, stacklevel=2)
