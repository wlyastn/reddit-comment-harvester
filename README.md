# Reddit Comment Harvester

A lightweight Python package for analyzing Reddit discussions. Extracts thread data and comments for research and data analysis purposes.

**Disclaimer:** This tool is designed for educational and research purposes only. Users are responsible for ensuring compliance with Reddit's Terms of Service and applicable laws. Always use responsibly and respect rate limits.

## Table of Contents
- [About](#about)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [CSV Format](#csv-format)
- [Rate Limiting & Responsible Use](#rate-limiting--responsible-use)
- [Contributing](#contributing)
- [License](#license)

## About

Reddit Comment Harvester provides a simple, Pythonic interface for extracting Reddit thread and comment data for analysis purposes. This is a research and data analysis tool designed to help researchers study Reddit discussions.

**Important:** This tool should be used in accordance with Reddit's Terms of Service. Always implement responsible scraping practices including reasonable delays between requests and respecting server resources.

## Getting Started

This section covers installation and basic setup.

### Installation

Install via pip:

```bash
pip install reddit-comment-harvester
```

Or install from source:

```bash
git clone https://github.com/wlyastn/reddit-comment-harvester.git
cd reddit-comment-harvester
pip install -e .
```

### Quick Start

Basic usage for extracting thread data:

```python
from reddit_url_harvester import RedditScraper

scraper = RedditScraper()
thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")

print(f"Title: {thread.title}")
print(f"Subreddit: {thread.subreddit}")
print(f"Comments: {len(thread.comments)}")

for comment in thread.comments[:3]:
    print(f"  {comment.author}: {comment.body[:80]}")
```

## Usage

### Scrape a Single Thread

```python
from reddit_url_harvester import RedditScraper

scraper = RedditScraper()
thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
```

### Batch Process Multiple URLs

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

All parameters are optional. Defaults are optimized for reliable and responsible scraping:

```python
scraper = RedditScraper(
    timeout=60.0,           # Request timeout in seconds (default: 60.0)
    delay=True,             # Enable automatic random delays (default: True)
    proxies=None            # Optional proxy config (default: None)
)
```

### Configuration Parameters

**timeout** (float): Request timeout in seconds. Default: 60.0
- Increase for slower connections or larger responses

**delay** (bool): Enable automatic random delays between requests. Default: True
- Recommended to keep enabled for responsible scraping
- Delays typically 2-6 seconds to simulate human behavior

**proxies** (dict): Optional proxy configuration
- Format: `{"https": "http://proxy.example.com:8080"}`

### Updating Configuration

```python
scraper = RedditScraper()

scraper.set_timeout(45.0)
scraper.set_delay(True)
scraper.set_proxy({"https": "http://proxy.example.com:8080"})

thread = scraper.scrape(url)
```

## API Reference

### RedditScraper Class

#### scrape(url: str) -> Thread

Scrape a single Reddit thread or comment.

```python
thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
```

#### scrape_batch(urls: List[str], skip_errors: bool = True) -> List[Thread]

Scrape multiple URLs and return results.

```python
threads = scraper.scrape_batch(urls, skip_errors=True)
```

#### scrape_csv(input_file: str, output_file: Optional[str] = None, url_column: str = "URL", skip_errors: bool = True) -> List[dict]

Scrape URLs from a CSV file and optionally save results.

```python
results = scraper.scrape_csv("urls.csv", output_file="results.csv")
```

### Data Models

#### Thread

Represents a Reddit thread with the following attributes:

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

Represents a comment with the following attributes:

```python
comment.author        # str - Comment author username
comment.body          # str - Comment text/content
comment.score         # int - Comment upvotes/score
comment.timestamp     # str - Comment timestamp
```

## CSV Format

### Input CSV

Format your input file with a header row containing at least a URL column:

```csv
URL
https://reddit.com/r/python/comments/abc123/
https://reddit.com/r/python/comments/def456/
https://reddit.com/r/programming/comments/ghi789/
```

### Output CSV

Results are saved with the following columns:

```csv
url,title,subreddit,post_id,num_comments,author,score
https://reddit.com/r/python/comments/abc123/,Title Here,python,abc123,42,author_name,150
```

## Rate Limiting & Responsible Use

This is a research and data analysis tool. Responsible use is critical:

- Enable automatic delays (default: True) - respects Reddit's servers
- Use reasonable intervals between requests (2-6 second default delays)
- Do not attempt to circumvent rate limiting
- Cache and reuse results when possible
- Monitor for 429 (Too Many Requests) responses and back off
- Do not use this tool to violate Reddit's Terms of Service
- Consider the ethical implications of your research

### Handling Rate Limits

If you encounter 429 errors:

```python
scraper = RedditScraper(delay=True)  # Ensure delay is enabled
# Increase timeout for slower responses
scraper.set_timeout(90.0)
```

### Troubleshooting

**429 Too Many Requests:** Increase delays or add exponential backoff

**Timeout Errors:** Increase the timeout parameter

**SSL Errors:** Try using a proxy or verify your internet connection

## Contributing

Contributions are welcome. Please ensure any contributions maintain responsible scraping practices:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contact & Disclaimer

**Important Disclaimer:** This tool is for educational and research purposes only. Users are solely responsible for:
- Ensuring compliance with Reddit's Terms of Service
- Complying with all applicable laws and regulations in their jurisdiction
- Using this tool responsibly and ethically
- Respecting rate limits and server resources
- Obtaining any necessary permissions before scraping
- Protecting user privacy and data

The creators of this tool are not responsible for misuse or violations of Reddit's Terms of Service. Use at your own risk.
# reddit-comment-harvester
