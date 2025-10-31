from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.dependencies import get_current_user
from app.services.ai_generator import get_ai_generator
from app.config import settings

router = APIRouter()


@router.post("/generate", response_model=schemas.AIGenerateResponse)
async def generate_tweet_variants(
    request: schemas.AIGenerateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered tweet variants using Gemini"""
    
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    try:
        ai_generator = get_ai_generator()
        variants = ai_generator.generate_tweet_variants(
            topic=request.topic,
            tone=request.tone,
            num_variants=request.num_variants,
            include_hashtags=request.include_hashtags,
            include_cta=request.include_cta
        )
        
        # Save as drafts
        for variant in variants:
            tweet = models.Tweet(
                user_id=current_user.id,
                text=variant['text'],
                generated_by_ai=True,
                viral_score=variant.get('viral_score'),
                status="draft"
            )
            db.add(tweet)
        db.commit()
        
        return {"variants": variants, "metadata": {"topic": request.topic, "tone": request.tone}}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/analyze")
async def analyze_tweet(text: str, current_user: models.User = Depends(get_current_user)):
    """Analyze tweet sentiment"""
    try:
        ai_generator = get_ai_generator()
        return ai_generator.analyze_tweet_sentiment(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
