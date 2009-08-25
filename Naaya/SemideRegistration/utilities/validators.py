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
    if administrative_email and not email_expr.match(administrative_email):
        REQUEST.set('administrative_email_invalid', True)
        has_errors = True
    if start_date:
        try:
            date = time.strptime(start_date, "%d/%m/%Y")
        except:
            REQUEST.set('start_date_invalid', True)
            has_errors = True
    if end_date:
        try:
            date = time.strptime(end_date, "%d/%m/%Y")
        except:
            REQUEST.set('end_date_invalid', True)
            has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors