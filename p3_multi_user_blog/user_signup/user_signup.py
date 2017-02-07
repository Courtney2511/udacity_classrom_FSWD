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
                    <td class="error">%(error_username)s</td>
                </tr>
                <tr>
                    <td class="label">Password</td>
                    <td><input type="password" name="password"
                        value="%(password)s"></td>
                    <td class="error">%(error_password)s</td>
                </tr>
                <tr>
                    <td class="label">Confirm</td>
                    <td><input type="password" name="verify"
                    value="%(verify)s"></td>
                    <td class="error">%(error_verify)s</td>
                </tr>
                <tr>
                    <td class="label">Email</td>
                    <td><input type="text" name="email"
                    value="%(email)s"></td>
                    <td class="error">%(error_email)s</td>
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
    return username and USER_RE.match(username)


# validates users password against password regex
def valid_password(password):
    return password and PASSWORD_RE.match(password)


# validates users email address against email regex
def valid_email(email):
    return email and EMAIL_RE.match(email)


def escape_html(string):
    return cgi.escape(string, quote=True)


class MainPage(Handler):
    def write_form(self, error_username="", username="", error_password="",
                   password="", error_verify="", verify="", error_email="",
                   email=""):
        self.write(signup_form % {"error_username": error_username,
                                  "username": escape_html(username),
                                  "error_password": error_password,
                                  "password": escape_html(password),
                                  "error_verify": error_verify,
                                  "verify": escape_html(verify),
                                  "error_email": error_email,
                                  "email": escape_html(email)})

    def get(self):
        self.write_form()

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username)

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
            print params
            self.write_form(**params)
        else:
            self.redirect("/welcome?username=" + username)


class WelcomePage(Handler):
    def get(self):
        username = self.request.get('username')
        self.write(welcome_page % {"username": username})


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/welcome', WelcomePage)
], debug=True)
