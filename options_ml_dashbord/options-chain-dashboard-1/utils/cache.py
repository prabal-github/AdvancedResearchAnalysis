from datetime import datetime, timedelta
import os
import json
import pickle

CACHE_DIR = 'cache'
CACHE_EXPIRY = timedelta(minutes=10)

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def cache_set(key, value):
    """Set a value in the cache with a specific key."""
    cache_file = os.path.join(CACHE_DIR, f"{key}.pkl")
    with open(cache_file, 'wb') as f:
        pickle.dump((datetime.now(), value), f)

def cache_get(key):
    """Get a value from the cache by key."""
    cache_file = os.path.join(CACHE_DIR, f"{key}.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            timestamp, value = pickle.load(f)
            if datetime.now() - timestamp < CACHE_EXPIRY:
                return value
            else:
                os.remove(cache_file)  # Remove expired cache
    return None

def clear_cache():
    """Clear all cache files."""
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)
        os.remove(file_path)