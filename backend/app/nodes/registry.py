"""
Node Registry - Factory for creating nodes
"""
from typing import Dict, Any, Type
from .base import BaseNode
from .http_node import HTTPNode
from .delay_node import DelayNode
from .condition_node import ConditionNode
from .python_node import PythonNode
from .llm_node import LLMNode
from ..schemas.node import NodeType
import logging

logger = logging.getLogger(__name__)


class NodeRegistry:
    """Registry for node types"""
    
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
        Create a node instance
        
        Args:
            node_id: Unique node identifier
            name: Node name
            node_type: Type of node
            config: Node configuration
            
        Returns:
            BaseNode instance
            
        Raises:
            ValueError: If node type is not registered
        """
        node_class = cls._registry.get(node_type)
        
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")
        
        logger.debug(f"Creating node: {node_id} of type {node_type}")
        return node_class(node_id, name, config)
    
    @classmethod
    def register_node(cls, node_type: str, node_class: Type[BaseNode]):
        """Register a custom node type"""
        cls._registry[node_type] = node_class
        logger.info(f"Registered custom node type: {node_type}")
    
    @classmethod
    def get_registered_types(cls) -> list:
        """Get list of registered node types"""
        return list(cls._registry.keys())


# Convenience function
def create_node(node_id: str, name: str, node_type: str, config: Dict[str, Any]) -> BaseNode:
    """Create a node using the registry"""
    return NodeRegistry.create_node(node_id, name, node_type, config)

