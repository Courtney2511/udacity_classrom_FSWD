
""" Multi User Blog application with commenting and 'like' functionality """
import os
import hashlib
import hmac
import random
import re
import cgi
import string
import webapp2
import jinja2

from models import User, Post, Comment, Like


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

SECRET = "kickass"


# ---- Handler Classes ---- #


class Handler(webapp2.RequestHandler):
    """ Basic Handler Class """

    def write(self, *a, **kw):
        """ writes response """
        self.response.out.write(*a, **kw)

    @staticmethod
    def render_str(template, **params):
        """ renders jinja template string """
        jinja_template = JINJA_ENV.get_template(template)
        return jinja_template.render(params)

    def render(self, template, **kw):
        """ renders jinja template """
        self.write(Handler.render_str(template, **kw))

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
        user = User.user_by_name(username)
        return user


class MainPage(Handler):
    """ Handles requests to MainPage """

    def render_index(self):
        """ renders index template """
        posts = Post.all().order("-created").run()
        # cookie = self.request.cookies.get('username')
        is_logged_in = self.is_logged_in()
        self.render("index.html", posts=posts, is_logged_in=is_logged_in)

    def get(self):
        """ handles get requests """
        self.render_index()


class NewPost(Handler):
    """ Handles NewPost requests """

    def render_newpost(self, title="", post="", error=""):
        """ renders the newpost template """
        is_logged_in = self.is_logged_in()
        self.render("newpost.html", title=title, post=post, error=error,
                    is_logged_in=is_logged_in)

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
        user = User.user_by_name(username)

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

    def render_article(self, post_id):
        """ renders the article template """
        is_logged_in = self.is_logged_in()
        logged_in_user = self.logged_in_user()
        article = Post.get_by_id(int(post_id))
        already_liked = False
        # returns returns True if the current user has liked the article
        if logged_in_user:
            already_liked = (logged_in_user.likes.filter("post = ",
                                                         article).count() > 0)

        self.render('post.html', article=article, is_logged_in=is_logged_in,
                    logged_in_user=logged_in_user, already_liked=already_liked)

    def get(self, post_id):
        """ handles get request """
        self.render_article(post_id)

    def post(self, post_id):
        """ handles post request from comment form """
        article = Post.get_by_id(int(post_id))
        comment = self.request.get("comment")
        if comment:
            cookie = self.request.cookies.get("username")
            if cookie:
                username = check_secure_val(cookie)
                user = User.user_by_name(username)
                new_comment = Comment(comment=comment, post=article,
                                      user=user)
                new_comment.put()
                self.redirect('/' + post_id)


class EditPost(Handler):
    """ Handles requests for the edit post page """

    def get(self, post_id):
        """ defines get """
        post = Post.post_by_id(post_id)
        is_logged_in = self.is_logged_in()
        logged_in_user = self.logged_in_user()
        if logged_in_user.name == post.user.name:  # pylint: disable=no-member
            self.render('editpost.html', post=post, is_logged_in=is_logged_in,
                        post_id=post_id)
        else:
            self.write("you can't edit other peoples posts")

    def post(self, post_id):
        """ defines posts """
        post = Post.post_by_id(post_id)
        subject = self.request.get("subject")
        content = self.request.get("content")
        post.title = subject
        post.post = content
        post.put()  # pylint: disable=no-member
        self.redirect('/' + post_id)


class DeletePost(Handler):
    """ Handle requests to delete likes """
    def get(self, post_id):
        """ handles get request """

    def post(self, post_id):
        """ deletes post form db """
        post = Post.post_by_id(post_id)
        logged_in_user = self.logged_in_user()
        if logged_in_user.name == post.user.name:
            post.delete()
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
        is_logged_in = self.is_logged_in()

        self.render('signup.html', is_logged_in=is_logged_in)

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
        if User.user_by_name(username) is not None:
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
        is_logged_in = self.is_logged_in()

        if cookie:
            username = check_secure_val(cookie)

        if username:
            self.render("welcome.html", username=username,
                        is_logged_in=is_logged_in)
        else:
            self.redirect("/signup")


class LoginPage(Handler):
    """ Request Handling for Login page """

    def render_login(self, error=""):
        """ renders login template """
        is_logged_in = self.is_logged_in()
        self.render('login.html', error=error, is_logged_in=is_logged_in)

    def get(self):
        """ handles get request """
        self.render_login()

    def post(self):
        """ handles post request """
        username = self.request.get('username')
        password = self.request.get('password')

        user = valid_login(username, password)

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


class LikeHandler(Handler):
    """ Handles requests for like page """

    def get(self, post_id):
        """ handles get request """
        # post = post_by_id(post_id)

    def post(self, post_id):
        """ handles post request """
        action = self.request.get("like-button")
        user = self.logged_in_user()
        post = Post.post_by_id(post_id)

        if action == 'like':
            like = Like(post=post, user=user)
            like.put()
        else:
            like = user.likes.filter("post =", post).get()
            like.delete()
        self.redirect('/' + post_id)


# working on unlike handler to delete likes on button click
# class UnlikeHandler(Handler):
#     """ Handles requests to unlike """
#
#     def get(self, post_id):
#         """ handles get request """
#
#     def post(self, post_id):
#         """ handles post request """
#         logged_in_user = self.logged_in_user()
#         post = Post.post_by_id(post_id)
#         liked_post = logged_in_user.likes.filter("post = ", post)
#         print liked_post


#  SIGN UP PAGE FUNCTIONS

# regex constant for username validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# regex constant for password validation
PASSWORD_RE = re.compile(r"^.{3,20}$")
# regex constant for email validation
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def valid_login(username, password):
    """ checks for a valid user and password """
    user = User.user_by_name(username)

    if user and valid_pw(username, password, user.pw_hash):
        return user


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


# Routing

app = webapp2.WSGIApplication([('/', MainPage), # pylint: disable=C0103
                               ('/newpost', NewPost),
                               (r'/(\d+)/edit', EditPost),
                               (r'/(\d+)/delete', DeletePost),
                               (r'/(\d+)', PostPage),
                               ('/signup', SignUp),
                               ('/welcome', WelcomePage),
                               ('/login', LoginPage),
                               ('/logout', LogOut),
                               (r'/(\d+)/like', LikeHandler)
                              ], debug=True)
