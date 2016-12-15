import os
import webapp2
import re  # imports regex module

# regex constant for username validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# regex constant for password validation
PASSWORD_RE = re.compile(r"^.{3,20}$")
# regex constant for email validation
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

# signup form for main page
signup_form = """
    <h1>Signup</h1>
    <br>
    <form method="post">
        <label>Name
            <input type="text" name="username">
        </label>
            <br>
        <label>Password
            <input type="password" name="password">
        </label>
            <br>
        <label>Confirm
            <input type="password" name="verify">
        </label>
            <br>
        <label>Email (optional)
            <input type="text" name="email">
        </label>
        <br>
        <br>
        <input type="submit" name="submit">
"""


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # def render_str(self, temple, **params):
    #     t = jinja_env.get_template(template)
    #     return t.render(params)


class MainPage(Handler):
    def get(self):
        self.write(signup_form)

    def post(self):
        user_username = valid_username(self.request.get('username'))
        user_password = valid_password(self.request.get('password'))
        user_email = valid_email(self.request.get('email'))

        if not (user_username and user_password and user_email):
            self.write(signup_form)
        else:
            self.write("Thanks for signing up!")

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)


# validates users username against username regex
def valid_username(username):
    return USER_RE.match(username)


# validates users password against password regex
def valid_password(password):
    return PASSWORD_RE.match(password)


# validates users email address against email regex
def valid_email(email):
    return EMAIL_RE.match(email)
