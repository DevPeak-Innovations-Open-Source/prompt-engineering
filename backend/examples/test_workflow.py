#!/usr/bin/env python3
"""
Example script to create and execute a workflow
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def create_simple_workflow():
    """Create a simple test workflow"""
    workflow = {
        "name": "Test Workflow",
        "description": "A test workflow with delay and Python nodes",
        "start_node": "delay1",
        "nodes": [
            {
                "id": "delay1",
                "name": "Wait 1 second",
                "type": "delay",
                "config": {"seconds": 1},
                "next_nodes": ["python1"]
            },
            {
                "id": "python1",
                "name": "Process Data",
                "type": "python_code",
                "config": {
                    "code": "output['message'] = 'Hello, ' + input_data.get('name', 'World')\noutput['timestamp'] = str(input_data.get('timestamp', 'N/A'))"
                },
                "next_nodes": []
            }
        ]
    }
    
    print("📝 Creating workflow...")
    response = requests.post(f"{BASE_URL}/api/v1/workflows/", json=workflow)
    response.raise_for_status()
    
    workflow_data = response.json()
    print(f"✅ Workflow created with ID: {workflow_data['id']}")
    return workflow_data['id']


def execute_workflow(workflow_id, input_data):
    """Execute a workflow with input data"""
    print(f"\n🚀 Executing workflow {workflow_id}...")
    
    execute_request = {
        "workflow_id": workflow_id,
        "input_data": input_data
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/workflows/execute", json=execute_request)
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Execution completed with status: {result['status']}")
    print(f"📊 Output: {json.dumps(result['output'], indent=2)}")
    return result


def list_workflows():
    """List all workflows"""
    print("\n📋 Listing workflows...")
    response = requests.get(f"{BASE_URL}/api/v1/workflows/")
    response.raise_for_status()
    
    data = response.json()
    print(f"Found {data['total']} workflows:")
    for workflow in data['workflows']:
        print(f"  - {workflow['name']} (ID: {workflow['id']})")


def main():
    """Main function"""
    print("=" * 60)
    print("Mini N8N - Workflow Test Script")
    print("=" * 60)
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("✅ API is running\n")
        
        # Create a workflow
        workflow_id = create_simple_workflow()
        
        # Execute the workflow
        input_data = {
            "name": "Alice",
            "timestamp": time.time()
        }
        execute_workflow(workflow_id, input_data)
        
        # List all workflows
        list_workflows()
        
        print("\n✅ Test completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        print("Start the server with: uvicorn app.main:app --reload")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

