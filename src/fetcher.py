"""
Reddit Data API Client with Rate Limiting

This module handles authenticated, rate-limited access to the Reddit Data API.
It only uses read-only endpoints and respects Reddit's 100 QPM limit.

Compliance: Reddit Responsible Builder Policy, Developer Terms, Data API Terms
"""

import os
import time
import logging
from collections import deque
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class RedditFetcher:
    """Rate-limited Reddit Data API client. Read-only access only."""

    BASE_URL = "https://oauth.reddit.com"
    AUTH_URL = "https://www.reddit.com/api/v1/access_token"
    MAX_QPM = 100  # Reddit's rate limit: 100 queries per minute
    WINDOW_SECONDS = 600  # 10-minute averaging window

    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        self.access_token = None
        self.token_expiry = 0
        self._request_times = deque()

    def _authenticate(self):
        """Obtain OAuth 2.0 access token using script-type credentials."""
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        headers = {"User-Agent": self.user_agent}
        response = requests.post(self.AUTH_URL, auth=auth, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.token_expiry = time.time() + token_data.get("expires_in", 3600)
        logger.info("Reddit OAuth token obtained successfully")

    def _ensure_authenticated(self):
        """Re-authenticate if token is expired or missing."""
        if not self.access_token or time.time() >= self.token_expiry - 60:
            self._authenticate()

    def _rate_limit(self):
        """Enforce rate limiting: max 100 QPM averaged over 10 minutes."""
        now = time.time()
        # Remove requests older than the averaging window
        while self._request_times and self._request_times[0] < now - self.WINDOW_SECONDS:
            self._request_times.popleft()

        # Check if we're at the limit
        max_requests = self.MAX_QPM * (self.WINDOW_SECONDS / 60)
        if len(self._request_times) >= max_requests:
            sleep_time = self._request_times[0] + self.WINDOW_SECONDS - now
            logger.warning(f"Rate limit reached. Sleeping {sleep_time:.1f}s")
            time.sleep(max(sleep_time, 0.1))

        self._request_times.append(time.time())

    def _get(self, endpoint, params=None):
        """Make an authenticated, rate-limited GET request to Reddit API."""
        self._ensure_authenticated()
        self._rate_limit()

        headers = {
            "Authorization": f"bearer {self.access_token}",
            "User-Agent": self.user_agent,
        }
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers, params=params)

        # Respect rate limit headers from Reddit
        remaining = response.headers.get("x-ratelimit-remaining")
        reset = response.headers.get("x-ratelimit-reset")
        if remaining and float(remaining) < 10:
            logger.warning(f"Low rate limit remaining: {remaining}, reset in {reset}s")
            time.sleep(float(reset) if reset else 60)

        response.raise_for_status()
        return response.json()

    def fetch_subreddit_posts(self, subreddit, sort="hot", limit=25):
        """Fetch posts from a subreddit. Read-only."""
        endpoint = f"/r/{subreddit}/{sort}"
        params = {"limit": limit}
        data = self._get(endpoint, params)

        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            # Only extract anonymized metadata - NO usernames or PII
            posts.append({
                "title": post.get("title"),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "created_utc": post.get("created_utc"),
                "subreddit": subreddit,
                "fetched_at": datetime.utcnow().isoformat(),
            })
        return posts

    def search_posts(self, query, subreddit=None, limit=25):
        """Search for posts matching a query. Read-only."""
        endpoint = "/search"
        params = {"q": query, "limit": limit, "sort": "relevance", "t": "week"}
        if subreddit:
            params["restrict_sr"] = True
            endpoint = f"/r/{subreddit}/search"
        data = self._get(endpoint, params)

        posts = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append({
                "title": post.get("title"),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "created_utc": post.get("created_utc"),
                "subreddit": post.get("subreddit"),
                "fetched_at": datetime.utcnow().isoformat(),
            })
        return posts

    def get_subreddit_info(self, subreddit):
        """Get subreddit metadata. Read-only."""
        endpoint = f"/r/{subreddit}/about"
        data = self._get(endpoint)
        info = data.get("data", {})
        return {
            "name": info.get("display_name"),
            "subscribers": info.get("subscribers", 0),
            "active_users": info.get("accounts_active", 0),
            "description": info.get("public_description", ""),
        }
