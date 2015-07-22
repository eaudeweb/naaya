import Interface

class IDocFile(Interface.Base):
    """ DocFile is a ?????"""
                
    def manageProperties(title, description, releasedate, language, coverage, keywords, sortorder, approved, source,
                         f_source, file, precondition, content_type, downloadfilename, file_version, status):
        """ updates DocFile instance properties (console)"""
    def saveProperties(title, description, language, coverage, keywords, sortorder, f_source, file, content_type,
                       downloadfilename, file_version, status):
        """ updates File instance properties """      
    def saveComment(doc_title, doc_comment, doc_email):
        """ creates a comment """            
    def uploadFile(file):
        """ asociates a file to the DocFile object """    
    def download(REQUEST, RESPONSE):
        """ set for download asociated file """
    def getDownloadInfo():
        """ returns download information """    
    def showVersionData(vid):
        """ returns version's data """                 