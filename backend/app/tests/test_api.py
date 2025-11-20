"""
Tests for API endpoints
"""
import pytest
from httpx import AsyncClient
from ..main import app
from ..storage.db import init_db, async_session_maker
from ..schemas.node import NodeType


@pytest.fixture
async def test_client():
    """Create test client"""
    # Initialize test database
    await init_db()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_root_endpoint(test_client):
    """Test root endpoint"""
    response = await test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "mini_n8n"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint(test_client):
    """Test health check endpoint"""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_workflow(test_client):
    """Test workflow creation"""
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "start_node": "node1",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 1},
                "next_nodes": []
            }
        ]
    }
    
    response = await test_client.post("/api/v1/workflows/", json=workflow_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workflow"
    assert data["id"] is not None
    assert len(data["nodes"]) == 1


@pytest.mark.asyncio
async def test_list_workflows(test_client):
    """Test workflow listing"""
    # Create a workflow first
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "start_node": "node1",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 1},
                "next_nodes": []
            }
        ]
    }
    await test_client.post("/api/v1/workflows/", json=workflow_data)
    
    # List workflows
    response = await test_client.get("/api/v1/workflows/")
    assert response.status_code == 200
    data = response.json()
    assert "workflows" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_workflow(test_client):
    """Test getting a single workflow"""
    # Create workflow
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "start_node": "node1",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 1},
                "next_nodes": []
            }
        ]
    }
    create_response = await test_client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]
    
    # Get workflow
    response = await test_client.get(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workflow_id
    assert data["name"] == "Test Workflow"


@pytest.mark.asyncio
async def test_update_workflow(test_client):
    """Test workflow update"""
    # Create workflow
    workflow_data = {
        "name": "Test Workflow",
        "description": "Original description",
        "start_node": "node1",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 1},
                "next_nodes": []
            }
        ]
    }
    create_response = await test_client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]
    
    # Update workflow
    update_data = {
        "name": "Updated Workflow",
        "description": "Updated description"
    }
    response = await test_client.put(f"/api/v1/workflows/{workflow_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Workflow"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_workflow(test_client):
    """Test workflow deletion"""
    # Create workflow
    workflow_data = {
        "name": "Test Workflow",
        "description": "To be deleted",
        "start_node": "node1",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 1},
                "next_nodes": []
            }
        ]
    }
    create_response = await test_client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]
    
    # Delete workflow
    response = await test_client.delete(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = await test_client.get(f"/api/v1/workflows/{workflow_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_execute_workflow(test_client):
    """Test workflow execution"""
    # Create workflow
    workflow_data = {
        "name": "Execution Test",
        "description": "Test execution",
        "start_node": "node1",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 0.1},
                "next_nodes": []
            }
        ]
    }
    create_response = await test_client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]
    
    # Execute workflow
    execute_data = {
        "workflow_id": workflow_id,
        "input_data": {"test": "value"}
    }
    response = await test_client.post("/api/v1/workflows/execute", json=execute_data)
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == workflow_id
    assert data["status"] == "completed"
    assert data["execution_id"] is not None


@pytest.mark.asyncio
async def test_invalid_workflow_creation(test_client):
    """Test creating invalid workflow"""
    # Missing start node
    invalid_workflow = {
        "name": "Invalid Workflow",
        "description": "Missing start node",
        "start_node": "node_does_not_exist",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 1},
                "next_nodes": []
            }
        ]
    }
    
    response = await test_client.post("/api/v1/workflows/", json=invalid_workflow)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_workflow_not_found(test_client):
    """Test getting non-existent workflow"""
    response = await test_client.get("/api/v1/workflows/non-existent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_execute_inactive_workflow(test_client):
    """Test executing inactive workflow"""
    # Create workflow
    workflow_data = {
        "name": "Inactive Workflow",
        "description": "Test",
        "start_node": "node1",
        "nodes": [
            {
                "id": "node1",
                "name": "Delay Node",
                "type": "delay",
                "config": {"seconds": 0.1},
                "next_nodes": []
            }
        ]
    }
    create_response = await test_client.post("/api/v1/workflows/", json=workflow_data)
    workflow_id = create_response.json()["id"]
    
    # Deactivate workflow
    await test_client.put(f"/api/v1/workflows/{workflow_id}", json={"is_active": False})
    
    # Try to execute
    execute_data = {
        "workflow_id": workflow_id,
        "input_data": {}
    }
    response = await test_client.post("/api/v1/workflows/execute", json=execute_data)
    assert response.status_code == 400
    assert "not active" in response.json()["detail"]

