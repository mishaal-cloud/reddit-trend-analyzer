# Compliance Documentation

## Reddit Responsible Builder Policy Compliance

This document maps each requirement of Reddit's Responsible Builder Policy to our specific implementation.

### 1. Approval Required
- We have submitted a formal API access request through Reddit's Help Center
- We will not access any API endpoints until approval is granted
- We use a single OAuth token under u/SpiritualForever8722

### 2. Transparency
- This repository fully documents our data access patterns, endpoints, and use case
- We do not misrepresent how or why we access Reddit data
- We have registered a single account and submitted a single request for this use case

### 3. Rate Limits
- Our fetcher.py implements a queue-based rate limiter capped at 100 QPM
- We use a 10-minute averaging window to support bursting without exceeding limits
- We read and respect x-ratelimit-remaining and x-ratelimit-reset headers
- A circuit breaker halts all requests if remaining quota drops below 10

### 4. No Bot Manipulation
- Our app is read-only. It never posts, comments, votes, or sends messages
- We do not manipulate karma, voting, or any Reddit feature
- We do not circumvent any safety mechanisms

### 5. Privacy
- We do NOT store usernames, user IDs, or any PII
- We do NOT attempt to re-identify, de-anonymize, or profile Reddit users
- We do NOT derive sensitive characteristics (health, political affiliation, etc.)
- We only store anonymized aggregate statistics (topic counts, average scores)

### 6. No Data Sale
- We do NOT sell, license, sublicense, or broker Reddit data
- Our clients only see aggregated trend dashboards
- No raw Reddit content is ever shared with third parties

### 7. No Illegal or Malicious Activity
- Our use case is lawful market research using publicly available data
- We comply with all Reddit Rules
- All content access is through the official API with proper authentication

## Data Retention Policy

| Data Type | Retention Period | Storage |
|---|---|---|
| Raw API responses | In-memory only, discarded within 24 hours | None (memory) |
| Aggregated statistics | 90-day rolling window | Encrypted database |
| User data / PII | Never collected | N/A |
| API credentials | Encrypted env vars | Server-side only |

## Contact

For compliance questions: mishaal@ascendgtm.net
