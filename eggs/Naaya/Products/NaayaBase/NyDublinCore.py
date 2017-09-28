"""
This module contains the class that provides Dublin Core elements.
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from constants import *

class NyDublinCore:
    """
    The class that provides Dublin Core elements.
    """

    def __init__(self):
        """
        Initialize variables.
        """

        pass

    security = ClassSecurityInfo()

    security.declarePublic('format')
    def format(self):
        """
        The physical or digital manifestation of the resource.
        """

        return 'text/html'

    security.declarePublic('type')
    def type(self):
        """
        The nature or genre of the content of the resource.
        """

        return 'Text'

    security.declarePublic('identifier')
    def identifier(self):
        """
        An unambiguous reference to the resource within a given context.
        """

        return self.absolute_url()

    security.declarePublic('language')
    def language(self):
        """
        A language of the intellectual content of the resource.
        """

        return self.gl_get_selected_language()

InitializeClass(NyDublinCore)
