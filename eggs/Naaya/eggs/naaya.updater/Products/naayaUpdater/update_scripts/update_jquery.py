#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Alexandru Plugaru, Eau de Web


#Python
import re
from DateTime import DateTime
#Zope
from AccessControl import ClassSecurityInfo

#Naaya
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY

class UpdateJquery(UpdateScript):
    """ Replace script tags in standard_template """
    id = 'update_jquery'
    title = 'Update jQuery'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('May 6, 2010')
    authors = ['Alexandru Plugaru',]
    #priority = PRIORITY['LOW']
    description = 'Replaces script tag with jquery from local to Google storage'
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        standard_template = portal.getLayoutTool().get_current_skin()._getOb('standard_template')
        old_content = standard_template._text
        if 'jquery' in old_content:
            new_content = old_content.replace("""        <metal:block define-slot="standard-head-content">
            <script type="text/javascript" tal:attributes="src string:${site_url}/misc_/Naaya/jquery-1.3.2.min.js"></script>
            <script type="text/javascript">
            //<![CDATA[
            // required for the replacement of target="_blank"
            function externalLinks() {
                if (!document.getElementsByTagName) return;
                var anchors = document.getElementsByTagName("a");
                for (var i=0; i<anchors.length; i++) {
                    var anchor = anchors[i];
                    if (anchor.getAttribute("rel") == "external") {
                        anchor.target = "_blank";
                        anchor.style.display = "inline";
                    }
                    else {
                        anchor.style.display = "";
                    }
                }
            }
            window.onload = externalLinks;
            //]]>
            </script>
        </metal:block>""", """
        <metal:block define-slot="standard-head-content">
            <script type="text/javascript" tal:attributes="src string:${site_url}/misc_/Naaya/jquery.js"></script>
            <script type="text/javascript" tal:attributes="src string:${site_url}/misc_/Naaya/jquery-ui.js"></script>
            <script type="text/javascript" tal:attributes="src string:${site_url}/misc_/Naaya/utils.js"></script>
        </metal:block>
""")
            if new_content != old_content:
                standard_template.pt_edit(text=new_content, content_type="text/html")
            else:
                self.log.debug(('The %s haven\'t been changed') % standard_template.getId())
        return True
