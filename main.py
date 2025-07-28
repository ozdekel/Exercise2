import os
import pickle
from collections import Counter
from helpers.auth import authenticate
from helpers.cache import connect_to_redis, process_email_with_cache
from helpers.visualizer import plot_email_categories
from helpers.classifier import categorize_email
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_PATH = "data/email_embeddings.pkl"


def embed_text(text: str) -> list[float]:
    """Generate embedding for a given text using OpenAI."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    from numpy import dot
    from numpy.linalg import norm
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def load_labeled_embeddings():
    with open(EMBEDDING_PATH, "rb") as f:
        return pickle.load(f)


def classify_with_embedding(subject: str, sender: str) -> str:
    """Classify an email using embedding similarity to labeled examples."""
    try:
        labeled = load_labeled_embeddings()
        email_text = f"{sender} {subject}"
        email_vec = embed_text(email_text)

        similarities = [(cosine_similarity(email_vec, item["embedding"]), item["category"])
                        for item in labeled]
        best_match = max(similarities, key=lambda x: x[0])
        return best_match[1]
    except Exception as e:
        print(f"⚠️ Embedding classification failed: {e}")
        return categorize_email(subject, sender)  # fallback


def fetch_emails():
    """Authenticate, fetch emails, classify and visualize."""
    creds = authenticate()
    from googleapiclient.discovery import build
    service = build('gmail', 'v1', credentials=creds)
    redis_conn = connect_to_redis()

    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    categorized = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        headers = msg_detail['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

        category = classify_with_embedding(subject, sender)
        categorized.append(category)

    counter = Counter(categorized)
    plot_email_categories(counter)


if __name__ == "__main__":
    fetch_emails()
