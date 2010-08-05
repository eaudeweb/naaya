from App.ImageFile import ImageFile

from Products.Naaya import register_content
import CHMRegistration
from utilities.StaticServe import StaticServeFromZip

ADD_PERMISSION = 'Add CHM Registration'

# Register as a folder content type
register_content(
    module=CHMRegistration,
    klass=CHMRegistration.CHMRegistration,
    module_methods={'manage_add_chm_registration': ADD_PERMISSION, 'add_chm_registration': ADD_PERMISSION},
    klass_methods={},
    add_method=('add_chm_registration', ADD_PERMISSION),
)

def initialize(context):
    context.registerClass(
                          CHMRegistration.CHMRegistration,
                          permission = ADD_PERMISSION,
                          constructors=(
                                    CHMRegistration.add_chm_registration,
                                    CHMRegistration.manage_add_chm_registration),
                          icon='www/CHMRegistration.gif',
                          )

misc_ = {
    'tinymce': StaticServeFromZip('', 'www/tinymce_3_2_5.zip', globals()),
    'tinymceconfig.js': ImageFile('www/tinymceconfig.js', globals()),
    'calendar.js': ImageFile('www/calendar.js', globals()),
    'core.js': ImageFile('www/core.js', globals()),
    'datetime.js': ImageFile('www/datetime.js', globals()),
    'style.css': ImageFile('www/style.css', globals()),
    'print.css': ImageFile('www/print.css', globals()),
    'CHMParticipant.png': ImageFile('www/CHMParticipant.png', globals()),
    'print.gif': ImageFile('www/print.gif', globals()),
    'EmailTemplates.gif': ImageFile('www/EmailTemplates.gif', globals()),
    }