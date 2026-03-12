"""Unit tests for Deadline Extraction Agent."""

import json
from unittest.mock import patch, MagicMock

import pytest

from backend.agents.deadline_agent import DeadlineAgent


class TestDeadlineAgent:
    """Tests for the deadline extraction agent."""

    @patch("backend.agents.deadline_agent.ChatGroq")
    def test_extract_explicit_deadline(self, mock_groq_class):
        """Test extraction of a clear deadline."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "deadline": "2026-03-20",
            "action": "Submit project proposal form",
        })
        mock_groq_class.return_value = MagicMock()

        agent = DeadlineAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.extract(
            {
                "subject": "Project Submission Form",
                "body": "Submit the project proposal before March 20, 2026.",
            },
            today="2026-03-12",
        )

        assert result["deadline"] == "2026-03-20"
        assert result["action"] is not None

    @patch("backend.agents.deadline_agent.ChatGroq")
    def test_no_deadline_found(self, mock_groq_class):
        """Test when no deadline exists in email."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"deadline": None, "action": None})
        mock_groq_class.return_value = MagicMock()

        agent = DeadlineAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.extract({
            "subject": "Flash Sale",
            "body": "50% off on all electronics!",
        })

        assert result["deadline"] is None

    @patch("backend.agents.deadline_agent.ChatGroq")
    def test_invalid_json_returns_none(self, mock_groq_class):
        """Test fallback when LLM returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.content = "not valid json"
        mock_groq_class.return_value = MagicMock()

        agent = DeadlineAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.extract({
            "subject": "Test",
            "body": "Test body",
        })

        assert result["deadline"] is None
        assert result["action"] is None

    @patch("backend.agents.deadline_agent.ChatGroq")
    def test_invalid_date_format_returns_none(self, mock_groq_class):
        """Test fallback when LLM returns invalid date format."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "deadline": "March 20, 2026",  # Not YYYY-MM-DD
            "action": "Submit form",
        })
        mock_groq_class.return_value = MagicMock()

        agent = DeadlineAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.extract({
            "subject": "Test",
            "body": "Due March 20",
        })

        assert result["deadline"] is None

    @patch("backend.agents.deadline_agent.ChatGroq")
    def test_registration_deadline(self, mock_groq_class):
        """Test extraction of registration deadline."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "deadline": "2026-03-25",
            "action": "Complete semester registration",
        })
        mock_groq_class.return_value = MagicMock()

        agent = DeadlineAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.extract({
            "subject": "Semester Registration Deadline - March 25",
            "body": "All students must complete registration by March 25, 2026.",
        })

        assert result["deadline"] == "2026-03-25"
