import os
import cgi
import re
import string
import random
import hmac
import hashlib
import webapp2
import jinja2

from google.appengine.ext import db

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

SECRET = "kickass"

# ---- Entity Models ---- #


class User(db.Model):
    """ User Model """
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()


class Post(db.Model):
    """ Post Model """
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)
    user = db.ReferenceProperty(User, collection_name='user_posts')
    likes = db.IntegerProperty()


class Comment(db.Model):
    """ Comment Model """
    comment = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)
    user = db.ReferenceProperty(User, collection_name='user_comments')
    post = db.ReferenceProperty(Post, collection_name='post_comments')

# ---- Handler Classes ---- #


class Handler(webapp2.RequestHandler):
    """ Basic Handler Class """

    def write(self, *a, **kw):
        """ writes response """
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """ renders jinja template string """
        jinja_template = JINJA_ENV.get_template(template)
        return jinja_template.render(params)

    def render(self, template, **kw):
        """ renders jinja template """
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, cookie_name, cookie_val):
        """ sets secure cookie"""
        self.response.set_cookie(cookie_name, cookie_val)

    def logout(self):
        """ deletes user from username cookie"""
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/')

    def is_logged_in(self):
        """ checks for a logged in user """
        cookie = self.request.cookies.get("username")
        if cookie.name is not None:
            return cookie.name


class MainPage(Handler):
    """ Handles requests to MainPage """

    def render_index(self):
        """ renders index template """
        posts = db.GqlQuery("SELECT * from Post ORDER BY created DESC")
        cookie = self.request.cookies.get('username')
        username = check_secure_val(cookie)
        # TODO sort out the user to get edit and delete working
        user = user_by_name(username)
        print user
        self.render("index.html", posts=posts)

    def get(self):
        """ handles get requests """
        self.render_index()


class NewPost(Handler):
    """ Handles NewPost requests """

    def render_newpost(self, title="", post="", error="", username=""):
        """ renders the newpost template """
        self.render("newpost.html", title=title, post=post, error=error)

    def get(self, username=""):
        """ handles get requests """
        cookie = self.request.cookies.get("username")

        if cookie:
            username = check_secure_val(cookie)
        else:
            self.redirect("/login")

        if username:
            self.render_newpost(username=username)

    def post(self, username=""):
        """ handles post requests from newpost form """
        title = self.request.get("subject")
        post = self.request.get("content")
        cookie = self.request.cookies.get("username")

        username = check_secure_val(cookie)
        user = user_by_name(username)

        if title and post and username:
            # creates a Post entity and saves to db
            p = Post(user=user, title=title, post=post, likes=0)
            p.put()
            post_id = p.key().id()
            # redirects to post page
            self.redirect('/' + str(post_id))
        else:
            error = "Entry must have a title and a body!"
            self.render_newpost(title, post, error)


# Post Page Handler
class PostPage(Handler):
    """ handles requests to PostPage """

    def render_article(self, post_id):
        """ renders the article template """
        article = Post.get_by_id(int(post_id))   # pylint: disable=no-member
        self.render('post.html', article=article)

    def get(self, post_id):
        """ handles get request """
        self.render_article(post_id)

    def post(self, post_id):
        """ handles post request from comment form """
        article = Post.get_by_id(int(post_id))  # pylint: disable=no-member
        comment = self.request.get("comment")
        if comment:
            cookie = self.request.cookies.get("username")
            if cookie:
                username = check_secure_val(cookie)
                user = user_by_name(username)
                c = Comment(comment=comment, post=article, user=user)
                c.put()
                self.render('post.html', article=article)


