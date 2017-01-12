import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# Basic Handler class
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):

    def render_index(self, title="", post="", error=""):
        self.render("index.html", title=title, post=post, error=error)

    def get(self):
        self.render_index()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            self.write("Thanks!")
        else:
            error = "Entry must have a title and a body!"
            self.render_index(title, post, error)

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
