"""Unit tests for Gmail Fetcher service."""

import pytest
from unittest.mock import patch, MagicMock
import base64

from backend.services.gmail_fetcher import GmailFetcher


class TestGmailFetcher:
    """Tests for the Gmail fetching service."""

    def test_parse_message_basic(self):
        """Test parsing a basic Gmail API message structure."""
        fetcher = GmailFetcher()

        body_text = "Hello, please submit the form."
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        message = {
            "id": "msg_123",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "test@example.com"},
                    {"name": "Date", "value": "Thu, 12 Mar 2026 10:00:00 +0000"},
                ],
                "body": {"data": encoded_body},
            },
        }

        result = fetcher._parse_message(message)

        assert result is not None
        assert result["gmail_id"] == "msg_123"
        assert result["subject"] == "Test Subject"
        assert result["sender"] == "test@example.com"
        assert "Hello" in result["body"]

    def test_parse_message_multipart(self):
        """Test parsing a multipart email message."""
        fetcher = GmailFetcher()

        body_text = "This is the plain text body."
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        message = {
            "id": "msg_456",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Multipart Email"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Date", "value": "Thu, 12 Mar 2026 10:00:00 +0000"},
                ],
                "body": {},
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": encoded_body},
                    },
                    {
                        "mimeType": "text/html",
                        "body": {"data": encoded_body},
                    },
                ],
            },
        }

        result = fetcher._parse_message(message)

        assert result["gmail_id"] == "msg_456"
        assert "plain text body" in result["body"]

    def test_parse_message_missing_headers(self):
        """Test parsing when headers are missing."""
        fetcher = GmailFetcher()

        message = {
            "id": "msg_789",
            "payload": {
                "headers": [],
                "body": {},
            },
        }

        result = fetcher._parse_message(message)

        assert result["subject"] == "(No Subject)"
        assert result["sender"] == "Unknown"

    def test_extract_body_empty(self):
        """Test body extraction when no body data exists."""
        fetcher = GmailFetcher()

        payload = {"body": {}, "parts": []}
        result = fetcher._extract_body(payload)
        assert result == ""
