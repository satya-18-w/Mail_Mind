"""Unit tests for Classification Agent."""

import json
from unittest.mock import patch, MagicMock

import pytest

from backend.agents.classifier_agent import ClassifierAgent


class TestClassifierAgent:
    """Tests for the email classification agent."""

    @patch("backend.agents.classifier_agent.ChatGroq")
    def test_classify_institute_email(self, mock_groq_class):
        """Test classification of an institute email."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = json.dumps({"category": "Institute", "subcategory": "Academic"})
        mock_llm.__or__ = MagicMock(return_value=MagicMock(invoke=MagicMock(return_value=mock_response)))
        mock_groq_class.return_value = mock_llm

        agent = ClassifierAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.classify({
            "subject": "Semester Registration Deadline",
            "sender": "admin@university.edu",
            "body": "All students must complete registration by March 25.",
        })

        assert result["category"] == "Institute"

    @patch("backend.agents.classifier_agent.ChatGroq")
    def test_classify_linkedin_email(self, mock_groq_class):
        """Test classification of a LinkedIn email."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = json.dumps({"category": "LinkedIn", "subcategory": None})
        mock_groq_class.return_value = mock_llm

        agent = ClassifierAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.classify({
            "subject": "5 new connection requests",
            "sender": "notifications@linkedin.com",
            "body": "You have 5 new connection requests.",
        })

        assert result["category"] == "LinkedIn"

    @patch("backend.agents.classifier_agent.ChatGroq")
    def test_classify_promotion_email(self, mock_groq_class):
        """Test classification of a promotional email."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"category": "Promotion", "subcategory": None})
        mock_groq_class.return_value = MagicMock()

        agent = ClassifierAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.classify({
            "subject": "Flash Sale - 50% off",
            "sender": "noreply@amazon.com",
            "body": "Don't miss our biggest sale!",
        })

        assert result["category"] == "Promotion"

    @patch("backend.agents.classifier_agent.ChatGroq")
    def test_classify_invalid_json_returns_personal(self, mock_groq_class):
        """Test fallback to Personal when LLM returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.content = "This is not valid JSON"
        mock_groq_class.return_value = MagicMock()

        agent = ClassifierAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.classify({
            "subject": "Test",
            "sender": "test@test.com",
            "body": "Test body",
        })

        assert result["category"] == "Personal"
        assert result["subcategory"] is None

    @patch("backend.agents.classifier_agent.ChatGroq")
    def test_classify_invalid_category_defaults_personal(self, mock_groq_class):
        """Test fallback when LLM returns an invalid category."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"category": "InvalidCategory", "subcategory": None})
        mock_groq_class.return_value = MagicMock()

        agent = ClassifierAgent()
        agent.chain = MagicMock(invoke=MagicMock(return_value=mock_response))

        result = agent.classify({
            "subject": "Test",
            "sender": "test@test.com",
            "body": "Test body",
        })

        assert result["category"] == "Personal"
