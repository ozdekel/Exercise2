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

    # Setup Gmail service mock chain
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_list = MagicMock()

    mock_service.users.return_value = mock_users
    mock_users.messages.return_value = mock_messages
    mock_messages.list.return_value = mock_list
    mock_list.execute.return_value = {
        'messages': [{'id': '111'}, {'id': '222'}]
    }

    mock_messages.get.side_effect = lambda userId, id, format: {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': f'Test Subject {id}'},
                {'name': 'From', 'value': f'sender{id}@mail.com'}
            ]
        }
    }

    # Mock Redis and classification
    mock_connect_to_redis.return_value = MagicMock()
    mock_process_email_with_cache.return_value = ("Work", "Important", "Yes")

    fetch_emails()

    assert mock_process_email_with_cache.call_count == 2
    mock_plot_chart.assert_called_once()
