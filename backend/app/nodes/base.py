"""
Base node class for all workflow nodes in mini_n8n
Handles:
- Execution lifecycle (timing, retries, errors)
- Shared context management
- Configuration validation
- Structured logging for better observability
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from app.schemas.node import (
    HTTPNodeConfig, DelayNodeConfig, ConditionNodeConfig,
    PythonNodeConfig, LLMNodeConfig, NodeType
)

logger = logging.getLogger(__name__)


class NodeExecutionContext:
    """
    Context object shared across node executions.
    Holds workflow-level metadata and state.
    """

    def __init__(self, workflow_id: str, execution_id: str, global_state: Dict[str, Any]):
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.global_state = global_state  # Shared data across all nodes
        self.node_outputs: Dict[str, Any] = {}  # Stores outputs of previously executed nodes


class BaseNode(ABC):
    """
    Abstract base class for all workflow nodes.
    Every node (HTTP, Delay, Python, etc.) inherits from this class.
    """

    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.name = name
        self.config = config
        self.next_nodes: List[str] = []
        self.on_error: Optional[str] = None

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Core logic for each node.
        Must be implemented in child classes (e.g., DelayNode, LLMNode).
        """
        pass

    async def run(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Executes a node safely with:
        - Validation
        - Retries
        - Timing
        - Error handling
        - Structured logging
        """
        start_time = time.time()

        # Default execution result structure
        result = {
            "node_id": self.node_id,
            "node_name": self.name,
            "status": "success",
            "output": None,
            "error": None,
            "execution_time": 0,
            "next_nodes": self.next_nodes
        }

        # Optional retry support
        retries = int(self.config.get("retries", 0))
        retry_delay = float(self.config.get("retry_delay", 1))
        attempt = 0

        while attempt <= retries:
            try:
                logger.info(
                    f"[Workflow: {context.workflow_id} | Exec: {context.execution_id}] "
                    f"Running node {self.name} ({self.node_id}) - Attempt {attempt + 1}"
                )

                # Validate configuration before running
                self.validate_config()

                # Add async timeout control for long tasks
                timeout = float(self.config.get("timeout", 60))
                output = await asyncio.wait_for(self.execute(input_data, context), timeout=timeout)

                result["output"] = output
                result["status"] = "success"
                logger.info(f"Node {self.node_id} completed successfully")
                break

            except asyncio.TimeoutError:
                attempt += 1
                result["status"] = "error"
                result["error"] = f"Node timed out after {timeout}s"
                logger.warning(f"Timeout: {self.name} ({self.node_id})")

            except Exception as e:
                attempt += 1
                result["status"] = "error"
                result["error"] = str(e)
                logger.error(f"Error in node {self.node_id}: {e}")

                if attempt <= retries:
                    logger.info(f"Retrying node {self.node_id} after {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    continue

            # If max retries exceeded, set error handler
            if self.on_error:
                result["next_nodes"] = [self.on_error]
            else:
                result["next_nodes"] = []
            break

        result["execution_time"] = round(time.time() - start_time, 3)
        return result

    def set_next_nodes(self, next_nodes: List[str]):
        """Attach the IDs of the nodes to execute next."""
        self.next_nodes = next_nodes

    def set_error_handler(self, error_node_id: Optional[str]):
        """Assign a fallback node to execute if this node fails."""
        self.on_error = error_node_id

    def validate_config(self) -> bool:
        """
        Validate node configuration using Pydantic schemas.
        Raises ValueError if configuration is invalid.
        """
        schema_map = {
            NodeType.HTTP_REQUEST: HTTPNodeConfig,
            NodeType.DELAY: DelayNodeConfig,
            NodeType.CONDITION: ConditionNodeConfig,
            NodeType.PYTHON_CODE: PythonNodeConfig,
            NodeType.LLM: LLMNodeConfig
        }

        node_type = self.config.get("type")
        schema_class = schema_map.get(node_type)

        if not schema_class:
            raise ValueError(f"Unknown or missing node type: {node_type}")

        # Validate by initializing schema; Pydantic auto-raises errors if invalid
        schema_class(**self.config)
        return True

    def __str__(self):
        """Readable string representation for debugging."""
        return f"{self.__class__.__name__}(id={self.node_id}, name={self.name})"
