from zope.interface import Interface

class IDumpReader(Interface):
    """ Utility that can read data from an LDAP dump """

    def latest_timestamp():
        """ get a `datetime` value of the latest dump """

    def get_dump():
        """ get an iterator for key/value pairs with all dumped data """
