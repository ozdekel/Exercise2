import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from unittest.mock import patch, MagicMock
from main import fetch_and_classify_emails


@patch("main.plot_email_categories")
@patch("main.classify_with_embedding")
@patch("main.fetch_from_gmail_and_cache")
@patch("main.connect_to_redis")
@patch("main.authenticate")
@patch("main.build")
def test_main_run_end_to_end(mock_build, mock_authenticate, mock_connect_to_redis,
                             mock_fetch_from_gmail_and_cache, mock_classify_with_embedding, mock_plot_chart):
    # 🧠 Fake classification results
    mock_classify_with_embedding.side_effect = ["Work", "Finance", "Spam", "Social", "Updates",
                                                "Work", "Finance", "Spam", "Social", "Updates"]

    # Gmail API mocks
    mock_creds = MagicMock()
    mock_authenticate.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.users().messages().list().execute.return_value = {
        'messages': [{'id': str(i)} for i in range(10)]
    }
    mock_service.users().messages().get.side_effect = lambda userId, id, format: {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': f'Test Subject {id}'},
                {'name': 'From', 'value': f'sender{id}@mail.com'}
            ]
        }
    }

    # ✅ Redis mock with dynamic key-based lookup
    def redis_get_mock(key):
        try:
            i = int(key.split(":")[1])
            return json.dumps({
                "subject": f"Test Subject {i}",
                "sender": f"sender{i}@mail.com"
            })
        except (IndexError, ValueError):
            return None  # simulate missing keys gracefully

    mock_redis = MagicMock()
    mock_redis.get.side_effect = redis_get_mock
    mock_connect_to_redis.return_value = mock_redis

    # 🔁 Run main logic
    fetch_and_classify_emails()

    # ✅ Assert things worked
    assert mock_classify_with_embedding.call_count == 10
    mock_plot_chart.assert_called_once()
