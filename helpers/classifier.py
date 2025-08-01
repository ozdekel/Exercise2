import os
import re
import pickle
import numpy as np

CATEGORY_KEYWORDS = {
    "Army": ["גדוד", "military", "army", "חיל", "קרבי", "מילואים", "זום"],
    "Work": ["LinkedIn", "job", "recruitment", "career", "משרה", "עבודה", "profile", "invitation"],
    "Bills": ["invoice", "bill", "payment", "receipt", "חשבון", "חשמל", "שירות", "אישור"],
    "Personal": ["birthday", "party", "family", "יום הולדת", "משפחה"],
    "Shopping": ["order", "purchase", "cart", "עגלה", "רכישה", "הזמנה"],
    "University": ["presentation", "deck", "class", "assignment", "university", "אוניברסיטה", "קורס"],
    "Entertainment": ["movie", "concert", "festival", "event", "זום", "אירוע", "invitation"],
    "Notifications": ["notification", "alert", "reminder", "התראה", "תזכורת"],
    "Promotions": ["sale", "discount", "offer", "מבצע", "הנחה", "הצעה"],
}

try:
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    openai_client = None

def load_embeddings(path="data/email_embeddings.pkl"):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def score_keyword_match(subject: str, sender: str, category: str) -> float:
    text = f"{subject} {sender}".lower()
    keywords = CATEGORY_KEYWORDS.get(category, [])
    return sum(1 for kw in keywords if kw.lower() in text) * 0.02  # each match adds 0.02 to score

def combined_category(subject: str, sender: str) -> str | None:
    if openai_client is None:
        return None

    try:
        email_text = f"{sender} {subject}"
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=email_text
        )
        email_vector = response.data[0].embedding

        labeled_vectors = load_embeddings()
        if labeled_vectors is None:
            return None

        scored = []
        for item in labeled_vectors:
            sim = cosine_similarity(email_vector, item["embedding"])
            boost = score_keyword_match(subject, sender, item["category"])
            scored.append((sim + boost, item["category"]))

        best_match = max(scored, key=lambda x: x[0])
        return best_match[1]

    except Exception:
        return None

def keyword_based_category(subject: str, sender: str) -> str:
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in subject_lower or keyword.lower() in sender_lower:
                return category

    return "Personal"

def categorize_email(subject: str, sender: str) -> str:
    category = combined_category(subject, sender)
    if category is not None:
        return category
    return keyword_based_category(subject, sender)

def validate_category(category: str) -> str:
    return category if category in CATEGORY_KEYWORDS else "Personal"
