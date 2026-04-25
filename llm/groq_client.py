"""Groq LLM client configuration."""

import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.language_models import BaseChatModel
from dotenv import load_dotenv

from utils.helpers import setup_logging

load_dotenv()
logger = setup_logging()


class GroqClient:
    """Wrapper for Groq LLM client with anti-hallucination settings."""
    
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    DEFAULT_TEMPERATURE = 0.2  # Low temperature to reduce hallucination
    
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        api_key: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.model = model
        self.temperature = temperature
        self._llm: Optional[BaseChatModel] = None
        
        logger.info(f"Initializing Groq client with model: {model}, temperature: {temperature}")
    
    @property
    def llm(self) -> BaseChatModel:
        """Lazy initialization of the LLM."""
        if self._llm is None:
            self._llm = ChatGroq(
                groq_api_key=self.api_key,
                model_name=self.model,
                temperature=self.temperature,
                max_tokens=4096,
            )
        return self._llm
    
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt."""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error invoking Groq LLM: {e}")
            raise


def get_groq_llm(
    model: str = GroqClient.DEFAULT_MODEL,
    temperature: float = GroqClient.DEFAULT_TEMPERATURE
) -> BaseChatModel:
    """Factory function to get a configured Groq LLM instance."""
    client = GroqClient(model=model, temperature=temperature)
    return client.llm
