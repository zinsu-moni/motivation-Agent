from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import User, MotivationLog
import logging
import uuid

logger = logging.getLogger(__name__)

class UserService:
    async def create_user(self, db: AsyncSession, name: str, email: str) -> User:
        try:
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info(f"User with email {email} already exists")
                return existing_user
            
            # Create new user
            user = User(
                name=name,
                email=email
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new user: {name} ({email})")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await db.rollback()
            raise
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> User:
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> User:
        try:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def get_all_active_users(self, db: AsyncSession) -> list[User]:
        try:
            result = await db.execute(
                select(User).where(User.is_active == True, User.daily_motivation_enabled == True)
            )
            users = result.scalars().all()
            return list(users)
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def update_user_motivation_preferences(self, db: AsyncSession, user_id: str, 
                                                enabled: bool, preferred_time: str = None) -> bool:
        try:
            user = await self.get_user_by_id(db, user_id)
            if not user:
                return False
            
            user.daily_motivation_enabled = enabled
            if preferred_time:
                user.preferred_motivation_time = preferred_time
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Updated motivation preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            await db.rollback()
            return False
    
    async def log_motivation_interaction(self, db: AsyncSession, user_id: str, 
                                       user_message: str, ai_response: str, 
                                       method: str, response_time_ms: int = None):
        """Log a motivation interaction"""
        try:
            log_entry = MotivationLog(
                user_id=user_id,
                user_message=user_message,
                ai_response=ai_response,
                method=method,
                response_time_ms=response_time_ms
            )
            
            db.add(log_entry)
            await db.commit()
            
            logger.info(f"Logged motivation interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error logging motivation interaction: {e}")
            await db.rollback()
    
    async def get_user_motivation_history(self, db: AsyncSession, user_id: str, limit: int = 10) -> list[MotivationLog]:
        try:
            result = await db.execute(
                select(MotivationLog)
                .where(MotivationLog.user_id == user_id)
                .order_by(MotivationLog.created_at.desc())
                .limit(limit)
            )
            history = result.scalars().all()
            return list(history)
        except Exception as e:
            logger.error(f"Error getting user motivation history: {e}")
            return []