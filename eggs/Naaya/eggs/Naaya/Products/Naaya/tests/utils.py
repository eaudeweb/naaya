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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

"""
Testing utilities
"""

replaced_objects = []

def replace(namespace, name, test_value):
    """
    Replaces the element `name` of `namespace` with `test_value`:

        from Products.Naaya.tests import utils as test_utils
        from my_product import mail_module

        class MyTestCase(unittest.TestCase):
            def tearDown(self):
                test_utils.restore_all()

            def test_mails(self):
                sent_messages = []
                def mock_send_mail(message):
                    sent_messages.append(message)
                test_utils.replace(mail_module, 'send_mail', mock_send_mail)

                # ... do some test that sends an email
                self.assertEqual(len(sent_messages), 1)
    """
    original = getattr(namespace, name)
    replaced_objects.append( (namespace, name, original) )
    setattr(namespace, name, test_value)

def restore_all():
    for namespace, name, original in replaced_objects:
        setattr(namespace, name, original)
