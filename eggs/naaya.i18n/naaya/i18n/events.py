from zope.interface import implementer
from .interfaces import IMessageAddEvent


@implementer(IMessageAddEvent)
class MessageAddEvent(object):
    """ New message added to catalog """


    def __init__(self, message_catalog, msgid, lang, default):
        self.message_catalog = message_catalog
        self.msgid = msgid
        self.lang = lang
        self.default = default
