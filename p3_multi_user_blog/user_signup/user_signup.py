import os
import webapp2
import cgi
import re  # imports regex module


# signup form for main page
signup_form = """
    <style>
        .error {
            color:red;
        }
    </style>
    <h1>Signup</h1>
    <br>
    <form method="post">
        <table>
            <tbody>
                <tr>
                    <td class="label">Username</td>
                    <td><input type="text" name="username"
                        value="%(username)s"></td>
                    <td class="error">%(error)s</td>
                </tr>
                <tr>
                    <td class="label">Password</td>
                    <td><input type="password" name="password"
                        value="%(password)s"></td>
                    <td class="error"></td>
                </tr>
                <tr>
                    <td class="label">Confirm</td>
                    <td><input type="password" name="verify"
                    value="%(verify)s"></td>
                    <td class="error"></td>
                </tr>
                <tr>
                    <td class="label">Email</td>
                    <td><input type="text" name="email"
                    value="%(email)s"></td>
                    <td class="error"></td>
            </tbody>
        </table>
            <br>
            <input type="submit" name="submit">
</form>
"""

welcome_page = """
    <h1>Welcome, %(username)s</h1>
"""


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # def render_str(self, temple, **params):
    #     t = jinja_env.get_template(template)
    #     return t.render(params)


# regex constant for username validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# regex constant for password validation
PASSWORD_RE = re.compile(r"^.{3,20}$")
# regex constant for email validation
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


# validates users username against username regex
def valid_username(username):
    return USER_RE.match(username)


# validates users password against password regex
def valid_password(password):
    return PASSWORD_RE.match(password)

# validates users password against users verify  TODO - write function
# def valid_verify(verify):
#     if user_password == user_verify:
#         return


# validates users email address against email regex
def valid_email(email):
    return EMAIL_RE.match(email)


def escape_html(string):
    return cgi.escape(string, quote=True)


class MainPage(Handler):
    def write_form(self, error="", username="", password="", verify="",
                   email=""):
        self.write(signup_form % {"error": error,
                                  "username": escape_html(username),
                                  "password": escape_html(password),
                                  "verify": escape_html(verify),
                                  "email": escape_html(email)})

    def get(self):
        self.write_form()

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')

        username = valid_username(user_username)
        password = valid_password(user_password)
        verify = user_verify  # TODO write verification for matching passwords
        email = valid_email(user_email)

        # checks validity of input TODO add password/verify match
        if not ((password and verify) and (username or email)):
            self.write_form("That doesn't look valid!", user_username,
                            user_email)
            # TODO keep user email upon form rewrite
        else:
            self.redirect("/welcome?username=" + user_username)


class WelcomePage(Handler):
    def get(self):
        username = self.request.get('username')
        self.write(welcome_page % {"username": username})  # TODO sort username variable


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/welcome', WelcomePage)
], debug=True)
