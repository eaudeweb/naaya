import logging
import traceback
from naaya.i18n.patches import get_request


log = logging.getLogger('naaya.i18n')


def update_transaction_note(*args):
    import transaction, re

    def label_with_count(count):
        return "(Saving %d new i18n messages)" % count
    def increment_count(match):
        return label_with_count(int(match.group('count')) + 1)
    p = re.compile(r'\(Saving (?P<count>\d+) new i18n messages\)')

    t = transaction.get()
    if p.search(t.description) is None:
        t.note(label_with_count(0))
    t.description = p.sub(increment_count, t.description)


def debug_messages(event):
    request = get_request()
    if not hasattr(request, 'PARENTS'): # wsgi request?
        return
    if not hasattr(request.PARENTS[0], 'getSite'): # Zope root?
        return
    portal_i18n = request.PARENTS[0].getSite()['portal_i18n']
    for pattern in portal_i18n.message_debug_list:
        if pattern in event.msgid:
            msg = "found problematic message %r" % event.msgid
            if portal_i18n.message_debug_exception:
                raise ValueError(msg)
            stack = ''.join(traceback.format_stack())
            log.warn("%r - %s.\n\nstack:\n%s", msg, portal_i18n, stack)
        break
