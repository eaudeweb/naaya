"""A `safe' dictionary for string interpolation."""
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
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Cornel Nitu - Finsiel Romania


from types import StringType
from UserDict import UserDict

COMMASPACE = ', '


class SafeDict(UserDict):
    """Dictionary which returns a default value for unknown keys.

    This is used in maketext so that editing templates is a bit more robust.
    """
    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            if isinstance(key, StringType):
                return '%('+key+')s'
            else:
                return '<Missing key: %s>' % `key`

    def interpolate(self, template):
        return template % self


class MsgSafeDict(SafeDict):
    def __init__(self, msg, dict=None):
        self.__msg = msg
        SafeDict.__init__(self, dict)

    def __getitem__(self, key):
        if key.startswith('msg_'):
            return self.__msg.get(key[4:], 'n/a')
        elif key.startswith('allmsg_'):
            missing = []
            all = self.__msg.get_all(key[7:], missing)
            if all is missing:
                return 'n/a'
            return COMMASPACE.join(all)
        else:
            return SafeDict.__getitem__(self, key)

    def copy(self):
        d = self.data.copy()
        for k in self.__msg.keys():
            vals = self.__msg.get_all(k)
            if len(vals) == 1:
                d['msg_'+k.lower()] = vals[0]
            else:
                d['allmsg_'+k.lower()] = COMMASPACE.join(vals)
        return d