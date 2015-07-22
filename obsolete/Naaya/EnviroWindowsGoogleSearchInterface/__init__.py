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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
#
#
#$Id: __init__.py 2719 2004-11-29 17:08:51Z finrocvs $

#Python imports

#Zope imports
from App.ImageFile import ImageFile

#Product imports
from constants import *
import EWGoogleEngine
import EWGoogleSearchInterface

def initialize(context):
    """ initialize the EWInstaller object """

    #add EWInstaller
    app = context._ProductContext__app
    if hasattr(app, EWGOOGLEENGINE_ID):
        obj = getattr(app, EWGOOGLEENGINE_ID)
    else:
        try:
            obj = EWGoogleEngine.EWGoogleEngine()
            app._setObject(EWGOOGLEENGINE_ID, obj)
            get_transaction().note('Added EWGoogleEngine')
            get_transaction().commit()
        except:
            pass
        obj = getattr(app, EWGOOGLEENGINE_ID)
    assert obj is not None

    #register classes
    context.registerClass(
        EWGoogleSearchInterface.EWGoogleSearchInterface,
        permission = 'Add EWGoogleSearchInterface object',
        constructors = (
                EWGoogleSearchInterface.manage_addEWGoogleSearchInterface_html,
                EWGoogleSearchInterface.addEWGoogleSearchInterface_html,
                EWGoogleSearchInterface.addEWGoogleSearchInterface,
                ),
        icon = 'images/EWGoogleSearchInterface.gif'
        )

misc_ = {
    'EWGoogleEngine.gif': ImageFile('images/EWGoogleEngine.gif', globals()),
    'EWGoogleSearchInterface.gif': ImageFile('images/EWGoogleSearchInterface.gif', globals()),
    'search.jpg': ImageFile('images/search.jpg', globals()),
    'temp_basket.jpg': ImageFile('images/temp_basket.jpg', globals()),
    'empty_basket.jpg': ImageFile('images/empty_basket.jpg', globals()),
    'properties.jpg': ImageFile('images/properties.jpg', globals()),
    'help.gif': ImageFile('images/help.gif', globals()),
    'log.jpg': ImageFile('images/log.jpg', globals()),
    'search_words.jpg': ImageFile('images/search_words.jpg', globals()),
    'tab_bleu_bg.gif': ImageFile('images/tab_bleu_bg.gif', globals()),
    'edit.gif': ImageFile('images/edit.gif', globals()),
}

#try to set the constructor for the EWFolder class
try:
    from Products.Naaya.NyFolder import NyFolder
    NyFolder.addEWGoogleSearchInterface_html = EWGoogleSearchInterface.addEWGoogleSearchInterface_html
    NyFolder.addEWGoogleSearchInterface = EWGoogleSearchInterface.addEWGoogleSearchInterface
except:
    pass
