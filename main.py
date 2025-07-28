import os
import pickle
import json
from collections import Counter
from dotenv import load_dotenv
from openai import OpenAI
from helpers.classifier import categorize_email
from helpers.cache import connect_to_redis
from helpers.visualizer import plot_email_categories
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_PATH = "data/email_embeddings.pkl"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = "token.json"
CREDS_FILE = "client_secret.json"


def embed_text(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(vec1, vec2):
    from numpy import dot
    from numpy.linalg import norm
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def load_labeled_embeddings():
    with open(EMBEDDING_PATH, "rb") as f:
        return pickle.load(f)


def classify_with_embedding(subject: str, sender: str) -> str:
    try:
        labeled = load_labeled_embeddings()
        email_text = f"{sender} {subject}"
        email_vec = embed_text(email_text)

        similarities = [
            (cosine_similarity(email_vec, item["embedding"]), item["category"])
            for item in labeled
        ]
        best_match = max(similarities, key=lambda x: x[0])
        return best_match[1]
    except Exception as e:
        print(f"⚠️ Embedding classification failed: {e}")
        return categorize_email(subject, sender)


def authenticate():
    creds = None

    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"⚠️ Failed to load token: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def fetch_from_gmail_and_cache(redis_conn):
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    for i, msg in enumerate(messages):
        detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        headers = detail.get("payload", {}).get("headers", [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
        redis_conn.set(f"email:{i}", json.dumps({"subject": subject, "sender": sender}))


def fetch_and_classify_emails():
    redis_conn = connect_to_redis()
    print("\nConnected to Redis.")

    # Check if emails exist
    missing_keys = [f"email:{i}" for i in range(10) if not redis_conn.get(f"email:{i}")]
    if missing_keys:
        print("🔁 Fetching emails from Gmail because Redis is empty or incomplete...")
        fetch_from_gmail_and_cache(redis_conn)

    categorized = []
    print("\n📬 Classifying last 10 cached emails:\n")

    for i in range(10):
        key = f"email:{i}"
        data = redis_conn.get(key)
        if not data:
            print(f"⚠️ No email found for key: {key}")
            continue

        email = json.loads(data)
        subject = email.get("subject", "")
        sender = email.get("sender", "")

        category = classify_with_embedding(subject, sender)
        categorized.append(category)

        print(f"📧 Subject: {subject}\n👤 From: {sender}\n🧠 Category: {category}\n")

    counter = Counter(categorized)
    plot_email_categories(counter)


if __name__ == "__main__":
    fetch_and_classify_emails()
