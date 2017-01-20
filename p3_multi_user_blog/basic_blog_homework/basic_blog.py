import os
import cgi
import re
import webapp2
import jinja2
import hashlib
import hmac
import random
import string

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

SECRET = "kickass"

# ---- Entity Models ---- #


# Post Model
class Post(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)


# User Model
class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()


# ---- Handler Classes ---- #

# Basic Handler class
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, cookie_name, cookie_val):
        self.response.set_cookie(cookie_name, cookie_val)

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/')


# Main Page Handler
class MainPage(Handler):

    def render_index(self):
        posts = db.GqlQuery("SELECT * from Post ORDER BY created DESC")
        self.render("index.html", posts=posts)

    def get(self):
        self.render_index()


# New Post Page Handler
class NewPost(Handler):

    # renders the newpost template
    def render_newpost(self, title="", post="", error=""):
        self.render("newpost.html", title=title, post=post, error=error)

    # gets newpost page
    def get(self):
        self.render_newpost()

    # posts from newpost form
    def post(self):
        title = self.request.get("subject")
        post = self.request.get("content")

        if title and post:
            # creates a Post entity and saves to db
            p = Post(title=title, post=post)
            p.put()
            post_id = p.key().id()
            # redirects to post page
            self.redirect('/' + str(post_id))
        else:
            error = "Entry must have a title and a body!"
            self.render_newpost(title, post, error)


# Post Page Handler
class PostPage(Handler):

    # renders the article template
    def render_article(self, post_id):
        article = Post.get_by_id(int(post_id))
        self.render('post.html', article=article)

    # gets post page
    def get(self, post_id):
        self.render_article(post_id)


# Sign Up Page Handler
class SignUp(Handler):

    # creates a User entity and saves to db
    def register(self, username, password, email):
        # hashes password
        pw_hash = make_pw_hash(username, password)
        u = User(name=username, pw_hash=pw_hash, email=email)
        u.put()
        # creates and sets name cookie
        cookie_val = make_secure_val(u.name)
        self.set_secure_cookie('username', cookie_val)

    def get(self):
        self.render('signup.html')

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username, email=email)

        if not valid_username(username):
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

        else:
            self.register(username, password, email)
            self.redirect('/welcome')  # TODO redirect and send user??????


# Welcome Page Handler
class WelcomePage(Handler):

    def get(self, username=""):
        cookie = self.request.cookies.get("username")

        if cookie:
            username = check_secure_val(cookie)

        if username:
            self.render("welcome.html", username=username)
        else:
            self.redirect("/signup")


class LoginPage(Handler):

    def valid_login(self, username, password):
        user = user_by_name(username)

        if user and valid_pw(username, password, user.pw_hash):
            return user

    def render_login(self, error=""):
        self.render('login.html', error=error)

    def get(self):
        self.render_login()

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')

        user = self.valid_login(username, password)

        if user is None:
            error = "Invalid Login"
            self.render_login(error)

        if user:
            cookie_val = make_secure_val(username)
            self.set_secure_cookie('username', cookie_val)
            self.redirect('/welcome')

class LogOut(Handler):

    def get(self):
        self.logout()
        self.redirect('/signup')


class UsersPage(Handler):
    def get(self):
        users = db.GqlQuery("SELECT * from User")
        self.render('users.html', users=users)

#  SIGN UP PAGE FUNCTIONS

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


# USER FUNCTIONS

# gets user by name
def user_by_name(username):
    user = User.all().filter('name =', username).get()
    return user


# makes a random 5 letter salt
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


# creates a password hash and salt if not already generated
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)


# tests if password is valid
def valid_pw(name, pw, h):
    salt = h.split('|')[1]
    return h == make_pw_hash(name, pw, salt)


def hash_str(string):
    return hmac.new(SECRET, string).hexdigest()


def make_secure_val(val):
    return "%s|%s" % (val, hash_str(val))


def check_secure_val(secure_val):
    val = secure_val.split("|")[0]
    if secure_val == make_secure_val(val):
        return val

# Routing

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost),
                               (r'/(\d+)', PostPage),
                               ('/signup', SignUp),
                               ('/welcome', WelcomePage),
                               ('/login', LoginPage),
                               ('/logout', LogOut),
                               ('/users', UsersPage)
                               ], debug=True)
