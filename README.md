# Reddit URL Harvester

**Reddit URL Harvester** is a lightweight Python package that scrapes Reddit threads and comments without requiring API keys or proxies. Built with automatic bot detection evasion for reliable scraping.

## About

Reddit URL Harvester provides a simple, Pythonic interface for extracting Reddit thread and comment data. No API keys, no registration, no complexity - just straightforward scraping.

**Features:**
- No API Key Required
- Bot Detection Evasion (User-Agent rotation, realistic headers, automatic delays)
- Optional Proxy Support
- Batch Processing with Error Handling
- CSV File Support
- Full Comment Extraction
- Connection Pooling & Efficient Session Reuse

## Installation

Install via pip:

```bash
pip install reddit-url-harvester
```

Or install from source:

```bash
git clone https://github.com/yourusername/reddit-url-harvester.git
cd reddit-url-harvester
pip install -e .
```

## Quick Start

### Basic Usage with RedditScraper

```python
from reddit_url_harvester import RedditScraper

scraper = RedditScraper()
thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")

print(f"{thread.title}")
print(f"Subreddit: {thread.subreddit}")
print(f"Comments: {len(thread.comments)}")

for comment in thread.comments[:3]:
    print(f"  {comment.author}: {comment.body[:80]}")
```

### Batch Processing URLs

```python
from reddit_url_harvester import RedditScraper

scraper = RedditScraper()

urls = [
    "https://reddit.com/r/python/comments/abc123/",
    "https://reddit.com/r/python/comments/def456/",
    "https://reddit.com/r/python/comments/ghi789/",
]

threads = scraper.scrape_batch(urls)
print(f"Scraped {len(threads)} threads")
```

### Process URLs from CSV

```python
from reddit_url_harvester import RedditScraper

scraper = RedditScraper()

results = scraper.scrape_csv(
    input_file="urls.csv",
    output_file="results.csv",
    url_column="URL"
)

print(f"Saved {len(results)} results to results.csv")
```

## Configuration

### RedditScraper Parameters

All parameters are optional. Defaults are optimized for reliable scraping:

```python
scraper = RedditScraper(
    timeout=60.0,           # Request timeout in seconds (default: 60.0)
    delay=True,             # Enable automatic random delays (default: True)
    proxies=None            # Optional proxy config (default: None)
)
```

### Example with Proxy

```python
scraper = RedditScraper(
    timeout=30.0,
    delay=True,
    proxies={"https": "http://proxy.example.com:8080"}
)

thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
```

### Changing Configuration

```python
scraper = RedditScraper()

scraper.set_timeout(45.0)
scraper.set_delay(False)
scraper.set_proxy({"http": "http://proxy.example.com:8080"})

thread = scraper.scrape(url)
```

## API Reference

### RedditScraper Class

#### `scrape(url: str) -> Thread`

Scrape a single Reddit thread or comment.

```python
thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
```

#### `scrape_batch(urls: List[str], skip_errors: bool = True) -> List[Thread]`

Scrape multiple URLs and return results.

```python
threads = scraper.scrape_batch(urls, skip_errors=True)
```

#### `scrape_csv(input_file: str, output_file: Optional[str] = None, url_column: str = "URL", skip_errors: bool = True) -> List[dict]`

Scrape URLs from a CSV file and optionally save results.

```python
results = scraper.scrape_csv("urls.csv", output_file="results.csv")
```

### Data Models

#### Thread

```python
thread.title          # str - Thread title
thread.subreddit      # str - Subreddit name
thread.author         # str - Post author username
thread.url            # str - Full Reddit URL
thread.post_id        # str - Reddit post ID
thread.score          # int - Post upvotes/score
thread.comments       # List[Comment] - List of comments
```

#### Comment

```python
comment.author        # str - Comment author username
comment.body          # str - Comment text/content
comment.score         # int - Comment upvotes/score
comment.timestamp     # str - Comment timestamp
```

## Function-Based API (Legacy)

If you prefer the function-based interface:

```python
from reddit_url_harvester import scrape_thread

thread = scrape_thread("https://reddit.com/r/python/comments/abc123/")
```

## How Bot Detection Evasion Works

**User-Agent Rotation:** Automatically rotates between 8 realistic user agents (Windows/Mac/Linux, Chrome/Firefox/Edge/Safari)

**Realistic Headers:** Includes Accept, Accept-Language, DNT, and Sec-Fetch-* headers

**Automatic Delays:** 2-6 second random delays between requests to simulate human behavior

**Connection Pooling:** Reuses HTTP connections efficiently while maintaining realistic patterns

This approach allows reliable scraping without proxy services or API keys.

## CSV Format

**Input CSV** (`urls.csv`):

```csv
URL
https://reddit.com/r/python/comments/abc123/
https://reddit.com/r/python/comments/def456/
https://reddit.com/r/programming/comments/ghi789/
```

**Output CSV** (`results.csv`):

```csv
url,title,subreddit,post_id,num_comments,author,score
https://reddit.com/r/python/comments/abc123/,Title Here,python,abc123,42,author_name,150
...
```

## Rate Limiting & Responsible Use

**Important:** Respect Reddit's Terms of Service

- Use reasonable delays (default 2-6 seconds is good)
- Don't hammer Reddit's servers
- Consider implementing backoff strategies for production use
- Cache results when possible
- Monitor for 429 (Too Many Requests) responses

## Examples

See [examples.py](examples.py) for more detailed usage examples.

## Troubleshooting

### 429 Too Many Requests

Increase delays or add proxy support:

```python
scraper = RedditScraper(delay=True)  # Ensure delay is enabled
```

### Timeout Errors

Increase the timeout:

```python
scraper = RedditScraper(timeout=90.0)
thread = scraper.scrape(url)
```

### SSL Errors

Consider using a proxy or try again later.

## Contributing

Contributions welcome! 

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Disclaimer

This tool is for educational and research purposes. Users are responsible for ensuring their use of this tool complies with Reddit's Terms of Service and applicable laws in their jurisdiction.
# reddit-comment-harvester
