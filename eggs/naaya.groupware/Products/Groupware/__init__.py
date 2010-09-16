import os
from App.ImageFile import ImageFile
from naaya.groupware import groupware_site


groupware_folder = os.path.dirname(groupware_site.__file__)
def initialize(context):
    """ """
    context.registerClass(
        groupware_site.GroupwareSite,
        permission = 'Groupware - Add Groupware Site objects',
        constructors = (
                groupware_site.manage_addGroupwareSite_html,
                groupware_site.manage_addGroupwareSite,
                ),
        icon = groupware_folder + '/www/site.gif'
        )

misc_ = {
    'site.gif':ImageFile(groupware_folder + '/www/site.gif'),
    'printer.gif':ImageFile(groupware_folder + '/www/printer.gif'),
    'button_go.gif':ImageFile(groupware_folder + '/www/button_go.gif'),
}
