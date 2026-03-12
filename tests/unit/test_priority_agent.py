"""Unit tests for Priority Agent."""

import json
from unittest.mock import patch, MagicMock

import pytest

from backend.agents.priority_agent import PriorityAgent


class TestPriorityAgent:
    """Tests for the email priority assessment agent."""

    @patch("backend.agents.priority_agent.ChatGroq")
    def test_high_priority_deadline_email(self, mock_groq_class):
        """Test HIGH priority for email with deadline."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"priority": "HIGH"})
        mock_groq_class.return_value = MagicMock()

        agent = PriorityAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.assess({
            "subject": "Project Submission Form - Due March 20",
            "sender": "professor@university.edu",
            "body": "Submit the form before March 20. This is mandatory.",
            "category": "Professor",
        })

        assert result["priority"] == "HIGH"

    @patch("backend.agents.priority_agent.ChatGroq")
    def test_low_priority_promotion(self, mock_groq_class):
        """Test LOW priority for promotional email."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"priority": "LOW"})
        mock_groq_class.return_value = MagicMock()

        agent = PriorityAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.assess({
            "subject": "Flash Sale - 50% off",
            "sender": "noreply@amazon.com",
            "body": "Don't miss our biggest sale!",
            "category": "Promotion",
        })

        assert result["priority"] == "LOW"

    @patch("backend.agents.priority_agent.ChatGroq")
    def test_medium_priority_society(self, mock_groq_class):
        """Test MEDIUM priority for society event."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"priority": "MEDIUM"})
        mock_groq_class.return_value = MagicMock()

        agent = PriorityAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.assess({
            "subject": "Tech Talk - March 15",
            "sender": "ieee@college.edu",
            "body": "Join us for a tech talk on AI.",
            "category": "Society",
        })

        assert result["priority"] == "MEDIUM"

    @patch("backend.agents.priority_agent.ChatGroq")
    def test_invalid_json_returns_low(self, mock_groq_class):
        """Test fallback to LOW when LLM returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.content = "not json"
        mock_groq_class.return_value = MagicMock()

        agent = PriorityAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.assess({
            "subject": "Test",
            "sender": "test@test.com",
            "body": "Test",
            "category": "Personal",
        })

        assert result["priority"] == "LOW"

    @patch("backend.agents.priority_agent.ChatGroq")
    def test_invalid_priority_defaults_low(self, mock_groq_class):
        """Test fallback when LLM returns invalid priority."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"priority": "CRITICAL"})
        mock_groq_class.return_value = MagicMock()

        agent = PriorityAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.assess({
            "subject": "Test",
            "sender": "test@test.com",
            "body": "Test",
            "category": "Personal",
        })

        assert result["priority"] == "LOW"
