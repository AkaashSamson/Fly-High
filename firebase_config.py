# firebase_config.py
import os
import firebase_admin
from firebase_admin import credentials, firestore



# Get the path to the service account key from an environment variable
service_account_path = os.getenv('FIREBASE_APPLICATION_CREDENTIALS')

# Initialize Firebase Admin SDK
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred)

db = firestore.client()