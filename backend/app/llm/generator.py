"""
AI-powered workflow generator
"""
from typing import Dict, Any, List
from ..schemas.workflow import WorkflowCreate
from ..schemas.node import NodeSchema, NodeType
from .provider import get_llm_provider
import json
import logging

logger = logging.getLogger(__name__)


class WorkflowGenerator:
    """Generates workflows from natural language descriptions using LLM"""
    
    def __init__(self):
        self.provider = get_llm_provider()
    
    async def generate_workflow(
        self,
        description: str,
        context: Dict[str, Any] = None
    ) -> WorkflowCreate:
        """
        Generate a workflow from natural language description
        
        Args:
            description: Natural language description of the workflow
            context: Additional context for generation
            
        Returns:
            WorkflowCreate schema with generated workflow
        """
        logger.info(f"Generating workflow from description: {description}")
        
        # Build prompt for workflow generation
        prompt = self._build_generation_prompt(description, context)
        
        # Generate workflow using LLM
        response = await self.provider.generate(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=2000,
            system_message=self._get_system_message()
        )
        
        # Parse response
        workflow = self._parse_workflow_response(response, description)
        
        logger.info(f"Generated workflow: {workflow.name} with {len(workflow.nodes)} nodes")
        return workflow
    
    def _get_system_message(self) -> str:
        """Get system message for workflow generation"""
        return """You are a workflow automation expert. Your task is to generate workflow definitions in JSON format.

Available node types:
1. http_request - Makes HTTP requests (GET, POST, etc.)
2. delay - Adds delays in workflow execution
3. condition - Conditional branching based on data
4. python_code - Executes custom Python code
5. llm - Interacts with language models

Generate workflows that are practical, efficient, and follow best practices.
Always return valid JSON in the specified format."""
    
    def _build_generation_prompt(self, description: str, context: Dict[str, Any] = None) -> str:
        """Build prompt for workflow generation"""
        prompt = f"""Generate a workflow automation for the following requirement:

Description: {description}
"""
        
        if context:
            prompt += f"\nAdditional Context: {json.dumps(context, indent=2)}\n"
        
        prompt += """

Please generate a complete workflow definition with the following JSON structure:

{
  "name": "Workflow Name",
  "description": "Workflow description",
  "start_node": "node1",
  "nodes": [
    {
      "id": "node1",
      "name": "Node Name",
      "type": "http_request|delay|condition|python_code|llm",
      "config": {
        // Node-specific configuration
      },
      "next_nodes": ["node2"],
      "on_error": null
    }
  ]
}

Node configuration examples:

HTTP Request:
{
  "url": "https://api.example.com/data",
  "method": "GET",
  "headers": {"Authorization": "Bearer {token}"},
  "timeout": 30
}

Delay:
{
  "seconds": 5
}

Condition:
{
  "field": "status_code",
  "operator": "==",
  "value": 200,
  "true_branch": "node2",
  "false_branch": "node3"
}

Python Code:
{
  "code": "output['result'] = input_data.get('value', 0) * 2",
  "timeout": 30
}

LLM:
{
  "prompt": "Analyze this data: {data}",
  "temperature": 0.7,
  "max_tokens": 500
}

Return ONLY the JSON workflow definition, no additional text."""
        
        return prompt
    
    def _parse_workflow_response(self, response: str, original_description: str) -> WorkflowCreate:
        """Parse LLM response into WorkflowCreate schema"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            
            if response.endswith("```"):
                response = response[:-3]
            
            response = response.strip()
            
            # Parse JSON
            workflow_data = json.loads(response)
            
            # Validate and create workflow
            nodes = []
            for node_data in workflow_data.get("nodes", []):
                nodes.append(NodeSchema(
                    id=node_data["id"],
                    name=node_data["name"],
                    type=NodeType(node_data["type"]),
                    config=node_data.get("config", {}),
                    next_nodes=node_data.get("next_nodes", []),
                    on_error=node_data.get("on_error")
                ))
            
            workflow = WorkflowCreate(
                name=workflow_data.get("name", "Generated Workflow"),
                description=workflow_data.get("description", original_description),
                nodes=nodes,
                start_node=workflow_data["start_node"]
            )
            
            return workflow
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse workflow JSON: {e}")
            raise ValueError(f"Invalid workflow JSON generated: {str(e)}")
        except KeyError as e:
            logger.error(f"Missing required field in workflow: {e}")
            raise ValueError(f"Missing required field in workflow: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing workflow: {e}")
            raise ValueError(f"Error parsing workflow: {str(e)}")

