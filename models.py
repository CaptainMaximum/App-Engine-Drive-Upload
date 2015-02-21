from google.appengine.ext import ndb

class APICredentials(ndb.Model):
    date_obtained = ndb.IntegerProperty(required=True)
    credentials = ndb.TextProperty(required=True)
    user_requested = ndb.StringProperty()

class UserStory(ndb.Model):
    date_posted = ndb.IntegerProperty(required=True)
    subject = ndb.StringProperty(required=True)