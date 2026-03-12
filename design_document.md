AI Mail Intelligence Agent

System Design Document

Version: 1.0
Author: Satyajit Samal
Project Type: Personal AI Multi-Agent System
Architecture: AI + Microservices + Agent Workflow

1. Project Overview
Problem

Email inbox contains many different types of messages such as:

LinkedIn notifications

Educational institute emails

Professor communications

Society announcements

Promotional emails

Important emails such as academic deadlines or forms get buried among less important notifications.

Goal

Build a multi-agent AI system that:

Reads all emails from mailbox

Understands content using LLMs

Clusters emails into categories

Assigns priority levels

Extracts deadlines and actions

Displays organized emails in a modern UI dashboard

Allows quick filtering and viewing

2. Key Features
Email Intelligence

Email classification

Email clustering

Priority detection

Deadline extraction

Email summarization

UI Features

Email category dashboard

Priority filtering

Action-required inbox

Deadline view

Email summary view

Agent Features

Multi-agent pipeline

Autonomous email processing

Scheduled email scanning

Context storage

Semantic search

3. System Architecture
                USER DASHBOARD
                      |
                      v
                Frontend (Next.js)
                      |
                      v
                API Gateway
                      |
                      v
                Backend Service
                      |
          -----------------------------
          |           |              |
     Email Fetcher   AI Agents    Database
                         |
                ---------------------
                |       |      |
           Classifier  Priority  Deadline
4. Technology Stack
Backend

Language:
Python 3.11+

Framework:
FastAPI

Agent Framework:
LangGraph

Database:
PostgreSQL

Vector Database:
pgvector

Scheduler:
Celery + Redis

Frontend

Framework:
Next.js 14

UI Library:
Shadcn UI

Styling:
TailwindCSS

State Management:
React Query

Charts:
Recharts

AI Models

Classification Model:
Llama 3 70B (Groq)

Embedding Model:
BAAI bge-small

Summarization:
Mixtral 8x7b

5. Multi-Agent Architecture

The system uses specialized AI agents.

Agent Types

Email Fetch Agent

Classification Agent

Priority Agent

Deadline Extraction Agent

Summarization Agent

Notification Agent

6. Agent Workflow

Pipeline:

Email Fetch Agent
        |
        v
Email Parsing Agent
        |
        v
Classification Agent
        |
        v
Priority Agent
        |
        v
Deadline Agent
        |
        v
Summary Agent
        |
        v
Database Storage Agent
7. Email Fetch Agent

Responsible for retrieving emails.

Source:
Gmail API

Capabilities:

Fetch latest emails

Parse subject/body

Extract sender

Detect attachments

Output format

{
 "id": "email_id",
 "sender": "example@university.edu",
 "subject": "Project Submission Form",
 "body": "Please submit the form before March 20",
 "timestamp": "2026-03-12"
}
8. Classification Agent

Classifies emails into categories.

Categories

Institute

Professor

LinkedIn

Society

Promotions

Personal

Prompt Template

Classify the following email.

Categories:
Institute
Professor
LinkedIn
Society
Promotion
Personal

Return JSON.

Example Output

{
 "category": "Institute",
 "subcategory": "Professor"
}
9. Priority Agent

Determines importance.

Priority Levels

High
Medium
Low

High Priority Conditions

Deadline mentioned

Action required

Form submission

Academic requirement

Output

{
 "priority": "HIGH"
}
10. Deadline Extraction Agent

Extracts time sensitive tasks.

Example

Input

Submit the project proposal before March 20

Output

{
 "deadline": "2026-03-20"
}
11. Email Summary Agent

Generates a short summary.

Example

Professor requesting project submission before March 20
12. Database Design
Emails Table

Fields

id
sender
subject
body
category
subcategory
priority
deadline
summary
timestamp
Categories Table
id
name
count
Tasks Table
id
email_id
deadline
status
priority
13. API Design

Base URL

/api/v1

Endpoints

Get Emails by Category
GET /emails/category/{category}
Get High Priority Emails
GET /emails/priority/high
Get Deadlines
GET /emails/deadlines
Search Emails
POST /emails/search

Uses semantic search.

14. Frontend UI

Dashboard Layout

---------------------------------------
AI Mail Intelligence
---------------------------------------

Sidebar

Institute (12)
LinkedIn (52)
Societies (6)
Promotions (120)

High Priority (4)

---------------------------------------

Email List

[HIGH] Project Submission Form
[MED] Society Meeting Announcement
[LOW] LinkedIn Notification

---------------------------------------

Email Detail

Summary
Deadline
Action Required
15. UI Components

Components to build

Sidebar
EmailList
EmailCard
PriorityBadge
DeadlineAlert
EmailDetailPanel
SearchBar
16. Folder Structure
ai-mail-agent
│
├── backend
│
│   ├── agents
│   │   ├── classifier_agent.py
│   │   ├── priority_agent.py
│   │   ├── deadline_agent.py
│   │   └── summary_agent.py
│
│   ├── services
│   │   └── gmail_fetcher.py
│
│   ├── workflows
│   │   └── email_graph.py
│
│   ├── api
│   │   └── email_routes.py
│
│   ├── database
│   │   └── models.py
│
│   └── scheduler
│       └── worker.py
│
├── frontend
│
│   ├── components
│   ├── pages
│   ├── services
│   └── hooks
│
└── tests
17. LangGraph Workflow

Graph Definition

fetch_email_node
      |
parse_email_node
      |
classification_node
      |
priority_node
      |
deadline_node
      |
summary_node
      |
database_node

Each node is an independent agent.

18. Scheduler

Email scanning frequency

Every 5 minutes.

Scheduler triggers

fetch_email_agent
19. Testing Strategy
Unit Tests

Test each agent independently.

Examples

test_classifier.py
test_priority_agent.py
test_deadline_agent.py
Integration Tests

Test full pipeline

email -> classification -> priority -> database
UI Tests

Use

Playwright

Test cases

category filtering

email viewing

deadline alerts

20. Security

OAuth2 authentication for Gmail.

Secrets stored in

.env

Sensitive data encrypted.

21. Performance Considerations

Batch email processing

Vector search caching

Async API calls

22. Observability

Logging system

OpenTelemetry

Monitoring

Prometheus
Grafana
23. Deployment

Dockerized services.

Infrastructure

Docker
Redis
PostgreSQL
FastAPI
Next.js

Cloud Options

AWS
GCP
Railway
Render

24. Future Features
AI Email Reply

Generate replies automatically.

Calendar Integration

Extract meetings from emails.

Voice Query

Example

Show emails with deadlines this week
Autonomous Inbox Cleaning

Archive low priority emails automatically.

25. Acceptance Criteria

The system is complete when:

Emails fetched automatically

Emails categorized correctly

Priority detection works

Deadlines extracted

Dashboard UI displays emails

Filters work

Tests pass

26. Copilot Build Instruction

Give the following instruction to Copilot Workspace:

Build a full-stack AI email assistant system using:

Backend:
Python
FastAPI
LangGraph
PostgreSQL
pgvector
Celery

Frontend:
Next.js
Tailwind
Shadcn UI

Features:
Multi-agent email classification
Priority detection
Deadline extraction
Dashboard UI
Semantic search
Automated tests

Follow the architecture and folder structure from the system design document.

If you want, I can also give you a MUCH MORE POWERFUL version of this system:

A true autonomous inbox AI system (like a mini Gmail AI) with:

Critical point:

i want to build all this system with 0 cost so use those api which is 0 cost in langchain and langgraph and tackle my work perfectly

build the skill and mcp that need to build the project effectively and i want the databases and other running in docker in development phase
