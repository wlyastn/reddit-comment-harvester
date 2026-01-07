from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

from .fetch import fetch_url
from .models import Thread
from .parser import parse_reddit_thread_json


def reddit_json_url(url: str, *, raw_json: bool = True) -> str:
    """
    Convert a Reddit thread/comment URL into the corresponding `.json` URL.

    Examples:
      https://www.reddit.com/r/foo/comments/abc123/title/        -> .../title/.json
      https://www.reddit.com/r/foo/comments/abc123/comment/xyz/  -> .../comment/xyz/.json
    """
    u = url.strip()

    # Remove trailing slash if present
    if u.endswith("/"):
        u = u[:-1]
    
    # Append .json if not already there
    if not u.endswith(".json"):
        u = u + ".json"

    return u


def scrape_thread(
    url: str,
    *,
    timeout: float = 60.0,
    proxies: Optional[Dict[str, str]] = None,
    delay: bool = True,
) -> Thread:
    """
    Fetch a Reddit `.json` endpoint and parse it into a Thread

    Args:
        url: Reddit thread or comment URL
        timeout: Request timeout in seconds
        proxies: Optional proxy configuration (e.g., {"http": "...", "https": "..."})
        delay: Apply random delays between requests to avoid detection (default True)

    Returns:
        Parsed Thread object with comments
    """
    jurl = reddit_json_url(url)
    text, meta = fetch_url(jurl, timeout=timeout, proxies=proxies, delay=delay)

    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON from response. err={e}") from e

    thread = parse_reddit_thread_json(url=url, payload=payload)
    return thread
