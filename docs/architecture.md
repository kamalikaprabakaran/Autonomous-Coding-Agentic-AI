# Architecture

## Overview

The Autonomous Coding Agentic AI is designed as a modular, layered system where each component has a single, well-defined responsibility. This separation enables independent development, testing, and future replacement of individual components.

## Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        Frontend (React/TS)                       │
│                         (future phase)                           │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼───────────────────────────────────────┐
│                        API Layer (FastAPI)                        │
│  ┌──────────┐  ┌────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │  /health  │  │  /tasks    │  │  /agents    │  │  /repos    │  │
│  └──────────┘  └─────┬──────┘  └──────┬──────┘  └─────┬──────┘  │
└───────────────────────┼───────────────┼───────────────┼──────────┘
                        │               │               │
┌───────────────────────▼───────────────▼───────────────▼──────────┐
│                      Services Layer                               │
│  Orchestrates business logic, coordinates agents and tools        │
└───────────────────────┬───────────────┬──────────────────────────┘
                        │               │
          ┌─────────────▼──┐   ┌────────▼──────────┐
          │  Agents Layer   │   │   Tools Layer      │
          │  (LangGraph)    │   │  (file, exec, git) │
          └─────────────────┘   └────────────────────┘
                        │               │
┌───────────────────────▼───────────────▼──────────────────────────┐
│                      Core Layer                                   │
│  Config · Logging · LLM Provider Abstraction · Shared Models      │
└──────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### `core/` – Infrastructure Foundation

| Module | Responsibility |
|--------|---------------|
| `config.py` | Load and validate configuration from environment variables using Pydantic Settings |
| `logging.py` | Structured application logging with configurable level |

### `api/` – HTTP Interface

Defines FastAPI route handlers. Each route delegates to a service; no business logic lives here. Currently exposes only `GET /health`.

### `agents/` – LangGraph Agents *(future)*

Contains LangGraph graph definitions for autonomous coding workflows: planning, code generation, testing, and self-correction loops.

### `services/` – Business Logic

Coordinates workflows across agents and internal components.

#### `analyzer/` – Repository Intelligence Subsystem
A specialized service boundary that reads and analyzes codebases without modifying them:
- **discovery**: Maps directory structures, bounding path traversals inside repository roots, caching file sizes and ignoring configured directories (`.venv`, `.git`, etc.).
- **search**: Fast, boundary-aware search, invoking system `ripgrep` optionally via JSON schemas, and falling back to native Python `os.walk` if missing.
- **parser**: Tree-sitter integration that analyzes `.py` files to discover AST level constructs (classes, methods, functions, imports). Safely catches parse failures or drops massive files (>1MB) without breaking standard traversal.

### `tools/` – Agent-Callable Tools
Individual, sandboxed capabilities the agents can invoke on isolated repositories:
- **Interfaces**: Strongly-typed structures (`ToolResult`, `ListFilesInput`, etc).
- **Tool Registry**: Base manager class where arbitrary tools combine by namespace and enforce validation natively.
- **File Tools**: `list_files`, `read_file`, `write_file`, `edit_file`, and `get_file_info`. Protected recursively mapping boundary traversals (`../../`) to block system leakage, and applying smart parsing (dropping large files & binaries).
- **Search Tool**: Harnesses AST searching from `search.py` wrapped directly into an accessible Agent Interface returning json output logs.

### *Future capabilities (Phase 5+)*
- **Git tools** – commit, branch, diff, create PRs
- **Code execution** - run code inside a Docker sandbox

### `services/` – Business Logic *(future)*

Coordinates multi-step workflows across agents and tools. Examples: "analyse a repository", "implement a feature request with tests".

### `models/` – Data Schemas *(future)*

Pydantic models shared across layers: task definitions, agent state, tool inputs/outputs.

### `utils/` – Shared Utilities *(future)*

Stateless helper functions (string processing, retry logic, etc.) used across multiple layers.

## Data Flow

```
User Request
    │
    ▼
API Layer ──▶ validates input, creates task
    │
    ▼
Services Layer ──▶ orchestrates workflow
    │
    ▼
Agents Layer ──▶ LangGraph executes plan/code/test cycle
    │
    ├──▶ Tools Layer ──▶ reads/writes files, runs code
    │
    ▼
Response ──▶ streamed back through API to frontend
```

## Why Components Are Separated

| Principle | Rationale |
|-----------|-----------|
| **Single Responsibility** | Each module does one thing, making it easy to understand, test, and replace. |
| **Layer Isolation** | API handlers never touch the file system directly; agents never know about HTTP. This prevents coupling. |
| **Testability** | Small, focused components can be unit-tested with simple mocks, without spinning up the entire stack. |
| **Extensibility** | Adding a new tool (e.g., database queries) requires creating one file in `tools/`, with zero changes to the API or agent layers. |
| **Security Boundary** | Code execution is isolated in `tools/` behind a Docker sandbox, preventing accidental damage to the host system. |
