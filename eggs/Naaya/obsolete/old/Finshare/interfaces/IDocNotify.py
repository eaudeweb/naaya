import Interface

class IDocNotify(Interface.Base):
    """ interface for DocNotify """

    def addMember():
        """ register a new member in the subscriber notification list"""

    def delMember():
        """ delete the given member from the subscriber notification list """

    def updateMember():
        """ update the members's subscriptions """

    def addArticle(id, title, description, author, date):
        """ add an article in the notification list """

    def delArticle(id):
        """ delete the given article from the notification list """

    def updateArticle(id):
        """ update the given article's metadata """