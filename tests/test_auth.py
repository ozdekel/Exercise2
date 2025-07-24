import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from helpers.auth import authenticate


@patch("helpers.auth.os.path.exists")
@patch("helpers.auth.Credentials.from_authorized_user_file")
@patch("helpers.auth.Request")
def test_authenticate_with_expired_token_refresh(mock_request, mock_from_file, mock_exists):
    mock_exists.side_effect = [True, True]
    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = "refresh"
    mock_creds.to_json.return_value = '{"mock": "json"}'
    mock_from_file.return_value = mock_creds

    creds = authenticate()
    assert creds is mock_creds


@patch("helpers.auth.os.path.exists")
@patch("helpers.auth.Credentials.from_authorized_user_file")
def test_authenticate_with_valid_token(mock_from_file, mock_exists):
    mock_exists.side_effect = [True]
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_from_file.return_value = mock_creds

    creds = authenticate()
    assert creds is mock_creds


@patch("helpers.auth.os.path.exists")
def test_authenticate_missing_secret_raises(mock_exists):
    mock_exists.side_effect = [False, False]

    with pytest.raises(FileNotFoundError):
        authenticate()


@patch("helpers.auth.os.path.exists")
@patch("helpers.auth.Credentials.from_authorized_user_file")
@patch("helpers.auth.InstalledAppFlow.from_client_secrets_file")
def test_authenticate_with_user_flow(mock_flow, mock_from_file, mock_exists):
    mock_exists.side_effect = [False, True]
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.to_json.return_value = '{"mock": "json"}'
    mock_instance = MagicMock()
    mock_instance.run_local_server.return_value = mock_creds
    mock_flow.return_value = mock_instance

    creds = authenticate()
    assert creds is mock_creds
