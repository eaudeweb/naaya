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

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplateForm, manage_addPageTemplate

#Product imports
from Products.NaayaBase.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.Report.tools.constants import *
from RateList import manage_addRateListForm, manage_addRateList
from ChartItem import manage_addChartItemForm, manage_addChartItem

def manage_addStatisticsTool(self, rate_list=[], REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    ob = StatisticsTool(ID_STATISTICSTOOL, TITLE_STATISTICSTOOL, rate_list)
    self._setObject(ID_STATISTICSTOOL, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class StatisticsTool(Folder, utils):
    """
    Class that implements the tool.
    """

    meta_type = METATYPE_STATISTICSTOOL

    security = ClassSecurityInfo()

    def __init__(self, id, title, rate_list):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title
        self.colors = CHART_COLORS

    meta_types = (
        {'name': METATYPE_RATELIST, 'action': 'manage_addRateListForm'},
        {'name': METATYPE_CHARTITEM, 'action': 'manage_addChartItemForm'},
        {'name': 'Page Template', 'action': 'manage_addPageTemplateForm'},
        )
    all_meta_types = meta_types

    #constructors
    manage_addRateListForm = manage_addRateListForm
    manage_addRateList = manage_addRateList

    manage_addChartItemForm = manage_addChartItemForm
    manage_addChartItem = manage_addChartItem

    manage_addPageTemplateForm = manage_addPageTemplateForm
    manage_addPageTemplate = manage_addPageTemplate

    def getChartColors(self):
        """ return the chart colors list """
        return self.colors

    def getRateLists(self): return self.objectValues(METATYPE_RATELIST)

    def getRateListById(self, p_id):
        #return the selection list with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type != METATYPE_RATELIST: ob = None
        return ob

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None):
        """ """
        pass

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None):
        """ """
        REQUEST.RESPONSE.redirect('manage_properties_html')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/statistics_properties', globals())

    security.declareProtected(view_management_screens, 'rate_properties_html')
    rate_properties_html = PageTemplateFile('zpt/rate_properties', globals())

InitializeClass(StatisticsTool)