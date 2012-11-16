import unittest
import mock
from time import time

import naaya.cache.cache as naaya_cache


class NaayaCacheTestCase(unittest.TestCase):

    def setUp(self):
        self._id = 'X'

    def tearDown(self):
        del self._id

    @naaya_cache.timed(10)
    def gonna_blow(self, when, message):
        left = when - time()
        return "%s: It's gonna blow in %.5f sec. %s" % (self._id, left, message)

    @naaya_cache.timed(10)
    def not_gonna_blow(self, when, message):
        return "%s: Different method, same args: %s" % (self._id, message)

    def test_timed_cache_memoization(self):
        """ test func and arguments memoization works """
        when = time() + 33.0
        first_call = self.gonna_blow(when, "Run for your life!")
        second_call = self.gonna_blow(when, "Run for your life!")
        self.assertEqual(first_call, second_call)
        changed_args = self.gonna_blow(when, "Wait a sec!")
        self.assertTrue(first_call != changed_args)
        same_args_other_method = self.not_gonna_blow(when, "Run for your life!")
        self.assertTrue(same_args_other_method != first_call)

    @mock.patch('time.time')
    def test_timed_cache_timeout(self, time_mock):
        """ test values expire after given timeout in cache """
        time_mock.return_value = 1000.00
        when = time() + 33.0
        first_call = self.gonna_blow(when, "Run for your life!")
        time_mock.return_value = 1001.00
        immediate_recall = self.gonna_blow(when, "Run for your life!")
        self.assertEqual(first_call, immediate_recall)
        time_mock.return_value = 1010.01
        later_recall = self.gonna_blow(when, "Run for your life!")
        self.assertTrue(first_call != later_recall)

    @mock.patch('time.time')
    def test_timed_cache_cleared(self, time_mock):
        """ Test old values in cache are cleared """
        time_mock.return_value = 1000.00
        when = time() + 33.0
        a_hit = self.gonna_blow(when, "Run for your life!")
        time_mock.return_value = 46001.00 # 1h later
        self.gonna_blow(when, "Run for your life!")
        time_mock.return_value = 1000.00 # back in time
        self._id = 'C'
        with_same_old_key = self.gonna_blow(when, "Run for your life!")
        self.assertTrue(a_hit != with_same_old_key)
