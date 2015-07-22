import Interface

class IDocAuth(Interface.Base):
    """ interface for DocAuth """

    def getUserNames():
        """ Return a list of usernames """
    
    def getUsers():
        """ Return a list of user objects """
        
    def getUser(name):
        """ Return the named user object or None """
    
    def getUserAccount(user_obj):
        """ Return the username """
    
    def getUserPassword(user_obj):
        """ Return the password """
    
    def getUserFirstName(user_obj):
        """ Return the firstname """
        
    def getUserLastName(user_obj):
        """ Return the lastname """
    
    def getUserEmail(user_obj):
        """ Return the email """
    
    def getUserHistory(user_obj):
        """ Return the last login """
        
    def getUserCreatedDate(user_obj):
        """ Return the created date """
        
    def getUserLastUpdated(user_obj):
        """ Return the lastupdated date """
        
    def forgotPassword(email):
        """ retrieve user's password given the email """