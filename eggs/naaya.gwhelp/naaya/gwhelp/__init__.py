from gwhelp import manage_addGWHelp_html, manage_addGWHelp
from gwhelp import GWHelp

def initialize(context):
    context.registerClass(GWHelp, constructors=(
        ('manage_addGWHelp_html', manage_addGWHelp_html),
        ('manage_addGWHelp', manage_addGWHelp),
    ))
