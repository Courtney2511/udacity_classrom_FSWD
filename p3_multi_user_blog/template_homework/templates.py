import os

import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')  # sets the template directory for jinja
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),  # adds the directory to the jinja env
                               autoescape=True)


class Handler(webapp2.RequestHandler):  # sets up a Handler class to define write and render
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        items = self.request.get_all("food")  # sets items = all requests with name = food
        self.render("shopping_list.html", items=items)  # renders page with items = to items


class FizzBuzzHandler(Handler):
    def get(self):
        n = self.request.get('n', 0)  # gets n from query parameter
        n = n and int(n)  # converts n to an int
        self.render('fizzbuzz.html', n=n)  # renders page with n = to n


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/fizzbuzz', FizzBuzzHandler)
                               ],
                              debug=True)
