# mini_n8n

mini_n8n is a lightweight, AI-assisted workflow automation backend inspired by [n8n.io](https://n8n.io). It ships with a modular FastAPI service, asynchronous workflow execution engine, pluggable node system (HTTP, Delay, Condition, Python, LLM), optional LLM-driven workflow generator, and persistence via SQLite/SQLAlchemy.

## Project layout

```
mini_n8n/
├── backend/
│   ├── app/              # FastAPI application
│   │   ├── api/          # REST routes
│   │   ├── nodes/        # Node implementations + registry
│   │   ├── orchestrator/ # Execution engine
│   │   ├── llm/          # Providers & workflow generator
│   │   ├── storage/      # Database + CRUD helpers
│   │   ├── schemas/      # Pydantic models
│   │   └── tests/        # Pytest suite
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting started

### 1. Install dependencies

```bash
cd mini_n8n/backend
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000/docs` for interactive Swagger docs.

### 3. Docker / Compose

```
docker compose up --build
```

The service listens on port `8000` and persists workflow data in `./data/mini_n8n.db`.

## Configuration

`backend/app/config.py` reads environment variables prefixed with `MINI_N8N_`. Key options:

| Variable | Description | Default |
|----------|-------------|---------|
| `MINI_N8N_DATABASE_URL` | SQLAlchemy URL (async) | `sqlite+aiosqlite:///./mini_n8n.db` |
| `MINI_N8N_OPENAI_API_KEY` | Enables OpenAI provider | _unset_ |
| `MINI_N8N_VERTEX_PROJECT`, `MINI_N8N_VERTEX_LOCATION` | Enables Vertex AI provider | _unset_ |

## Testing

```
cd mini_n8n/backend
pytest
```

The suite covers node behavior, orchestrator logic, and API workflow lifecycle.

## API overview

- `POST /api/workflows` – create workflow definitions using JSON nodes
- `GET /api/workflows` / `GET /api/workflows/{id}` – inspect stored workflows
- `POST /api/workflows/{id}/run` – execute a workflow with runtime inputs
- `GET /api/workflows/{id}/logs` – fetch prior run logs
- `POST /api/workflows/generate` – optional LLM-assisted workflow draft
- `GET /health` – basic health probe

## Extending nodes

Add new node classes in `app/nodes/`, inherit from `BaseNode`, and register via `@register_node(NodeType.X)`. The orchestrator picks them up automatically once imported.

## LLM providers

`app/llm/provider.py` ships with:

- `HeuristicProvider` (default, no credentials required)
- `OpenAIProvider` (requires `openai` Python package + API key)
- `VertexAIProvider` (requires `google-cloud-aiplatform` package and project configuration)

Select providers per-node or per prompt via config.

## Future enhancements

- Persistence adapters beyond SQLite
- Richer branching, parallelism, and retries
- Frontend workflow builder
- Secrets management for node credentials

Contributions welcome!

