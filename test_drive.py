import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'drive_token.json'

def list_recent_docs():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    
    yesterday = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat().replace('+00:00', 'Z')
    query = f"mimeType='application/vnd.google-apps.document' and name contains 'Transcript' and trashed=false and createdTime > '{yesterday}'"
    
    results = drive_service.files().list(
        q=query, 
        spaces='drive',
        fields='files(id, name, createdTime)'
    ).execute()
    
    items = results.get('files', [])
    if not items:
        print("No recent docs found.")
    else:
        print("Recent Docs:")
        for item in items:
            print(f"- {item['name']} (ID: {item['id']})")

if __name__ == '__main__':
    list_recent_docs()
