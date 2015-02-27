from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import models, re

# Creates an fresh GoogleAuth instance
def get_authenticated_gauth():
    gauth = GoogleAuth()
    # Get the latest stored Drive API credentials
    latest_credentials = models.APICredentials.query().order(-models.APICredentials.date_obtained).get()
    #[x for x in models.APICredentials.query().order(-models.APICredentials.date_obtained)][0]
    creds_json = latest_credentials.credentials
    gauth.CredentialsFromJSON(creds_json)
    gauth.Refresh()
    return gauth

# Uploads user story information to a public Google Drive folder
# @param 'title' (type=string): Title of the story, also part of the folder name
# @param 'audio_blob'(type=BlobInfo): Blob object that contains audio data
# @param 'picture_blob'(type=BlobInfo): Blob object that contains picture data
# @param 'date_created'(type=int): Epoch time (in seconds) that this Story was uploaded.
#       Also forms the other part of the folder name  
# +returns 'folder_id'(type=string): ID of the folder that we put the files into
def upload_to_drive(title, audio_blob, picture_blob, date_created):
    # Create an authenticated google drive service
    gauth = get_authenticated_gauth()
    drive = GoogleDrive(gauth)
    # Create a folder to put all of our files in
    # TODO: Store parent ID in the database so that we can update the folder we want all of the stories in dynamically
    folder_title = "%s_%d" %(title, date_created)
    folder = drive.CreateFile({'title': folder_title, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [{"id": "0B-8O_XwimC2dY1dpRGVmaHRFVzQ"}]})
    folder.Upload()
    folder_id = folder['id']
    # Upload the audio file to the folder
    audio_title = re.sub("\s", "", audio_blob.filename)
    audio_file = drive.CreateFile({'title': audio_title, 'mimeType': audio_blob.content_type, "parents": [{"id": folder_id}]})
    audio_file.SetContentObject(audio_blob)
    audio_file.Upload()
    # Upload the picture file to the folder
    picture_title = re.sub("\s", "", picture_blob.filename)
    picture_file = drive.CreateFile({'title': picture_title, 'mimeType': picture_blob.content_type, "parents": [{"id": folder_id}]})
    picture_file.SetContentObject(picture_blob)
    picture_file.Upload()
    return folder_id

# Trashes (soft delete) a file from the google drive
# @param 'file_id': ID of the file to delete
def trash_drive_file(file_id):
    gauth = get_authenticated_gauth()
    drive = GoogleDrive(gauth)
    to_trash = drive.CreateFile({'id':file_id})
    to_trash._FilesTrash(param={'fileId': file_id})

# Removes 
def remove_post(post_id):
    story_model = models.Phase2Story.get_by_id(long(post_id))
    folder_id = story_model.folder_id
    trash_drive_file(folder_id)
    story_model.key.delete()
