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

from permissions import *
import SurveyQuestionnaire
import SurveyAnswer
import SurveyTool
import SurveyTemplate
import SurveyReport
import MegaSurvey
from ImageFile import ImageFile

from Products.Naaya import register_content

import statistics

def initialize(context):
    """ """
    context.registerClass(
        SurveyTool.SurveyTool,
        permission = PERMISSION_ADD_SURVEYTOOL,
        constructors = SurveyTool.SurveyTool._constructors,
        icon = 'www/SurveyTool.gif'
    )
    context.registerClass(
        SurveyTemplate.SurveyTemplate,
        permission = PERMISSION_ADD_SURVEYTEMPLATE,
        constructors = SurveyTemplate.SurveyTemplate._constructors,
        icon = 'www/Survey.gif'
    )
    context.registerClass(
        SurveyQuestionnaire.SurveyQuestionnaire,
        permission = PERMISSION_ADD_QUESTIONNAIRE,
        constructors = SurveyQuestionnaire.SurveyQuestionnaire._constructors,
        icon = 'www/NySurveyQuestionnaire.gif'
    )
    context.registerClass(
        MegaSurvey.MegaSurvey,
        permission = PERMISSION_ADD_QUESTIONNAIRE,
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
        permission = PERMISSION_MANAGE_SURVEYTEMPLATE,
        constructors = SurveyReport.SurveyReport._constructors,
        icon = 'www/NySurveyReport.gif'
    )
    statistics.initialize(context)

    # Register as a folder content type
    register_content(
        module=SurveyQuestionnaire,
        klass=SurveyQuestionnaire.SurveyQuestionnaire,
        module_methods={'manage_addSurveyQuestionnaire': PERMISSION_ADD_QUESTIONNAIRE},
        klass_methods={'questionnaire_add_html': PERMISSION_ADD_QUESTIONNAIRE},
        add_method=('questionnaire_add_html', PERMISSION_ADD_QUESTIONNAIRE),
    )
    register_content(
        module=MegaSurvey,
        klass=MegaSurvey.MegaSurvey,
        module_methods={'manage_addMegaSurvey': PERMISSION_ADD_MEGASURVEY},
        klass_methods={'megasurvey_add_html': PERMISSION_ADD_MEGASURVEY},
        add_method=('megasurvey_add_html', PERMISSION_ADD_MEGASURVEY),
    )

misc_ = {
    'SurveyTemplate.gif': ImageFile('www/Survey.gif', globals()),
    'SurveyTool.gif': ImageFile('www/SurveyTool.gif', globals()),
    'NySurveyQuestionnaire.gif': ImageFile('www/NySurveyQuestionnaire.gif', globals()),
    'NySurveyQuestionnaire_marked.gif': ImageFile('www/NySurveyQuestionnaire_marked.gif', globals()),
    'NySurveyAnswer.gif': ImageFile('www/NySurveyAnswer.gif', globals()),
    'barchart': ImageFile('www/barchart.png', globals()),
}
