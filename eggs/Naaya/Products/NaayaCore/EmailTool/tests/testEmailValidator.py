import time
import unittest
from mock import patch, MagicMock


from Products.NaayaCore.EmailTool.EmailValidator import EmailValidator

class EmailValidatorTest(unittest.TestCase):
    def setUp(self, maxW=2):
        self.maxW = maxW
        EmailValidator.THREAD_IDLE_SEC = 0.1
        self.email_validator = EmailValidator("checked_emails", maxWorkers=self.maxW)
        now = time.time()
        obj = MagicMock()
        # init the cache with one value already resolved to invalid
        # we expect the resolvation function not to be called for this email
        obj.checked_emails = {'alreadyBad@edw.ro': (False, now),
                              'alreadyGood@edw.ro': (True, now),
                              'alreadyBadButExpired@edw.ro':
                                (False, now - (EmailValidator.VERIFY_EMAIL_BADADDRESS_TTL + 1)),
                              'alreadyGoodButExpired@edw.ro':
                                (False, now - (EmailValidator.VERIFY_EMAIL_GOODADDRESS_TTL + 1)),
                            }
        self.email_validator.bind(obj)

    def test_validate_from_cache(self):
        r = self.email_validator.validate_from_cache('alreadyBad@edw.ro')
        self.assertNotEqual(r, True)
        self.assertNotEqual(r, None)

        r = self.email_validator.validate_from_cache('alreadyGood@edw.ro')
        self.assertEqual(r, True)

        r = self.email_validator.validate_from_cache('alreadyBadButExpired@edw.ro')
        self.assertEqual(r, None)

        r = self.email_validator.validate_from_cache('alreadyGoodButExpired@edw.ro')
        self.assertEqual(r, None)

        r = self.email_validator.validate_from_cache('notThere@edw.ro')
        self.assertEqual(r, None)

    @patch('Products.NaayaCore.EmailTool.EmailValidator.validate_email')
    def test_enqueue(self, mock_validate_email):
        # make resolvation function always return true (valid)
        mock_validate_email.return_value = True
        emails = ['alreadyBad@edw.ro', 'alreadyGood@edw.ro', 'alreadyBadButExpired@edw.ro', 'notInCache@edw.ro']
        for email in emails:
            self.email_validator.enqueue(email)
        self.assertEqual(len(self.email_validator._workers), self.maxW)
        time.sleep(EmailValidator.THREAD_IDLE_SEC + 0.05)

        # they are all in the cache either True or False
        for email in emails:
            r = self.email_validator.validate_from_cache(email)
            self.assertNotEqual(r, None)
        # after the sleep period all the threads exited
        for th in self.email_validator._workers.values():
            self.assertFalse(th['running'])

    @patch('Products.NaayaCore.EmailTool.EmailValidator.validate_email')
    def test_enqueue_retry(self, mock_validate_email):
        self.setUp(1)
        # make resolvation function return invalid for nr of retries - 1
        return_sequence = [False] * EmailValidator.VALIDATION_ATTEMPTS
        return_sequence[-1] = True
        mock_validate_email.side_effect = return_sequence

        email = 'newInvalidOne@edw.ro'
        self.email_validator.enqueue(email)
        time.sleep(0.1)
        self.assertTrue(self.email_validator.validate_from_cache(email))

