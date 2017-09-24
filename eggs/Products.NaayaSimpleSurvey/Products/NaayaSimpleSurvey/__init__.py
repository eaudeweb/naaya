#Zope imports
from App.ImageFile import ImageFile

#Product imports
import NySurvey
import NySurveyTemplate
import NySurveyAnswer


def initialize(context):
    """ """

    #register classes
    context.registerClass(
    NySurvey.NySurvey,
    permission = 'Add Content',
    constructors = (
            NySurvey.manage_addNySurvey_html,
            NySurvey.addNySurvey,
            ),
    icon = 'www/NySurvey.gif'
    )

    context.registerClass(
    NySurveyTemplate.NySurveyTemplate,
    permission = 'Add Content',
    constructors = (
            NySurveyTemplate.manage_addNySurveyTemplate_html,
            NySurveyTemplate.addNySurveyTemplate,
            ),
    icon = 'www/NySurveyTemplate.gif'
    )

    context.registerClass(
    NySurveyAnswer.NySurveyAnswer,
    permission = 'Add Content',
    constructors = (
            NySurveyAnswer.manage_addNySurveyAnswer_html,
            NySurveyAnswer.addNySurveyAnswer,
            ),
    icon = 'www/NySurveyAnswer.gif'
    )

