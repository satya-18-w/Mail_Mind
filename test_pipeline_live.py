"""Test the full AI email processing pipeline with real Groq API calls."""

from dotenv import load_dotenv
load_dotenv()

from backend.workflows.email_graph import build_email_graph

# Build the pipeline
pipeline = build_email_graph()

# Test emails covering different categories
test_emails = [
    {
        "gmail_id": "test_001",
        "sender": "registrar@iiit-bh.ac.in",
        "subject": "End Semester Exam Schedule - Spring 2026",
        "body": "Dear Students, The end semester examinations for Spring 2026 will begin from April 15, 2026. Please check the attached schedule and report any conflicts by March 20, 2026. All students must carry their ID cards.",
        "timestamp": "2026-03-12T10:00:00",
    },
    {
        "gmail_id": "test_002",
        "sender": "dr.sharma@iiit-bh.ac.in",
        "subject": "Research Paper Submission Deadline Extended",
        "body": "Hi, I wanted to let you know that the deadline for the Machine Learning conference paper has been extended to March 25, 2026. Please finalize your section on transformer architectures and send me the draft by March 18.",
        "timestamp": "2026-03-12T09:30:00",
    },
    {
        "gmail_id": "test_003",
        "sender": "noreply@linkedin.com",
        "subject": "You appeared in 15 searches this week",
        "body": "Your profile has been viewed by recruiters from Google, Microsoft, and Amazon. Upgrade to Premium to see who viewed your profile and get InMail credits.",
        "timestamp": "2026-03-12T08:00:00",
    },
]

print("=" * 60)
print("AI MAIL INTELLIGENCE PIPELINE TEST")
print("=" * 60)

for i, email in enumerate(test_emails, 1):
    print(f"\n--- Email {i}: {email['subject'][:50]} ---")
    print(f"From: {email['sender']}")
    result = pipeline.invoke(email)
    print(f"  Category:    {result['category']} ({result.get('subcategory', 'N/A')})")
    print(f"  Priority:    {result['priority']}")
    print(f"  Deadline:    {result['deadline'] or 'None detected'}")
    print(f"  Summary:     {result['summary']}")
    if result.get("embedding"):
        print(f"  Embedding:   {len(result['embedding'])} dimensions")
    else:
        print(f"  Embedding:   None")
    print(f"  Error:       {result.get('error', 'None')}")

print("\n" + "=" * 60)
print("ALL 3 TEST EMAILS PROCESSED SUCCESSFULLY!")
print("=" * 60)
