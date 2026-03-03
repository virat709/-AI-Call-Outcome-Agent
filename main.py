import argparse
from analyzer import TranscriptAnalyzer
from database import SheetsLogger
from mailer import GmailDrafter

def process_call(transcript: str, recipient_email: str = ""):
    print(f"--- Processing Call ---")
    
    print("1. Analyzing Transcript...")
    analyzer = TranscriptAnalyzer()
    analysis_result = analyzer.analyze(transcript)
    outcome = analysis_result.get("outcome")
    summary = analysis_result.get("summary")
    client_name = analysis_result.get("client_name", "Client")
    client_email = analysis_result.get("client_email", "")
    
    safe_name = str(client_name).encode('ascii', 'ignore').decode('ascii')
    safe_outcome = str(outcome).encode('ascii', 'ignore').decode('ascii')
    safe_summary = str(summary).encode('ascii', 'ignore').decode('ascii')
    
    print(f"   Extracted Name: {safe_name}")
    print(f"   Outcome: {safe_outcome}")
    print(f"   Summary: {safe_summary}")
    
    print("2. Creating Email Draft...")
    mailer = GmailDrafter()
    
    # Use the extracted email if available, otherwise fallback to the provided recipient_email
    final_email = client_email if client_email else recipient_email
    
    email_status = mailer.create_draft(safe_name, outcome, summary, final_email)
    safe_email_status = str(email_status).encode('ascii', 'ignore').decode('ascii')
    print(f"   Email Status: {safe_email_status}")
    
    print("3. Logging to Database...")
    logger = SheetsLogger()
    logger.log_call(safe_name, outcome, summary, email_status)
    print("--- Processing Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Call Outcome Agent")
    parser.add_argument("--transcript", type=str, required=True, help="Path to transcript file or direct text. Direct text preferred for test runs.")
    parser.add_argument("--email", type=str, default="", help="Optional: Client's Email Address (Will be blank in draft if omitted)")
    
    args = parser.parse_args()
    
    # Simple check if transcript is a file path or direct text
    transcript_text = args.transcript
    import os
    if os.path.exists(args.transcript):
        with open(args.transcript, 'r') as f:
            transcript_text = f.read()

    process_call(transcript_text, args.email)
