import os
import redis
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gpt4all import GPT4All
import hashlib

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    """Authenticate and return Gmail API credentials."""
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secret_file = r'C:\Users\user\Desktop\Year C\Software development using AI\Assignment 1_exercise 2\client_secret.json'
            if not os.path.exists(client_secret_file):
                raise FileNotFoundError(f"Error: '{client_secret_file}' not found.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def load_gpt4all_model():
    """Load the GPT4All model."""
    model_name = "Phi-3-mini-4k-instruct.Q4_0.gguf"
    return GPT4All(model_name)

def connect_to_redis():
    """Connect to the Redis database."""
    redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
    try:
        redis_client.ping()
        print("Connected to Redis.")
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
        exit(1)
    return redis_client

def generate_cache_key(subject, sender):
    """Generate a unique cache key using subject and sender."""
    data = f"{subject}:{sender}"
    return hashlib.sha256(data.encode()).hexdigest()

def parse_llm_response(response):
    """
    Parse the LLM response and extract Category, Priority, and Requires Response fields.
    """
    category = "Unknown"
    priority = "Normal"
    requires_response = "No"

    # Debug the raw response
    print(f"Raw response from LLM:\n{response}")

    # Filter and extract relevant lines
    lines = [line.strip() for line in response.split("\n") if ":" in line]
    for line in lines:
        if "Category:" in line:
            category = line.split(":", 1)[1].strip()
        elif "Priority:" in line:
            priority = line.split(":", 1)[1].strip()
        elif "Requires Response:" in line:
            requires_response = line.split(":", 1)[1].strip()

    return category, priority, requires_response

def validate_response(category, priority, requires_response):
    """
    Validate the extracted values and ensure they are within the expected ranges.
    """
    valid_categories = {"Work", "Bills", "Personal", "Shopping", "Notifications", "Promotions", "Entertainment", "School", "Travel", "Other"}
    valid_priorities = {"Urgent", "Important", "Normal", "Low"}
    valid_responses = {"Yes", "No"}

    if category not in valid_categories:
        print(f"Invalid category: {category}. Defaulting to 'Unknown'.")
        category = "Unknown"
    if priority not in valid_priorities:
        print(f"Invalid priority: {priority}. Defaulting to 'Normal'.")
        priority = "Normal"
    if requires_response not in valid_responses:
        print(f"Invalid response: {requires_response}. Defaulting to 'No'.")
        requires_response = "No"

    return category, priority, requires_response

def process_email_with_cache(subject, sender, llm, redis_client):
    """
    Check Redis cache for the LLM response. If not found, query the LLM and cache the response.
    """
    cache_key = generate_cache_key(subject, sender)

    # Check if the response is already cached
    cached_response = redis_client.get(cache_key)
    if cached_response:
        print(f"Cached response: {cached_response}")
        try:
            category, priority, requires_response = cached_response.split('|')
            return category, priority, requires_response
        except ValueError as e:
            print(f"Error unpacking cached response: {e}. Cached response: {cached_response}")
            redis_client.delete(cache_key)

    # If not cached or cache is invalid, query the LLM
    prompt = f"""
    You are an AI email classifier. Analyze the following email details:

    Subject: {subject}
    Sender: {sender}

    Provide the result exactly in this format:
    Category: <One of: Work, Bills, Personal, Shopping, Notifications, Promotions, Entertainment, School, Travel, Other>
    Priority: <One of: Urgent, Important, Normal, Low>
    Requires Response: <Yes or No>

    Do not add extra text or comments. Only return the three fields exactly as described.
    """
    response = llm.generate(prompt, max_tokens=100).strip()
    category, priority, requires_response = parse_llm_response(response)
    category, priority, requires_response = validate_response(category, priority, requires_response)

    # Cache the response for 4 hours
    redis_client.setex(cache_key, 4 * 60 * 60, f"{category}|{priority}|{requires_response}")
    return category, priority, requires_response

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

        for msg in messages:
            msg_details = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_details.get('payload', {}).get('headers', [])
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
            
            category, priority, requires_response = process_email_with_cache(subject, sender, llm, redis_client)
            
            print(f"From: {sender}")
            print(f"Subject: {subject}")
            print(f"Category: {category}")
            print(f"Priority: {priority}")
            print(f"Requires Response: {requires_response}")
            print()
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    fetch_emails()
