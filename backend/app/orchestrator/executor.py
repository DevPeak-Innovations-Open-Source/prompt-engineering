"""
Node executor - Handles individual node execution
"""
from typing import Dict, Any
from ..nodes.base import BaseNode, NodeExecutionContext
from .state import WorkflowExecutionState
import logging

logger = logging.getLogger(__name__)


class NodeExecutor:
    """Executes individual nodes"""
    
    def __init__(self, state: WorkflowExecutionState):
        self.state = state
    
    async def execute_node(self, node: BaseNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single node
        
        Args:
            node: Node to execute
            input_data: Input data for the node
            
        Returns:
            Execution result dictionary
        """
        # Create execution context
        context = NodeExecutionContext(
            workflow_id=self.state.workflow_id,
            execution_id=self.state.execution_id,
            global_state=self.state.global_state
        )
        
        # Add outputs from all previous nodes to context
        for result in self.state.node_results:
            node_id = result.get("node_id")
            if node_id:
                context.node_outputs[node_id] = result.get("output")
        
        # Execute the node
        logger.info(f"Executing node: {node.node_id} ({node.name})")
        result = await node.run(input_data, context)
        
        # Store result in state
        self.state.add_node_result(result)
        
        logger.info(f"Node {node.node_id} execution completed with status: {result['status']}")
        
        return result

