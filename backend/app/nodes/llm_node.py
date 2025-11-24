"""
LLM Node - Interacts with Large Language Models (LLMs)

Purpose:
---------
This node acts as the "AI Brain" of the workflow, similar to n8n’s
AI / LLM nodes. It allows the workflow to dynamically generate text,
summaries, or insights using providers like OpenAI or Vertex AI.

Features:
---------
--> Config validation (Pydantic)
--> Dynamic prompt templating
--> Model & provider auto-selection
--> Context-aware system messages
--> Structured logging
--> Error handling and fallback support
--> Token usage tracking (if available)
"""

import logging
from typing import Dict, Any, Optional
from .base import BaseNode, NodeExecutionContext
from ..config import settings
from app.schemas.node import LLMNodeConfig

logger = logging.getLogger(__name__)


class LLMNode(BaseNode):
    """
    Node for interacting with Large Language Models.

    Supports providers defined in config (OpenAI, Vertex AI, or others added later).
    """

    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        """
        Initialize the LLM node.

        Args:
            node_id (str): Unique identifier for the node.
            name (str): Human-friendly name.
            config (dict): Node configuration (prompt, temperature, etc.)

        This also validates the configuration using LLMNodeConfig
        to ensure consistency and prevent runtime errors.
        """
        super().__init__(node_id, name, config)
        LLMNodeConfig(**config)  # Validate schema immediately

    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Executes an LLM request to generate a text-based response.

        Args:
            input_data (dict): Data from previous node outputs (used for variable substitution).
            context (NodeExecutionContext): Shared workflow execution context.

        Config Parameters:
            - prompt (str): Prompt text with placeholders (e.g., "Summarize {text}").
            - model (str): Model name (optional, falls back to settings.default_model).
            - temperature (float): Controls creativity (0.0 = factual, 1.0 = creative).
            - max_tokens (int): Maximum tokens for generation.
            - system_message (str): System-level instruction (optional).

        Returns:
            dict: Merged input data + LLM response and metadata.
        """
        # Extract LLM config
        prompt_template = self.config.get("prompt")
        model = self.config.get("model") or settings.openai_model or settings.vertexai_model
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 1000)
        system_message = self.config.get("system_message", "You are a helpful assistant.")

        if not prompt_template:
            raise ValueError("'prompt' parameter is required for LLM node")

        # Build the final prompt by replacing variables like {name}, {data.key}, etc.
        prompt = self._replace_variables(prompt_template, input_data)

        logger.info(
            f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
            f"Executing LLM request using provider: {settings.llm_provider}, model: {model}"
        )

        # Import LLM provider dynamically (OpenAI / Vertex)
        from ..llm.provider import get_llm_provider
        provider = get_llm_provider()

        try:
            # Send the prompt to the chosen provider
            response = await provider.generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                system_message=system_message
            )

            # Capture optional metadata like token usage (if provider supports it)
            metadata = {}
            if isinstance(response, dict) and "usage" in response:
                metadata["token_usage"] = response["usage"]

            logger.info(
                f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
                "LLM generation completed successfully."
            )

            # Return structured response data to the workflow engine
            return {
                **input_data,
                "llm_prompt": prompt,
                "llm_response": response.get("content") if isinstance(response, dict) else response,
                "llm_model": model,
                "llm_provider": settings.llm_provider,
                "metadata": metadata
            }

        except Exception as e:
            logger.error(
                f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
                f"LLM generation failed: {e}"
            )
            # Continue workflow safely even if the LLM fails
            return {
                **input_data,
                "llm_error": str(e),
                "llm_response": None,
                "llm_model": model,
                "llm_provider": settings.llm_provider,
                "status": "failed"
            }

    def _replace_variables(self, text: str, data: Dict[str, Any]) -> str:
        """
        Replace {variable} placeholders in a string prompt with actual values.

        Example:
            prompt = "Summarize the text: {article}"
            input_data = {"article": "AI is transforming industries"}
            → "Summarize the text: AI is transforming industries"

        Supports nested access like {user.name} if input_data is nested.
        """
        if not isinstance(text, str):
            return text

        result = text

        # Replace simple keys first
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))

        # Support nested placeholders like {user.name}
        import re

        def _nested_replace(match):
            path = match.group(1)
            value = self._get_nested_field(data, path)
            return str(value) if value is not None else f"{{{path}}}"

        result = re.sub(r"\{([\w\.]+)\}", _nested_replace, result)
        return result

    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Optional[Any]:
        """
        Retrieve nested field values from input data using dot notation.

        Example:
            field_path = "user.profile.email"
            input_data = {"user": {"profile": {"email": "test@example.com"}}}
            → returns "test@example.com"
        """
        keys = field_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
