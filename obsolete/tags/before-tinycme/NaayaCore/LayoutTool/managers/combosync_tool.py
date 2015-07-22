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

#Python imports

#Zope imports

#Product imports

class combosync_tool:
    """ """

    def __init__(self):
        """ """
        pass

    def getMasterCombo(self, p_name='theMasterList'):
        """ """
        l_mastercombo = '<select onchange="OnChangeTopic()" name="%s" style="width: 150px;">' % p_name
        for i in range(0,20):
            l_mastercombo += '<option value="">&nbsp;</option>'
        l_mastercombo += '</select>'
        return l_mastercombo

    def getSlaveCombo(self, p_name='theSlaveList'):
        """ """
        l_mastercombo = '<select onchange="OnChangeScheme()" name="%s" style="width: 150px;">' % p_name
        for i in range(0,20):
            l_mastercombo += '<option value="">&nbsp;</option>'
        l_mastercombo += '</select>'
        return l_mastercombo

    def getSyncroObject(self, p_data):
        """ """
        l_master_default, l_slave_default, l_data = p_data
        l_master_index = l_slave_index = 0
        l_master_found = 0
        l_syncroobject = '<script type="text/javascript">\n'
        l_syncroobject += '<!--\n\n'
        l_syncroobject += 'var theLayoutToolPath = "%s";\n\n' % self.getLayoutToolPath();
        l_syncroobject += 'var SyncroObject = new SyncroView();\n\n'
        i = j = 0
        for item in l_data:
            if item[0]==l_master_default:
                l_master_index = i
                l_master_found = 1
            l_syncroobject += 'var SyncroSkin%s = new SyncroTopic(\'%s\', \'%s\');\n' % (i, item[0], item[1])
            j = 0
            for pair in item[2]:
                if pair[1]==l_slave_default and l_master_found:
                    l_slave_index = j
                    l_master_found = 0
                l_syncroobject += 'SyncroSkin%s.AddURL(new URLPair(\'%s\',\'%s\'));\n' % (i, pair[0], pair[1])
                j += 1
            l_syncroobject += 'SyncroObject.AddTopic(SyncroSkin%s);\n\n' % i
            i += 1
        l_syncroobject += 'var theMasterIndex = %s;\n' % l_master_index
        l_syncroobject += 'var theSlaveIndex = %s;\n' % l_slave_index
        l_syncroobject += '//-->\n'
        l_syncroobject += '</script>\n'
        return l_syncroobject
