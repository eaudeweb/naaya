#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

#Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

class Subscriptions(SimpleItem):
    security = ClassSecurityInfo()

    title = "Meeting subscriptions"

    def __init__(self, id):
        """ """
        self.id = id

    def subscribe(self):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'meeting_subscription_add')
    
    def addSubscription(self, REQUEST):
        """ """
        pass


InitializeClass(Subscriptions)

NaayaPageTemplateFile('zpt/subscription_add', globals(), 'meeting_subscription_add')

