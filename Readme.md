# Mini N8N - AI-Powered Workflow Automation System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Mini N8N** is a lightweight, AI-powered workflow automation system inspired by n8n.io. It allows you to build, execute, and manage complex workflows using a variety of nodes including HTTP requests, delays, conditions, Python code execution, and LLM interactions.

## 🌟 Features

- **Modular Node System**: Extensible architecture with multiple node types
  - HTTP Request Node: Make API calls with full HTTP method support
  - Delay Node: Add timed delays in workflows
  - Condition Node: Conditional branching with multiple operators
  - Python Code Node: Execute custom Python code
  - LLM Node: Integrate with OpenAI or Vertex AI
  
- **Asynchronous Execution**: Built on FastAPI with full async/await support
- **Workflow Orchestration**: Sophisticated engine for managing workflow execution
- **AI Workflow Generation**: Generate workflows from natural language descriptions
- **Persistent Storage**: SQLite database with async support
- **RESTful API**: Complete API for workflow management and execution
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Comprehensive Testing**: Full test coverage for nodes, orchestrator, and API

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Node Types](#node-types)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Examples](#examples)
- [Development](#development)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip
- Docker and Docker Compose (optional, for containerized deployment)

### Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd mini_n8n
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## ⚡ Quick Start

### Using Docker Compose (Recommended)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Create Your First Workflow

```python
import requests

# Define a simple workflow
workflow = {
    "name": "Hello Workflow",
    "description": "A simple workflow that delays and returns data",
    "start_node": "delay1",
    "nodes": [
        {
            "id": "delay1",
            "name": "Wait 2 seconds",
            "type": "delay",
            "config": {"seconds": 2},
            "next_nodes": ["python1"]
        },
        {
            "id": "python1",
            "name": "Process Data",
            "type": "python_code",
            "config": {
                "code": "output['message'] = 'Hello, ' + input_data.get('name', 'World')"
            },
            "next_nodes": []
        }
    ]
}

# Create workflow
response = requests.post("http://localhost:8000/api/v1/workflows/", json=workflow)
workflow_id = response.json()["id"]

# Execute workflow
execution = requests.post("http://localhost:8000/api/v1/workflows/execute", json={
    "workflow_id": workflow_id,
    "input_data": {"name": "John"}
})

print(execution.json())
```

## 📁 Project Structure

```
mini_n8n/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration management
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes_workflow.py  # Workflow API routes
│   │   ├── schemas/
│   │   │   ├── node.py          # Node schemas
│   │   │   └── workflow.py      # Workflow schemas
│   │   ├── nodes/
│   │   │   ├── base.py          # Base node class
│   │   │   ├── http_node.py     # HTTP request node
│   │   │   ├── delay_node.py    # Delay node
│   │   │   ├── condition_node.py # Condition node
│   │   │   ├── python_node.py   # Python code node
│   │   │   ├── llm_node.py      # LLM node
│   │   │   └── registry.py      # Node registry
│   │   ├── orchestrator/
│   │   │   ├── engine.py        # Workflow engine
│   │   │   ├── executor.py      # Node executor
│   │   │   └── state.py         # Execution state
│   │   ├── llm/
│   │   │   ├── provider.py      # LLM providers
│   │   │   └── generator.py     # Workflow generator
│   │   ├── storage/
│   │   │   ├── db.py            # Database connection
│   │   │   ├── crud_workflow.py # Workflow CRUD
│   │   │   └── crud_logs.py     # Logs CRUD
│   │   ├── models/
│   │   │   ├── workflow_model.py # Workflow DB model
│   │   │   └── log_model.py     # Log DB model
│   │   └── tests/
│   │       ├── test_nodes.py
│   │       ├── test_orchestrator.py
│   │       └── test_api.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Node Types

### HTTP Request Node
Makes HTTP requests to external APIs.

```json
{
  "type": "http_request",
  "config": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "headers": {"Authorization": "Bearer {token}"},
    "body": {"key": "value"},
    "timeout": 30
  }
}
```

### Delay Node
Adds a delay in workflow execution.

```json
{
  "type": "delay",
  "config": {
    "seconds": 5.0
  }
}
```

### Condition Node
Conditional branching based on data evaluation.

```json
{
  "type": "condition",
  "config": {
    "field": "status_code",
    "operator": "==",
    "value": 200,
    "true_branch": "success_node",
    "false_branch": "error_node"
  }
}
```

**Supported operators**: `==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `in`

### Python Code Node
Executes custom Python code.

```json
{
  "type": "python_code",
  "config": {
    "code": "output['result'] = input_data['x'] * 2",
    "timeout": 30
  }
}
```

### LLM Node
Interacts with Large Language Models (OpenAI or Vertex AI).

```json
{
  "type": "llm",
  "config": {
    "prompt": "Summarize this: {text}",
    "temperature": 0.7,
    "max_tokens": 500,
    "system_message": "You are a helpful assistant"
  }
}
```

## 🌐 API Endpoints

### Workflows

- **POST** `/api/v1/workflows/` - Create a new workflow
- **GET** `/api/v1/workflows/` - List all workflows
- **GET** `/api/v1/workflows/{workflow_id}` - Get a specific workflow
- **PUT** `/api/v1/workflows/{workflow_id}` - Update a workflow
- **DELETE** `/api/v1/workflows/{workflow_id}` - Delete a workflow

### Execution

- **POST** `/api/v1/workflows/execute` - Execute a workflow
- **GET** `/api/v1/workflows/{workflow_id}/executions` - List workflow executions
- **GET** `/api/v1/workflows/executions/{execution_id}` - Get execution details

### AI Generation

- **POST** `/api/v1/workflows/generate` - Generate workflow from description

### System

- **GET** `/` - API information
- **GET** `/health` - Health check

Full API documentation available at `http://localhost:8000/docs` (Swagger UI)

## ⚙️ Configuration

Configuration is managed through environment variables or `.env` file:

```bash
# Application
APP_NAME=mini_n8n
DEBUG=false

# Database
DATABASE_URL=sqlite+aiosqlite:///./mini_n8n.db

# LLM Provider
LLM_PROVIDER=openai  # or vertexai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4

# Workflow
MAX_WORKFLOW_EXECUTION_TIME=3600
MAX_NODE_RETRIES=3
```

## 💡 Examples

### Example 1: API Data Processor

```json
{
  "name": "API Data Processor",
  "start_node": "fetch",
  "nodes": [
    {
      "id": "fetch",
      "name": "Fetch User Data",
      "type": "http_request",
      "config": {
        "url": "https://api.example.com/users/{user_id}",
        "method": "GET"
      },
      "next_nodes": ["check"]
    },
    {
      "id": "check",
      "name": "Check Status",
      "type": "condition",
      "config": {
        "field": "status_code",
        "operator": "==",
        "value": 200,
        "true_branch": "process",
        "false_branch": "error"
      },
      "next_nodes": []
    },
    {
      "id": "process",
      "name": "Process Data",
      "type": "python_code",
      "config": {
        "code": "output['user_name'] = input_data['body']['name'].upper()"
      },
      "next_nodes": []
    }
  ]
}
```

### Example 2: AI-Powered Content Generator

```json
{
  "name": "Content Generator",
  "start_node": "generate",
  "nodes": [
    {
      "id": "generate",
      "name": "Generate Content",
      "type": "llm",
      "config": {
        "prompt": "Write a blog post about: {topic}",
        "temperature": 0.7,
        "max_tokens": 1000
      },
      "next_nodes": ["delay"]
    },
    {
      "id": "delay",
      "name": "Wait",
      "type": "delay",
      "config": {"seconds": 1},
      "next_nodes": ["post"]
    },
    {
      "id": "post",
      "name": "Post to API",
      "type": "http_request",
      "config": {
        "url": "https://api.example.com/posts",
        "method": "POST",
        "body": {"content": "{llm_response}"}
      },
      "next_nodes": []
    }
  ]
}
```

### Example 3: AI Workflow Generation

```python
import requests

# Generate a workflow using AI
response = requests.post("http://localhost:8000/api/v1/workflows/generate", json={
    "description": "Create a workflow that fetches weather data from an API, checks if temperature is above 25, and sends a notification",
    "context": {"api": "https://api.weather.com"}
})

workflow = response.json()
print(f"Generated workflow: {workflow['name']}")
print(f"Nodes: {len(workflow['nodes'])}")
```

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Adding Custom Nodes

1. Create a new node class in `app/nodes/`:

```python
from .base import BaseNode, NodeExecutionContext
from typing import Dict, Any

class CustomNode(BaseNode):
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        # Your custom logic here
        return {"result": "custom output"}
```

2. Register the node in `app/nodes/registry.py`:

```python
from .custom_node import CustomNode

NodeRegistry._registry["custom_type"] = CustomNode
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_nodes.py

# Run with verbose output
pytest -v
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t mini-n8n:latest ./backend

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -v $(pwd)/data:/app/data \
  --name mini-n8n \
  mini-n8n:latest
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f mini-n8n-backend

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## 📊 Monitoring and Logs

### Health Check

```bash
curl http://localhost:8000/health
```

### View Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker container
docker logs -f mini-n8n
```

### Database

The SQLite database is stored at:
- Local: `./mini_n8n.db`
- Docker: `./backend/data/mini_n8n.db`

## 🔐 Security Considerations

- **API Keys**: Never commit API keys to version control
- **Production**: Use environment variables for sensitive configuration
- **CORS**: Configure CORS appropriately for production
- **Code Execution**: Python code node executes arbitrary code - use with caution
- **Rate Limiting**: Implement rate limiting for production deployments

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Inspired by [n8n.io](https://n8n.io)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- LLM integration via OpenAI and Google Vertex AI

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation at `/docs` endpoint

---

**Made with ❤️ for workflow automation enthusiasts**

