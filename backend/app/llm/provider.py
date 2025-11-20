"""
LLM Provider abstraction supporting OpenAI and Vertex AI
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, default_model: str):
        self.default_model = default_model
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_message: Optional[str] = None
    ) -> str:
        """Generate text completion"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self):
        super().__init__(default_model=settings.openai_model)
        
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
        
        # Import here to avoid import errors if not installed
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            raise
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_message: Optional[str] = None
    ) -> str:
        """Generate text using OpenAI"""
        model = model or self.default_model
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        logger.info(f"Calling OpenAI API with model: {model}")
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info("OpenAI API call successful")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class VertexAIProvider(BaseLLMProvider):
    """Google Vertex AI LLM provider"""
    
    def __init__(self):
        super().__init__(default_model=settings.vertexai_model)
        
        if not settings.vertexai_project_id:
            logger.warning("Vertex AI project ID not configured")
        
        # Import here to avoid import errors if not installed
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            vertexai.init(
                project=settings.vertexai_project_id,
                location=settings.vertexai_location
            )
            self.GenerativeModel = GenerativeModel
            
        except ImportError:
            logger.error("google-cloud-aiplatform package not installed. Run: pip install google-cloud-aiplatform")
            raise
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_message: Optional[str] = None
    ) -> str:
        """Generate text using Vertex AI"""
        model_name = model or self.default_model
        
        logger.info(f"Calling Vertex AI with model: {model_name}")
        
        try:
            model_instance = self.GenerativeModel(model_name)
            
            # Combine system message with prompt if provided
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            # Configure generation
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            response = await model_instance.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            
            content = response.text
            logger.info("Vertex AI API call successful")
            return content
            
        except Exception as e:
            logger.error(f"Vertex AI error: {e}")
            raise RuntimeError(f"Vertex AI error: {str(e)}")


def get_llm_provider() -> BaseLLMProvider:
    """Get configured LLM provider"""
    provider = settings.llm_provider.lower()
    
    if provider == "openai":
        return OpenAIProvider()
    elif provider == "vertexai":
        return VertexAIProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Use 'openai' or 'vertexai'")

