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
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor:
# Cornel Nitu, Finsiel Romania
#
# $Id: MyURLopener.py 864 2003-12-08 17:14:01Z finrocvs $
#

import urllib

class MyURLopener(urllib.FancyURLopener):

    http_error_default = urllib.URLopener.http_error_default

    def __init__(*args):
        self = args[0]
        apply(urllib.FancyURLopener.__init__, args)
        self.addheaders = [('User-agent', 'LinkChecker'),]

    def http_error_401(self, url, fp, errcode, errmsg, headers):
        return self.http_error_default(url, fp, errcode, errmsg, headers)