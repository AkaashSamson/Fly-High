import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
import base64

# load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive']

# Get the content of the service account key from an environment variable
SERVICE_ACCOUNT_CONTENT = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Decode from Base64, then load the JSON
if SERVICE_ACCOUNT_CONTENT:
    credentials_json = base64.b64decode(SERVICE_ACCOUNT_CONTENT).decode()
    service_account_info = json.loads(credentials_json)
# Parse the JSON content
# service_account_info = json.loads(SERVICE_ACCOUNT_CONTENT)

credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES)
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