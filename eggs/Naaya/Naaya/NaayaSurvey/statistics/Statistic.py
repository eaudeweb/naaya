# Zope imports
from OFS.SimpleItem import SimpleItem

# Naaya imports
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.NaayaCore.managers.utils import utils

gUtil = utils()


def manage_addStatistic(klass, container, id="", REQUEST=None, **kwargs):
    """Add statistic"""
    global gUtil

    if not id:
        id = gUtil.utGenRandomId()

    idSuffix = ''
    while (id+idSuffix in container.objectIds() or
           getattr(container, id+idSuffix, None) is not None):
        idSuffix = gUtil.utGenRandomId(p_length=4)
    id = id + idSuffix

    # Get selected language
    lang = REQUEST and REQUEST.form.get('lang', None)
    lang = lang or kwargs.get('lang', container.gl_get_selected_language())
    statistic = klass(id, lang=lang, **kwargs)

    container.gl_add_languages(statistic)
    container._setObject(id, statistic)

    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
    return id


class Statistic(SimpleItem, LocalPropertyManager):
    """Base class for statistics"""

    manage_options=(
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'View', 'action':'index_html'},
        )

    # Properties
    _properties=(
        {'id':'sortorder', 'type':'int','mode':'w', 'label':'Sort order'},
    )

    def __init__(self, id, question, lang=None, **kwargs):
        """__init__

            @param id: id
            @param question: question
            @param lang: language
        """
        self.id = id
        self.question = question
        self.sortorder = kwargs.get('sortorder', question.sortorder)
