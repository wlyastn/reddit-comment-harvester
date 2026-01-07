#!/usr/bin/env python3
"""
Batch scrape Reddit comments from a CSV file and append results to the same CSV.
Designed for robustness with 20k+ URLs - incremental saves, resume capability, minimal memory.

Usage:
    python scrape_csv_batch.py --csv-in INPUT.csv --csv-out OUTPUT.csv --url-col URL [--threads N] [--batch-size N]

Example:
    python scrape_csv_batch.py --csv-in gilead_hiv_dec.csv --csv-out gilead_hydrated.csv --url-col URL --threads 1
"""

import argparse
import csv
import logging
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.reddit_url_harvester.scrape import scrape_thread


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RobustBatchScraper:
    """
    Production-grade scraper with:
    - Incremental checkpointing after each batch
    - Resume from interruption (.partial files)
    - Row-by-row progress tracking
    - Minimal memory footprint
    - Safe concurrent writes
    """
    
    def __init__(
        self,
        csv_in: str,
        csv_out: str,
        url_column: str = "URL",
        threads: int = 1,
    ):
        self.csv_in = Path(csv_in)
        self.csv_out = Path(csv_out)
        self.partial_path = Path(str(self.csv_out) + ".partial")
        self.url_column = url_column
        self.threads = threads
        
        # Auto-resume: prefer partial (in-progress), then completed out, else original in
        self.resume_path = self.csv_in
        if self.partial_path.exists():
            self.resume_path = self.partial_path
            logger.info(f"Found checkpoint: resuming from {self.resume_path}")
        elif self.csv_out != self.csv_in and Path(self.csv_out).exists():
            self.resume_path = Path(self.csv_out)
            logger.info(f"Found completed output: resuming from {self.resume_path}")
        else:
            logger.info(f"Starting fresh from: {self.resume_path}")
        
        # Load CSV
        if not self.resume_path.exists():
            raise FileNotFoundError(f"Input CSV not found: {self.resume_path}")
        
        logger.info(f"Loading rows from: {self.resume_path}")
        self.df = pd.read_csv(self.resume_path, dtype=str, keep_default_na=False)
        
        if self.url_column not in self.df.columns:
            raise ValueError(f"Column '{self.url_column}' not found. Columns: {list(self.df.columns)}")
        
        # Ensure output columns exist
        self._ensure_output_columns()
        
        # Statistics
        self.stats_lock = threading.Lock()
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
    
    def _ensure_output_columns(self) -> None:
        """Ensure all output columns exist in DataFrame."""
        output_cols = [
            "content",  # The scraped comment/post text
            "content_error",  # Error message if scraping failed
            "comment_id",  # Reddit comment/post ID
            "author",  # Author of the comment/post
            "score",  # Upvote score
            "created_utc",  # Creation timestamp
            "depth",  # Comment depth (0 for posts/top-level)
            "community_name",  # Subreddit name
            "thread_title",  # Title of the thread
        ]
        
        for col in output_cols:
            if col not in self.df.columns:
                self.df[col] = ""
    
    def _get_pending_rows(self) -> List[int]:
        """
        Get indices of rows that need processing:
        No content AND no error set yet (resumable state)
        """
        pending_mask = (
            (self.df["content"].astype(str).str.len() == 0) & 
            (self.df["content_error"].astype(str).str.len() == 0)
        )
        return self.df.index[pending_mask].tolist()
    
    
    def _process_url(self, row_idx: int) -> bool:
        """Scrape a single Reddit URL and update the DataFrame."""
        try:
            url = self.df.at[row_idx, self.url_column]
            row_num = row_idx + 2  # Account for header and 1-based indexing
            
            logger.info(f"Scraping row {row_num}: {url}")
            thread = scrape_thread(url)
            
            if not thread.comments:
                logger.warning(f"Row {row_num}: No comments/post found")
                self.df.at[row_idx, "content_error"] = "No comments or post data found"
                with self.stats_lock:
                    self.stats["failed"] += 1
                    self.stats["errors"].append({
                        "row": row_num,
                        "url": url,
                        "error": "No comments or post data found"
                    })
                return False
            
            # Get the first comment/post (only one since we extract single comments/posts)
            first = thread.comments[0]
            
            # Sanitize content: replace newlines with spaces, strip excessive whitespace
            body_text = (first.body or "").replace('\n', ' ').replace('\r', ' ')
            body_text = ' '.join(body_text.split())  # Collapse multiple spaces
            
            # Update row with extracted data - set content LAST to mark as complete
            self.df.at[row_idx, "comment_id"] = first.id or ""
            self.df.at[row_idx, "author"] = first.author or ""
            self.df.at[row_idx, "score"] = str(first.score) if first.score is not None else ""
            self.df.at[row_idx, "created_utc"] = str(int(first.created_utc)) if first.created_utc else ""
            self.df.at[row_idx, "depth"] = str(first.depth) if first.depth is not None else "0"
            self.df.at[row_idx, "community_name"] = thread.subreddit or ""
            self.df.at[row_idx, "thread_title"] = thread.title or ""
            self.df.at[row_idx, "content_error"] = ""  # Clear any error
            self.df.at[row_idx, "content"] = body_text  # LAST - marks row complete
            
            with self.stats_lock:
                self.stats["success"] += 1
            
            logger.info(f"[OK] Row {row_num}: {body_text[:50]}...")
            return True
            
        except Exception as e:
            url = self.df.at[row_idx, self.url_column]
            row_num = row_idx + 2
            logger.error(f"[ERROR] Row {row_num}: {e}")
            
            # Mark as error - prevents re-processing on resume
            self.df.at[row_idx, "content_error"] = str(e)[:200]
            
            with self.stats_lock:
                self.stats["failed"] += 1
                self.stats["errors"].append({
                    "row": row_num,
                    "url": url,
                    "error": str(e)[:100]
                })
            
            return False
    
    def _checkpoint(self, batch_num: int, total_batches: int) -> None:
        """Write checkpoint file after each batch."""
        self.df.to_csv(self.partial_path, index=False, quoting=1)  # quoting=csv.QUOTE_ALL for safety
        pending = len(self._get_pending_rows())
        logger.info(f"[CHECKPOINT] Batch {batch_num}/{total_batches}: Wrote {self.partial_path} ({pending} pending)")
    
    def run(self, batch_size: int = 50) -> Dict:
        """Run the batch scraping with checkpoints."""
        pending_indices = self._get_pending_rows()
        self.stats["total"] = len(self.df)
        
        if not pending_indices:
            logger.info("Nothing to do: all rows already hydrated.")
            # Final write (move partial to output if needed)
            self.df.to_csv(self.csv_out, index=False, quoting=1)
            return self.stats
        
        logger.info(f"Found {len(self.df)} total rows, {len(pending_indices)} pending")
        
        # Split into batches for checkpointing
        batches = [
            pending_indices[i : i + batch_size] 
            for i in range(0, len(pending_indices), batch_size)
        ]
        total_batches = len(batches)
        logger.info(f"Processing {total_batches} batch(es) of ~{batch_size} rows each\n")
        
        for batch_num, batch_indices in enumerate(batches, 1):
            logger.info(f"[Batch {batch_num}/{total_batches}] Processing {len(batch_indices)} rows...")
            
            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {
                    executor.submit(self._process_url, idx): idx
                    for idx in batch_indices
                }
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Unexpected error: {e}")
            
            # Checkpoint after each batch
            self._checkpoint(batch_num, total_batches)
        
        # Final write: move partial -> output
        self.df.to_csv(self.csv_out, index=False, quoting=1)
        logger.info(f"[DONE] Final output written to: {self.csv_out}")
        
        # Clean up partial if everything succeeded
        if self.partial_path.exists():
            self.partial_path.unlink()
            logger.info(f"[CLEANUP] Cleaned up checkpoint: {self.partial_path}")
        
        return self.stats
    
    def print_summary(self) -> None:
        """Print summary statistics."""
        success_pct = 100 * self.stats["success"] / max(1, self.stats["total"])
        
        print("\n" + "=" * 70)
        print("BATCH SCRAPING SUMMARY")
        print("=" * 70)
        print(f"Total rows:    {self.stats['total']}")
        print(f"Successful:    {self.stats['success']} ({success_pct:.1f}%)")
        print(f"Failed:        {self.stats['failed']}")
        print(f"Output CSV:    {self.csv_out}")
        
        if self.stats['errors']:
            print(f"\nFirst 10 errors:")
            for err in self.stats['errors'][:10]:
                print(f"  Row {err['row']}: {err['error'][:60]}")
        
        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Batch scrape Reddit comments from CSV with incremental checkpointing. "
                    "Designed for 20k+ URLs with automatic resume capability."
    )
    parser.add_argument(
        "--csv-in",
        required=True,
        help="Input CSV file with Reddit comment URLs"
    )
    parser.add_argument(
        "--csv-out",
        required=True,
        help="Output CSV file (will create .partial checkpoint during processing)"
    )
    parser.add_argument(
        "--url-col",
        default="URL",
        help="Name of CSV column containing URLs (default: 'URL')"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of parallel threads (default: 1 for stability; increase cautiously)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Rows per checkpoint batch (default: 50; smaller = more checkpoints)"
    )

    args = parser.parse_args()

    try:
        scraper = RobustBatchScraper(
            csv_in=args.csv_in,
            csv_out=args.csv_out,
            url_column=args.url_col,
            threads=args.threads,
        )

        stats = scraper.run(batch_size=args.batch_size)
        scraper.print_summary()

        sys.exit(0 if stats["failed"] == 0 else 1)
    
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user. Progress has been checkpointed.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
