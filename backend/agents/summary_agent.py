"""Summary Agent - Generates concise email summaries using Groq (free tier, Mixtral)."""

import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from backend.core.config import get_settings

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert email summarizer. Create brief, actionable summaries. "
        "Respond ONLY with valid JSON, no extra text.",
    ),
    (
        "human",
        """Summarize this email in one concise sentence (max 100 words).

Email Subject: {subject}
Email From: {sender}
Email Category: {category}
Email Priority: {priority}
Email Body (first 800 chars): {body}

Return JSON with format:
{{"summary": "<one sentence summary>"}}""",
    ),
])


class SummaryAgent:
    """Generates concise email summaries."""

    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            temperature=0.3,
            max_tokens=150,
        )
        self.chain = SUMMARY_PROMPT | self.llm

    def summarize(self, email: dict) -> dict:
        """Generate summary for a single email.

        Args:
            email: Dict with 'subject', 'sender', 'body', 'category', 'priority' keys.

        Returns:
            Dict with 'summary' key.
        """
        response = self.chain.invoke({
            "subject": email.get("subject", ""),
            "sender": email.get("sender", ""),
            "category": email.get("category", "Personal"),
            "priority": email.get("priority", "LOW"),
            "body": email.get("body", "")[:800],
        })

        try:
            result = json.loads(response.content)
            return result
        except (json.JSONDecodeError, AttributeError):
            return {"summary": email.get("subject", "No summary available")}
