import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from main import fetch_emails


@patch("main.plot_email_categories")
@patch("main.process_email_with_cache")
@patch("main.connect_to_redis")
@patch("main.authenticate")
@patch("main.build")
def test_main_run_end_to_end(mock_build, mock_authenticate, mock_connect_to_redis,
                             mock_process_email_with_cache, mock_plot_chart):
    # Mock credentials
    mock_creds = MagicMock()
    mock_authenticate.return_value = mock_creds

    # Mock Gmail service
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_service.users().messages().list().execute.return_value = {
        'messages': [{'id': '111'}, {'id': '222'}]
    }

    def mock_get(userId, id, format):
        return {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': f'Test Subject {id}'},
                    {'name': 'From', 'value': f'sender{id}@mail.com'}
                ]
            }
        }

    mock_service.users().messages().get.side_effect = mock_get

    # Mock Redis and classification logic
    mock_connect_to_redis.return_value = MagicMock()
    mock_process_email_with_cache.return_value = ("Work", "Important", "Yes")

    fetch_emails()

    # Validation
    assert mock_process_email_with_cache.call_count == 2
    mock_plot_chart.assert_called_once()
