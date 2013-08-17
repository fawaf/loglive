from tornado.web import RequestHandler, URLSpec


class FrontPageHandler(RequestHandler):
    def get(self, *args, **kwargs):
        template = 'index.html'
        return self.render(template)


handlers = [
            URLSpec(r'/', FrontPageHandler, name="front_page"),
            ]
