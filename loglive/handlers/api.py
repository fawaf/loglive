from tornado.web import RequestHandler, URLSpec
from loglive.models import IrcNetwork

class NetworksHandler(RequestHandler):
    def get(self):
        networks = IrcNetwork.all()
        ret = list()
        for network in networks:
            ret.append({'name': network.name})
        self.write({'networks': ret})

handlers = [
            URLSpec('/api/networks.json', NetworksHandler),
            ]
