import json
import pickle
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_PATH = "data/labeled_emails.json"
OUTPUT_PATH = "data/email_embeddings.pkl"

def load_emails():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def create_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def main():
    emails = load_emails()
    labeled_vectors = []

    for email in emails:
        full_text = f"{email['from']} {email['subject']}"
        embedding = create_embedding(full_text)
        labeled_vectors.append({
            "category": email["category"],
            "embedding": embedding,
            "text": full_text
        })

    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(labeled_vectors, f)

    print(f"✅ Saved {len(labeled_vectors)} embeddings to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
