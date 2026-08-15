from fastapi import APIRouter, HTTPException, Query

from app.modules.campaign.campaign_service import CampaignService
from app.schemas.campaign import (
    PRCampaignDetail,
    PRCampaignSummary,
    PRTransactionPageResponse,
    PRTransactionLogPageResponse,
)

router = APIRouter()


@router.get("", response_model=list[PRCampaignSummary])
def get_campaigns():
    """Get all PR Campaign overview summaries."""
    return CampaignService.get_campaign_summaries()


@router.get("/transactions", response_model=PRTransactionPageResponse)
def get_pr_transactions(
    camp_id: int | None = Query(None, description="Filter by Campaign ID"),
    review_status_id: int | None = Query(None, description="Filter by Review Status ID (548=Pending, 550=Approved, 551=Reject)"),
    delivery_status_id: int | None = Query(None, description="Filter by Delivery Status ID (554=Pending, 555=Delivered, 559=Decline)"),
    search: str | None = Query(None, description="Search recipient name, PR owner name, or campaign title"),
    limit: int = Query(25, ge=1, le=200, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """Get paginated PR campaign recipient transactions."""
    return CampaignService.get_pr_transactions(
        camp_id=camp_id,
        review_status_id=review_status_id,
        delivery_status_id=delivery_status_id,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/audit-log", response_model=PRTransactionLogPageResponse)
def get_pr_audit_logs(
    camp_id: int | None = Query(None, description="Filter by Campaign ID"),
    limit: int = Query(25, ge=1, le=200, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """Get paginated PR campaign review audit logs."""
    return CampaignService.get_pr_audit_logs(
        camp_id=camp_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{camp_id}", response_model=PRCampaignDetail)
def get_campaign_detail(camp_id: int):
    """Get single PR Campaign detailed profile with configured items and event mappings."""
    detail = CampaignService.get_campaign_detail(camp_id)
    if not detail:
        raise HTTPException(
            status_code=404,
            detail=f"PR Campaign #{camp_id} not found.",
        )
    return detail
