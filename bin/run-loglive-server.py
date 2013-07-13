#!/usr/bin/env python
from loglive import config
from loglive.web import application
import tornado.ioloop


if __name__ == "__main__":
    application.listen(config.TORNADO_PORT)
    tornado.ioloop.IOLoop.instance().start()
