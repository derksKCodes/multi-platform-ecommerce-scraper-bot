import logging
import time
from typing import Callable, Any
from retrying import retry
from functools import wraps
import random

def setup_logging():
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )

def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
    """Decorator for retrying failed operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time:.2f}s")
                    time.sleep(sleep_time)
        return wrapper
    return decorator

def human_delay(min_delay: float = 1.0, max_delay: float = 3.0):
    """Add human-like delay between operations"""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re
    url_pattern = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'(([A-Z0-9]([A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

def read_urls_from_file(file_path: str) -> list:
    """Read URLs from a file"""
    urls = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                url = line.strip()
                if url and validate_url(url):
                    urls.append(url)
    except FileNotFoundError:
        logging.warning(f"File {file_path} not found")
    return urls