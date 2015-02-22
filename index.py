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
    def get(self):
        gauth = GoogleAuth(flow_params = {'state':'', 'approval_prompt': 'force', 'user_id':'drivebox.test@gmail.com'})
        self.response.out.write('<a href="' + gauth.GetAuthUrl() + '">Authenticate</a>')

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

class RefreshTester(webapp2.RequestHandler):
    def get(self):
        gauth = GoogleAuth(flow_params = {'state':'', 'approval_prompt': 'force', 'user_id':'drivebox.test@gmail.com'})
        credentials_model = [x for x in models.APICredentials.query().order(-models.APICredentials.date_obtained)][0]
        creds_json = credentials_model.credentials
        gauth.CredentialsFromJSON(creds_json)
        gauth.Refresh()
        drive = GoogleDrive(gauth)
        self.response.out.write(gauth.credentials.to_json())
        file1 = drive.CreateFile({'title': 'Hello.txt'}) # Create GoogleDriveFile instance with title 'Hello.txt'
        file1.SetContentString('Hello World!')
        file1.Upload() # Upload it

class FormPageHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url("/upload")
        html = render_template('formpage.html', {"upload": upload_url})
        self.response.out.write(html)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        title = self.request.get('title')
        _file = self.get_uploads()[0]
        gauth = GoogleAuth(flow_params = {'state':'', 'approval_prompt': 'force', 'user_id':'drivebox.test@gmail.com'})
        credentials_model = [x for x in models.APICredentials.query().order(-models.APICredentials.date_obtained)][0]
        creds_json = credentials_model.credentials
        gauth.CredentialsFromJSON(creds_json)
        gauth.Refresh()
        drive = GoogleDrive(gauth)
        file1 = drive.CreateFile({'title': _file.filename, 'mimetype': _file.content_type})
        file1.SetContentObject(_file)
        file1.Upload()
        _file.delete()
        self.redirect("/")
       # self.response.out.write(_file.open().read())


app = webapp2.WSGIApplication([
    ("/", FormPageHandler),
    ("/oauth2callback", OauthHandler),
    ("/upload", UploadHandler)
    ])
