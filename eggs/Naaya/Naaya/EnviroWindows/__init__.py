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
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Gabriel Agu
# Miruna Badescu

#Python imports

#Zope imports
from ImageFile import ImageFile

#Product imports
from constants import *
import EnviroWindowsSite
def initialize(context):
    """ """

    #register classes
    context.registerClass(
        EnviroWindowsSite.EnviroWindowsSite,
        permission = PERMISSION_ADD_EWSITE,
        constructors = (
                EnviroWindowsSite.manage_addEnviroWindowsSite_html,
                EnviroWindowsSite.manage_addEnviroWindowsSite,
                ),
        icon = 'www/Site.gif'
        )

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
}
