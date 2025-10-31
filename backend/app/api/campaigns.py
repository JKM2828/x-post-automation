from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.Campaign, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: schemas.CampaignCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new campaign"""
    
    campaign = models.Campaign(
        user_id=current_user.id,
        name=campaign_data.name,
        description=campaign_data.description,
        recurrence=campaign_data.recurrence,
        slots=campaign_data.slots,
        active=True
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.get("/", response_model=List[schemas.Campaign])
async def get_campaigns(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all campaigns for current user"""
    
    campaigns = db.query(models.Campaign).filter(
        models.Campaign.user_id == current_user.id
    ).all()
    
    return campaigns


@router.get("/{campaign_id}", response_model=schemas.Campaign)
async def get_campaign(
    campaign_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific campaign"""
    
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == campaign_id,
        models.Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


@router.put("/{campaign_id}", response_model=schemas.Campaign)
async def update_campaign(
    campaign_id: int,
    campaign_data: schemas.CampaignCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update campaign"""
    
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == campaign_id,
        models.Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.name = campaign_data.name
    campaign.description = campaign_data.description
    campaign.recurrence = campaign_data.recurrence
    campaign.slots = campaign_data.slots
    
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete campaign"""
    
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == campaign_id,
        models.Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    db.delete(campaign)
    db.commit()
    
    return None


@router.post("/{campaign_id}/toggle", response_model=schemas.Campaign)
async def toggle_campaign(
    campaign_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle campaign active status"""
    
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == campaign_id,
        models.Campaign.user_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.active = not campaign.active
    db.commit()
    db.refresh(campaign)
    
    return campaign
