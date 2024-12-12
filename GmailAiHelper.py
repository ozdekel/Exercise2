import os
import redis
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gpt4all import GPT4All
import hashlib
import matplotlib.pyplot as plt
import re

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

CATEGORY_KEYWORDS = {
    "Army": ["גדוד", "military", "army", "חיל", "קרבי", "מילואים", "זום"],
    "Work": ["LinkedIn", "job", "recruitment", "career", "משרה", "עבודה", "profile", "invitation"],
    "Bills": ["invoice", "bill", "payment", "receipt", "חשבון", "חשמל", "שירות", "אישור"],
    "Personal": ["birthday", "party", "family", "יום הולדת", "משפחה"],
    "Shopping": ["order", "purchase", "cart", "עגלה", "רכישה", "הזמנה"],
    "University": ["presentation", "deck", "class", "assignment", "university", "אוניברסיטה"],
    "Entertainment": ["movie", "concert", "festival", "event", "זום", "אירוע", "invitation"],
    "Notifications": ["notification", "alert", "reminder", "התראה", "תזכורת"],
    "Promotions": ["sale", "discount", "offer", "מבצע", "הנחה", "הצעה"],
}

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

def categorize_email(subject, sender):
    """Categorize email based on keywords and specific sender-based rules."""
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    # Sender-based rules
    if "iec.co.il" in sender_lower:
        return "Bills"
    if "linkedin.com" in sender_lower:
        return "Work"
    if "@gmail.com" in sender_lower:
        return "Personal"
    if "idf.il" in sender_lower or "זום גדוד" in subject_lower:
        return "Army"

    # Keyword-based categorization
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword.lower())}\b", subject_lower):
                return category

    # Fallback to Personal if no category matches
    return "Personal"

def validate_category(category):
    """Ensure the category is valid and fallback if necessary."""
    valid_categories = set(CATEGORY_KEYWORDS.keys())
    if category not in valid_categories:
        return "Personal"
    return category

def process_email_with_cache(subject, sender, llm, redis_client):
    """
    Check Redis cache for the LLM response. If not found, query the LLM and cache the response.
    """
    cache_key = generate_cache_key(subject, sender)

    # Check if the response is already cached
    cached_response = redis_client.get(cache_key)
    if cached_response:
        try:
            category, priority, requires_response = cached_response.split('|')
            category = validate_category(category)
            return category, priority, requires_response
        except ValueError:
            redis_client.delete(cache_key)

    # Use generalized keyword mapping for category
    category = categorize_email(subject, sender)

    # Query the LLM for priority and response requirement
    prompt = f"""
    Analyze the following email details:
    Subject: {subject}
    Sender: {sender}

    Provide results in this format:
    Priority: <One of: Urgent, Important, Normal, Low>
    Requires Response: <Yes or No>
    """
    response = llm.generate(prompt, max_tokens=100).strip()
    lines = response.split("\n")
    priority = "Normal"
    requires_response = "No"

    for line in lines:
        if "Priority:" in line:
            priority = line.split(":", 1)[1].strip()
        elif "Requires Response:" in line:
            requires_response = line.split(":", 1)[1].strip()

    # Cache the results
    redis_client.setex(cache_key, 4 * 60 * 60, f"{category}|{priority}|{requires_response}")
    return category, priority, requires_response

def plot_email_categories(categories_count):
    """Plot a pie chart of email categories."""
    labels = list(categories_count.keys())
    sizes = list(categories_count.values())
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Email Categories Distribution")
    plt.show(block=True)

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
