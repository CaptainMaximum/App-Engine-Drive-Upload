from google.appengine.ext import ndb
from google.appengine.ext import blobstore

# Database model to represent Google Drive API credentials.
# Note that there should only be one instance of this present in the database
# at any time.
class APICredentials(ndb.Model):
    date_obtained = ndb.IntegerProperty(required=True)
    credentials = ndb.TextProperty(required=True)
    user_requested = ndb.StringProperty()

# Initial story uploads to the site.
# It is expected that the audio for Phase 1 stories may be much longer than
# audio for Phase 2 stories.
class Phase1Story(ndb.Model):
    date_posted = ndb.IntegerProperty(required=True)
    audio_key = ndb.BlobKeyProperty()
    picture_key = ndb.BlobKeyProperty()
    text_story = ndb.TextProperty()

# Final stories to be uploaded for public viewing
# The audio is expected to be edited at this point to be shorter than the audio
# in Phase 1.  Because we are hosting the files on Google Drive, we only need
# to store the name of the file, not a blob key
class Phase2Story(ndb.Model):
    date_posted = ndb.IntegerProperty(required=True)
    uploader = ndb.StringProperty()
    # 'Title' is going to be part of the folder name that a story is saved in on Drive
    title = ndb.StringProperty(required=True)
    audio_name = ndb.StringProperty(required=True)
    picture_name = ndb.StringProperty()
    text_story = ndb.TextProperty()
    category = ndb.StringProperty()
    folder_id = ndb.StringProperty(required=True)

# Category that a story falls under (examples given were grief, guilt, etc.)
class Category(ndb.Model):
    category_name = ndb.StringProperty(required=True)