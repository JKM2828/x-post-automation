from celery import Celery
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app import models
from app.services.x_client import get_twitter_client
from app.services.ai_generator import get_ai_generator
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'x_post_automation',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'check-scheduled-tweets': {
            'task': 'app.tasks.scheduler.check_scheduled_tweets',
            'schedule': 60.0,  # Run every minute
        },
        'update-tweet-metrics': {
            'task': 'app.tasks.scheduler.update_tweet_metrics',
            'schedule': 300.0,  # Run every 5 minutes
        },
        'process-campaigns': {
            'task': 'app.tasks.scheduler.process_campaigns',
            'schedule': 3600.0,  # Run every hour
        }
    }
)


@celery_app.task(name='app.tasks.scheduler.check_scheduled_tweets')
def check_scheduled_tweets():
    """Check and post scheduled tweets"""
    db: Session = SessionLocal()
    
    try:
        now = datetime.utcnow()
        
        # Get tweets scheduled for posting
        scheduled_tweets = db.query(models.Tweet).filter(
            models.Tweet.status == "scheduled",
            models.Tweet.scheduled_at <= now
        ).all()
        
        logger.info(f"Found {len(scheduled_tweets)} tweets to post")
        
        for tweet in scheduled_tweets:
            try:
                user = db.query(models.User).filter(
                    models.User.id == tweet.user_id
                ).first()
                
                if not user or not user.api_key:
                    logger.warning(f"User {tweet.user_id} has no API key")
                    continue
                
                # Post to Twitter
                twitter_client = get_twitter_client(user.api_key)
                result = twitter_client.post_tweet(tweet.text, tweet.media_links)
                
                # Update tweet status
                tweet.tweet_id_twitter = result.get("id_str")
                tweet.status = "posted"
                tweet.posted_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"Posted tweet {tweet.id}")
                
            except Exception as e:
                logger.error(f"Failed to post tweet {tweet.id}: {str(e)}")
                tweet.status = "failed"
                db.commit()
        
        return f"Processed {len(scheduled_tweets)} tweets"
        
    finally:
        db.close()


@celery_app.task(name='app.tasks.scheduler.update_tweet_metrics')
def update_tweet_metrics():
    """Update metrics for posted tweets"""
    db: Session = SessionLocal()
    
    try:
        # Get recently posted tweets (last 7 days)
        recent_tweets = db.query(models.Tweet).filter(
            models.Tweet.status == "posted",
            models.Tweet.tweet_id_twitter.isnot(None)
        ).limit(100).all()
        
        logger.info(f"Updating metrics for {len(recent_tweets)} tweets")
        
        for tweet in recent_tweets:
            try:
                user = db.query(models.User).filter(
                    models.User.id == tweet.user_id
                ).first()
                
                if not user or not user.api_key:
                    continue
                
                # Fetch metrics from Twitter
                twitter_client = get_twitter_client(user.api_key)
                metrics_data = twitter_client.get_tweet_metrics(tweet.tweet_id_twitter)
                
                # Calculate engagement rate
                total_engagement = (
                    metrics_data['likes'] + 
                    metrics_data['retweets'] + 
                    metrics_data['replies']
                )
                engagement_rate = (
                    total_engagement / metrics_data.get('impressions', 1) * 100
                    if metrics_data.get('impressions') else 0
                )
                
                # Create new metric entry
                metric = models.Metric(
                    tweet_id=tweet.id,
                    likes=metrics_data['likes'],
                    retweets=metrics_data['retweets'],
                    replies=metrics_data['replies'],
                    impressions=metrics_data.get('impressions'),
                    engagement_rate=engagement_rate,
                    timestamp=datetime.utcnow()
                )
                
                db.add(metric)
                db.commit()
                
            except Exception as e:
                logger.error(f"Failed to update metrics for tweet {tweet.id}: {str(e)}")
        
        return f"Updated metrics for {len(recent_tweets)} tweets"
        
    finally:
        db.close()


@celery_app.task(name='app.tasks.scheduler.process_campaigns')
def process_campaigns():
    """Process active campaigns and generate/schedule tweets"""
    db: Session = SessionLocal()
    
    try:
        active_campaigns = db.query(models.Campaign).filter(
            models.Campaign.active == True
        ).all()
        
        logger.info(f"Processing {len(active_campaigns)} active campaigns")
        
        for campaign in active_campaigns:
            try:
                user = db.query(models.User).filter(
                    models.User.id == campaign.user_id
                ).first()
                
                if not user:
                    continue
                
                # Check if we need to generate new tweets for this campaign
                # Based on campaign slots and recurrence
                
                for slot in campaign.slots:
                    # Generate AI content for each slot
                    ai_generator = get_ai_generator()
                    variants = ai_generator.generate_tweet_variants(
                        topic=slot.get('topic', 'general'),
                        tone=slot.get('tone', 'professional'),
                        num_variants=1
                    )
                    
                    if variants:
                        # Schedule the tweet
                        tweet = models.Tweet(
                            user_id=user.id,
                            text=variants[0]['text'],
                            generated_by_ai=True,
                            viral_score=variants[0].get('viral_score'),
                            campaign_id=campaign.id,
                            status="scheduled",
                            scheduled_at=slot.get('scheduled_at')
                        )
                        db.add(tweet)
                
                db.commit()
                logger.info(f"Processed campaign {campaign.id}")
                
            except Exception as e:
                logger.error(f"Failed to process campaign {campaign.id}: {str(e)}")
        
        return f"Processed {len(active_campaigns)} campaigns"
        
    finally:
        db.close()


@celery_app.task(name='app.tasks.scheduler.post_tweet_now')
def post_tweet_now(tweet_id: int):
    """Post a tweet immediately (async task)"""
    db: Session = SessionLocal()
    
    try:
        tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
        
        if not tweet:
            raise ValueError(f"Tweet {tweet_id} not found")
        
        user = db.query(models.User).filter(models.User.id == tweet.user_id).first()
        
        if not user or not user.api_key:
            raise ValueError("User API key not configured")
        
        # Post to Twitter
        twitter_client = get_twitter_client(user.api_key)
        result = twitter_client.post_tweet(tweet.text, tweet.media_links)
        
        # Update tweet
        tweet.tweet_id_twitter = result.get("id_str")
        tweet.status = "posted"
        tweet.posted_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Posted tweet {tweet_id}")
        
        return {"status": "success", "tweet_id": tweet_id}
        
    except Exception as e:
        logger.error(f"Failed to post tweet {tweet_id}: {str(e)}")
        if tweet:
            tweet.status = "failed"
            db.commit()
        raise
        
    finally:
        db.close()