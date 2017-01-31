""" Defines the Google Datastore Models """

from google.appengine.ext import db

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
