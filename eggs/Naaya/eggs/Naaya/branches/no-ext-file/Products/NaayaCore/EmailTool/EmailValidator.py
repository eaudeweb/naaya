import time
import logging
LOG = logging.getLogger(__name__)
from threading import Thread, Lock, Semaphore
from Products.NaayaCore.EmailTool.SharedSet import SharedSet, Full, Empty

from validate_email import validate_email

import transaction

class EmailValidator(object):
    """Runs mail addresses through validate_email lib using detached threads
    to parallelize this action and not keep the curent op waiting in I/O
    Make sure to use bind() befaore enqueue() so that the result can be stored
    asynchronously. outputObj must have a dict like property named by string
    storage_name."""

    # Note that while we avoid most of the duplicate validations,
    # they may still occur when one thread spends time waiting for validation,
    # email was thus removed from Q, and some client js asks for the same email
    # to be validated (it willnot be a Q duplicate,
    # another thread will pick it up, it will not find it in the cache
    # and will start validating it). This is benign however.
    VERIFY_EMAIL_BADADDRESS_TTL = (24 * 60 * 60)
    VERIFY_EMAIL_GOODADDRESS_TTL = (30 * 24 * 60 * 60)
    THREAD_IDLE_SEC = 60
    VALIDATION_ATTEMPTS = 3 # number of consecutive attempt to avoid false negatives

    def __init__(self, storage_name, maxWorkers=10, maxPoolSize=4000):
        self._outputObj = None
        # FIXME this is a per _outputObj lock, and should depend on it
        # while we can chenge the _outputObj, we still share the same lock
        # but we are going to use only the portal level object anyway
        # and yes, this is not encapsulation friendly;
        # perhaps the storing obj should live here?
        self._outputObjLock = Lock()
        self._storage_name = storage_name
        self._workersLock = Lock()
        self._workers = {}
        self._workerCountSemaphore = Semaphore(maxWorkers)
        self._seq = 0   # this will only grow
        self._inQ = SharedSet(maxPoolSize)

    def _setupWorkers(self):
        while self._workerCountSemaphore.acquire(False):
            name = "emailValidationThread_%d"%self._seq
            self._workersLock.acquire()
            self._workers[name] = {'th': Thread(
                target=EmailValidator._worker, name=name, args=(self,name)),
                                  'running': None}
            self._workersLock.release()
            self._seq += 1

        self._workersLock.acquire()
        # Altering dict size during iteration; avoid generator based iterators
        for name, th in self._workers.items():
            if th['running'] is None:
                th['th'].daemon = True
                th['th'].start()
                th['running'] = True
            if th['running'] is False:
                del self._workers[name]
        self._workersLock.release()

    def bind(self, outputObj):
        if not hasattr(outputObj, self._storage_name):
            raise RuntimeError("{} instance should be bound to an object containing {}"
                " PersistentMapping".format(self.__class__.__name__, self._storage_name))
        self._outputObj = outputObj

    def validate_from_cache(self, email):
        now = time.time()
        check_value, check_ts = getattr(self._outputObj, self._storage_name).get(email, (None, None));
        if ( check_value is None
            or (check_value is False and check_ts < now - self.VERIFY_EMAIL_BADADDRESS_TTL)
            or (check_value is True and check_ts < now - self.VERIFY_EMAIL_GOODADDRESS_TTL) ):
            return None
        return check_value


    def enqueue(self, email):
        if not self._outputObj:
            raise RuntimeError("{} instance should be bound to an object containing {}"
                " PersistentMapping".format(self.__class__.__name__, self._storage_name))
        self._setupWorkers()
        try:
            self._inQ.put_nowait(email)
        except Full:
            LOG.warn("input validate mail queue full. %s will not be resolved now" % email)

    def _worker(self, name):
        LOG.debug("new thread started: %s" % name)
        while True:
            try:
                email = self._inQ.get(True, self.THREAD_IDLE_SEC)
            except Empty:
                break
            check_value = self.validate_from_cache(email)
            if check_value is None:
                for i in range(self.VALIDATION_ATTEMPTS):
                    # long I/O bound operation
                    try:
                        check_value = validate_email(email, verify=True)
                    except:
                        check_value = False
                    if check_value:
                        break

                self._outputObjLock.acquire()
                now = time.time()
                getattr(self._outputObj, self._storage_name)[email] = (check_value, now)
                transaction.commit()
                self._outputObjLock.release()
            self._inQ.task_done()
        self._workersLock.acquire()
        self._workers[name]['running'] = False
        self._workersLock.release()
        LOG.debug("thread exits after %d seconds idle: %s" % (self.THREAD_IDLE_SEC, name))
        self._workerCountSemaphore.release()

