#!/usr/bin/env python3
import os
import datetime
import sys
from requests_oauthlib import OAuth1Session

def main():
    consumer_key = os.environ.get("X_API_KEY")
    consumer_secret = os.environ.get("X_API_KEY_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print("ERROR: Missing one or more required environment variables.", file=sys.stderr)
        print("Required: X_API_KEY, X_API_KEY_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET", file=sys.stderr)
        sys.exit(1)

    # OAuth1 session for posting to Twitter/X v2 POST /2/tweets
    oauth = OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Date (UTC) and message template (can override with DAILY_MESSAGE_TEMPLATE)
    today = datetime.datetime.utcnow().date().isoformat()
    template = os.environ.get("DAILY_MESSAGE_TEMPLATE", "特定の文章 {date}")
    text = template.format(date=today)

    url = "https://api.twitter.com/2/tweets"
    payload = {"text": text}

    resp = oauth.post(url, json=payload)
    if resp.status_code >= 400:
        print("Post failed:", resp.status_code, resp.text, file=sys.stderr)
        resp.raise_for_status()

    print("Posted successfully:", resp.json())

if __name__ == "__main__":
    main()
