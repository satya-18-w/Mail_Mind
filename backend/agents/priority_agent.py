"""Priority Agent - Determines email importance level using Groq (free tier).

Priority Levels: HIGH, MEDIUM, LOW
HIGH conditions: Deadline mentioned, Action required, Form submission, Academic requirement
"""

import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from backend.core.config import get_settings

PRIORITY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an email priority assessment expert. Determine the priority of emails. "
        "Respond ONLY with valid JSON, no extra text.",
    ),
    (
        "human",
        """Determine the priority of this email.

Priority Levels:
- HIGH: Deadline mentioned, action required, form submission, academic requirement, urgent
- MEDIUM: Informational but relevant, meeting updates, course announcements
- LOW: Newsletters, promotions, social media notifications, general updates

Email Subject: {subject}
Email From: {sender}
Email Category: {category}
Email Body (first 500 chars): {body}

Return JSON with format:
{{"priority": "HIGH" | "MEDIUM" | "LOW"}}""",
    ),
])


class PriorityAgent:
    """Determines email priority level."""

    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            temperature=0,
            max_tokens=50,
        )
        self.chain = PRIORITY_PROMPT | self.llm

    def assess(self, email: dict) -> dict:
        """Assess priority of a single email.

        Args:
            email: Dict with 'subject', 'sender', 'body', 'category' keys.

        Returns:
            Dict with 'priority' key.
        """
        response = self.chain.invoke({
            "subject": email.get("subject", ""),
            "sender": email.get("sender", ""),
            "category": email.get("category", "Personal"),
            "body": email.get("body", "")[:500],
        })

        try:
            result = json.loads(response.content)
            if result.get("priority") not in {"HIGH", "MEDIUM", "LOW"}:
                result["priority"] = "LOW"
            return result
        except (json.JSONDecodeError, AttributeError):
            return {"priority": "LOW"}
