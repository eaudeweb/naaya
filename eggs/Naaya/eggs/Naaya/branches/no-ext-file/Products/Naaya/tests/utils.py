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

def load_test_file(filename, globals_):
    """ Load data from a test file """
    home = package_home(globals_)
    filename = os.path.sep.join([home, filename])
    data = StringIO(open(filename, 'rb').read())
    data.filename = os.path.basename(filename)
    return data
