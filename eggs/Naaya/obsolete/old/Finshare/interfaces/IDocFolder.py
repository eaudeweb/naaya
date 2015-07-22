import Interface

class IDocFolder(Interface.Base):
    """ DocFolder is a container for all DocManager objects """

    def saveProperties(title, description, coverage, keywords, sortorder, locator):
        """ updates DocFolder instance properties """

    def manageProperties(title, description, abstract, releasedate, coverage,
                         keywords, sortorder, maintainer_email, approved, source):
        """ updates DocFolder instance properties (console) """

    def index_rdf():
        """ return a rdf file with all published objects """

    def getDocFolderURL():
        """ returns the folder URL """

    def getThematicAreas():
        """ returns a list with all thematic areas """

    def getPublishedDMObjects():
        """ returns a list with all  objects approved"""

    def checkPermissionManageObjects():
        """ returns containing objects of the current folder """