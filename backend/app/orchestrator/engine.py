"""
Workflow orchestration engine
"""
from typing import Dict, Any, List, Optional
from ..nodes.base import BaseNode
from ..nodes.registry import NodeRegistry
from ..schemas.workflow import WorkflowResponse
from .state import WorkflowExecutionState, ExecutionStatus
from .executor import NodeExecutor
from ..config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Orchestrates workflow execution"""
    
    def __init__(self):
        self.node_registry = NodeRegistry()
    
    async def execute_workflow(
        self,
        workflow: WorkflowResponse,
        input_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecutionState:
        """
        Execute a complete workflow
        
        Args:
            workflow: Workflow definition
            input_data: Initial input data for the workflow
            
        Returns:
            WorkflowExecutionState with execution results
        """
        # Initialize execution state
        state = WorkflowExecutionState(
            workflow_id=workflow.id,
            input_data=input_data or {}
        )
        
        # Build node graph
        nodes_map = self._build_node_graph(workflow)
        
        # Start execution
        state.start()
        logger.info(f"Starting workflow execution: {workflow.id} (execution: {state.execution_id})")
        
        try:
            # Add start node to pending queue
            state.add_pending_nodes([workflow.start_node])
            
            # Create executor
            executor = NodeExecutor(state)
            
            # Track current input data
            current_input = input_data or {}
            
            # Execute with timeout
            await asyncio.wait_for(
                self._execute_nodes(state, nodes_map, executor, current_input),
                timeout=settings.max_workflow_execution_time
            )
            
            # Workflow completed successfully
            final_output = state.get_latest_output()
            state.complete(final_output)
            logger.info(f"Workflow {workflow.id} completed successfully")
            
        except asyncio.TimeoutError:
            error_msg = f"Workflow execution exceeded maximum time of {settings.max_workflow_execution_time} seconds"
            logger.error(error_msg)
            state.fail(error_msg)
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg)
            state.fail(error_msg)
        
        return state
    
    async def _execute_nodes(
        self,
        state: WorkflowExecutionState,
        nodes_map: Dict[str, BaseNode],
        executor: NodeExecutor,
        initial_input: Dict[str, Any]
    ):
        """Execute nodes in the workflow"""
        max_iterations = 1000  # Prevent infinite loops
        iterations = 0
        
        while state.has_pending_nodes() and iterations < max_iterations:
            iterations += 1
            
            # Get next node to execute
            node_id = state.get_next_node()
            if not node_id:
                break
            
            # Get node from map
            node = nodes_map.get(node_id)
            if not node:
                logger.warning(f"Node {node_id} not found in workflow")
                continue
            
            # Get input for this node (output from last node or initial input)
            node_input = state.get_latest_output() if state.node_results else initial_input
            
            # Execute node
            result = await executor.execute_node(node, node_input)
            
            # Handle execution result
            if result["status"] == "success":
                # Add next nodes to pending queue
                next_nodes = result.get("next_nodes", [])
                state.add_pending_nodes(next_nodes)
                
            elif result["status"] == "error":
                # If there's an error handler, add it to pending
                error_nodes = result.get("next_nodes", [])
                if error_nodes:
                    state.add_pending_nodes(error_nodes)
                else:
                    # No error handler, fail the workflow
                    raise RuntimeError(f"Node {node_id} failed: {result.get('error')}")
        
        if iterations >= max_iterations:
            raise RuntimeError("Workflow execution exceeded maximum iterations (possible infinite loop)")
    
    def _build_node_graph(self, workflow: WorkflowResponse) -> Dict[str, BaseNode]:
        """Build a map of nodes from workflow definition"""
        nodes_map = {}
        
        for node_schema in workflow.nodes:
            # Create node instance
            node = self.node_registry.create_node(
                node_id=node_schema.id,
                name=node_schema.name,
                node_type=node_schema.type,
                config=node_schema.config
            )
            
            # Set next nodes and error handler
            node.set_next_nodes(node_schema.next_nodes)
            node.set_error_handler(node_schema.on_error)
            
            nodes_map[node_schema.id] = node
        
        logger.info(f"Built node graph with {len(nodes_map)} nodes")
        return nodes_map
    
    def validate_workflow(self, workflow: WorkflowResponse) -> tuple[bool, Optional[str]]:
        """
        Validate workflow structure
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if start node exists
        node_ids = {node.id for node in workflow.nodes}
        
        if workflow.start_node not in node_ids:
            return False, f"Start node '{workflow.start_node}' not found in workflow"
        
        # Check if all referenced next_nodes exist
        for node in workflow.nodes:
            for next_node in node.next_nodes:
                if next_node not in node_ids:
                    return False, f"Node '{node.id}' references non-existent node '{next_node}'"
            
            if node.on_error and node.on_error not in node_ids:
                return False, f"Node '{node.id}' references non-existent error handler '{node.on_error}'"
        
        # Check for duplicate node IDs
        if len(node_ids) != len(workflow.nodes):
            return False, "Duplicate node IDs found in workflow"
        
        return True, None

