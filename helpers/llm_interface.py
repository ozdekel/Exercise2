from openai import OpenAI
from helpers.classifier import validate_category

def generate_cache_key(subject: str, sender: str) -> str:
    return f"{subject}|{sender}"

def process_email_with_cache(subject: str, sender: str, redis_client):
    cache_key = generate_cache_key(subject, sender)

    cached_response = redis_client.get(cache_key)
    if cached_response:
        if isinstance(cached_response, bytes):
            cached_response = cached_response.decode("utf-8")
        try:
            category, priority, requires_response = cached_response.split('|')
            return validate_category(category), priority, requires_response
        except ValueError:
            pass  # Corrupted format, fall back to fresh call

    # If cache miss or corrupted
    openai_client = OpenAI()
    chat_response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful email assistant."},
            {"role": "user", "content": f"Classify the following email:\nSubject: {subject}\nSender: {sender}\n\n"
                                        "Return response with two fields:\n"
                                        "Priority: Low/Normal/Urgent/Important\n"
                                        "Requires Response: Yes/No"}
        ]
    )

    content = chat_response.choices[0].message["content"]

    lines = content.splitlines()
    priority = ""
    requires_response = ""

    for line in lines:
        if line.startswith("Priority:"):
            priority = line.split(":", 1)[1].strip()
        elif line.startswith("Requires Response:"):
            requires_response = line.split(":", 1)[1].strip()

    # Dummy logic to choose category
    category = "Work" if "job" in subject.lower() else "Personal"

    # Cache it
    value = f"{category}|{priority}|{requires_response}"
    redis_client.setex(cache_key, 3600, value)

    return validate_category(category), priority, requires_response
