# Autonomous Coding Agentic AI

A production-oriented autonomous coding agent that can understand software repositories, plan coding tasks, inspect and modify files through controlled tools, execute code in a sandbox, run tests, analyse failures, and iteratively correct its implementation.

## Current Phase

**Phase 0 – Foundation** ✅

Establishes the project skeleton, configuration management, structured logging, health endpoint, and test infrastructure.

## Project Structure

```
autonomous-coding-agent/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application & /health endpoint
│   │   ├── core/
│   │   │   ├── config.py     # Pydantic Settings configuration
│   │   │   └── logging.py    # Structured logging setup
│   │   ├── api/              # API routes (future)
│   │   ├── agents/           # LangGraph agents (future)
│   │   ├── tools/            # Agent tools (future)
│   │   ├── services/         # Business logic (future)
│   │   ├── models/           # Data models (future)
│   │   └── utils/            # Shared utilities (future)
│   └── tests/                # Pytest test suite
├── frontend/                 # React + TypeScript UI (future)
├── docker/                   # Container configs (future)
├── docs/
│   └── architecture.md       # Architecture documentation
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd autonomous-coding-agent

# Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create your environment file
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```

## Running the Backend

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The health endpoint will be available at: `http://localhost:8000/health`

## Running Tests

```bash
pytest -v
```

## Future Phases

| Phase | Scope |
|-------|-------|
| 1 | LLM provider abstraction & basic agent loop |
| 2 | Tree-sitter code analysis & file tools |
| 3 | Sandboxed code execution (Docker) |
| 4 | GitHub integration & PR workflows |
| 5 | React + TypeScript frontend |
| 6 | Firebase persistence & auth |
| 7 | OpenTelemetry observability |
