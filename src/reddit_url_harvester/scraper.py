"""
RedditScraper - Main class for scraping Reddit threads and comments.

Example usage:
    from reddit_url_harvester import RedditScraper

    scraper = RedditScraper()
    thread = scraper.scrape("https://reddit.com/r/example/comments/abc123/")
    print(f"{thread.title}: {len(thread.comments)} comments")
"""

from __future__ import annotations

from typing import Dict, List, Optional
import csv

from .scrape import scrape_thread
from .models import Thread


class RedditScraper:
    """
    Main class for scraping Reddit threads and comments.

    Features:
    - Automatic User-Agent rotation
    - Built-in random delays to avoid detection
    - Optional proxy support
    - Batch processing with error handling
    - CSV file support
    """

    def __init__(
        self,
        timeout: float = 60.0,
        delay: bool = True,
        proxies: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the Reddit scraper.

        Args:
            timeout: Request timeout in seconds (default: 60.0)
            delay: Apply random delays between requests (default: True)
            proxies: Optional proxy configuration (dict with 'http' and/or 'https' keys)

        Example:
            scraper = RedditScraper(
                timeout=30.0,
                delay=True,
                proxies={"https": "http://proxy.example.com:8080"}
            )
        """
        self.timeout = timeout
        self.delay = delay
        self.proxies = proxies

    def scrape(self, url: str) -> Thread:
        """
        Scrape a single Reddit thread or comment.

        Args:
            url: Reddit URL (thread or comment)

        Returns:
            Thread object with title, subreddit, and comments

        Example:
            thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
            print(f"{thread.title}")
            for comment in thread.comments:
                print(f"  {comment.author}: {comment.body}")
        """
        return scrape_thread(
            url,
            timeout=self.timeout,
            proxies=self.proxies,
            delay=self.delay,
        )

    def scrape_batch(
        self,
        urls: List[str],
        skip_errors: bool = True,
    ) -> List[Thread]:
        """
        Scrape multiple URLs and return results.

        Args:
            urls: List of Reddit URLs to scrape
            skip_errors: Skip failed URLs and continue (default: True)

        Returns:
            List of Thread objects

        Example:
            urls = [
                "https://reddit.com/r/python/comments/abc123/",
                "https://reddit.com/r/python/comments/def456/",
            ]
            threads = scraper.scrape_batch(urls)
            print(f"Scraped {len(threads)} threads")
        """
        results = []
        for url in urls:
            try:
                thread = self.scrape(url)
                results.append(thread)
            except Exception as e:
                if skip_errors:
                    print(f"Warning: Failed to scrape {url}: {type(e).__name__}")
                    continue
                else:
                    raise
        return results

    def scrape_csv(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        url_column: str = "URL",
        skip_errors: bool = True,
    ) -> List[dict]:
        """
        Scrape URLs from a CSV file and optionally save results.

        Args:
            input_file: Path to input CSV with URLs
            output_file: Path to save results CSV (optional)
            url_column: Name of column containing URLs (default: "URL")
            skip_errors: Skip failed URLs and continue (default: True)

        Returns:
            List of dicts with thread data

        Example:
            results = scraper.scrape_csv(
                "urls.csv",
                output_file="results.csv",
                url_column="reddit_url"
            )
            print(f"Saved {len(results)} results")
        """
        results = []
        failed = []

        # Read input CSV
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            urls = [row[url_column] for row in reader]

        # Scrape each URL
        for i, url in enumerate(urls, 1):
            print(
                f"[{i}/{len(urls)}] Scraping {url.split('/')[-2]}...",
                end=" ",
                flush=True,
            )

            try:
                thread = self.scrape(url)

                # Convert to dict for CSV output
                result = {
                    "url": thread.url,
                    "title": thread.title,
                    "subreddit": thread.subreddit,
                    "post_id": thread.post_id,
                    "num_comments": len(thread.comments),
                    "author": thread.author,
                    "score": thread.score,
                }
                results.append(result)
                print("OK")

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)[:50]}"
                print(f"FAILED {error_msg}")
                failed.append((url, error_msg))

                if not skip_errors:
                    raise

        # Save results to CSV if output_file specified
        if output_file and results:
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"\nResults saved to {output_file}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"Completed: {len(results)}/{len(urls)} successful")
        if failed:
            print(f"Failed: {len(failed)}")
            for url, error in failed[:3]:
                print(f"  - {url}: {error}")
        print(f"{'='*60}")

        return results

    def set_timeout(self, timeout: float):
        """Change request timeout."""
        self.timeout = timeout

    def set_delay(self, delay: bool):
        """Enable/disable random delays."""
        self.delay = delay

    def set_proxy(self, proxies: Optional[Dict[str, str]]):
        """Set proxy configuration."""
        self.proxies = proxies
