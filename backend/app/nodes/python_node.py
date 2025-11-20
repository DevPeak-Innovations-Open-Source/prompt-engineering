"""
Python Code Node - Executes custom Python code
"""
import asyncio
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
import logging

logger = logging.getLogger(__name__)


class PythonNode(BaseNode):
    """Node for executing custom Python code"""
    
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Execute Python code
        
        Config parameters:
        - code: Python code to execute (required)
        - timeout: Execution timeout in seconds (default: 30)
        
        The code has access to:
        - input_data: The input data dictionary
        - context: The execution context
        - output: Dictionary to store results (initially empty)
        """
        code = self.config.get("code")
        timeout = self.config.get("timeout", 30)
        
        if not code:
            raise ValueError("'code' parameter is required for Python node")
        
        logger.info(f"Executing Python code (timeout: {timeout}s)")
        
        # Prepare execution namespace
        exec_globals = {
            "input_data": input_data,
            "context": context,
            "output": {},
            "__builtins__": __builtins__,
        }
        
        # Add safe imports
        exec_globals.update({
            "json": __import__("json"),
            "math": __import__("math"),
            "datetime": __import__("datetime"),
            "re": __import__("re"),
        })
        
        try:
            # Execute code with timeout
            await asyncio.wait_for(
                self._execute_code(code, exec_globals),
                timeout=timeout
            )
            
            # Get output from execution
            output = exec_globals.get("output", {})
            
            # If output is empty, return input_data
            if not output:
                output = input_data
            
            logger.info("Python code executed successfully")
            return output
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Python code execution exceeded timeout of {timeout} seconds")
        except Exception as e:
            logger.error(f"Python code execution failed: {e}")
            raise RuntimeError(f"Python code execution error: {str(e)}")
    
    async def _execute_code(self, code: str, exec_globals: Dict[str, Any]):
        """Execute code in a separate thread to avoid blocking"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, exec, code, exec_globals)

