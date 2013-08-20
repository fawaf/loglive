from tornado.web import RequestHandler, URLSpec
from loglive.lib import user_can_access_channel
from loglive.models import IrcNetwork


class LogLiveRequestHandler(RequestHandler):
    def get_user(self):
        return self.get_secure_cookie('email')


class NetworkListHandler(LogLiveRequestHandler):
    def get(self):
        networks = IrcNetwork.all()
        ret = list()
        for network in networks:
            ret.append({'name': network.name})
        self.write({'networks': ret})


class NetworkDetailHandler(LogLiveRequestHandler):
    def get(self, network_name):
        try:
            network = IrcNetwork.get(network_name)
        except ValueError:
            self.send_error(status_code=404)
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

handlers = [
            URLSpec(r'/api/networks\.json', NetworkListHandler),
            URLSpec(r'/api/networks/(?P<network_name>[^/]+).json', NetworkDetailHandler),
            ]
