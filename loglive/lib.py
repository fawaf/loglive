import functools
import re
import os
from collections import namedtuple
from datetime import datetime as dt
from tornado.web import HTTPError
from loglive import config

LOG_FILENAME_REGEX = r'^(#?[^\.\_]+)_(\d{8}).log$'
LogFileMeta = namedtuple('LogFileMeta', ['channel', 'date'])


def rule_wildcard_applies(rule_str, user_str):
    """
    If the rule_str is a wildcard, then it applies to all user_str.
    If the rule_str isn't a wildcard, then it only applies if it matches
    user_str.
    """
    if rule_str == "*":
        return True
    elif rule_str == user_str:
        return True
    return False


def __get_first_matching_rule(user, network, channel):
    for rule in config.ACCESS_RULES:
        # first, we check if the rule applies to this situation
        (rule_action, rule_user, rule_network, rule_channel) = rule
        if ((not rule_wildcard_applies(rule_user, user) or
             not rule_wildcard_applies(rule_network, network))):
            continue
        if not re.search(rule_channel, channel):
            continue
        return rule


def user_can_access_channel(user, network, channel):
    rule = __get_first_matching_rule(user, network, channel)
    action = rule[0]
    return action.upper() == "ALLOW"


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

