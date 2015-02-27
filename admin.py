import os, time, re, models, webapp2, utils

from google.appengine.ext.webapp import template, blobstore_handlers
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.appengine.ext import blobstore

def render_template(templatename, templatevalues):
    path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
    html = template.render(path, templatevalues)
    return html

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<a href="/admin/formupload/">Upload a file to the Site</a><br />')
        self.response.out.write('<a href="/admin/authorize/">Authorize upload to Google Drive (Only use if upload is broken!)</a>')

# Handler to show an admin a form so that they may upload a Phase 2 story to the site
class AdminUploadFormHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url("/admin/upload")
        html = render_template('adminupload.html', {'uploadurl': upload_url})
        self.response.out.write(html)

# Handler to allow an admin to reset the Google Drive API credentials, if needed.
class AdminAuthHandler(webapp2.RequestHandler):
    def get(self):
        gauth = GoogleAuth(flow_params = {'state':'', 'approval_prompt': 'force', 'user_id':'drivebox.test@gmail.com'})
        self.response.out.write('<a href="' + gauth.GetAuthUrl() + '">Authenticate</a>')

# Handler that is called after an admin submits a form to upload a Phase 2 story to the site
class AdminUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        # Extract form data, including files uploaded
        title = self.request.get('title')
        category = self.request.get('category')
        user_story = self.request.get('user-story')
        audio = self.get_uploads('audio')[0]
        picture = self.get_uploads('picture')[0]
        # Upload the files to Google Drive
        time_uploaded = int(time.time())
        folder_id = utils.upload_to_drive(title=title, audio_blob=audio, picture_blob=picture, date_created=time_uploaded)
        # Put what we have just added into the database
        audio_title = re.sub("\s", "", audio.filename)
        picture_title = re.sub("\s", "", picture.filename)
        user_story = models.Phase2Story(
            date_posted = time_uploaded, 
            title = title, 
            audio_name = audio_title, 
            picture_name = picture_title, 
            text_story = user_story,
            category = category,
            folder_id = folder_id
        )
        user_story.put()
        # Now delete the blobs, we don't need them anymore
        audio.delete()
        picture.delete()
        self.redirect("/admin/")


# Handler to allow an admin to view a list of Phase 2 stories that they can
# update or delete
class AdminEditHandler(webapp2.RequestHandler):
    def get(self):
        all_posts = models.Phase2Story.query().order(-models.Phase2Story.date_posted)
        html = render_template('adminedit.html', {'POSTS': all_posts})
        self.response.out.write(html)

# Handler to show an admin the Phase 1 stories that users have uploaded so that they
# may download and/or delete them.
class UserUploadViewer(webapp2.RequestHandler):
    def get(self):
        pass

# Handler for removing Phase 2 stories from the website
class AdminRemoveHandler(webapp2.RequestHandler):
    def post(self):
        post_ids = self.request.get_all("user-story")
        for post in post_ids:
            utils.remove_post(post)
        self.redirect("/admin/edit/")


app = webapp2.WSGIApplication([
    ("/admin/?", MainHandler),
    ("/admin/formupload/?", AdminUploadFormHandler),
    ("/admin/upload/?", AdminUploadHandler),
    ("/admin/authorize/?", AdminAuthHandler),
    ("/admin/edit/?", AdminEditHandler),
    ("/admin/user_uploads/?", UserUploadViewer),
    ("/admin/remove/?", AdminRemoveHandler)
    ])
