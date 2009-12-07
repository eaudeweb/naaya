from zope.interface import Interface, implements
from OFS.SimpleItem import SimpleItem


class IGWApplications(Interface):

    def mymethod():
        """Return some text.
        """


class GWApplications(SimpleItem):

    implements(IGWApplications)

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def mymethod(self):
        return "Hello world"


class GWApplicationsAddView:

    """Add view for GW applications.
    """

    def __call__(self, add_input_name='', title='', submit_add=''):
        if submit_add:
            obj = GWApplications(add_input_name, title)
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()
