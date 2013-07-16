#!/usr/bin/env python
from loglive import config
from loglive.tailer import LogTailer
from loglive.web import application
from tornado.httpserver import HTTPServer
import tornado.ioloop
import zmq


def make_log_tailer_callback(socket):
    def callback(network, channel, content):
        socket.send("{network}~{channel}\n{message}".format(
            network=network,
            channel=channel,
            message=content))
    return callback


if __name__ == "__main__":
    server = HTTPServer(application)
    server.listen(config.TORNADO_PORT)

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:{0}".format(config.ZEROMQ_PORT))

    ioloop = tornado.ioloop.IOLoop.instance()

    tailer = LogTailer(config.NETWORK_DIRECTORIES,
                       ioloop,
                       make_log_tailer_callback(socket))
    ioloop.start()
