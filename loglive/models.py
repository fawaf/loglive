import os
from loglive.lib import parse_log_filename


class IrcNetwork(object):
    """
    Class to help retrieve each network's list of channels
    """
    def __init__(self, name, directory):
        """
        Constructor for IrcNetwork. If `directory` isn't a valid directory,
        then returns None
        """
        if not os.path.isdir(directory):
            return None

        self.name = name
        self.directory = directory

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<IrcNetwork '{0}'>".format(self.name)

    def get_log_filepaths(self):
        """
        Generator for file paths (not filenames) that match the pattern for logs
        """
        for filename in os.listdir(self.directory):
            path = os.path.join(self.directory, filename)
            if not os.path.isfile(path):
                continue
            log_meta = parse_log_filename(path)
            if not log_meta:
                continue
            yield path

    def get_channels(self):
        """
        Returns a list of IrcChannel objects for this network
        """
        channel_names = set()
        channels = list()
        for path in self.get_log_filepaths():
            log_meta = parse_log_filename(path)
            if log_meta.channel in channel_names:
                continue
            channel_names.add(log_meta.channel)
            channels.append(IrcChannel(self, log_meta.channel))
        return channels


class IrcChannel(object):
    """
    A specific channel or private messages to individual users
    on a specific server
    """
    def __init__(self, network, name):
        self.network = network
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<IrcChannel '{channel}' on '{network}'>".format(
            channel=self.name,
            network=self.network.name)

    def get_logs(self):
        """
        Returns a sorted list of IrcLog objects,
        sorted by increasing date (oldest first)
        """
        logs = list()
        for path in self.network.get_log_filepaths():
            log_meta = parse_log_filename(path)
            if not log_meta.channel == self.name:
                continue
            logs.append(IrcLog(self,
                               log_meta.date,
                               path))
        return sorted(logs, key=lambda log: log.date)


class IrcLog(object):
    """
    Object representing a single log file from a channel on a server
    """
    def __init__(self, channel, date, path):
        self.channel = channel
        self.date = date
        self.path = path

    def __str__(self):
        return self.path

    def __repr__(self):
        return "<IrcLog {network} {channel} {date}>".format(
            network=self.channel.network.name,
            channel=self.channel.name,
            date=self.date.strftime("%Y-%m-%d"))
