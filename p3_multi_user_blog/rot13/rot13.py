import os
import webapp2
import jinja2

# set up template directory for jinja
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# defines a Handler class
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


# defines the main page
class MainPage(Handler):
    # renders the main html page upon get request

    def get(self):
        self.render("base.html")

    # renders the main page with rot13 transation upon form post
    def post(self):
        user_text = self.request.get("text")
        text = rot13(user_text)
        self.render("base.html", text=text)

# defines a dictionary for rot13 translation
dictionary = {'a': 'n', 'b': 'o', 'c': 'p',
              'd': 'q', 'e': 'r', 'f': 's',
              'g': 't', 'h': 'u', 'i': 'v',
              'j': 'w', 'k': 'x', 'l': 'y',
              'm': 'z', 'n': 'a', 'o': 'b',
              'p': 'c', 'q': 'd', 'r': 'e',
              's': 'f', 't': 'g', 'u': 'h',
              'v': 'i', 'w': 'j', 'x': 'k',
              'y': 'l', 'z': 'm', 'A': 'N',
              'B': 'O', 'C': 'P', 'D': 'Q',
              'E': 'R', 'F': 'S', 'G': 'T',
              'H': 'U', 'I': 'V', 'J': 'W',
              'K': 'X', 'L': 'Y', 'M': 'Z',
              'N': 'A', 'O': 'B', 'P': 'C',
              'Q': 'D', 'R': 'E', 'S': 'F',
              'T': 'G', 'U': 'H', 'V': 'I',
              'W': 'J', 'X': 'K', 'Y': 'L',
              'Z': 'M'}


# returns the endoced message preserving capitalization and punctuation
def rot13(string):
    result = ""
    for char in string:
        if char not in dictionary:
            result += char
        else:
            result += dictionary.get(char)
    return result

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
