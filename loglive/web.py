from loglive import config
from loglive.logs import get_log_files_by_channel
from tornado.web import RequestHandler, Application, HTTPError
import os




class NetworkListingHandler(RequestHandler):
    def get(self):
        self.write(",".join(config.NETWORK_DIRECTORIES.keys()))

class ChannelListingHandler(RequestHandler):
    def get(self, network):
        if network not in config.NETWORK_DIRECTORIES:
            raise HTTPError(404, "{0} not a valid network".format(network))
        self.write(network)
        directory = config.NETWORK_DIRECTORIES[network]
        channels = get_log_files_by_channel(directory)
        self.write(",".join(channels))

class ChannelHandler(RequestHandler):
    def get(self, network, channel):
        if network not in config.NETWORK_DIRECTORIES:
            raise HTTPError(404, "{0} not a valid network".format(network))
        directory = config.NETWORK_DIRECTORIES[network]
        channels = get_log_files_by_channel(directory)
        if channel not in channels.keys():
            raise HTTPError(404, "{0} on {1} not a valid channel".format(
                channel, network))
        self.write(network + " ~ " + channel)

application = Application(
    handlers=[
        (r'/', NetworkListingHandler),
        (r'/([^/]+)', ChannelListingHandler),
        (r'/([^/]+)/([^/]+)/', ChannelHandler),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static")
)
