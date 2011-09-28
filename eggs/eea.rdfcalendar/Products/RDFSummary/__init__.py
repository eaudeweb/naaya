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
# The Original Code is RDFSummary version 1.0.
#
# The Initial Developer of the Original Code is European Environment
# Agency (EEA).  Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
#
import RDFSummary

def initialize(context):
    """Initialize the RDFSummary product.
    """
    context.registerClass(
        RDFSummary.RDFSummary,
        constructors = (RDFSummary.manage_addRDFSummaryForm,
                        RDFSummary.manage_addRDFSummary),
        icon = 'rss.gif')
