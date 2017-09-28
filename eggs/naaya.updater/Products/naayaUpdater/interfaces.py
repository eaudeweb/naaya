from zope import schema
from zope.interface import Interface

class IUpdater(Interface):
    """ Updater tool
    """

class IUpdateScript(Interface):
    """ Update script
    """
    title = schema.TextLine(title=u'Title', required=True)
    description = schema.Text(title=u'Description', required=False)
    creation_date = schema.Date(title=u'Creation date', required=True)
    authors = schema.Tuple(title=u'Authors', required=True)
    priority = schema.Int(title=u'Priority', required=False)

    def update(portal, do_dry_run):
        """ Update
        @param portal NaayaSite instance to run update on
        @param do_dry_run Abort transaction if true
        """
