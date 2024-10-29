# google_drive.py
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

# Get the path to the service account key from an environment variable
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def upload_file(file_path, content_type):
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True, mimetype=content_type)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # Set the file permissions to "anyone with the link can view"
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    drive_service.permissions().create(fileId=file.get('id'), body=permission).execute()
    
    return f"https://drive.google.com/file/d/{file.get('id')}/view"