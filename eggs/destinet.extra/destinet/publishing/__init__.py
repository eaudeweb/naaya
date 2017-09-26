"""
Initialization of destinet.publishing package:
 * register DestinetPublisher class in context
"""

from App.ImageFile import ImageFile

from DestinetPublisher import DestinetPublisher, manage_addDestinetPublisher


def initialize(context):
    """ """

    context.registerClass(
        DestinetPublisher,
        constructors = (manage_addDestinetPublisher, ),
        icon='www/icon.png')


misc_ = {
    'icon.png': ImageFile('www/icon.png', globals())
}
