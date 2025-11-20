"""
Delay Node - Adds a delay in workflow execution
"""
import asyncio
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
import logging

logger = logging.getLogger(__name__)


class DelayNode(BaseNode):
    """Node for adding delays in workflow"""
    
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Execute delay
        
        Config parameters:
        - seconds: Number of seconds to delay (required)
        """
        seconds = self.config.get("seconds")
        
        if seconds is None:
            raise ValueError("'seconds' parameter is required for Delay node")
        
        try:
            seconds = float(seconds)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid 'seconds' value: {seconds}. Must be a number.")
        
        if seconds < 0:
            raise ValueError("'seconds' must be non-negative")
        
        logger.info(f"Delaying for {seconds} seconds")
        await asyncio.sleep(seconds)
        logger.info(f"Delay of {seconds} seconds completed")
        
        # Pass through input data with delay info
        return {
            **input_data,
            "_delay_info": {
                "delayed_seconds": seconds,
                "node_id": self.node_id
            }
        }

