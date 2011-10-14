from zope.interface import Interface

from Products.Naaya.interfaces import INySite

class IGroupwareApplication(Interface):
    """ This is a Zope App marker where groupware is installed """

class IGWSite(INySite):
    """ Interface for EnviroWindowsSite """
    pass
