"""
Delay Node - Adds a configurable delay in workflow execution
Supports:
- Static and dynamic delays (from previous node outputs)
- Validation via Pydantic schema
- Structured logging
- Graceful cancellation handling
"""

import asyncio
import logging
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
from app.schemas.node import DelayNodeConfig

logger = logging.getLogger(__name__)


class DelayNode(BaseNode):
    """Node that introduces an async delay within a workflow"""

    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        """
        Validate configuration on initialization.
        Ensures 'seconds' is provided and valid.
        """
        super().__init__(node_id, name, config)
        DelayNodeConfig(**config)  # Validate schema early

    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Executes a delay step within the workflow.

        Config parameters:
            - seconds: Number of seconds to delay (can be numeric or templated)
        
        Returns:
            The same input_data with added _delay_info metadata.
        """
        raw_value = self.config.get("seconds")

        # Support dynamic value references like "{{delay_time}}"
        if isinstance(raw_value, str) and raw_value.startswith("{{") and raw_value.endswith("}}"):
            variable_name = raw_value.strip("{} ")
            seconds = float(input_data.get(variable_name, 0))
            logger.info(f"[Node: {self.node_id}] Using dynamic delay from input: {seconds}s")
        else:
            try:
                seconds = float(raw_value)
            except (TypeError, ValueError):
                raise ValueError(f"Invalid 'seconds' value: {raw_value}. Must be a numeric value or variable reference.")

        if seconds < 0:
            raise ValueError("'seconds' must be non-negative")

        logger.info(
            f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
            f"Delaying execution for {seconds} seconds"
        )

        start_time = asyncio.get_event_loop().time()

        # Use wait_for to handle cancellation or workflow timeout gracefully
        try:
            await asyncio.wait_for(asyncio.sleep(seconds), timeout=seconds + 5)
        except asyncio.CancelledError:
            logger.warning(f"[Node: {self.node_id}] Delay node was cancelled before completion.")
            raise
        except asyncio.TimeoutError:
            logger.error(f"[Node: {self.node_id}] Delay exceeded maximum safe timeout.")
            raise

        actual_duration = round(asyncio.get_event_loop().time() - start_time, 3)

        logger.info(
            f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
            f"Completed delay of {actual_duration} seconds"
        )

        # Return updated workflow data with delay info
        return {
            **input_data,
            "_delay_info": {
                "requested_seconds": seconds,
                "actual_waited_seconds": actual_duration,
                "node_id": self.node_id,
                "status": "completed"
            }
        }
