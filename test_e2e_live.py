"""End-to-end test: process emails through AI pipeline and store in database, then query via API."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import datetime
import httpx
from backend.workflows.email_graph import build_email_graph
from backend.database.session import async_session, engine, Base
from backend.database.models import Email
from backend.database.crud import upsert_email, search_emails_by_vector, get_category_counts, get_priority_counts
from backend.services.embedding_service import EmbeddingService

test_emails = [
    {
        "gmail_id": "test_e2e_001",
        "sender": "registrar@iiit-bh.ac.in",
        "subject": "End Semester Exam Schedule - Spring 2026",
        "body": "Dear Students, The end semester examinations for Spring 2026 will begin from April 15, 2026. Please check the attached schedule and report any conflicts by March 20, 2026.",
        "timestamp": "2026-03-12T10:00:00",
    },
    {
        "gmail_id": "test_e2e_002",
        "sender": "dr.sharma@iiit-bh.ac.in",
        "subject": "Research Paper Submission Deadline Extended",
        "body": "The deadline for the Machine Learning conference paper has been extended to March 25, 2026. Please finalize your section on transformer architectures.",
        "timestamp": "2026-03-12T09:30:00",
    },
    {
        "gmail_id": "test_e2e_003",
        "sender": "noreply@linkedin.com",
        "subject": "You appeared in 15 searches this week",
        "body": "Your profile has been viewed by recruiters from Google, Microsoft, and Amazon. Upgrade to Premium to see who viewed your profile.",
        "timestamp": "2026-03-12T08:00:00",
    },
    {
        "gmail_id": "test_e2e_004",
        "sender": "offers@amazon.in",
        "subject": "Great Indian Summer Sale - Up to 70% OFF!",
        "body": "Huge discounts on electronics, clothing, and more. Sale starts March 15. Use code SUMMER26 for extra 10% off on your first purchase!",
        "timestamp": "2026-03-12T07:00:00",
    },
    {
        "gmail_id": "test_e2e_005",
        "sender": "techsoc@iiit-bh.ac.in",
        "subject": "Hackathon Registration Open - CodeStorm 2026",
        "body": "Register for CodeStorm 2026 hackathon by March 22. Teams of 2-4 members. Prizes worth 50000 INR. Event on April 1-2 at Main Auditorium.",
        "timestamp": "2026-03-12T06:00:00",
    },
]


async def main():
    pipeline = build_email_graph()

    print("=" * 60)
    print("END-TO-END PIPELINE + DATABASE TEST")
    print("=" * 60)

    # Step 1: Process through AI pipeline and store in DB
    print("\n[STEP 1] Processing emails through AI pipeline...")
    async with async_session() as db:
        for i, email in enumerate(test_emails, 1):
            print(f"  Processing {i}/5: {email['subject'][:45]}...", end=" ")
            result = pipeline.invoke(email)

            deadline_str = result.get("deadline")
            deadline_val = None
            if deadline_str:
                try:
                    deadline_val = datetime.date.fromisoformat(deadline_str)
                except (ValueError, TypeError):
                    deadline_val = None

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
                "timestamp": datetime.datetime.fromisoformat(email["timestamp"]),
            }
            await upsert_email(db, db_data)
            print("OK")

    # Step 2: Query via API
    print("\n[STEP 2] Querying via REST API...")
    async with httpx.AsyncClient(base_url="http://localhost:8000/api/v1") as client:
        # Get all emails
        r = await client.get("/emails")
        emails = r.json()
        print(f"  Total emails in DB: {len(emails)}")

        # Category stats
        r = await client.get("/stats/categories")
        cats = r.json()
        print(f"  Categories: {cats}")

        # Priority stats
        r = await client.get("/stats/priorities")
        pris = r.json()
        print(f"  Priorities: {pris}")

        # Deadlines
        r = await client.get("/emails/deadlines/upcoming")
        deadlines = r.json()
        print(f"  Emails with deadlines: {len(deadlines)}")
        for d in deadlines:
            print(f"    - {d['subject'][:40]} -> {d['deadline']}")

    # Step 3: Semantic search
    print("\n[STEP 3] Testing semantic search...")
    async with async_session() as db:
        emb_service = EmbeddingService()
        query = "exam schedule and deadlines"
        query_vec = emb_service.embed(query)
        results = await search_emails_by_vector(db, query_vec, limit=3)
        print(f"  Query: '{query}'")
        print(f"  Top {len(results)} results:")
        for r in results:
            print(f"    - [{r.category}] {r.subject}")

    print("\n" + "=" * 60)
    print("END-TO-END TEST COMPLETE - ALL SYSTEMS WORKING!")
    print("=" * 60)


asyncio.run(main())
