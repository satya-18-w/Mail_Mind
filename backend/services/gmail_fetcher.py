"""Gmail email fetching service using Google API.

Uses OAuth2 for authentication. Requires credentials.json from Google Cloud Console.
Setup: Enable Gmail API -> Create OAuth2 credentials -> Download credentials.json
"""

import base64
import datetime
import os
from email.utils import parsedate_to_datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from backend.core.config import get_settings

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = Path("token.json")
CREDENTIALS_PATH = Path("credentials.json")


class GmailFetcher:
    """Fetches emails from Gmail using the Gmail API."""

    def __init__(self, access_token: str | None = None, refresh_token: str | None = None):
        self.settings = get_settings()
        self.service = None
        self._access_token = access_token
        self._refresh_token = refresh_token

    def authenticate(self) -> Credentials | None:
        """Authenticate with Gmail API using OAuth2 (per-user tokens or file-based)."""
        creds = None

        if self._access_token:
            # Per-user token auth (web app flow)
            creds = Credentials(
                token=self._access_token,
                refresh_token=self._refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.settings.gmail_client_id,
                client_secret=self.settings.gmail_client_secret,
                scopes=SCOPES,
            )
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
            self.service = build("gmail", "v1", credentials=creds)
            return creds

        # Legacy file-based auth (CLI flow)
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_PATH.exists():
                    raise FileNotFoundError(
                        "credentials.json not found. Download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
                creds = flow.run_local_server(port=0)

            TOKEN_PATH.write_text(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)
        return None

    def fetch_emails(self, max_results: int = 50, days: int = 30) -> list[dict]:
        """Fetch emails from Gmail inbox within the last N days.

        Args:
            max_results: Maximum number of emails to fetch.
            days: Only fetch emails from the last N days.

        Returns:
            List of parsed email dictionaries.
        """
        if not self.service:
            self.authenticate()

        after_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).strftime("%Y/%m/%d")
        query = f"after:{after_date}"

        all_messages = []
        page_token = None

        while True:
            kwargs = {
                "userId": "me",
                "maxResults": min(max_results - len(all_messages), 100),
                "labelIds": ["INBOX"],
                "q": query,
            }
            if page_token:
                kwargs["pageToken"] = page_token

            results = self.service.users().messages().list(**kwargs).execute()
            all_messages.extend(results.get("messages", []))

            page_token = results.get("nextPageToken")
            if not page_token or len(all_messages) >= max_results:
                break

        emails = []
        for msg_meta in all_messages[:max_results]:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_meta["id"], format="full")
                .execute()
            )
            parsed = self._parse_message(msg)
            if parsed:
                emails.append(parsed)

        return emails

    def _parse_message(self, message: dict) -> dict | None:
        """Parse a raw Gmail API message into a structured dict."""
        headers = {h["name"]: h["value"] for h in message["payload"].get("headers", [])}

        subject = headers.get("Subject", "(No Subject)")
        sender = headers.get("From", "Unknown")
        date_str = headers.get("Date", "")

        try:
            timestamp = parsedate_to_datetime(date_str)
        except Exception:
            timestamp = datetime.datetime.now(datetime.timezone.utc)

        body = self._extract_body(message["payload"])

        return {
            "gmail_id": message["id"],
            "sender": sender,
            "subject": subject,
            "body": body,
            "timestamp": timestamp.isoformat(),
        }

    def _extract_body(self, payload: dict) -> str:
        """Extract plain text body from email payload."""
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

        parts = payload.get("parts", [])
        for part in parts:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                    "utf-8", errors="replace"
                )
            # Recurse into nested parts
            if part.get("parts"):
                result = self._extract_body(part)
                if result:
                    return result

        return ""
