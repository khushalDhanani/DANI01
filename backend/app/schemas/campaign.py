from datetime import datetime
from pydantic import BaseModel, Field


class PRCampaignItem(BaseModel):
    CampDetID: int
    CampID: int
    PRClassID: int
    PRClassName: str | None = None
    ItemRefID: int | None = None
    ItemName: str | None = None
    AdHocLimit: int | None = None


class PRCampaignEventMapping(BaseModel):
    ID: int
    CampID: int
    LocID: int | None = None
    DLEventID: int | None = None
    EventSubject: str | None = None
    EventFromDate: datetime | None = None
    EventToDate: datetime | None = None


class PRCampaignSummary(BaseModel):
    CampID: int
    CampName: str
    CampStartDate: datetime | None = None
    CampReviewCutOfDate: datetime | None = None
    CampDelReminderDate: datetime | None = None
    TransCutOffDate: datetime | None = None
    CampCloseDate: datetime | None = None
    CampStatusID: int | None = None
    CampStatus: str | None = None
    CampIsActive: bool = True
    CreatedBy: str | None = None
    CreatedAt: datetime | None = None
    TotalTransactions: int = 0
    ApprovedCount: int = 0
    PendingReviewCount: int = 0
    RejectedCount: int = 0
    DeliveredCount: int = 0


class PRCampaignDetail(PRCampaignSummary):
    Items: list[PRCampaignItem] = Field(default_factory=list)
    Events: list[PRCampaignEventMapping] = Field(default_factory=list)


class PRTransactionItem(BaseModel):
    PRID: int
    CampID: int
    CampName: str | None = None
    PersonID: int
    RecipientName: str | None = None
    PersonTitle: str | None = None
    PersonDepartment: str | None = None
    PersonPRClassID: int | None = None
    PRClassName: str | None = None
    PRTypeID: int | None = None
    PRTypeName: str | None = None
    CampReviewStatusID: int | None = None
    ReviewStatusName: str | None = None
    DeliveryTypeID: int | None = None
    DeliveryTypeName: str | None = None
    DeliveryStatusID: int | None = None
    DeliveryStatusName: str | None = None
    PROwnerEmpID: int | None = None
    OwnerName: str | None = None
    OwnerDepartment: str | None = None
    GiftOrderedDt: datetime | None = None
    IsReattempt: bool = False
    IsActive: bool = True


class PRTransactionPageResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[PRTransactionItem]


class PRTransactionLogItem(BaseModel):
    TransactionID: int
    CampID: int | None = None
    CampName: str | None = None
    PRID: int | None = None
    TransactionStatusID: int | None = None
    StatusName: str | None = None
    TransactionDesc: str | None = None
    ModuleName: str | None = None
    TransactionMessage: str | None = None
    EntUser: str | None = None
    EntDt: datetime | None = None
    CorrelationId: str | None = None
    Severity: int | None = None


class PRTransactionLogPageResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[PRTransactionLogItem]
