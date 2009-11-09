# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web


#Python imports
import os
from os.path import join
from StringIO import StringIO
from urllib2 import urlopen
from urllib import urlencode

import simplejson as json

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from App.ImageFile import ImageFile

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript

from Products.Naaya import NySite as NySite_module
from Products.Naaya.managers.skel_parser import skel_parser
from Products.naayaUpdater.utils import (convertLinesToList, convertToList,
    get_template_content, normalize_template, html_diff, readFile)

default_service_url = 'http://speaker.edw.ro/css_diff?format=json'
service_url = os.environ.get('NY_UPDATER_CSS_URL', default_service_url)

class UpdateCSS(UpdateScript):
    """ Update portal_layout stylesheets """
    id = 'update_css'
    title = 'Update css'
    authors = ['Alex Morega']
    creation_date = DateTime('Nov 9, 2009')

    css_scheme_names = ['scheme_style', 'style', 'style_common']
    css_layout_names = ['common_css', 'style_css',
                        'ew_common_css', 'ew_style_css',
                        'chm_common_css']

    def _update(self, portal):
        self.log.debug('/'.join(portal.getPhysicalPath()))

        form = self.REQUEST.form # TODO: don't rely on self.REQUEST
        new_css = form.get('new_css', '')
        skip_css_scheme_names = form.get('skip_css_scheme_names', [])
        skip_css_layout_names = form.get('skip_css_layout_names', [])

        all_css = StringIO()

        layout_tool = portal.portal_layout
        for name in self.css_layout_names:
            if name in skip_css_layout_names:
                continue
            ob = getattr(layout_tool, name, None)
            if ob is None:
                continue
            elif isinstance(ob, ImageFile):
                all_css.write(open(ob.path, 'rb').read())
            else:
                raise NotImplementedError

        scheme = layout_tool.getCurrentSkinScheme()
        for name in self.css_scheme_names:
            if name in skip_css_scheme_names:
                continue
            ob = getattr(scheme, name, None)
            if ob is not None:
                all_css.write(ob())

        data = {'left_css': all_css.getvalue(),
                'right_css': new_css}
        rq = urlopen(service_url, urlencode(data.items()))

        resp = json.loads(rq.read())
        new_css_delta = resp['output'][0]['added']
        self.log.info('new rules:\n======\n%s=======', new_css_delta)

        if 'scheme_style' in scheme.objectIds():
            style_ob = scheme._getOb('scheme_style')
        elif 'style' in scheme.objectIds():
            style_ob = scheme._getOb('style')
        else:
            self.log.error('No custom stylesheet found in current css scheme')
            return False

        new_text = style_ob._text + '\n\n' + new_css_delta
        style_ob.pt_edit(new_text, style_ob.content_type)

        return True

    update_template = PageTemplateFile('zpt/update_css', globals())
    update_template.default = UpdateScript.update_template
