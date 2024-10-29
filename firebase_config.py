# firebase_config.py
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the content of the service account key from an environment variable
SERVICE_ACCOUNT_CONTENT = os.getenv('FIREBASE_APPLICATION_CREDENTIALS')

# Parse the JSON content
service_account_info = json.loads(SERVICE_ACCOUNT_CONTENT)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

db = firestore.client()