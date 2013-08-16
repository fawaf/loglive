from zmq.eventloop import ioloop
ioloop.install()


import zmq
from loglive import config
from tornado.web import URLSpec
from tornado.websocket import WebSocketHandler
from zmq.eventloop.zmqstream import ZMQStream


class LiveLogHandler(WebSocketHandler):
    """
    Handles websocket connections for viewing live updates to logs.
    Listens to localhost on the ZEROMQ_PORT defined in config.

    Subscribes to messages published on ZeroMQ that start with
    "NetworkName~ChannelName".
    """
    def open(self, network, channel):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(config.ZEROMQ_ENDPOINT)
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


handlers = [
            URLSpec(r'/(?P<network>[^/]+)/(?P<channel>[^/]+)/live', LiveLogHandler, name="live_log"),
            ]
