import functools
import re
import os
from collections import namedtuple
from datetime import datetime as dt


LOG_FILENAME_REGEX = r'^(#?[^\.\_]+)_(\d{8}).log$'
LogFileMeta = namedtuple('LogFileMeta', ['channel', 'date'])


def memoize(f):
    """
    Memoize function results based on the *args to that function,
    ignoring **kwargs
    """
    cache = dict()

    @functools.wraps(f)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = f(*args, **kwargs)
        return cache[args]
    return memoizer


@memoize
def parse_log_filename(file_path):
    """
    Given a file path of a log file, it parses the channel and date
    and returns it in a LogFileMeta namedtuple.

    If the filename doesn't match the known format, returns None.
    """
    filename = os.path.basename(file_path)
    match = re.match(LOG_FILENAME_REGEX, filename)
    if not match:
        return None
    (channel, date) = match.groups()
    return LogFileMeta(channel=channel,
                       date=dt.strptime(date, '%Y%m%d').date())

