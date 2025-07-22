from gpt4all import GPT4All
from helpers.cache import generate_cache_key
from helpers.classifier import categorize_email, validate_category

def load_gpt4all_model(model_name="Phi-3-mini-4k-instruct.Q4_0.gguf") -> GPT4All:
    """Load the GPT4All model by name."""
    return GPT4All(model_name)

def process_email_with_cache(subject: str, sender: str, llm, redis_client):
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

    # Use keyword logic for category
    category = categorize_email(subject, sender)

    # Query the LLM
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

    # Sanitize LLM output
    valid_priorities = ["Urgent", "Important", "Normal", "Low"]
    priority = next((p for p in valid_priorities if p.lower() in priority.lower()), "Normal")

    valid_responses = ["Yes", "No"]
    requires_response = next((r for r in valid_responses if r.lower() in requires_response.lower()), "No")

    # Cache the results
    redis_client.setex(cache_key, 4 * 60 * 60, f"{category}|{priority}|{requires_response}")
    return category, priority, requires_response
