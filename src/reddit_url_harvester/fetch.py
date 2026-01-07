from __future__ import annotations

import random
import time
from typing import Dict, Optional, Tuple

import requests


class FetchError(RuntimeError):
    """Error fetching a URL."""
    pass


# User-Agent pool for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Realistic headers to avoid bot detection
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}


class SmartSession:
    """Session with rotation, delays, and realistic behavior."""
    
    def __init__(self):
        self.session = requests.Session()
        self._last_request_time = 0
        self._min_delay = 2.0  # Minimum delay between requests
        self._max_delay = 6.0  # Maximum delay between requests
        self._setup_session()
    
    def _setup_session(self):
        """Configure session with realistic headers."""
        for key, value in DEFAULT_HEADERS.items():
            self.session.headers[key] = value
        self._rotate_user_agent()
    
    def _rotate_user_agent(self):
        """Randomly rotate user agent."""
        self.session.headers["User-Agent"] = random.choice(USER_AGENTS)
    
    def _apply_delay(self):
        """Apply random delay to simulate human behavior."""
        now = time.time()
        elapsed = now - self._last_request_time
        
        # Random jitter between min and max delay
        target_delay = random.uniform(self._min_delay, self._max_delay)
        
        if elapsed < target_delay:
            wait_time = target_delay - elapsed
            time.sleep(wait_time)
        
        self._last_request_time = time.time()
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """GET request with delay and rotation."""
        self._apply_delay()
        self._rotate_user_agent()
        return self.session.get(url, **kwargs)


# Global session instance for connection pooling
_global_session = SmartSession()


def fetch_url(
    url: str,
    *,
    timeout: float = 60.0,
    session: Optional[requests.Session] = None,
    proxies: Optional[Dict[str, str]] = None,
    delay: bool = True,
) -> Tuple[str, Dict]:
    """
    Fetch a URL with bot detection evasion and optional proxy support.

    Features:
    - User-Agent rotation
    - Random delays between requests
    - Realistic HTTP headers
    - Request pooling
    - Optional proxy support

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        session: Optional requests.Session to reuse (uses global pooled session by default)
        proxies: Optional dict of proxy mappings (e.g., {"http": "...", "https": "..."})
        delay: Whether to apply random delays (default True)

    Returns:
        (response_text, meta) where meta contains status info

    Raises:
        FetchError: If the request fails
    """
    sess = session or _global_session
    meta: Dict = {"url": url, "status": "error", "http_status": None}

    try:
        # Apply delay only if using global session and delay is enabled
        if sess is _global_session and delay:
            _global_session._apply_delay()
            _global_session._rotate_user_agent()
        
        resp = sess.get(url, timeout=timeout, proxies=proxies)
        meta["http_status"] = resp.status_code
        resp.raise_for_status()
        meta["status"] = "ok"
        return resp.text, meta
    except Exception as e:
        meta["status"] = "error"
        meta["error"] = str(e)
        raise FetchError(f"Failed to fetch {url}: {e}") from e
