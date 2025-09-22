"""
OpenAI service for ChatGPT integration
"""

from typing import Optional, List, Dict, Any
from openai import OpenAI
from app.core.config import settings


class OpenAIService:
    """OpenAI service for ChatGPT integration"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            self.client = None
            self.model = "gpt-3.5-turbo"
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-3.5-turbo"
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate chat completion using OpenAI API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: OpenAI model to use (defaults to gpt-3.5-turbo)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API call
            
        Returns:
            Dictionary containing the chat completion response
        """
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured. Please set OPENAI_API_KEY in your environment variables.",
                    "content": None
                }
            
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    async def simple_chat(self, user_message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Simple chat interface for basic conversations
        
        Args:
            user_message: The user's message
            system_prompt: Optional system prompt to set context
            
        Returns:
            Dictionary containing the chat response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat_completion(messages)
    
    async def conversational_chat(
        self,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat with conversation history context
        
        Args:
            conversation_history: Previous messages in the conversation
            user_message: The new user message
            system_prompt: Optional system prompt to set context
            
        Returns:
            Dictionary containing the chat response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat_completion(messages)


# Create singleton instance
openai_service = OpenAIService()
