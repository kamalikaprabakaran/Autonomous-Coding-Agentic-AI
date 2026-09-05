# Autonomous Coding Agentic AI

A production-oriented autonomous coding agent that can understand software repositories, plan coding tasks, inspect and modify files through controlled tools, execute code in a sandbox, run tests, analyse failures, and iteratively correct its implementation.

## Current Phase

**Phase 4 – Initial Agent Brain (LangGraph)** ✅

**Phase 3 – Coding Tool System** ✅
**Phase 2 – Repository Intelligence** ✅
**Phase 1 – Backend API Foundation** ✅
**Phase 0 – Foundation** ✅

Phase 3 implements the strictly bounded repository manipulation capabilities natively, creating structured objects for File Reading, File Listing, Fast Search iteration (via ripgrep fallback bounds), and Ambiguity-resilient file editing. These operate entirely sandboxed inside specific repository limits checking against path traversals.

## Project Structure

```
autonomous-coding-agent/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application & entry point
│   │   ├── core/
│   │   │   ├── config.py     # Pydantic Settings configuration
│   │   │   ├── exceptions.py # NotFoundError and handlers
│   │   │   └── logging.py    # Structured logging setup
│   │   ├── api/              # API routers (/projects, /tasks, /agent)
│   │   ├── agents/           # LangGraph agents (future)
│   │   ├── models/           # Domain models 
│   │   ├── repositories/     # In-memory persistence layers
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic layer
│   │   │   └── analyzer/     # Repository Intelligence subsystem
│   │   ├── tools/            # Agent tools (future)
│   │   └── utils/            # Shared utilities (future)
│   └── tests/                # Comprehensive Pytest test suite
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

## Available Endpoints

The API is structured around REST principles.

### Projects
- `GET /projects`: List all managed projects
- `POST /projects`: Create a new project
- `GET /projects/{project_id}`: Retrieve a project
- `GET /projects/{project_id}/analysis`: Retrieve full repository metrics and AST summary

### Tasks
- `POST /tasks`: Create a new coding task attached to a project
- `GET /tasks/{task_id}`: Retrieve a coding task by ID

### Agent Runs
- `GET /agent/status/{run_id}`: Retrieve agent execution status

*Plus the standard `GET /health` and Swagger UI at `GET /docs`.*

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

The Swagger UI will be available at: `http://localhost:8000/docs`
The health endpoint is available at: `http://localhost:8000/health`

## Example Usage

Create a project:
```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "My first AI project"}'
```

Create a task for the project (using the returned UUID):
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "<UUID_HERE>", "description": "Build an authentication service"}'
```

## Running Tests

```bash
pytest -v
```

All 29 tests cover endpoints, business logic validation, 404 responses, and data models cleanly using isolated `app.state` instances.

## Current Limitations

- **Transient Storage**: The backend currently uses an in-memory repository layer. Restarting the server clears all projects and tasks. Firebase persistence will replace this in a future phase.
- **Empty Agent Runs**: The agent endpoints exist to track status, but no AI is actually hooked up to execute runs (Phase 1 focus only).

## Future Phases

| Phase | Scope |
|-------|-------|
| 2 | Tree-sitter code analysis & file tools |
| 3 | Sandboxed code execution (Docker) |
| 4 | GitHub integration & PR workflows |
| 5 | React + TypeScript frontend |
| 6 | Firebase persistence & auth |
| 7 | OpenTelemetry observability |
