from zope.interface import Interface

class ITemplate(Interface):
    def __call__(*args, **kwargs):
        """Render the template"""
