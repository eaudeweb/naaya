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
# The Original Code is ChangeNotification version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Cornel Nitu, Finsiel Romania

#This product includes software developed by Jens Vagelpohl
#for use in the Z Object Publishing Environment
#(http://www.zope.org/).


# General python imports
from types import StringType
import os
import tempfile
from Products.Finshare.utils import utils


# Zope imports
from Products.MailHost.MailHost import MailHost

MAILDROP_HOME = os.path.join(CLIENT_HOME,'maildrop')
if not os.path.isdir( MAILDROP_HOME ):
    try:
        os.mkdir(MAILDROP_HOME)
    except:
        raise OSError, 'Can\'t create directory %s' % MAILDROP_HOME

MAILDROP_SPOOL = os.path.join(MAILDROP_HOME,'spool')
if not os.path.isdir(MAILDROP_SPOOL):
    try:
        os.mkdir(MAILDROP_SPOOL)
    except:
        raise OSError, 'Can\'t create directory %s' %MAILDROP_SPOOL

class MaildropHost(MailHost):
    """ A MaildropHost """

    def _send(self, headers, body=''):
        """ Send a mail using the asynchronous maildrop handler """
        email = Email(headers['from'], headers['to'], body)
        email.send()


class Email:
    """ Simple non-persistent class to model a email message """

    def __init__(self, mfrom, mto, body):
        """ Instantiate a new email object """
        if not isinstance(mto, StringType):
            self.m_to = ','.join(mto)
        else:
            self.m_to = mto
        self.m_from = mfrom
        self.body = body


    def send(self):
        """ Write myself to the file system """
        id = utils().utGenRandomId(5)
        try:
            temp_path = os.tmpname(MAILDROP_SPOOL)
        except:
            temp_path = os.path.join(MAILDROP_SPOOL, id)

        lock = open('%s.lck' % temp_path, 'w')
        lock.write('locked')
        lock.close()

        temp = open(temp_path, 'w')
        temp.write(MAIL_TEMPLATE % (self.m_to, self.m_from, self.body))
        temp.close()

        os.unlink('%s.lck' % temp_path)


MAIL_TEMPLATE = """
##To:%s
##From:%s
%s
"""