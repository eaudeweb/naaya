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
    creation_date = schema.Date(title=u'Creation date', required=False)
    authors = schema.Tuple(title=u'Authors', required=False)
    priority = schema.Int(title=u'Priority', required=True)
    categories = schema.Tuple(title=u'Categories', required=False)

    def update(portal, do_dry_run):
        """ Update
        @param portal NaayaSite instance to run update on
        @param do_dry_run Abort transaction if true
        """
