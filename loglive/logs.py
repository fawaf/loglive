from collections import defaultdict, namedtuple
import re


LOG_PATH_REGEX = r'^(#?[^\.\_]+)_(\d{8}).log$'
ChannelLogFile = namedtuple('ChannelLogFile', ['channel', 'date', 'filename', 'path'])


def parse_log_filename(file_path):
    filename = os.path.basename(file_path)
    match = re.match(LOG_PATH_REGEX, filename)
    if not match:
        return None
    (channel, date) = match.groups()
    return ChannelLogFile(path=file_path,
                          filename=filename,
                          channel=channel,
                          date=dt.strptime(date, '%Y%m%d'))


def get_log_files(directory):
    if not os.path.isdir(directory):
        return

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            continue
        log = parse_log_filename(file_path)
        if not log:
            continue
        yield log

def get_log_files_by_channel(directory):
    logs = sorted(get_log_files(directory), key=lambda f: f.date)
    files_by_channel = defaultdict(lambda: list())
    for log in logs:
        files_by_channel[log.channel].append(log)
    return files_by_channel
