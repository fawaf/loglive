import os
from loglive import config
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
            raise ValueError("Directory {0} isn't a valid log directory".\
                             format(directory))

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
        Generator of IrcChannel objects for this network, one object per
        channel
        """
        seen_channel_names = set()
        for path in self.get_log_filepaths():
            log_meta = parse_log_filename(path)
            if log_meta.channel in seen_channel_names:
                continue
            seen_channel_names.add(log_meta.channel)
            yield IrcChannel(self, log_meta.channel)

    @classmethod
    def all(cls):
        """
        Generator of all IrcNetwork objects, based on NETWORK_DIRECTORIES
        """
        for (name, directory) in config.NETWORK_DIRECTORIES.iteritems():
            try:
                network = cls(name, directory)
            except ValueError:
                # the directory didn't exist, or there was some other error
                continue
            yield network

    @classmethod
    def get(cls, network_name):
        """
        Returns an IrcNetwork for the given network name if it's a key in
        NETWORK_DIRECTORIES, else returns None
        """
        if network_name not in config.NETWORK_DIRECTORIES:
            return None
        return cls(network_name, config.NETWORK_DIRECTORIES[network_name])

    def get_channel(self, channel_name):
        """
        Returns an IrcChannel object for the given channel_name if it exists,
        else None
        """
        for channel in self.get_channels():
            if channel.name == channel_name:
                return channel
        return None


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
        sorted by decreasing date (newest first)
        """
        logs = list()
        for path in self.network.get_log_filepaths():
            log_meta = parse_log_filename(path)
            if not log_meta.channel == self.name:
                continue
            logs.append(IrcLog(self,
                               log_meta.date,
                               path))
        return sorted(logs, key=lambda log: log.date, reverse=True)

    def get_log(self, date):
        """
        Returns the IrcLog object of the log file with the specified date,
        else None
        """
        for log in self.get_logs():
            if log.date == date:
                return log
        return None

    def get_latest_log(self):
        """
        Returns the IrcLog object of the latest (newest) log file, else None
        """
        logs = self.get_logs()
        if len(logs):
            return logs[0]
        return None


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
