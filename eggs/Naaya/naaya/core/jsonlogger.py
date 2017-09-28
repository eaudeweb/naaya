import logging
import re
from backport import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    A custom formatter to format logging records as JSON objects

    """

    def parse(self):
        standard_formatters = re.compile(r'\((.*?)\)', re.IGNORECASE)
        return standard_formatters.findall(self._fmt)

    def format(self, record):
        """
        Formats a log record and serializes to JSON

        """

        mappings = {
            'asctime': create_timestamp,
            'message': lambda record: record.msg,
        }

        formatters = self.parse()

        log_record = {}
        for formatter in formatters:
            try:
                log_record[formatter] = mappings[formatter](record)
            except KeyError:
                log_record[formatter] = record.__dict__[formatter]

        return json.dumps(log_record)

def create_timestamp(record):
    """
    Creates a human readable timestamp for a log records created date

    """

    timestamp = datetime.fromtimestamp(record.created)
    return timestamp.strftime("%y-%m-%d %H:%M:%S,%f")
