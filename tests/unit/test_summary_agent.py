"""Unit tests for Summary Agent."""

import json
from unittest.mock import patch, MagicMock

import pytest

from backend.agents.summary_agent import SummaryAgent


class TestSummaryAgent:
    """Tests for the email summarization agent."""

    @patch("backend.agents.summary_agent.ChatGroq")
    def test_summarize_professor_email(self, mock_groq_class):
        """Test summarization of a professor email."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "summary": "Professor requesting project submission before March 20."
        })
        mock_groq_class.return_value = MagicMock()

        agent = SummaryAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.summarize({
            "subject": "Project Submission Form",
            "sender": "professor@university.edu",
            "body": "Submit the form before March 20. Mandatory requirement.",
            "category": "Professor",
            "priority": "HIGH",
        })

        assert "summary" in result
        assert len(result["summary"]) > 0

    @patch("backend.agents.summary_agent.ChatGroq")
    def test_summarize_promotion_email(self, mock_groq_class):
        """Test summarization of a promotional email."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "summary": "Amazon flash sale with 50% off electronics."
        })
        mock_groq_class.return_value = MagicMock()

        agent = SummaryAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.summarize({
            "subject": "Flash Sale - 50% off",
            "sender": "noreply@amazon.com",
            "body": "Don't miss our biggest sale!",
            "category": "Promotion",
            "priority": "LOW",
        })

        assert "summary" in result

    @patch("backend.agents.summary_agent.ChatGroq")
    def test_invalid_json_returns_subject(self, mock_groq_class):
        """Test fallback to subject when LLM returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.content = "not valid json"
        mock_groq_class.return_value = MagicMock()

        agent = SummaryAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.summarize({
            "subject": "Test Subject",
            "sender": "test@test.com",
            "body": "Test body",
            "category": "Personal",
            "priority": "LOW",
        })

        assert result["summary"] == "Test Subject"
