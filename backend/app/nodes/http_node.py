"""
HTTP Request Node - Makes HTTP requests
"""
import httpx
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
import logging

logger = logging.getLogger(__name__)


class HTTPNode(BaseNode):
    """Node for making HTTP requests"""
    
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Execute HTTP request
        
        Config parameters:
        - url: Request URL
        - method: HTTP method (GET, POST, PUT, DELETE, etc.)
        - headers: Request headers
        - body: Request body (for POST/PUT)
        - timeout: Request timeout in seconds
        """
        url = self.config.get("url")
        method = self.config.get("method", "GET").upper()
        headers = self.config.get("headers", {})
        body = self.config.get("body")
        timeout = self.config.get("timeout", 30)
        
        if not url:
            raise ValueError("URL is required for HTTP node")
        
        # Replace variables in URL, headers, and body with input data
        url = self._replace_variables(url, input_data)
        headers = {k: self._replace_variables(v, input_data) for k, v in headers.items()}
        
        if body:
            body = self._replace_variables_in_dict(body, input_data)
        
        logger.info(f"Making {method} request to {url}")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
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
        
        # Try to parse JSON response, fallback to text
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response_data,
            "url": url,
            "method": method
        }
    
    def _replace_variables(self, text: str, data: Dict[str, Any]) -> str:
        """Replace {variable} placeholders in text"""
        if not isinstance(text, str):
            return text
            
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(value))
        return text
    
    def _replace_variables_in_dict(self, obj: Any, data: Dict[str, Any]) -> Any:
        """Recursively replace variables in dictionaries"""
        if isinstance(obj, dict):
            return {k: self._replace_variables_in_dict(v, data) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_variables_in_dict(item, data) for item in obj]
        elif isinstance(obj, str):
            return self._replace_variables(obj, data)
        else:
            return obj

