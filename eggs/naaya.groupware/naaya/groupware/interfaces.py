from zope.interface import Interface

from Products.Naaya.interfaces import INySite

class IGroupwareApplication(Interface):
    """ This is a Zope App marker where groupware is installed """

class IEionetForumApplication(IGroupwareApplication):
    """ This is a Zope App marker where EIONET Forum is installed """

class IArchivesForumApplication(IGroupwareApplication):
    """ This is a Zope App marker where EIONET Forum is installed """

class ISinanetApplication(IGroupwareApplication):
    """ This is a Zope App marker where SINAnet Forum is installed """

class IGWSite(INySite):
    """ Interface for EnviroWindowsSite """
    pass
