"""
LLM Node - Interacts with Large Language Models
"""
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class LLMNode(BaseNode):
    """Node for LLM interactions"""
    
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Execute LLM request
        
        Config parameters:
        - prompt: Prompt template (can use {variables} from input)
        - model: Model to use (optional, uses config default)
        - temperature: Temperature for generation (default: 0.7)
        - max_tokens: Maximum tokens to generate (default: 1000)
        - system_message: System message for the LLM (optional)
        """
        prompt_template = self.config.get("prompt")
        model = self.config.get("model")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 1000)
        system_message = self.config.get("system_message")
        
        if not prompt_template:
            raise ValueError("'prompt' parameter is required for LLM node")
        
        # Replace variables in prompt
        prompt = self._replace_variables(prompt_template, input_data)
        
        logger.info(f"Executing LLM request with provider: {settings.llm_provider}")
        
        # Get LLM provider
        from ..llm.provider import get_llm_provider
        provider = get_llm_provider()
        
        # Generate response
        response = await provider.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_message=system_message
        )
        
        logger.info("LLM request completed successfully")
        
        return {
            **input_data,
            "llm_response": response,
            "llm_prompt": prompt,
            "llm_model": model or provider.default_model,
        }
    
    def _replace_variables(self, text: str, data: Dict[str, Any]) -> str:
        """Replace {variable} placeholders in text"""
        if not isinstance(text, str):
            return text
        
        result = text
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result

