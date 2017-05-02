import os
import re
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_post(response, post):
        response.out.write('<b>' + post.subject + '</b><br>')
        response.out.write(post.content)

class MainPage(BlogHandler):
    def get(self):
        t = jinja_env.get_template("base.html")
        content = t.render()
        self.response.write(content)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogFront(BlogHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        template = jinja_env.get_template("front.html")
        page = template.render(posts=posts)
        self.response.write(page)


class ViewPostHandler(BlogHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            posts = Post(subject = subject, content = content)
            posts.put()
            idTag = posts.key().id()
            self.redirect('/blog/%s'% idTag)

        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?', BlogFront),
                               webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
                               ('/blog/newpost', NewPost)
                               ],
                              debug=True)
