"""
Tests for node implementations
"""
import pytest
from ..nodes.base import NodeExecutionContext
from ..nodes.http_node import HTTPNode
from ..nodes.delay_node import DelayNode
from ..nodes.condition_node import ConditionNode
from ..nodes.python_node import PythonNode
from ..nodes.registry import NodeRegistry
import time


@pytest.fixture
def execution_context():
    """Create a test execution context"""
    return NodeExecutionContext(
        workflow_id="test-workflow",
        execution_id="test-execution",
        global_state={}
    )


@pytest.mark.asyncio
async def test_delay_node(execution_context):
    """Test delay node"""
    config = {"seconds": 0.1}
    node = DelayNode("delay1", "Test Delay", config)
    
    start_time = time.time()
    result = await node.run({"test": "data"}, execution_context)
    elapsed_time = time.time() - start_time
    
    assert result["status"] == "success"
    assert elapsed_time >= 0.1
    assert result["output"]["test"] == "data"
    assert "_delay_info" in result["output"]


@pytest.mark.asyncio
async def test_condition_node_true(execution_context):
    """Test condition node with true condition"""
    config = {
        "field": "status",
        "operator": "==",
        "value": "active",
        "true_branch": "node2",
        "false_branch": "node3"
    }
    node = ConditionNode("condition1", "Test Condition", config)
    
    input_data = {"status": "active"}
    result = await node.run(input_data, execution_context)
    
    assert result["status"] == "success"
    assert result["output"]["_condition_result"]["result"] is True
    assert result["next_nodes"] == ["node2"]


@pytest.mark.asyncio
async def test_condition_node_false(execution_context):
    """Test condition node with false condition"""
    config = {
        "field": "status",
        "operator": "==",
        "value": "active",
        "true_branch": "node2",
        "false_branch": "node3"
    }
    node = ConditionNode("condition1", "Test Condition", config)
    
    input_data = {"status": "inactive"}
    result = await node.run(input_data, execution_context)
    
    assert result["status"] == "success"
    assert result["output"]["_condition_result"]["result"] is False
    assert result["next_nodes"] == ["node3"]


@pytest.mark.asyncio
async def test_condition_node_operators(execution_context):
    """Test different condition operators"""
    test_cases = [
        ({"value": 10}, ">", 5, True),
        ({"value": 10}, "<", 20, True),
        ({"value": 10}, ">=", 10, True),
        ({"value": 10}, "<=", 10, True),
        ({"value": 10}, "!=", 5, True),
        ({"value": "hello"}, "contains", "ell", True),
    ]
    
    for input_data, operator, compare_value, expected in test_cases:
        config = {
            "field": "value",
            "operator": operator,
            "value": compare_value,
            "true_branch": "true_node",
            "false_branch": "false_node"
        }
        node = ConditionNode("condition1", "Test Condition", config)
        result = await node.run(input_data, execution_context)
        
        assert result["output"]["_condition_result"]["result"] == expected


@pytest.mark.asyncio
async def test_python_node(execution_context):
    """Test Python code node"""
    code = """
result = input_data.get('x', 0) + input_data.get('y', 0)
output['sum'] = result
output['message'] = 'Calculation complete'
"""
    config = {"code": code, "timeout": 5}
    node = PythonNode("python1", "Test Python", config)
    
    input_data = {"x": 5, "y": 10}
    result = await node.run(input_data, execution_context)
    
    assert result["status"] == "success"
    assert result["output"]["sum"] == 15
    assert result["output"]["message"] == "Calculation complete"


@pytest.mark.asyncio
async def test_python_node_error(execution_context):
    """Test Python node with error"""
    code = "raise ValueError('Test error')"
    config = {"code": code, "timeout": 5}
    node = PythonNode("python1", "Test Python", config)
    
    result = await node.run({}, execution_context)
    
    assert result["status"] == "error"
    assert "Test error" in result["error"]


@pytest.mark.asyncio
async def test_http_node_mock(execution_context, httpx_mock):
    """Test HTTP node with mocked response"""
    httpx_mock.add_response(
        url="https://api.example.com/test",
        json={"message": "success", "data": [1, 2, 3]}
    )
    
    config = {
        "url": "https://api.example.com/test",
        "method": "GET",
        "headers": {},
        "timeout": 30
    }
    node = HTTPNode("http1", "Test HTTP", config)
    
    result = await node.run({}, execution_context)
    
    assert result["status"] == "success"
    assert result["output"]["status_code"] == 200
    assert result["output"]["body"]["message"] == "success"


@pytest.mark.asyncio
async def test_http_node_variable_replacement(execution_context, httpx_mock):
    """Test HTTP node with variable replacement"""
    httpx_mock.add_response(
        url="https://api.example.com/users/123",
        json={"id": 123, "name": "John"}
    )
    
    config = {
        "url": "https://api.example.com/users/{user_id}",
        "method": "GET",
        "headers": {"Authorization": "Bearer {token}"},
        "timeout": 30
    }
    node = HTTPNode("http1", "Test HTTP", config)
    
    input_data = {"user_id": "123", "token": "secret-token"}
    result = await node.run(input_data, execution_context)
    
    assert result["status"] == "success"
    assert result["output"]["url"] == "https://api.example.com/users/123"


def test_node_registry():
    """Test node registry"""
    registry = NodeRegistry()
    
    # Test HTTP node creation
    node = registry.create_node("test1", "Test", "http_request", {"url": "http://test.com"})
    assert isinstance(node, HTTPNode)
    assert node.node_id == "test1"
    
    # Test Delay node creation
    node = registry.create_node("test2", "Test", "delay", {"seconds": 5})
    assert isinstance(node, DelayNode)
    
    # Test unknown node type
    with pytest.raises(ValueError):
        registry.create_node("test3", "Test", "unknown_type", {})


def test_node_next_nodes():
    """Test node next_nodes management"""
    node = DelayNode("delay1", "Test", {"seconds": 1})
    
    assert node.next_nodes == []
    
    node.set_next_nodes(["node2", "node3"])
    assert node.next_nodes == ["node2", "node3"]
    
    node.set_error_handler("error_node")
    assert node.on_error == "error_node"

