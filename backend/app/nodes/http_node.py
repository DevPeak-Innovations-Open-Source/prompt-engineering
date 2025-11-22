"""
HTTP Request Node - Handles making HTTP requests within the workflow.

Purpose:
---------
This node lets a workflow send API requests (GET, POST, PUT, DELETE, etc.)
and process the responses. It can dynamically substitute variables from
previous node outputs into URLs, headers, and bodies.

Features:
---------
✅ Schema validation for config correctness
✅ Support for dynamic variable placeholders (e.g. {user_id})
✅ Safe async HTTP calls using httpx
✅ Graceful JSON parsing fallback
✅ Structured logging for observability
"""

import httpx
import logging
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
from app.schemas.node import HTTPNodeConfig  # For config validation

# Initialize logger for this node
logger = logging.getLogger(__name__)


class HTTPNode(BaseNode):
    """
    Node for making HTTP requests during workflow execution.

    This node acts like a “connector” node in n8n — allowing the workflow
    to fetch, send, or manipulate external data via REST APIs.
    """

    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize the HTTP node with validation.

        Args:
            node_id (str): Unique identifier of the node.
            name (str): Human-friendly name.
            config (Dict[str, Any]): Node configuration (URL, method, headers, etc.)

        Steps:
            - Calls BaseNode constructor
            - Validates provided configuration using Pydantic schema
        """
        super().__init__(node_id, name, config)
        HTTPNodeConfig(**config)  # Validate schema immediately

    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Executes an HTTP request and returns the response data.

        Args:
            input_data (dict): Data from previous node outputs.
            context (NodeExecutionContext): Shared workflow context.

        Config Parameters:
            - url (str): Target API endpoint.
            - method (str): HTTP method (GET, POST, etc.)
            - headers (dict): Custom headers (supports placeholders).
            - body (dict): Request body for POST/PUT/PATCH.
            - timeout (int): Timeout in seconds (default: 30).

        Returns:
            dict: HTTP response including status, headers, and body.
        """

        # Extract configuration values
        url = self.config.get("url")
        method = self.config.get("method", "GET").upper()
        headers = self.config.get("headers", {})
        body = self.config.get("body")
        timeout = self.config.get("timeout", 30)

        # Validate required parameters
        if not url:
            raise ValueError("URL is required for HTTP node")

        # Replace placeholders with values from input_data
        url = self._replace_variables(url, input_data)
        headers = {k: self._replace_variables(v, input_data) for k, v in headers.items()}

        if body:
            body = self._replace_variables_in_dict(body, input_data)

        # Log request details for debugging
        logger.info(
            f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
            f"Making {method} request to {url}"
        )

        # Perform HTTP request using async httpx client
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # Match HTTP method to proper request
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=body)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=body)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                elif method == "PATCH":
                    response = await client.patch(url, headers=headers, json=body)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            except httpx.RequestError as e:
                # Handle network errors (DNS fail, refused connection, etc.)
                logger.error(f"[Node: {self.node_id}] HTTP request failed: {e}")
                raise

        # Attempt to parse JSON, fallback to plain text
        try:
            response_data = response.json()
        except Exception:
            response_data = response.text

        # Log response summary
        logger.info(
            f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
            f"Response status: {response.status_code}"
        )

        # Return response details for next nodes
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response_data,
            "url": url,
            "method": method
        }

    def _replace_variables(self, text: str, data: Dict[str, Any]) -> str:
        """
        Replaces {variable} placeholders in strings with actual values.

        Example:
            text = "https://api.example.com/users/{user_id}"
            data = {"user_id": 42}
            → "https://api.example.com/users/42"
        """
        if not isinstance(text, str):
            return text

        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(value))

        return text

    def _replace_variables_in_dict(self, obj: Any, data: Dict[str, Any]) -> Any:
        """
        Recursively replaces variables in nested dictionaries or lists.

        Example:
            body = {"user": {"id": "{user_id}", "name": "{user_name}"}}
            data = {"user_id": 1, "user_name": "Dhruv"}
            → {"user": {"id": "1", "name": "Dhruv"}}
        """
        if isinstance(obj, dict):
            return {k: self._replace_variables_in_dict(v, data) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_variables_in_dict(item, data) for item in obj]
        elif isinstance(obj, str):
            return self._replace_variables(obj, data)
        else:
            return obj
