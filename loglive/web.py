from datetime import datetime as dt
from loglive import config
from loglive.formatters import irc_format
from loglive.logs import get_log_files_by_channel
from tornado.web import RequestHandler, Application, HTTPError, URLSpec
import os


class MainHandler(RequestHandler):
    def get(self):
        networks = config.NETWORK_DIRECTORIES.keys()
        self.render("networks_list.html", networks=networks)


class NetworkHandler(RequestHandler):
    def get(self, network):
        networks = config.NETWORK_DIRECTORIES.keys()
        if network not in networks:
            raise HTTPError(404, "{0} not a valid network".format(network))
        directory = config.NETWORK_DIRECTORIES[network]
        channels = get_log_files_by_channel(directory)
        self.render("network.html",
                    networks=networks,
                    network=network,
                    channels=channels)


class ChannelHandler(RequestHandler):
    def get(self, network, channel):
        networks = config.NETWORK_DIRECTORIES.keys()
        if network not in networks:
            raise HTTPError(404, "{0} not a valid network".format(network))
        directory = config.NETWORK_DIRECTORIES[network]
        logs_by_channel = get_log_files_by_channel(directory)
        if channel not in logs_by_channel.keys():
            raise HTTPError(404, "{0} on {1} not a valid channel".format(
                channel, network))
        logs = logs_by_channel[channel]
        self.render("channel.html",
                    networks=networks,
                    network=network,
                    channel=channel,
                    logs=logs)


class LogHandler(RequestHandler):
    def get(self, network, channel, datestring):
        networks = config.NETWORK_DIRECTORIES.keys()
        if network not in networks:
            raise HTTPError(404, "{0} not a valid network".format(network))
        directory = config.NETWORK_DIRECTORIES[network]
        logs_by_channel = get_log_files_by_channel(directory)
        if channel not in logs_by_channel.keys():
            raise HTTPError(404, "{0} on {1} not a valid channel".format(
                channel, network))
        channel_logs = logs_by_channel[channel]
        try:
            desired_date = dt.strptime(datestring, '%Y%m%d')
        except ValueError, e:
            raise HTTPError(404, "{0} not a valid date string".format(
                datestring))

        index_of_desired_log = None
        previous_log = None
        desired_log = None
        next_log = None

        reverse_sorted_logs = [x for x in reversed(channel_logs)]
        for (i, log) in enumerate(reverse_sorted_logs):
            # search for the log file in reverse chronological order
            # since newer logs will probably be most desired
            if log.date == desired_date:
                index_of_desired_log = i
                desired_log = log
                break
        if not desired_log:
            raise HTTPError(
                404,
                "Log for {channel} on {network} on {date} not found".format(
                    channel=channel, network=network, date=desired_dare))
        if (index_of_desired_log + 1) < len(reverse_sorted_logs):
            previous_log = reverse_sorted_logs[index_of_desired_log + 1]
        if index_of_desired_log > 0:
            next_log = reverse_sorted_logs[index_of_desired_log - 1]
        self.render("log.html",
                    networks=networks,
                    network=network,
                    channel=channel,
                    log=desired_log,
                    previous_log=previous_log,
                    next_log=next_log,
                    irc_format=irc_format)

application = Application(
    handlers=[
        URLSpec(r'/', MainHandler, name="network_listing"),
        URLSpec(r'/([^/]+)', NetworkHandler, name="network"),
        URLSpec(r'/([^/]+)/([^/]+)/', ChannelHandler, name="channel"),
        URLSpec(r'/([^/]+)/([^/]+)/(\d{8})', LogHandler, name="log"),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static")
)
