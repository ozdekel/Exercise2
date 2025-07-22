
from googleapiclient.discovery import build
from helpers.auth import authenticate
from helpers.llm_interface import load_gpt4all_model, process_email_with_cache
from helpers.cache import connect_to_redis, generate_cache_key
from helpers.classifier import categorize_email, validate_category
from helpers.visualizer import plot_email_categories


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
def fetch_emails():
    """Fetch and process emails from Gmail."""
    try:
        creds = authenticate()
        if not creds:
            print("Authentication failed.")
            return
        
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found.")
            return
        
        llm = load_gpt4all_model()
        redis_client = connect_to_redis()

        categories_count = {}

        for msg in messages:
            msg_details = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_details.get('payload', {}).get('headers', [])
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
            
            category, priority, requires_response = process_email_with_cache(subject, sender, llm, redis_client)
            categories_count[category] = categories_count.get(category, 0) + 1

            print(f"From: {sender}")
            print(f"Subject: {subject}")
            print(f"Category: {category}")
            print(f"Priority: {priority}")
            print(f"Requires Response: {requires_response}")
            print()
        
        # Plot the categories distribution
        plot_email_categories(categories_count)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    fetch_emails()
