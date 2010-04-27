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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania

import os, popen2
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG, WARNING
from converters import xslt

converter = xslt.Converter()
depends_on = getattr(converter, 'depends_on', None)
description = converter.getDescription()

if depends_on and os.name == 'posix':
    PO =  popen2.Popen3('which %s' % depends_on)
    out = PO.fromchild.read()
    PO.wait()
    del PO
    if out.find('no %s' % depends_on) > - 1 or out.lower().find('not found') > -1 or len(out.strip()) == 0:
        LOG('SEMIDE', WARNING, 'Converter "%s" not registered because executable "%s" could not be found' % (description, depends_on))
    else:
        LOG('SEMIDE', INFO, 'Converter "%s" registered' % description)

if depends_on and os.name == 'nt':
    out = os.popen('%s' % depends_on, 'r').read()
    if out =='' or len(out.strip()) == 0:
        LOG('SEMIDE', WARNING, 'Converter "%s" not registered because executable "%s" could not be found' % (description, depends_on))
    else:
        LOG('SEMIDE', INFO, 'Converter "%s" registered' % description)