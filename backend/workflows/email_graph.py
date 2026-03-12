"""LangGraph email processing workflow.

Pipeline: Fetch -> Parse -> Classify -> Priority -> Deadline -> Summary -> Store

Each node is an independent agent step. State flows through the entire graph.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

from backend.agents.classifier_agent import ClassifierAgent
from backend.agents.priority_agent import PriorityAgent
from backend.agents.deadline_agent import DeadlineAgent
from backend.agents.summary_agent import SummaryAgent
from backend.services.embedding_service import EmbeddingService


class EmailState(TypedDict):
    """State that flows through the email processing pipeline."""
    gmail_id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    category: str | None
    subcategory: str | None
    priority: str | None
    deadline: str | None
    action: str | None
    summary: str | None
    embedding: list[float] | None
    error: str | None


# --- Node Functions ---

def classification_node(state: EmailState) -> dict:
    """Classify email into a category."""
    try:
        agent = ClassifierAgent()
        result = agent.classify(state)
        return {"category": result["category"], "subcategory": result.get("subcategory")}
    except Exception as e:
        return {"category": "Personal", "subcategory": None, "error": str(e)}


def priority_node(state: EmailState) -> dict:
    """Assess email priority."""
    try:
        agent = PriorityAgent()
        result = agent.assess(state)
        return {"priority": result["priority"]}
    except Exception as e:
        return {"priority": "LOW", "error": str(e)}


def deadline_node(state: EmailState) -> dict:
    """Extract deadline from email."""
    try:
        agent = DeadlineAgent()
        result = agent.extract(state)
        return {"deadline": result.get("deadline"), "action": result.get("action")}
    except Exception as e:
        return {"deadline": None, "action": None, "error": str(e)}


def summary_node(state: EmailState) -> dict:
    """Generate email summary."""
    try:
        agent = SummaryAgent()
        result = agent.summarize(state)
        return {"summary": result["summary"]}
    except Exception as e:
        return {"summary": state.get("subject", ""), "error": str(e)}


def embedding_node(state: EmailState) -> dict:
    """Generate embedding for semantic search."""
    try:
        service = EmbeddingService()
        text = f"{state.get('subject', '')} {state.get('body', '')[:500]}"
        embedding = service.embed(text)
        return {"embedding": embedding}
    except Exception as e:
        return {"embedding": None, "error": str(e)}


# --- Graph Builder ---

def build_email_graph() -> StateGraph:
    """Build and compile the LangGraph email processing workflow.

    Returns:
        Compiled StateGraph ready to invoke.
    """
    graph = StateGraph(EmailState)

    # Add nodes
    graph.add_node("classify", classification_node)
    graph.add_node("prioritize", priority_node)
    graph.add_node("extract_deadline", deadline_node)
    graph.add_node("summarize", summary_node)
    graph.add_node("embed", embedding_node)

    # Define edges (sequential pipeline)
    graph.set_entry_point("classify")
    graph.add_edge("classify", "prioritize")
    graph.add_edge("prioritize", "extract_deadline")
    graph.add_edge("extract_deadline", "summarize")
    graph.add_edge("summarize", "embed")
    graph.add_edge("embed", END)

    return graph.compile()


# Singleton compiled graph
email_pipeline = build_email_graph()


def process_email(email: dict) -> EmailState:
    """Process a single email through the full agent pipeline.

    Args:
        email: Dict with gmail_id, sender, subject, body, timestamp.

    Returns:
        Fully enriched EmailState with all agent results.
    """
    initial_state: EmailState = {
        "gmail_id": email["gmail_id"],
        "sender": email["sender"],
        "subject": email["subject"],
        "body": email["body"],
        "timestamp": email["timestamp"],
        "category": None,
        "subcategory": None,
        "priority": None,
        "deadline": None,
        "action": None,
        "summary": None,
        "embedding": None,
        "error": None,
    }

    result = email_pipeline.invoke(initial_state)
    return result
