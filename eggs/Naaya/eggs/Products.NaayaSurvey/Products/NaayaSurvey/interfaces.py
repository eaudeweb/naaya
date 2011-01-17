from zope.interface import Interface, Attribute

class INySurveyAnswer(Interface):
    """ A NaayaSurveyAnswer object """

class INySurveyAnswerAddEvent(Interface):
    """ A NaayaSurveyAnswer object adding was finished """

    context = Attribute("INySurveyAnswer instance")
