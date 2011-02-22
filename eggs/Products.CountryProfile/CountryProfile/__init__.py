import CountryProfile
from App.ImageFile import ImageFile

def initialize(context):
    """ """
    context.registerClass(
        CountryProfile.CountryProfile,
        constructors = (
            CountryProfile.manage_add_html,
            CountryProfile.manage_add_object),
        icon = 'www/meta_type.gif'
    )

misc_ = {
#    'meta_type.gif':ImageFile('www/meta_type.gif', globals()),
}