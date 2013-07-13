#!/usr/bin/env python
from loglive import config
from loglive.web import application
from tornado.httpserver import HTTPServer
import tornado.ioloop


if __name__ == "__main__":
    server = HTTPServer(application)
    server.listen(config.TORNADO_PORT)
    tornado.ioloop.IOLoop.instance().start()
