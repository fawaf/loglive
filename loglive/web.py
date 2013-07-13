from loglive import config
from loglive.logs import get_log_files_by_channel
from tornado.web import RequestHandler, Application





class NetworkListingHandler(RequestHandler):
    def get(self):
        self.write(",".join(config.NETWORK_DIRECTORIES.keys()))

class ChannelListingHandler(RequestHandler):
    def get(self, network):
        if network not in NETWORK_DIRECTORIES:
            self.send_error(404)
        self.write(network)

class ChannelHandler(RequestHandler):
    def get(self, network, channel):
        if network not in config.NETWORK_DIRECTORIES:
            self.send_error(404)
        directory = config.NETWORK_DIRECTORIES[network]
        channels = get_log_files_by_channel(directory)
        if channel not in channels:
            self.send_error(404)
        self.write(network + " ~ " + channel)

application = Application([
    (r'/', NetworkListingHandler),
    (r'/([^/]+)', ChannelListingHandler),
    (r'/([^/]+)/([^/]+)/', ChannelHandler),
])
