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
# The Initial Owner of the Original Code is EEA.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Eau de Web
# Cornel Nitu, Eau de Web
# Miruna Badescu, Eau de Web

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PythonScripts.PythonScript import PythonScript
from Products.PageTemplates.PageTemplateFile import PageTemplateFile


#Product related imports
from Products.Report.tools.constants import *

manage_addChartItemForm = PageTemplateFile('zpt/chartitem_add', globals())
def manage_addChartItem(self, id='', title='', description='', flash='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_SUFIX_CHARTITEM % self.utGenRandomId(6)
    ob = ChartItem(id, title, description, flash)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class ChartItem(PythonScript):
    """ """

    meta_type = METATYPE_CHARTITEM
    icon = 'misc_/Report/ChartItem.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
        )
        +
        (
            PythonScript.manage_options[0],
        )
        +
        PythonScript.manage_options[2:]
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, flash):
        """ """
        PythonScript.__dict__['__init__'](self, id)
        self.id = id
        self.title = title
        self.description = description
        self.flash = flash
        #xml attributes
        self.caption = ''
        self.sub_caption = ''
        self.yaxisname = ''
        self.xaxisname = ''
        self.canvasbgcolor = ''
        self.gridbgcolor = ''
        self.hovercapbg = ''
        self.hovercapborder = ''
        self.divlinecolor = 'F47E00'
        self.showActualValues = 1
        self.yaxisminvalue = 0
        self.yaxismaxvalue = ''
        self.showCanvas = 1
        self.showgridbg = 1
        self.legendboxbgcolor = ''
        self.legendboxbrdrcolor = ''
        self.numberSuffix=''
        self.decimalPrecision = 0

    def __setstate__(self,state):
        """Updates"""
        ChartItem.inheritedAttribute("__setstate__") (self, state)
        if not hasattr(self, 'decimalPrecision'):
            self.decimalPrecision = 0

