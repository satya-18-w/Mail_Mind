"""Shared test fixtures and configuration."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch


# Sample test emails for all tests
SAMPLE_EMAILS = [
    {
        "gmail_id": "test_001",
        "sender": "professor@university.edu",
        "subject": "Project Submission Form - Due March 20",
        "body": "Dear students, please submit the project proposal form before March 20, 2026. "
        "This is a mandatory academic requirement. Late submissions will not be accepted.",
        "timestamp": "2026-03-12T10:00:00",
    },
    {
        "gmail_id": "test_002",
        "sender": "notifications@linkedin.com",
        "subject": "You have 5 new connection requests",
        "body": "Hi, you have 5 new connection requests on LinkedIn. "
        "Check out profiles that viewed your profile this week.",
        "timestamp": "2026-03-11T08:00:00",
    },
    {
        "gmail_id": "test_003",
        "sender": "ieee-society@college.edu",
        "subject": "Upcoming Tech Talk - March 15",
        "body": "IEEE Student Chapter presents a tech talk on AI and Machine Learning. "
        "Date: March 15, 2026. Venue: Auditorium. Registration required.",
        "timestamp": "2026-03-10T14:00:00",
    },
    {
        "gmail_id": "test_004",
        "sender": "noreply@amazon.com",
        "subject": "Flash Sale - 50% off Electronics",
        "body": "Don't miss our biggest sale of the season! 50% off on all electronics. "
        "Limited time offer. Shop now!",
        "timestamp": "2026-03-09T09:00:00",
    },
    {
        "gmail_id": "test_005",
        "sender": "admin@university.edu",
        "subject": "Semester Registration Deadline - March 25",
        "body": "All students must complete semester registration by March 25, 2026. "
        "Failure to register will result in enrollment cancellation. "
        "Visit the portal to complete registration.",
        "timestamp": "2026-03-08T11:00:00",
    },
]
