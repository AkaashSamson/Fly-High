# firebase_config.py
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import base64

# Load environment variables from .env file
# load_dotenv()

# Get the content of the service account key from an environment variable
SERVICE_ACCOUNT_CONTENT = os.getenv('FIREBASE_APPLICATION_CREDENTIALS')

if SERVICE_ACCOUNT_CONTENT:
    credentials_json = base64.b64decode(SERVICE_ACCOUNT_CONTENT).decode()
    service_account_info = json.loads(credentials_json)

# Parse the JSON content

# Initialize Firebase Admin SDK
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

db = firestore.client()