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

def embedding_based_category(subject: str, sender: str) -> str | None:
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

        best_match = max(
            labeled_vectors,
            key=lambda lv: cosine_similarity(email_vector, lv["embedding"])
        )
        return best_match["category"]
    except Exception:
        return None

def keyword_based_category(subject: str, sender: str) -> str:
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    if "iec.co.il" in sender_lower:
        return "Bills"
    if "linkedin.com" in sender_lower:
        return "Work"
    if "@gmail.com" in sender_lower:
        return "Personal"
    if "idf.il" in sender_lower or "זום גדוד" in subject_lower:
        return "Army"

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword.lower())}\b", subject_lower):
                return category

    return "Personal"

def categorize_email(subject: str, sender: str) -> str:
    category = embedding_based_category(subject, sender)
    if category is not None:
        return category
    return keyword_based_category(subject, sender)

def validate_category(category: str) -> str:
    return category if category in CATEGORY_KEYWORDS else "Personal"
