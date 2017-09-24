import os
import re

from naaya.groupware.interfaces import ISinanetApplication


def patch_template(tmpl):
    full_path = os.path.dirname(os.path.abspath(__file__))
    standard_template_file = os.path.join(full_path, 'zpt/standard_template.zpt')
    standard_template = open(standard_template_file, 'r')
    new_content = standard_template.read()
    tmpl.pt_edit(new_content, tmpl.content_type)
    standard_template.close()

def patch_style_for_new_site(event):
    application = event.application
    site = application.unrestrictedTraverse(application.created_path)
    root = application.unrestrictedTraverse("/")
    if ISinanetApplication.providedBy(root): # special case for sinanet
        patch_sinanet_ig(site)
    else:
        patch_ispra_ig(site)

def patch_ispra_ig(site):
    tmpl = site['portal_layout'].get_current_skin()['standard_template']
    _update_logo(site, logo_id='right_logo.gif', delete=True)
    _update_logo(site, 'left_logo.gif', 'left_logo.png', 'image/png',
                 'Site left logo')
    site.mail_address_from = 'no-reply@groupware.info-rac.org'
    site.notify_on_errors_email = 'naayacrashteam@eaudeweb.ro'
    patch_template(tmpl)

def patch_sinanet_ig(site):
    tmpl = site['portal_layout'].get_current_skin()['standard_template']
    _update_logo(site, logo_id='right_logo.gif', delete=True)
    _update_logo(site, 'left_logo.gif', 'sinanet_logo.gif', 'Site left logo')
    site.mail_address_from = 'websinanet@isprambiente.it'
    site.notify_on_errors_email = 'naayacrashteam@eaudeweb.ro'
    patch_template(tmpl)

def _update_logo(site, logo_id='', new_logo_file='', content_type='image/gif',
                 title='', delete=False):
    """
    Updates logo file
    """
    layout_tool = site.getLayoutTool()
    layout_tool.manage_delObjects([logo_id])

    if not delete:
        full_path = os.path.dirname(os.path.abspath(__file__))
        logo_file = os.path.join(full_path, 'www/', new_logo_file)
        logo_content = open(logo_file, 'rb')
        layout_tool.manage_addImage(id=logo_id,
                                   file=logo_content,
                                   content_type=content_type,
                                   title=title)
        logo_content.close()
