from App.ImageFile import ImageFile

from Products.Naaya import register_content
import CHMProjectRegistration
from utilities.StaticServe import StaticServeFromZip

ADD_PERMISSION = 'CHM Project Registration - Manage Registration'

# Register as a folder content type
register_content(
    module=CHMProjectRegistration,
    klass=CHMProjectRegistration.CHMProjectRegistration,
    module_methods={'manage_add_chm_project_registration': ADD_PERMISSION, 'add_chm_project_registration': ADD_PERMISSION},
    klass_methods={},
    add_method=('add_chm_project_registration', ADD_PERMISSION),
)

def initialize(context):
    context.registerClass(
                          CHMProjectRegistration.CHMProjectRegistration,
                          permission = ADD_PERMISSION,
                          constructors=(
                                    CHMProjectRegistration.add_chm_project_registration,
                                    CHMProjectRegistration.manage_add_chm_project_registration),
                          icon='www/CHMProjectRegistration.gif',
                          )

misc_ = {
    'tinymce': StaticServeFromZip('', 'www/tinymce_3_2_7.zip', globals()),
    'tinymceconfig.js': ImageFile('www/tinymceconfig.js', globals()),
    'calendar.js': ImageFile('www/calendar.js', globals()),
    'core.js': ImageFile('www/core.js', globals()),
    'datetime.js': ImageFile('www/datetime.js', globals()),
    'process.js': ImageFile('www/process.js', globals()),
    'style.css': ImageFile('www/style.css', globals()),
    'print.css': ImageFile('www/print.css', globals()),
    'CHMProject.png': ImageFile('www/CHMProject.png', globals()),
    'print.gif': ImageFile('www/print.gif', globals()),
    'EmailTemplates.gif': ImageFile('www/EmailTemplates.gif', globals()),
    }