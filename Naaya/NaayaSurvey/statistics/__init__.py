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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# Cristian Ciupitu, Eau de Web

import glob
import os.path

from permissions import PERMISSION_ADD_STATISTICS

def _get_available_statistics():
    """ Return available statistics in current dir."""
    current_dir = os.path.dirname(__file__)
    modules = [i.split('.')[0] for i in glob.glob1(current_dir, "*.py")]
    statistics = []
    for module in modules:
        statistic = __import__(module, globals(),  locals())
        if not hasattr(statistic, 'getStatistic'):
            continue
        statistic = statistic.getStatistic()
        statistics.append(statistic)
    return statistics

AVAILABLE_STATISTICS = _get_available_statistics()
AVAILABLE_STATISTICS.sort(lambda x, y: cmp(x.meta_sortorder, y.meta_sortorder)) # predictible order

def register_statistic(context, statistic):
    """ Register given statistic to context"""
    context.registerClass(
        statistic,
        constructors = statistic._constructors,
        permission = PERMISSION_ADD_STATISTICS,
        icon = getattr(statistic, 'icon_filename', 'statistics/www/statistic.gif'))

def initialize(context):
    """Called at zope startup"""
    global AVAILABLE_STATISTICS
    for statistic in AVAILABLE_STATISTICS:
        register_statistic(context, statistic)
