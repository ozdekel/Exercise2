import redis
import hashlib

def connect_to_redis(host='localhost', port=6379) -> redis.StrictRedis:
    """Connect to the Redis database."""
    redis_client = redis.StrictRedis(host=host, port=port, decode_responses=True)
    try:
        redis_client.ping()
        print("Connected to Redis.")
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
        exit(1)
    return redis_client

def generate_cache_key(subject: str, sender: str) -> str:
    """Generate a unique cache key using subject and sender."""
    data = f"{subject}:{sender}"
    return hashlib.sha256(data.encode()).hexdigest()
