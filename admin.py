import webapp2
from google.appengine.ext.webapp import template
import os, time
import models
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

def render_template(templatename, templatevalues):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    return html

class MainHandler(webapp2.RequestHandler):
    self.response.out.write('<a href="/admin/formupload/">Upload a file to the Site</a><br />')
    self.response.out.write('<a href="/admin/authorize/">Authorize upload to Google Drive (Only use if upload is broken!)</a>')

class AdminUploadFormHandler(webapp2.RequestHandler):
    upload_url = blobstore.create_upload_url("/upload")
    html = render_template('adminupload.html', {'uploadurl': upload_url})
    self.response.out.write(html)

class AdminAuthHandler(webapp2.RequestHandler):
    def get(self):
        gauth = GoogleAuth(flow_params = {'state':'', 'approval_prompt': 'force', 'user_id':'drivebox.test@gmail.com'})
        self.response.out.write('<a href="' + gauth.GetAuthUrl() + '">Authenticate</a>')

class AdminUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        title = self.request.get('title')
        _file = self.get_uploads()[0]
        new_file = models.UserStory(date_posted = int(time.time()), subject = title, blob_key = _file.key())
        new_file.put()

app = webapp2.WSGIApplication([
    ("/admin/", MainHandler),
    ("/admin/formupload/", AdminUploadFormHandler),
    ("/admin/upload/", AdminUploadHandler),
    ("/admin/authorize/", AdminAuthHandler)
    ])
