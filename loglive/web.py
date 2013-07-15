from zmq.eventloop import ioloop
ioloop.install()

from datetime import datetime as dt
import functools
from loglive import config
from loglive.formatters import irc_format
from loglive.logs import get_log_files_by_channel
from tornado.options import define, options
from tornado.web import RequestHandler, Application, HTTPError, URLSpec
from tornado.websocket import WebSocketHandler
import os
import zmq
from zmq.eventloop.zmqstream import ZMQStream


def get_available_networks():
    return config.NETWORK_DIRECTORIES.keys()


def get_logs_directory(network):
    return config.NETWORK_DIRECTORIES.get(network, list())


def require_network_exists(func):
    """
    Raises 404 if the function isn't called with a valid "network" parameter.

    This decorator injects:
        - logs_directory: the path to the directory that has the logs for this network
        - logs by channel: a dictionary mapping of this network's channels to
                           a sorted list of logs for that channel
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        network = kwargs.get('network', None)
        available_networks = get_available_networks()
        if not network or network not in available_networks:
            raise HTTPError(404, "{0} not a valid network".format(network))
        kwargs['logs_directory'] = get_logs_directory(network)
        kwargs['logs_by_channel'] = get_log_files_by_channel(kwargs['logs_directory'])
        return func(*args, **kwargs)
    return wrapper

def require_channel_exists(func):
    """
    Raises 404 if the function isn't called with 'network' and 'channel' params
    where there exist logs for 'channel' for that 'network'.

    Be sure this is called after @requires_network_exists
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logs_by_channel = kwargs['logs_by_channel']
        if kwargs['channel'] not in logs_by_channel.keys():
            raise HTTPError(404,
                            "{channel} on {network} does not have any logs".\
                            format(
                                channel=kwargs['channel'],
                                network=kwargs['network']))
        return func(*args, **kwargs)
    return wrapper



class NetworksListMixin(object):
    def render_with_networks(self, template, **kwargs):
        """
        Inject the list of available networks into the template, since
        almost every page needs it for the nav bar
        """
        kwargs['networks'] = get_available_networks()
        return self.render(template, **kwargs)


class MainHandler(RequestHandler, NetworksListMixin):
    def get(self):
        self.render_with_networks("networks_list.html")


class NetworkHandler(RequestHandler, NetworksListMixin):
    @require_network_exists
    def get(self, network, **kwargs):
        channels = get_log_files_by_channel(kwargs['logs_directory'])
        self.render_with_networks(
            "network.html",
            network=network,
            channels=channels)


class ChannelHandler(RequestHandler, NetworksListMixin):
    @require_network_exists
    @require_channel_exists
    def get(self, network, channel, **kwargs):
        logs = kwargs['logs_by_channel'][channel]
        self.render_with_networks(
            "channel.html",
            network=network,
            channel=channel,
            logs=logs)


class LogHandler(RequestHandler, NetworksListMixin):
    @require_network_exists
    @require_channel_exists
    def get(self, network, channel, date_string, **kwargs):
        channel_logs = kwargs['logs_by_channel'][channel]
        try:
            desired_date = dt.strptime(date_string, '%Y%m%d')
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
        enable_live_updates = index_of_desired_log == 0
        self.render_with_networks(
            "log.html",
            network=network,
            channel=channel,
            log=desired_log,
            previous_log=previous_log,
            next_log=next_log,
            enable_live_updates=enable_live_updates,
            irc_format=irc_format)


class LiveLogHandler(WebSocketHandler):
    def open(self, network, channel):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:{0}".format(config.ZEROMQ_PORT))
        self.socket.setsockopt(zmq.SUBSCRIBE, "{0}~{1}".format(network,channel))
        self.zmq_stream = ZMQStream(self.socket)
        self.zmq_stream.on_recv(self.on_zmq_msg_receive)

    def on_close(self):
        self.zmq_stream.close()
        self.socket.close()

    def on_zmq_msg_receive(self, data):
        data = data[0]
        lines = data.split("\n")[1:]
        self.write_message("\n".join([irc_format(line) for line in lines]))


application = Application(
    handlers=[
        URLSpec(r'/', MainHandler, name="network_listing"),
        URLSpec(r'/(?P<network>[^/]+)/?', NetworkHandler, name="network"),
        URLSpec(r'/(?P<network>[^/]+)/(?P<channel>[^/]+)/', ChannelHandler, name="channel"),
        URLSpec(r'/(?P<network>[^/]+)/(?P<channel>[^/]+)/(?P<date_string>\d{8})', LogHandler, name="log"),
        URLSpec(r'/(?P<network>[^/]+)/(?P<channel>[^/]+)/live', LiveLogHandler, name="live_log"),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static")
)
