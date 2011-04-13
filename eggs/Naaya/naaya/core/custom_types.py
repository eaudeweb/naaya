# Python imports
from datetime import datetime
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass


class Interval(tuple):
    """ Immutable type representing two datetime intervals and all_day option"""

    security = ClassSecurityInfo()

    def __new__(cls, start_date=None, start_time = None, end_date=None,
                end_time = None, all_day=False):
        if start_date is end_date is None:
            pass
        elif None in (start_date, end_date):
            raise ValueError('Start time (date) and End time (date) '
                             'must both have values')
        elif all_day is False and None in (start_time, end_time):
            raise ValueError('Start time (hh:mm) and End time (hh:mm) '
                             'must both have values when all_day is False')
        else:
            def normalize_date(date, time, all_day, name):
                try:
                    ds = map(int, date.split("/"))
                    if all_day is True:
                        return datetime(ds[2], ds[1], ds[0])
                    else:
                        (h, m) = map(int, time.split(":"))
                        return datetime(ds[2], ds[1], ds[0], h, m)
                except Exception, e:
                    raise ValueError('Bad value (%s, %s) for %s' % (repr(date),
                                                                    repr(time),
                                                                    name))
            start_date = normalize_date(start_date, start_time, all_day,
                                        'Start Time')
            end_date = normalize_date(end_date, end_time, all_day, 'End Time')
            if start_date > end_date:
                raise ValueError('End time can not precede start time')

        return tuple.__new__(cls, (start_date, end_date, all_day))


    security.declarePublic('start_date')
    @property
    def start_date(self):
        return self[0]

    security.declarePublic('end_date')
    @property
    def end_date(self):
        return self[1]

    security.declarePublic('all_day')
    @property
    def all_day(self):
        return self[2]

    def __repr__(self):
        data = {
            'start_date': self.start_date.strftime("%d/%m/%Y"),
            'end_date': self.end_date.strftime("%d/%m/%Y"),
            'start_time': self.start_date.strftime("%H:%M"),
            'end_time': self.end_date.strftime("%H:%M"),
            'all_day': repr(self.all_day),
        }
        return ("Interval:[%(start_date)s, %(start_time)s - "
                "%(end_date)s, %(end_time)s; All day: %(all_day)s]"
                % data)

InitializeClass(Interval)
