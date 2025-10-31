from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    twitter_username = Column(String, index=True)
    api_key = Column(Text)  # Twitter API key (encrypted)
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    tweets = relationship("Tweet", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user")

class Tweet(Base):
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tweet_id_twitter = Column(String, unique=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_at = Column(DateTime(timezone=True))
    posted_at = Column(DateTime(timezone=True))
    status = Column(String, default="draft")  # draft, scheduled, posted, failed
    media_links = Column(JSON, default=[])
    generated_by_ai = Column(Boolean, default=False)
    viral_score = Column(Float)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    user = relationship("User", back_populates="tweets")
    metrics = relationship("Metric", back_populates="tweet", cascade="all, delete-orphan")
    campaign = relationship("Campaign", back_populates="tweets")

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    impressions = Column(Integer)
    engagement_rate = Column(Float)
    additional_data = Column(JSON, default={})
    
    tweet = relationship("Tweet", back_populates="metrics")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    recurrence = Column(String)  # Cron expression
    slots = Column(JSON, default=[])
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="campaigns")
    tweets = relationship("Tweet", back_populates="campaign")