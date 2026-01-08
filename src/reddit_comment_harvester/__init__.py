"""Reddit Comment Harvester - Extract Reddit threads and comments for research and analysis."""

__version__ = "0.1.6"
__author__ = "Wiley"
__email__ = ""

from .scraper import RedditScraper
from .models import Thread, Comment
from .scrape import scrape_thread

__all__ = [
    "RedditScraper",
    "Thread",
    "Comment",
    "scrape_thread",
]
