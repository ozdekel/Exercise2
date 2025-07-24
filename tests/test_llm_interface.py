import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from helpers.llm_interface import process_email_with_cache, generate_cache_key
from helpers.classifier import validate_category

@pytest.fixture
def fake_redis():
    """Mocked Redis client using in-memory dictionary."""
    store = {}

    class FakeRedis:
        def get(self, key):
            return store.get(key)

        def setex(self, key, time, value):
            store[key] = value

        def delete(self, key):
            store.pop(key, None)

    return FakeRedis()

@patch("helpers.llm_interface.OpenAI")
def test_process_email_with_cache_cached(mock_openai_class, fake_redis):
    subject = "Your job alert"
    sender = "jobs@example.com"
    redis_key = generate_cache_key(subject, sender)

    fake_redis.setex(redis_key, 3600, "Work|Important|Yes")

    category, priority, response = process_email_with_cache(subject, sender, fake_redis)

    assert category == validate_category("Work")
    assert priority == "Important"
    assert response == "Yes"
    mock_openai_class.return_value.chat.completions.create.assert_not_called()

@patch("helpers.llm_interface.OpenAI")
def test_process_email_with_cache_uncached(mock_openai_class, fake_redis):
    subject = "New feature updates"
    sender = "update@example.com"

    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(message={"content": "Priority: Normal\nRequires Response: No"})
        ]
    )

    category, priority, response = process_email_with_cache(subject, sender, fake_redis)

    assert category in ["Personal", "Work", "Notifications"]
    assert priority == "Normal"
    assert response == "No"
    mock_client.chat.completions.create.assert_called_once()

@patch("helpers.llm_interface.OpenAI")
def test_process_email_with_cache_invalid_cached_value(mock_openai_class, fake_redis):
    subject = "Reminder"
    sender = "reminder@example.com"
    redis_key = generate_cache_key(subject, sender)

    fake_redis.setex(redis_key, 3600, "invalid_value")

    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(message={"content": "Priority: Urgent\nRequires Response: Yes"})
        ]
    )

    category, priority, response = process_email_with_cache(subject, sender, fake_redis)

    assert category in ["Personal", "Work", "Notifications"]
    assert priority == "Urgent"
    assert response == "Yes"
    mock_client.chat.completions.create.assert_called_once()
