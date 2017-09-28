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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
""" Patch CHMSite
"""
from os.path import join

from naaya.component import bundles

from Products.CHM2.CHMSite import CHMSite
from constants import CHM2BE_PRODUCT_PATH

def wrap_loadDefaultData(method):
    def loadDefaultData(self, *args, **kwargs):
        method(self, *args, **kwargs)
        self.loadSkeleton(join(CHM2BE_PRODUCT_PATH))

        parent_bundle_name = self.get_bundle().__name__
        if parent_bundle_name == 'CHM3':
            self.set_bundle(chm3_be_bundle)
        else:
            self.set_bundle(chmbe_bundle)

    return loadDefaultData

CHMSite.product_paths.append(CHM2BE_PRODUCT_PATH)
CHMSite.loadDefaultData = wrap_loadDefaultData(CHMSite.loadDefaultData)

chmbe_bundle = bundles.get("CHMBE")
chmbe_bundle.set_parent(bundles.get("CHM"))

chm3_be_bundle = bundles.get("CHM3-BE")
chm3_be_bundle.set_parent(bundles.get("CHM3"))
