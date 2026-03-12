# AI Mail Intelligence Agent

A multi-agent AI system that reads, classifies, prioritizes, and organizes emails using LLMs. Built with FastAPI, LangGraph, Next.js, and PostgreSQL.

## Architecture

```
USER DASHBOARD (Next.js)
        |
    API Gateway (FastAPI)
        |
   ┌────┴────────────┐
   |                  |
Gmail Fetcher    AI Pipeline (LangGraph)
                      |
        ┌─────────────┼──────────┐──────────┐
   Classifier    Priority   Deadline    Summary
    Agent         Agent      Agent       Agent
        |
   PostgreSQL + pgvector
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| AI Agents | LangGraph, LangChain |
| LLM | Groq (Llama 3.3 70B + Mixtral 8x7B) - **Free tier** |
| Embeddings | BAAI/bge-small-en-v1.5 - **Local, free** |
| Database | PostgreSQL + pgvector |
| Scheduler | Celery + Redis |
| Frontend | Next.js 14, TailwindCSS, React Query |
| Deployment | Docker Compose |

## Project Structure

```
ai-mail-agent/
├── backend/
│   ├── agents/           # AI agents (classifier, priority, deadline, summary)
│   ├── api/              # FastAPI routes & schemas
│   ├── core/             # Config & settings
│   ├── database/         # SQLAlchemy models & CRUD
│   ├── scheduler/        # Celery worker & beat
│   ├── services/         # Gmail fetcher, embedding service
│   ├── workflows/        # LangGraph pipeline
│   └── main.py           # FastAPI app entry
├── frontend/
│   └── src/
│       ├── app/          # Next.js pages
│       ├── components/   # React UI components
│       ├── hooks/        # React Query hooks
│       ├── services/     # API client
│       └── types/        # TypeScript types
├── tests/
│   ├── unit/             # Agent unit tests
│   └── integration/      # API integration tests
├── docker-compose.yml
└── pyproject.toml
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL with pgvector extension
- Redis
- Groq API key (free at https://console.groq.com)
- Gmail API credentials (from Google Cloud Console)

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Install Backend

```bash
pip install -e ".[dev]"
```

### 3. Install Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

### 4. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project and enable Gmail API
3. Create OAuth2 credentials (Desktop App)
4. Download `credentials.json` to project root

### 5. Run with Docker

```bash
docker compose up -d
```

Or run individually:

```bash
# Backend
uvicorn backend.main:app --reload

# Frontend
cd frontend && npm run dev

# Celery worker
celery -A backend.scheduler.worker worker --loglevel=info

# Celery beat (scheduler)
celery -A backend.scheduler.worker beat --loglevel=info
```

### 6. Run Tests

```bash
python -m pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/emails` | List all emails |
| GET | `/api/v1/emails/{id}` | Get email by ID |
| GET | `/api/v1/emails/category/{category}` | Filter by category |
| GET | `/api/v1/emails/priority/{priority}` | Filter by priority |
| GET | `/api/v1/emails/deadlines/upcoming` | Get deadline emails |
| POST | `/api/v1/emails/search` | Semantic search |
| GET | `/api/v1/stats/categories` | Category counts |
| GET | `/api/v1/stats/priorities` | Priority counts |
| GET | `/api/v1/tasks` | Pending tasks |
| POST | `/api/v1/pipeline/run` | Trigger email scan |
| GET | `/health` | Health check |

## AI Agents

- **Classifier Agent**: Categorizes emails into Institute, Professor, LinkedIn, Society, Promotion, Personal
- **Priority Agent**: Assigns HIGH/MEDIUM/LOW priority based on urgency and action requirements
- **Deadline Agent**: Extracts dates and action items from email content
- **Summary Agent**: Generates one-sentence summaries for quick scanning

## Cost

**$0** - All AI models use free tiers:
- Groq API: Free tier for Llama 3.3 70B and Mixtral 8x7B
- BAAI/bge-small: Runs locally via sentence-transformers
- PostgreSQL/Redis: Self-hosted via Docker
