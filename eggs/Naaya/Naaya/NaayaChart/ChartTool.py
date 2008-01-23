# Python imports
from os.path import dirname, join

# Zope imports
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Product imports
from Products.LocalFS.LocalFS import manage_addLocalFS



def manage_addChartTool(context, REQUEST=None):
    """ """
    ob = ChartTool(ChartTool.portal_id, title="Portal Chart Tool")
    context._setObject(ChartTool.portal_id, ob)
    ob = context._getOb(ChartTool.portal_id)
    ob.loadXmlSwfChartsFiles()
    if REQUEST:
        return context.manage_main(context, REQUEST, update_menu=1)
    return ChartTool.portal_id


class ChartTool(Folder):
    """Tool for generating charts"""

    meta_type = 'Naaya Chart Tool'
    portal_id = 'portal_chart'
    security = ClassSecurityInfo()

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
    )

    manage_options = (
        {'label': 'View', 'action': 'index_html'},
    )

    def __init__(self, id, **kw):
        Folder.__init__(self, id)
        self.manage_changeProperties(**kw)

    security.declarePrivate('loadXmlSwfChartsFiles')
    def loadXmlSwfChartsFiles(self):
        """Load the XML/SWF Charts files"""
        self.manage_addProduct['LocalFS'].manage_addLocalFS('XmlSwfCharts', '', join(dirname(__file__), 'XmlSwfCharts'))

InitializeClass(ChartTool)
