from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from .models import Comment, Thread


def _as_listing(obj: Any) -> Optional[Dict[str, Any]]:
    if isinstance(obj, dict) and obj.get("kind") == "Listing" and isinstance(obj.get("data"), dict):
        return obj
    return None


def _iter_comment_nodes(children: List[Dict[str, Any]]) -> Iterable[Tuple[Dict[str, Any], int]]:
    """
    Yield (comment_data, depth) for all t1 comments in a Reddit listing, recursively walking replies
    Skips 'more' objects
    """
    stack: List[Tuple[Dict[str, Any], int]] = []
    for c in reversed(children):
        stack.append((c, 0))

    while stack:
        node, depth = stack.pop()
        kind = node.get("kind")
        data = node.get("data") if isinstance(node.get("data"), dict) else None
        if not data:
            continue

        if kind == "t1":
            yield data, depth

            replies = data.get("replies")
            # replies can be "" or a Listing object
            if isinstance(replies, dict):
                lst = _as_listing(replies)
                if lst:
                    rep_children = lst["data"].get("children") or []
                    if isinstance(rep_children, list) and rep_children:
                        for rc in reversed(rep_children):
                            stack.append((rc, depth + 1))

        # ignore kind == "more"


def _extract_comment_id_from_url(url: str) -> Optional[str]:
    """
    Extract comment ID from URL if it's a comment-specific link.
    
    Examples:
      /r/sub/comments/postid/title/commentid/  -> commentid
      /r/sub/comments/postid/title/commentid/?...  -> commentid
      /r/sub/comments/postid/title/               -> None (thread URL)
      /r/sub/comments/postid/title/comment/commentid/ -> commentid
    """
    # Remove query params
    url_path = url.split('?')[0]
    parts = url_path.rstrip('/').split('/')
    
    # Look for pattern: comments/postid/*/commentid
    try:
        idx = parts.index('comments')
        if idx + 2 < len(parts):
            # parts[idx] = 'comments'
            # parts[idx+1] = postid
            # parts[idx+2] = title (or sometimes "comment" keyword)
            
            # Handle '/comment/' keyword format
            if idx + 3 < len(parts) and parts[idx + 2] == 'comment':
                candidate = parts[idx + 3]
                if candidate and candidate.isalnum() and len(candidate) >= 6:
                    return candidate
            
            # Handle standard format: /postid/title/commentid/
            if idx + 3 < len(parts):
                candidate = parts[idx + 3]
                # Comment IDs are alphanumeric, typically 6-10 chars
                if candidate and candidate.isalnum() and len(candidate) >= 6:
                    return candidate
    except (ValueError, IndexError):
        pass
    
    return None


def parse_reddit_thread_json(
    url: str,
    payload: Any,
) -> Thread:
    """
    Parse JSON returned by Reddit's `.json` endpoint for a thread URL

    The common structure is a list of two Listing objects:
      [0] post listing, first child is kind t3
      [1] comments listing, children are kind t1 and kind more
    
    If url is a comment-specific link (contains a comment ID), returns only that comment.
    """
    thread = Thread(url=url)
    target_comment_id = _extract_comment_id_from_url(url)

    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("Unexpected Reddit JSON: expected a list with 2 elements (post listing + comments listing)")

    post_listing = _as_listing(payload[0])
    comments_listing = _as_listing(payload[1])
    if not post_listing or not comments_listing:
        raise ValueError("Unexpected Reddit JSON: missing Listing objects.")

    # Post
    post_children = post_listing["data"].get("children") or []
    if post_children and isinstance(post_children, list):
        first = post_children[0]
        if isinstance(first, dict) and first.get("kind") == "t3" and isinstance(first.get("data"), dict):
            post = first["data"]
            thread.raw_post = post
            thread.subreddit = post.get("subreddit")
            thread.title = post.get("title")
            thread.post_id = post.get("id")
            thread.post_fullname = post.get("name")
            thread.permalink = post.get("permalink")
            thread.author = post.get("author")
            thread.created_utc = post.get("created_utc")
            thread.score = post.get("score")
            thread.num_comments = post.get("num_comments")

    # If this is a thread-only URL (no comment ID), return just the post as a synthetic comment
    if not target_comment_id:
        if thread.raw_post:
            post = thread.raw_post
            # Treat the post as a comment entry for consistency
            thread.comments.append(
                Comment(
                    id=post.get("id") or "",
                    body=post.get("selftext") or "",
                    author=post.get("author"),
                    created_utc=post.get("created_utc"),
                    score=post.get("score"),
                    depth=0,
                    parent_id=None,
                    permalink=post.get("permalink"),
                    raw=post,
                )
            )
        return thread

    # Comments
    children = comments_listing["data"].get("children") or []
    if isinstance(children, list):
        for cdata, depth in _iter_comment_nodes(children):
            body = cdata.get("body")
            if not isinstance(body, str):
                continue
            
            comment_id = str(cdata.get("id") or "")
            
            # If this is a comment-specific URL, only include the target comment
            if target_comment_id and comment_id != target_comment_id:
                continue
            
            thread.comments.append(
                Comment(
                    id=comment_id,
                    body=body,
                    author=cdata.get("author"),
                    created_utc=cdata.get("created_utc"),
                    score=cdata.get("score"),
                    depth=depth,
                    parent_id=cdata.get("parent_id"),
                    permalink=cdata.get("permalink"),
                    raw=cdata,
                )
            )

    return thread
