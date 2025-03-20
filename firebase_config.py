import firebase_admin
from firebase_admin import credentials, firestore

# Only initialize if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("newsbook-e9046-359984ad755d.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
