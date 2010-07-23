# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cristian Ciupitu, Eau de Web

# Zope imports
from OFS.SimpleItem import SimpleItem

# Naaya imports
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.NaayaCore.managers.utils import genObjectId, genRandomId

def manage_addStatistic(klass, container, id="", question=None, REQUEST=None, **kwargs):
    """Add statistic"""
    if not id:
        id = genRandomId()

    idSuffix = ''
    while (id+idSuffix in container.objectIds() or
           getattr(container, id+idSuffix, None) is not None):
        idSuffix = genRandomId(p_length=4)
    id = id + idSuffix

    # Get selected language
    lang = REQUEST and REQUEST.form.get('lang', None)
    lang = lang or kwargs.get('lang', container.gl_get_selected_language())
    statistic = klass(id, question, lang=lang, **kwargs)

    container.gl_add_languages(statistic)
    container._setObject(id, statistic)

    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
    return id

class BaseStatistic(SimpleItem, LocalPropertyManager):
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
