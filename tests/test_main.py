import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.auth import authenticate
from helpers.llm_interface import load_gpt4all_model, process_email_with_cache
from helpers.cache import connect_to_redis
from helpers.classifier import validate_category
from googleapiclient.discovery import build

def test_real_email_classification():
    # Step 1: Authenticate with Gmail
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    # Step 2: Get the last 10 emails
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    assert messages, "No messages returned from Gmail API."

    # Step 3: Initialize model and Redis
    llm = load_gpt4all_model()
    redis_client = connect_to_redis()

    for msg in messages:
        # Fetch subject & sender
        msg_details = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_details.get('payload', {}).get('headers', [])
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')

        # Process through full pipeline
        category, priority, requires_response = process_email_with_cache(subject, sender, llm, redis_client)

        # Step 4: Assert valid classification
        assert validate_category(category) == category, f"Invalid category: {category}"
        assert priority in ["Urgent", "Important", "Normal", "Low"], f"Invalid priority: {priority}"
        assert requires_response in ["Yes", "No"], f"Invalid requires_response: {requires_response}"

        print(f"[PASS] {subject[:30]}... → {category}, {priority}, response: {requires_response}")
