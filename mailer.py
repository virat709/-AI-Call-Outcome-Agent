import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google import genai
from dotenv import load_dotenv

load_dotenv()

# We need Gmail Compose scope to create drafts
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'gmail_token.json'

class GmailDrafter:
    def __init__(self):
        self.creds = None
        self._authenticate()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    def _generate_yes_email(self, client_name: str, summary: str) -> str:
        """
        Uses Gemini to draft a warm follow-up email when outcome is YES.
        """
        prompt = f"""
        Write a short, warm, and professional follow-up email to a client named '{client_name}'.
        The client agreed to move forward. The overall reason or context for their agreement is: "{summary}".
        The tone should be welcoming and outline that we will share next steps soon.
        Do not include a subject line in the response, just the body of the email.
        """
        response = self.gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()

    def create_draft(self, client_name: str, outcome: str, summary: str, recipient_email: str) -> str:
        """
        Creates a draft email based on the outcome and returns the draft status/ID.
        """
        try:
            message = EmailMessage()

            if outcome == "YES":
                message['Subject'] = "Great time with you / Next Steps"
                body = self._generate_yes_email(client_name, summary)
                message.set_content(body)
            else: # outcome == "NO"
                message['Subject'] = "Thanks for your time"
                body = f"Hi {client_name},\n\nThank you for having us. Hoping to meet again.\n\nBest regards,"
                message.set_content(body)

            if recipient_email:
                message['To'] = recipient_email
            # Do NOT add a 'From' header; the Gmail API infers it from the authenticated user.

            # Encode the message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'message': {'raw': encoded_message}}
            
            # Execute draft creation
            draft = self.service.users().drafts().create(userId="me", body=create_message).execute()
            print(f"Draft created successfully. Draft ID: {draft['id']}")
            return "Drafted"

        except HttpError as error:
            safe_err = str(error).encode('ascii', 'ignore').decode('ascii')
            print(f"An error occurred while creating draft: {safe_err}")
            return "Failed"
        except Exception as e:
            safe_err2 = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"Unexpected error creating draft: {safe_err2}")
            return "Failed"

# For testing
if __name__ == "__main__":
    drafter = GmailDrafter()
    drafter.create_draft("John Doe", "YES", "John wants to purchase the premium plan", "john.doe@example.com")
