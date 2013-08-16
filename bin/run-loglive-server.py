#!/usr/bin/env python
from loglive import config
from loglive.app import LogLiveApplication, LogTailer
from tornado.httpserver import HTTPServer
import tornado.ioloop
import zmq


if __name__ == "__main__":
    server = HTTPServer(LogLiveApplication())
    server.listen(config.TORNADO_PORT)

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(config.ZEROMQ_ENDPOINT)

    ioloop = tornado.ioloop.IOLoop.instance()
    tailer = LogTailer(ioloop, socket)

    ioloop.start()
