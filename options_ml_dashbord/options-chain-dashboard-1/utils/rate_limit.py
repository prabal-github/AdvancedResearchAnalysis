from flask import request, g
import time

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # max requests per window

# In-memory store for rate limiting
rate_limit_store = {}

def rate_limit():
    user_key = _get_user_key()
    current_time = time.time()

    if user_key not in rate_limit_store:
        rate_limit_store[user_key] = []

    # Remove timestamps that are outside the rate limit window
    rate_limit_store[user_key] = [timestamp for timestamp in rate_limit_store[user_key] if current_time - timestamp < RATE_LIMIT_WINDOW]

    if len(rate_limit_store[user_key]) >= RATE_LIMIT_MAX_REQUESTS:
        return False  # Rate limit exceeded

    # Record the current request timestamp
    rate_limit_store[user_key].append(current_time)
    return True

def _get_user_key():
    """Return a unique key for the user based on their session or IP address."""
    return request.remote_addr  # You can customize this to include session info if needed