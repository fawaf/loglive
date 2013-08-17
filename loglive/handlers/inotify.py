import os
import pyinotify
from collections import namedtuple


class NetworkDirectoryInotifyHandler(pyinotify.ProcessEvent):
    def my_init(self, network, callback):
        self.network = network
        self.callback = callback

        self.channel_positions = dict()
        # initalize with the end positions for each existing channel's
        # latest log file

        for channel in network.get_channels():
            log = channel.get_latest_log()
            position = 0
            with open(log.path, 'r') as fh:
                fh.seek(0, os.SEEK_END)
                position = fh.tell()
            self.channel_positions[channel.name] = position

    def process_IN_CREATE(self, event):
        """
        Whenever we see a CREATE for a file with a filename that fits the
        log file pattern, we assume it's the creation of the next log file
        without checking for the log file's date.
        """
        pathname = event.pathname
        log_meta = parse_log_filename(pathname)
        if not log_meta:
            return
        self.channel_positions[log_meta.channel] = 0

    def process_IN_MODIFY(self, event):
        """
        Whenever we see a MODIFY on a file with a filename that fits the log
        file pattern, we assume it was a write. We then call the callback
        with arguments:
            network name
            channel name
            new content appended to the file
        """
        log_meta = parse_log_filename(event.pathname)
        if not log_meta:
            return
        with open(event.pathname, "r") as fh:
            fh.seek(self.channel_positions[log_meta.channel])
            content = fh.read()
            self.channel_positions[log_meta.channel] = fh.tell()

        self.callback(self.network, log_file.channel, content)
