import re
import os
from flask import Flask, render_template
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        import pickle
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        import pickle
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def find_price(text):
    match = re.search(r'[\$₹]\s?\d+(?:,\d{3})*(?:\.\d{2})?', str(text))
    return match.group(0) if match else "N/A"

@app.route('/')
def home():
    print("Connecting to Gmail...")
    service = get_gmail_service()
    
    print("Fetching 10 recent emails...")
    # I removed the 'receipt' filter entirely so it just grabs your 10 newest emails
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    
    print(f"Google found {len(messages)} emails!")
    
    email_data = []
    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = txt['payload']['headers']
        snippet = txt.get('snippet', '')
        
        subject = "No Subject"
        sender = "Unknown"
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']
        
        price = find_price(snippet)
        
        email_data.append({
            'subject': subject, 
            'sender': sender,
            'snippet': snippet,
            'price': price
        })

    print("Sending data to webpage...")
    return render_template('index.html', emails=email_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)