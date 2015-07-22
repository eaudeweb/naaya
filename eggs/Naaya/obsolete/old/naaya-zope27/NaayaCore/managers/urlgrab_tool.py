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
#
#
#$Id: urlgrab_tool.py 1249 2004-03-24 14:13:42Z finrocvs $

#Python imports
import urllib

#Zope imports

#Product imports

class urlgrab_tool(urllib.FancyURLopener):
    """ Create sub-class in order to overide error 206.  This error means a
       partial file is being sent, which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass

    def http_error_404(self, url, fp, errcode, errmsg, headers, data=None):
        pass
