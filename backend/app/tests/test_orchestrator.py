"""
Tests for workflow orchestrator
"""
import pytest
from ..orchestrator.state import WorkflowExecutionState, ExecutionStatus
from ..orchestrator.engine import WorkflowEngine
from ..schemas.workflow import WorkflowResponse
from ..schemas.node import NodeSchema, NodeType
from datetime import datetime


def test_workflow_execution_state():
    """Test workflow execution state management"""
    state = WorkflowExecutionState("workflow1", input_data={"test": "data"})
    
    assert state.workflow_id == "workflow1"
    assert state.status == ExecutionStatus.PENDING
    assert state.input_data == {"test": "data"}
    assert len(state.node_results) == 0
    
    # Test start
    state.start()
    assert state.status == ExecutionStatus.RUNNING
    assert state.start_time is not None
    
    # Test add node result
    result = {
        "node_id": "node1",
        "status": "success",
        "output": {"result": "value"}
    }
    state.add_node_result(result)
    assert len(state.node_results) == 1
    assert "node1" in state.executed_nodes
    
    # Test pending nodes
    state.add_pending_nodes(["node2", "node3"])
    assert state.has_pending_nodes()
    assert state.get_next_node() == "node2"
    assert state.get_next_node() == "node3"
    assert not state.has_pending_nodes()
    
    # Test complete
    state.complete({"final": "output"})
    assert state.status == ExecutionStatus.COMPLETED
    assert state.end_time is not None
    assert state.output_data == {"final": "output"}
    
    # Test to_dict
    state_dict = state.to_dict()
    assert state_dict["workflow_id"] == "workflow1"
    assert state_dict["status"] == "completed"


def test_workflow_execution_state_fail():
    """Test workflow execution state failure"""
    state = WorkflowExecutionState("workflow1")
    state.start()
    
    state.fail("Test error")
    
    assert state.status == ExecutionStatus.FAILED
    assert state.error == "Test error"
    assert state.end_time is not None


@pytest.mark.asyncio
async def test_workflow_engine_simple():
    """Test simple workflow execution"""
    # Create a simple workflow with delay nodes
    nodes = [
        NodeSchema(
            id="node1",
            name="Delay 1",
            type=NodeType.DELAY,
            config={"seconds": 0.01},
            next_nodes=["node2"]
        ),
        NodeSchema(
            id="node2",
            name="Delay 2",
            type=NodeType.DELAY,
            config={"seconds": 0.01},
            next_nodes=[]
        )
    ]
    
    workflow = WorkflowResponse(
        id="test-workflow",
        name="Test Workflow",
        description="Test",
        nodes=nodes,
        start_node="node1",
        trigger_config=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    engine = WorkflowEngine()
    state = await engine.execute_workflow(workflow, {"initial": "data"})
    
    assert state.status == ExecutionStatus.COMPLETED
    assert len(state.node_results) == 2
    assert state.node_results[0]["node_id"] == "node1"
    assert state.node_results[1]["node_id"] == "node2"


@pytest.mark.asyncio
async def test_workflow_engine_condition():
    """Test workflow with conditional branching"""
    nodes = [
        NodeSchema(
            id="condition",
            name="Check Value",
            type=NodeType.CONDITION,
            config={
                "field": "value",
                "operator": ">",
                "value": 50,
                "true_branch": "high",
                "false_branch": "low"
            },
            next_nodes=[]  # Will be set by condition
        ),
        NodeSchema(
            id="high",
            name="High Value",
            type=NodeType.DELAY,
            config={"seconds": 0.01},
            next_nodes=[]
        ),
        NodeSchema(
            id="low",
            name="Low Value",
            type=NodeType.DELAY,
            config={"seconds": 0.01},
            next_nodes=[]
        )
    ]
    
    workflow = WorkflowResponse(
        id="test-workflow",
        name="Conditional Workflow",
        description="Test",
        nodes=nodes,
        start_node="condition",
        trigger_config=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    engine = WorkflowEngine()
    
    # Test with high value
    state_high = await engine.execute_workflow(workflow, {"value": 75})
    assert state_high.status == ExecutionStatus.COMPLETED
    assert state_high.node_results[1]["node_id"] == "high"
    
    # Test with low value
    state_low = await engine.execute_workflow(workflow, {"value": 25})
    assert state_low.status == ExecutionStatus.COMPLETED
    assert state_low.node_results[1]["node_id"] == "low"


@pytest.mark.asyncio
async def test_workflow_engine_python():
    """Test workflow with Python code node"""
    nodes = [
        NodeSchema(
            id="python",
            name="Calculate",
            type=NodeType.PYTHON_CODE,
            config={
                "code": "output['result'] = input_data['x'] * input_data['y']",
                "timeout": 5
            },
            next_nodes=[]
        )
    ]
    
    workflow = WorkflowResponse(
        id="test-workflow",
        name="Python Workflow",
        description="Test",
        nodes=nodes,
        start_node="python",
        trigger_config=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    engine = WorkflowEngine()
    state = await engine.execute_workflow(workflow, {"x": 5, "y": 10})
    
    assert state.status == ExecutionStatus.COMPLETED
    assert state.output_data["result"] == 50


def test_workflow_validation():
    """Test workflow validation"""
    engine = WorkflowEngine()
    
    # Valid workflow
    valid_workflow = WorkflowResponse(
        id="test",
        name="Valid",
        description="Test",
        nodes=[
            NodeSchema(
                id="node1",
                name="Node 1",
                type=NodeType.DELAY,
                config={"seconds": 1},
                next_nodes=[]
            )
        ],
        start_node="node1",
        trigger_config=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    is_valid, error = engine.validate_workflow(valid_workflow)
    assert is_valid is True
    assert error is None
    
    # Invalid: start node doesn't exist
    invalid_workflow = WorkflowResponse(
        id="test",
        name="Invalid",
        description="Test",
        nodes=[
            NodeSchema(
                id="node1",
                name="Node 1",
                type=NodeType.DELAY,
                config={"seconds": 1},
                next_nodes=[]
            )
        ],
        start_node="node2",  # Doesn't exist
        trigger_config=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    is_valid, error = engine.validate_workflow(invalid_workflow)
    assert is_valid is False
    assert "not found" in error
    
    # Invalid: next_node doesn't exist
    invalid_workflow2 = WorkflowResponse(
        id="test",
        name="Invalid",
        description="Test",
        nodes=[
            NodeSchema(
                id="node1",
                name="Node 1",
                type=NodeType.DELAY,
                config={"seconds": 1},
                next_nodes=["node2"]  # Doesn't exist
            )
        ],
        start_node="node1",
        trigger_config=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    is_valid, error = engine.validate_workflow(invalid_workflow2)
    assert is_valid is False
    assert "non-existent" in error

