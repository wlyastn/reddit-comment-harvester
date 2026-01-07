#!/usr/bin/env python
"""
Script to scrape all URLs from larger_test.csv using the RedditScraper API.

This demonstrates the batch processing capabilities of the RedditScraper class.
"""

import sys
from pathlib import Path
import time
import csv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from reddit_url_harvester import RedditScraper


def main():
    """Scrape all URLs from larger_test.csv and save results."""
    
    print("=" * 70)
    print("REDDIT URL HARVESTER - Batch Scraping Script")
    print("=" * 70)
    
    # Initialize scraper with reasonable settings
    scraper = RedditScraper(
        timeout=20.0,  # 20 second timeout
        delay=True,    # Enable automatic delays to avoid rate limiting
        proxies=None   # No proxy needed
    )
    
    input_file = "larger_test.csv"
    output_file = "larger_test_results.csv"
    
    print(f"\nConfiguration:")
    print(f"  Input file:  {input_file}")
    print(f"  Output file: {output_file}")
    print(f"  Timeout:     {scraper.timeout}s")
    print(f"  Delays:      Enabled (2-6s random jitter)")
    print(f"\n" + "=" * 70 + "\n")
    
    try:
        # Read URLs from CSV
        urls = []
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get the first column (URL)
                url = list(row.values())[0] if row else None
                if url and url.strip():
                    urls.append(url.strip())
        
        print(f"Found {len(urls)} URLs to scrape\n")
        
        # Scrape URLs one by one with progress tracking
        results = []
        successful = 0
        failed = 0
        start_time = time.time()
        
        for i, url in enumerate(urls, 1):
            subreddit = url.split('/')[-2][:20]  # Get subreddit name
            print(f"[{i:3d}/{len(urls)}] {subreddit:20s}", end=" ", flush=True)
            
            try:
                thread = scraper.scrape(url)
                
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
                print(f"OK - {len(thread.comments)} comments")
                successful += 1
                
            except Exception as e:
                error_type = type(e).__name__
                print(f"FAILED - {error_type}")
                failed += 1
        
        elapsed = time.time() - start_time
        
        # Save results to CSV
        if results:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE")
        print("=" * 70)
        print(f"\nResults:")
        print(f"  Total URLs:    {len(urls)}")
        print(f"  Successful:    {successful}")
        print(f"  Failed:        {failed}")
        print(f"  Success rate:  {100*successful/len(urls):.0f}%")
        print(f"  Total time:    {elapsed:.1f}s")
        if successful > 0:
            print(f"  Avg per URL:   {elapsed/successful:.1f}s")
        print(f"  Output file:   {output_file}")
        print("\n" + "=" * 70)
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
