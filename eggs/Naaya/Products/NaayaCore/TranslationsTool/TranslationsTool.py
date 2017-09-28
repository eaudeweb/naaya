"""
Left-overs required to unpickle class; can be deleted after applying
LocalizerToNaayaI18n update
"""
try:
    from Products.Localizer.MessageCatalog import MessageCatalog
except ImportError:
    pass
else:
    class TranslationsTool(MessageCatalog):
        """
        Class that implements the tool.
        """

        meta_type = 'Naaya Translations Tool'

        def __init__(self, id, title):
            """
            Initialize variables.
            """
            self.id = id
            self.title = title
            MessageCatalog.__dict__['__init__'](self, id, title, sourcelang='en', languages=['en'])
