
""" Multi User Blog application with commenting and 'like' functionality """

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


class Comment(db.Model):
    """ Comment Model """
    comment = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)
    user = db.ReferenceProperty(User, collection_name='user_comments')
    post = db.ReferenceProperty(Post, collection_name='post_comments')


class Like(db.Model):
    """ Like Model """
    post = db.ReferenceProperty(Post, required=True, collection_name='likes')
    user = db.ReferenceProperty(User, required=True, collection_name='likes')


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
        user = self.logged_in_user()
        return bool(user)

    def logged_in_user(self):
        """ returns the logged in user """
        cookie = self.request.cookies.get("username")
        username = check_secure_val(cookie)
        user = user_by_name(username)
        return user


class MainPage(Handler):
    """ Handles requests to MainPage """

    def render_index(self):
        """ renders index template """
        posts = Post.all().order("-created").run()
        # cookie = self.request.cookies.get('username')
        user = self.is_logged_in()
        self.render("index.html", posts=posts, user=user)

    def get(self):
        """ handles get requests """
        self.render_index()


class NewPost(Handler):
    """ Handles NewPost requests """

    def render_newpost(self, title="", post="", error=""):
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
            self.render_newpost()

    def post(self, username=""):
        """ handles post requests from newpost form """
        title = self.request.get("subject")
        post = self.request.get("content")
        cookie = self.request.cookies.get("username")

        username = check_secure_val(cookie)
        user = user_by_name(username)

        if title and post and username:
            # creates a Post entity and saves to db
            new_post = Post(user=user, title=title, post=post, likes=0)
            new_post.put()
            post_id = new_post.key().id()
            # redirects to post page
            self.redirect('/' + str(post_id))
        else:
            error = "Entry must have a title and a body!"
            self.render_newpost(title, post, error)


# Post Page Handler
class PostPage(Handler):
    """ handles requests to PostPage """

    # working on filtering likes for post liked by user for like once control
    def render_article(self, post_id):
        """ renders the article template """
        user = self.is_logged_in()
        logged_in_user = self.logged_in_user()
        article = Post.get_by_id(int(post_id),
                                 read_policy=db.STRONG_CONSISTENCY,
                                 deadline=5)  # pylint: disable=no-member
        # returns returns True if the current user has liked the article
        already_liked = (logged_in_user.likes.filter("post = ",
                                                     article).count() > 0)
        print "The user has liked this %s times" % already_liked

        self.render('post.html', article=article, user=user,
                    logged_in_user=logged_in_user, already_liked=already_liked)

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
                new_comment = Comment(comment=comment, post=article, user=user)
                new_comment.put()
                # TODO most recent comment not displayed until refresh
                self.redirect('/' + post_id)


class EditPost(Handler):
    """ Handles requests for the edit post page """

    def get(self, post_id):
        """ defines get """
        post = post_by_id(post_id)
        user = self.is_logged_in()
        logged_in_user = self.logged_in_user()
        if logged_in_user.name == post.user.name:  # pylint: disable=no-member
            self.render('editpost.html', post=post, user=user, post_id=post_id)
        else:
            self.write("you can't edit other peoples posts")

    def post(self, post_id):
        """ defines posts """
        post = post_by_id(post_id)
        subject = self.request.get("subject")
        content = self.request.get("content")
        post.title = subject
        post.post = content
        post.put()  # pylint: disable=no-member
        self.redirect('/' + post_id)


class DeletePost(Handler):

    def get(self, post_id):
        """ handles get request """

    def post(self, post_id):
        """ deletes post form db """
        post = post_by_id(post_id)
        logged_in_user = self.logged_in_user()
        if logged_in_user.name == post.user.name:  # pylint: disable=no-member
            post.delete()  # pylint: disable=no-member
            self.redirect('/')


class SignUp(Handler):
    """ request handling for signup page """

    def register(self, username, password, email):
        """ creates a User and saves to db """
        # hashes password
        pw_hash = make_pw_hash(username, password)
        new_user = User(name=username, pw_hash=pw_hash, email=email)
        new_user.put()
        # creates and sets name cookie
        cookie_val = make_secure_val(new_user.name)
        self.set_secure_cookie('username', cookie_val)

    def get(self):
        """ handles get request """
        user = self.is_logged_in()

        self.render('signup.html', user=user)

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
            self.redirect('/welcome')


class WelcomePage(Handler):
    """ Handles requests to the Welcome Page """

    def get(self, username=""):
        """ handles get request """

        cookie = self.request.cookies.get("username")
        user = self.is_logged_in()

        if cookie:
            username = check_secure_val(cookie)

        if username:
            self.render("welcome.html", username=username, user=user)
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
        user = self.is_logged_in()
        self.render('login.html', error=error, user=user)

    def get(self):
        """ handles get request """
        self.render_login()

    def post(self):
        """ handles post request """
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
        user = self.is_logged_in()
        self.render('users.html', user=user)


class LikeHandler(Handler):
    """ Handles requests for like page """

    def get(self, post_id):
        """ handles get request """
        # post = post_by_id(post_id)

    def post(self, post_id):
        """ handles post request """
        user = self.logged_in_user()
        post = post_by_id(post_id)
        like = Like(post=post, user=user)
        like.put()
        self.redirect('/' + post_id)
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


def escape_html(value):
    """ escapes html """
    return cgi.escape(value, quote=True)


# USER FUNCTIONS

def user_by_name(username):
    """ retrieves User by name """
    # pylint: disable=no-member
    user = User.all().filter('name =', username).get()
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


def hash_str(value):
    """ returns the hash value of a string """
    return hmac.new(SECRET, value).hexdigest()


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
    return Post.get_by_id(int(post_id))

# Routing

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/newpost', NewPost),
                               (r'/(\d+)/edit', EditPost),
                               (r'/(\d+)/delete', DeletePost),
                               (r'/(\d+)', PostPage),
                               ('/signup', SignUp),
                               ('/welcome', WelcomePage),
                               ('/login', LoginPage),
                               ('/logout', LogOut),
                               ('/user', UsersPage),
                               (r'/(\d+)/like', LikeHandler)
                              ], debug=True)
