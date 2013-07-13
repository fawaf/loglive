from loglive.tailer import LogTailer
from tornado.escape import json_encode
import zmq


def make_log_tailer_callback(socket):
    def callback(network, channel, content):
        socket.send(json_encode({
            "network": network,
            "channel": channel,
            "content": content}))
    return callback


if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:33399")

    tailer = LogTailer({
        "Rizon": "~/.znc/users/rizon/moddata/log",
        }, make_log_tailer_callback(socket))

    while True:
        tailer.loop()
