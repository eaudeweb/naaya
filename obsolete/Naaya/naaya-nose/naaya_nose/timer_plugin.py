from time import time
from nose.plugins import Plugin

class Timer(Plugin):
    """ Time duration of each test and show top 10 slowest tests. """

    def configure(self, options, config):
        super(Timer, self).configure(options, config)
        if self.enabled:
            self.timer_results = []

    def startTest(self, test):
        self.t0 = time()

    def afterTest(self, test):
        if not hasattr(self, 't0'):
            return
        self.timer_results.append(((time() - self.t0), str(test)))
        del self.t0

    def finalize(self, result):
        print("\nSlowest tests:")
        top_10 = sorted(self.timer_results, reverse=True)[:10]
        for duration, test_name in top_10:
            print("%.2f %s" % (duration, test_name))
