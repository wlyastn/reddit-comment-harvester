from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Optional

from .scrape import scrape_thread


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Fetch and parse Reddit thread JSON comments.")
    p.add_argument("url", help="Reddit thread or comment URL")
    p.add_argument("--out", help="Write comments as JSONL to this path. If omitted, prints summary.")
    p.add_argument("--timeout", type=float, default=60.0, help="Per-request timeout (seconds)")
    p.add_argument("--proxy-http", help="HTTP proxy URL (e.g., http://proxy.example.com:8080)")
    p.add_argument("--proxy-https", help="HTTPS proxy URL (e.g., http://proxy.example.com:8080)")
    args = p.parse_args(argv)

    # Build proxy dict if provided
    proxies = None
    if args.proxy_http or args.proxy_https:
        proxies = {}
        if args.proxy_http:
            proxies["http"] = args.proxy_http
        if args.proxy_https:
            proxies["https"] = args.proxy_https

    thread = scrape_thread(args.url, timeout=args.timeout, proxies=proxies)

    if not args.out:
        print(f"subreddit={thread.subreddit!r}")
        print(f"title={thread.title!r}")
        print(f"post_id={thread.post_id!r}")
        print(f"comments={len(thread.comments)}")
        if thread.comments:
            print("first_comment_body_preview=" + thread.comments[0].body[:200].replace("\n", " "))
        return 0

    with open(args.out, "w", encoding="utf-8") as f:
        # one JSON object per line, includes thread info + comment fields
        for c in thread.comments:
            row = {
                "thread_url": thread.url,
                "thread_title": thread.title,
                "thread_subreddit": thread.subreddit,
                "thread_post_id": thread.post_id,
                **asdict(c),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

