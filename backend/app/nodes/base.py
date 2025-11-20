"""
Base node class for all workflow nodes
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import logging

logger = logging.getLogger(__name__)


class NodeExecutionContext:
    """Context passed to nodes during execution"""
    
    def __init__(self, workflow_id: str, execution_id: str, global_state: Dict[str, Any]):
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.global_state = global_state  # Shared state across workflow execution
        self.node_outputs: Dict[str, Any] = {}  # Outputs from previous nodes


class BaseNode(ABC):
    """Base class for all workflow nodes"""
    
    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.name = name
        self.config = config
        self.next_nodes: List[str] = []
        self.on_error: Optional[str] = None
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Execute the node logic
        
        Args:
            input_data: Input data for this node
            context: Execution context
            
        Returns:
            Output data from node execution
        """
        pass
    
    async def run(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Run the node with timing and error handling
        
        Returns:
            Dictionary with execution result including status, output, error, execution_time
        """
        start_time = time.time()
        result = {
            "node_id": self.node_id,
            "node_name": self.name,
            "status": "success",
            "output": None,
            "error": None,
            "execution_time": 0,
            "next_nodes": self.next_nodes
        }
        
        try:
            logger.info(f"Executing node: {self.node_id} ({self.name})")
            output = await self.execute(input_data, context)
            result["output"] = output
            result["status"] = "success"
            logger.info(f"Node {self.node_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Node {self.node_id} failed: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
            
            # If error handler is defined, update next nodes to error handler
            if self.on_error:
                result["next_nodes"] = [self.on_error]
            else:
                result["next_nodes"] = []
                
        finally:
            result["execution_time"] = time.time() - start_time
            
        return result
    
    def set_next_nodes(self, next_nodes: List[str]):
        """Set the next nodes to execute"""
        self.next_nodes = next_nodes
        
    def set_error_handler(self, error_node_id: Optional[str]):
        """Set error handler node"""
        self.on_error = error_node_id
        
    def validate_config(self) -> bool:
        """Validate node configuration"""
        return True
    
    def __str__(self):
        return f"{self.__class__.__name__}(id={self.node_id}, name={self.name})"

