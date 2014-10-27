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

# Zope imports
from App.ImageFile import ImageFile

# Naaya imports
from Products.Naaya import register_content

# pkg imports
import MegaSurvey
from permissions import *
import SurveyAnswer
import SurveyAttachment
import SurveyReport


import statistics

def initialize(context):
    """ """
    context.registerClass(
        MegaSurvey.MegaSurvey,
        permission = PERMISSION_ADD_MEGASURVEY,
        constructors = MegaSurvey.MegaSurvey._constructors,
        icon = 'www/NySurveyQuestionnaire.gif'
    )
    context.registerClass(
        SurveyAnswer.SurveyAnswer,
        permission = PERMISSION_ADD_ANSWER,
        constructors = SurveyAnswer.SurveyAnswer._constructors,
        icon = 'www/NySurveyAnswer.gif'
    )
    context.registerClass(
        SurveyReport.SurveyReport,
        permission = PERMISSION_ADD_REPORT,
        constructors = SurveyReport.SurveyReport._constructors,
        icon = 'www/NySurveyReport.gif'
    )
    context.registerClass(
        SurveyAttachment.SurveyAttachment,
        permission = PERMISSION_ADD_ATTACHMENT,
        constructors = SurveyAttachment.SurveyAttachment._constructors,
        icon = 'www/NySurveyAttachment.gif'
    )
    statistics.initialize(context)

misc_ = {
    'SurveyTemplate.gif': ImageFile('www/Survey.gif', globals()),
    'NySurveyQuestionnaire.gif': ImageFile('www/NySurveyQuestionnaire.gif', globals()),
    'NySurveyQuestionnaire_marked.gif': ImageFile('www/NySurveyQuestionnaire_marked.gif', globals()),
    'NySurveyAnswer.gif': ImageFile('www/NySurveyAnswer.gif', globals()),
    'barchart': ImageFile('www/barchart.png', globals()),
}
