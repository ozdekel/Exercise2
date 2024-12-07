import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the required Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    """Authenticate and return Gmail API credentials."""
    creds = None

    # Check if token.json already exists for cached credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, initiate the OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Specify the correct path to your JSON file
            client_secret_file = r'C:\Users\user\Desktop\Year C\Software development using AI\Assignment 1\Gmail AI helper\client_secret.json'
            
            # Debugging: Check if the file exists
            if not os.path.exists(client_secret_file):
                raise FileNotFoundError(f"Error: '{client_secret_file}' not found in the directory '{os.getcwd()}'. Please ensure the file is present and named correctly.")
            
            print(f"Found client secret file: {client_secret_file}")
            
            # Initiate the OAuth2 flow
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def fetch_emails():
    """Fetch and print emails from Gmail."""
    try:
        # Authenticate and create the Gmail API service
        creds = authenticate()
        if not creds:
            print("Authentication failed.")
            return
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Fetch a list of messages
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found.")
            return
        
        print("Messages:")
        for msg in messages:
            # Fetch the details of each message
            msg_details = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_details.get('payload', {}).get('headers', [])
            
            # Extract subject and sender from headers
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
            
            print(f"From: {sender}")
            print(f"Subject: {subject}")
            print("-" * 40)
    
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    fetch_emails()
    
