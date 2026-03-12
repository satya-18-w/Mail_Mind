"""Fetch real emails from b123116@iiit-bh.ac.in and process through the AI pipeline."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import datetime
from backend.services.gmail_fetcher import GmailFetcher
from backend.workflows.email_graph import build_email_graph
from backend.database.session import async_session
from backend.database.crud import upsert_email, delete_old_emails


async def main():
    print("=" * 60)
    print("AI MAIL AGENT - LIVE EMAIL PROCESSING")
    print("Email: b123116@iiit-bh.ac.in")
    print("=" * 60)

    # Step 1: Authenticate with Gmail
    print("\n[1] Authenticating with Gmail...")
    print("    A browser window will open - sign in with b123116@iiit-bh.ac.in")
    fetcher = GmailFetcher()
    fetcher.authenticate()
    print("    Authenticated successfully!")

    # Step 2: Fetch emails (last 30 days)
    print("\n[2] Fetching emails from the last 30 days...")
    emails = fetcher.fetch_emails(max_results=500, days=30)
    print(f"    Fetched {len(emails)} emails")

    if not emails:
        print("    No emails found. Exiting.")
        return

    # Step 3: Process through AI pipeline
    print("\n[3] Processing emails through AI pipeline...")
    pipeline = build_email_graph()

    async with async_session() as db:
        for i, email in enumerate(emails, 1):
            subject = email.get("subject", "(No Subject)")[:50]
            print(f"\n  [{i}/{len(emails)}] {subject}")
            print(f"    From: {email.get('sender', 'Unknown')[:40]}")

            # Prepare email state for pipeline
            email_state = {
                "gmail_id": email["gmail_id"],
                "sender": email.get("sender", "Unknown"),
                "subject": email.get("subject", "(No Subject)"),
                "body": email.get("body", "")[:2000],
                "timestamp": email.get("timestamp", datetime.datetime.now(datetime.UTC)).isoformat()
                    if isinstance(email.get("timestamp"), datetime.datetime)
                    else str(email.get("timestamp", "")),
            }

            # Run through AI pipeline
            result = pipeline.invoke(email_state)

            # Convert deadline string to date object
            deadline_val = None
            if result.get("deadline"):
                try:
                    deadline_val = datetime.date.fromisoformat(result["deadline"])
                except (ValueError, TypeError):
                    deadline_val = None

            # Convert timestamp - strip timezone to naive datetime
            ts = email.get("timestamp", datetime.datetime.now(datetime.UTC))
            if isinstance(ts, str):
                try:
                    ts = datetime.datetime.fromisoformat(ts)
                except ValueError:
                    ts = datetime.datetime.now(datetime.UTC)
            if ts.tzinfo is not None:
                ts = ts.replace(tzinfo=None)

            print(f"    Category:  {result['category']} ({result.get('subcategory', '-')})")
            print(f"    Priority:  {result['priority']}")
            print(f"    Deadline:  {result.get('deadline') or 'None'}")
            print(f"    Summary:   {result['summary'][:80]}...")

            # Store in database
            db_data = {
                "gmail_id": result["gmail_id"],
                "sender": result["sender"],
                "subject": result["subject"],
                "body": result["body"],
                "category": result["category"],
                "subcategory": result.get("subcategory"),
                "priority": result["priority"],
                "deadline": deadline_val,
                "summary": result["summary"],
                "embedding": result.get("embedding"),
                "timestamp": ts,
            }
            await upsert_email(db, db_data)
            print(f"    -> Saved to database")

        # Step 4: Clean up old emails (keep only last 30 days)
        print("\n[4] Cleaning up emails older than 30 days...")
        deleted = await delete_old_emails(db, days=30)
        print(f"    Deleted {deleted} old emails from dashboard")

    print("\n" + "=" * 60)
    print(f"DONE! {len(emails)} emails processed and stored.")
    print(f"Emails older than 30 days have been removed.")
    print("View them at: http://localhost:3000")
    print("=" * 60)


asyncio.run(main())
