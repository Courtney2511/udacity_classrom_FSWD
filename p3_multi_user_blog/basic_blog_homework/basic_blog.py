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


class Post(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class MainPage(Handler):

    def render_index(self, title="", post="", error=""):
        posts = db.GqlQuery("SELECT * from Post ORDER BY created DESC")
        self.render("index.html", title=title, post=post, error=error,
                    posts=posts)

    def get(self):
        self.render_index()


class NewPost(Handler):

    def get(self):
        self.render("newpost.html")

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost)
                               ], debug=True)
