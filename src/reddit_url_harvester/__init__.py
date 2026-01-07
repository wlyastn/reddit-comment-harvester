"""
Reddit URL Harvester - Scrape Reddit threads and comments easily.

A lightweight Python package that scrapes Reddit threads and comments
without requiring proxies or API keys. Built with automatic bot detection
evasion for reliable, public-friendly scraping.

Getting Started:
    pip install reddit-url-harvester

Class-based usage (recommended):
    from reddit_url_harvester import RedditScraper
    
    scraper = RedditScraper()
    thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
    print(f"{thread.title}: {len(thread.comments)} comments")
    
    # Batch processing
    threads = scraper.scrape_batch([url1, url2, url3])
    
    # CSV file support
    results = scraper.scrape_csv("urls.csv", output_file="results.csv")

Function-based usage:
    from reddit_url_harvester import scrape_thread
    
    thread = scrape_thread("https://reddit.com/r/python/comments/abc123/")
    print(f"Title: {thread.title}")

Features:
- Automatic User-Agent rotation
- Built-in random delays to avoid detection
- Optional proxy support
- Batch processing with error handling
- CSV file support
- Full comment extraction
- No API keys required
"""

from .models import Thread, Comment
from .scrape import scrape_thread
from .fetch import fetch_url
from .scraper import RedditScraper

__version__ = "0.1.0"
__author__ = "Wiley"

__all__ = [
    "RedditScraper",
    "scrape_thread",
    "Thread",
    "Comment",
    "fetch_url",
]
