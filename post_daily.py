#!/usr/bin/env python3
import os
import sys
import datetime
import json
from zoneinfo import ZoneInfo
from requests_oauthlib import OAuth1Session
from requests import RequestException

# 設定
MAX_TWEET_LENGTH = 280

def get_today_iso(tz_name: str) -> str:
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
    now = datetime.datetime.now(tz)
    return now.date().isoformat()

def main():
    consumer_key = os.environ.get("X_API_KEY")
    consumer_secret = os.environ.get("X_API_KEY_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print("ERROR: Missing one or more required environment variables.", file=sys.stderr)
        print("Required: X_API_KEY, X_API_KEY_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET", file=sys.stderr)
        sys.exit(1)

    # 日付およびテンプレート設定
    tz_name = os.environ.get("DAILY_MESSAGE_TZ", "UTC")  # 例: 'Asia/Tokyo'
    today = get_today_iso(tz_name)
    template = os.environ.get("DAILY_MESSAGE_TEMPLATE", "特定の文章 {date}")
    try:
        text = template.format(date=today)
    except Exception as e:
        print("ERROR: Failed to format DAILY_MESSAGE_TEMPLATE:", e, file=sys.stderr)
        sys.exit(1)

    # 長さチェック
    if len(text) > MAX_TWEET_LENGTH:
        print(f"ERROR: Message too long ({len(text)} chars). Max is {MAX_TWEET_LENGTH}.", file=sys.stderr)
        print("Message preview:", text, file=sys.stderr)
        sys.exit(1)

    # ドライランモード（投稿しないテスト）
    dry_run = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")

    print("Posting message:", text)
    if dry_run:
        print("DRY_RUN enabled — not sending to X.")
        return

    oauth = OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    url = "https://api.twitter.com/2/tweets"
    payload = {"text": text}

    try:
        resp = oauth.post(url, json=payload, timeout=30)
    except RequestException as e:
        print("Network/request error while posting:", e, file=sys.stderr)
        sys.exit(1)

    # レスポンスハンドリング
    status = getattr(resp, "status_code", None)
    body = None
    try:
        body = resp.json()
    except Exception:
        body = resp.text

    if status is None or status >= 400:
        print("Post failed. HTTP status:", status, file=sys.stderr)
        print("Response body:", json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else body, file=sys.stderr)
        sys.exit(1)

    print("Posted successfully. Response:", json.dumps(body, ensure_ascii=False))

if __name__ == "__main__":
    main()
