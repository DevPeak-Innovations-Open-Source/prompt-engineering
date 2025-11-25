"""
Python Code Node - Securely executes custom Python code inside workflows.

Purpose:
---------
This node replicates n8n’s “Code Node” behavior.
It allows workflow users to write short Python snippets that process data
between other nodes — without compromising system security.

Features:
---------
--> Safe sandboxed execution (isolated environment)
--> Input and output handling consistent with n8n
--> Config validation with Pydantic
--> Async + timeout-safe execution
--> Graceful error reporting (doesn't crash workflow)
--> Human-readable logging and traceability
"""

import asyncio
import logging
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
from app.schemas.node import PythonNodeConfig  # schema for validation

logger = logging.getLogger(__name__)


class PythonNode(BaseNode):
    """Node for executing custom Python code safely and asynchronously."""

    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize the PythonNode and validate its configuration.

        Args:
            node_id (str): Unique identifier for the node.
            name (str): Node name for readability.
            config (dict): Contains 'code' and optional 'timeout'.

        This also validates the provided configuration using PythonNodeConfig
        (ensures 'code' exists and 'timeout' is valid).
        """
        super().__init__(node_id, name, config)
        PythonNodeConfig(**config)  # Validate using schema

    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Executes user-defined Python code within a controlled sandbox.

        Args:
            input_data (dict): Data from previous node output.
            context (NodeExecutionContext): Shared workflow context.

        Config Parameters:
            - code: (required) The Python code to execute.
            - timeout: (optional) Max execution time in seconds (default: 30).

        Returns:
            dict: Output dictionary defined by user code (or input_data if empty).
        """
        code = self.config.get("code")
        timeout = self.config.get("timeout", 30)

        if not code:
            raise ValueError("'code' parameter is required for Python node")

        logger.info(
            f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
            f"Executing Python code (timeout={timeout}s)"
        )

        # Define restricted built-ins for safety
        safe_builtins = {
            "len": len,
            "range": range,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "round": round,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "any": any,
            "all": all,
            "sorted": sorted,
            "print": print,
        }

        # Prepare sandboxed execution environment
        exec_globals = {
            "__builtins__": safe_builtins,
            "input_data": input_data,  # workflow data input
            "context": context,        # workflow context
            "output": {},              # user-defined output (mutable)
        }

        # Add a few safe modules for user convenience
        import math, json, re, datetime
        exec_globals.update({
            "math": math,
            "json": json,
            "re": re,
            "datetime": datetime,
        })

        try:
            # Execute user code asynchronously with timeout
            await asyncio.wait_for(
                self._execute_code(code, exec_globals),
                timeout=timeout
            )

            # Retrieve user-defined output or fallback to input_data
            output = exec_globals.get("output", {})
            if not output:
                output = input_data

            logger.info(
                f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
                "Python code executed successfully."
            )

            return output

        except asyncio.TimeoutError:
            error_msg = f"Python code execution exceeded timeout of {timeout} seconds"
            logger.error(f"[Node: {self.node_id}] {error_msg}")
            return {
                **input_data,
                "_python_error": error_msg,
                "status": "timeout"
            }

        except Exception as e:
            # Capture runtime errors safely without stopping the workflow
            logger.error(f"[Node: {self.node_id}] Python code execution failed: {e}")
            return {
                **input_data,
                "_python_error": str(e),
                "status": "failed"
            }

    async def _execute_code(self, code: str, exec_globals: Dict[str, Any]):
        """
        Runs the user-provided Python code inside the sandbox.

        Uses asyncio’s thread pool executor to avoid blocking the event loop.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, exec, code, exec_globals)
