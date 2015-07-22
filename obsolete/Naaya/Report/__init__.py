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
# Alexandru Ghica, Finsiel Romania

#Python imports

#Zope imports
from App.ImageFile import ImageFile

#Product imports
from constants import *
from Products.NaayaCore.constants import *
from tools.StatisticsTool import StatisticsTool
import ReportSite

def initialize(context):
    """ """

    #register classes
    context.registerClass(
        ReportSite.ReportSite,
        permission = PERMISSION_ADD_REPORTSITE,
        constructors = (
                ReportSite.manage_addReportSite_html,
                ReportSite.manage_addReportSite,
                ),
        icon = 'www/Site.gif'
        )

    context.registerClass(
        StatisticsTool.StatisticsTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                StatisticsTool.manage_addStatisticsTool,
                ),
        icon = 'tools/StatisticsTool/www/StatisticsTool.gif'
        )

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'StatisticsTool.gif':ImageFile('tools/StatisticsTool/www/StatisticsTool.gif', globals()),
    'RateList.gif':ImageFile('tools/StatisticsTool/www/RateList.gif', globals()),
    'ChartItem.gif':ImageFile('tools/StatisticsTool/www/ChartItem.gif', globals()),
    'FC2Area3D.swf':ImageFile('tools/StatisticsTool/www/FC2Area3D.swf', globals()),
    'FC2Bar.swf':ImageFile('tools/StatisticsTool/www/FC2Bar.swf', globals()),
    'FC2Column.swf':ImageFile('tools/StatisticsTool/www/FC2Column.swf', globals()),
    'FC2Line.swf':ImageFile('tools/StatisticsTool/www/FC2Line.swf', globals()),
    'FC2Pie3D.swf':ImageFile('tools/StatisticsTool/www/FC2Pie3D.swf', globals()),
    'FC2Pipe.swf':ImageFile('tools/StatisticsTool/www/FC2Pipe.swf', globals()),
}