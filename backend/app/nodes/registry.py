"""
Node Registry - Central factory and registry for workflow nodes.
Handles dynamic creation, registration, and validation of node classes.
"""

from typing import Dict, Any, Type, List
from .base import BaseNode
from .http_node import HTTPNode
from .delay_node import DelayNode
from .condition_node import ConditionNode
from .python_node import PythonNode
from .llm_node import LLMNode
from ..schemas.node import NodeType
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)


class NodeRegistry:
    """
    Registry and factory for workflow nodes.

    This class maps node types (like "http_request", "delay", etc.)
    to their corresponding implementation classes. It allows the
    workflow engine to dynamically instantiate nodes by type.
    """

    # Central registry mapping node type → node class
    _registry: Dict[str, Type[BaseNode]] = {
        NodeType.HTTP_REQUEST: HTTPNode,
        NodeType.DELAY: DelayNode,
        NodeType.CONDITION: ConditionNode,
        NodeType.PYTHON_CODE: PythonNode,
        NodeType.LLM: LLMNode,
    }

    @classmethod
    def create_node(cls, node_id: str, name: str, node_type: str, config: Dict[str, Any]) -> BaseNode:
        """
        Create and return a node instance based on the provided node type.

        Args:
            node_id (str): Unique identifier for the node.
            name (str): Human-readable name of the node.
            node_type (str): Type of the node (must exist in registry).
            config (Dict[str, Any]): Configuration dictionary for the node.

        Returns:
            BaseNode: Instantiated node object ready for execution.

        Raises:
            ValueError: If node type is invalid or not registered.
        """
        # Validate node_type
        if node_type not in cls._registry:
            valid_types = list(cls._registry.keys())
            logger.error(f"❌ Unknown node type '{node_type}'. Available types: {valid_types}")
            raise ValueError(
                f"Unknown node type '{node_type}'. Must be one of: {', '.join(valid_types)}"
            )

        node_class = cls._registry[node_type]
        logger.info(f"🧩 Creating node '{name}' (ID: {node_id}, Type: {node_type}) using {node_class.__name__}")
        return node_class(node_id=node_id, name=name, config=config)

    @classmethod
    def register_node(cls, node_type: str, node_class: Type[BaseNode]):
        """
        Register a new custom node type dynamically.

        Args:
            node_type (str): Unique string key representing the node type.
            node_class (Type[BaseNode]): Class implementing the node.

        Notes:
            - If the node_type already exists, a warning is logged and overwritten.
            - Helps developers add new custom nodes at runtime.
        """
        if not issubclass(node_class, BaseNode):
            logger.error(f"❌ Cannot register '{node_class.__name__}': must inherit from BaseNode")
            raise TypeError(f"Node class '{node_class.__name__}' must inherit from BaseNode")

        if node_type in cls._registry:
            logger.warning(f"⚠️ Node type '{node_type}' is already registered. Overwriting with {node_class.__name__}.")

        cls._registry[node_type] = node_class
        logger.info(f"✅ Successfully registered node type '{node_type}' → {node_class.__name__}")

    @classmethod
    def get_registered_types(cls) -> List[str]:
        """
        Return a list of currently registered node types.

        Returns:
            List[str]: Node type keys available for use.
        """
        return list(cls._registry.keys())

    @classmethod
    def has_node_type(cls, node_type: str) -> bool:
        """
        Check if a node type is currently registered.

        Args:
            node_type (str): Node type name to verify.

        Returns:
            bool: True if the node type exists in registry, else False.
        """
        return node_type in cls._registry


# Convenience factory function (used by orchestrator or tests)
def create_node(node_id: str, name: str, node_type: str, config: Dict[str, Any]) -> BaseNode:
    """
    Shortcut function to create a node instance using the NodeRegistry.

    Args:
        node_id (str): Unique node identifier.
        name (str): Node name.
        node_type (str): Type of node to create.
        config (Dict[str, Any]): Configuration for the node.

    Returns:
        BaseNode: Instantiated and ready-to-use node object.
    """
    return NodeRegistry.create_node(node_id, name, node_type, config)
