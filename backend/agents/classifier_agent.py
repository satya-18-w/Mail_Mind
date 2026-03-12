"""Classification Agent - Classifies emails into categories using Groq (free tier).

Categories: Institute, Professor, LinkedIn, Society, Promotion, Personal
"""

import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from backend.core.config import get_settings

CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an email classification expert. Classify emails into exactly one category. "
        "Respond ONLY with valid JSON, no extra text.",
    ),
    (
        "human",
        """Classify the following email into one of these categories:
- Institute
- Professor
- LinkedIn
- Society
- Promotion
- Personal

Email Subject: {subject}
Email From: {sender}
Email Body (first 500 chars): {body}

Return JSON with format:
{{"category": "<category>", "subcategory": "<optional subcategory or null>"}}""",
    ),
])


class ClassifierAgent:
    """Classifies emails into predefined categories."""

    def __init__(self):
        settings = get_settings()
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            temperature=0,
            max_tokens=100,
        )
        self.chain = CLASSIFICATION_PROMPT | self.llm

    def classify(self, email: dict) -> dict:
        """Classify a single email.

        Args:
            email: Dict with 'subject', 'sender', 'body' keys.

        Returns:
            Dict with 'category' and 'subcategory' keys.
        """
        response = self.chain.invoke({
            "subject": email.get("subject", ""),
            "sender": email.get("sender", ""),
            "body": email.get("body", "")[:500],
        })

        try:
            result = json.loads(response.content)
            valid_categories = {"Institute", "Professor", "LinkedIn", "Society", "Promotion", "Personal"}
            if result.get("category") not in valid_categories:
                result["category"] = "Personal"
            return result
        except (json.JSONDecodeError, AttributeError):
            return {"category": "Personal", "subcategory": None}
