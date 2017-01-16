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


# Creates Post table
class Post(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)


# Main Page Handler
class MainPage(Handler):

    def render_index(self, title="", post="", error=""):
        posts = db.GqlQuery("SELECT * from Post ORDER BY created DESC")
        self.render("index.html", title=title, post=post, error=error,
                    posts=posts)

    def get(self):
        self.render_index()


# New Post Page Handler
class NewPost(Handler):

    def render_newpost(self, title="", post="", error=""):
        self.render("newpost.html", title=title, post=post, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("subject")
        post = self.request.get("content")

        if title and post:
            # creates an instance of Post and saves to db
            p = Post(title=title, post=post)
            p.put()
            post_id = p.key().id()
            self.redirect('/' + str(post_id))
        else:
            error = "Entry must have a title and a body!"
            self.render_newpost(title, post, error)


# Post Page Handler
class PostPage(Handler):

    def render_article(self, post_id, title="", post=""):
        article = Post.get_by_id(int(post_id))
        self.render('post.html', post=post, title=title, article=article)

    def get(self, post_id):
        self.render_article(post_id)

# Sign Up Page Handler
class SignUp(Handler):

    def get(self):
        self.render('signup.html')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost),
                               (r'/(\d+)', PostPage),
                               ('/signup', SignUp)
                               ], debug=True)
