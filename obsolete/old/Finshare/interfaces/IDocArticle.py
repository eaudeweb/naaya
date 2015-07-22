import Interface

class IDocArticle(Interface.Base):
    """ DocArticle is a ?????"""
    
    def saveProperties(title, description, coverage, keywords, sortorder, locator):
        """ updates DocArticle instance properties """            
    def manageProperties(self, title, description, abstract, releasedate, coverage, keywords, sortorder,
                         maintainer_email, approved, source, thematic_area, links, source_type):
        """ updates DocArticle instance properties (console) """
    def index_rdf():
        """ return a rdf file with all published objects """        
    def getDocArticle():
        """ returns the Document Article """
    def getDocArticleURL():
        """ returns the Document Article URL """        
    def getThematicAreas():
        """ returns a list with all thematic areas """    
    def getParentNode():
        """ returns parent node"""
    def getPublishedDMObjects():
        """ returns a list with all published objects """                        
    def checkPermissionManageObjects(filter):
        """ returns containing objects of the current article """
    def saveComment(doc_title, doc_comment, doc_email):
        """ creates a comment """
    def voteThisDocument(rank):
        """allows voting"""    