# Sign Up Page Handler
class SignUp(Handler):
    """ request handling for signup page """

    def register(self, username, password, email):
        """ creates a User and saves to db """
        # hashes password
        pw_hash = make_pw_hash(username, password)
        u = User(name=username, pw_hash=pw_hash, email=email)
        u.put()
        # creates and sets name cookie
        cookie_val = make_secure_val(u.name)
        self.set_secure_cookie('username', cookie_val)

    def get(self):
        """ handles get request """
        self.render('signup.html')

    def post(self):
        """ handles post request """
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username, email=email)

        if not valid_username(username):
            params['error_username'] = "Username is not valid"
            have_error = True

        # checks to make sure name is not taken
        if user_by_name(username) is not None:
            params['error_username'] = "Username is already taken"
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


class WelcomePage(Handler):
    """ Handles requests to the Welcome Page """

    def get(self, username=""):
        """ handles get request """
        cookie = self.request.cookies.get("username")

        if cookie:
            username = check_secure_val(cookie)

        if username:
            self.render("welcome.html", username=username)
        else:
            self.redirect("/signup")


class LoginPage(Handler):
    """ Request Handling for Login page """

    def valid_login(self, username, password):
        """ checks for a valid user and password """
        user = user_by_name(username)

        if user and valid_pw(username, password, user.pw_hash):
            return user

    def render_login(self, error=""):
        """ renders login template """
        self.render('login.html', error=error)

    def get(self):
        """ handles get request """
        self.render_login()

    def post(self):
        """ handles post request """
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
    """ handles requests to logout """

    def get(self):
        """ handles get request """
        self.logout()
        self.redirect('/signup')


class UsersPage(Handler):
    """ handles requests for users page """
    def get(self):
        """ handles get request """
        users = db.GqlQuery("SELECT * from User")
        self.render('users.html', users=users)


class LikeHandler(Handler):
    """ Handles requests for like page """

    def get(self, post_id):
        """ handles get request """
        # post = post_by_id(post_id)

    def post(self, post_id):
        """ handles post request """
        p = post_by_id(post_id)
        p.likes = p.likes + 1
        p.put()
        self.render('post.html', article=p)

#  SIGN UP PAGE FUNCTIONS

# regex constant for username validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# regex constant for password validation
PASSWORD_RE = re.compile(r"^.{3,20}$")
# regex constant for email validation
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def valid_username(username):
    """ checks for valid username """
    return username and USER_RE.match(username)


def valid_password(password):
    """ checks for valid password """
    return password and PASSWORD_RE.match(password)


def valid_email(email):
    """ checks for valid email """
    return email and EMAIL_RE.match(email)


def escape_html(string):
    """ escapes html """
    return cgi.escape(string, quote=True)


# USER FUNCTIONS

def user_by_name(username):
    """ retrieves User by name """
    user = User.all().filter('name =', username).get()  # pylint: disable=no-member
    return user


def make_salt():
    """ makes a random 5 letter salt """
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, password, salt=None):
    """ creates a password hash and salt if not already generated """
    if not salt:
        salt = make_salt()
    pw_hash = hashlib.sha256(name + password + salt).hexdigest()
    return '%s|%s' % (pw_hash, salt)


def valid_pw(name, password, pw_hash):
    """ tests if password is valid """
    salt = pw_hash.split('|')[1]
    return pw_hash == make_pw_hash(name, password, salt)


def hash_str(string):
    """ returns the hash value of a string """
    return hmac.new(SECRET, string).hexdigest()


def make_secure_val(val):
    """ returns a secure value for cookies """
    return "%s|%s" % (val, hash_str(val))


def check_secure_val(secure_val):
    """ checks the secure value of the cookie"""
    val = secure_val.split("|")[0]
    if secure_val == make_secure_val(val):
        return val


# POST FUNCTIONS
def post_by_id(post_id):
    """ retrieves Post by id """
    post = Post.get_by_id(int(post_id))  # pylint: disable=no-member
    return post

# Routing

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost),
                               (r'/(\d+)', PostPage),
                               ('/signup', SignUp),
                               ('/welcome', WelcomePage),
                               ('/login', LoginPage),
                               ('/logout', LogOut),
                               ('/user', UsersPage),
                               (r'/(\d+)/like', LikeHandler)
                              ], debug=True)
