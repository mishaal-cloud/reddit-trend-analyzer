"""Trend analysis module for Reddit data.

Aggregates fetched subreddit data into anonymized B2B GTM insights.
"""

import logging
from collections import Counter
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def analyze_trends(posts: list[dict], top_n: int = 20) -> dict:
    """Analyze trending topics from fetched Reddit posts.

    Args:
        posts: List of post dicts from fetcher.fetch_subreddit_posts().
        top_n: Number of top keywords to return.

    Returns:
        Dict with trend summary including top keywords, post volume,
        and engagement metrics.
    """
    if not posts:
        logger.warning("No posts to analyze.")
        return {"keywords": [], "post_count": 0, "avg_score": 0}

    # Aggregate keyword frequencies from titles
    word_counts = Counter()
    total_score = 0
    total_comments = 0

    for post in posts:
        title_words = post.get("title", "").lower().split()
        # Filter short/common words
        meaningful = [w for w in title_words if len(w) > 3]
        word_counts.update(meaningful)
        total_score += post.get("score", 0)
        total_comments += post.get("num_comments", 0)

    post_count = len(posts)
    top_keywords = [
        {"keyword": word, "count": count}
        for word, count in word_counts.most_common(top_n)
    ]

    return {
        "keywords": top_keywords,
        "post_count": post_count,
        "avg_score": round(total_score / post_count, 1),
        "avg_comments": round(total_comments / post_count, 1),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
