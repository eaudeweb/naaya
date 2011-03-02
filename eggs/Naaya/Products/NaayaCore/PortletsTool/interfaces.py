from zope import interface

class INyPortlet(interface.Interface):
    """ A Naaya portlet, waiting to be rendered """

    title = interface.Attribute("Portlet title, shown in administration UI")

    def __call__(context, position):
        """
        Render the portlet. `context` is usually a folder or site. `position`
        is one of ('left', 'center', 'right').
        """
