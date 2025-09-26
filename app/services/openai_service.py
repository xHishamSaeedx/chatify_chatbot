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
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key":
            self.client = None
            self.model = "gpt-3.5-turbo"
            self.demo_mode = True
            print("⚠️  OpenAI API key not found. Running in demo mode with mock responses.")
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-3.5-turbo"
            self.demo_mode = False
    
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
            if not self.client or self.demo_mode:
                # Return demo response
                return self._get_demo_response(messages)
            
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
    
    def _get_demo_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate demo responses for testing without OpenAI API
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary containing the demo response
        """
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"].lower()
                break
        
        # Generate contextual demo responses
        demo_responses = {
            "hello": "Hello! I'm a demo AI assistant. How can I help you today?",
            "hi": "Hi there! I'm here to help. What would you like to know?",
            "how are you": "I'm doing great, thank you for asking! I'm a demo AI assistant ready to help you.",
            "what is": "That's an interesting question! In demo mode, I can provide general information. Could you be more specific?",
            "help": "I'm here to help! I can assist with general questions, provide information, or just have a friendly conversation.",
            "bye": "Goodbye! It was nice chatting with you. Feel free to come back anytime!",
            "thanks": "You're welcome! I'm happy to help. Is there anything else you'd like to know?",
            "name": "I'm a demo AI assistant created for testing the Chatify chatbot system. I don't have a specific name, but you can call me Assistant!",
            "weather": "I'm a demo AI, so I can't check real-time weather. But I can tell you that weather varies by location and season!",
            "time": "I'm a demo AI, so I don't have access to real-time information. But I can tell you that time is relative and always moving forward!",
            "date": "I'm a demo AI without real-time access, but I can tell you that dates help us organize our lives and mark important moments!",
            "joke": "Why don't scientists trust atoms? Because they make up everything! 😄",
            "story": "Once upon a time, there was a demo AI assistant who loved helping people. The end! (I'm keeping it short in demo mode)",
            "code": "I can help with coding concepts in demo mode! Programming is like building with digital LEGO blocks - you combine different pieces to create something amazing!",
            "love": "Love is a beautiful and complex emotion that connects us all. In demo mode, I can discuss the concept of love and relationships!",
            "food": "Food is wonderful! I can discuss cooking, nutrition, or just chat about your favorite meals. What's your favorite type of cuisine?",
            "music": "Music is the universal language! I can discuss different genres, instruments, or the emotional power of music. What kind of music do you enjoy?",
            "travel": "Travel opens our minds to new cultures and experiences! I can discuss destinations, travel tips, or the joy of exploration. Where would you like to go?",
            "work": "Work is an important part of life! I can discuss career advice, work-life balance, or help with professional development topics.",
            "study": "Learning is a lifelong journey! I can discuss study techniques, educational topics, or help with academic questions."
        }
        
        # Find the best matching response
        response = "I'm a demo AI assistant! I can help with general questions, have friendly conversations, or discuss various topics. What would you like to talk about?"
        
        for keyword, demo_response in demo_responses.items():
            if keyword in user_message:
                response = demo_response
                break
        
        # Add some variety to responses
        if "?" in user_message:
            response += " Feel free to ask me anything else!"
        elif len(user_message) < 5:
            response += " You can ask me about anything you're curious about!"
        
        return {
            "success": True,
            "content": response,
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "total_tokens": 80
            },
            "model": "demo-mode"
        }


# Create singleton instance
openai_service = OpenAIService()
