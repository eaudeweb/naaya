"""
Initialization of naaya.i18n package:
 * import patches, for thread_data module variable initialization
 * register NaayaI18n class in context
"""

import Globals # fixes Zope cross import when Zope not initialized
from App.ImageFile import ImageFile

from portal_tool import NaayaI18n, manage_addNaayaI18n
import patches


def initialize(context):
    """ """

    context.registerClass(
        NaayaI18n,
        constructors = (manage_addNaayaI18n, ),
        icon='www/icon.gif')


misc_ = {
    'icon.gif': ImageFile('www/icon.gif', globals())
}
