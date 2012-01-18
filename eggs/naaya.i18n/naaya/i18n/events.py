from zope.interface import implements
from interfaces import IMessageAddEvent


class MessageAddEvent(object):
    """ New message added to catalog """

    implements(IMessageAddEvent)

    def __init__(self, message_catalog, msgid, lang, default):
        self.message_catalog = message_catalog
        self.msgid = msgid
        self.lang = lang
        self.default = default
