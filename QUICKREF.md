# Quick Reference Guide

## Installation

```bash
pip install reddit-url-harvester
```

## Import

```python
from reddit_url_harvester import RedditScraper, scrape_thread
```

## Class-Based API (Recommended)

### Initialize

```python
scraper = RedditScraper(
    timeout=60.0,           # Request timeout in seconds
    delay=True,             # Enable automatic random delays
    proxies=None            # Optional proxy dict
)
```

### Scrape a Single URL

```python
thread = scraper.scrape("https://reddit.com/r/python/comments/abc123/")
print(thread.title)
print(f"Comments: {len(thread.comments)}")
```

### Scrape Multiple URLs

```python
urls = ["https://reddit.com/r/...", "https://reddit.com/r/...", ...]
threads = scraper.scrape_batch(urls)
print(f"Scraped {len(threads)} threads")
```

### Process CSV File

```python
results = scraper.scrape_csv(
    input_file="urls.csv",
    output_file="results.csv",
    url_column="URL"
)
```

### Update Configuration

```python
scraper.set_timeout(45.0)
scraper.set_delay(False)
scraper.set_proxy({"https": "http://proxy.example.com:8080"})
```

## With Proxy

```python
scraper = RedditScraper(
    proxies={
        "http": "http://proxy.example.com:8080",
        "https": "http://proxy.example.com:8080"
    }
)
thread = scraper.scrape(url)
```

## Data Models

### Thread Object

```python
thread.title              # str
thread.subreddit          # str
thread.author             # str
thread.url                # str
thread.post_id            # str
thread.score              # int
thread.comments           # List[Comment]
```

### Comment Object

```python
comment.author            # str
comment.body              # str
comment.score             # int
comment.timestamp         # str
```

## Error Handling

```python
try:
    thread = scraper.scrape(url)
except Exception as e:
    print(f"Error: {type(e).__name__}")
```

### Batch with Error Handling

```python
threads = scraper.scrape_batch(urls, skip_errors=True)
# Failed URLs are skipped and printed as warnings
```

## Function-Based API (Legacy)

```python
from reddit_url_harvester import scrape_thread

thread = scrape_thread(url, timeout=60.0, proxies=None, delay=True)
```

## CSV Format

**Input (urls.csv):**
```csv
URL
https://reddit.com/r/python/comments/abc123/
https://reddit.com/r/python/comments/def456/
```

**Output (results.csv):**
```csv
url,title,subreddit,post_id,num_comments,author,score
https://reddit.com/r/python/comments/abc123/,Title,python,abc123,42,author,150
```

## Common Patterns

### Save to JSON

```python
import json

thread = scraper.scrape(url)
data = {
    "title": thread.title,
    "comments_count": len(thread.comments),
    "comments": [
        {"author": c.author, "body": c.body}
        for c in thread.comments
    ]
}
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)
```

### Save to JSONL

```python
import json

thread = scraper.scrape(url)
with open("comments.jsonl", "w") as f:
    for comment in thread.comments:
        f.write(json.dumps({
            "author": comment.author,
            "body": comment.body,
            "score": comment.score
        }) + "\n")
```

### Batch with Progress

```python
import time

urls = [...]
threads = []
for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] Scraping...")
    thread = scraper.scrape(url)
    threads.append(thread)
    time.sleep(1)  # Extra delay between requests
```

## Tips & Best Practices

1. **Delays Enabled by Default** - The scraper includes 2-6 second random delays by default
2. **User-Agent Rotation** - Automatically rotates through 8 realistic user agents
3. **Respect Reddit** - Don't disable delays for large batches
4. **Handle Errors** - Use `skip_errors=True` for batch processing
5. **Test First** - Start with small batches before large operations
6. **Cache Results** - Save to CSV/JSON to avoid re-scraping
7. **Monitor Rate Limits** - Watch for 429 status codes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 429 Too Many Requests | Enable delays, reduce frequency, or add proxy |
| Timeout | Increase timeout value with `set_timeout()` |
| SSL Error | Try with proxy or check your network |
| Invalid URL | Verify Reddit URL format (with .json or /comments/) |
| Memory Issues | Process large batches in chunks, use CSV mode |

## Environment Variables (Optional)

```bash
export REDDIT_TIMEOUT=90
export REDDIT_DELAY=true
```

## CLI Usage

Basic usage:
```bash
python -c "from reddit_url_harvester import scrape_thread; \
  t = scrape_thread('https://reddit.com/r/...'); \
  print(t.title)"
```

Import example:
```bash
python -c "from examples import example_1_basic_scrape; example_1_basic_scrape()"
```
