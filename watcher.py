import sys
import io

# Removed sys.stdout override as it causes Win32 Access Violations

import os
import time
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from main import process_call

# We need Drive (metadata) and Docs (read content) scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly'
]

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'drive_token.json'
PROCESSED_LOG = 'processed_docs.txt'

class DriveWatcher:
    def __init__(self):
        self.creds = None
        self._authenticate()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.processed_ids = self._load_processed_ids()

    def _authenticate(self):
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())

    def _load_processed_ids(self) -> set:
        """Loads the IDs of already processed documents to avoid running them twice."""
        if not os.path.exists(PROCESSED_LOG):
            return set()
        with open(PROCESSED_LOG, 'r') as f:
            return set(line.strip() for line in f if line.strip())

    def _mark_as_processed(self, doc_id: str):
        """Saves a document ID to the processed log."""
        self.processed_ids.add(doc_id)
        with open(PROCESSED_LOG, 'a') as f:
            f.write(f"{doc_id}\n")

    def read_document_text(self, document_id: str) -> str:
        """Extracts text content from a Google Doc."""
        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            text = ""
            for item in document.get('body').get('content'):
                if 'paragraph' in item:
                    elements = item.get('paragraph').get('elements')
                    for element in elements:
                        if 'textRun' in element:
                            text += element.get('textRun').get('content')
            return text.strip()
        except HttpError as error:
            safe_err = str(error).encode('ascii', 'ignore').decode('ascii')
            print(f"An error occurred reading doc {document_id}: {safe_err}")
            return ""
        except Exception as e:
            with open("debug_log.txt", "a") as dbg: dbg.write(f"Exception in read_document_text: {str(e)}\n")
            return ""

    def check_for_new_transcripts(self):
        """Searches Drive for new 'Transcript' documents."""
        try:
            # Query: Documents created in the last 24 hours containing "Transcript" in the name
            yesterday = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat().replace('+00:00', 'Z')
            query = f"mimeType='application/vnd.google-apps.document' and name contains 'Transcript' and trashed=false and createdTime > '{yesterday}'"
            
            results = self.drive_service.files().list(
                q=query, 
                spaces='drive',
                fields='files(id, name, createdTime)'
            ).execute()
            
            items = results.get('files', [])

            if not items:
                print("No new transcripts found.")
                return

            for item in items:
                doc_id = item['id']
                if doc_id not in self.processed_ids:
                    with open("debug_log.txt", "a") as dbg: dbg.write(f"Processing ID: {doc_id}\n")
                    
                    safe_name = item['name'].encode('ascii', 'ignore').decode('ascii')
                    with open("debug_log.txt", "a") as dbg: dbg.write(f"Before Print\n")
                    print(f"\n[!] Found New Transcript: {safe_name}")
                    with open("debug_log.txt", "a") as dbg: dbg.write(f"After Print\n")
                    
                    transcript_text = self.read_document_text(doc_id)
                    with open("debug_log.txt", "a") as dbg: dbg.write(f"After Read Text\n")
                    
                    if transcript_text:
                        with open("debug_log.txt", "a") as dbg: dbg.write(f"Before process_call\n")
                        process_call(transcript_text, recipient_email="")
                        with open("debug_log.txt", "a") as dbg: dbg.write(f"After process_call\n")
                        self._mark_as_processed(doc_id)
                        with open("debug_log.txt", "a") as dbg: dbg.write(f"Marked processed\n")
                    else:
                        print("Document was empty or could not be read.")
                
        except HttpError as error:
            print(f"An error occurred searching drive: {error}")
        except Exception as e:
            import traceback
            with open("error_log.txt", "w") as f:
                f.write(traceback.format_exc())
            print("Fatal error occurred. See error_log.txt")

if __name__ == "__main__":
    watcher = DriveWatcher()
    print("Starting manual check for new transcripts...")
    watcher.check_for_new_transcripts()
    
    # Optional: To run continuously
    # print("Starting Drive Watcher... Listening for new Google Meet Transcripts.")
    # while True:
    #     watcher.check_for_new_transcripts()
    #     time.sleep(60) # check every minute
