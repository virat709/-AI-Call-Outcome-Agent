import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
SHEET_TITLE = 'Call_Outcome_Log'

class SheetsLogger:
    def __init__(self):
        self.creds = None
        self._authenticate()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.spreadsheet_id = None

    def _authenticate(self):
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())

    def ensure_sheet_exists(self):
        """
        Checks if the Call_Outcome_Log sheet exists. If not, creates it and sets up headers.
        """
        try:
            # Search for the file by name
            query = f"name='{SHEET_TITLE}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
            results = self.drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            items = results.get('files', [])

            if not items:
                print(f"Sheet '{SHEET_TITLE}' not found. Creating a new one.")
                # Create a new spreadsheet
                spreadsheet_body = {
                    'properties': {
                        'title': SHEET_TITLE
                    }
                }
                spreadsheet = self.sheets_service.spreadsheets().create(
                    body=spreadsheet_body, fields='spreadsheetId'
                ).execute()
                self.spreadsheet_id = spreadsheet.get('spreadsheetId')
                
                # Setup headers
                headers = [["Timestamp", "Client Name", "Outcome", "AI Summary", "Email Draft Status"]]
                body = {'values': headers}
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id, range="Sheet1!A1:E1",
                    valueInputOption="RAW", body=body
                ).execute()
                print(f"Created sheet with ID: {self.spreadsheet_id}")
            else:
                self.spreadsheet_id = items[0]['id']
                print(f"Found existing sheet '{SHEET_TITLE}' with ID: {self.spreadsheet_id}")
                
        except HttpError as error:
            safe_err = str(error).encode('ascii', 'ignore').decode('ascii')
            print(f"An error occurred: {safe_err}")
            raise error

    def log_call(self, client_name: str, outcome: str, summary: str, email_status: str):
        """
        Appends a new row to the log sheet.
        """
        if not self.spreadsheet_id:
            self.ensure_sheet_exists()

        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            values = [[timestamp, client_name, outcome, summary, email_status]]
            body = {'values': values}
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range="Sheet1!A:E",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            print(f"{result.get('updates').get('updatedCells')} cells appended to the sheet.")
            
        except HttpError as error:
            safe_err = str(error).encode('ascii', 'ignore').decode('ascii')
            print(f"An error occurred while logging: {safe_err}")
            raise error

# For testing
if __name__ == "__main__":
    logger = SheetsLogger()
    logger.ensure_sheet_exists()
    logger.log_call("Test Client", "YES", "Client agreed to the terms", "Drafted")