#####################################################################################
# API #
#######

    security.declareProtected(view_management_screens, 'setFlash')
    def setFlash(self, value):
        """ Set flash type
        """
        self.flash = value
        self._p_changed= 1

    security.declareProtected(view, 'getFlash')
    def getFlash(self):
        return self.flash

    security.declareProtected(view_management_screens, 'setLegend')
    def setLegend(self, value):
        """ This attribute determines the caption of the graph that 
            would appear at the top of the graph. 
        """
        self.caption = value
        self._p_changed= 1

    security.declareProtected(view, 'getLegend')
    def getLegend(self):
        return self.caption

    security.declareProtected(view_management_screens, 'setSubLegend')
    def setSubLegend(self, value):
        """ This attribute determines the sub-caption of the graph that 
            would appear right below the caption of the graph. 
        """
        self.sub_caption = value
        self._p_changed= 1

    security.declareProtected(view, 'getSubLegend')
    def getSubLegend(self):
        return self.sub_caption

    security.declareProtected(view_management_screens, 'setYAxisName')
    def setYAxisName(self, value):
        """ This attribute determines the caption of the y-axis. """
        self.yaxisname = value
        self._p_changed= 1

    security.declareProtected(view, 'getYAxisName')
    def getYAxisName(self):
        return self.yaxisname

    security.declareProtected(view_management_screens, 'setXAxisName')
    def setXAxisName(self, value):
        """ This attribute determines the caption of the x-axis. """
        self.xaxisname = value
        self._p_changed= 1

    security.declareProtected(view, 'getXAxisName')
    def getXAxisName(self):
        return self.xaxisname

    def setCanvasBGColor(self, value):
        """ This attribute specifies the background color of the graph canvas. """
        self.canvasbgcolor = value
        self._p_changed = 1

    def getCanvasBGColor(self):
        return self.canvasbgcolor

    security.declareProtected(view_management_screens, 'setGridBGColor')
    def setGridBGColor(self, value):
        """ If you have opted to show the grid background, 
            then using this attribute you could specify the hex color code for the grid background.
        """
        self.gridbgcolor = value
        self._p_changed= 1

    security.declareProtected(view, 'getGridBGColor')
    def getGridBGColor(self):
        return self.gridbgcolor

    security.declareProtected(view_management_screens, 'setHoverCapBG')
    def setHoverCapBG(self, value):
        """ If you have the showhovercap attribute containing the value 1, 
            you could use this attribute to specify the background color of the hover box.
        """
        self.hovercapbg = value
        self._p_changed= 1

    security.declareProtected(view, 'getHoverCapBG')
    def getHoverCapBG(self):
        return self.hovercapbg

    security.declareProtected(view_management_screens, 'setHoverCapBorder')
    def setHoverCapBorder(self, value):
        """ If you have the showhovercap attribute containing the value 1, 
            you could use this attribute to specify the border color of the hover box.
        """
        self.hovercapborder = value
        self._p_changed= 1

    security.declareProtected(view, 'getHoverCapBorder')
    def getHoverCapBorder(self):
        return self.hovercapborder

    security.declareProtected(view_management_screens, 'setDivLineColor')
    def setDivLineColor(self, value):
        """ If you have opted to show any divisional grid lines on the graph canvas, 
            then using this attribute you can specify the hex color code for all such lines. 
        """
        self.divlinecolor = value
        self._p_changed= 1

    security.declareProtected(view, 'getDivLineColor')
    def getDivLineColor(self):
        return self.divlinecolor

    security.declareProtected(view_management_screens, 'setShowActualValues')
    def setShowActualValues(self, value):
        """ Sets the configuration whether to display the percentage values on the pie/doughnut chart or whether to display the actual values. 
            By default, this has a value of 0 - i.e., the percentage values are displayed on the chart.
        """
        self.showActualValues = value
        self._p_changed= 1

    security.declareProtected(view, 'getShowActualValues')
    def getShowActualValues(self):
        return self.showActualValues

    security.declareProtected(view_management_screens, 'setYAxisMinValue')
    def setYAxisMinValue(self, value):
        """ This attribute determines the lower limit of y-axis. If you don't specify this value,
            it is automatically calculated based on the data provided by you.
        """
        self.yaxisminvalue = value
        self._p_changed = 1

    security.declareProtected(view, 'getYAxisMinValue')
    def getYAxisMinValue(self):
        return self.yaxisminvalue

    security.declareProtected(view_management_screens, 'setYAxisMaxValue')
    def setYAxisMaxValue(self, value):
        """ This attribute determines the upper limit of y-axis. If you don't specify this value, 
            it is automatically calculated based on the data provided by you.
        """
        self.yaxismaxvalue = value
        self._p_changed = 1

    security.declareProtected(view, 'getYAxisMaxValue')
    def getYAxisMaxValue(self):
        return self.yaxismaxvalue

    security.declareProtected(view_management_screens, 'setShowCanvas')
    def setShowCanvas(self, value):
        """ This attribute can have either of the two possible values: 1,0. 
            It sets the configuration whether the canvas would be displayed or not. 
        """
        self.showCanvas = value
        self._p_changed = 1

    security.declareProtected(view, 'getShowCanvas')
    def getShowCanvas(self):
        return self.showCanvas

    security.declareProtected(view_management_screens, 'setShowGridBG')
    def setShowGridBG(self, value):
        """ This attribute can have either of the two possible values: 1,0. 
            It sets the configuration whether the background of the grid will be shown or not.
        """
        self.showgridbg = value
        self._p_changed = 1

    security.declareProtected(view, 'getShowGridBG')
    def getShowGridBG(self):
        return self.showgridbg

    security.declareProtected(view_management_screens, 'setLegendBoxBGColor')
    def setLegendBoxBGColor(self, value):
        """ In case of pie chart/doughnut, this attribute lets you set the 
            background color of the legend box. 
        """
        self.legendboxbgcolor = value
        self._p_changed = 1

    security.declareProtected(view, 'getLegendBoxBGColor')
    def getLegendBoxBGColor(self):
        return self.legendboxbgcolor

    security.declareProtected(view_management_screens, 'setLegendBoxBrdColor')
    def setLegendBoxBrdColor(self, value):
        """ In case of pie chart/doughnut, this attribute lets you set the border color of the legend box. """
        self.legendboxbrdrcolor = value
        self._p_changed = 1

    security.declareProtected(view, 'getLegendBoxBrdColor')
    def getLegendBoxBrdColor(self):
        return self.legendboxbrdrcolor

    security.declareProtected(view_management_screens, 'setNumberSuffix')
    def setNumberSuffix(self, value):
        """ Using this attribute, you could add prefix to all the numbers visible on the graph. For example, to represent all figure 
            quantified as per annum on the chart, you could specify this attribute to ' /a' to show like 40000/a, 50000/a. """
        self.numberSuffix = value
        self._p_changed = 1

    security.declareProtected(view, 'getNumberSuffix')
    def getNumberSuffix(self):
        return self.numberSuffix

    security.declareProtected(view_management_screens, 'setDecimalPrecision')
    def setDecimalPrecision(self, value):
        """ set the number of places of decimals for all the numbers on the chart """
        self.decimalPrecision = value
        self._p_changed = 1

    security.declareProtected(view, 'getDecimalPrecision')
    def getDecimalPrecision(self):
        return self.decimalPrecision


