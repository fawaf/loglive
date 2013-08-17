import os
import pyinotify
from loglive import config
from loglive.handlers import auth, front
from loglive.handlers.inotify import NetworkDirectoryInotifyHandler
from loglive.models import IrcNetwork
from tornado.web import Application


class LogLiveApplication(Application):
    def __init__(self):
        kwargs = {
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
            'static_path': os.path.join(os.path.dirname(__file__), "static"),
            'cookie_secret': config.COOKIE_SECRET,
            'login_url': '/login',
        }
        handlers = list()
        for handler_module in [auth, front]:
            handlers.extend(handler_module.handlers)
        kwargs['handlers'] = handlers

        super(LogLiveApplication, self).__init__(**kwargs)


class LogTailer(object):
    def __init__(self, ioloop, socket):
        self.wm = pyinotify.WatchManager()
        self.callback = self.make_callback(socket)

        mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY

        for network in IrcNetwork.all():
            proc_fun = NetworkDirectoryInotifyHandler(
                network=network,
                callback=self.callback)
            self.wm.add_watch(network.directory,
                              mask,
                              proc_fun=proc_fun)

        self.notifier = pyinotify.TornadoAsyncNotifier(self.wm, ioloop)

    def make_callback(self, socket):
        def callback(network, channel, content):
            socket.send("{network}~{channel}\n{message}".format(
                network=network,
                channel=channel,
                message=content))
        return callback

    #handlers=[
    #    URLSpec(r'/', MainHandler, name="network_listing"),
    #    URLSpec(r'/login', GoogleLoginHandler, name="login"),
    #    URLSpec(r'/(?P<network>[^/]+)/?', NetworkHandler, name="network"),
    #    URLSpec(r'/(?P<network>[^/]+)/(?P<channel>[^/]+)/', ChannelHandler, name="channel"),
    #    URLSpec(r'/(?P<network>[^/]+)/(?P<channel>[^/]+)/(?P<date_string>\d{8})', LogHandler, name="log"),
    #    URLSpec(r'/(?P<network>[^/]+)/(?P<channel>[^/]+)/live', LiveLogHandler, name="live_log"),
    #],
