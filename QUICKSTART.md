# Quick Start Guide

Get mini_n8n up and running in 5 minutes!

## Option 1: Docker (Recommended)

```bash
# 1. Set your OpenAI API key (if using LLM features)
export OPENAI_API_KEY=your-api-key-here

# 2. Start the service
docker-compose up -d

# 3. Check the logs
docker-compose logs -f

# 4. Access the API
open http://localhost:8000/docs
```

## Option 2: Local Development

```bash
# 1. Navigate to backend directory
cd backend

# 2. Run the quick start script
chmod +x run.sh
./run.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test Your Installation

```bash
# Check API health
curl http://localhost:8000/health

# Or run the test script
cd backend/examples
python test_workflow.py
```

## Create Your First Workflow

### Using the API

```bash
curl -X POST http://localhost:8000/api/v1/workflows/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Workflow",
    "start_node": "delay1",
    "nodes": [{
      "id": "delay1",
      "name": "Wait 2 seconds",
      "type": "delay",
      "config": {"seconds": 2},
      "next_nodes": []
    }]
  }'
```

### Using Python

```python
import requests

workflow = {
    "name": "Hello World",
    "start_node": "python1",
    "nodes": [{
        "id": "python1",
        "name": "Say Hello",
        "type": "python_code",
        "config": {
            "code": "output['message'] = 'Hello, World!'"
        },
        "next_nodes": []
    }]
}

response = requests.post(
    "http://localhost:8000/api/v1/workflows/",
    json=workflow
)
workflow_id = response.json()["id"]

# Execute the workflow
execution = requests.post(
    "http://localhost:8000/api/v1/workflows/execute",
    json={"workflow_id": workflow_id, "input_data": {}}
)
print(execution.json())
```

## Generate Workflow with AI

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/workflows/generate",
    json={
        "description": "Create a workflow that fetches weather data and sends an alert if temperature is above 30 degrees"
    }
)

workflow = response.json()
print(f"Generated workflow: {workflow['name']}")
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Check Examples**: Look at `backend/examples/sample_workflows.json` for more workflow examples
3. **Read the Docs**: See `README.md` for detailed documentation
4. **Run Tests**: Execute `pytest` in the backend directory

## Troubleshooting

### Port Already in Use
```bash
# Change the port in docker-compose.yml or use:
docker-compose down
```

### Database Issues
```bash
# Reset the database
rm backend/data/mini_n8n.db
docker-compose restart
```

### LLM Not Working
- Verify your API key is set: `echo $OPENAI_API_KEY`
- Check the logs: `docker-compose logs -f`

## Get Help

- API Documentation: http://localhost:8000/docs
- GitHub Issues: Create an issue for bugs or questions
- Sample Workflows: Check `backend/examples/`

Happy automating! 🚀