#####################################################################################
# Charts render methods #
#########################

    security.declareProtected(view, 'showChart')
    def showChart(self, values=[], footnote=''):
        """ render the Flash """
        output = []
        out_a = output.append   #optimisation
        out_a('<OBJECT classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0" WIDTH="565" HEIGHT="420" id="%s" ALIGN="">' % self.id)
        out_a('<PARAM NAME=movie VALUE="%s/misc_/Report/%s.swf">' % (self.getSitePath(), self.flash))
        out_a('<PARAM NAME="FlashVars" value="&dataXML=%s">' % self.renderXML(values))
        out_a('<PARAM NAME=quality VALUE=high>')
        out_a('<PARAM NAME=bgcolor VALUE=#FFFFFF>')
        out_a('<EMBED src="%s/misc_/Report/%s.swf" FlashVars="&dataXML=%s" quality=high bgcolor=#FFFFFF WIDTH="565" HEIGHT="420" NAME="%s" ALIGN="" TYPE="application/x-shockwave-flash" PLUGINSPAGE="http://www.macromedia.com/go/getflashplayer"></EMBED>' % (self.getSitePath(), self.flash, self.renderXML(values), self.id))
        out_a('</OBJECT>')
        if footnote:
            out_a('<p>%s</p>' % footnote)
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/html')
        return '\n'.join(output)

    security.declareProtected(view, 'renderXML')
    def renderXML(self, values=[]):
        """ render the XML file """
        out = []
        out.append(self.render_xml_header())
        out.append(self.render_xml_body(values))
        out.append(self.render_xml_footer())
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
        return ''.join(out)

    security.declarePrivate('render_xml_header')
    def render_xml_header(self):
        """ render XML header """
        return """<graph bgcolor='%s' caption='%s' subCaption='%s' yaxisname='%s' xaxisname='%s' canvasbgcolor='%s' gridbgcolor='%s' 
            hovercapbg='%s' hovercapborder='%s' divlinecolor='%s' showActualValues='%s' yaxisminvalue='%s' yaxismaxvalue='%s' showCanvas='%s'
            showgridbg='%s' legendboxbgcolor='%s' legendboxbrdrcolor='%s' numberSuffix='%s' decimalPrecision='%s'> """ \
            % (self.getGridBGColor(), self.getLegend(), self.getSubLegend(), self.getYAxisName(), self.getXAxisName(), self.getCanvasBGColor(), \
               self.getGridBGColor(), self.getHoverCapBG(), self.getHoverCapBorder(), self.getDivLineColor(), self.getShowActualValues(), \
               self.getYAxisMinValue(), self.getYAxisMaxValue(), self.getShowCanvas(), self.getShowGridBG(), self.getLegendBoxBGColor(), \
               self.getLegendBoxBrdColor(), self.getNumberSuffix(), self.getDecimalPrecision())

    security.declarePrivate('render_xml_body')
    def render_xml_body(self, values):
        """ create xml elements from a list of values where 
            values is a list of dictioaries [{'name':, 'value':},...]
        """
        output = [] #output XML
        out_a = output.append   #optimisation
        stat_tool = self.getStatisticsTool()
        count = 0
        for val in values:
            elem = []
            elem.append("<set")
            for k,v in val.items():
                elem.append("%s='%s'" % (k,v))
            elem.append("color='%s'" % stat_tool.colors[count])
            elem.append("/>")
            out_a(" ".join(elem))
            count += 1
        return "\n".join(output)

    security.declarePrivate('render_xml_footer')
    def render_xml_footer(self):
        """ render XML footer """
        return "</graph>"

    def getData(self, *args):
        """ """
        return self._exec({'context': self, 'container': self}, args, {})

#####################################################################################
# ZMI actions #
###############

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', flash='', caption='', sub_caption='', xaxisname='', yaxisname='', canvasbgcolor='',
            gridbgcolor='', hovercapbg='', hovercapborder='', divlinecolor='', showActualValues='', showCanvas='', 
            showgridbg='', legendboxbgcolor='', legendboxbrdrcolor='', numberSuffix='', decimalPrecision='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self.flash = flash
        self.caption = caption
        self.sub_caption = sub_caption
        self.xaxisname = xaxisname
        self.yaxisname = yaxisname
        self.canvasbgcolor = canvasbgcolor
        self.gridbgcolor = gridbgcolor
        self.hovercapbg = hovercapbg
        self.hovercapborder = hovercapborder
        self.divlinecolor = divlinecolor
        self.showActualValues = showActualValues
        self.showCanvas = showCanvas
        self.showgridbg = showgridbg
        self.legendboxbgcolor = legendboxbgcolor
        self.legendboxbrdrcolor = legendboxbrdrcolor
        self.numberSuffix = numberSuffix
        self.decimalPrecision = decimalPrecision
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

#####################################################################################
# ZMI pages #
#############

    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/chartitem_properties', globals())

InitializeClass(ChartItem)