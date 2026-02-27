from unittest.mock import Mock

from Products.NaayaSurvey.MegaSurvey import MegaSurvey

class Survey(MegaSurvey):
    def __init__(self):
        pass

    def getPortalI18n(self):
        mock_i18n = Mock()
        mock_i18n.get_translation = lambda msg, **kw: msg
        return mock_i18n
