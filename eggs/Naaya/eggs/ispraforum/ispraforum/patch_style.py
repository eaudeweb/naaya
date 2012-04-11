import os
import re

line_pattern = re.compile(r'tal:attributes="href [^"]*/additional_style_css"')
new_href = 'tal:attributes="href string:${skin_files_path}/style-ispraforum.css"'


def patch_template(tmpl):
    lines = tmpl._text.splitlines()
    for i, line in enumerate(lines):
        m = line_pattern.search(line)
        if m is None:
            continue
        i += 1
        lines[i:i] = line_pattern.sub(new_href, line)
        break
    new_content = ''.join(lines)
    tmpl.pt_edit(new_content, tmpl.content_type)


def patch_style_for_new_site(event):
    application = event.application
    site = application.unrestrictedTraverse(application.created_path)
    tmpl = site['portal_layout'].get_current_skin()['standard_template']
    _update_logo(site, logo_id='right_logo.gif', delete=True)
    _update_logo(site, 'left_logo.gif', 'left_logo.png', 'image/png',
                 'Site left logo')
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
