import Interface

class IDocURL(Interface.Base):
    """ DocURL class"""
                
    def manageProperties(title, description, abstract, language, coverage, keywords, sortorder, approved, locator,):
        """ updates URL instance properties (console)"""
    def saveProperties(title, description, abstract, language, coverage, keywords, sortorder, locator):
        """ updates DocURL instance properties """
        
    def saveComment(doc_title, doc_comment, doc_email):
        """ creates a comment """            
    