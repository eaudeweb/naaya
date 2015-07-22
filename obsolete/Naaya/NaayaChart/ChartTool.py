# Python imports
from os.path import dirname, join
import urllib

# Zope imports
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Product imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
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
    """Tool for generating charts

        Usage example (ZPT):
        <span tal:replace="structure python: here.portal_chart.render(here.chart_data.absolute_url())">
            CHART
        </span>
    """

    meta_type = 'Naaya Chart Tool'
    portal_id = 'portal_chart'
    security = ClassSecurityInfo()

    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w', 'label': 'Title'},
    )

    manage_options = (
        {'label':'Contents', 'action':'manage_main'},
        {'label': 'View', 'action': 'index_html'},
    )

    xmlswfchart = PageTemplateFile('zpt/xmlswfchart.zpt', globals())

    def __init__(self, id, **kw):
        Folder.__init__(self, id)
        self.manage_changeProperties(**kw)

    security.declarePrivate('loadXmlSwfChartsFiles')
    def loadXmlSwfChartsFiles(self):
        """Load the XML/SWF Charts files"""
        self.manage_addProduct['LocalFS'].manage_addLocalFS('XmlSwfCharts', '', join(dirname(__file__), 'XmlSwfCharts'))

    security.declarePublic('render')
    def render(self, data_url, width=400, height=250):
        """Render chart using the data from data_url.

            @param data_url: URL of the XML data source
            @param width: width of the chart
            @param height: height of the chart
        """
        charts_url = '%s/charts.swf?%s' % \
                        (self.XmlSwfCharts.absolute_url(),
                         urllib.urlencode({'library_path': self.XmlSwfCharts.absolute_url() + '/' + 'charts_library',
                                           'xml_source': data_url}))
        return self.xmlswfchart(charts_url=charts_url, width=width, height=height)

InitializeClass(ChartTool)
