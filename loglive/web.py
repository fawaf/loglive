from loglive import config
from loglive.logs import get_log_files_by_channel
from tornado.web import RequestHandler, Application, HTTPError, URLSpec
import os


class NetworkListingHandler(RequestHandler):
    def get(self):
        networks = config.NETWORK_DIRECTORIES.keys()
        self.render("networks_list.html", networks=networks)

class ChannelListingHandler(RequestHandler):
    def get(self, network):
        networks = config.NETWORK_DIRECTORIES.keys()
        if network not in networks:
            raise HTTPError(404, "{0} not a valid network".format(network))
        directory = config.NETWORK_DIRECTORIES[network]
        channels = get_log_files_by_channel(directory)
        self.render("channels_list.html",
                    networks=networks,
                    network=network,
                    channels=channels)

class ChannelHandler(RequestHandler):
    def get(self, network, channel):
        networks = config.NETWORK_DIRECTORIES.keys()
        if network not in networks:
            raise HTTPError(404, "{0} not a valid network".format(network))
        directory = config.NETWORK_DIRECTORIES[network]
        channels = get_log_files_by_channel(directory)
        if channel not in channels.keys():
            raise HTTPError(404, "{0} on {1} not a valid channel".format(
                channel, network))
        self.render("channel.html",
                    networks=networks,
                    network=network,
                    channel=channel)

application = Application(
    handlers=[
        URLSpec(r'/', NetworkListingHandler, name="network_listing"),
        URLSpec(r'/([^/]+)', ChannelListingHandler, name="channel_listing"),
        URLSpec(r'/([^/]+)/([^/]+)/', ChannelHandler, name="channel"),
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static")
)
