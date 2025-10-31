from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    twitter_username: Optional[str] = None

class UserCreate(UserBase):
    api_key: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Tweet schemas
class TweetBase(BaseModel):
    text: str = Field(..., max_length=280)
    media_links: Optional[List[str]] = []

class TweetCreate(TweetBase):
    scheduled_at: Optional[datetime] = None

class TweetUpdate(BaseModel):
    text: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None

class Tweet(TweetBase):
    id: int
    user_id: int
    tweet_id_twitter: Optional[str] = None
    status: str
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    generated_by_ai: bool
    viral_score: Optional[float] = None
    
    class Config:
        from_attributes = True

# Metric schemas
class MetricBase(BaseModel):
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    impressions: Optional[int] = None

class Metric(MetricBase):
    id: int
    tweet_id: int
    timestamp: datetime
    engagement_rate: Optional[float] = None
    
    class Config:
        from_attributes = True

# Campaign schemas
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    recurrence: Optional[str] = None
    slots: Optional[List[Dict]] = []

class CampaignCreate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int
    user_id: int
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI Generation schemas
class AIGenerateRequest(BaseModel):
    topic: str
    tone: str = "professional"
    variant_count: int = Field(3, ge=1, le=5)
    max_length: int = Field(280, le=280)
    include_hashtags: bool = True
    include_call_to_action: bool = True

class AIGenerateResponse(BaseModel):
    variants: List[Dict]
    metadata: Dict

# Analytics schemas
class AnalyticsSummary(BaseModel):
    total_tweets: int
    total_engagement: int
    avg_engagement_rate: float
    top_tweet: Optional[Tweet] = None
    best_time_slots: List[Dict]
