from datetime import datetime as dt
from tornado.web import RequestHandler, URLSpec
from loglive.lib import user_can_access_channel
from loglive.models import IrcNetwork


class LogLiveRequestHandler(RequestHandler):
    def get_user(self):
        """
        Returns the identifier for the current user, which is used
        in the access control lists
        """
        return self.get_secure_cookie('email')

    def get_network_or_404(self, network_name):
        """
        Returns an IrcNetwork for the given network name, or raises 404
        """
        try:
            network = IrcNetwork.get(network_name)
        except ValueError:
            self.send_error(status_code=404)
        return network

    def get_channel_or_404(self, network, channel_name):
        """
        Returns an IrcChannel for the given IrcNetwork and channel name,
        or raises 404
        """
        channel = network.get_channel(channel_name)
        if not channel:
            self.send_error(status_code=404)
        return channel


class NetworkListHandler(LogLiveRequestHandler):
    def get(self):
        networks = IrcNetwork.all()
        ret = list()
        for network in networks:
            ret.append({'name': network.name})
        self.write({'networks': ret})


class NetworkDetailHandler(LogLiveRequestHandler):
    def get(self, network_name):
        network = self.get_network_or_404(network_name)
        user = self.get_user()
        channel_names = sorted(channel.name for channel
                               in network.get_channels()
                               if user_can_access_channel(user,
                                                          network_name,
                                                          channel.name))

        ret = {'name': network_name,
               'channels': [{'name': channel_name} for channel_name
                            in channel_names]}
        self.write(ret)


class ChannelDetailHandler(LogLiveRequestHandler):
    def get(self, network_name, channel_name):
        network = self.get_network_or_404(network_name)
        channel = self.get_channel_or_404(network, channel_name)
        user = self.get_user()
        if not user_can_access_channel(user, network_name, channel_name):
            self.send_error(status_code=403)

        logs = sorted(log.date.strftime("%Y-%m-%d") for log in channel.get_logs())
        ret = {'name': channel_name,
               'network': network.name,
               'logs': logs}
        self.write(ret)


class LogDetailHandler(LogLiveRequestHandler):
    def get(self, network_name, channel_name, date_string):
        network = self.get_network_or_404(network_name)
        channel = self.get_channel_or_404(network, channel_name)
        user = self.get_user()

        if not user_can_access_channel(user, network_name, channel_name):
            self.send_error(status_code=403)

        try:
            date = dt.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            self.send_error(status_code=404)

        log = channel.get_log(date)
        with open(log.path, "r") as f:
            lines = [line for line in f]
        ret = {'date': date_string,
               'channel': channel_name,
               'network': network_name,
               'lines': lines}
        self.write(ret)


handlers = [
            URLSpec(r'/api/networks\.json',
                    NetworkListHandler),
            URLSpec(r'/api/networks/(?P<network_name>[^/]+).json',
                    NetworkDetailHandler),
            URLSpec(r'/api/networks/(?P<network_name>[^/]+)/(?P<channel_name>[^/]+).json',
                    ChannelDetailHandler),
            URLSpec(r'/api/networks/(?P<network_name>[^/]+)/(?P<channel_name>[^/]+)/(?P<date_string>\d{4}-\d{2}-\d{2}).json',
                    LogDetailHandler),
            ]
