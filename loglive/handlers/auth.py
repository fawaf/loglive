from tornado.auth import GoogleMixin
from tornado.gen import coroutine
from tornado.web import asynchronous, RequestHandler, URLSpec


class GoogleLoginHandler(RequestHandler, GoogleMixin):
    @asynchronous
    @coroutine
    def get(self):
        if self.get_argument("openid.mode", None):
            user = yield self.get_authenticated_user()
            self.set_secure_cookie('email', user['email'])
        else:
            yield self.authenticate_redirect()


handlers = [
            URLSpec(r'/login', GoogleLoginHandler, name="login"),
            ]

