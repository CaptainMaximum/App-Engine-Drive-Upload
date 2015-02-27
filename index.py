import webapp2
from google.appengine.ext.webapp import template
import os, time
import models
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
import logging

def render_template(templatename, templatevalues):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    return html

class MainHandler(webapp2.RequestHandler):
    def get(self):
        html = render_template('main_template.html', {})
        self.response.out.write(html)

class OauthHandler(webapp2.RequestHandler):
    def get(self):
        gauth = GoogleAuth(flow_params = {'state':'', 'approval_prompt': 'force', 'user_id':'drivebox.test@gmail.com'})
        code = self.request.get("code")
        #self.response.out.write(gauth.credentials.to_json() + "<br />")
        gauth.Auth(code)
        creds = gauth.credentials.to_json()
        # Delete any other stored credentials.  We only want one!
        past_credentials = models.APICredentials.query()
        for c in past_credentials:
            c.key.delete()

        credentials_model = models.APICredentials(date_obtained=int(time.time()), credentials=creds)
        credentials_model.put()
        self.redirect("/admin/")

class UploadPageHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url("/upload")
        html = render_template('formpage.html', {"upload": upload_url})
        self.response.out.write(html)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            picture = self.get_uploads("picture")[0]
            audio = self.get_uploads("audio")[0]
            text = self.request.get('user-story')
        except:
            self.response.out.write("You must fill out all fields in the form")
            return
        curr_time = int(time.time())
        new_story = models.Phase1Story(date_posted = curr_time, audio_key = audio.key(), picture_key = picture.key(), text_story = text)
        new_story.put()
        self.redirect("/")

class ListenHandler(webapp2.RequestHandler):
    def get(self):
        latest_stories = models.Phase2Story.query().order(-models.Phase2Story.date_posted)
        html = render_template('listen_template.html', {'story_list': latest_stories})
        self.response.out.write(html)

class StoryPageHandler(webapp2.RequestHandler):
    base_source = "https://googledrive.com/host/0B-8O_XwimC2dY1dpRGVmaHRFVzQ/"
    def get(self, story_id):
        #story_query = models.Phase2Story.query(str(models.Phase2Story.id()) == str(story_id))
        story = models.Phase2Story.get_by_id(long(story_id))#story_query.get()
        if story:
            img_url = self.base_source + story.title + "_" + str(story.date_posted) + "/" + story.picture_name
            audio_url = self.base_source + story.title + "_" + str(story.date_posted) + "/" + story.audio_name
            html = render_template('story_template.html', {'audio': audio_url, 'image': img_url, 'story': story})
            self.response.out.write(html)
        else:
            self.response.out.write(story_id)


class AudioDownloader(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, audio_key):
        if not blobstore.get(audio_key):
            self.error(404)
        else:
            self.send_blob(blobstore.get(audio_key), content_type="application/octet-stream", save_as=True)

class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Error handling your request <br />")
        self.response.out.write('<a href="/">Home Page</a>')


app = webapp2.WSGIApplication([
    ("/", MainHandler),
    ("/oauth2callback/?", OauthHandler),
    ("/uploadpage/?", UploadPageHandler),
    ("/upload/?", UploadHandler),
    ("/listen/?", ListenHandler),
    ("/audio/([^/]+)?", AudioDownloader),
    ("/error/?", ErrorHandler),
    ("/listen/([^/]+)/?", StoryPageHandler)
    ])
