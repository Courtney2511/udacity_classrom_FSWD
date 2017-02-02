""" Defines the Google Datastore Models """

from google.appengine.ext import db

# ---- Entity Models ---- #


class User(db.Model):
    """ User Model """
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def user_by_name(cls, username):
        """ retrieves User by name """
        user = cls.all().filter('name =', username).get()
        return user


class Post(db.Model):
    """ Post Model """
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)
    user = db.ReferenceProperty(User, collection_name='user_posts')

    @classmethod
    def post_by_id(cls, post_id):
        """ retrieves Post by id """
        return cls.get_by_id(int(post_id))


class Comment(db.Model):
    """ Comment Model """
    comment = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)
    user = db.ReferenceProperty(User, collection_name='user_comments')
    post = db.ReferenceProperty(Post, collection_name='post_comments')

    @classmethod
    def comment_by_id(cls, comment_id):
        """ retrieves Comment by id """
        return cls.get_by_id(int(comment_id))


class Like(db.Model):
    """ Like Model """
    post = db.ReferenceProperty(Post, required=True, collection_name='likes')
    user = db.ReferenceProperty(User, required=True, collection_name='likes')
