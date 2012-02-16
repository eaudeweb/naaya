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
    patch_template(tmpl)
