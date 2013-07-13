#!/usr/bin/env python
from loglive import config
from loglive.tailer import LogTailer
from tornado.escape import json_encode
import zmq


def make_log_tailer_callback(socket):
    def callback(network, channel, content):
        socket.send("{network}~{channel}\n{message}".format(
            network=network,
            channel=channel,
            message=content))
    return callback


if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:{0}".format(config.ZEROMQ_PORT))

    tailer = LogTailer(config.NETWORK_DIRECTORIES,
                       make_log_tailer_callback(socket))

    while True:
        tailer.loop()
