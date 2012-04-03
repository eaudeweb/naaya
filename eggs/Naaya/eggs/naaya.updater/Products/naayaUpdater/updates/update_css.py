# -*- coding=utf-8 -*-

import os
import re
from StringIO import StringIO

from AccessControl import ClassSecurityInfo
from App.ImageFile import ImageFile

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateCSS(UpdateScript):
    """ Update portal stylesheets files with given CSS rules """
    title = 'Update portal stylesheets files with given CSS rules'
    authors = [u'Bogdan Tănase']
    description = 'Appends given CSS rules to the selected stylesheet of portal'
    creation_date = 'Mar 28, 2012'
    priority = PRIORITY['LOW']
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        """
        Append new CSS rules to selected CSS files of the portal
        """

        def _clean(text):
            """
            Remove carriage return characters (\r)
            and line break characters (\n)
            """
            return re.sub(r'[\r\n]', '', text)

        def _remove_comments(css):
            """
            Remove comments from CSS
            """
            pattern = r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)'
            return re.sub(pattern, '', css)

        def _parse_css(css):
            """
            Get declarations and blocks from CSS code

            e.g.
            - block:
            '.akismet-loading .icon {
                display: inline-block;
                width: 16px;
                height: 16px;
            }'

            - declaration:
            .akismet-loading .icon {
            """
            css = _remove_comments(css)

            declarations = re.findall(declaration_pattern, css)
            declarations = [_clean(declaration) for declaration in declarations]

            rough_blocks = re.findall(block_pattern, css)
            try:
                blocks = [block[1] for block in rough_blocks
                          if (type(block) is tuple and block[1])]
            except IndexError:
                blocks = []
            original_blocks = blocks
            blocks = [_clean(block) for block in blocks]

            return [
                set(declarations),
                set(blocks),
                original_blocks
            ]

        declaration_pattern = ('[[\t\n\r]*[a-zA-Z0-9\.# -_:@]+[\t\n\r]*\{.*'
                               '[\t\n\r]*]*')
        block_pattern = ('(\/\*[^.]+\*\/\n+)?([\t]*[a-zA-Z0-9\.# -_:@\s\n\r]+['
                         '\t\s]*\{[^}]+\})')

        form = self.REQUEST.form
        new_css = form.get('new_css', '')
        portal_path = '/'.join(portal.getPhysicalPath())
        portal_paths = form.get('portal_paths', None)

        if new_css:
            declarations, blocks, original_blocks = _parse_css(new_css)

            if portal_path in portal_paths and declarations and blocks:
                file_to_update = form.get(portal_path + '-style_files', None)
                if file_to_update:
                    scheme = portal.portal_layout.getCurrentSkinScheme()
                    if file_to_update in scheme.objectIds():
                        style_ob = scheme._getOb(file_to_update)
                        current_declarations, current_blocks, current_original_blocks = _parse_css(style_ob._text)
                        declarations_diff = declarations - current_declarations
                        blocks_diff = blocks - current_blocks

                        if not len(declarations_diff) and not len(blocks_diff):
                            self.log.info('File "%s" already has the changes'
                                          ' applied' % file_to_update)
                            return True
                        else:
                            if len(blocks_diff) != len(blocks):
                                css_to_add = '\n'.join([original_blocks[list(blocks).index(block)] for block in list(blocks_diff)])
                            else:
                                css_to_add = new_css

                        new_text = style_ob._text + '\n\n' + css_to_add
                        style_ob.pt_edit(new_text, style_ob.content_type)
                        self.log.debug('Added new CSS rules \n%s\n to portal'
                                       ' "%s" in file "%s"' %
                                        (css_to_add, portal_path,
                                         file_to_update))
                    else:
                        self.log.error('The file selected selected to update '
                                       'was "%s" but the portal has only "%s"!'
                                       % (file_to_update,
                                          ', '.join(scheme.objectIds)))
                        return False
                else:
                    self.log.error('No CSS file to update selected for portal'
                                   ' "%s"' % portal_path)
                    return False
        else:
            self.log.debug('No CSS rules were specified for this update!')

        return True

    update_template = PageTemplateFile('zpt/update_css', globals())
    update_template.default = UpdateScript.update_template
