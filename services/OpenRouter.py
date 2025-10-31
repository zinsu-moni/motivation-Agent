import os
import openai
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: str = None):
        # allow passing api_key at runtime (e.g., from request header) or fall back to env var
        resolved_api_key = api_key or os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL')
        if resolved_api_key:
            openai.api_key = resolved_api_key

        # create async client (some environments may not need base_url)
        self.client = openai.AsyncOpenAI(
            api_key=resolved_api_key,
            base_url=base_url
        )
    
    async def generate_motivation(self, user_message: str, user_id: str = None, db: AsyncSession = None) -> str:
        try:
            user_context = ""
            if user_id and db:
                user_context = f"User ID: {user_id}. "
            
            system_prompt = """You are Motivo AI, a compassionate and energetic motivational coach. 
            Your role is to provide personalized, uplifting, and actionable motivation to help people overcome challenges.
            
            Guidelines:
            - Keep responses concise (1-3 sentences)
            - Be empathetic and understanding
            - Include practical advice when appropriate
            - Use encouraging language and positive affirmations
            - Add relevant emojis to make messages more engaging
            - Focus on growth mindset and resilience
            - Avoid being overly generic - personalize based on the user's specific concern
            """
            
            user_prompt = f"{user_context}User says: '{user_message}'\n\nProvide a motivational response that addresses their specific concern."
            
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            motivation = response.choices[0].message.content.strip()
            logger.info(f"Generated motivation for message: '{user_message[:50]}...'")
            return motivation
            
        except Exception as e:
            logger.error(f"Error generating motivation: {e}")
            # Fallback motivational messages
            fallback_messages = [
                "Every challenge is an opportunity to grow stronger  Keep pushing forward!",
                "You're capable of amazing things! Take it one step at a time ",
                "Believe in yourself - you've overcome difficulties before, and you can do it again ",
                "Progress isn't always linear, but every effort counts. Keep going! ",
                "Your dreams are valid and achievable. Stay focused and persistent! "
            ]
            import random
            return random.choice(fallback_messages)
    
    async def generate_daily_motivation(self, user_id: str = None, db: AsyncSession = None) -> str:
        """Generate a daily motivational message"""
        try:
            system_prompt = """You are Motivo AI, sending a daily motivational message. 
            Create an inspiring, positive message to start someone's day right.
            
            Guidelines:
            - Keep it brief but impactful (1-2 sentences)
            - Focus on themes like: new opportunities, growth, gratitude, achievement, resilience
            - Make it energetic and uplifting
            - Include relevant emojis
            - Vary between different motivational themes
            """
            
            user_prompt = "Generate a daily motivational message to inspire someone to have a great day."
            
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            motivation = response.choices[0].message.content.strip()
            logger.info("Generated daily motivation message")
            return motivation
            
        except Exception as e:
            logger.error(f"Error generating daily motivation: {e}")
            fallback_messages = [
                "Today is full of possibilities! Make it count ",
                "You have the power to make today amazing. Believe in yourself! ",
                "Every new day is a chance to grow and achieve your dreams ",
                "Embrace today with gratitude and determination. You've got this! ",
                "Your potential is limitless. Make today the day you shine! "
            ]
            import random
            return random.choice(fallback_messages)
    
    async def generate_reminder_motivation(self, original_request: str, reminder_text: str) -> str:
        """Generate motivational content for reminder emails"""
        try:
            system_prompt = """You are Motivo AI, creating a motivational reminder message.
            The user previously set a reminder, and now it's time to send it with motivational context.
            
            Guidelines:
            - Acknowledge their original request
            - Provide encouragement to take action
            - Keep it motivating and actionable
            - Include relevant emojis
            - 2-3 sentences maximum
            """
            
            user_prompt = f"User's original request: '{original_request}'\nReminder text: '{reminder_text}'\n\nCreate a motivational reminder message."
            
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=120,
                temperature=0.7
            )
            
            motivation = response.choices[0].message.content.strip()
            logger.info("Generated reminder motivation")
            return motivation
            
        except Exception as e:
            logger.error(f"Error generating reminder motivation: {e}")
            return f"Reminder: {reminder_text}\n\nYou've got this! Take action and make progress today"


# Export an alias so other modules importing OpenRouterService keep working
OpenRouterService = OpenAIService