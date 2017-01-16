import os
import cgi
import re
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

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username, email=email)

        if not valid_password(username):
            params['error_username'] = "Username is not valid"
            have_error = True

        if not valid_password(password):
            params['error_password'] = "Password is not valid"
            have_error = True
        elif password != verify:
            params['error_verify'] = "Password did not match"
            have_error = True

        if email and not valid_email(email):
            params['error_email'] = "Email is not valid"
            have_error = True

        if have_error:
            self.render('signup.html', **params)



# SIGN UP PAGE FUNCTIONS

# regex constant for username validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# regex constant for password validation
PASSWORD_RE = re.compile(r"^.{3,20}$")
# regex constant for email validation
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


# validates users username against username regex
def valid_username(username):
    return username and USER_RE.match(username)


# validates users password against password regex
def valid_password(password):
    return password and PASSWORD_RE.match(password)


# validates users email address against email regex
def valid_email(email):
    return email and EMAIL_RE.match(email)


def escape_html(string):
    return cgi.escape(string, quote=True)

# Page Mapping

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost),
                               (r'/(\d+)', PostPage),
                               ('/signup', SignUp)
                               ], debug=True)
