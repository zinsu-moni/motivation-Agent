from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    daily_motivation_enabled = Column(Boolean, default=True)
    preferred_motivation_time = Column(String(10), default="08:00")  

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)  
    reminder_text = Column(Text, nullable=False)
    original_request = Column(Text, nullable=True) 
    scheduled_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)

class MotivationLog(Base):
    __tablename__ = "motivation_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True) 
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    method = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    response_time_ms = Column(Integer, nullable=True) 

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    email_type = Column(String(50), nullable=False)
    sent_at = Column(DateTime, server_default=func.now())
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)