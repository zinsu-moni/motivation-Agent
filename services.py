"""
Motivation Service - Generates motivational content using OpenRouter AI
"""
import re
import logging
from typing import Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class MotivationService:
    """Service for generating motivational content via OpenRouter API."""
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "gpt-3.5-turbo",
    ):
        """
        Initialize MotivationService.
        
        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter base URL
            model: Model to use (default: gpt-3.5-turbo)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        logger.info(f"✅ MotivationService initialized with model: {model}")
    
    async def generate_motivation(self, user_input: str) -> str:
        """
        Generate a motivational response to user input.
        
        Args:
            user_input: The user's message or request
            
        Returns:
            Motivational response (cleaned of preambles, 1-3 sentences)
        """
        try:
            logger.info(f"🤖 Calling OpenRouter for motivation...")
            
            # Create system prompt for a compassionate motivational coach
            system_prompt = (
                "You are a compassionate and energetic motivational coach. "
                "Your role is to provide encouragement and motivation without asking clarifying questions. "
                "Respond with genuine, heartfelt motivation in 1-3 sentences. "
                "Be direct and avoid lengthy preambles or explanations."
            )
            
            # Call OpenRouter via OpenAI client
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            
            # Extract response
            motivation = response.choices[0].message.content.strip()
            logger.info(f"📝 Raw response: {motivation[:100]}...")
            
            # Clean the response
            cleaned = self._clean_motivation(motivation)
            logger.info(f"✨ Cleaned response: {cleaned}")
            
            return cleaned
        
        except Exception as e:
            logger.error(f"❌ Error generating motivation: {e}", exc_info=True)
            # Return a default motivational message if API fails
            return "You've got this! Keep pushing forward and believe in yourself. 💪"
    
    def _clean_motivation(self, text: str) -> str:
        """
        Clean motivation text by removing preambles and limiting to 1-3 sentences.
        
        Removes common AI preambles like:
        - "You're seeking..."
        - "Here's some motivation..."
        - "I'd like to..."
        
        Args:
            text: Raw text from model
            
        Returns:
            Cleaned motivation text
        """
        # Remove common preambles
        preambles = [
            r"^(?:You're seeking|You seem to be|I sense that|Here's|I'd like to|Let me|The fact that|It sounds like|I understand|You mention|Based on what you've shared).*?[:.]?\s*",
            r"^Here'?s (?:my|some) motivation[:.]?\s*",
            r"^I want to|^Let me|^I'd|^Alright[,!]\s*",
        ]
        
        for preamble_pattern in preambles:
            text = re.sub(preamble_pattern, "", text, flags=re.IGNORECASE)
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        # Keep 1-3 sentences, remove empty ones
        sentences = [s.strip() for s in sentences if s.strip()]
        sentences = sentences[:3]
        
        # Join and ensure ends with proper punctuation
        result = " ".join(sentences)
        if result and result[-1] not in ".!?":
            result += "."
        
        return result
