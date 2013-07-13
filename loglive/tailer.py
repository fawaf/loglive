from collections import defaultdict, namedtuple
from datetime import datetime as dt
import os
from pprint import pprint
import pyinotify
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


class NetworkDirectoryEventHandler(pyinotify.ProcessEvent):
    def my_init(self, network, channel_files, callback):
        self.network = network
        self.callback = callback

        self.channel_fh = dict()
        for (channel, files) in channel_files.iteritems():
            latest_file = files[-1]
            fh = open(latest_file.path, 'r')
            fh.seek(0, os.SEEK_END)
            self.channel_fh[channel] = fh

    def process_IN_CREATE(self, event):
        pathname = event.pathname
        log_file = parse_log_filename(pathname)
        if not log_file:
            return
        if log_file.path in self.channel_fh:
            self.channel_fh.close()
        fh = open(event.pathname, 'r')
        self.channel_fh[log_file.channel] = fh

    def process_IN_MODIFY(self, event):
        log_file = parse_log_filename(event.pathname)
        if not log_file:
            return

        content = self.channel_fh[log_file.channel].read()
        self.callback(self.network, log_file.channel, content)


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


class LogTailer(object):
    def __init__(self, network_log_dirs, callback):
        self.notifier = None
        self.wm = pyinotify.WatchManager()
        self.callback = callback

        mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY

        for (network, directory) in network_log_dirs.iteritems():
            if not os.path.isdir(directory):
                continue

            channel_files = defaultdict(lambda: list())
            log_files = sorted(get_log_files(directory),
                               key=lambda f: f.date)
            for f in log_files:
                channel_files[f.channel].append(f)
            proc_fun = NetworkDirectoryEventHandler(
                network=network,
                channel_files=channel_files,
                callback=callback)
            self.wm.add_watch(directory,
                         mask,
                         proc_fun=proc_fun)

        self.notifier = pyinotify.ThreadedNotifier(self.wm)

    def loop(self):
        self.notifier.loop()
