#!/usr/bin/env python
"""
Reddit URL Harvester - Usage Examples

Demonstrates the new RedditScraper class-based API
"""

import sys
from pathlib import Path

# Add src to path for this example
sys.path.insert(0, str(Path(__file__).parent / "src"))

from reddit_url_harvester import RedditScraper, scrape_thread


# Example 1: Basic Single URL Scrape


def example_1_basic_scrape():
    """Scrape a single Reddit thread"""
    print("=" * 60)
    print("Example 1: Basic Scrape")
    print("=" * 60)

    scraper = RedditScraper()

    try:
        thread = scraper.scrape("https://reddit.com/r/python/comments/example/")

        print(f"Title: {thread.title}")
        print(f"Author: {thread.author}")
        print(f"Subreddit: r/{thread.subreddit}")
        print(f"Score: {thread.score}")
        print(f"Comments: {len(thread.comments)}")

        if thread.comments:
            print("\nFirst 3 comments:")
            for comment in thread.comments[:3]:
                preview = comment.body[:70].replace("\n", " ")
                print(f"  @{comment.author}: {preview}...")
    except Exception as e:
        print(f"Error: {e}")


# Example 2: Batch Processing Multiple URLs


def example_2_batch_scrape():
    """Scrape multiple URLs efficiently"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Scrape")
    print("=" * 60)

    scraper = RedditScraper()

    urls = [
        "https://reddit.com/r/python/comments/example1/",
        "https://reddit.com/r/python/comments/example2/",
        "https://reddit.com/r/python/comments/example3/",
    ]

    try:
        threads = scraper.scrape_batch(urls)

        print(f"Successfully scraped: {len(threads)}/{len(urls)} threads\n")
        for i, thread in enumerate(threads, 1):
            print(f"  [{i}] r/{thread.subreddit}")
            print(f"      Title: {thread.title}")
            print(f"      Comments: {len(thread.comments)}\n")
    except Exception as e:
        print(f"Error: {e}")


# Example 3: CSV File Processing


def example_3_csv_processing():
    """Process Reddit URLs from a CSV file"""
    print("\n" + "=" * 60)
    print("Example 3: CSV Processing")
    print("=" * 60)

    scraper = RedditScraper()

    try:
        results = scraper.scrape_csv(
            input_file="urls.csv", output_file="results.csv", url_column="URL"
        )

        print(f"\nProcessed {len(results)} URLs")
        print("Results saved to: results.csv")

        if results:
            print("\nFirst result:")
            r = results[0]
            print(f"  URL: {r['url']}")
            print(f"  Title: {r['title']}")
            print(f"  Comments: {r['num_comments']}")
    except Exception as e:
        print(f"Error: {e}")


# Example 4: Custom Configuration with Proxy


def example_4_with_proxy():
    """Use a proxy server for requests"""
    print("\n" + "=" * 60)
    print("Example 4: Proxy Configuration")
    print("=" * 60)

    scraper = RedditScraper(
        timeout=30.0,
        delay=True,
        proxies={
            "http": "http://proxy.example.com:8080",
            "https": "http://proxy.example.com:8080",
        },
    )

    try:
        thread = scraper.scrape("https://reddit.com/r/python/comments/example/")
        print(f"Scraped with proxy: {thread.title}")
        print(f"  Comments: {len(thread.comments)}")
    except Exception as e:
        print(f"Error: {e}")


# Example 5: Dynamic Configuration Changes


def example_5_dynamic_config():
    """Change configuration after initialization"""
    print("\n" + "=" * 60)
    print("Example 5: Dynamic Configuration")
    print("=" * 60)

    scraper = RedditScraper()

    print(f"Initial config:")
    print(f"  timeout: {scraper.timeout}s")
    print(f"  delay: {scraper.delay}")
    print(f"  proxies: {scraper.proxies}")

    # Change settings
    scraper.set_timeout(45.0)
    scraper.set_delay(False)
    scraper.set_proxy({"https": "http://proxy.example.com:8080"})

    print(f"\nUpdated config:")
    print(f"  timeout: {scraper.timeout}s")
    print(f"  delay: {scraper.delay}")
    print(f"  proxies: {scraper.proxies}")


# Example 6: Error Handling


def example_6_error_handling():
    """Handle errors gracefully in batch processing"""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    scraper = RedditScraper()

    urls = [
        "https://reddit.com/r/python/comments/valid1/",
        "https://reddit.com/r/invalid/comments/bad/",  # May fail
        "https://reddit.com/r/python/comments/valid2/",
    ]

    print(f"Processing {len(urls)} URLs with error handling...\n")

    # skip_errors=True means failed URLs won't break the batch
    threads = scraper.scrape_batch(urls, skip_errors=True)

    print(f"\nResult: {len(threads)}/{len(urls)} successful")


# Example 7: Function-Based API (Legacy)


def example_7_function_api():
    """Use the function-based API directly"""
    print("\n" + "=" * 60)
    print("Example 7: Function-Based API (Legacy)")
    print("=" * 60)

    try:
        thread = scrape_thread("https://reddit.com/r/python/comments/example/")

        print(f"Title: {thread.title}")
        print(f"Subreddit: r/{thread.subreddit}")
        print(f"Comments: {len(thread.comments)}")
    except Exception as e:
        print(f"Error: {e}")


# Example 8: Save to JSON


def example_8_save_json():
    """Save scraped data to JSON file"""
    print("\n" + "=" * 60)
    print("Example 8: Save to JSON")
    print("=" * 60)

    import json

    scraper = RedditScraper()

    try:
        thread = scraper.scrape("https://reddit.com/r/python/comments/example/")

        # Convert to dict
        data = {
            "title": thread.title,
            "subreddit": thread.subreddit,
            "author": thread.author,
            "score": thread.score,
            "comments_count": len(thread.comments),
            "comments": [
                {
                    "author": c.author,
                    "body": c.body[:200],  # First 200 chars
                    "score": c.score,
                }
                for c in thread.comments[:10]  # First 10 comments
            ],
        }

        with open("thread_example.json", "w") as f:
            json.dump(data, f, indent=2)

        print(f"Saved to: thread_example.json")
        print(f"Title: {thread.title}")
        print(f"Comments in file: {len(data['comments'])}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\nReddit URL Harvester - Usage Examples")
    print("=" * 60)
    print("\nAvailable examples:\n")
    print("  1. example_1_basic_scrape()        - Scrape a single URL")
    print("  2. example_2_batch_scrape()        - Scrape multiple URLs")
    print("  3. example_3_csv_processing()      - Process URLs from CSV")
    print("  4. example_4_with_proxy()          - Use a proxy server")
    print("  5. example_5_dynamic_config()      - Change config dynamically")
    print("  6. example_6_error_handling()      - Handle errors gracefully")
    print("  7. example_7_function_api()        - Function-based API (legacy)")
    print("  8. example_8_save_json()           - Save results to JSON")
    print("\nTo run an example:")
    print(
        "  python -c 'from examples import example_1_basic_scrape; example_1_basic_scrape()'"
    )
    print()
