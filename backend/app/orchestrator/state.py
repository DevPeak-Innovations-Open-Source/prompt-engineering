"""
Workflow execution state management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class ExecutionStatus(str, Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowExecutionState:
    """Manages the state of a workflow execution"""
    
    def __init__(self, workflow_id: str, execution_id: Optional[str] = None, input_data: Optional[Dict[str, Any]] = None):
        self.workflow_id = workflow_id
        self.execution_id = execution_id or str(uuid.uuid4())
        self.status = ExecutionStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.input_data = input_data or {}
        self.output_data: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        
        # Track node executions
        self.node_results: List[Dict[str, Any]] = []
        self.executed_nodes: set = set()
        self.pending_nodes: List[str] = []
        
        # Global state shared across nodes
        self.global_state: Dict[str, Any] = {
            "workflow_id": workflow_id,
            "execution_id": self.execution_id,
            "start_time": None
        }
    
    def start(self):
        """Mark execution as started"""
        self.status = ExecutionStatus.RUNNING
        self.start_time = datetime.utcnow()
        self.global_state["start_time"] = self.start_time
    
    def complete(self, output_data: Optional[Dict[str, Any]] = None):
        """Mark execution as completed"""
        self.status = ExecutionStatus.COMPLETED
        self.end_time = datetime.utcnow()
        self.output_data = output_data
    
    def fail(self, error: str):
        """Mark execution as failed"""
        self.status = ExecutionStatus.FAILED
        self.end_time = datetime.utcnow()
        self.error = error
    
    def cancel(self):
        """Mark execution as cancelled"""
        self.status = ExecutionStatus.CANCELLED
        self.end_time = datetime.utcnow()
    
    def add_node_result(self, result: Dict[str, Any]):
        """Add a node execution result"""
        self.node_results.append(result)
        node_id = result.get("node_id")
        if node_id:
            self.executed_nodes.add(node_id)
    
    def add_pending_nodes(self, node_ids: List[str]):
        """Add nodes to pending execution queue"""
        for node_id in node_ids:
            if node_id not in self.executed_nodes and node_id not in self.pending_nodes:
                self.pending_nodes.append(node_id)
    
    def get_next_node(self) -> Optional[str]:
        """Get next node to execute"""
        if self.pending_nodes:
            return self.pending_nodes.pop(0)
        return None
    
    def has_pending_nodes(self) -> bool:
        """Check if there are pending nodes"""
        return len(self.pending_nodes) > 0
    
    def get_node_output(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get output from a specific node"""
        for result in self.node_results:
            if result.get("node_id") == node_id:
                return result.get("output")
        return None
    
    def get_latest_output(self) -> Dict[str, Any]:
        """Get output from the last executed node"""
        if self.node_results:
            return self.node_results[-1].get("output", {})
        return self.input_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "node_results": self.node_results,
            "executed_nodes": list(self.executed_nodes),
            "pending_nodes": self.pending_nodes
        }

