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
# Alex Morega, Eau de Web
# David Batranu, Eau de Web

import os
import shutil
import tempfile
from unittest.mock import patch

from App.config import getConfiguration

from naaya.content.talkback.comment_item import Contributor


def user_contributor(userid):
    return Contributor(name=userid, email='', organisation='', source='',
                       invite='')


def invite_contributor(invitation):
    return Contributor(name=invitation.name, email=invitation.email,
                       organisation='', source='invite', invite=invitation.key)


def anonymous_contributor(name, email='', organisation=''):
    return Contributor(name=name, email=email, organisation=organisation,
                       source='anonymous', invite='')


def use_temp_sites_log(test):
    """ Point SITES_LOG_PATH (saved emails, site logs) to a temp dir """
    tmp_dir = tempfile.mkdtemp(prefix='talkback-sites-log-')
    test.addCleanup(shutil.rmtree, tmp_dir, True)
    # getExtConfiguration copies os.environ over the configuration
    for environment in (getConfiguration().environment, os.environ):
        env_patch = patch.dict(environment, {'SITES_LOG_PATH': tmp_dir})
        env_patch.start()
        test.addCleanup(env_patch.stop)
    return tmp_dir
