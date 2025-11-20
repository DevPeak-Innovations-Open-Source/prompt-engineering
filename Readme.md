Mini N8N – AI-Powered Workflow Automation System

A lightweight, Python-based automation engine inspired by n8n.io

Build, execute, and manage workflows using modular nodes — including HTTP calls, conditions, Python code, and LLM-powered automation.

✨ Key Features

🧩 Modular Node System – Easily extend with custom node types

🌐 HTTP Request Node – Full REST API support (GET, POST, PUT, DELETE)

⏱️ Delay Node – Pause execution for a specified duration

⚖️ Condition Node – Branch logic dynamically using operators (==, >, contains, etc.)

🧮 Python Code Node – Run custom Python code securely

🤖 LLM Node – Integrate with OpenAI, Google Gemini, or other LLMs

⚡ Asynchronous Execution – Built with FastAPI and async/await

🔁 Workflow Orchestration – Robust engine to manage execution order & state

🧠 AI Workflow Generation – Create workflows from plain English descriptions

💾 Persistent Storage – SQLite (async) or PostgreSQL via SQLAlchemy

🧱 RESTful API – Complete API for workflow management & execution

🐳 Docker Support – Simple container deployment

🧪 Full Test Suite – Nodes, orchestrator, and API coverage

📦 Installation
Prerequisites

Python 3.11+

pip

(Optional) Docker & Docker Compose

Local Setup
git clone <repository-url>
cd mini_n8n

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Copy and edit environment variables
cp .env.example .env

Run the App
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


API available at 👉 http://localhost:8000

Interactive docs at 👉 http://localhost:8000/docs

⚡ Quick Start (Using Docker)
# Optional: Set your LLM key
export OPENAI_API_KEY=your-api-key-here

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f


Stop or rebuild anytime:

docker-compose down
docker-compose up -d --build

🧰 Create Your First Workflow
import requests

workflow = {
    "name": "Hello Workflow",
    "description": "Delays and returns a greeting",
    "start_node": "delay1",
    "nodes": [
        {
            "id": "delay1",
            "type": "delay",
            "config": {"seconds": 2},
            "next_nodes": ["python1"]
        },
        {
            "id": "python1",
            "type": "python_code",
            "config": {
                "code": "output['message'] = 'Hello, ' + input_data.get('name', 'World')"
            }
        }
    ]
}

# Create and execute
w = requests.post("http://localhost:8000/api/v1/workflows/", json=workflow).json()
r = requests.post("http://localhost:8000/api/v1/workflows/execute",
                  json={"workflow_id": w["id"], "input_data": {"name": "Dhruv"}})
print(r.json())

🧱 Project Structure
mini_n8n/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Config management
│   │   ├── api/routes_workflow.py
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── nodes/               # Node implementations
│   │   ├── orchestrator/        # Workflow engine & executor
│   │   ├── llm/                 # LLM providers & AI workflow generator
│   │   ├── storage/             # CRUD + DB connectors
│   │   ├── models/              # SQLAlchemy models
│   │   └── tests/               # Unit tests
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md

🔧 Supported Node Types
Node Type	Description
HTTP Request	Call external APIs using any HTTP method
Delay	Pause workflow for a set duration
Condition	Route execution based on logical conditions
Python Code	Execute custom Python snippets
LLM	Use AI models (OpenAI, Gemini, etc.) for generation or reasoning
🌐 API Endpoints
Endpoint	Method	Description
/api/v1/workflows/	POST	Create new workflow
/api/v1/workflows/	GET	List all workflows
/api/v1/workflows/{id}	GET	Retrieve workflow
/api/v1/workflows/{id}	PUT	Update workflow
/api/v1/workflows/{id}	DELETE	Delete workflow
/api/v1/workflows/execute	POST	Execute workflow
/api/v1/workflows/generate	POST	Generate workflow from text
/health	GET	Health check
/	GET	API info

📘 Full Swagger docs: http://localhost:8000/docs

⚙️ Configuration

Environment variables (.env):

APP_NAME=mini_n8n
DATABASE_URL=sqlite+aiosqlite:///./mini_n8n.db
LLM_PROVIDER=gemini
OPENAI_API_KEY=your-key
MAX_WORKFLOW_EXECUTION_TIME=3600
MAX_NODE_RETRIES=3


Supports both SQLite (default) and PostgreSQL.

💡 Example Workflows
1. API Data Processor

Fetch data, check status, and process results.

{
  "name": "API Data Processor",
  "start_node": "fetch",
  "nodes": [
    {"id": "fetch", "type": "http_request", "config": {"url": "https://api.example.com/users/{id}"}},
    {"id": "check", "type": "condition", "config": {"field": "status_code", "operator": "==", "value": 200}},
    {"id": "process", "type": "python_code", "config": {"code": "output['name'] = input_data['body']['name'].upper()"}}
  ]
}

2. AI Content Generator

Generate text with LLM → delay → send via API.

{
  "name": "Content Generator",
  "start_node": "llm1",
  "nodes": [
    {"id": "llm1", "type": "llm", "config": {"prompt": "Write a blog post about {topic}"}},
    {"id": "delay", "type": "delay", "config": {"seconds": 1}},
    {"id": "post", "type": "http_request", "config": {"url": "https://api.example.com/posts", "method": "POST"}}
  ]
}

🧑‍💻 Development
Run in Dev Mode
pip install -r requirements.txt
uvicorn app.main:app --reload

Add a Custom Node
from .base import BaseNode
class MyCustomNode(BaseNode):
    async def execute(self, input_data, context):
        return {"result": "Hello from custom node"}


Register it in nodes/registry.py:

from .my_custom_node import MyCustomNode
NodeRegistry.register("my_custom", MyCustomNode)

🧪 Testing
pytest -v --cov=app


Generates coverage reports in htmlcov/.

🐳 Docker Deployment
docker build -t mini-n8n:latest ./backend
docker run -d -p 8000:8000 mini-n8n:latest


Or with Compose:

docker-compose up -d


Database (default SQLite):

Local: ./mini_n8n.db

Docker: ./backend/data/mini_n8n.db

🔐 Security Best Practices

Never commit API keys

Use environment variables in production

Limit Python code node usage (exec risks)

Enable CORS only where required

Add rate limiting for production workloads

🤝 Contributing

Fork the repo

Create your branch: git checkout -b feature/amazing-feature

Commit changes: git commit -m 'Add amazing feature'

Push and open a PR

📝 License

Licensed under the MIT License.

Acknowledgments

Inspired by n8n.io

Built with FastAPI

LLM integrations powered by OpenAI, Google Gemini, and others