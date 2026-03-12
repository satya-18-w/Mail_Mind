"""Deadline Extraction Agent - Extracts time-sensitive deadlines from emails using Groq (free tier)."""

import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from backend.core.config import get_settings

DEADLINE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert at extracting deadlines and due dates from emails. "
        "Respond ONLY with valid JSON, no extra text.",
    ),
    (
        "human",
        """Extract any deadline or due date from this email.
Today's date is {today}.

Email Subject: {subject}
Email Body: {body}

If a deadline exists, return it in YYYY-MM-DD format.
If no deadline is found, return null.

Return JSON with format:
{{"deadline": "YYYY-MM-DD" | null, "action": "<what needs to be done or null>"}}""",
    ),
])


class DeadlineAgent:
    """Extracts deadlines and action items from emails."""

    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            temperature=0,
            max_tokens=100,
        )
        self.chain = DEADLINE_PROMPT | self.llm

    def extract(self, email: dict, today: str | None = None) -> dict:
        """Extract deadline from a single email.

        Args:
            email: Dict with 'subject' and 'body' keys.
            today: Today's date as YYYY-MM-DD string.

        Returns:
            Dict with 'deadline' and 'action' keys.
        """
        import datetime

        if today is None:
            today = datetime.date.today().isoformat()

        response = self.chain.invoke({
            "subject": email.get("subject", ""),
            "body": email.get("body", "")[:1000],
            "today": today,
        })

        try:
            result = json.loads(response.content)
            # Validate date format
            if result.get("deadline"):
                datetime.date.fromisoformat(result["deadline"])
            return result
        except (json.JSONDecodeError, AttributeError, ValueError):
            return {"deadline": None, "action": None}
