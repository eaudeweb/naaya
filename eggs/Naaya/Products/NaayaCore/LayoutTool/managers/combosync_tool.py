


class combosync_tool:
    """ """

    def __init__(self):
        """ """
        pass

    def getMainCombo(self, p_name='theMainList'):
        """ """
        l_maincombo = '<select onchange="OnChangeTopic()" name="%s">' % p_name
        for i in range(0,20):
            l_maincombo += '<option value="">&nbsp;</option>'
        l_maincombo += '</select>'
        return l_maincombo

    def getSubordinateCombo(self, p_name='theSubordinateList'):
        """ """
        l_maincombo = '<select onchange="OnChangeScheme()" name="%s">' % p_name
        for i in range(0,20):
            l_maincombo += '<option value="">&nbsp;</option>'
        l_maincombo += '</select>'
        return l_maincombo

    def getSyncroObject(self, p_data):
        """ """
        l_main_default, l_subordinate_default, l_data = p_data
        l_main_index = l_subordinate_index = 0
        l_main_found = 0
        l_syncroobject = '<script type="text/javascript">\n'
        l_syncroobject += '<!--\n\n'
        l_syncroobject += 'var theLayoutToolPath = "%s";\n\n' % self.getLayoutToolPath();
        l_syncroobject += 'var SyncroObject = new SyncroView();\n\n'
        i = j = 0
        for item in l_data:
            if item[0]==l_main_default:
                l_main_index = i
                l_main_found = 1
            l_syncroobject += 'var SyncroSkin%s = new SyncroTopic(\'%s\', \'%s\');\n' % (i, item[0], item[1])
            j = 0
            for pair in item[2]:
                if pair[1]==l_subordinate_default and l_main_found:
                    l_subordinate_index = j
                    l_main_found = 0
                l_syncroobject += 'SyncroSkin%s.AddURL(new URLPair(\'%s\',\'%s\'));\n' % (i, pair[0], pair[1])
                j += 1
            l_syncroobject += 'SyncroObject.AddTopic(SyncroSkin%s);\n\n' % i
            i += 1
        l_syncroobject += 'var theMainIndex = %s;\n' % l_main_index
        l_syncroobject += 'var theSubordinateIndex = %s;\n' % l_subordinate_index
        l_syncroobject += '//-->\n'
        l_syncroobject += '</script>\n'
        return l_syncroobject
