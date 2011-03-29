from zope.interface import Interface
from zope.component.interfaces import IObjectEvent

class INyGlossaryItem(Interface):
    """
    An item in the glossary. Can be a folder or a leaf element. It contains
    translated versions of its title in any of the Glossary's languages.
    """

    def set_translations_list(language, value):
        """
        Set this item's translation in `language` to `value`. This will send
        an IItemTranslationChanged event and will automatically update the
        glossary's catalog.
        """

class INyGlossaryElement(INyGlossaryItem):
    """ A leaf element in a Nayaa Glossary.  """

class INyGlossaryFolder(INyGlossaryItem):
    """
    A folder in a Nayaa Glossary.  It may contain sub-folders and elements.
    """

class IItemTranslationChanged(IObjectEvent):
    """ The translation in a language for a glossary item was changed. """
