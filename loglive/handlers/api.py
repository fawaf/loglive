from tornado.web import RequestHandler, URLSpec
from loglive.models import IrcNetwork

class NetworkListHandler(RequestHandler):
    def get(self):
        networks = IrcNetwork.all()
        ret = list()
        for network in networks:
            ret.append({'name': network.name})
        self.write({'networks': ret})


class NetworkDetailHandler(RequestHandler):
    def get(self, network_name):
        try:
            network = IrcNetwork.get(network_name)
        except ValueError:
            self.send_error(status_code=404)
        channel_names = sorted(channel.name for channel
                               in network.get_channels())

        ret = {'name': network_name,
               'channels': [{'name': channel_name} for channel_name
                            in channel_names]}
        self.write(ret)

handlers = [
            URLSpec(r'/api/networks\.json', NetworkListHandler),
            URLSpec(r'/api/networks/(?P<network_name>[^/]+).json', NetworkDetailHandler),
            ]
