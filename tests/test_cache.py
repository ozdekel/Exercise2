import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from redis.exceptions import ConnectionError as RedisConnectionError
from helpers.cache import connect_to_redis, generate_cache_key


def test_generate_cache_key_is_consistent():
    subject = "Test Subject"
    sender = "sender@example.com"
    key1 = generate_cache_key(subject, sender)
    key2 = generate_cache_key(subject, sender)
    assert key1 == key2
    assert isinstance(key1, str)
    assert len(key1) == 64  # SHA-256 hash length


@patch("helpers.cache.redis.StrictRedis")
def test_connect_to_redis_success(mock_redis_class):
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    mock_redis_class.return_value = mock_redis

    client = connect_to_redis()
    assert client is mock_redis
    mock_redis.ping.assert_called_once()


@patch("helpers.cache.redis.StrictRedis")
def test_connect_to_redis_failure(mock_redis_class, capsys):
    mock_redis = MagicMock()
    mock_redis.ping.side_effect = RedisConnectionError("Connection failed")
    mock_redis_class.return_value = mock_redis

    with pytest.raises(SystemExit):
        connect_to_redis()

    captured = capsys.readouterr()
    assert "Redis connection error" in captured.out


def test_generate_cache_key_different_inputs():
    key1 = generate_cache_key("Subject A", "sender@example.com")
    key2 = generate_cache_key("Subject B", "sender@example.com")
    key3 = generate_cache_key("Subject A", "other@example.com")
    assert key1 != key2
    assert key1 != key3
    assert key2 != key3
