import re
import time

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)
def form_validation (mandatory_fields=[], date_fields=[], time_fields=[],
                    number_fields=[], pair_fields=[[]], email_fields=[], REQUEST=None):
    has_errors = False
    req = REQUEST.form
    #@TODO reverse cycling oder mandatory_fields --> REQUEST.form
    for k,v in req.items():
        if k in mandatory_fields and (k in number_fields and v=='0' or not v):
            REQUEST.set('%s_error' % k, True)
            has_errors = True
        if 'email' in k and v:
            if not email_expr.match(v):
                REQUEST.set('%s_notvalid' % k, True)
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
        if k in number_fields and v:
            try:
                temp = float(v)
            except:
                REQUEST.set('%s_notvalid' % k, True)
                has_errors = True
        for pair in pair_fields:
            if k in pair and (not v or v=='0'):
                if req.get(pair[1-pair.index(k)])!='0':
                    REQUEST.set('%s_error' % k, True)
                    has_errors = True
    total_requested = req.get('total_requested')
    total_own = req.get('total_own')
    try:
        total_requested = float(total_requested)
        if not (total_requested > 0):
            REQUEST.set('total_requested_error', True)
            has_errors = True
    except:
        REQUEST.set('total_requested_notvalid', True)
        has_errors = True
    try:
        total_own = float(total_own)
        if not (total_own > 0):
            REQUEST.set('total_own_error', True)
            has_errors = True
    except:
        REQUEST.set('total_own_notvalid', True)
        has_errors = True
    try:
        total_requested = float(total_requested)
        total_own = float(total_own)
        percentage = total_own/(total_own + total_requested)
        if percentage < 0.6:
            percentage = '%s%%' % percentage * 100
            REQUEST.set('percentage_error', percentage)
            has_errors = True
    except:
        pass
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors


def registration_validation(mandatory_fields, date_fields, time_fields, REQUEST):
    """ Validates the new meeting registration fields """
    has_errors = False

    for k,v in REQUEST.form.items():
        if k in mandatory_fields and not v:
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

    administrative_email = REQUEST.form.get('administrative_email', '')
    if administrative_email and not has_errors:
        for email_address in administrative_email:
            if email_address and not email_expr.match(email_address):
                REQUEST.set('administrative_email_notvalid', True)
                has_errors = True

    start_date = REQUEST.form.get('start_date', '')
    end_date = REQUEST.form.get('end_date', '')
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