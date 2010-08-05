import re
import time

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)
def form_validation (mandatory_fields, date_fields, time_fields, REQUEST):
    has_errors = False
    #@TODO reverse cycling oder mandatory_fields --> REQUEST.form
    for k,v in REQUEST.form.items():
        if k in mandatory_fields:
            if k == 'email' and v:
                if not email_expr.match(v):
                    REQUEST.set('%s_notvalid' % k, True)
                    has_errors = True
            if not v:
                REQUEST.set('%s_error' % k, True)
                has_errors = True
        if k in date_fields and v:
            try:
                temp = time.strptime(v, "%d/%m/%Y")
            except:
                REQUEST.set('%s_notvalid' % k, True)
                has_errors = True
        if k in time_fields and v:
            try:
                temp = time.strptime(v, "%H:%M")
            except:
                REQUEST.set('%s_notvalid' % k, True)
                has_errors = True

        event_1 = REQUEST.get('event_1', False)
        event_2 = REQUEST.get('event_2', False)
        event_3 = REQUEST.get('event_3', False)
        if event_3 and (event_1 or event_2):
            REQUEST.set('event_error', True)
            has_errors = True
        if event_2 and not event_1:
            REQUEST.set('event_error', True)
            has_errors = True
        if not (event_1 or event_2 or event_3):
            REQUEST.set('no_event_error', True)
            has_errors = True

        topic_1 = int(REQUEST.get('topic_1', False))
        topic_2 = int(REQUEST.get('topic_2', False))
        topic_3 = int(REQUEST.get('topic_3', False))
        topic_4 = int(REQUEST.get('topic_4', False))
        if topic_1 + topic_2 + topic_3 + topic_4 != 10:
            REQUEST.set('topic_error', True)
            has_errors = True

    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors


def registration_validation(REQUEST):
    """ Validates the new meeting registration fields """
    has_errors = False

    title = REQUEST.form.get('title', '')
    administrative_email = REQUEST.form.get('administrative_email', '')
    start_date = REQUEST.form.get('start_date', '')
    end_date = REQUEST.form.get('end_date', '')

    if not title:
        REQUEST.set('title_error', True)
        has_errors = True
    if not administrative_email:
        REQUEST.set('administrative_email_error', True)
        has_errors = True
    if not start_date:
        REQUEST.set('start_date_error', True)
        has_errors = True
    if not end_date:
        REQUEST.set('end_date_error', True)
        has_errors = True
    if administrative_email:
        for email_address in administrative_email:
            if email_address and not email_expr.match(email_address):
                REQUEST.set('administrative_email_invalid', True)
                has_errors = True
    if start_date:
        date = str2date(start_date)
        if date is None:
            REQUEST.set('start_date_invalid', True)
            has_errors = True
    if end_date:
        date = str2date(end_date)
        if date is None:
            REQUEST.set('end_date_invalid', True)
            has_errors = True
    if start_date and end_date and not has_errors:
        if str2date(start_date) > str2date(end_date):
            REQUEST.set('date_interval_invalid', True)
            has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

def str2date(s, format='%d/%m/%Y'):
    try:
        return time.strptime(s, format)
    except:
        return None