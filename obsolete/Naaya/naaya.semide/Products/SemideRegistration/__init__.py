from App.ImageFile import ImageFile

from Products.Naaya import register_content
import SemideRegistration
from naaya.core.StaticServe import StaticServeFromZip

ADD_PERMISSION = 'Add Semide Registration'

# Register as a folder content type
register_content(
    module=SemideRegistration,
    klass=SemideRegistration.SemideRegistration,
    module_methods={'manage_add_registration': ADD_PERMISSION, 'add_registration': ADD_PERMISSION},
    klass_methods={},
    add_method=('add_registration', ADD_PERMISSION),
)

def initialize(context):
    context.registerClass(
                          SemideRegistration.SemideRegistration,
                          permission = ADD_PERMISSION,
                          constructors=(
                                    SemideRegistration.add_registration,
                                    SemideRegistration.manage_add_registration),
                          icon='www/SemideRegistration.gif',
                          )

misc_ = {
    'tinymce': StaticServeFromZip('', 'www/tinymce_3_2_5.zip', globals()),
    'tinymceconfig.js': ImageFile('www/tinymceconfig.js', globals()),
    'calendar.js': ImageFile('www/calendar.js', globals()),
    'core.js': ImageFile('www/core.js', globals()),
    'datetime.js': ImageFile('www/datetime.js', globals()),
    'jquery-1.3.2.min.js': ImageFile('www/jquery-1.3.2.min.js', globals()),
    'autocomplete.js': ImageFile('www/jquery.autocomplete.min.js', globals()),
    'autocomplete.css': ImageFile('www/jquery.autocomplete.css', globals()),
    'style.css': ImageFile('www/style.css', globals()),
    'print.css': ImageFile('www/print.css', globals()),
    'SemideParticipant.png': ImageFile('www/SemideParticipant.png', globals()),
    'SemidePress.gif': ImageFile('www/SemidePress.gif', globals()),
    'print.gif': ImageFile('www/print.gif', globals()),
    'EmailTemplates.gif': ImageFile('www/EmailTemplates.gif', globals()),
    }