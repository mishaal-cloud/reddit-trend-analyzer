# Reddit Trend Analyzer

> A read-only Reddit Data API integration for aggregating public subreddit trends into anonymized B2B go-to-market insights. Built by [Ascend GTM](https://ascendgtm.net).

## Overview

Reddit Trend Analyzer is a server-side analytics pipeline that uses the Reddit Data API to surface trending topics, discussions, and engagement patterns across public B2B-relevant subreddits. It helps go-to-market teams understand what their target audiences are discussing in real time.

This tool is **read-only** — it does not post, comment, vote, or send messages on Reddit. It only reads publicly available data.

## Architecture

```
+------------------+       +----------------+       +-------------------+
|  Reddit Data API | ----> |  n8n Workflow  | ----> | Aggregated Stats  |
|  (read-only)     |       |  (server-side) |       | (anonymized JSON) |
+------------------+       +----------------+       +-------------------+
        |                         |                          |
   OAuth 2.0               Rate-limited              Dashboard/Reports
   Authentication          Queue-based                (no raw data)
                           Processing
```

### Data Flow

1. **Fetch**: n8n workflow calls Reddit Data API endpoints on a scheduled basis
2. **Process**: Raw responses are parsed in memory — post titles, upvote counts, comment counts, timestamps
3. **Aggregate**: Data is grouped by subreddit, topic, and time period into statistical summaries
4. **Store**: Only anonymized aggregate statistics are stored (e.g., "r/sales had 47 posts about 'cold outreach' this week")
5. **Discard**: Raw API responses are discarded within 24 hours. No comment bodies, usernames, or PII are retained.

## API Usage Details

### Endpoints Used

| Endpoint | Purpose | Scope |
|---|---|---|
| `/r/{subreddit}/hot` | Fetch trending posts | `read` |
| `/r/{subreddit}/new` | Fetch recent posts | `read` |
| `/search` | Search for topic-specific discussions | `read` |
| `/r/{subreddit}/about` | Get subreddit metadata | `read` |

### OAuth Scope

We request **only the `read` scope**. No write permissions are needed or requested.

### Rate Limiting

- Strict adherence to Reddit's **100 QPM** limit
- Queue-based request system with exponential backoff
- Requests averaged over 10-minute windows to support bursting
- Built-in circuit breaker to halt requests if rate limit headers indicate throttling

### Target Subreddits

| Subreddit | Relevance |
|---|---|
| r/sales | Sales strategies and trends |
| r/marketing | Marketing tactics and discussions |
| r/B2BMarketing | B2B-specific marketing insights |
| r/SaaS | SaaS product and GTM discussions |
| r/startups | Startup ecosystem trends |
| r/Entrepreneur | Entrepreneurship and business |
| r/digital_marketing | Digital marketing techniques |
| r/growthmarketing | Growth strategies |
| r/recruiting | Talent acquisition trends |
| r/humanresources | HR and workforce management |

All subreddits are public. We do not access private or restricted communities.

## Data Handling & Privacy

### What We Store

- Aggregated topic counts per subreddit per time period
- Average engagement metrics (upvotes, comment counts) per topic
- Trend direction indicators (rising, falling, stable)

### What We Do NOT Store

- Individual usernames or user IDs
- Comment bodies or full post content
- Any personally identifiable information (PII)
- User posting history or behavioral patterns
- Private messages or direct communications

### Data Retention

- Raw API responses: **Processed in memory, discarded within 24 hours**
- Aggregated statistics: Retained for trend analysis (rolling 90-day window)
- No raw Reddit data is ever persisted to disk or database

### Data Sharing

- We do **NOT** sell, license, sublicense, or broker Reddit data
- Clients see only aggregated trend dashboards — never raw Reddit content
- No third-party data sharing of any kind

## Security

- OAuth credentials stored in **encrypted environment variables**
- All API calls are **server-side only** (n8n workflow instance) — no client-side API exposure
- Access to the n8n instance is restricted to authenticated team members
- HTTPS-only communication with Reddit's API
- No API keys or tokens committed to source code

## Compliance

This project is built in full compliance with:

- [Reddit Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564)
- [Reddit Developer Terms](https://www.redditinc.com/policies/developer-terms)
- [Reddit Data API Terms](https://www.redditinc.com/policies/data-api-terms)
- [Reddit Public Content Policy](https://support.reddithelp.com/hc/en-us/articles/26410290525844-Public-Content-Policy)

### Specific Compliance Points

| Policy Requirement | Our Implementation |
|---|---|
| Approval required before access | Submitting formal request via Reddit Help Center |
| Transparent about data usage | This README documents all access patterns |
| Respect rate limits | Queue-based system with 100 QPM cap |
| No re-identification of users | No usernames or PII stored or processed |
| No sensitive characteristic derivation | Only topic-level aggregation, no user profiling |
| No data sale or brokerage | Clients see dashboards only, no raw data shared |
| No bot manipulation | Read-only — no voting, posting, or messaging |
| Single account, single request | One OAuth token under u/SpiritualForever8722 |

## Tech Stack

- **Runtime**: Python 3.11+
- **Workflow Automation**: [n8n](https://n8n.io) (self-hosted)
- **API Client**: `requests` library with OAuth 2.0
- **Data Processing**: `pandas` for aggregation
- **Deployment**: Server-side only (no public-facing API)

## User-Agent

Per Reddit API guidelines, our User-Agent follows the required format:

```
server:reddit-trend-analyzer:v1.0.0 (by /u/SpiritualForever8722)
```

## Project Structure

```
reddit-trend-analyzer/
|-- config/
|   |-- subreddits.yaml       # Target subreddit configuration
|   |-- settings.py            # App settings (no secrets)
|-- src/
|   |-- auth.py                # OAuth 2.0 authentication
|   |-- fetcher.py             # Reddit API client with rate limiting
|   |-- aggregator.py          # Data aggregation logic
|   |-- scheduler.py           # Scheduled fetch jobs
|-- docs/
|   |-- architecture.md        # Detailed architecture documentation
|   |-- compliance.md          # Full compliance documentation
|   |-- data-flow.md           # Data flow diagrams
|-- tests/
|   |-- test_fetcher.py        # API client tests
|   |-- test_aggregator.py     # Aggregation logic tests
|-- .env.example               # Environment variable template (no secrets)
|-- .gitignore
|-- README.md
|-- requirements.txt
```

## Getting Started

1. Clone this repository
2. Copy `.env.example` to `.env` and add your Reddit OAuth credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Configure target subreddits in `config/subreddits.yaml`
5. Run: `python -m src.scheduler`

## Contact

- **Company**: [Ascend GTM](https://ascendgtm.net)
- **Email**: mishaal@ascendgtm.net
- **Reddit**: u/SpiritualForever8722

## License

Proprietary — Ascend GTM. All rights reserved.
