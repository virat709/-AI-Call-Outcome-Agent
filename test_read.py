import sys
import io

# Force utf-8 for stdout just in case
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from watcher import DriveWatcher
from main import process_call

watcher = DriveWatcher()
print("Reading doc: 1m0rvn6UsGWqr6gsDjKdPcK7WVPjz5bBMIYg4qa7GV34")
text = watcher.read_document_text("1m0rvn6UsGWqr6gsDjKdPcK7WVPjz5bBMIYg4qa7GV34")
print("Extracted Text Length:", len(text))

print("\nPassing to process_call...")
process_call(text, recipient_email="")
